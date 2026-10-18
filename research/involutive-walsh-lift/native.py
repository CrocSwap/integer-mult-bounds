"""Check exact native operators without the producer's Clifford compiler.

Circuits list gates in execution order. Pauli action determines a Clifford
operator up to a scalar. An exact nine-bit state image fixes that scalar.
"""

from fractions import Fraction
from functools import lru_cache


def require(condition, label):
    if not condition:
        raise ValueError(label)


def parity(value):
    return value.bit_count() % 2


def mul(matrix, vector):
    return sum(parity(row & vector) << i for i, row in enumerate(matrix))


def transpose(matrix):
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(matrix)) for j in range(len(matrix)))


def inverse(matrix):
    n = len(matrix)
    rows = [row | (1 << (n+i)) for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i] >> j & 1), None)
        require(pivot is not None, 'singular binary chart')
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(n):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    require([row & ((1 << n)-1) for row in rows] == [1 << i for i in range(n)], 'binary inverse')
    return tuple(row >> n for row in rows)


def extend(vectors, n):
    columns, pivots = [], {}
    for value in tuple(vectors) + tuple(1 << i for i in range(n)):
        reduced = value
        while reduced:
            j = reduced.bit_length()-1
            if j not in pivots:
                pivots[j] = reduced
                columns.append(value)
                break
            reduced ^= pivots[j]
    require(len(columns) == n, 'frame basis extension')
    return tuple(columns)


def adjoint(circuit):
    out = []
    for gate in reversed(circuit):
        if gate[0] == 'P':
            out.append(('P', inverse(gate[1])))
        elif gate[0] == 'D':
            out.append(('D', gate[1], tuple(-a % 4 for a in gate[2])))
        elif gate[0] == 'C':
            out.append(('C', gate[1], -gate[2]))
        elif gate[0] == 'phase':
            out.append(('phase', -gate[1] % 4))
        else:
            require(gate[0] == 'X', 'adjoint gate type')
            out.append(gate)
    return tuple(out)


def fourier(rank):
    return tuple(('C', 1 << i, 1) for i in range(rank))


def frame(vectors, n):
    rank = len(vectors)
    if rank == 0:
        return ()
    if rank == n:
        return fourier(n)
    matrix = transpose(extend(vectors, n))
    columns = transpose(inverse(matrix))
    quadratic = tuple((1 << i) ^ sum(parity(a & b) << j for j, b in enumerate(columns)) for i, a in enumerate(columns))
    diagonal = tuple((row >> i) & 1 for i, row in enumerate(quadratic))
    chart = (('P', matrix), ('D', quadratic, diagonal))
    return adjoint(chart) + fourier(rank) + chart


def monomial(record):
    matrix = tuple(record['matrix_rows'])
    quadratic = tuple(record['quadratic_rows'])
    linear = tuple(record['linear_Z4'])
    require(transpose(quadratic) == quadratic, 'quadratic symmetry')
    require(len(matrix) == len(quadratic) == len(linear) and len(matrix) > 0, 'monomial dimension')
    require(all(a % 2 == (quadratic[i] >> i) & 1 for i, a in enumerate(linear)), 'diagonal parity')
    inverse(matrix)
    return (('D', quadratic, linear), ('P', matrix), ('X', record['offset']), ('phase', record['phase']))


def recipe(record):
    rank = record['rank']
    require(isinstance(rank, int) and 0 <= rank <= 9, 'child rank')
    if rank == 0:
        require(record['right'] is None, 'rank zero right factor')
        return monomial(record['left'])
    return monomial(record['right']) + fourier(rank) + monomial(record['left'])


def tableau(circuit, n=9):
    rows = [(1 << i, 0, 0) for i in range(n)] + [(0, 1 << i, 0) for i in range(n)]
    for gate in circuit:
        tag = gate[0]
        out = []
        inverse_transpose = transpose(inverse(gate[1])) if tag == 'P' else None
        for x, z, phase in rows:
            if tag == 'P':
                x, z = mul(gate[1], x), mul(inverse_transpose, z)
            elif tag == 'X':
                phase += 2 * parity(z & gate[1])
            elif tag == 'C':
                if parity(z & gate[1]):
                    x ^= gate[1]
                    phase += 3 * gate[2]
            elif tag == 'D':
                quadratic, linear = gate[1:]
                phase += sum(linear[i] for i in range(n) if x >> i & 1)
                phase += 2 * sum(parity((quadratic[i] >> (i+1)) & (x >> (i+1))) for i in range(n) if x >> i & 1)
                z ^= mul(quadratic, x)
            else:
                require(tag == 'phase', 'tableau gate type')
            out.append((x, z, phase % 4))
        rows = out
    return tuple(rows)


@lru_cache(maxsize=512)
def action(gate):
    if gate[0] == 'P':
        return tuple(mul(gate[1], x) for x in range(512))
    require(gate[0] == 'D', 'state action type')
    quadratic, linear = gate[1:]
    return tuple((sum(linear[i] for i in range(9) if x >> i & 1)
                  + 2 * sum(parity((quadratic[i] >> (i+1)) & (x >> (i+1))) for i in range(9) if x >> i & 1)) % 4 for x in range(512))


def rotate(pair, power):
    a, b = pair
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def state(circuit, basis=0):
    value = [(0, 0)] * 512
    value[basis] = (1, 0)
    denominator = 0
    for gate in circuit:
        tag = gate[0]
        if tag == 'P':
            moved = [(0, 0)] * 512
            for source, target in enumerate(action(gate)):
                moved[target] = value[source]
            value = moved
        elif tag == 'X':
            value = [value[x ^ gate[1]] for x in range(512)]
        elif tag == 'D':
            value = [rotate(pair, p) for pair, p in zip(value, action(gate))]
        elif tag == 'phase':
            value = [rotate(pair, gate[1]) for pair in value]
        elif tag == 'C':
            direction, sign = gate[1:]
            moved = []
            for x, (a, b) in enumerate(value):
                c, d = value[x ^ direction]
                moved.append((a-sign*b+c+sign*d, b+sign*a+d-sign*c))
            value = moved
            denominator += 1
        else:
            raise ValueError('state gate type')
        while denominator and all((a | b) % 2 == 0 for a, b in value):
            value = [(a//2, b//2) for a, b in value]
            denominator -= 1
    return value, denominator


def equal(actual, expected, label):
    require(tableau(actual) == tableau(expected), label + ': Pauli action')
    require(state(actual) == state(expected), label + ': global phase')


def scalar_cost(gate):
    if gate[0] in ('copy', 'clear'):
        return 1
    value = Fraction(*gate[-2:])
    numerator, denominator = abs(value.numerator), value.denominator
    require(numerator > 0 and denominator & (denominator-1) == 0, 'nonzero dyadic scalar')
    if gate[0] == 'scale':
        require(numerator & (numerator-1) == 0, 'dyadic scale unit')
        return abs(numerator.bit_length()-denominator.bit_length()) + (value < 0)
    require(gate[0] == 'add', 'scalar type')
    return 3 + numerator.bit_length()-1 + numerator.bit_count() + denominator.bit_length()-1
