"""Bounded, exact corroboration of the singular polynomial cost theorem."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def addc(a, b, q):
    return a ^ b if q == 4 else (a + b) % q


def mulc(a, b, q):
    if q != 4:
        return a * b % q
    raw = (a if b & 1 else 0) ^ (a << 1 if b & 2 else 0)
    return raw ^ 7 if raw & 4 else raw


def negc(a, q):
    return a if q == 4 else -a % q


def norm(a):
    require(len(a) <= 33, 'polynomial capacity')
    end = len(a)
    for _ in range(len(a)):
        if end == 0 or a[end - 1]:
            break
        end -= 1
    return tuple(a[:end])


def add(a, b, q):
    return norm(tuple(addc(a[i] if i < len(a) else 0,
                           b[i] if i < len(b) else 0, q)
                      for i in range(max(len(a), len(b)))))


def scale(a, c, q):
    return norm(tuple(mulc(x, c, q) for x in a))


def mul(a, b, q):
    if not a or not b:
        return ()
    require(len(a) + len(b) <= 34, 'product capacity')
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = addc(out[i + j], mulc(x, y, q), q)
    return norm(out)


def divmodp(a, b, q):
    require(bool(b), 'zero polynomial divisor')
    r = a
    out = [0] * max(0, len(a) - len(b) + 1)
    inv = next(c for c in range(1, q) if mulc(c, b[-1], q) == 1)
    for _ in range(len(a) + 1):
        if len(r) < len(b):
            return norm(out), r
        shift = len(r) - len(b)
        c = mulc(r[-1], inv, q)
        out[shift] = c
        r = add(r, (0,) * shift + scale(b, negc(c, q), q), q)
    raise ValueError('polynomial division exhausted')


def gcd(a, b, q):
    for _ in range(34):
        if not b:
            if not a:
                return ()
            inv = next(c for c in range(1, q) if mulc(c, a[-1], q) == 1)
            return scale(a, inv, q)
        a, b = b, divmodp(a, b, q)[1]
    raise ValueError('gcd exhausted')


def mm(a, b, q):
    return tuple(add(mul(a[2*i], b[j], q),
                     mul(a[2*i+1], b[2+j], q), q)
                 for i in range(2) for j in range(2))


def inv2(a, q):
    det = addc(mulc(a[0], a[3], q), negc(mulc(a[1], a[2], q), q), q)
    require(det != 0, 'singular free map')
    c = next(x for x in range(1, q) if mulc(x, det, q) == 1)
    return tuple(scale((x,), c, q) for x in
                 (a[3], negc(a[1], q), negc(a[2], q), a[0]))


def dot(a, b, q):
    return add(scale(a[0], b[0], q), scale(a[1], b[1], q), q)


def directions(q):
    return tuple((1, x) for x in range(q)) + ((0, 1),)


def primitive(m, q):
    j = 0 if m[0] or m[2] else 1
    d = gcd(m[j], m[2+j], q)
    a = (divmodp(m[j], d, q)[0], divmodp(m[2+j], d, q)[0])
    b = []
    i = 0 if a[0] else 1
    for k in range(2):
        quotient, remainder = divmodp(m[2*i+k], a[i], q)
        require(not remainder, 'primitive factorization divisibility')
        b.append(quotient)
    require(tuple(mul(x, y, q) for x in a for y in b) == m,
            'primitive factorization reconstruction')
    require(gcd(*a, q) == (1,), 'primitive column gcd')
    return a, tuple(b)


def predicted(a, b, q):
    constant = all(len(x) <= 1 for x in a)
    values = tuple(dot(b, v, q) for v in directions(q))
    if constant and any(len(x) == 1 for x in values):
        return 1
    d = gcd(*b, q)
    if constant or any(x and len(x) == len(d) and not divmodp(x, d, q)[1]
                       for x in values):
        return 2
    return 3


def direct_one(m, q):
    return any((w := (dot(m[:2], v, q), dot(m[2:], v, q))) != ((), ())
               and all(len(x) <= 1 for x in w) for v in directions(q))


def direct_two(m, q):
    for phi in directions(q):
        row = (dot((m[0], m[2]), phi, q), dot((m[1], m[3]), phi, q))
        for t in directions(q):
            s = (0, 1) if t[0] else (1, 0)
            left, right = dot(row, t, q), dot(row, s, q)
            if not left and right:
                continue
            if left and divmodp(right, left, q)[1]:
                continue
            psi = (0, 1) if phi[0] else (1, 0)
            g = tuple((x,) if x else () for x in phi + psi)
            hraw = (t[0], s[0], t[1], s[1])
            h = tuple((x,) if x else () for x in hraw)
            n = mm(mm(g, m, q), h, q)
            c = divmodp(n[1], n[0], q)[0] if n[0] else ()
            f1 = (n[0], (), n[2], (1,))
            f2 = ((1,), c, (), add(n[3], scale(mul(n[2], c, q), negc(1, q), q), q))
            graw = phi + psi
            restored = mm(mm(mm(inv2(graw, q), f1, q), f2, q), inv2(hraw, q), q)
            require(restored == m, 'two-factor witness')
            return True
    return False


def upper_word(a, b, q):
    f = (a[0], (), a[1], (1,))
    g = ((1,), b[1], (), ())
    h = (b[0], (), (), (1,))
    require(mm(mm(f, g, q), h, q) == tuple(mul(x, y, q) for x in a for y in b),
            'three-factor word')
    return f, g, h


def census(q, degree):
    require((q, degree) in ((2, 4), (3, 2), (4, 1), (5, 1)), 'census domain')
    polys = tuple(norm(x) for x in product(range(q), repeat=degree + 1))
    products = {(a, b): mul(a, b, q) for a in polys for b in polys}
    histogram = [0, 0, 0, 0]
    total = 0
    for m in product(polys, repeat=4):
        if products[m[0], m[3]] != products[m[1], m[2]]:
            continue
        total += 1
        if not any(m):
            require(not direct_one(m, q) and direct_two(m, q), 'zero exact cost')
            histogram[2] += 1
            continue
        a, b = primitive(m, q)
        cost = predicted(a, b, q)
        require((cost == 1) == direct_one(m, q), 'one-factor classification')
        require((cost <= 2) == direct_two(m, q), 'two-factor classification')
        upper_word(a, b, q)
        histogram[cost] += 1
    require(sum(histogram) == total, 'census partition')
    return {'q': q, 'degree_at_most': degree, 'targets': total, 'costs': histogram}


def controls():
    count = 0
    for q in (2, 3, 4, 5):
        a, b = ((1,), (0, 1)), ((0, 1), (1, 0, 1))
        m = tuple(mul(x, y, q) for x in a for y in b)
        require(predicted(a, b, q) == 3 and not direct_two(m, q), 'sharp target')
        f, g, h = upper_word(a, b, q)
        require(mm(mm(h, g, q), f, q) != m, 'reversed word control')
        require(mm(f, g, q) != m and mm(g, h, q) != m, 'omitted factors')
        require(not direct_one(m, q), 'false one-factor shortcut')
        # Scaling the row content cannot turn the cost-three target into cost two.
        bscaled = tuple(mul(x, (0, 1), q) for x in b)
        require(predicted(a, bscaled, q) == 3, 'gcd normalization control')
        require(predicted(((1,), ()), bscaled, q) == 2, 'constant column exception')
        require(predicted(((1,), ()), ((1,), (0, 1)), q) == 1, 'cost-one boundary')
        require(predicted(a, ((0, 1), (0, 1, 1)), q) == 2, 'gcd in row span')
        count += 8
    for invalid in (0, 6):
        try:
            census(invalid, 1)
        except ValueError:
            count += 1
        else:
            raise ValueError('invalid field accepted')
    try:
        divmodp((1,), (), 2)
    except ValueError:
        count += 1
    else:
        raise ValueError('zero divisor accepted')
    return count


def main():
    cases = ((2, 4), (3, 2), (4, 1), (5, 1))
    results = [census(q, d) for q, d in cases]
    expected = ((0, 279, 7489, 936), (0, 800, 5761, 0),
                (0, 975, 1201, 0), (0, 3024, 3601, 0))
    require(tuple(tuple(x['costs']) for x in results) == expected, 'frozen census counts')
    control_count = controls()
    require(control_count == 35, 'control coverage')
    package = Path(__file__).resolve().parent
    hashes = {p.name: sha256(p.read_bytes()).hexdigest()
              for p in sorted(package.iterdir()) if p.is_file()}
    receipt = {'results': results, 'control_checks': control_count, 'sha256': hashes}
    print(json.dumps(receipt, sort_keys=True))
    print('PASS_SINGULAR_POLYNOMIAL_COST targets=' + str(sum(x['targets'] for x in results))
          + ' controls=' + str(control_count) + ' no_new_kappa')


if __name__ == '__main__':
    main()
