"""Literal programs and free noncommutative replay. Apache-2.0.
Ross Richardson, with substantial OpenAI Codex assistance.
"""
from collections import Counter

TARGET = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
# kind, operator/coefficient, query sign, root (0=z, 1=w)
WORD = [
    ('A', 0, 1, 0), ('R', -1, 1, 0), ('B', 0, -1, 1),
    ('A', 2, -1, 1), ('B', 1, -1, 1), ('R', 1, 1, 0),
    ('A', 1, -1, 0), ('B', 2, -1, 0), ('A', 0, -1, 0),
    ('R', -1, 1, 0), ('B', 0, 1, 1), ('A', 2, 1, 1),
    ('B', 1, 1, 1), ('R', 1, 1, 0), ('A', 1, 1, 0),
    ('B', 2, 1, 0),
]
# Charles Bethin, PR1637, 9bee6cc01f151b92ccfe147046855715843f066a.
PREDECESSOR = [
    ('B', 0, 1, 0), ('A', 2, 1, 0), ('B', 1, 1, 0),
    ('R', -1, 1, 0), ('A', 0, 1, 0), ('R', 2, 1, 0),
    ('A', 1, 1, 0), ('R', -1, 1, 0), ('B', 0, -1, 0),
    ('A', 2, -1, 0), ('B', 1, -1, 0), ('B', 2, 1, 1),
    ('R', -1, 1, 0), ('A', 0, -1, 0), ('R', 2, 1, 0),
    ('A', 1, -1, 0), ('R', -1, 1, 0), ('B', 2, -1, 1),
]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def inverse(word):
    return [(kind, op, -sign, root) for kind, op, sign, root in reversed(word)]


def symbolic(word):
    state = [{(str(i),): 1} for i in range(8)]
    for kind, op, sign, root in word:
        require(kind in ('A', 'B', 'R') and sign in (-1, 1), 'alphabet')
        require(root in (0, 1), 'root')
        if kind == 'R':
            require(root == 0 and op != 0, 'one-way nonzero transfer')
            src, dst, coefficient, prefix = 7, 6, sign * op, ()
        else:
            require(op in range(3), 'operator')
            src, dst = (op, 6 + root) if kind == 'B' else (6 + root, 3 + op)
            coefficient, prefix = sign, (kind + str(op),)
        for term, value in list(state[src].items()):
            key = prefix + term
            new = state[dst].get(key, 0) + coefficient * value
            if new:
                state[dst][key] = new
            else:
                state[dst].pop(key, None)
    return state


def expected():
    state = symbolic([])
    for i, row in enumerate(TARGET):
        for j, value in enumerate(row):
            if value:
                state[3 + i][('A' + str(i), 'B' + str(j), str(j))] = value
    return state


LENGTHS = {'B0': 2, 'B1': 3, 'B2': 4, 'A0': 5, 'A1': 6, 'A2': 7}
FACTORS = {}
_next = 0
for _name, _length in LENGTHS.items():
    FACTORS[_name] = tuple(range(_next, _next + _length))
    _next += _length


def leaf_inverse(word):
    return [(kind, op, -sign, src, dst) for kind, op, sign, src, dst in reversed(word)]


def lower(factors, src, dst, scratch):
    require(src != dst and src not in scratch and dst not in scratch, 'disjoint scratch')
    if len(factors) == 1:
        return [('F', factors[0], 1, src, dst)]
    require(bool(scratch), 'scratch exhaustion')
    pivot = len(factors) // 2
    a = lower(factors[:pivot], src, scratch[0], scratch[1:])
    b = lower(factors[pivot:], scratch[0], dst, scratch[1:])
    return a + b + leaf_inverse(a) + leaf_inverse(b)


def expand(word):
    out = []
    for kind, op, sign, root in word:
        if kind == 'R':
            out.append(('R', op, sign, 7, 6))
            continue
        src, dst = (op, 6 + root) if kind == 'B' else (6 + root, 3 + op)
        child = lower(FACTORS[kind + str(op)], src, dst, (8, 9, 10))
        out.extend(child if sign == 1 else leaf_inverse(child))
    return out


def expanded_symbolic(word):
    state = [{(i, ()): 1} for i in range(11)]
    for kind, op, sign, src, dst in word:
        for (origin, factors), value in list(state[src].items()):
            key = (origin, factors + (op,)) if kind == 'F' else (origin, factors)
            value = state[dst].get(key, 0) + sign * (op if kind == 'R' else 1) * value
            if value:
                state[dst][key] = value
            else:
                state[dst].pop(key, None)
    return state


def expanded_expected():
    state = expanded_symbolic([])
    for i, row in enumerate(TARGET):
        for j, value in enumerate(row):
            if value:
                factors = FACTORS['B' + str(j)] + FACTORS['A' + str(i)]
                state[i + 3][(j, factors)] = value
    return state


def head_polynomial(word):
    # coefficient list for L^0,...,L^4; R=11 mutable rows in both layouts.
    out = [0] * 5
    for kind, op, sign, src, dst in word:
        out[0] -= 2
        if kind == 'F':
            out[4] += 2 * op + 1
            out[3] += 21 - 2 * min(src, dst)
            out[1] += 2 * (dst + 1)
        else:
            require((src, dst) == (7, 6), 'root layout')
            out[2] += 2
            out[1] += 14
    return out


def invoice(word):
    calls = expand(word)
    return {
        'child_queries': sum(e[0] != 'R' for e in word),
        'root_transfers': sum(e[0] == 'R' for e in word),
        'root_doublings': sum(e[0] == 'R' and abs(e[1]) == 2 for e in word),
        'primitive_factor_calls': sum(e[0] == 'F' for e in calls),
        'primitive_instructions': len(calls),
        'mutable_rows': 11, 'root_rows': 2, 'private_child_rows': 3,
        'coefficient_matrices': 27,
        'head_moves_coefficients_L0_through_L4': head_polynomial(calls),
        'operator_multiplicities': dict(sorted(Counter(k + str(o) for k, o, s, r in word if k != 'R').items())),
    }
