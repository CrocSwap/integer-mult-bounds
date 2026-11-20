"""Differential checks of the pinned covered rank-one lowering at new rings."""

import sys
from math import gcd
from pathlib import Path
from random import Random


def assert_equal(actual, expected):
    if actual != expected:
        raise ValueError((actual, expected))


def lift(seed_u, seed_v, pivot, prime, modulus, random):
    u = [a + prime*random.randrange(modulus//prime) for a in seed_u]
    v = [a + prime*random.randrange(modulus//prime) for a in seed_v]
    v[pivot] = (1 - sum(a*b for i,(a,b) in enumerate(zip(u,v)) if i != pivot)) * pow(
        u[pivot], -1, modulus) % modulus
    assert_equal(sum(a*b for a,b in zip(u,v)) % modulus, 1)
    return u,v,[[a*b % modulus for b in v] for a in u]


def oracle(u, v, weights, head, tail, modulus, wrong_tail=False):
    n, f = len(u), len(weights)
    out = [[0]*f for _ in range(2*n)]
    for j, units in enumerate(weights):
        logical = j if wrong_tail else f-1-j
        x = [row[j] * pow(a,-1,modulus) % modulus for row,a in zip(head,units)]
        y = [tail[n-1-i][logical] for i in range(n)]
        pairing = sum(v[i]*(y[i]-x[i]) for i in range(n)) % modulus
        for i in range(n):
            out[i][j] = units[i]*(x[i]+u[i]*pairing) % modulus
            out[2*n-1-i][logical] = (y[i]-u[i]*pairing) % modulus
    return out


def topology(program):
    return tuple(tuple(op) if op[0] == "sign" else tuple(op[:3]) for op in program)


def main(package):
    sys.path.insert(0,str(package.resolve()))
    from leaf import column_program, run_columns
    rng = Random(7830480)
    counts = {"cases":0,"good":0,"bad":0,"nonzero_nonunit":0,"wrong_tail_rejected":0,
              "wrong_weight_rejected":0}
    for prime, power in ((3,2),(3,3),(5,2),(7,2)):
        modulus = prime**power
        units = tuple(x for x in range(1,modulus) if gcd(x,prime)==1)
        for n in (2,3,5):
            for seed in range(4):
                # Both genuine good and genuine bad residue classes.
                pivot = 0 if seed%2==0 else n-1
                seed_u = [rng.randrange(prime) for _ in range(n)]
                seed_u[pivot] = 1
                if seed%2:
                    seed_u[0] = 0
                seed_v = [rng.randrange(prime) for _ in range(n)]
                fixed_topology = None
                for _ in range(4):
                    u,v,p = lift(seed_u,seed_v,pivot,prime,modulus,rng)
                    for f in (1,2,3,6,7):
                        weights = [[rng.choice(units) for _ in range(n)] for _ in range(f)]
                        head = [[rng.randrange(modulus) for _ in range(f)] for _ in range(n)]
                        tail = [[rng.randrange(modulus) for _ in range(f)] for _ in range(n)]
                        actual,good,calls = run_columns(p, weights, head, tail,prime,power)
                        assert_equal(actual, oracle(u,v,weights,head,tail,modulus))
                        assert_equal(good,gcd(p[0][0],prime)==1)
                        assert_equal(all(c in (f,f//2) and c>0 for c in calls),True)
                        assert_equal(calls==[f] if good else len(calls)<32*n*n, True)
                        for coeff in weights:
                            ops, mode = column_program(p,coeff,prime,power)
                            if fixed_topology is None:
                                fixed_topology = topology(ops)
                            assert_equal((topology(ops),mode),(fixed_topology,good))
                        counts["cases"] += 1
                        counts["good" if good else "bad"] += 1
                        counts["nonzero_nonunit"] += int(not good and p[0][0]!=0)
                        counts["wrong_tail_rejected"] += int(actual!=oracle(
                            u,v,weights,head,tail,modulus,wrong_tail=True))
                        counts["wrong_weight_rejected"] += int(actual!=oracle(
                            u,v,[[1]*n for _ in range(f)],head,tail,modulus))
    for x in counts.values():
        assert_equal(x>0,True)
    print(counts)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
