"""Exact tests of a rounded two-pass periodic first-order filter.

No floating arithmetic, numerical root finder, or kernel builder is used.
This certifies the listed finite cases; PROOF.md gives the general bound.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import json

ZERO = (F(0), F(0))
ONE = (F(1), F(0))

def add(a, b): return (a[0]+b[0], a[1]+b[1])
def neg(a): return (-a[0], -a[1])
def sub(a, b): return add(a, neg(b))
def mul(a, b): return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
def norm2(a): return a[0]*a[0]+a[1]*a[1]
def div(a, b):
    d = norm2(b)
    if not d: raise ValueError('zero divisor')
    c = mul(a, (b[0], -b[1]))
    return (c[0]/d, c[1]/d)

def need(ok, message):
    if not ok: raise ValueError(message)

def rounded(a, bits):
    scale = 1 << bits
    def component(v):
        w = v * scale + F(1, 2)
        return F(w.numerator // w.denominator, scale)
    return (component(a[0]), component(a[1]))

def scan(x, b, beta, bits, direction):
    need(len(x) > 0, 'empty cycle')
    need(direction in (-1, 1), 'invalid direction')
    need(0 < beta <= 1, 'invalid margin')
    need(norm2(b) <= (1-beta)**2, 'uncertified stable factor')
    u = F(1, 1 << bits)
    need(u <= beta*beta/2, 'precision too low for closure')
    order = list(range(len(x))) if direction == 1 else list(reversed(range(len(x))))
    z, power = ZERO, ONE
    for i in order:
        z = rounded(add(x[i], mul(b, z)), bits)
        power = rounded(mul(b, power), bits)
    den = sub(ONE, power)
    need(norm2(den) >= (beta/2)**2, 'closure lower bound failed')
    seed = rounded(div(z, den), bits)
    y, previous = [ZERO]*len(x), seed
    for i in order:
        previous = rounded(add(x[i], mul(b, previous)), bits)
        y[i] = previous
    return y

def dense_solve(x, b, direction):
    """Independent exact Gaussian elimination on the cyclic matrix."""
    n = len(x)
    a = [[ZERO for _ in range(n)] + [x[i]] for i in range(n)]
    for i in range(n):
        a[i][i] = add(a[i][i], ONE)
        j = (i-direction) % n
        a[i][j] = sub(a[i][j], b)
    for k in range(n):
        pivot = next(i for i in range(k, n) if a[i][k] != ZERO)
        a[k], a[pivot] = a[pivot], a[k]
        p = a[k][k]
        a[k] = [div(v, p) for v in a[k]]
        for i in range(n):
            if i == k: continue
            p = a[i][k]
            a[i] = [sub(v, mul(p, w)) for v, w in zip(a[i], a[k])]
    return [row[-1] for row in a]

def residual_bound(x, y, b, beta, direction, bound):
    # Neumann inverse norm <= 1/beta converts residual to forward error.
    for i in range(len(x)):
        residual = sub(sub(y[i], mul(b, y[(i-direction) % len(x)])), x[i])
        need(norm2(residual) <= (beta*bound)**2, 'residual error bound failed')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    cases = []
    for beta in (F(1, 2), F(1, 16), F(1, 4096)):
        for unit in (ONE, (F(-1), F(0)), (F(3, 5), F(4, 5))):
            b = mul((1-beta, F(0)), unit)
            for n in (1, 2, 3, 8, 17, 64):
                x = [(F((i*7)%13-6, 8), F((i*11)%17-8, 16)) for i in range(n)]
                B = max(abs(v[0])+abs(v[1]) for v in x)
                for direction in (-1, 1):
                    bits = 64
                    bound = 6*(B+1)*F(1, 1 << bits)/beta**3
                    y = scan(x, b, beta, bits, direction)
                    residual_bound(x, y, b, beta, direction, bound)
                    if n <= 8:
                        exact = dense_solve(x, b, direction)
                        need(all(norm2(sub(v,w)) <= bound**2 for v,w in zip(y,exact)), 'dense comparison failed')
                    cases.append(dict(beta=str(beta), b=[str(v) for v in b], length=n,
                                      direction=direction, bits=bits, forward_error_bound=str(bound),
                                      dense_crosscheck=n<=8, residual_check=True))
    controls = []
    for name, x, b, beta, bits, direction in (
        ('unstable', [ONE], ONE, F(1,2), 64, 1),
        ('underprecision', [ONE], (F(15,16),F(0)), F(1,16), 3, 1),
        ('empty', [], ZERO, F(1,2), 64, 1),
        ('bad_direction', [ONE], ZERO, F(1,2), 64, 0),
    ):
        try: scan(x,b,beta,bits,direction)
        except ValueError as error: controls.append(dict(name=name,rejected=str(error)))
        else: raise ValueError('negative control accepted: '+name)
    x = [ONE, ZERO, ONE]
    b, beta = (F(1,2),F(0)), F(1,2)
    y = scan(x,b,beta,64,1)
    y[0] = add(y[0],ONE)
    try: residual_bound(x,y,b,beta,1,F(1,1<<40))
    except ValueError as error: controls.append(dict(name='corrupt_output',rejected=str(error)))
    else: raise ValueError('corrupt output accepted')
    args.out.write_text(json.dumps(dict(status='passed',cases=cases,controls=controls),indent=2)+'\n')
    print(json.dumps(dict(status='passed',cases=len(cases),dense_cases=sum(c['dense_crosscheck'] for c in cases),controls=len(controls))))

if __name__ == '__main__': main()
