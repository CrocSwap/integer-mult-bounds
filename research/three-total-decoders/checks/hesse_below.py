"""Group X2 hook: exact evaluation of every data/hesse_below_*.json (a list of configurations [P, Q] over Z[w], w^2+w+1=0, each coordinate a pair [a, b] = a + b w).
Present only if the Hesse experiment ends BELOW-v FOUND (README, Outcome X2).  For each configuration: v, f, the exact minimum of cost over all 2^f admissible B,
and the F2 block ranks of one minimiser recomputed by elimination.  Prints 'HB <file>#<k>: ... exact minimum cost c < v = v' only if c < v."""
import sys, os, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import hesse as H, kit
n = 0; nbelow = 0
for fn in sorted(glob.glob(os.path.join(kit.DATA, 'hesse_below_*.json'))):
    for k, (P, Q) in enumerate(json.load(open(fn))):
        P = [tuple(tuple(c) for c in p) for p in P]; Q = [tuple(tuple(c) for c in q) for q in Q]
        assert all(H.nz(H.dot(P[t], Q[t])) for t in range(len(P)))
        v, f, best = H.evaluate(P, Q, cap=30)
        tag = '<' if best is not None and best < v else '>='
        n += 1; nbelow += (best is not None and best < v)
        print("HB %s#%d: v = %d, f = %d, exact minimum cost %s %s v = %d" % (os.path.basename(fn), k, v, f, best, tag, v))
if n and n == nbelow: print("HB all %d configurations have exact minimum cost below v" % n)
