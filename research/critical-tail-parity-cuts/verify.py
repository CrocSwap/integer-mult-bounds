"""Exact critical-tail parity-cut evidence. Produced by Nick Petalas.

Apache-2.0. Only the Python standard library is used; execution writes nothing.
"""

from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def eye(n):
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def mul(a, b):
    n = len(a)
    return tuple(tuple(sum((a[i][k] * b[k][j] for k in range(n)), Q(0))
                       for j in range(n)) for i in range(n))


def norm(a):
    return max(sum(abs(x) for x in row) for row in a)


def inverse(a):
    """Independent dense row elimination, with bounded pivot search."""
    n = len(a)
    rows = [list(row) + list(unit) for row, unit in zip(a, eye(n))]
    for k in range(n):
        pivot = next((i for i in range(k, n) if rows[i][k]), None)
        need(pivot is not None, 'invertible literal matrix')
        rows[k], rows[pivot] = rows[pivot], rows[k]
        q = rows[k][k]
        rows[k] = [x / q for x in rows[k]]
        for i in range(n):
            if i != k:
                q = rows[i][k]
                rows[i] = [x - q * y for x, y in zip(rows[i], rows[k])]
    return tuple(tuple(row[n:]) for row in rows)


def convolution(a, b, n):
    return tuple(sum((a[j] * b[i - j] for j in range(i + 1)
                      if j < len(a) and i - j < len(b)), Q(0))
                 for i in range(n))


def reciprocal(a):
    need(a[0] == 1, 'unit constant coefficient')
    out = [Q(1)]
    for k in range(1, len(a)):
        out.append(-sum((a[j] * out[k - j] for j in range(1, k + 1)), Q(0)))
    return tuple(out)


def toeplitz(f):
    n = len(f)
    return tuple(tuple(f[i - j] if i >= j else Q(0) for j in range(n))
                 for i in range(n))


def split(f, wrong_sign=False):
    n = len(f)
    need(n >= 2 and n & (n - 1) == 0, 'dyadic nonleaf dimension')
    e, o = f[::2], f[1::2]
    k = convolution(o, reciprocal(e), n // 2)
    correction = convolution(o, k, n // 2)
    sign = 1 if wrong_sign else -1
    s = tuple(e[i] + sign * (correction[i - 1] if i else 0)
              for i in range(n // 2))
    return e, s, k


def shears(k):
    """Embed both complete shears in original coefficient order."""
    n = 2 * len(k)
    u, l = [list(row) for row in eye(n)], [list(row) for row in eye(n)]
    for i in range(n // 2):
        for j in range(i + 1):
            l[2 * i + 1][2 * j] = k[i - j]
            if j < i:
                u[2 * i][2 * j + 1] = k[i - j - 1]
    return tuple(map(tuple, u)), tuple(map(tuple, l))


def interlace(a, b):
    n = len(a)
    return tuple(tuple(a[i // 2][j // 2] if i % 2 == j % 2 == 0
                       else b[i // 2][j // 2] if i % 2 == j % 2 == 1
                       else Q(0) for j in range(2 * n)) for i in range(2 * n))


def cut_states(f):
    """Enumerate every child-cut pair, using a bottom-up nonrecursive tree."""
    need(1 <= len(f) <= 8 and len(f) & (len(f) - 1) == 0, 'cut census size')
    levels = [[f]]
    for _ in range(len(f).bit_length() - 1):
        children = []
        for symbol in levels[-1]:
            e, s, _ = split(symbol)
            children.extend((e, s))
        levels.append(children)
    states = [(eye(1),) for _ in levels[-1]]
    nodes = 0
    for symbols in reversed(levels[:-1]):
        parents = []
        for index, symbol in enumerate(symbols):
            e, s, k = split(symbol)
            a = sum(abs(x) for x in e[1:])
            b = sum(abs(x) for x in symbol[1::2])
            need(a + b <= 1, 'inherited unit tail budget')
            need(sum(abs(x) for x in k) <= 1, 'bounded complete shear')
            need(sum(abs(x) for x in s[1:]) <= 1, 'Schur unit tail budget')
            u, l = shears(k)
            endpoint = mul(l, mul(interlace(toeplitz(e), toeplitz(s)), u))
            need(endpoint == toeplitz(symbol), 'literal parity endpoint')
            prefixes = {eye(len(symbol)), endpoint}
            for left, right in product(states[2 * index], states[2 * index + 1]):
                prefixes.add(mul(interlace(left, right), u))
            parents.append(tuple(sorted(prefixes)))
            nodes += 1
        states = parents
    return states[0], nodes


def check_symbol(f):
    need(f[0] == 1 and sum(abs(x) for x in f[1:]) <= 1, 'admitted symbol')
    prefixes, nodes = cut_states(f)
    target = toeplitz(f)
    target_inverse = inverse(target)
    need(mul(target, target_inverse) == eye(len(f)), 'independent endpoint inverse')
    digest = sha256()
    for prefix in prefixes:
        pinv = inverse(prefix)
        suffix = mul(target, pinv)
        sinv = mul(prefix, target_inverse)
        need(mul(suffix, prefix) == target, 'complete chronological cut')
        need(mul(suffix, sinv) == eye(len(f)), 'literal suffix inverse')
        need(all(norm(x) <= len(f) for x in (prefix, pinv, suffix, sinv)),
             'four critical-cut envelopes')
        digest.update(str((prefix, pinv, suffix, sinv)).encode())
    return len(prefixes), nodes, digest.hexdigest()


def fixtures():
    yield (Q(1),)
    for n in (2, 4):
        for tail in product(range(-4, 5), repeat=n - 1):
            if sum(abs(x) for x in tail) <= 4:
                yield (Q(1),) + tuple(Q(x, 4) for x in tail)
    for shift in range(1, 8):
        for sign in (-1, 1):
            yield (Q(1),) + tuple(Q(sign if i == shift else 0) for i in range(1, 8))
    for signs in product((-1, 1), repeat=3):
        yield (Q(1), Q(signs[0], 2), Q(signs[1], 4), Q(signs[2], 4)) + (Q(0),) * 4
    yield (Q(1), Q(0), Q(1, 2), Q(1, 2), Q(0), Q(0), Q(0), Q(0))


def controls():
    checks = []
    f = (Q(1), Q(1, 2), Q(1, 2), Q(0))
    e, s, k = split(f, wrong_sign=True)
    u, l = shears(k)
    need(mul(l, mul(interlace(toeplitz(e), toeplitz(s)), u)) != toeplitz(f),
         'wrong Schur sign must fail')
    checks.append('wrong Schur sign')
    e, s, k = split(f)
    middle = interlace(toeplitz(e), toeplitz(s))
    need(mul(u, mul(middle, l)) != toeplitz(f), 'wrong chronology must fail')
    need(mul(middle, u) != toeplitz(f), 'missing left shear must fail')
    checks.extend(('wrong chronology', 'missing left shear'))
    for bad in ((Q(0),), (Q(1), Q(2))):
        try:
            check_symbol(bad)
        except ValueError:
            checks.append('invalid symbol ' + str(bad))
        else:
            raise ValueError('invalid symbol accepted')
    f = (Q(1), Q(0), Q(1), Q(0))
    need(split(f)[2] == (0, 0), 'even-tail-one singular-denominator branch')
    checks.append('even-tail-one branch')
    need(norm(inverse(toeplitz((Q(1), Q(-1))))) == 2,
         'constant common envelope cannot replace dimension')
    checks.append('missing dimension loss')
    return checks


def main():
    cases, total_cuts, nodes, critical = [], 0, 0, 0
    for f in fixtures():
        count, visited, digest = check_symbol(f)
        cases.append([list(map(str, f)), count, digest])
        total_cuts += count
        nodes += visited
        critical += sum(abs(x) for x in f[1:]) == 1
    sharp = []
    for n in (1, 2, 4, 8, 16, 32):
        f = (Q(1),) + ((Q(-1),) if n > 1 else ()) + (Q(0),) * max(0, n - 2)
        inv = inverse(toeplitz(f))
        need(norm(inv) == n, 'attained sharp dimension envelope')
        need(inv == tuple(tuple(Q(i >= j) for j in range(n)) for i in range(n)),
             'literal geometric inverse entries')
        sharp.append([n, str(norm(inv))])
    result = {'status': 'PASS_CRITICAL_TAIL_PARITY_CUTS', 'symbols': len(cases),
              'critical_symbols': critical, 'cut_quadruples': total_cuts,
              'tree_nodes': nodes, 'cases_sha256': sha256(json.dumps(cases).encode()).hexdigest(),
              'sharpness': sharp, 'controls': controls()}
    here = Path(__file__).resolve().parent
    names = ('PROOF.md', 'README.md', 'SOURCES.json', 'TASK.json', 'VERIFY.json', 'verify.py')
    result['files_sha256'] = {name: sha256((here / name).read_bytes()).hexdigest()
                              for name in names}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
