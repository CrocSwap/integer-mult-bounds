"""Literal finite controls in the retained F2[group] superposition model."""
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def mat(rows):
    return tuple(tuple(Q(x) for x in row) for row in rows)


def identity(n):
    return mat([[int(i == j) for j in range(n)] for i in range(n)])


def multiply(a, b):
    return mat([[sum(a[i][k]*b[k][j] for k in range(len(b)))
                 for j in range(len(b[0]))] for i in range(len(a))])


def shear(a):
    m = len(a)
    return mat([[int(i == j) if (i < m) == (j < m) else
                 a[i][j-m] if i < m else 0 for j in range(2*m)]
                for i in range(2*m)])


def lower(k):
    m = len(k)
    return mat([[int(i == j) if (i < m) == (j < m) else
                 k[i-m][j] if j < m else 0 for j in range(2*m)]
                for i in range(2*m)])


def rank(a, prime=None):
    a = [list(row) for row in a]
    if prime:
        a = [[Q(x).numerator*pow(Q(x).denominator, -1, prime) % prime for x in row] for row in a]
    r = 0
    for c in range(len(a[0])):
        pivot = next((j for j in range(r, len(a)) if a[j][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        divisor = a[r][c]
        a[r] = [(x*pow(divisor, -1, prime)) % prime if prime else Q(x)/divisor for x in a[r]]
        for j in range(r+1, len(a)):
            factor = a[j][c]
            a[j] = [(x-factor*y) % prime if prime else x-factor*y for x, y in zip(a[j], a[r])]
        r += 1
    return r


def fixture():
    a1 = mat([[1, '-1/2'], [0, 0]])
    a2 = mat([[0, '1/2'], [0, 1]])
    k = mat([[0, '1/2'], [2, 0]])
    l, li = lower(k), lower(mat([[-x for x in row] for row in k]))
    singular = mat([[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    matrices = [shear(a1), shear(a2), l, li, singular]
    operations = [('mix', 0, 1), ('map', 0, 2), ('map', 1, 2),
                  ('map', 0, 0), ('map', 0, 1), ('map', 1, 0), ('map', 1, 1),
                  ('map', 0, 3), ('map', 1, 3), ('mix', 0, 1), ('map', 2, 4)]
    return matrices, operations


def replay(matrices, operations):
    """Chronological left multiplication; every matrix entry is a formal F2 support."""
    unit = identity(4)
    state = [[{unit} if i == j else set() for j in range(3)] for i in range(3)]
    for kind, target, argument in operations:
        if kind == 'mix':
            state[target] = [a ^ b for a, b in zip(state[target], state[argument])]
        else:
            # Left multiplication is injective because these matrices are invertible.
            g = mat(matrices[argument])
            need(rank(g) == 4, 'literal register map must be rationally invertible')
            state[target] = [{multiply(g, term) for term in entry} for entry in state[target]]
    endpoint = multiply(multiply(mat(matrices[3]), shear(identity(2))), mat(matrices[2]))
    expected = [[{endpoint} if i == j and i < 2 else
                 {mat(matrices[4])} if i == j == 2 else set() for j in range(3)] for i in range(3)]
    need(state == expected, 'complete formal dirty-input endpoint')
    return state
