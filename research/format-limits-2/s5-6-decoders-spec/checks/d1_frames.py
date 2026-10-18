"""D1 (frame-substitution part): the E-graph of P112 has 1260 cliques of size 8 ('frames') and none of size 9; any exact decoder
restricted to a frame is a full-rank 8x8 problem, so >= 8 terms meet every frame.  Searching label-span pairs (U,V) for the best
(fraction of frames hit)/beta gives max 1/8 at beta 8 and strictly more at beta 3..7, hence the weighted covering bound is only
ceil(8/rho) ~ 44 < 64: the frame-substitution argument does not prune decoders that mix beta<=7 terms.
Same search space as the original run (all-lines x hyperplane, hyperplane x hyperplane, 20000 random codim<=3 pairs, random.seed(1))."""
import random, numpy as np
import e8model as m

fails = 0
def ok(tag, cond, info=""):
    global fails
    print(("PASS " if cond else "FAIL ") + tag + (" | " + info if info else ""), flush=True)
    fails += (not cond)

n = 112
par = lambda x: bin(x).count("1") & 1
L = list(m.Lm); LS = list(m.LSm)
N = np.array([[par(LS[i] & L[j]) for j in range(n)] for i in range(n)], dtype=np.uint8)
assert (N == N.T).all()
A = (N == 1) & ~np.eye(n, dtype=bool)
fr = []
def ext(cl, cand):
    if len(cl) == 8:
        fr.append(tuple(cl)); return
    for k, v in enumerate(cand):
        ext(cl + [v], [w for w in cand[k + 1:] if A[v, w]])
ext([], list(range(n)))
fr = np.array(fr); F = len(fr)
ok("D1.frames.1260-eight-cliques", F == 1260, str(F))
# no 9-clique: extend each 8-clique by a common E-neighbour
common9 = any(A[list(c)].all(0).any() for c in fr)
ok("D1.frames.no-9-clique", not common9)

nb = max(x.bit_length() for x in L)
# parity table and per-line 'violation' ints for fast label spans
Pm = np.array([[par(w & x) for w in range(1 << nb)] for x in L], dtype=bool)      # Pm[i,w] = <w, l_i>
Pint = [int("".join("1" if b else "0" for b in row[::-1]), 2) for row in Pm]
spancache = {}
def span_of(R):
    key = 0
    for i in R: key |= Pint[i]
    if key not in spancache:
        perp = [w for w in range(1 << nb) if not (key >> w) & 1]          # w with <w,l>=0 for all l in R
        U = [v for v in range(1 << nb) if all(par(v & w) == 0 for w in perp)]
        spancache[key] = m.span_basis(U)
    return key, spancache[key]
rcache = {}
def beta(R, Aset):
    (kr, ur), (ka, ua) = span_of(R), span_of(Aset)
    if (kr, ka) not in rcache:
        # pairing rank of U x V under the label form (rows of LS-space vs labels): use the model's pair_rank on bases
        vb = m.span_basis([int("".join(str(x) for x in (np.array([(u >> (nb - 1 - i)) & 1 for i in range(nb)]) @ m.S9 % 2)), 2) for u in ur])
        rows = []
        for v in vb:
            row = 0
            for k, w in enumerate(ua): row |= (bin(v & w).count("1") & 1) << k
            rows.append(row)
        rcache[(kr, ka)] = len(m.span_basis(rows))
    return rcache[(kr, ka)]
def hit(R, Aset):
    Rm = np.zeros(n, bool); Rm[R] = 1; Am = np.zeros(n, bool); Am[Aset] = 1
    return (Rm[fr].any(1) & Am[fr].any(1)).sum()
best = {}
def upd(b, r):
    if b not in best or r > best[b]: best[b] = r
def ev(R, Aset):
    if len(R) == 0 or len(Aset) == 0: return None
    b = beta(R, Aset)
    if b == 0: return (0, 0.0)
    return (b, hit(R, Aset) / F / b)
def lines_with(ws):
    okm = np.ones(n, bool)
    for w in ws: okm &= ~Pm[:, w]
    return np.nonzero(okm)[0]
allL = np.arange(n)
hyp = {w: lines_with([w]) for w in range(1, 1 << nb)}
for w in hyp:
    r = ev(allL, hyp[w])
    if r: upd(*r)
for w in hyp:
    for v in hyp:
        if v < w: continue
        r = ev(hyp[w], hyp[v])
        if r: upd(*r)
random.seed(1)
for t in range(20000):
    k1 = random.choice([1, 2, 3]); k2 = random.choice([1, 2, 3])
    w = [random.randrange(1, 1 << nb) for _ in range(k1)]; v = [random.randrange(1, 1 << nb) for _ in range(k2)]
    r = ev(lines_with(w), lines_with(v))
    if r: upd(*r)
print("beta : max (frames hit / 1260) / beta   [1/8 = 0.125]")
for b in sorted(best): print("  ", b, round(best[b], 4))
ok("D1.frames.beta8-max-is-exactly-1/8", abs(best[8] - 0.125) < 1e-12, "%.6f" % best[8])
ok("D1.frames.beta7-pair-hits-all-frames", abs(best[7] - 1 / 7) < 1e-12, "%.6f" % best[7])
ok("D1.frames.beta6-pair-hits-all-frames", abs(best[6] - 1 / 6) < 1e-12, "%.6f" % best[6])
rho = max(best.values())
ok("D1.frames.covering-bound-below-64", 40 <= 8 / rho < 48, "rho %.4f, 8/rho = %.1f (sampled rho; the bound only falls as rho grows)" % (rho, 8 / rho))
raise SystemExit(1 if fails else 0)
