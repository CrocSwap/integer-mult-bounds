"""Independent exact controls for the Gaussian parity/tensor certificates.

Python standard library only. Exhaustive tests support the formal statements;
they are not a proof of arbitrary-dimensional transforms or tape complexity.
"""
from fractions import Fraction as F
from itertools import product
from random import Random
import json

def add(z, w): return z[0]+w[0], z[1]+w[1]
def neg(z): return -z[0], -z[1]
def sub(z, w): return add(z, neg(w))
def mul(z, w): return z[0]*w[0]-z[1]*w[1], z[0]*w[1]+z[1]*w[0]
def scale(c, z): return c*z[0], c*z[1]
I = (0, 1)
ONE = (1, 0)
PI = (1, 1)

def powg(z, n):
    ans = ONE
    for _ in range(n): ans = mul(ans, z)
    return ans

def divide(z, w):
    return scale(F(1, w[0]**2+w[1]**2), mul(z, (w[0], -w[1])))

def is_integer(z): return all(F(t).denominator == 1 for t in z)
def pi_residue(z):
    assert is_integer(z)
    return (int(z[0])+int(z[1])) % 2

def pair(u, v, inverse=False):
    # C=(iI+X)/(1+i), C^-1=(I+iX)/(1+i).
    if inverse:
        return divide(add(u, mul(I, v)), PI), divide(add(mul(I, u), v), PI)
    return divide(add(mul(I, u), v), PI), divide(add(u, mul(I, v)), PI)

def tensor_staged(values, d, inverse=False):
    out = list(values)
    assert len(out) == 1 << d
    for k in range(d):
        for x in range(1 << d):
            if not (x >> k) & 1:
                y = x ^ (1 << k)
                out[x], out[y] = pair(out[x], out[y], inverse)
    return out

def tensor_closed(values, d, inverse=False):
    den = powg(PI, d)
    out = []
    for x in range(1 << d):
        total = (0, 0)
        for y, value in enumerate(values):
            distance = (x ^ y).bit_count()
            exponent = distance if inverse else d-distance
            total = add(total, mul(powg(I, exponent), value))
        out.append(divide(total, den))
    return out

def normalized_via_phase(values, d):
    phased = [mul(powg(I,x.bit_count()),z) for x,z in enumerate(values)]
    result = tensor_staged(phased,d)
    return [divide(mul(powg(I,x.bit_count()),z),powg(PI,d))
            for x,z in enumerate(result)]

def normalized_closed(values, d):
    out=[]
    for x in range(1 << d):
        total=(0,0)
        for y,z in enumerate(values):
            sign=-1 if (x & y).bit_count()%2 else 1
            total=add(total,scale(sign,z))
        out.append(scale(F(1,1 << d),total))
    return out

def main():
    counts = {"division_cases":0, "pair_cases":0, "tensor_cases":0,
              "tensor_output_values":0, "sharpness_dimensions":0,
              "normalized_cases":0, "normalized_output_values":0,
              "normalized_sharpness_dimensions":0}
    for r, s in product(range(-30, 31), repeat=2):
        quotient = divide((r, s), PI)
        assert is_integer(quotient) == ((r-s) % 2 == 0)
        counts["division_cases"] += 1
    values = list(product(range(-4, 5), repeat=2))
    for u, v in product(values, repeat=2):
        good = pi_residue(u) == pi_residue(v)
        for inverse in (False, True):
            a, b = pair(u, v, inverse)
            assert (is_integer(a) and is_integer(b)) == good
            if good: assert pi_residue(a) == pi_residue(b)
            assert pair(a, b, not inverse) == (u, v)
            counts["pair_cases"] += 1
    rng = Random(109)
    for d in range(9):
        for inverse in (False, True):
            for trial in range(4):
                xs = [(rng.randint(-19,19), rng.randint(-19,19)) for _ in range(1 << d)]
                staged = tensor_staged(xs, d, inverse)
                assert staged == tensor_closed(xs, d, inverse)
                for z in staged:
                    binary_numerator = scale(1 << ((d+1)//2), z)
                    assert is_integer(binary_numerator)
                    if d % 2: assert pi_residue(binary_numerator) == 0
                assert tensor_staged(staged, d, not inverse) == xs
                counts["tensor_cases"] += 1
                counts["tensor_output_values"] += len(staged)
                if not inverse:
                    normalized=normalized_via_phase(xs,d)
                    assert normalized == normalized_closed(xs,d)
                    assert all(is_integer(scale(1 << d,z)) for z in normalized)
                    counts["normalized_cases"] += 1
                    counts["normalized_output_values"] += len(normalized)
        impulse = [ONE] + [(0,0)]*((1 << d)-1)
        z = tensor_staged(impulse,d)[0]
        q = (d+1)//2
        assert is_integer(scale(1 << q,z))
        if q: assert not is_integer(scale(1 << (q-1),z))
        counts["sharpness_dimensions"] += 1
        h=normalized_via_phase(impulse,d)[0]
        assert h == (F(1,1 << d),0)
        if d: assert not is_integer(scale(1 << (d-1),h))
        if d >= 2: assert not is_integer(scale(1 << q,h))
        counts["normalized_sharpness_dimensions"] += 1
    # A stronger componentwise-parity test wrongly rejects this legal pair.
    assert pair((1,0),(0,1)) == ((1,1),(0,0))
    # Uniform pi residue on a tensor input is NOT enough for complete integrality.
    bad = [(0,0),(0,0),PI,(0,0)]
    assert len({pi_residue(z) for z in bad}) == 1
    assert any(not is_integer(z) for z in tensor_staged(bad,2))
    # Forgetting (1+i)'s odd numerator causes an illegal exact divide.
    assert not is_integer(divide((1,0),PI))
    print(json.dumps({"status":"passed","counts":counts,
      "negative_controls":["componentwise pair parity too strong", "uniform tensor pi residue insufficient", "odd Gaussian numerator division rejected", "C grid bound insufficient for normalized H0 when D>=2"],
      "scope":"finite exact arithmetic controls; no asymptotic or tape-machine claim"},indent=2))

if __name__ == "__main__": main()
