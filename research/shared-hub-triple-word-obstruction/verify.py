"""Exact shared-hub triple word checks.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Matrix, rank, degree-two and Laurent routines adapt Ali Romman's PR7695,
which retains CubeJerry's PR6782 and Ali Romman's PR7694 methods.
This is author-checked work, not independent source review.
"""
from fractions import Fraction
from math import factorial
from pathlib import Path
import hashlib
import json

PAIRS = ((6, 5), (5, 6), (7, 7), (12, 20), (20, 12), (28, 28))

def require(ok, message):
    if not ok:
        raise ValueError(message)


def basis(values):
    pivots = {}
    for value in values:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return tuple(pivots[i] for i in sorted(pivots, reverse=True))


def reduce_vector(value, pivots):
    for row in pivots:
        value = min(value, value ^ row)
    return value


def outer(x, y, width):
    return sum(y << (i * width) for i in range(width) if x >> i & 1)


def identity(width):
    return sum(1 << (i * width + i) for i in range(width))


def left_project(pair, matrix, width):
    x, y = pair
    row, mask = 0, (1 << width) - 1
    while y:
        bit = y & -y
        row ^= (matrix >> ((bit.bit_length() - 1) * width)) & mask
        y ^= bit
    return outer(x, row, width)


def rational_rank(rows):
    pivots = {}
    for original in rows:
        row = [Fraction(x) for x in original]
        for col in sorted(pivots):
            coefficient = row[col]
            if coefficient:
                row = [x - coefficient * y for x, y in zip(row, pivots[col])]
        nonzero = next((i for i, x in enumerate(row) if x), None)
        if nonzero is not None:
            lead = row[nonzero]
            pivots[nonzero] = [x / lead for x in row]
    return len(pivots)


def quadratic(order, exps, products):
    coefficients = {}
    supports = [[i for i, x in enumerate(row) if x % 2] for row in exps]
    for j in range(len(order)):
        for i in range(j):
            matrix = products[order[j], order[i]]
            if matrix:
                for a in supports[i]:
                    for b in supports[j]:
                        monomial = (min(a, b), max(a, b))
                        coefficients[monomial] = coefficients.get(monomial, 0) ^ matrix
    return {key: value for key, value in coefficients.items() if value}


def laurent(order, exps, pairs, width):
    """Multiply the full matrices with exact integer exponent tuples."""
    zero = (0,) * len(exps[0])
    out = {zero: identity(width)}
    for kind, exponent in zip(order, exps):
        new = {}
        for key, matrix in out.items():
            projected = left_project(pairs[kind], matrix, width)
            new[key] = new.get(key, 0) ^ matrix ^ projected
            shifted = tuple(x + y for x, y in zip(key, exponent))
            new[shifted] = new.get(shifted, 0) ^ projected
        out = {key: value for key, value in new.items() if value}
    return out


def orders(counts):
    remaining = list(counts)
    word = []
    def visit():
        if len(word) == sum(counts):
            yield tuple(word)
        else:
            for kind, number in enumerate(remaining):
                if number:
                    remaining[kind] -= 1
                    word.append(kind)
                    yield from visit()
                    word.pop()
                    remaining[kind] += 1
    yield from visit()


def exponents(order):
    dimension = len(order) - 4
    out = [None] * len(order)
    free = 2
    for kind in range(6):
        slots = [i for i, value in enumerate(order) if value == kind]
        total = [0] * dimension
        total[kind // 3] = 1
        for slot in slots[:-1]:
            row = [0] * dimension
            row[free] = 1
            out[slot] = tuple(row)
            total[free] -= 1
            free += 1
        out[slots[-1]] = tuple(total)
    require(free == dimension, 'all quotient variables allocated')
    return out


def endpoint(exps, width):
    zero = (0,) * len(exps[0])
    u = (1, 0) + zero[2:]
    v = (0, 1) + zero[2:]
    uv = (1, 1) + zero[2:]
    out = {u: (1 << 0) | (1 << (width + 1)),
           uv: 1 << (2 * width + 2),
           v: (1 << (3 * width + 3)) | (1 << (4 * width + 4))}
    if width > 5:
        out[zero] = sum(1 << (i * width + i) for i in range(5, width))
    return out


def two_blocks(order):
    groups = [x // 3 for x in order]
    return sum(a != b for a, b in zip(groups, groups[1:])) == 1


def product_table(width):
    mask = ((1 << (width * width)) - 1) ^ identity(width)
    matrices = [outer(*p, width) for p in PAIRS]
    q = basis([p & mask for p in matrices])
    products = {(i, j): reduce_vector(left_project(PAIRS[i], matrices[j], width) & mask, q)
                for i in range(6) for j in range(6)}
    return matrices, q, products


def geometry():
    matrices, q, products = product_table(5)
    require(len(q) == 4, 'pattern dimension four')
    for i in range(6):
        for j in range(6):
            if i // 3 == j // 3:
                require(left_project(PAIRS[i], matrices[j], 5) == (matrices[i] if i == j else 0),
                        'each triple is orthogonal')
    cs = [products[i, j] ^ products[j, i] for i in range(3) for j in range(3, 6)]
    relations = []
    for mask in range(1, 512):
        value = 0
        for i, c in enumerate(cs):
            if mask >> i & 1:
                value ^= c
        if not value:
            relations.append(mask)
    require(relations == [511], 'only the sum of all cross-commutators vanishes')
    return {'pattern_rank': 4, 'cross_quotient_rank': len(basis(cs)),
            'cross_relation_masks': relations, 'cross_quotient_vectors': cs}


def word_census():
    domains = [(1, 1, 1, 1, 1, 1), (2, 1, 1, 1, 1, 1),
               (2, 1, 1, 2, 1, 1), (2, 2, 1, 1, 1, 1), (2, 2, 1, 2, 1, 1)]
    matrices, q, products = product_table(5)
    mask = ((1 << 25) - 1) ^ identity(5)
    rows = []
    digest = hashlib.sha256()
    for counts in domains:
        seen = passed = 0
        for order in orders(counts):
            exps = exponents(order)
            degree2 = not quadratic(order, exps, products)
            actual = laurent(order, exps, PAIRS, 5)
            predicted = two_blocks(order)
            diagonal = not any(value & mask for value in actual.values())
            require(degree2 == predicted == diagonal, 'exact word classification')
            if predicted:
                require(actual == endpoint(exps, 5), 'full monomial endpoint')
            seen += 1
            passed += predicted
            digest.update(bytes(order) + bytes([predicted]))
        expected = 2 * factorial(sum(counts[:3])) * factorial(sum(counts[3:]))
        for count in counts:
            expected //= factorial(count)
        total = factorial(sum(counts))
        for count in counts:
            total //= factorial(count)
        require((seen, passed) == (total, expected), 'independent multinomial counts')
        rows.append({'multiplicities': counts, 'orders': seen, 'passing': passed})
    return {'domains': rows, 'order_status_sha256': digest.hexdigest(),
            'total_orders': sum(r['orders'] for r in rows),
            'total_passing': sum(r['passing'] for r in rows)}


def embed_vector(value, coordinates):
    return sum(1 << coordinates[i] for i in range(5) if value >> i & 1)


def difference_column(actual, expected, width):
    for exponent in sorted(set(actual) | set(expected)):
        difference = actual.get(exponent, 0) ^ expected.get(exponent, 0)
        if difference:
            column = next(j for j in range(width)
                          if any(difference >> (i * width + j) & 1 for i in range(width)))
            return {'exponent': exponent, 'input_column': column,
                    'output_mask': sum(1 << i for i in range(width)
                                       if difference >> (i * width + column) & 1)}
    raise ValueError('expected an actual input difference')


def larger_fixtures():
    rows = []
    counts_list = [(2, 2, 2, 2, 2, 2), (3, 1, 2, 2, 4, 1), (4, 3, 2, 1, 2, 3)]
    for width, coordinates in [(5, (0, 1, 2, 3, 4)), (7, (6, 0, 4, 2, 5)),
                               (11, (1, 7, 9, 0, 5)), (17, (16, 3, 8, 11, 1))]:
        pairs = tuple((embed_vector(x, coordinates), embed_vector(y, coordinates)) for x, y in PAIRS)
        for counts in counts_list:
            a = tuple(k for repeat in range(max(counts)) for k in (2, 0, 1) if counts[k] > repeat)
            b = tuple(k for repeat in range(max(counts)) for k in (4, 5, 3) if counts[k] > repeat)
            for reverse in [False, True]:
                order = b + a if reverse else a + b
                exps = exponents(order)
                require(rational_rank(exps) == len(order) - 4, 'actual paid group rank')
                zero = (0,) * len(exps[0])
                expected = {}
                for i in range(width):
                    e = zero
                    if i in coordinates:
                        slot = coordinates.index(i)
                        e = ((1, 0) if slot < 2 else (0, 1) if slot > 2 else (1, 1)) + zero[2:]
                    expected[e] = expected.get(e, 0) | (1 << (i * width + i))
                allocations = [(0,), (1,), (2, 5), (3,), (4,)]
                assigned = []
                for slot, kinds in enumerate(allocations):
                    indices = [i for i, kind in enumerate(order) if kind in kinds]
                    assigned.extend(indices)
                    total = tuple(sum(exps[i][j] for i in indices) for j in range(len(zero)))
                    target = ((1, 0) if slot < 2 else (0, 1) if slot > 2 else (1, 1)) + zero[2:]
                    require(total == target, 'exact disjoint paid subset for each target')
                require(sorted(assigned) == list(range(len(order))), 'each paid call assigned once')
                actual = laurent(order, exps, pairs, width)
                require(actual == expected, 'all original and spectator inputs')
                cut = len(b) if reverse else len(a)
                mutated = list(order)
                mutated[cut - 1], mutated[cut] = mutated[cut], mutated[cut - 1]
                mutant_exps = list(exps)
                mutant_exps[cut - 1], mutant_exps[cut] = mutant_exps[cut], mutant_exps[cut - 1]
                witness = difference_column(laurent(mutated, mutant_exps, pairs, width), expected, width)
                rows.append({'width': width, 'coordinates': coordinates, 'multiplicities': counts,
                             'reverse_blocks': reverse, 'calls': len(order),
                             'crossed_boundary_witness': witness})
    return rows


def boundary_controls():
    legal = (0, 1, 2, 3, 4, 5)
    exps = exponents(legal)
    expected = endpoint(exps, 5)
    _, _, products = product_table(5)
    controls = {}
    for kind in [0, 3]:
        changed = list(exps)
        row = list(changed[kind]); row[kind // 3] += 2; changed[kind] = tuple(row)
        require(rational_rank(changed) == 2, 'even-total control keeps four relations')
        require(not quadratic(legal, changed, products), 'quadratic quotient alone misses exact total')
        actual = laurent(legal, changed, PAIRS, 5)
        controls['nonzero_even_total_' + str(kind)] = difference_column(actual, expected, 5)
    interleaved = (0, 3, 1, 4, 2, 5)
    proper = exponents(interleaved)
    doubled = [tuple(2 * x for x in e) for e in proper]
    require(quadratic(interleaved, proper, products), 'correct paid group rejects interleaving')
    require(not quadratic(interleaved, doubled, products), 'wrong ambient group hides degree two')
    controls['wrong_ambient_group'] = difference_column(laurent(interleaved, doubled, PAIRS, 5),
                                                       laurent(legal, [tuple(2*x for x in e) for e in exps], PAIRS, 5), 5)
    five_exps = [(0,) if k < 3 else (1,) for k in interleaved]
    actual = laurent(interleaved, five_exps, PAIRS, 5)
    mask = ((1 << 25) - 1) ^ identity(5)
    require(not any(m & mask for m in actual.values()), 'five-relation interleaved diagonal control')
    require(6 - rational_rank(five_exps) == 5, 'five relations, three zero calls')
    controls['five_relations'] = {'word': interleaved, 'paid_exponents': five_exps,
                                  'endpoint': sorted(actual.items()), 'zero_calls': 3}
    palindrome = (0, 3, 1, 4, 2, 5, 5, 2, 4, 1, 3, 0)
    inverse_exps = []
    for i, kind in enumerate(palindrome):
        row = [0] * 6; row[kind] = 1 if i < 6 else -1; inverse_exps.append(tuple(row))
    require(len(palindrome) - rational_rank(inverse_exps) == 6, 'six relations')
    require(laurent(palindrome, inverse_exps, PAIRS, 5) == {(0,) * 6: identity(5)},
            'interleaved identity with every call nonzero')
    controls['six_relation_nonzero_identity'] = {'word': palindrome, 'paid_exponents': inverse_exps}
    omitted = laurent(legal[:-1], exps[:-1], PAIRS, 5)
    controls['omitted_type'] = difference_column(omitted, expected, 5)
    wrong_target = dict(expected)
    hub = 1 << 12
    wrong_target[(1, 1)] ^= hub
    wrong_target.pop((1, 1))
    wrong_target[(1, 0)] ^= hub
    controls['wrong_hub_target'] = difference_column(expected, wrong_target, 5)
    return controls


def compute():
    return {'status': 'PASS_SHARED_HUB_TRIPLE_WORD_OBSTRUCTION',
            'geometry': geometry(), 'words': word_census(),
            'larger_fixtures': larger_fixtures(), 'controls': boundary_controls()}

if __name__ == '__main__':
    actual = json.loads(json.dumps(compute()))
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(actual == expected, 'exact committed receipt')
    print(actual['status'])
    print('68760 complete Laurent words; 1584 two-block endpoints')
    print('24 larger fixtures; disjoint paid-subset targets and all boundary controls pass')
