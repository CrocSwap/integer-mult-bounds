"""Input-independent exact source preparation and dyadic nilpotent pages.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def need(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b):
    return tuple(tuple(sum((x*y for x, y in zip(row, col)), Q())
                       for col in zip(*b)) for row in a)


def inverse(a):
    n = len(a)
    rows = [list(row)+[Q(i == j) for j in range(n)] for i, row in enumerate(a)]
    for k in range(n):
        at = next((i for i in range(k, n) if rows[i][k]), None)
        need(at is not None, 'invertible admitted broad interior')
        rows[k], rows[at] = rows[at], rows[k]
        pivot = rows[k][k]
        rows[k] = [x/pivot for x in rows[k]]
        for i in range(n):
            if i != k:
                ratio = rows[i][k]
                rows[i] = [x-ratio*y for x, y in zip(rows[i], rows[k])]
    return tuple(tuple(row[n:]) for row in rows)


def sub(a, rows, columns):
    return tuple(tuple(a[i][j] for j in columns) for i in rows)


def norm(a):
    return max(sum(map(abs, row), Q()) for row in a)


def rounded(value, precision):
    value = Q(value)
    integer = (abs(value.numerator) << precision)//value.denominator
    return Q(-integer if value < 0 else integer, 1 << precision)


def broad_source(reference):
    """Small actual broad Reference Schur, not a relabelled narrow matrix."""
    origin, length, interior = 16, 4, (1, 2)
    boundary = (0, 3)
    source = reference.source_at.get(origin+interior[0])
    need(source is not None, 'selected broad interior start')
    coordinates, _, _ = reference.interior(source, len(interior))
    need(tuple(coordinates) == tuple(origin+i for i in interior),
         'original phase-pure broad interior')
    h = tuple(tuple(reference.entry('broad', origin+i, origin+j).value
                    for j in range(length)) for i in range(length))
    a, b, c, d = (sub(h, interior, interior), sub(h, interior, boundary),
                   sub(h, boundary, interior), sub(h, boundary, boundary))
    ai = inverse(a)
    correction = multiply(multiply(c, ai), b)
    f = tuple(tuple(x-y for x, y in zip(row, term)) for row, term in zip(d, correction))
    return f, dict(kind='broad', reference_sha256=reference.description_hash,
                   parameters=list(reference.spec.__dict__.values()), origin=origin,
                   length=length, I=list(interior), J=list(boundary),
                   H=[[str(x) for x in row] for row in h],
                   F=[[str(x) for x in row] for row in f],
                   interior_inverse_norm=str(norm(ai)), schur_norm=str(norm(f)),
                   scope='exact finite rational source; no whole broad word or ideal comparison')


def factors(matrix, block, precision, *, pre_round=True):
    n = len(matrix)
    need(n > 0 and all(len(row) == n for row in matrix), 'square forward matrix')
    need(type(block) is int and block > 0 and block & (block-1) == 0
         and type(precision) is int and precision >= 0, 'dyadic lift and integer grid')
    need(all(not Q(x) or abs(2*i-(2*j+1)) <= block
             for i, row in enumerate(matrix) for j, x in enumerate(row)),
         'funded exact forward bandwidth before rounding')
    data = tuple(tuple(rounded(x, precision) if pre_round else Q(x) for x in row)
                 for row in matrix)
    extent = 2*n
    nilpotent = tuple(tuple(-data[i//2][j//2] if i % 2 == 0 and j % 2 == 1 else Q()
                            for j in range(extent)) for i in range(extent))
    need(all(not x or abs(i-j) <= block for i, row in enumerate(nilpotent)
             for j, x in enumerate(row)), 'funded original interleaved bandwidth')
    lower = tuple(tuple(Q(i == j)+(nilpotent[i][j] if i//block > j//block else 0)
                         for j in range(extent)) for i in range(extent))
    upper = tuple(tuple(Q(i == j)+(nilpotent[i][j] if i//block <= j//block else 0)
                         for j in range(extent)) for i in range(extent))
    return lower, upper


def expected_pages(matrix, block, precision, *, pre_round=True):
    """External direct mask observer; not used to supply physical page data."""
    lower, upper = factors(matrix, block, precision, pre_round=pre_round)
    n = len(lower)
    size = ((n+block-1)//block)*block
    def padded(a):
        return tuple(tuple(a[i][j] if i < n and j < n else Q(i == j)
                           for j in range(size)) for i in range(size))
    out = []
    for direction, a in enumerate((padded(lower), padded(upper))):
        if direction:
            a = tuple(tuple(reversed(row)) for row in reversed(a))
        diagonals, coupling = [], []
        for start in range(0, size, block):
            diagonals.extend(rounded(2*Q(i == j)-a[start+i][start+j], precision)
                             for i in range(block) for j in range(block))
            if start:
                coupling.extend(rounded(a[i][j], precision)
                                for i in range(start, start+block)
                                for j in range(start-block, start))
        out.extend((tuple(diagonals), tuple(coupling)))
    return tuple(out)


def physical_factors(matrix, block, precision, pool):
    """Serialize pre-rounded exact factors, then caller runs prepare_pages."""
    from cardinal_counts import Count
    from gaussian_matrix import Matrix
    from gaussian_rationals import Rational
    from ring_check_words import decode
    from ring_words import Signed
    from router_metadata import owned
    data = factors(matrix, block, precision)
    owners = []
    def make(value):
        return Rational(Signed(Count.literal(abs(value.numerator)), value < 0),
                        Count.literal(value.denominator))
    try:
        for a in data:
            with owned(Count.literal(len(a))) as (size,):
                owners.append(Matrix(size, size, pool,
                    lambda i, j, a=a: make(a[decode(i)][decode(j)])))
        return tuple(owners)
    except BaseException:
        for owner in owners:
            owner.close()
        raise


def rounded_oracle(matrix, rhs, block, precision):
    """Finite rational recurrence observer, independent of physical movement."""
    n, columns = len(matrix), len(rhs[0])
    banks = expected_pages(matrix, block, precision)
    size = ((2*n+block-1)//block)*block
    current = []
    for row in rhs:
        current.extend(([Q()]*columns, list(row)))
    current.extend([[Q()]*columns for _ in range(size-2*n)])
    for direction in range(2):
        if direction:
            current.reverse()
        output = []
        diagonal, coupling = banks[2*direction:2*direction+2]
        for start in range(0, size, block):
            residual = current[start:start+block]
            if start:
                offset = (start-block)*block
                c = tuple(coupling[offset+i*block:offset+(i+1)*block] for i in range(block))
                term = multiply(c, output[-block:])
                residual = [[rounded(x-y, precision) for x, y in zip(row, part)]
                            for row, part in zip(residual, term)]
            offset = start*block
            d = tuple(diagonal[offset+i*block:offset+(i+1)*block] for i in range(block))
            output.extend([rounded(x, precision) for x in row] for row in multiply(d, residual))
        current = output
    current.reverse()
    need(tuple(tuple(current[2*i+1]) for i in range(n)) == tuple(tuple(row) for row in rhs),
         'oracle preserved sources')
    return tuple(tuple(current[2*i]) for i in range(n))
