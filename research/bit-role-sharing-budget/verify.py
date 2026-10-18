#!/usr/bin/env python3
"""Price role sharing before construction. No new supplier or kappa is admitted.

Prepared for androolloyd with substantial OpenAI Codex assistance. Apache-2.0.
The interval engine uses positive atanh sums, independently of the inherited
Mercator engine. All admission and corruption checks also run under -O.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DYAD = 1 << 224


def need(ok, message):
    if not ok:
        raise ValueError(message)


def down(x):
    return Q(x.numerator * DYAD // x.denominator, DYAD)


def up(x):
    return -down(-x)


@lru_cache(None)
def log_interval(x):
    need(x >= 1, 'log domain')
    k = 0
    while x >= 2:
        x /= 2
        k += 1

    def atanh(y):
        z = (y - 1) / (y + 1)
        term = z
        total = Q(0)
        for i in range(96):
            total += 2 * term / (2*i + 1)
            term *= z*z
        tail = 2 * term / (193 * (1-z*z))
        return total, total + tail

    lo, hi = atanh(x)
    a, b = atanh(Q(2))
    return down(lo+k*a), up(hi+k*b)


def exp_interval(lo, hi):
    need(0 <= lo <= hi < Q(1, 10), 'exponential domain')

    def polynomial(x):
        total = term = Q(1)
        for k in range(1, 29):
            term *= x/k
            total += term
        return total, term

    lower, _ = polynomial(lo)
    upper, last = polynomial(hi)
    return down(lower), up(upper + last*hi/29/(1-hi/30))


@lru_cache(None)
def rate_factor(rank, c):
    lo, hi = log_interval(Q(64, rank))
    return exp_interval(c*lo, c*hi)


def moment(profile, c, bad=True):
    lo = hi = Q(0)
    for rank, count in profile.items():
        need(0 < rank < 64 and count > 0, 'proper positive child')
        a, b = rate_factor(rank, c)
        weight = Q(rank*count, 64*28416)
        lo += weight*a
        hi += weight*b
    a, b = rate_factor(1, c)
    fallback = Q(32*64*sum(profile.values()), 10**16*28416) if bad else Q(0)
    return down(lo+fallback*a), up(hi+fallback*b)


def rational_rank(vectors):
    pivots = {}
    for vector in vectors:
        row = list(map(Q, vector))
        for j, old in sorted(pivots.items()):
            coefficient = row[j]
            row = [x-coefficient*y for x, y in zip(row, old)]
        j = next((j for j, x in enumerate(row) if x), None)
        if j is not None:
            coefficient = row[j]
            pivots[j] = [x/coefficient for x in row]
    return len(pivots)


def binary_rank(rows):
    basis = {}
    for value in rows:
        while value:
            i = value.bit_length()-1
            if i not in basis:
                basis[i] = value
                break
            value ^= basis[i]
    return len(basis)


def extract_word(word, expected):
    """Read the actual word, not only its advertised local histogram."""
    v, helpers = word['v'], word['R']
    need((v, helpers, word['h']) == (111, 439, 8), 'pinned dimensions')
    dims = [rational_rank(word['lines'][i] for i in frame) for frame in word['frames']]
    masks = [sum(1 << i for i in frame) for frame in word['frames']]
    current = word['start'][:]
    rows = [1 << i for i in range(2*v+helpers)]
    histogram = Counter()
    role_mass = Counter()

    def climb(role, frame):
        old = current[role]
        need(masks[old] & ~masks[frame] == 0, 'nested frame')
        delta = dims[frame] - dims[old]
        need(delta >= 0, 'nonnegative climb')
        if delta:
            histogram[delta] += 1
            role_mass['source' if role < v else 'target' if role < 2*v else 'helper'] += delta
        current[role] = frame

    def gates(section):
        for frame, target, sources in word[section]:
            need(len({target, *sources}) == len(sources)+1, 'distinct scalar operands')
            for role in [target, *sources]:
                climb(role, frame)
            for source in sources:
                rows[target] ^= rows[source]

    gates('D')
    gates('A')
    copies = [dims[current[role]] for role in word['ret']]
    response_rows = [sum(1 << k for k in sources) for sources in word['scatter']]
    need(binary_rank(response_rows) == 9, 'retained-total response rank')
    snapshots = [rows[role] for role in word['ret']]
    need(binary_rank(snapshots) == 9, 'independent retained total inputs')
    for target, sources in enumerate(word['scatter']):
        for k in sources:
            rows[v+target] ^= snapshots[k]
    gates('B')
    gates('C')
    for role, frame in enumerate(word['final']):
        climb(role, frame)
    want = [(1 << i) ^ ((1 << (i-v)) if v <= i < 2*v else 0) for i in range(len(rows))]
    need(rows == want, 'full local Boolean endpoint')
    histogram.update(copies)
    need(dict(histogram) == {int(r): n for r, n in expected['local_histogram'].items()}, 'local paid profile')
    need(copies == [7]*9 and dict(role_mass) == dict(source=777, target=777, helper=3512), 'complete local rank mass')
    return histogram, dict(columns=len(rows), copy_ranks=copies, response_rank=9,
                           independent_retained_inputs=9, role_climb_mass=dict(role_mass),
                           paid_histogram=dict(sorted(histogram.items())), rank_mass=5129)


def pinned_inputs():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for name, digest in pins['files'].items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, 'source hash mismatch: '+name)
    directory = ROOT/'research/e8-bit-p111-tuned/tune'
    expected = json.loads((directory/'EXPECTED.json').read_text())
    word = json.loads(gzip.decompress((directory/'bitE8mut-p111-tuned.json.gz').read_bytes()))
    # Read literal frozen-hosting constants without importing a dependency tree.
    constants = {}
    for node in ast.parse((directory/'fastc.py').read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('REM', 'W', 'm', 'T'):
                    constants[target.id] = ast.literal_eval(node.value)
    need((constants['W'], constants['m'], constants['T']) == (28416, 64, 288), 'global constants')
    return pins, word, expected, constants


def combine(remainder, mass, cap, integral=False):
    result = Counter(remainder)
    if integral:
        count, tail = divmod(mass, cap)
        result[cap] += count
        if tail:
            result[tail] += 1
    else:
        result[cap] += Q(mass, cap)
    return dict(sorted((r, n) for r, n in result.items() if n))


def bracket_root(profile):
    lo, hi = Q(0), Q(1, 50)
    need(moment(profile, lo)[1] < 1 < moment(profile, hi)[0], 'root bracket initial')
    for _ in range(72):
        mid = (lo+hi)/2
        lower, upper = moment(profile, mid)
        if upper < 1:
            lo = mid
        else:
            need(lower > 1, 'root interval ambiguity')
            hi = mid
    return dict(saving=[lo, hi], kappa_ceiling_upper=hi/(1+hi),
                kappa_ceiling_display=format(float(hi/(1+hi)), '.15g'))


def query_controls():
    """Exact operator checks on a two-address swap, including private dirt."""
    def mix(rows, matrix):
        return [tuple(sum_xor(rows[j][a] for j in range(len(rows)) if mask >> j & 1)
                      for a in range(2)) for mask in matrix]

    def flatten(rows):
        return [value for row in rows for value in row]

    gl2 = [pair for a in range(1, 4) for b in range(1, 4)
           if binary_rank(pair := (a, b)) == 2]
    inputs = [(1, 2), (4, 8)]
    target = [(2, 1), (8, 4)]
    failures = 0
    # Complete GL(2,2) before/after charts with at most one queried row.
    for before in gl2:
        for after in gl2:
            for row in (None, 0, 1):
                values = mix(inputs, before)
                if row is not None:
                    values[row] = values[row][::-1]
                values = mix(values, after)
                need(values != target, 'sub-two-query all-role counterexample')
                failures += 1
    bases = 0
    for active in range(1, 9):
        for private in range(4):
            values = [(1 << (2*j), 1 << (2*j+1)) for j in range(active+private)]
            goal = [row[::-1] if j < active else row for j, row in enumerate(values)]
            difference = [x ^ y for x, y in zip(flatten(values), flatten(goal))]
            need(binary_rank(difference) == active, 'direct-sum displacement rank')
            actual = values[:]
            for j in range(active):
                actual[j] = actual[j][::-1]
            need(actual == goal, 'matching query count and restored dirt')
            bases += 2*(active+private)
    return dict(zero_or_one_query_chart_programs_rejected=failures, matching_query_basis_columns=bases,
                scope='Two-address involution tests; the arbitrary-size lower bound is proved separately.')


def sum_xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    pins, word, expected, constants = pinned_inputs()
    local, word_receipt = extract_word(word, expected['word'])
    remainder = constants['REM']
    baseline = Counter({r: 288*n for r, n in local.items()})
    baseline.update(remainder)
    need(dict(baseline) == {int(r): n for r, n in expected['nine']['profile'].items()}, 'full frozen-hosting invoice')
    mass = 288*sum(r*n for r, n in local.items())
    need(mass == 1477152 and sum(r*n for r, n in baseline.items()) == 1808352, 'global rank masses')
    current = Q(expected['nine']['bit_lower'])
    need(moment(baseline, current)[1] < 1 < moment(baseline, current+Q(1, 10**24))[0], 'independent current root enclosure')
    target = Q(1, 99)
    base_interval = moment(baseline, target)
    pooling = []
    for batch in (1, 2, 4, 8, 16, 32):
        bill = {}
        calls = 0
        for rank, count in baseline.items():
            full, tail = divmod(count, batch)
            bill[rank] = batch*full + tail
            calls += full + bool(tail)
        need(bill == dict(baseline), 'full batch-volume accounting')
        pooling.append(dict(batch_size=batch, optimistic_dispatches=calls, volume_weighted_invoice=bill,
                            moment=moment(bill, target)))
    need(base_interval[0] > 1 and base_interval[1]/2 < 1, 'omitted volume mutation')
    stage = combine(remainder, mass, 8)
    free_copy = combine(remainder, mass-288*63, 8)
    need(moment(stage, target)[0] > 1 and moment(free_copy, target)[0] > 1, 'intra-stage rejection')
    mass_cut_99 = moment(combine(remainder, mass-288*99, 8), target)
    mass_cut_100 = moment(combine(remainder, mass-288*100, 8), target)
    need(mass_cut_99[0] > 1 > mass_cut_100[1], 'net rank-mass reduction threshold')
    caps = []
    first_local = first_global = None
    total_mass = sum(r*n for r, n in baseline.items())
    for cap in range(1, 64):
        relaxed = moment(combine(remainder, mass, cap), target)
        global_relaxed = moment({cap: Q(total_mass, cap)}, target)
        if first_local is None and relaxed[1] < 1:
            first_local = cap
        if first_global is None and global_relaxed[1] < 1:
            first_global = cap
        caps.append(dict(rank_cap=cap, fixed_boundary_moment=relaxed, freely_repacked_boundary_moment=global_relaxed))
    need((first_local, first_global) == (56, 37), 'rank threshold')
    # These exclusions do not depend on a loose positive fallback estimate.
    need(moment(combine(remainder, mass, 55), target, False)[0] > 1, 'cap-55 rejection without fallback')
    need(moment(free_copy, target, False)[0] > 1, 'free-copy rejection without fallback')
    # A fixed-port stage-span argument must not be applied across all ports.
    base_span = rational_rank(word['lines'])
    need(base_span == 8 and base_span+7*7 == 57 > 1+7*7, 'cross-port span control')
    # A conditional invoice: it is not a supplied operator or hosting plan.
    conditional = []
    unit = moment({1: 1}, target)
    for cap in (56, 57, 63):
        profile = combine(remainder, mass, cap, integral=True)
        lo, hi = moment(profile, target)
        allowance = (1-hi)//unit[1]
        need(hi+allowance*unit[1] < 1 < lo+(allowance+1)*unit[0], 'repair allowance integer fence')
        # Rank-mass fraction needing fusion from ideal rank-eight calls.
        unfused = moment(stage, target)
        all_fused = moment(combine(remainder, mass, cap), target)
        fraction_lo = (unfused[0]-1)/(unfused[1]-all_fused[0])
        fraction_hi = (unfused[1]-1)/(unfused[0]-all_fused[1])
        need(0 < fraction_lo <= fraction_hi < 1, 'fusion coverage interval')
        conditional.append(dict(rank_cap=cap, profile=profile, moment=[lo, hi],
                                additional_rank_one_child_budget=int(allowance),
                                required_fused_local_rank_mass_fraction=[fraction_lo, fraction_hi],
                                required_fused_percent_display=format(float(100*fraction_hi), '.12g'),
                                status='ARITHMETIC_TARGET_ONLY_NO_OPERATOR_OR_HOSTING'))
    # Meaningful arithmetic controls, not accepted alternative assumptions.
    need(moment({8: Q(mass, 8)}, target)[1] < 1, 'omitted idle boundary control')
    need(moment(baseline, Q(0))[1] < 1 < base_interval[0], 'zero-saving-only admission control')
    malformed = dict(baseline)
    malformed[64] = 1
    try:
        moment(malformed, target)
    except ValueError as error:
        need(str(error) == 'proper positive child', 'proper-child rejection')
    else:
        raise ValueError('full-width recursive call accepted')
    controls = query_controls()
    result = dict(status='PASS_BIT_ROLE_SHARING_COST_SCREEN_NO_NEW_KAPPA',
                  source_hashes=pins['files'], local_word=word_receipt,
                  baseline=dict(m=64, live=28416, profile=dict(sorted(baseline.items())),
                                rank_mass=total_mass, deficit=64*28416-total_mass,
                                target_saving=target, target_moment=base_interval, idle_remainder=remainder),
                  role_pooling=pooling,
                  perfect_stage_fusion=dict(moment=moment(stage, target), root=bracket_root(stage)),
                  perfect_stage_fusion_and_free_copies=dict(moment=moment(free_copy, target), root=bracket_root(free_copy)),
                  alternative_net_mass_target=dict(removed_per_invocation=100, global_removed=28800,
                                                   profile=combine(remainder, mass-288*100, 8),
                                                   moment=mass_cut_100, one_less_removed_moment=mass_cut_99,
                                                   scope='Also grants perfect rank-eight consolidation. Net invoice reduction after hosting, with unchanged W and remainder; not a helper-deletion construction.'),
                  rank_caps=caps, necessary_rank_cap_with_fixed_boundaries=first_local,
                  necessary_rank_cap_with_free_boundary_repacking=first_global,
                  conditional_invoices=conditional, query_controls=controls,
                  geometry_scope=dict(fixed_port_seven_positive_stage_span=50,
                                      all_ports_seven_positive_stage_span=57,
                                      universal_stage_count_claim_rejected=True),
                  rejected_cost_mutations=['omit pooled volume', 'omit idle boundary', 'test saving zero only', 'allow rank m recursion'],
                  scope='Fixed m, live volume, retained rank mass and stated boundary rules. Relaxed costs can reject a class but cannot admit an unconstructed supplier. Complex endpoint unchanged.')
    args.out.write_text(json.dumps(result, indent=2, default=str)+'\n')
    print(result['status'])
    print('fixed-boundary cap >=', first_local, '; free-boundary cap >=', first_global)
    print('conditional rank-one repair budgets:', [(x['rank_cap'], x['additional_rank_one_child_budget']) for x in conditional])


if __name__ == '__main__':
    main()
