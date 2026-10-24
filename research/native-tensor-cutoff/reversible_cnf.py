"""Compile three-literal CNF to a reversible five-role native identity test.

The width-five group-program construction is Barrington's classical method.
"""
from exact import need

IDENTITY = (0, 1, 2, 3, 4)
A = (1, 2, 3, 4, 0)
B = (1, 3, 0, 4, 2)
C = (4, 3, 1, 0, 2)


def compose(p, q):
    return tuple(p[q[i]] for i in range(5))


def inverse(p):
    return tuple(p.index(i) for i in range(5))


def conjugator(source, target):
    out = [None] * 5
    i = j = 0
    for _ in range(5):
        out[i] = j
        i, j = source[i], target[j]
    need(sorted(out) == list(range(5)), 'five-cycle conjugator')
    return tuple(out)


def invert_word(word):
    return [(variable, inverse(zero), inverse(one)) for variable, zero, one in reversed(word)]


def formula_word(formula, target=A):
    if type(formula) is bool:
        return [(None, target, target)] if formula else []
    if type(formula) is int:
        return [(abs(formula) - 1, IDENTITY, target)] if formula > 0 else [(abs(formula) - 1, target, IDENTITY)]
    op, *children = formula
    if op == 'not':
        return invert_word(formula_word(children[0], target)) + [(None, target, target)]
    if op == 'or':
        return formula_word(('not', ('and', ('not', children[0]), ('not', children[1]))), target)
    need(op == 'and', 'Boolean formula operation')
    f = conjugator(C, target)
    left_target = compose(f, compose(A, inverse(f)))
    right_target = compose(f, compose(B, inverse(f)))
    left, right = formula_word(children[0], left_target), formula_word(children[1], right_target)
    return left + right + invert_word(left) + invert_word(right)


def balanced(op, items, empty):
    if not items:
        return empty
    items = list(items)
    while len(items) > 1:
        items = [(op, items[i], items[i + 1]) if i + 1 < len(items) else items[i]
                 for i in range(0, len(items), 2)]
    return items[0]


def cnf_word(n, clauses):
    need(type(n) is int and n >= 1, 'CNF axis count')
    need(all(len(clause) <= 3 and all(type(lit) is int and 1 <= abs(lit) <= n for lit in clause)
             for clause in clauses), 'CNF literal or clause extent')
    formula = balanced('and', [balanced('or', clause, False) for clause in clauses], True)
    word = formula_word(formula)
    need(len(word) <= 50 * max(1, len(clauses)) ** 2, 'proved group-program bound')
    return word


def evaluate(word, assignment):
    p = IDENTITY
    for variable, zero, one in word:
        step = one if variable is not None and assignment >> variable & 1 else zero
        p = compose(step, p)
    return p


def swaps(permutation):
    seen = set()
    result = []
    for i in range(5):
        if i in seen:
            continue
        seen.add(i)
        j = permutation[i]
        while j != i:
            result.append((i, j))
            seen.add(j)
            j = permutation[j]
    return result


def controlled_swap(i, j, generator):
    """Swap at native sign -1 and act as identity at sign +1."""
    return [{'op': 'add', 'src': j, 'dst': i, 'coefficient': -1},
            {'op': 'add', 'src': i, 'dst': j, 'coefficient': '1/2'},
            {'op': 'query', 'src': i, 'dst': j, 'generator': generator, 'coefficient': '-1/2'},
            {'op': 'apply', 'dst': i, 'generator': generator},
            {'op': 'add', 'src': j, 'dst': i}]


def lower_word(n, word):
    generators = {}
    for i in range(n):
        linear = [0] * n
        linear[i] = 2
        generators['Z' + str(i + 1)] = {'matrix_rows': [1 << j for j in range(n)], 'offset': 0,
                                       'phase': 0, 'linear_Z4': linear, 'quadratic_rows': [0] * n}
    code = []
    for variable, zero, one in word:
        code.extend({'op': 'swap', 'src': i, 'dst': j} for i, j in swaps(zero))
        if variable is not None:
            for i, j in swaps(compose(one, inverse(zero))):
                code.extend(controlled_swap(i, j, 'Z' + str(variable + 1)))
        else:
            need(zero == one, 'constant group instruction')
    need(len(code) <= 24 * len(word), 'proved register instruction bound')
    return {'axes': n, 'roles': 5, 'generators': generators, 'program': code, 'reference': []}


def cnf_problem(n, clauses):
    return lower_word(n, cnf_word(n, clauses))
