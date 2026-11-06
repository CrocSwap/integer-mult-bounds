"""New finite formal-algebra corroboration; no predecessor executable runs.

Products are in written order: F_s * F_t has formal label st. Finite fields
and dimensions corroborate, but do not prove, the all-field tariff theorem.
"""
from fractions import Fraction as F
from itertools import product
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
MANIFEST_SHA = '13071f312dc31569a121853f4b42d24084617f967937edca5a0cdbf5823b0705'
PATHS = {'predecessor/PR6817-README.md', 'predecessor/PR6817-PROOF.md',
         'predecessor/PR1941-README.md', 'predecessor/PR1966-PROOF.md'}
LABELS = ('e', 's', 't', 'st', 'ts', 'sts')


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
    return json.loads(raw, object_pairs_hook=unique, parse_float=no_number, parse_constant=no_number)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def authenticate():
    raw = (PACKAGE / 'SOURCE-PINS.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA, 'source manifest bytes')
    manifest = load(raw)
    require(type(manifest['schema_version']) is int and manifest['schema_version'] == 1, 'source version')
    require(len(manifest['files']) == 4 and {x['local_path'] for x in manifest['files']} == PATHS,
            'source inventory')
    identities = {}
    for row in manifest['files']:
        path = PACKAGE / row['local_path']
        require(path.is_file() and not path.is_symlink(), 'source regular file')
        data = path.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require((len(data), hashlib.sha256(data).hexdigest(), blob) ==
                (row['bytes'], row['sha256'], row['git_blob']) and row['mode'] == '100644', 'source bytes')
        identities[row['local_path']] = row['sha256']
    return identities


def group_table():
    compose = lambda a, b: tuple(a[b[i]] for i in range(3))
    e, s, t = (0, 1, 2), (1, 0, 2), (0, 2, 1)
    basis = (e, s, t, compose(s, t), compose(t, s), compose(s, compose(t, s)))
    require(len(set(basis)) == 6, 'six distinct S3 labels')
    table = [[basis.index(compose(a, b)) for b in basis] for a in basis]
    require(table[1][2] == 3 and table[2][1] == 4 and table[1][1] == table[2][2] == 0,
            'S3 product orientation')
    return table


def zero(n):
    return [[0] * n for _ in range(n)]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def madd(a, b, field, sign=1):
    return [[(x + sign*y) % field for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def mmul(a, b, field):
    n, out = len(a), zero(len(a))
    for i in range(n):
        for k, value in enumerate(a[i]):
            if value:
                for j, other in enumerate(b[k]):
                    if other:
                        out[i][j] = (out[i][j] + value * other) % field
    return out


def rank(matrix, field):
    work = [row[:] for row in matrix]
    height, width, pivot_row = len(work), len(work[0]) if work else 0, 0
    for column in range(width):
        pivot = next((i for i in range(pivot_row, height) if work[i][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = pow(work[pivot_row][column], field - 2, field)
        work[pivot_row] = [(x * inverse) % field for x in work[pivot_row]]
        for i in range(height):
            if i != pivot_row and work[i][column]:
                scalar = work[i][column]
                work[i] = [(x - scalar*y) % field for x, y in zip(work[i], work[pivot_row])]
        pivot_row += 1
        if pivot_row == height:
            break
    return pivot_row


def inverse(matrix, field):
    n = len(matrix)
    work = [row[:] + tail for row, tail in zip(matrix, identity(n))]
    for column in range(n):
        pivot = next((i for i in range(column, n) if work[i][column]), None)
        require(pivot is not None, 'singular free scalar map')
        work[column], work[pivot] = work[pivot], work[column]
        scalar = pow(work[column][column], field - 2, field)
        work[column] = [(x * scalar) % field for x in work[column]]
        for i in range(n):
            if i != column and work[i][column]:
                scalar = work[i][column]
                work[i] = [(x - scalar*y) % field for x, y in zip(work[i], work[column])]
    result = [row[n:] for row in work]
    require(mmul(matrix, result, field) == mmul(result, matrix, field) == identity(n), 'free inverse')
    return result


def clean(poly):
    return {label: matrix for label, matrix in poly.items() if any(any(row) for row in matrix)}


def paid(coupling, label, cap, field, edge=False):
    amount = rank(coupling, field)
    if not edge:
        require(amount > 0, 'zero paid rank')
        require(amount <= cap, 'paid rank cap')
    return clean({0: madd(identity(len(coupling)), coupling, field, -1), label: coupling}), amount


def pmul(left, right, table, field):
    result = {}
    for a, matrix in left.items():
        for b, other in right.items():
            label, value = table[a][b], mmul(matrix, other, field)
            result[label] = madd(result.get(label, zero(len(matrix))), value, field)
    return clean(result)


def target(d, n):
    productive, spectator = zero(n), zero(n)
    for i in range(n):
        (productive if i < d else spectator)[i][i] = 1
    return clean({3: productive, 0: spectator})


def augmentation(poly, n, field):
    result = zero(n)
    for matrix in poly.values():
        result = madd(result, matrix, field)
    return result


def cut_rank(poly, n, positive, table, field):
    negative = [g for g in range(6) if g not in positive]
    block = []
    for i in range(n):
        for output in negative:
            row = []
            for j in range(n):
                for incoming in positive:
                    row.append(sum(matrix[i][j] for label, matrix in poly.items()
                                   if table[label][incoming] == output) % field)
            block.append(row)
    return rank(block, field)


def cut_checks(table):
    rows = []
    for field in (2, 3, 5):
        ranks, nonprojectors, checks = {}, 0, 0
        for cells in product(range(field), repeat=4):
            coupling = [list(cells[:2]), list(cells[2:])]
            amount = rank(coupling, field)
            ranks[amount] = ranks.get(amount, 0) + 1
            nonprojectors += int(mmul(coupling, coupling, field) != coupling)
            for name, positive, isolated in (('s', (0, 2), 1), ('t', (0, 1), 2)):
                for label in (1, 2):
                    factor, measured = paid(coupling, label, 2, field, edge=True)
                    actual = cut_rank(factor, 2, positive, table, field)
                    require(measured == amount and actual == (2*amount if label == isolated else 0),
                            'selective cut rank')
                    checks += 1
        scalar = [[1, 1], [1, 0]]
        require(rank(scalar, field) == 2, 'free scalar example')
        for positive in ((0, 2), (0, 1)):
            require(cut_rank({0: scalar}, 2, positive, table, field) == 0, 'free scalar cut')
        require(ranks.get(0) == 1 and nonprojectors > 0, 'arbitrary coupling domain')
        rows.append(dict(field=field, matrices=field**4, rank_histogram=ranks,
                         nonprojectors=nonprojectors, gate_cut_checks=checks,
                         zero_coupling_is_edge_not_paid=True))
    return rows


def mixed(matrix, productive):
    return any(matrix[i][j] for i in range(len(matrix)) for j in range(len(matrix))
               if (i < productive) != (j < productive))


def word(d, cap, field, order=(1, 2)):
    n = d + 2
    left, right = identity(n), identity(n)
    left[0][d], right[d+1][0] = 1, 1
    gauge = mmul(left, right, field)
    instructions, calls = [['scalar', gauge]], []
    for start in range(0, d, cap):
        projector = zero(n)
        for i in range(start, min(start + cap, d)):
            projector[i][i] = 1
        calls += [(label, projector, start) for label in order]
    for index, (label, projector, start) in enumerate(calls):
        coupling = mmul(mmul(inverse(gauge, field), projector, field), gauge, field)
        instructions.append(['paid', label, coupling])
        if index + 1 == len(calls):
            scalar = inverse(gauge, field)
        else:
            scalar = identity(n)
            a, b = (start, d) if index % 2 == 0 else (d+1, start)
            scalar[a][b] = 1
        instructions.append(['scalar', scalar])
        gauge = mmul(gauge, scalar, field)
    require(gauge == identity(n), 'gauge return')
    return instructions


def execute(instructions, d, cap, field, table):
    n, result = d + 2, {0: identity(d + 2)}
    ranks, labels, coupled, interleaved = [], [], 0, 0
    for index, instruction in enumerate(instructions):
        if instruction[0] == 'scalar':
            matrix = instruction[1]
            require(rank(matrix, field) == n, 'free scalar rank')
            if 0 < index < len(instructions)-1:
                interleaved += int(mixed(matrix, d))
            factor = {0: matrix}
        else:
            require(instruction[0] == 'paid', 'instruction kind')
            factor, amount = paid(instruction[2], instruction[1], cap, field)
            ranks.append(amount)
            labels.append(LABELS[instruction[1]])
            coupled += int(mixed(instruction[2], d))
        result = pmul(result, factor, table, field)
    return result, ranks, labels, coupled, interleaved


def price(name, cap):
    return [F(0)] + [F(0) if name == 'zero' else F(k) if name == 'linear'
                    else F(1) if name == 'flat' else F(k, k+1) for k in range(1, cap+1)]


def packed(demand, cap, prices):
    return (demand // cap) * prices[cap] + prices[demand % cap]


def packing_dp(demand, cap, prices):
    values, witnesses = [F(0)], [[]]
    for amount in range(1, demand+1):
        choices = [(prices[k] + values[max(0, amount-k)],
                    [k] + witnesses[max(0, amount-k)]) for k in range(1, cap+1)]
        value, witness = min(choices, key=lambda x: (x[0], x[1]))
        values.append(value)
        witnesses.append(witness)
    return values[-1], witnesses[-1]


def rational(value):
    return [value.numerator, value.denominator]


def price_checks():
    rows = []
    for cap in range(1, 7):
        for d in range(1, 7):
            for name in ('zero', 'linear', 'flat', 'hyperbolic'):
                prices = price(name, cap)
                optimum, witness = packing_dp(d, cap, prices)
                expected = packed(d, cap, prices)
                require(optimum == expected, 'packing tariff')
                rows.append(dict(d=d, cap=cap, price=name, exact_st_tariff=rational(2*expected),
                                 packing_witness=witness))
    sample = price('hyperbolic', 2)
    require(2*packed(3, 2, sample) == F(7, 3), 'credited three-role control')
    require(2*packed(5, 2, sample) == F(11, 3) and packed(10, 2, sample) == F(10, 3),
            'five-role tariff distinction')
    return rows


def endpoint_rows(table):
    rows = []
    for field in (2, 3, 5):
        for d in range(1, 7):
            for cap in range(1, 7):
                instructions = word(d, cap, field)
                actual, ranks, labels, coupled, interleaved = execute(instructions, d, cap, field, table)
                expected = target(d, d+2)
                require(actual == expected, 'full formal endpoint')
                require(coupled > 0 and interleaved > 0, 'genuine dirty mixing')
                for positive in ((0, 2), (0, 1)):
                    require(cut_rank(actual, d+2, positive, table, field) == 2*d, 'target cut rank')
                for name in ('zero', 'linear', 'flat', 'hyperbolic'):
                    prices = price(name, cap)
                    require(sum((prices[k] for k in ranks), F(0)) == 2*packed(d, cap, prices),
                            'actual word tariff')
                rows.append(dict(field=field, d=d, cap=cap, dirty_spectators=2,
                                 call_ranks=ranks, call_labels=labels, dirty_coupled_calls=coupled,
                                 mixed_interleaved_scalars=interleaved, word_sha256=digest(instructions),
                                 complete_endpoint_sha256=digest(sorted(actual.items()))))
    require(len(rows) == 108, 'complete finite endpoint domain')
    return rows


def witness(actual, expected, n):
    for label in range(6):
        a, e = actual.get(label, zero(n)), expected.get(label, zero(n))
        for i in range(n):
            for j in range(n):
                if a[i][j] != e[i][j]:
                    return dict(label=LABELS[label], output_role=i, input_role=j,
                                actual=a[i][j], expected=e[i][j])
    raise ValueError('missing differing coefficient')


def bad_endpoint(name, instructions, table):
    actual, _, _, _, _ = execute(instructions, 5, 2, 5, table)
    expected = target(5, 7)
    require(actual != expected, 'endpoint mutation accepted: ' + name)
    return dict(name=name, outcome='DETECTED_FULL_FORMAL_DIFFERENCE',
                witness=witness(actual, expected, 7), augmentation_identity=augmentation(actual, 7, 5) == identity(7))


def controls(table):
    original = word(5, 2, 5)
    omitted = original[:]
    del omitted[next(i for i, ins in enumerate(omitted) if ins[0] == 'paid')]
    rows = [bad_endpoint('omitted_paid_call', omitted, table),
            bad_endpoint('wrong_st_order', word(5, 2, 5, (2, 1)), table)]
    leak = zero(7)
    leak[5][0] = 1
    row = bad_endpoint('dirty_leak_invisible_to_augmentation', original + [['paid', 1, leak]], table)
    require(row['augmentation_identity'] and row['witness']['output_role'] >= 5, 'dirty leak witness')
    rows.append(row)
    larger = word(5, 5, 5)
    actual, ranks, _, _, _ = execute(larger, 5, 5, 5, table)
    require(actual == target(5, 7) and ranks == [5, 5], 'larger-cap actual endpoint')
    larger_cost = sum((price('hyperbolic', 5)[k] for k in ranks), F(0))
    require(larger_cost < 2*packed(5, 2, price('hyperbolic', 2)), 'rank-cap price distinction')
    try:
        execute(larger, 5, 2, 5, table)
    except ValueError as error:
        require(str(error) == 'paid rank cap', 'wrong cap-control reason')
        rows.append(dict(name='larger_rank_not_free_workspace', outcome='REJECTED', reason=str(error),
                         admitted_cap=2, attempted_ranks=ranks, legal_cap5_cost=rational(larger_cost)))
    else:
        raise ValueError('rank-cap mutant accepted')
    for name, prices, demand in (('nonconcave_price', [F(0), F(1), F(4)], 2),
                                ('nonmonotone_price', [F(0), F(2), F(1)], 1)):
        best, chosen = packing_dp(demand, 2, prices)
        floor = packed(demand, 2, prices)
        require(best < floor, 'price-hypothesis witness')
        rows.append(dict(name=name, outcome='PACKING_LEMMA_FAILS_OUTSIDE_PREMISE',
                         demand=demand, ranks=chosen, actual_cost=rational(best), false_bound=rational(floor)))
    try:
        paid(zero(2), 1, 2, 5)
    except ValueError as error:
        require(str(error) == 'zero paid rank', 'wrong zero-rank reason')
        rows.append(dict(name='zero_matrix_not_a_paid_call', outcome='REJECTED', reason=str(error)))
    else:
        raise ValueError('zero paid rank accepted')
    return rows


def calculate():
    sources = authenticate()
    table = group_table()
    return dict(status='PASS_A2_ST_ALL_CAP_TARIFF', schema_version=1,
                source_sha256=sources, source_programs_executed=False, group_labels=LABELS,
                group_multiplication=table, selective_cut_checks=cut_checks(table),
                complete_endpoints=endpoint_rows(table), price_cases=price_checks(), controls=controls(table),
                scope='Finite all-cap st formal tariff corroboration; native/physical bill unprovided.')


def main():
    require(sys.argv[1:] in ([], ['--emit']), 'only optional --emit is supported')
    packet = calculate()
    if not sys.argv[1:]:
        require(canonical(load((PACKAGE / 'RESULT.json').read_bytes())) == canonical(packet),
                'retained complete result mismatch')
    print(canonical(packet).decode())


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print('FAIL_A2_ST_ALL_CAP_TARIFF: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
