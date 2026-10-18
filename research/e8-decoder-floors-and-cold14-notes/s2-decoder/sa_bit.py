import sys, random, math
from fractions import Fraction as Fr
from bitp import *
def ev(Pset):
    live = [i for i in range(NL) if i not in Pset]
    if rankQ_lines(live) < 8: return None
    ch, c = greedy_basis(s_all(Pset))
    return c
def sa(p, iters, seed):
    rng = random.Random(seed)
    P = set(rng.sample(range(NL), p))
    c = ev(P); best = (Fr(c, NL - p), sorted(P), c)
    T = 2.0
    for it in range(iters):
        out = rng.choice(sorted(P)); inn = rng.choice([i for i in range(NL) if i not in P])
        Q = set(P); Q.remove(out); Q.add(inn)
        cq = ev(Q)
        if cq is None: continue
        if cq <= c or rng.random() < math.exp(-(cq - c) / T):
            P, c = Q, cq
            if Fr(c, NL - p) < best[0]: best = (Fr(c, NL - p), sorted(P), c)
        T = max(0.05, T * 0.999)
    return best
if __name__ == '__main__':
    p = int(sys.argv[1]); seed = int(sys.argv[2]); iters = int(sys.argv[3])
    b = sa(p, iters, seed)
    print(p, seed, 'cst', b[2], 'v', NL - p, 'x', b[0], float(b[0]), b[1], flush=True)
