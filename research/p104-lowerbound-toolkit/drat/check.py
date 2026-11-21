#!/usr/bin/env python3
"""Checks for the TIGHT55 DRAT certificate package (standard library only; no solver, no pickles, no absolute paths).

  python3 check.py              hash reproduction for 100 evenly spaced cubes + every structural check
  python3 check.py --sample N   hash reproduction for N cubes
  python3 check.py --full       hash reproduction for ALL 1001 cubes (plus the base CNF, implicitly)

Structural checks (all exact, from data/e8base.json, data/labels.txt, data/zclauses.json, data/perms.json):
  geometry; covering clauses re-derived from the Z4 definition; tight vectors = +-Z16; price formula;
  the 384 symmetries (group, each realised by T in GL(9,2): ports permuted, Q invariant, covering clauses mapped);
  CNF fidelity spot checks (representability, membership forced, totalizer, lex-leader extension);
  cube structure; splits exhaustive and disjoint; PARTITION COMPLETENESS: the exhaustive search over all 65536
  inactive sets I finds exactly 993 sets that admit a d satisfying all 384 lex constraints, and the cubes cover all
  of them; the old partition (indicator-orbit-lexmax only) is shown unsound on two explicit witnesses.
What this does NOT check: that kissat's UNSAT is right (that is DRAT, run_drat.sh), the paper reductions (README).
"""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gen  # noqa: E402

DATA = HERE / "data"
ok_all = True
T0 = time.time()


def report(name, ok, info=""):
    global ok_all
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + name + ("  [" + info + "]" if info else ""), flush=True)


def rank(vs):
    piv = []
    for x in vs:
        for p in piv:
            x = min(x, x ^ p)
        if x:
            piv.append(x)
    return len(piv)


def bits(v):  # list of 0/1 -> int, entry 0 = bit 0
    return sum(int(b) << i for i, b in enumerate(v))


# ------------------------------------------------------------------ geometry
E = json.loads((DATA / "e8base.json").read_text())
CR = E["C"]; G = E["Gb"]
LAB = [int(x) for x in (DATA / "labels.txt").read_text().split()]
assert len(CR) == 120 and len(LAB) == 104
C = CR[:104]; Z = CR[104:]
ip = lambda a, b: sum(a[i] * G[i][j] * b[j] for i in range(8) for j in range(8))
report("all 120 vectors are roots (norm 2) of E8", all(ip(c, c) == 2 for c in CR))
Bm = [[x % 2 for x in r] for r in G]
H = [[1] + [x % 2 for x in c] for c in C]
Nz = [[1] + [x % 2 for x in z] for z in Z]


def beta(x, y):
    return (x[0] * y[0] + sum(x[1 + i] * Bm[i][j] * y[1 + j] for i in range(8) for j in range(8))) % 2


Q = [[bin(a & b).count("1") & 1 for b in LAB] for a in LAB]
report("P104 geometry: Q == H beta H^T (mod 2) from labels.txt",
       all(beta(H[s], H[t]) == Q[s][t] for s in range(104) for t in range(104)))
Hs = {tuple(h) for h in H}; Ns = {tuple(h) for h in Nz}
report("120 classes distinct mod 2; n_z is not a port label (so a row with U=<n_z> serves no port)",
       len({tuple(x % 2 for x in c) for c in CR}) == 120 and len(Hs) == 104 and len(Ns) == 16 and not (Hs & Ns))

# ------------------------------------------------------------------ Z4 table over all x in Z4^8
GC = [[sum(G[i][j] * c[j] for j in range(8)) for i in range(8)] for c in CR]   # (G c)_i ; <x,c> = sum x_i (Gc)_i
def half_tables(vec):
    lo = [sum(((x >> (2 * k)) & 3) * vec[k] for k in range(4)) for x in range(256)]        # x digits 0..3
    hi = [sum(((x >> (2 * k)) & 3) * vec[4 + k] for k in range(4)) for x in range(256)]    # digits 4..7
    return lo, hi
TAB = [half_tables(v) for v in GC]
IPC = [[0] * 104 for _ in range(65536)]
Rm = [0] * 65536
tight = []
for x in range(65536):
    lo_i, hi_i = x & 255, x >> 8
    row = [(TAB[v][0][lo_i] + TAB[v][1][hi_i]) % 4 for v in range(120)]
    IPC[x] = row[:104]
    m = 0
    for zi in range(16):
        if row[104 + zi]: m |= 1 << zi
    Rm[x] = m
    if x and 2 not in row[:104]:
        tight.append(x)
# digits of x: digit k = (x >> 2k) & 3 for k<8  (x = lo | hi<<8, consistent with half_tables)
CL = json.loads((DATA / "zclauses.json").read_text())
mism = 0
for t in range(104):
    Rs = sorted({Rm[x] for x in range(65536) if IPC[x][t] != 0}, key=lambda r: (bin(r).count("1"), r))
    mins = []
    for r in Rs:
        if not any((a & r) == a for a in mins):
            mins.append(r)
    if set(mins) != set(CL[t]) or len(mins) != len(CL[t]):
        mism += 1
report("zclauses.json == minimal covering masks re-derived from the Z4 definition (all 104 ports)", mism == 0,
       "clauses/port %d-%d" % (min(map(len, CL)), max(map(len, CL))))
digits = lambda x: tuple(((x >> (2 * k)) & 3) for k in range(8))
tset = {digits(x) for x in tight}
zset = {tuple(v % 4 for v in z) for z in Z} | {tuple((-v) % 4 for v in z) for z in Z}
report("tight Z4 vectors (no port value 2) are exactly {+-z : z in Z16}: 32 nonzero", tset == zset and len(tset) == 32)

# price formula
allv = list(itertools.product([0, 1], repeat=9))
bad = 0
for z in range(16):
    S = [s for s in range(104) if ip(C[s], Z[z]) % 4]
    if rank([bits(H[s]) for s in S]) != 8:
        bad += 1; continue
    perp = [v for v in allv if any(v) and all(beta(H[s], v) == 0 for s in S)]
    if not (len(perp) == 1 and list(perp[0]) == Nz[z]):
        bad += 1
report("price formula: span{h_s : s in S_z} is a hyperplane whose beta-perp is exactly n_z=(1,z), all 16 z", bad == 0,
       "so rank Q[P,S_z] = dim span(P) - [n_z in span(P)]; price_z = dim U_z - [n_z in U_z]")

# ------------------------------------------------------------------ symmetries
PERMS = [tuple(p) for p in json.loads((DATA / "perms.json").read_text())]
Pset = set(PERMS); ident = tuple(range(16))
report("perms.json: 384 distinct permutations of 0..15, a group",
       len(Pset) == 384 and all(sorted(p) == list(range(16)) for p in PERMS) and ident in Pset
       and all(tuple(p[q[i]] for i in range(16)) in Pset for p in PERMS for q in PERMS))
Zb = [[x % 2 for x in z] for z in Z]


def solve_g(rows, targets):
    A = [list(rows[i]) + list(targets[i]) for i in range(len(rows))]
    r = 0
    for c in range(8):
        p = next((i for i in range(r, len(A)) if A[i][c]), None)
        if p is None: return None
        A[r], A[p] = A[p], A[r]
        for i in range(len(A)):
            if i != r and A[i][c]: A[i] = [a ^ b for a, b in zip(A[i], A[r])]
        r += 1
    if any(any(A[i]) for i in range(8, len(A))): return None
    return [A[i][8:] for i in range(8)]


Hidx = {tuple(h): i for i, h in enumerate(H)}
CLs = [set(c) for c in CL]
nok = 0; why = set()
for p in PERMS:
    g = solve_g(Zb, [Zb[p[z]] for z in range(16)])
    if g is None: why.add("no T"); continue
    T = [[1] + [0] * 8] + [[0] + g[i] for i in range(8)]
    ap = lambda v: [sum(v[i] * T[i][j] for i in range(9)) % 2 for j in range(9)]
    if any(ap(Nz[z]) != Nz[p[z]] for z in range(16)): why.add("nT"); continue
    pp = []
    for h in H:
        k = Hidx.get(tuple(ap(h)))
        if k is None: break
        pp.append(k)
    if len(pp) != 104 or len(set(pp)) != 104: why.add("ports"); continue
    if any(Q[pp[s]][pp[t]] != Q[s][t] for s in range(104) for t in range(104)): why.add("Q"); continue
    if any({sum(1 << p[z] for z in range(16) if r >> z & 1) for r in CL[t]} != CLs[pp[t]] for t in range(104)):
        why.add("CL"); continue
    nok += 1
report("each of the 384 perms p is realised by T in GL(9,2): n_z T = n_{p z}, ports permuted (h_t T = h_{pp t}), Q invariant, "
       "covering clauses map onto themselves", nok == 384, "%d/384 %s" % (nok, sorted(why)))

# ------------------------------------------------------------------ CNF fidelity
b = gen.Base()
cls = b.cls
for i in range(1, 1):
    pass
rng = random.Random(1)
evalcl = lambda cl, val: all(any(val.get(abs(l), False) == (l > 0) for l in c) for c in cl)


def rand_perp(d):
    while True:
        rows = [tuple(rng.randint(0, 1) for _ in range(9)) for _ in range(d)]
        if rank([bits(r) for r in rows]) == d: break
    A = [list(r) for r in rows]; r = 0
    for c in range(9):
        p = next((i for i in range(r, len(A)) if A[i][c]), None)
        if p is None: continue
        A[r], A[p] = A[p], A[r]
        for i in range(len(A)):
            if i != r and A[i][c]: A[i] = [a ^ x for a, x in zip(A[i], A[r])]
        r += 1
    return [tuple(a) for a in A[:r]]


def assign(perps):
    val = {}
    for z in range(16):
        R = perps[z]
        for i in range(len(R)):
            val[b.used[z, i]] = True
            lead = next(c for c in range(9) if R[i][c])
            for c in range(9):
                val[b.f[z, i, c]] = bool(R[i][c]); val[b.L[z, i, c]] = (c == lead)
        for t in range(104):
            val[b.m[z, t]] = all(sum(r[c] * H[t][c] for c in range(9)) % 2 == 0 for r in R)
        val[b.nin[z]] = all(sum(r[c] * Nz[z][c] for c in range(9)) % 2 == 0 for r in R)
    for pv in sorted(b.xdef):
        a, c = b.xdef[pv]; val[pv] = val.get(a, False) ^ val.get(c, False)
    return val


rowcls = cls[:b.n_cov0]
ok1 = True
for trial in range(40):
    perps = [rand_perp(rng.choice([0, 1, 2, 3, 5, 7, 8, 9]) if trial % 3 else rng.randint(0, 9)) for _ in range(16)]
    if not evalcl(rowcls, assign(perps)): ok1 = False; break
report("representability: random 16-tuples of subspaces satisfy all row/xor/membership clauses with m=[h_t in U_z], nin=[n_z in U_z]", ok1, "40 random configs")
viol = 0
for trial in range(30):
    val = assign([rand_perp(rng.randint(1, 9)) for _ in range(16)])
    z = rng.randrange(16); outs = [t for t in range(104) if not val[b.m[z, t]]]
    if not outs: continue
    val[b.m[z, rng.choice(outs)]] = True
    viol += (not evalcl(rowcls, val))
report("membership forced: m[z,t]=True with h_t not in U_z violates a clause", viol > 0, "%d violations in 30 trials" % viol)

K = gen.K
okt = True
for trial in range(120):
    ct = rng.choice([K - 3, K - 1, K, K + 1, K + 5, rng.randint(0, 160)])
    bt = [1] * max(0, min(160, ct)) + [0] * (160 - max(0, min(160, ct))); rng.shuffle(bt)
    val = {l: bool(x) for l, x in zip(b.lits, bt)}
    for o, a, c in b.tnodes:     # post-order: children first
        cnt = sum(val[x] for x in a) + sum(val[x] for x in c)
        for k, v in enumerate(o): val[v] = cnt >= k + 1
    top = b.tnodes[-1][0]
    if not evalcl(cls[b.n_tot0:b.n_tot1 - 1], val) or (sum(bt) >= K) != val[top[K - 1]]: okt = False
report("totalizer: true-count aux satisfies all totalizer clauses (no over-constraint) and o_K <=> count >= K=89", okt and 16 * 9 == 144, "120 random inputs")


def lexmax_ok(d):
    for p in PERMS:
        for j in range(16):
            if d[j] != d[p[j]]:
                if d[j] < d[p[j]]: return False
                break
    return True


def orbit_lexmax(d):
    return max(tuple(d[p[j]] for j in range(16)) for p in PERMS)


okx = 0
for trial in range(60):
    d = orbit_lexmax(tuple(rng.choice([rng.randint(0, 9), rng.choice([7, 8, 9])]) for _ in range(16)))
    val = {}
    for z in range(16):
        for i in range(9): val[b.used[z, i]] = i < d[z]
    prev = {}
    for (p, j, e, ss) in b.lex:
        for v, sv in enumerate(ss): val[sv] = (d[j] > v) and not (d[p[j]] > v)
        val[e] = (True if prev.get(id(p)) is None else val[prev[id(p)]]) and not any(val[sv] for sv in ss)
        prev[id(p)] = e
    okx += evalcl(cls[b.n_tot1:], val)
report("lex-leader block: orbit-lexmax d always extends to a satisfying aux assignment", okx == 60, "%d/60" % okx)
report("sanity: used/f/L/m/nin variable layout is the documented one (used[0,8]=153, used[1,0]=172)", b.used[0, 8] == 153 and b.used[1, 0] == 172)

# ------------------------------------------------------------------ cubes.txt
rows = [l.rstrip("\n").split("\t") for l in (HERE / "cubes.txt").read_text().splitlines() if not l.startswith("#")]
ids = [r[0] for r in rows]
report("cubes.txt: 1001 distinct cubes", len(ids) == 1001 and len(set(ids)) == 1001)
inv = {v: k for k, v in b.used.items()}
Imask = {}
splits = {}
bad = []
for cid, ia, sp in rows:
    ex = gen.cube_extra(b, cid)
    I = 0 if ia == "-" else sum(1 << int(z) for z in ia.split(","))
    norm = {(-b.used[z, 7], b.used[z, 8], -b.nin[z]) for z in range(16)}
    units = {c[0] for c in ex if len(c) == 1}
    others = [c for c in ex if len(c) != 1]
    inv_units = {abs(u): u > 0 for u in units}
    lo = {z: 0 for z in range(16)}; hi = {z: 9 for z in range(16)}
    for v, s in inv_units.items():
        z, i = inv[v]
        if s: lo[z] = max(lo[z], i + 1)
        else: hi[z] = min(hi[z], i)
    if not ({tuple(c) for c in others} == norm and len(others) == 16): bad.append(cid)
    unit8 = {z: (b.used[z, 8] in units) for z in range(16)}
    if any((b.used[z, 8] in units) != bool(I >> z & 1) or (-b.used[z, 8] in units) != (not I >> z & 1) for z in range(16)): bad.append(cid)
    if cid[0] in "if" and cid[1:].isdigit():
        if units != {(b.used[z, 8] if I >> z & 1 else -b.used[z, 8]) for z in range(16)} or I != int(cid[1:]): bad.append(cid)
    else:
        splits[cid] = (I, lo, hi)
        if any(inv[abs(u)][0] > 1 and inv[abs(u)][1] != 8 for u in units): bad.append(cid)
    Imask[cid] = I
report("every cube = base body + 16 normalization clauses + unit clauses only; units on used[z,8] encode I; mask cubes carry nothing else", not bad, "bad=%s" % bad[:5])
c0 = [n for n in splits if n.startswith(("i0_", "j8_"))]
c1 = [n for n in splits if n.startswith("i1_")]
def inbox(cube, a, c2):
    I, lo, hi = splits[cube]
    return lo[0] <= a <= hi[0] and lo[1] <= c2 <= hi[1]
cnt0 = [sum(inbox(n, a, c2) for n in c0) for a in range(9) for c2 in range(9)]
cnt1 = [sum(inbox(n, 9, c2) for n in c1) for c2 in range(9)]
report("splits exhaustive & disjoint: I=empty: every (d_0,d_1) in 0..8^2 in exactly one of 6 cubes; I={0}: every d_1 in 0..8 in exactly one of 4",
       len(c0) == 6 and len(c1) == 4 and set(cnt0) == {1} and set(cnt1) == {1} and all(splits[n][0] == 0 for n in c0) and all(splits[n][0] == 1 for n in c1))

# ------------------------------------------------------------------ partition completeness
def img(I, p): return sum(1 << j for j in range(16) if I >> p[j] & 1)
def key(m): return int("{:016b}".format(m)[::-1], 2)       # position 0 most significant
seen = set(); lexmax = set()
for I in range(1 << 16):
    if I in seen: continue
    orb = {img(I, p) for p in PERMS}
    seen |= orb
    lexmax.add(max(orb, key=key))
reps = lexmax - {0}
mask_ids = {int(c[1:]) for c in ids if c[0] == "i" and c[1:].isdigit()}
fids = {int(c[1:]) for c in ids if c[0] == "f" and c[1:].isdigit()}
report("i<mask> cubes = indicator-orbit-lexmax masks except {0} (mask 1 = I={0} is split into i1_d1*; I=empty into i0_d0*/j8*)",
       mask_ids == reps - {1} and 1 in reps and len(reps) == 401, "%d orbit-lexmax masks incl. empty" % len(lexmax))

PNF = [p for p in PERMS if p != ident]


def feasible(I):
    """exhaustive DFS: is there d in {0..8}^(complement of I) x {9}^I with d >=lex d o p for all 383 non-identity p
    (position 0 most significant)?  Positions in I are known from the start; complement positions are assigned in
    index order, with lookahead (a complement value is in [0,8], so an unknown side is bounded)."""
    d = [9 if I >> u & 1 else -1 for u in range(16)]

    def advance(alive, Kn):
        out = []
        for (p, j) in alive:
            sat = False
            while j < 16:
                q = p[j]
                if q == j: j += 1; continue
                kj = (I >> j & 1) or j < Kn; kq = (I >> q & 1) or q < Kn
                if kj and kq:
                    x, y = d[j], d[q]
                    if x > y: sat = True; break
                    if x < y: return None
                    j += 1; continue
                if kj:
                    if d[j] > 8: sat = True
                elif kq:
                    if d[q] > 8: return None
                break
            if not sat: out.append((p, j))
        return out

    def dfs(k, alive):
        while k < 16 and I >> k & 1: k += 1
        if k == 16: return True
        for v in range(8, -1, -1):
            d[k] = v
            n2 = advance(alive, k + 1)
            if n2 is not None and dfs(k + 1, n2): return True
        d[k] = -1
        return False

    a0 = advance([(p, 0) for p in PNF], 0)
    if a0 is not None and dfs(0, a0): return list(d)
    return None


t1 = time.time()
feas = {}
for I in range(1 << 16):
    w = feasible(I)
    if w is not None: feas[I] = w
print("   exhaustive DFS over 65536 inactive sets: %.0fs" % (time.time() - t1), flush=True)
report("every witness d found by the DFS has inactive set exactly I and satisfies all 384 lex constraints (direct check)",
       all(lexmax_ok(w) and sum(1 << z for z in range(16) if w[z] == 9) == I for I, w in feas.items()), "%d witnesses" % len(feas))
covered = mask_ids | {0, 1} | fids
report("PARTITION COMPLETE: the sets I that admit a lex-constrained d are exactly the 993 covered by the cubes (400 + {0} + {1} + 591)",
       set(feas) == covered and len(covered) == 993 and not (mask_ids & fids) and 0 not in mask_ids | fids, "%d feasible, %d covered" % (len(feas), len(covered)))
report("every orbit-lexmax mask is feasible (the cubes for them are not vacuous)", lexmax <= set(feas))
w1 = (9, 8, 8, 8, 7, 9, 8, 8, 7, 7, 8, 7, 8, 7, 7, 8)
w2 = (9, 9, 8, 6, 6, 8, 9, 4, 4, 2, 9, 0, 5, 6, 8, 8)
okw = True
for w in (w1, w2):
    I = sum(1 << z for z in range(16) if w[z] == 9)
    okw &= lexmax_ok(w) and I not in reps and I not in (0, 1) and I in set(fids)
report("old partition (cubes only for indicator-orbit-lexmax I) is UNSOUND: both witnesses satisfy all 384 lex constraints but I is not in the old cubes; the new f<mask> cubes cover them",
       okw, "witness masks %d and %d" % (sum(1 << z for z in range(16) if w1[z] == 9), sum(1 << z for z in range(16) if w2[z] == 9)))

# ------------------------------------------------------------------ hashes
H_ROWS = {}
for l in (HERE / "hashes.tsv").read_text().splitlines():
    if l.startswith("#"): continue
    p = l.split("\t"); H_ROWS[p[0]] = p
report("hashes.tsv covers exactly the cubes of cubes.txt, all kissat UNSAT / drat-trim VERIFIED",
       set(H_ROWS) == set(ids) and all(r[4] == "UNSAT" and r[5] == "VERIFIED" for r in H_ROWS.values()))
args = sys.argv[1:]
if "--full" in args: sel = ids
else:
    n = int(args[args.index("--sample") + 1]) if "--sample" in args else 100
    sel = [ids[round(i * (len(ids) - 1) / (n - 1))] for i in range(n)]
    sel = list(dict.fromkeys(sel + [c for c in gen.SPLITS]))   # always include the split cubes
tt = time.time(); badh = []
for cid in sel:
    h = hashlib.sha256(gen.cube_text(cid, b).encode()).hexdigest()
    if h != H_ROWS[cid][1]: badh.append(cid)
report("regenerated CNF sha256 == hashes.tsv", not badh, "%d cubes (%s), %.0fs, mismatches %s" % (len(sel), "all" if "--full" in args else "sample", time.time() - tt, badh[:5]))
print("ALL CHECKS PASS" if ok_all else "SOME CHECK FAILED")
print("total %.0fs" % (time.time() - T0))
sys.exit(0 if ok_all else 1)
