"""CANCEL: close one-shared-term batches with square coordinate restrictions (any dangling, any cancellers, unconditional via Thm P).
batch >= 64 + 64 - saving + n01 + n10, saving = 16 - cost(shared), n = induced family of twin 2x2 witness blocks (greedy LB).
Closed iff n01 + n10 >= saving. Block (1,0) is handled by the same search on B10 = B01^T with roles swapped."""
import sys, random; sys.path.insert(0, '.')
sys.argv = sys.argv[:1] + ['0']
exec(open('twinblk.py').read().split('rng = random.Random(11)')[0])
def fam(Bc, Ti, Tj, rng, tries=300):
    blocks = [((a, b), (s, t)) for (a, b, c) in Ti for (s, t, d) in Tj if Bc[np.ix_([a, b], [s, t])].all()]
    best = 0
    for _ in range(tries if blocks else 0):
        cand = blocks[:]; k = 0
        while cand:
            R, C = rng.choice(cand); k += 1
            cand = [(R2, C2) for (R2, C2) in cand if not Bc[np.ix_(list(R), list(C2))].any() and not Bc[np.ix_(list(R2), list(C))].any()]
        best = max(best, k)
    return best
rng = random.Random(5); tot = clo = 0; open_ = {}
NT = 8
for trial in range(NT):
    Phi = np.eye(9, dtype=np.int64) if trial == 0 else rand_phi(rng)
    L1 = (lab @ Phi.T) % 2; B01 = (lab @ Gb @ L1.T) % 2
    for i in range(8):
        for j in range(8):
            Ri = np.nonzero(X[:, i])[0]; Aj = np.nonzero(X[:, j])[0]
            U = np.vstack([lab[Ri], L1[Aj]]); cost = rank2((U @ Gb @ U.T) % 2); sav = 16 - cost
            n01 = fam(B01, TW[i], TW[j], rng); n10 = fam(B01.T.copy(), TW[j], TW[i], rng)
            tot += 1; ok = n01 + n10 >= sav; clo += ok
            if not ok: open_[(sav, n01, n10)] = open_.get((sav, n01, n10), 0) + 1
    print(f'trial {trial}: closed {clo}/{tot}; open (saving, n01, n10): {open_}', flush=True)
