"""Exact finite evidence for incremental quadratic phases over Z/4.
The accompanying proof applies universally; this script checks small cases.
"""
import itertools
import json
import random

def quadratic(a, cols, x):
    r = len(a)
    z = sum((a[j] for j in range(r) if x >> j & 1))
    for j in range(r):
        for k in range(j + 1, r):
            z += 2 * (cols[j] >> k & 1) * (x >> j & 1) * (x >> k & 1)
    return z & 3

def stream(a, cols):
    r = len(a)
    if not len(cols) == r:
        raise AssertionError('exact check failed')
    if not all((0 <= c < 1 << r for c in cols)):
        raise AssertionError('exact check failed')
    if not all((not cols[j] >> j & 1 for j in range(r))):
        raise AssertionError('exact check failed')
    if not all((cols[j] >> k & 1 == cols[k] >> j & 1 for j in range(r) for k in range(r))):
        raise AssertionError('exact check failed')
    q, gradient, x = (0, 0, 0)
    result, flips = ([], 0)
    for target in range(1 << r):
        if not target == x:
            raise AssertionError('exact check failed')
        result.append(q)
        if target + 1 == 1 << r:
            break
        j, mask = (0, 1)
        while True:
            old = bool(x & mask)
            delta = a[j] + (2 if gradient & mask else 0) & 3
            q = (q + 4 - delta if old else q + delta) & 3
            gradient ^= cols[j]
            flips += 1
            if not old:
                break
            j += 1
            mask <<= 1
        x += 1
    if not flips == 2 * (1 << r) - r - 2:
        raise AssertionError('exact check failed')
    return result

def columns_from_edges(r, edge_bits):
    cols = [0] * r
    for bit, (j, k) in enumerate(itertools.combinations(range(r), 2)):
        if edge_bits >> bit & 1:
            cols[j] |= 1 << k
            cols[k] |= 1 << j
    return cols

def negate_limbs(words, k):
    beta = 1 << k
    carry = 1
    out = []
    for a in words:
        z = beta - 1 - a + carry
        carry = int(z == beta)
        out.append(z - beta if carry else z)
    return out

def value(words, k):
    return sum((a << j * k for j, a in enumerate(words)))

def verify():
    phase_cases = 0
    for r in range(5):
        for a in itertools.product(range(4), repeat=r):
            for e in range(1 << r * (r - 1) // 2):
                cols = columns_from_edges(r, e)
                if not stream(a, cols) == [quadratic(a, cols, x) for x in range(1 << r)]:
                    raise AssertionError('exact check failed')
                phase_cases += 1
    rng = random.Random(20261022)
    for r in range(5, 12):
        for _ in range(20):
            a = [rng.randrange(4) for j in range(r)]
            cols = columns_from_edges(r, rng.getrandbits(r * (r - 1) // 2))
            if not stream(a, cols) == [quadratic(a, cols, x) for x in range(1 << r)]:
                raise AssertionError('exact check failed')
            phase_cases += 1
    neg_cases = 0
    for k in range(1, 5):
        for L in range(1, 5):
            limit = 1 << k * L
            xs = range(limit) if limit <= 1024 else [rng.randrange(limit) for _ in range(1000)]
            for x in xs:
                words = [x >> k * j & (1 << k) - 1 for j in range(L)]
                got = negate_limbs(words, k)
                if not all((0 <= z < 1 << k for z in got)):
                    raise AssertionError('exact check failed')
                if not value(got, k) == -x % limit:
                    raise AssertionError('exact check failed')
                neg_cases += 1
    return dict(status='PASS', phase_cases=phase_cases, modular_negation_cases=neg_cases, scope='exact portable finite replay, not kernel proof or new kappa')
if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
