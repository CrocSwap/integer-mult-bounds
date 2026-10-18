"""D1: complex decoder floor on P112 (B14 model).  Reproduces, in memory and from nothing but the E8 root system:
  (1) the reduction lemma (N-graph; free entries; 5824 forced entries are all nonzero),
  (2) the census of hyperplane-flat supports: 440,880 supports, 9 label spans, minimum pairing rank 8,
  (3) the tangent-space nullity 175 of the n=8 masked system at the coordinate decoder (gauge dimension 176 - 1)."""
import itertools, time, numpy as np, sympy
import e8model as m

fails = 0
def ok(tag, cond, info=""):
    global fails
    print(("PASS " if cond else "FAIL ") + tag + (" | " + info if info else ""), flush=True)
    fails += (not cond)

n = 112
DOT = (m.Ln @ m.S9 @ m.Ln.T) % 2
E = (DOT == 1) & ~np.eye(n, dtype=bool)
Z = m.M4
# (1) reduction lemma
ok("D1.reduce.diagonal-label-pairing-1", set(DOT.diagonal()) == {1})
ok("D1.reduce.N-equals-1-iff-E8-ip-even", ((DOT == 1) == (m.G % 2 == 0)).all())
ok("D1.reduce.N0-entries-5824-all-nonzero-in-M4", (DOT == 0).sum() == 5824 and ((Z != 0) & (DOT == 0)).sum() == 5824)
ok("D1.reduce.M4-zero-on-E-offdiag", (Z[E] == 0).all())
ok("D1.reduce.rank-F2-N-is-9", len(m.span_basis(m.tomask(DOT))) == 9)
ok("D1.reduce.E-graph-60-ones-per-row", set(DOT.sum(1)) == {60})

# (2) census of hyperplane flats: supports S_q = {i : <r_i, q> != 0}, q in W(E8)-orbits of the 8 fundamental weights
B = m.basis()
Bi = sympy.Matrix(B.tolist())
W = ((Bi * Bi.T) / 4).inv()
omegas = [np.array([int(x) for x in (W[i, :] * Bi)]) for i in range(8)]

def orbit(o):
    seen = {tuple(o)}; fr = np.array([o]); allv = [fr]
    while len(fr):
        new = []
        for r in B:
            c = fr @ r
            assert (c % 4 == 0).all()
            new.append(fr - (c // 4)[:, None] * r[None, :])
        new = np.unique(np.concatenate(new), axis=0)
        keep = [v for v in map(tuple, new) if v not in seen]
        seen.update(keep); fr = np.array(keep) if keep else np.zeros((0, 8), int)
        if len(fr): allv.append(fr)
    return np.concatenate(allv)

RP32 = m.RP.astype(np.int32)
masks = set(); sizes = []
for o in omegas:
    V = orbit(o).astype(np.int32); sizes.append(len(V))
    Sm = (V @ RP32.T) != 0
    for row in np.unique(np.packbits(Sm, axis=1), axis=0): masks.add(row.tobytes())
ok("D1.census.orbit-sizes", sorted(sizes) == [240, 2160, 6720, 17280, 60480, 69120, 241920, 483840], str(sorted(sizes)))
ok("D1.census.440880-distinct-supports", len(masks) == 440880, str(len(masks)))
Sb = np.unpackbits(np.array([np.frombuffer(b, dtype=np.uint8) for b in masks]), axis=1)[:, :112].astype(np.float32)
# label span of a support: U^perp = {w : <w,l_i> = 0 for all i in S};  key = which w are violated
par = lambda x: bin(x).count("1") & 1
Pm = np.array([[par(w & m.Lm[i]) for w in range(1, 512)] for i in range(n)], dtype=np.float32)
keys = set()
for a in range(0, len(Sb), 40000):
    viol = (Sb[a:a + 40000] @ Pm) > 0
    for row in np.unique(np.packbits(viol, axis=1), axis=0): keys.add(row.tobytes())
Us = []
for k in keys:
    viol = np.unpackbits(np.frombuffer(k, dtype=np.uint8))[:511].astype(bool)
    perp = [w for w in range(1, 512) if not viol[w - 1]]
    U = [v for v in range(512) if all(par(v & w) == 0 for w in perp)]
    Us.append(m.span_basis(U))
dims = sorted(len(u) for u in Us)
ok("D1.census.9-distinct-label-spans", len(Us) == 9 and dims == [8] * 8 + [9], str(dims))
def form(u, v):
    a = np.array([(u >> (8 - i)) & 1 for i in range(9)]); b = np.array([(v >> (8 - i)) & 1 for i in range(9)])
    return int(a @ m.S9 @ b) % 2
def rank_pair(U, V):
    rows = []
    for u in U:
        row = 0
        for k, v in enumerate(V): row |= form(u, v) << k
        rows.append(row)
    return len(m.span_basis(rows))
betas = [rank_pair(U, V) for U in Us for V in Us]
ok("D1.census.min-pair-beta-is-8", min(betas) == 8, "min %d over %d ordered pairs of spans" % (min(betas), len(betas)))

# (3) tangent space at the coordinate decoder
X0 = m.RP.astype(float); c = 0.5
idx = np.nonzero((DOT == 1).ravel())[0]   # E-graph incl. the diagonal: 112*60 = 6720 constraints
J = np.zeros((len(idx), 112 * 8 * 2))
for t, k in enumerate(idx):
    i, j = divmod(k, 112)
    J[t, i * 8:(i + 1) * 8] = c * X0[j]
    J[t, 896 + j * 8:896 + (j + 1) * 8] = c * X0[i]
rk = np.linalg.matrix_rank(J, tol=1e-8)
ok("D1.rigid.tangent-nullity-175", J.shape == (6720, 1792) and rk == 1617 and 1792 - rk == 175,
   "rank %d nullity %d; gauge GL8(64)+row scalings(112)-1 shared = 175" % (rk, 1792 - rk))
raise SystemExit(1 if fails else 0)
