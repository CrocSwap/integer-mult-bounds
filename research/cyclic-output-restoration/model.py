"""Order-three fixed-reader interface. Ross Richardson / OpenAI Codex, Apache-2.0."""
from functools import lru_cache


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dimensions(matrix):
    require(isinstance(matrix, list) and bool(matrix), 'nonempty matrix required')
    n, m = len(matrix), len(matrix[0])
    require(n % 3 == m % 3 == 0 and m > 0, 'dimensions must be positive multiples of three')
    require(all(len(row) == m for row in matrix), 'ragged matrix')
    require(all(type(x) is int for row in matrix for x in row), 'exact integer entries required')
    return m // 3, n // 3


def admitted(matrix):
    """RP=QR, with P,Q sending (a,b,c) to (c,a,b) on every block."""
    m, n = dimensions(matrix)
    return all(matrix[r][3*(c//3)+(c+1)%3] == matrix[3*(r//3)+(r-1)%3][c]
               for r in range(3*n) for c in range(3*m))


@lru_cache(None, typed=True)
def plan(k, workspace_cost, output_cost):
    """Minimum cost in the complete-register P^u,Q^v boundary alphabet."""
    require(type(k) is int and k >= 1, 'positive child count required')
    require(type(workspace_cost) is int and workspace_cost > 0, 'positive workspace price required')
    require(type(output_cost) is int and output_cost > 0, 'positive output price required')
    states = {t: ((workspace_cost + output_cost)*(t != 0), ((t, t),)) for t in range(3)}
    for i in range(k):
        following = {}
        for s in ([0] if i == k-1 else range(3)):
            candidates = []
            for t, (cost, gaps) in states.items():
                u, v = (s-t-1) % 3, (s-t) % 3
                candidates.append((cost+workspace_cost*(u != 0)+output_cost*(v != 0), gaps+((u, v),)))
            following[s] = min(candidates)
        states = following
    return states[0]


def rotate(start, blocks, power):
    require(power in (0, 1, 2), 'invalid cyclic power')
    word = []
    if power:
        for b in range(blocks):
            word.append(('R', start+3*b, power))
    return word


def inverse(word):
    return [(('A', op[1], op[2], -op[3]) if op[0] == 'A'
             else ('R', op[1], (-op[2]) % 3)) for op in reversed(word)]


def matrix_of(node):
    if 'matrix' in node:
        r = node['matrix']
        require(admitted(r), 'reader does not intertwine the cyclic actions')
        return [row[:] for row in r]
    require(set(node) == {'children'} and bool(node['children']), 'nonempty child list required')
    matrices = [matrix_of(c) for c in node['children']]
    require(all(dimensions(r) == dimensions(matrices[0]) for r in matrices), 'child dimension mismatch')
    return [[sum(r[i][j] for r in matrices) for j in range(len(matrices[0][0]))] for i in range(len(matrices[0]))]


def depth(node):
    return 0 if 'matrix' in node else 1+max(map(depth, node['children']))


def reader(node, source, output, free, m, n, eager=False):
    if 'matrix' in node:
        word = []
        for i, row in enumerate(node['matrix']):
            for j, value in enumerate(row):
                word.extend([('A', output+i, source+j, 1 if value > 0 else -1)]*abs(value))
    else:
        word = echo(node['children'], source, output, free, m, n, eager)
    return word + rotate(source, m, 1)


def batch(children, source, output, free, m, n, eager=False):
    gaps = ((0, 0),)+((2, 0),)*len(children) if eager else plan(len(children), m, n)[1]
    word = []
    for i, (u, v) in enumerate(gaps):
        word += rotate(source, m, u)+rotate(output, n, v)
        if i < len(children):
            word += reader(children[i], source, output, free, m, n, eager)
    return word


def echo(children, source, output, free, m, n, eager=False):
    b = batch(children, free, output, free+3*m, m, n, eager)
    copy = [('A', free+i, source+i, 1) for i in range(3*m)]
    return copy+b+inverse(copy)+inverse(b)


def compile_word(node, contract='echo', eager=False):
    r = matrix_of(node)
    m, n = dimensions(r)
    require(contract in ('echo', 'reader'), 'invalid contract')
    require(contract == 'reader' or 'children' in node, 'echo needs children')
    args = (3*n, 0, 3*n+3*m, m, n, eager)
    word = reader(node, *args) if contract == 'reader' else echo(node['children'], *args)
    return word, 3*n+(depth(node)+1)*3*m


def expand(word):
    """Six signed ADDs per triple rotation, with no extra register or NEG.

    The power-two circuit is two adjacent signed swaps; its literal inverse
    is power one. Credit the prior six-primitive upper bound in PR1145.
    """
    result = []
    for op in word:
        if op[0] == 'R':
            _, a, power = op
            b, c = a+1, a+2
            cycle = [('A', a, b, 1), ('A', b, a, -1), ('A', a, b, 1),
                     ('A', b, c, 1), ('A', c, b, -1), ('A', b, c, 1)]
            result += cycle if power == 2 else inverse(cycle)
        else:
            result.append(op)
    return result


def recurrence(node, contract='echo', eager=False):
    r = matrix_of(node)
    m, n = dimensions(r)
    if 'matrix' in node:
        require(contract == 'reader', 'leaf requires reader contract')
        return sum(abs(x) for row in r for x in row), m
    child = [recurrence(c, 'reader', eager) for c in node['children']]
    b = len(child)*m if eager else plan(len(child), m, n)[0]
    return 2*sum(a for a, s in child)+6*m, 2*sum(s for a, s in child)+2*b+(m if contract == 'reader' else 0)


def invoice(word):
    a = sum(op[0] == 'A' for op in word)
    g = sum(op[0] == 'N' for op in word)
    require(a+g == len(word), 'invoice expects expanded ADD/NEG word')
    position = travel = 0
    for op in word:
        visits = (op[2], op[1]) if op[0] == 'A' else (op[1],)
        for address in visits:
            travel += abs(address-position)
            position = address
    travel += position  # canonical cursor return
    return dict(add=a, neg=g, dispatch=a+g, reads=2*a+g, writes=a+g,
                descriptor_fields=4*a+2*g, address_travel=travel)
