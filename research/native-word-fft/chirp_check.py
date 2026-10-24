"""Exact algebraic control for diagonal-Hankel-diagonal Gaussian blocks.
Apache-2.0; Dugongue with substantial OpenAI Codex assistance.
Fraction arithmetic is a test oracle, not the bounded-word runtime.
"""
from fractions import Fraction
import json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def check():
    cases = entries = products = 0
    mutation_detected = False
    r = Fraction(3, 4)
    for q in (1, 2, 3, 5):
        for u, v, c in ((1, 1, 0), (2, 3, 1), (3, 2, -2)):
            d = [r ** ((u*u + u*v)*x*x + 2*c*u*x) for x in range(q)]
            e = [r ** ((v*v + u*v)*y*y - 2*c*v*y) for y in range(q)]
            h = [r ** (-u*v*k*k) for k in range(2*q-1)]
            z = r ** (c*c)
            data = [Fraction((-1)**j*(j+1), j+2) for j in range(q)]
            # Reverse the weighted source to obtain ordinary linear convolution.
            source = [e[y]*data[y] for y in range(q)][::-1]
            conv = [Fraction(0) for _ in range(3*q-2)]
            for i, a in enumerate(source):
                for j, b in enumerate(h):
                    conv[i+j] += a*b
            for x in range(q):
                direct = sum(r ** ((u*x-v*y+c)**2)*data[y] for y in range(q))
                fast = z*d[x]*conv[x+q-1]
                need(fast == direct, 'Gaussian convolution identity')
                if q > 1 and c != 0:
                    wrong = d[x]*conv[x+q-1]
                    if wrong != direct:
                        mutation_detected = True
                for y in range(q):
                    need(z*d[x]*e[y]*h[x+y] == r**((u*x-v*y+c)**2), 'entry identity')
                    entries += 1
                products += 1
            cases += 1
    need(mutation_detected, 'omitted constant factor control')
    return dict(status='PASS', block_cases=cases, exact_matrix_entries=entries,
                exact_matvec_outputs=products, omitted_constant_detected=True,
                scope='exact algebraic identity; does not measure FFT work or prove analytic errors')


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
