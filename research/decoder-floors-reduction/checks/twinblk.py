"""CANCEL: dangling-proof cancellation witnesses, one shared term (call-0 coord i merged with call-1 coord j), square coordinate restrictions.
i-twins: lines r, r' with x_r = c x_r' off coordinate i and x_r,i = -c x_r',i (each line of N(f_i) has exactly one).
Omega = (e_r - c e_r')(e_s - c' e_s')^T kills all dangling (outputs X e_k, k != i; inputs X e_l, l != j) and has <Omega, X e_i (X e_j)^T> != 0.
It is a valid witness iff the 2x2 block {r,r'} x {s,s'} is all-ones in B01. An induced family of n such blocks forces canceller cost >= n.
Report: #valid blocks and a greedy lower bound on the largest induced family, per (i,j), per chart."""
import sys, random; sys.path.insert(0, '.')
from dangle import *
def twins(i):
    out = []; S = np.nonzero(X[:, i])[0]
    for a in S:
        for b in S:
            if a < b:
                for c in (1, -1):
                    if all(X[a, k] == c * X[b, k] for k in range(8) if k != i) and X[a, i] == -c * X[b, i]: out.append((a, b, c))
    return out
TW = [twins(i) for i in range(8)]; assert all(len(t) == 28 for t in TW)
rng = random.Random(11); hist = {}
for trial in range(int(sys.argv[1]) if len(sys.argv) > 1 else 4):
    Phi = np.eye(9, dtype=np.int64) if trial == 0 else rand_phi(rng)
    B01 = (lab @ Gb @ ((lab @ Phi.T) % 2).T) % 2
    for i in range(8):
        for j in range(8):
            blocks = [((a, b), (s, t)) for (a, b, c) in TW[i] for (s, t, d) in TW[j] if B01[np.ix_([a, b], [s, t])].all()]
            # sanity: witness value and dangling-orthogonality
            for (a, b), (s, t) in blocks[:3]:
                pass
            best = 0
            for _ in range(200):
                cand = blocks[:]; k = 0
                while cand:
                    R, C = rng.choice(cand); k += 1
                    cand = [(R2, C2) for (R2, C2) in cand if not B01[np.ix_(list(R), list(C2))].any() and not B01[np.ix_(list(R2), list(C))].any()]
                best = max(best, k)
            hist[(len(blocks) > 0, best)] = hist.get((len(blocks) > 0, best), 0) + 1
    print('trial', trial, 'Phi=I' if trial == 0 else '', '(any block, induced family LB):', dict(sorted(hist.items())), flush=True)
