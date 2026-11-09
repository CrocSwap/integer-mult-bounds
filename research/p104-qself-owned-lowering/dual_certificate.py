"""Independent backward covectors with exact integer dyadic coefficients.

For each q in {1,i,-1,-i}, D variables remain formal.  The four evaluations
are injective on Q(i)[q]/(q^4-1); this is not sampled-D verification.
No forward replay or its arithmetic implementation is imported.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction


def require(test, message):
    if not test:
        raise ValueError(message)


def norm(a, b, s):
    while s and not (a & 1 or b & 1):
        a //= 2
        b //= 2
        s -= 1
    return a, b, s


ONE = (1, 0, 0)
ZERO = (0, 0, 0)
IPHASE = ((1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0))


def scalar(text):
    f = Fraction(text)
    d = f.denominator
    require(d & (d-1) == 0, 'dyadic dual scalar')
    return f.numerator, 0, d.bit_length()-1


def plus(u, v):
    a, b, s = u
    c, d, t = v
    w = max(s, t)
    return norm((a << (w-s)) + (c << (w-t)), (b << (w-s)) + (d << (w-t)), w)


def times(u, v):
    a, b, s = u
    c, d, t = v
    return norm(a*c-b*d, a*d+b*c, s+t)


def stretch(poly, c=ONE, mask=0):
    ans = {}
    for (output, old), coefficient in poly.items():
        require(not old & mask, 'dual repeated D factor')
        value = times(coefficient, c)
        if value != ZERO:
            ans[(output, old | mask)] = value
    return ans


def sum_poly(left, right):
    ans = dict(left)
    for key, value in right.items():
        value = plus(ans.get(key, ZERO), value)
        if value == ZERO:
            ans.pop(key, None)
        else:
            ans[key] = value
    return ans


def certificate(caller):
    receipts = []
    for character in range(4):
        # At the output boundary, each output covector is independent.
        C = [{(r, 0): ONE} for r in range(caller['roles'])]
        peak = 0
        q = IPHASE[character]
        qi = IPHASE[-character % 4]
        for event in reversed(caller['events']):
            if event[0] == 'J':
                mask = 1 << (event[1]-1)
                u, v, x, y = event[2]
                for r in (u, v, x, y):
                    C[r] = stretch(C[r], mask=mask)
                # Transposes of the two triangular HOST2 updates.
                C[u] = sum_poly(C[u], stretch(C[v], qi))
                C[y] = sum_poly(C[y], stretch(C[x], times(scalar(caller['types']['A']['alpha2']), q)))
                a, b, alpha, beta = event[3]
                al, be = scalar(alpha), scalar(beta)
                # The dense HOST 2x2 block is transposed, not inverted.
                ca = sum_poly(C[a], stretch(C[b], times(be, qi)))
                cb = sum_poly(stretch(C[a], times(al, q)), stretch(C[b], plus(ONE, times(al, be))))
                C[a], C[b] = stretch(ca, mask=mask), stretch(cb, mask=mask)
                peak = max(peak, sum(len(poly) for poly in C))
                require(peak <= 500000, 'bounded independent dual replay')
                continue
            op, x = event[1:3]
            if op == 'ADD':
                y = event[3]
                C[y] = sum_poly(C[y], stretch(C[x], scalar(event[4])))
            elif op == 'QUERY':
                y = event[3]
                C[y] = sum_poly(C[y], stretch(C[x], IPHASE[(character*event[4]) % 4]))
            elif op == 'SCALE':
                C[x] = stretch(C[x], scalar(event[3]))
            elif op == 'SWAP':
                C[x], C[event[3]] = C[event[3]], C[x]
            elif op == 'QSELF':
                C[x] = stretch(C[x], IPHASE[(character*event[3]) % 4])
            elif op == 'IDLE_ONE':
                mask = sum(1 << (k-1) for k in event[3])
                require(mask.bit_count() == len(event[3]), 'dual unique idle stages')
                C[x] = stretch(C[x], mask=mask)
            elif op == 'LAMBDA':
                # Exact character value of ((1+s i)+(1-s i)q^2)/2.
                C[x] = stretch(C[x], ONE if character % 2 == 0 else IPHASE[event[3] % 4])
            else:
                raise ValueError('unsupported dual source event')
            peak = max(peak, sum(len(poly) for poly in C))
            require(peak <= 500000, 'bounded independent dual replay')
        for ty in ('A', 'B'):
            t = caller['types'][ty]
            for j, diagonal in enumerate(t['diagonal']):
                r = t['offset'] + j
                mask = sum(bit << k for k, bit in enumerate(diagonal[2:]))
                target = {(r, mask): IPHASE[(character*diagonal[0]) % 4]}
                require(C[r] == target, 'backward arbitrary-output covector endpoint')
        receipts.append({'q_character_power_of_i': character, 'peak_terms': peak,
                         'independent_outputs': len(C), 'formal_D_variables': 18})
    return receipts
