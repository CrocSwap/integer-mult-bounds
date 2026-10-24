"""Truncated-algebra tensor characters. Ali Romman with OpenAI Codex. Apache-2.0."""
from itertools import product
from math import gcd
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def det(columns, p):
    n = len(columns)
    a = [[columns[j][i] for j in range(n)] for i in range(n)]
    answer = 1
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        if pivot is None:
            return 0
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            answer = -answer
        value = a[j][j]
        answer = answer * value % p
        inverse = pow(value, -1, p)
        for i in range(j + 1, n):
            factor = a[i][j] * inverse % p
            a[i] = [(x-factor*y) % p for x, y in zip(a[i], a[j])]
    return answer % p


def multiply(a, b, p):
    n = len(a)
    return tuple(sum(a[i]*b[j-i] for i in range(j+1)) % p for j in range(n))


def image(p, n):
    require(p in (2, 3, 5, 7) and 1 <= n <= 6, 'bounded prime-field domain')
    units = range(1, p)
    dn = gcd(n, p-1); da = gcd(n*(n-1)//2, p-1)
    e = (p-1)//dn; f = (p-1)//da
    return {(u, v, w) for u, v, w in product(units, repeat=3)
            if pow(v*w % p, e, p) == pow(u*w % p, e, p) == 1
            and pow(u*v*w % p, f, p) == 1}


def complete_census(p, n):
    elements = list(product(range(p), repeat=n))
    index = {x: i for i, x in enumerate(elements)}
    zero = index[(0,)*n]
    mul = [[index[multiply(a, b, p)] for b in elements] for a in elements]
    invertible = []
    for indices in product(range(len(elements)), repeat=n):
        d = det([elements[i] for i in indices], p)
        if d:
            invertible.append((indices, d))
    actual = set(); accepted = pairs = 0
    for (a, da), (b, db) in product(invertible, repeat=2):
        pairs += 1
        h = tuple(mul[x][b[0]] for x in a)
        dh = det([elements[i] for i in h], p)
        if not dh:
            continue
        if all(mul[a[i]][b[j]] == (h[i+j] if i+j < n else zero)
               for i, j in product(range(n), repeat=2)):
            accepted += 1
            actual.add((pow(da, -1, p), pow(db, -1, p), dh))
    require(actual == image(p, n), ('complete stabilizer image', p, n, actual))
    expected = (p-1)**2 if n == 1 else (p-1)**3 * p**(3*n-4)
    require(accepted == expected, ('autotopism count', p, n, accepted))
    return pairs, accepted


def attainment(p, n):
    actual = set(); count = 0
    for a, b, c in product(range(1, p), repeat=3):
        sigma = [tuple(pow(c, j, p) if i == j else 0 for i in range(n)) for j in range(n)]
        f = [tuple(a*x % p for x in col) for col in sigma]
        g = [tuple(b*x % p for x in col) for col in sigma]
        h = [tuple(a*b*x % p for x in col) for col in sigma]
        require(all(multiply(f[i], g[j], p) == (h[i+j] if i+j < n else (0,)*n)
                    for i, j in product(range(n), repeat=2)), 'literal attainment product')
        actual.add((pow(det(f, p), -1, p), pow(det(g, p), -1, p), det(h, p)))
        count += 1
    require(actual == image(p, n), ('attainment image', p, n))
    require(len(actual)*gcd(n, p-1)**2*gcd(n*(n-1)//2, p-1) == (p-1)**3, 'orbit index')
    return count


def main():
    generated = sum(attainment(p, n) for p in (2, 3, 5, 7) for n in range(1, 7))
    pairs = accepted = 0
    contexts = ((2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (5, 1), (5, 2))
    for p, n in contexts:
        a, b = complete_census(p, n)
        pairs += a; accepted += b
    require((2, 1, 2) not in image(7, 4) and (4, 1, 2) in image(7, 4), 'inverse-input convention')
    require(len(image(5, 2)) == 16, 'non-surjective unit norm')
    require(len(image(5, 3)) == 64, 'automorphism determinants need not be signs')
    require(len(image(5, 1)) == 16, 'dimension-one boundary')
    require(image(2, 6) == {(1, 1, 1)}, 'binary determinant boundary')
    for p, n in ((4, 2), (3, 0)):
        try:
            image(p, n)
        except ValueError:
            pass
        else:
            raise ValueError('bounded-domain violation accepted')
    print(json.dumps(dict(status='PASS_TRUNCATED_TENSOR_CHARACTERS', generated_maps=generated,
                         complete_domains=len(contexts), input_map_pairs=pairs, autotopisms=accepted,
                         controls=7, no_new_kappa=True), sort_keys=True))


if __name__ == '__main__':
    main()
