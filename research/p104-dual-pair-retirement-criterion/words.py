"""Exact replay of the retained caller words (Laurent/Gaussian-dyadic rows) and the native word.

The caller word acts on `roles` registers; rows[i][j] is the coefficient (a ring element) of independent
input j in register i.  Monomial keys are tuples (q-exponent mod 4, stage-0 flag, stage exponents...);
coefficients are Gaussian rationals (re, im).  Event semantics follow the retained caller verifiers
(Ali Romman, thu-nmrc, zxv; Apache-2.0).
"""
from fractions import Fraction as Q
from dualpair import accumulate, cmulz, ZERO, need, rmul

ONE = (Q(1), ZERO)


def coefficient(x):
    return (Q(x), ZERO)


def shifted(row, term):
    out = []
    for cell in row:
        tgt = {}
        for key, v in cell.items():
            new = ((key[0] + term[0]) % 4,) + tuple(a + b for a, b in zip(key[1:], term[1:]))
            accumulate(tgt, {new: v})
        out.append(tgt)
    return out


def mulkey(a, b):
    return ((a[0] + b[0]) % 4,) + tuple(x + y for x, y in zip(a[1:], b[1:]))


def caller_rmul(a, b):
    return rmul(a, b, mulkey)


def init(word, extra=0):
    n = word['roles']
    width = word['stages'] + 2
    zero = (0,) * width
    cols = n + extra
    rows = [[{zero: coefficient(1)} if i == j else {} for j in range(cols)] for i in range(n)]
    return rows, n, width, cols


def step(rows, event, width, cols):
    op = event[0]
    if op == 'ADD':
        _, dst, src, c = event
        cc = coefficient(c)
        for a, b in zip(rows[dst], rows[src]):
            accumulate(a, b, cc)
    elif op == 'SCALE':
        _, dst, c = event
        cc = coefficient(c)
        rows[dst] = [{k: cmulz(cc, v) for k, v in cell.items()} for cell in rows[dst]]
    elif op == 'SWAP':
        _, a, b = event
        rows[a], rows[b] = rows[b], rows[a]
    elif op in ('LOCAL', 'QUERY'):
        if op == 'LOCAL':
            _, stage, src, dst = event
            exponent = -1
        else:
            _, dst, src, exponent = event
        term = (exponent,) + (0,) * (width - 1)
        for a, b in zip(rows[dst], shifted(rows[src], term)):
            accumulate(a, b)
        if op == 'LOCAL':
            term = (0,) + tuple(int(s == stage) for s in range(width - 1))
            for r in (src, dst):
                rows[r] = shifted(rows[r], term)
    elif op == 'LAMBDA':
        _, r, sign = event
        old = rows[r]
        other = shifted(old, (2,) + (0,) * (width - 1))
        rows[r] = [{} for _ in range(cols)]
        for dst, a, b in zip(rows[r], old, other):
            accumulate(dst, a, (Q(1, 2), Q(sign, 2)))
            accumulate(dst, b, (Q(1, 2), Q(-sign, 2)))
    elif op in ('IDLE', 'IDLE_ONE'):
        roles, stages = (event[1:3], event[3]) if op == 'IDLE' else ([event[1]], event[2])
        term = (0,) + tuple(int(s in stages) for s in range(width - 1))
        for r in roles:
            rows[r] = shifted(rows[r], term)
    else:
        raise ValueError(op)


def run(rows, events, width, cols):
    for e in events:
        step(rows, e, width, cols)


def sdef(m1, kind):
    """The job s as a ring element: monomial (kind 0) or lambda_sigma * monomial (kind +-1)."""
    if kind == 0:
        return {m1: (Q(1), ZERO)}
    m2 = ((m1[0] + 2) % 4,) + m1[1:]
    return {m1: (Q(1, 2), Q(kind, 2)), m2: (Q(1, 2), Q(-kind, 2))}


def candidates(rows, G, n):
    mons = set()
    for g in G:
        for i in range(n):
            mons.update(rows[i][g].keys())
    out = []
    for m in sorted(mons):
        out.append((m, 0))
        if m[0] % 4 in (0, 1):
            out += [(m, 1), (m, -1)]
    return out


def endpoint_is_diagonal(word, rows, n):
    for i in range(n):
        for j in range(n):
            exp = {tuple(x % 4 if k == 0 else x for k, x in enumerate(word['diagonal'][i])): ONE} if i == j else {}
            need(rows[i][j] == exp, ('endpoint is not the declared diagonal', i, j))
    return True
