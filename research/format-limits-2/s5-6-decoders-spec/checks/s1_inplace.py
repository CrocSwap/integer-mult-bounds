"""S1: in-place elimination is dead under the shipped frame rules (ck word of #622/#626, frames = F2^9 subspaces).
Reads inputs/pr626/ck-CANONICAL-WORD.json.gz.  The content map M is recomputed by exact rational replay of the word's A, B and cut
phases (target t = register 112+t, source j = register j)."""
import gzip, json, os, sys
from fractions import Fraction as Q
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(gzip.open(os.path.join(ROOT, "inputs/pr626/ck-CANONICAL-WORD.json.gz")))
fails = 0
def ok(tag, cond, info=""):
    global fails
    print(("PASS " if cond else "FAIL ") + tag + (" | " + info if info else ""), flush=True)
    fails += (not cond)

fr = d["frames"]; ports = d["ports"]; fin = d["final"]
def spanset(B):
    s = {0}
    for b in B: s |= {x ^ b for x in s}
    return frozenset(s)
par = lambda x: bin(x).count("1") & 1
H = [spanset(fr[fin[112 + p]]) for p in range(112)]
ok("S1.ports-distinct", len(set(ports)) == 112)
ok("S1.target-end-frame-is-perp-port", all(H[p] == frozenset(w for w in range(512) if par(w & ports[p]) == 0) for p in range(112)))
ok("S1.port-not-in-own-end-frame", sum(ports[p] in H[p] for p in range(112)) == 0, "0/112")
A = np.zeros((112, 112), int)
for a in range(112):
    for b in range(112):
        if a != b:
            A[a, b] = {ports[a], ports[b], ports[a] ^ ports[b]} <= (H[a] & H[b])
ok("S1.legal-cross-port-inplace-0-of-12432", A.sum() == 0 and 112 * 111 == 12432)
B = np.array([[ports[b] in H[a] for b in range(112)] for a in range(112)], int)
ok("S1.legal-target-reads-5824-diag-0", B.sum() == 5824 and np.trace(B) == 0, str(B.sum()))
# content map by exact replay
rows = {r: {r: Q(1)} for r in range(112)}
for ph in ("A", "B", "cut"):
    for o in d[ph]:
        if o[0] == "add":
            t, s = o[1], o[2]; q = Q(o[3], o[4]); rt = rows.setdefault(t, {})
            for j, x in list(rows.get(s, {}).items()):
                z = rt.get(j, 0) + q * x
                if z: rt[j] = z
                else: rt.pop(j, None)
        else:
            t = o[1]; q = Q(o[2], o[3]); rows[t] = {j: q * x for j, x in rows.get(t, {}).items()}
M = np.zeros((112, 112))
for t in range(112):
    for j, x in rows[112 + t].items(): M[t, j] = float(x)
off = (np.abs(M) > 1e-9) & ~np.eye(112, dtype=bool)
nz = int((np.abs(M) > 1e-9).sum()); legal = int((off & (B > 0)).sum()); tot = int(off.sum())
print("   M: nnz %d, off-diagonal %d, off-diagonal inside the legal read mask %d (%.1f%%), rank %d" % (nz, tot, legal, 100 * legal / tot, np.linalg.matrix_rank(M)))
ok("S1.M-rank-112", np.linalg.matrix_rank(M) == 112)
ok("S1.M-offdiag-legal-5264-of-8960", (legal, tot) == (5264, 8960), "%d legal, %d illegal off-diagonal reads (41.2%% illegal) on the vendored canonical word" % (legal, tot - legal))
rowill = (off & (B == 0)).sum(1)
ok("S1.every-row-needs-illegal-reads", rowill.min() == rowill.max() == 33, "per-row illegal reads min %d max %d mean %.1f" % (rowill.min(), rowill.max(), rowill.mean()))
raise SystemExit(1 if fails else 0)
