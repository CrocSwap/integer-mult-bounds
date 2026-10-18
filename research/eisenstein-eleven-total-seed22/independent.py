"""Independent coordinate and direct-factorization checks. Apache-2.0.
Charles Bethin, with substantial OpenAI Codex assistance.
No predecessor geometry or primary traversal functions are imported here.
"""
from fractions import Fraction
from itertools import combinations
from collections import defaultdict


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rref(rows, width):
    a = [[Fraction(x) for x in row] for row in rows]
    pivots = []
    h = 0
    for j in range(width):
        k = next((i for i in range(h, len(a)) if a[i][j]), None)
        if k is None:
            continue
        a[h], a[k] = a[k], a[h]
        scale = a[h][j]
        a[h] = [x / scale for x in a[h]]
        for i in range(len(a)):
            if i != h and a[i][j]:
                scale = a[i][j]
                a[i] = [x - scale*y for x, y in zip(a[i], a[h])]
        pivots.append(j)
        h += 1
        if h == len(a):
            break
    return a[:h], pivots


def complement(rows, width):
    a, pivots = rref(rows, width)
    out = []
    for j in range(width):
        if j in pivots:
            continue
        v = [Fraction(0)] * width
        v[j] = 1
        for row, p in zip(a, pivots):
            v[p] = -row[j]
        out.append(v)
    return out


def dot(x, y):
    return sum(a*b for a, b in zip(x, y))


def check_frames(lines, frames):
    full = (1 << len(lines)) - 1
    require(sum(frames) == full and all(f.bit_count() == 4 for f in frames), 'partition')
    require(len(set(frames)) == 10, 'frame count')
    for f in frames:
        ports = [i for i in range(40) if f >> i & 1]
        rows = [v for i in ports for v in lines[i]]
        require(len(rref(rows, 8)[0]) == 8, 'frame spanning')
        for i, j in combinations(ports, 2):
            require(all(dot(x, y) == 0 for x in lines[i] for y in lines[j]), 'frame orthogonality')


def check_complements(lines, frames, low):
    # Canonicalize each local bit pattern by numeric minimum, independently of
    # the primary check's least-bit pivot elimination.
    buckets = defaultdict(list)
    for mask, rank in low.items():
        signature = tuple(min(mask & f, f ^ (mask & f)) for f in frames)
        buckets[signature].append((mask, rank))
    support_count = pair_count = group_count = 0
    for entries in buckets.values():
        if len(entries) < 2:
            continue
        group_count += 1
        spaces = []
        for mask, rank in entries:
            rows = [v for i in range(40) if mask >> i & 1 for v in lines[i]]
            null = complement(rows, 8)
            require(len(null) == 8 - 2*rank, 'independent support rank')
            spaces.append(null)
            support_count += 1
        for a, b in combinations(spaces, 2):
            require(all(dot(x, y) == 0 for x in a for y in b), 'complement orthogonality')
            pair_count += 1
        require(sum(map(len, spaces)) <= 8, 'rational deficit bound')
    return {'multi_member_cosets': group_count, 'complements_checked': support_count,
            'complement_pairs_checked': pair_count, 'independent_coset_count': len(buckets)}


def small_factorizations():
    # q=2,d=2. Two orthogonal bases, no frame-code reduction or coset lemma.
    # Exhaust every ordered pair of nonempty binary supports: 15^2 rectangles.
    # Exhaust every ordered pair of rectangles, then test the necessary third.
    vectors = [(1, 0), (0, 1), (1, 1), (1, -1)]
    rectangles = {}
    for r in range(1, 16):
        for a in range(1, 16):
            rows = [i for i in range(4) if r >> i & 1]
            cols = [i for i in range(4) if a >> i & 1]
            matrix = sum(1 << (4*i+j) for i in rows for j in cols)
            gram = [[dot(vectors[i], vectors[j]) for j in cols] for i in rows]
            cost = len(rref(gram, len(cols))[0])
            rectangles[matrix] = cost
    target = sum(1 << (4*i+j) for i in range(4) for j in range(4) if i//2 == j//2)
    minima = [rectangles.get(target)]
    best2 = best3 = 100
    exact2 = exact3 = 0
    for x, cx in rectangles.items():
        for y, cy in rectangles.items():
            if x ^ y == target:
                best2 = min(best2, cx+cy)
                exact2 += 1
            z = target ^ x ^ y
            if z in rectangles:
                best3 = min(best3, cx+cy+rectangles[z])
                exact3 += 1
    minima.extend([best2, best3])
    require(minima == [None, 4, 4], 'direct small factorization minimum')
    # A full-span/full-span rectangle costs dimension two, not one.
    require(rectangles[(1 << 16)-1] == 2, 'underpriced full-span control')
    return {'ports': 4, 'rectangles': len(rectangles), 'ordered_pairs': len(rectangles)**2,
            'exact_two_term_decompositions': exact2, 'exact_three_term_decompositions': exact3,
            'minimum_charge_by_active_terms_1_2_3': minima}


def independent_supports(lines):
    """Independent flat coverage by all 1-, 2-, 3-port generator sets.

    Every input row has norm sqrt(8). Every minor of at most eight rows
    has absolute determinant <= sqrt(8)^8 = 4096 < 65537. Thus rank over
    this prime agrees with rational rank, including all membership tests.
    No rank-adjoining traversal or predecessor row reduction is used.
    """
    prime = 65537
    require(len(lines) == 40 and all(len(pair) == 2 for pair in lines), 'line dimensions')
    require(all(dot(row, row) == 8 for pair in lines for row in pair), 'minor norm bound')
    def reduce(rows):
        a = [[x % prime for x in row] for row in rows]
        h = 0
        for col in range(8):
            pivot = next((i for i in range(h, len(a)) if a[i][col]), None)
            if pivot is None:
                continue
            a[h], a[pivot] = a[pivot], a[h]
            scale = pow(a[h][col], -1, prime)
            a[h] = [(x*scale) % prime for x in a[h]]
            for i in range(len(a)):
                if i != h and a[i][col]:
                    scale = a[i][col]
                    a[i] = [(x-scale*y) % prime for x, y in zip(a[i], a[h])]
            h += 1
            if h == len(a):
                break
        return tuple(tuple(row) for row in a[:h])
    bases = set()
    tested = 0
    for size in (1, 2, 3):
        for ports in combinations(range(40), size):
            basis = reduce([v for i in ports for v in lines[i]])
            require(len(basis) in (2, 4, 6), 'proper rank parity')
            bases.add(basis)
            tested += 1
    flats = []
    for basis in bases:
        def member(row):
            row = [x % prime for x in row]
            for b in basis:
                pivot = next(i for i, x in enumerate(b) if x)
                scale = row[pivot]
                row = [(x-scale*y) % prime for x, y in zip(row, b)]
            return not any(row)
        mask = 0
        for i, pair in enumerate(lines):
            yes = [member(v) for v in pair]
            require(yes[0] == yes[1], 'independent J closure')
            if yes[0]:
                mask |= 1 << i
        flats.append((len(basis)//2, mask))
    require(len(set(flats)) == len(bases), 'independent flat distinction')
    low = {}
    for rank, mask in sorted(flats):
        ports = [i for i in range(40) if mask >> i & 1]
        for size in range(1, len(ports)+1):
            for subset in combinations(ports, size):
                support = sum(1 << i for i in subset)
                low.setdefault(support, rank)
    return low, {'prime': prime, 'minor_absolute_bound': 4096,
                 'generator_sets': tested, 'proper_nonzero_flats': len(flats),
                 'proper_nonempty_supports': len(low)}
