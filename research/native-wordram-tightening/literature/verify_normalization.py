"""Exact rational controls for the separately proved all-field normalizer."""
from fractions import Fraction as F
from itertools import product
from random import Random
import json


def normalizer(factors):
    if not factors or any(len(g) != 4 or any(z == 0 for z in g) for g in factors):
        raise ValueError("nonempty list of all-nonzero 2 by 2 factors required")
    n = 1 << len(factors)
    ts = [a*d/(b*c) for a,b,c,d in factors]
    left, right, values = [], [], []
    for x in range(n):
        l = r = v = F(1)
        for i,(a,b,c,d) in enumerate(factors):
            bit = (x >> i) & 1
            l *= c if bit else a
            r *= b/a if bit else 1
            v *= 1 if bit else ts[i]
        left.append(l); right.append(r); values.append(v)
    return left, right, values


def direct(factors,x,y):
    ans=F(1)
    for i,g in enumerate(factors):
        ans *= g[2*((x>>i)&1)+((y>>i)&1)]
    return ans


def check(factors):
    left,right,values=normalizer(factors)
    n=len(values); mask=n-1
    changed=False
    for x in range(n):
        for y in range(n):
            actual=direct(factors,x,y)
            supplied=left[x]*values[(x^mask)|(y^mask)]*right[y]
            if actual != supplied:
                raise ValueError("normalizer does not preserve complete matrix")
            # Omitting complement is a meaningful wrong identity control.
            changed |= actual != left[x]*values[x|y]*right[y]
    return n*n,changed


def main():
    rng=Random(20261022); count=entries=controls=0
    domain=[F(a,b) for a in [-5,-3,-2,-1,1,2,3,5] for b in [1,2,3]]
    for k in range(1,7):
        for _ in range(12):
            gs=[tuple(rng.choice(domain) for _ in range(4)) for _ in range(k)]
            checked,changed=check(gs); entries+=checked; count+=1
            if changed:controls+=1
    rejected=0
    for i in range(4):
        g=[F(1),F(2),F(3),F(5)];g[i]=0
        try:normalizer([g])
        except ValueError:rejected+=1
        else:raise ValueError("zero-entry guard accepted malformed input")
    if rejected != 4 or controls < 60:
        raise ValueError("controls did not exercise declared domain")
    print(json.dumps({"status":"PASS_EXACT_PAID_OR_NORMALIZATION", "rational_factor_cases":count,"matrix_entries_checked":entries,"omitted_flip_controls":controls,"zero_entry_rejections":rejected,"new_kappa_established":False},sort_keys=True))


if __name__ == "__main__":main()
