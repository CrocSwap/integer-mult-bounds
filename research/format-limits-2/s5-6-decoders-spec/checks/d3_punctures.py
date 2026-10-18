"""D3: exact non-star complex decoders on punctured P112 (B14 model, D T^T = M4 on the kept lines, cost = sum of F2 pairing ranks).
 P111: six single-line punctures (0,1,30 D8-type; 48,70,111 spin-type) reach cst 63 with one cost-7 term; punctures 0 and 111 also at |coef|<=2.
 P104: P112 minus the 8-clique drawn by numpy default_rng(1) (label-nonorthogonal lines) reaches cst 56 (three independent walkers)."""
import glob, os, numpy as np
import e8model as m
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = 0
def ok(tag, cond, info=""):
    global fails
    print(("PASS " if cond else "FAIL ") + tag + (" | " + info if info else ""), flush=True)
    fails += (not cond)
def load(f):
    D = []; T = []
    for l in open(f):
        s = l.strip()
        if s.startswith("d:"): D.append([int(x) for x in s[2:].split()])
        if s.startswith("t:"): T.append([int(x) for x in s[2:].split()])
    return np.array(D).T, np.array(T).T
def verify(f, keep):
    D, T = load(f); keep = list(keep)
    ex = (D @ T.T == m.M4[np.ix_(keep, keep)]).all()
    Df = np.zeros((112, D.shape[1]), int); Tf = Df.copy(); Df[keep] = D; Tf[keep] = T
    cs = [m.pair_rank(np.nonzero(Df[:, k])[0], np.nonzero(Tf[:, k])[0]) for k in range(D.shape[1])]
    return ex, cs, int(abs(D).max()), int(abs(T).max()), D.shape[1]
for name, q in (("g0", 0), ("g1", 1), ("g30", 30), ("g48", 48), ("g70", 70), ("g111", 111), ("c2_0", 0), ("c2_111", 111)):
    ex, cs, cd, ct, n = verify(os.path.join(ROOT, "inputs/local-hits/P111/HIT_%s.txt" % name), [i for i in range(112) if i != q])
    cap = 2 if name.startswith("c2") else 3
    ok("D3.P111.puncture%d.%s" % (q, name), ex and n == 8 and sum(cs) == 63 and sorted(cs) == [7] + [8] * 7 and max(cd, ct) <= cap,
       "exact, n=8, costs %s, max|coef| %d" % (cs, max(cd, ct)))
rng = np.random.default_rng(1)
while True:
    cl = [int(rng.integers(112))]
    cand = [i for i in range(112) if m.DOT[cl[0], i] == 1 and i != cl[0]]
    while cand and len(cl) < 8:
        c = cand[int(rng.integers(len(cand)))]; cl.append(c)
        cand = [i for i in cand if m.DOT[c, i] == 1 and i != c]
    if len(cl) == 8: break
keep = [i for i in range(112) if i not in cl]
ok("D3.P104.removed-set-is-8-clique", sorted(cl) == [9, 15, 24, 46, 52, 66, 94, 104] and all(m.DOT[a, b] == 1 for a in cl for b in cl if a != b), str(sorted(cl)))
for s in "abc":
    ex, cs, cd, ct, n = verify(os.path.join(ROOT, "inputs/local-hits/P104/HIT_flip_3%s.txt" % s), keep)
    ok("D3.P104.walker-%s-exact-cost-56" % s, ex and n == 8 and sum(cs) == 56, "costs %s, max|coef| %d" % (cs, max(cd, ct)))
raise SystemExit(1 if fails else 0)
