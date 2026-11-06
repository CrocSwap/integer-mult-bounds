"""Exact fixed-invoice relaxation; no word, census or native engine executes.

The grouped delivery/eligibility is hypothetical. Allowances are recursive
raw-moment debits, never scalar-time or physical implementation fees.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
K = F(781451, 250000000)
GRID = 1 << 192
LOG_TERMS = 64
SOURCE = 'research/p104-helper470-twin-rung-removal/RESULT.json'
PINS = {
    SOURCE: (12798, '84fcbe2a0b64307b5703c363408042bdd91555b0419509aa50daa43b3b1924ad'),
    'predecessor/PR6083-PROOF.md': (6222, 'ff3f06c2025ec53bdc89f6b0b803c1f78be50b5e0d5825a8a167755814c666da'),
    'predecessor/PR6083-README.md': (4286, '68dc75b94e5ae0b2a6f6ba01c81c07f046bbe7bbb2ba77338dde1bc0e2d8f988'),
}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def no_number(text):
    raise ValueError('noninteger JSON number')


def load(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_float=no_number, parse_constant=no_number)


def authenticate():
    bodies, identities = {}, {}
    for name, expected in PINS.items():
        path = ROOT / name if name == SOURCE else PACKAGE / name
        require(path.is_file() and not path.is_symlink(), 'source regular file')
        raw = path.read_bytes()
        actual = (len(raw), hashlib.sha256(raw).hexdigest())
        require(actual == expected, 'source bytes: ' + name)
        bodies[name] = raw
        identities[name] = actual[1]
    return load(bodies[SOURCE]), identities


def histogram(value):
    require(type(value) is dict and value, 'histogram object')
    result = {}
    for key, count in value.items():
        require(type(key) is str and key.isdecimal(), 'histogram rank')
        rank = int(key)
        require(rank > 0 and str(rank) == key, 'histogram rank')
        require(type(count) is int and count > 0, 'histogram count')
        result[rank] = count
    return result


def combine(*pieces):
    result = {}
    for coefficient, values in pieces:
        for rank, count in values.items():
            result[rank] = result.get(rank, 0) + coefficient * count
    return {rank: count for rank, count in result.items() if count}


def profile(source):
    complete, local, caller = source['complete_cost'], source['local'], source['physical_caller']
    require(complete['kappa'] == str(K), 'fixed saving')
    require(type(complete['full_forward_calls']) is int and complete['full_forward_calls'] == 18,
            'LOCAL count')
    require(type(caller['full_calls']) is int and caller['full_calls'] == 18, 'LOCAL count')
    targets, paid = histogram(complete['targets']), histogram(complete['paid'])
    helpers = histogram(local['helpers'])
    require(max(helpers) <= 9 and helpers.get(9) == 385, 'rank9 source inventory')
    main, idles = histogram(caller['main_targets']), histogram(caller['whole_idle_jobs'])
    require(targets == combine((18, helpers), (1, main)), 'target profile reconstruction')
    ports, queries = caller['ports'], complete['query_shears']
    require(type(ports) is int and ports == 104 and type(queries) is int and queries == 15,
            'query count')
    expected_paid = combine((18, histogram(local['paid'])), (1, idles), (1, {1: ports * queries}))
    require(paid == expected_paid, 'paid profile reconstruction')
    require(sum(targets.values()) == 13444 and sum(paid.values()) == 66834, 'complete counts')
    require(sum(r * n for r, n in targets.items()) - sum(r * n for r, n in paid.items()) == 760,
            'rank-mass surplus')
    return targets, paid, helpers


def rounded(value, upper=False):
    numerator = value.numerator * GRID
    units = -((-numerator) // value.denominator) if upper else numerator // value.denominator
    return F(units, GRID)


def interval_sum(*values):
    return (sum((x[0] for x in values), F(0)), sum((x[1] for x in values), F(0)))


def times(integer, value):
    return (integer * value[0], integer * value[1]) if integer >= 0 else (integer * value[1], integer * value[0])


def subtract(left, right):
    return interval_sum(left, times(-1, right))


def encoded(value):
    return [[endpoint.numerator, endpoint.denominator] for endpoint in value]


def log_series(q):
    require(F(1) <= q <= F(2), 'log range reduction')
    z = (q - 1) / (q + 1)
    total, power = F(0), z
    for j in range(LOG_TERMS):
        total += 2 * power / (2 * j + 1)
        power *= z * z
    tail = 2 * power / ((2 * LOG_TERMS + 1) * (1 - z * z))
    return total, total + tail


def log_integer(rank, log_two):
    require(type(rank) is int and rank >= 1, 'positive integer rank')
    exponent = rank.bit_length() - 1
    low, high = log_series(F(rank, 1 << exponent))
    return (rounded(low + exponent * log_two[0]),
            rounded(high + exponent * log_two[1], True))


def exp_minus(x):
    require(F(0) <= x < F(1, 50), 'exponential range')
    total, term = F(1), F(1)
    even = None
    for j in range(1, 34):
        term *= -x / j
        total += term
        if j == 32:
            even = total
    return total, even  # alternating odd33 lower and even32 upper


def powers_for(ranks):
    log_two = log_series(F(2))
    powers, logs = {}, {}
    for rank in sorted(ranks):
        bounds = log_integer(rank, log_two)
        logs[rank] = bounds
        lower = exp_minus(K * bounds[1])[0]
        upper = exp_minus(K * bounds[0])[1]
        powers[rank] = (rounded(rank * lower), rounded(rank * upper, True))
        require(powers[rank][0] <= powers[rank][1], 'power interval order')
    return powers, logs


def moment(coefficients, powers):
    return interval_sum(*(times(count, powers[rank]) for rank, count in coefficients.items()))


def split_checks(powers, delta):
    rows = []
    for rank in range(2, 10):
        for left in range(1, rank):
            gain = subtract(interval_sum(powers[left], powers[rank - left]), powers[rank])
            maximizing = rank == 9 and left in (4, 5)
            if maximizing:
                require(gain == delta, 'balanced rank9 identity')
            else:
                require(gain[1] < delta[0], 'rank9 split domination')
            rows.append(dict(rank=rank, left=left, right=rank-left,
                             gain=encoded(gain), maximizer=maximizing))
    require(len(rows) == 36, 'all36 binary splits')
    return rows


def attainer(helpers, splits):
    require(type(splits) is int and 0 <= splits <= 4, 'split budget')
    require(helpers.get(9, 0) >= splits, 'rank9 inventory')
    result = combine((1, helpers), (splits, {4: 1, 5: 1, 9: -1}))
    require(all(n > 0 for n in result.values()), 'attainer counts')
    require(sum(r*n for r,n in result.items()) == sum(r*n for r,n in helpers.items()), 'attainer rank mass')
    return result


def uniform_rows(targets, paid, helpers, powers, base, delta):
    rows = []
    for splits in range(5):
        changed_local = attainer(helpers, splits)
        change = combine((18, changed_local), (-18, helpers))
        ceiling = interval_sum(base, times(18 * splits, delta))
        direct = moment(combine((1, targets), (-1, paid), (1, change), (-1, {1: 1})), powers)
        margin = subtract(ceiling, powers[1])
        require(max(direct[0], margin[0]) <= min(direct[1], margin[1]), 'direct/factored invoice overlap')
        rows.append(dict(splits_per_LOCAL=splits, total_split_tickets=18*splits,
                         target_delta={str(r):n for r,n in sorted(change.items())},
                         strict_total_recursive_debit_ceiling=encoded(ceiling),
                         after_one_global_rank1=encoded(margin), direct_edited_moment=encoded(direct),
                         after_one_rank2=encoded(subtract(ceiling, powers[2])),
                         after_two_rank1=encoded(subtract(ceiling, times(2, powers[1])))))
    return rows


def rejection(name, callback, reason):
    try:
        callback()
    except ValueError as error:
        require(str(error) == reason, 'wrong rejection: ' + name)
        return dict(name=name, outcome='REJECTED', reason=reason)
    raise ValueError('control accepted: ' + name)


def controls(source, helpers, base, delta, powers):
    two = subtract(interval_sum(base, times(36, delta)), powers[1])
    four = interval_sum(base, times(72, delta))
    require(two[1] < 0, 'two tickets unexpectedly fund rank1')
    require(subtract(four, powers[2])[1] < 0, 'rank2 unexpectedly affordable')
    require(subtract(four, times(2, powers[1]))[1] < 0, 'second rank1 unexpectedly affordable')
    rows = [dict(name='two_per_LOCAL_tickets_cannot_pay_rank1', outcome='NEGATIVE_RAW_MOMENT', witness=encoded(two)),
            dict(name='rank2_cannot_be_paid', outcome='NEGATIVE_RAW_MOMENT', witness=encoded(subtract(four, powers[2]))),
            dict(name='two_rank1_cannot_be_paid', outcome='NEGATIVE_RAW_MOMENT', witness=encoded(subtract(four, times(2, powers[1]))))]
    bad = load(json.dumps(source))
    bad['complete_cost']['paid']['1'] -= 1
    rows.append(rejection('omit_one_old_paid_call', lambda: profile(bad), 'paid profile reconstruction'))
    wrong_targets = load(json.dumps(source))
    wrong_targets['complete_cost']['targets']['4'] += 18
    wrong_targets['complete_cost']['targets']['5'] += 18
    rows.append(rejection('credit_children_without_rank9_debit', lambda: profile(wrong_targets),
                          'target profile reconstruction'))
    scarce = dict(helpers)
    scarce[9] = 3
    rows.append(rejection('insufficient_rank9_roots', lambda: attainer(scarce, 4), 'rank9 inventory'))
    rows.append(rejection('boolean_count', lambda: histogram({'9': True}), 'histogram count'))
    rows.append(rejection('duplicate_JSON', lambda: load('{"x":1,"x":1}'), 'duplicate JSON key'))
    rows.append(rejection('floating_JSON', lambda: load('{"x":1.0}'), 'noninteger JSON number'))
    rows.append(rejection('nonfinite_JSON', lambda: load('{"x":NaN}'), 'noninteger JSON number'))
    return rows


def calculate():
    source, identities = authenticate()
    targets, paid, helpers = profile(source)
    powers, logs = powers_for(set(targets) | set(paid) | set(range(1, 10)))
    base = moment(combine((1, targets), (-1, paid)), powers)
    delta = subtract(interval_sum(powers[4], powers[5]), powers[9])
    require(base[0] > 0 and delta[0] > 0, 'baseline/split positivity')
    split_rows = split_checks(powers, delta)
    uniform = uniform_rows(targets, paid, helpers, powers, base, delta)
    threshold = [n for n in range(73) if interval_sum(base, times(n, delta))[0] > 1]
    require(threshold, 'no global split count funds rank1')
    minimum = min(threshold)
    require(interval_sum(base, times(minimum-1, delta))[1] < 1, 'global threshold separation')
    require(subtract(interval_sum(base, times(54, delta)), powers[1])[0] > 0, 'three tickets do not fund rank1')
    faults = controls(source, helpers, base, delta, powers)
    packet = dict(status='PASS_COUPLED_CUT_DELIVERY_FEE_BUDGET', schema_version=1,
                  source_sha256=identities, saving=str(K), interval_grid_bits=192,
                  local_calls=18, rank9_roots=helpers[9], baseline_moment=encoded(base), delta9=encoded(delta),
                  baseline_targets={str(r):n for r,n in sorted(targets.items())},
                  baseline_paid={str(r):n for r,n in sorted(paid.items())}, split_cases=split_rows,
                  uniform_cases=uniform, minimum_uniform_splits_per_LOCAL=3,
                  minimum_total_splits_in_relaxation=minimum,
                  minimum_coordinates_per_LOCAL_cut_under_two_split_contract=2,
                  rank2_tariff=encoded(powers[2]), controls=faults, control_count=len(faults),
                  physical_delivery=None, nonrecursive_costs=None,
                  allowance_units='Additional recursive raw-moment debit; strict ceiling, not scalar or physical time.',
                  source_programs_executed=False)
    return packet


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode()


def main():
    require(sys.argv[1:] in ([], ['--emit']), 'only optional --emit is supported')
    packet = calculate()
    if not sys.argv[1:]:
        retained = load((PACKAGE / 'RESULT.json').read_bytes())
        require(canonical(packet) == canonical(retained), 'retained complete result mismatch')
    print(canonical(packet).decode())


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print('FAIL_COUPLED_CUT_DELIVERY_FEE_BUDGET: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
