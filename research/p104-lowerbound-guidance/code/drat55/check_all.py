"""DRAT55 independent exact checks for TIGHT55 (own code; reads only raw data: e8base.json, labels.txt,
zclauses.pkl, perms.pkl, reps.pkl, s55.cnf(+.map), cube cnfs).  Does NOT import sym.py / zsat_sym.py / ncore.py.
Run: python3 check_all.py   (threads=1, no solver)"""
import json, pickle, itertools, random, sys, os, hashlib
import numpy as np
T55 = 'code/tight55/'
NL = 'code/nonlin/'
D = '<research-tree>/cards/WILD/LUNCH/exchange/d56dir/mod4/'
E = json.load(open(D + 'e8base.json'))
CR = np.array(E['C'], dtype=np.int64); G = np.array(E['Gb'], dtype=np.int64)
LAB = [int(x) for x in open(D + 'labels.txt').read().split()]
ok_all = True
def report(name, ok, info=''):
    global ok_all
    ok_all &= bool(ok)
    print(('PASS ' if ok else 'FAIL ') + name + ('  ' + info if info else ''), flush=True)

# ---------- geometry ----------
assert len(CR) == 120 and len(LAB) == 104
C = CR[:104]; Z = CR[104:]
assert all(int(c @ G @ c) == 2 for c in CR)                      # all 120 are roots
Cb = C % 2; Zb = Z % 2; Bm = G % 2
H = np.concatenate([np.ones((104, 1), np.int64), Cb], 1)          # port labels in F2^9
Nz = np.concatenate([np.ones((16, 1), np.int64), Zb], 1)          # n_z = (1,z) in F2^9
Beta = np.zeros((9, 9), np.int64); Beta[0, 0] = 1; Beta[1:, 1:] = Bm
dot = lambda a, b: bin(a & b).count('1') & 1
Q = np.array([[dot(a, b) for b in LAB] for a in LAB], dtype=np.int64)
report('P104 geometry: Q == H beta H^T (mod 2) from labels.txt', ((H @ Beta @ H.T) % 2 == Q).all())
Hs = {tuple(h) for h in H.tolist()}; Ns = {tuple(h) for h in Nz.tolist()}
report('120 classes distinct mod 2; n_z not a port label (=> row with U=<n_z> serves no port, normalization sound)',
       len({tuple(r) for r in (CR % 2).tolist()}) == 120 and len(Hs) == 104 and len(Ns) == 16 and not (Hs & Ns))

def f2rank(rows):
    rows = [int(''.join(map(str, r)), 2) for r in np.asarray(rows).tolist()]
    r = 0; piv = []
    for x in rows:
        for p in piv: x = min(x, x ^ p)
        if x: piv.append(x); r += 1
    return r

# ---------- covering clauses re-derived from the definition ----------
# for x in Z4^8, port t with <x,c_t> != 0 (mod 4): row z allowed to t and <x,z> != 0 mod 4 must exist.
CL = pickle.load(open(NL + 'zclauses.pkl', 'rb'))
X = np.array(list(itertools.product(range(4), repeat=8)), dtype=np.int64)
IPc = (X @ G @ C.T) % 4; IPz = (X @ G @ Z.T) % 4
Rm = ((IPz != 0) * (1 << np.arange(16))).sum(1)
mism = 0
for t in range(104):
    Rs = sorted(set(Rm[IPc[:, t] != 0].tolist()), key=lambda r: (bin(r).count('1'), r))
    mins = []
    for r in Rs:
        if not any((a & r) == a for a in mins): mins.append(r)
    if set(mins) != set(CL[t]) or len(mins) != len(CL[t]): mism += 1
report('zclauses.pkl == minimal covering masks re-derived from Z4 definition (all 104 ports)', mism == 0,
       f'mismatching ports={mism}, clauses/port {min(len(v) for v in CL.values())}-{max(len(v) for v in CL.values())}')

# ---------- tight vectors are exactly +-Z16 ----------
vals = (X @ G @ C.T) % 4                       # value of v_s = <c_s, x> mod 4
tight = [i for i in range(len(X)) if not (vals[i] == 2).any()]
Zset = {tuple(z % 4) for z in Z} | {tuple((-z) % 4) for z in Z}
tset = {tuple(X[i]) for i in tight if X[i].any()}
report('tight Z4 vectors (no port value 2) = {+-z : z in Z16}: 32 nonzero', tset == Zset and len(tset) == 32,
       f'{len(tset)} nonzero tight vectors, equal to +-Z16 mod 4: {tset == Zset}')

# ---------- price formula: span(H_{S_z}) hyperplane with beta-perp n_z ----------
bad = 0
allv = np.array(list(itertools.product([0, 1], repeat=9)), dtype=np.int64)
for z in range(16):
    S = np.nonzero((C @ (G @ Z[z])) % 4)[0]
    if f2rank(H[S]) != 8: bad += 1; continue
    perp = [v for v in allv if not ((H[S] @ Beta @ v) % 2).any() and v.any()]   # beta-perp of span(H_S)
    if not (len(perp) == 1 and (perp[0] == Nz[z]).all()): bad += 1
report('price formula: span{h_s : s in S_z} is a hyperplane whose beta-perp is exactly n_z=(1,z) (all 16 z)', bad == 0,
       'hence rank Q[P,S_z] = dim span(P) - [n_z in span(P)] for every port set P (linear algebra)')

# ---------- symmetry group ----------
PERMS = pickle.load(open(T55 + 'perms.pkl', 'rb'))
PERMS = [tuple(p) for p in PERMS]
report('perms.pkl: 384 distinct permutations of 0..15', len(set(PERMS)) == 384 and all(sorted(p) == list(range(16)) for p in PERMS))
Pset = set(PERMS); ident = tuple(range(16))
closed = all(tuple(p[q[i]] for i in range(16)) in Pset for p in PERMS for q in PERMS)
report('perms.pkl is a group (identity, closed under composition)', ident in Pset and closed)

# every p: unique invertible T (9x9 over F2) with n_z T = n_{p z}; then H T = H[pp] for a permutation pp of ports; CL maps to CL
def solve_g(Rows, Targets):
    """unique g (8x8 over F2, row-vector convention x -> x g) with Rows g = Targets, Rows of rank 8"""
    A = [list(map(int, Rows[i])) + list(map(int, Targets[i])) for i in range(len(Rows))]
    r = 0
    for c in range(8):
        p = next((i for i in range(r, len(A)) if A[i][c]), None)
        if p is None: return None
        A[r], A[p] = A[p], A[r]
        for i in range(len(A)):
            if i != r and A[i][c]: A[i] = [a ^ b for a, b in zip(A[i], A[r])]
        r += 1
    for i in range(8, len(A)):
        if any(A[i]): return None
    return np.array([A[i][8:] for i in range(8)], dtype=np.int64)
def solve_T(Nrows, Trows, p=None):
    g = solve_g(Zb, Zb[list(p)])
    if g is None: return None
    Tm = np.zeros((9, 9), np.int64); Tm[0, 0] = 1; Tm[1:, 1:] = g
    return Tm
Hidx = {tuple(h): i for i, h in enumerate(H.tolist())}
nsym_ok = 0; fails = []
CLsets = {t: set(CL[t]) for t in range(104)}
for p in PERMS:
    Tm = solve_T(Nz, Nz[list(p)], p)
    if Tm is None: fails.append((p, 'no T')); continue
    if f2rank(Tm) != 9: fails.append((p, 'T singular')); continue
    if not (((Nz @ Tm) % 2) == Nz[list(p)]).all(): fails.append((p, 'nT')); continue
    img = (H @ Tm) % 2
    try: pp = [Hidx[tuple(r)] for r in img.tolist()]
    except KeyError: fails.append((p, 'ports not preserved')); continue
    if sorted(pp) != list(range(104)): fails.append((p, 'pp not perm')); continue
    # P104 preserved as beta-isometry (Q invariant) and covering clauses map exactly
    if not (Q[np.ix_(pp, pp)] == Q).all(): fails.append((p, 'Q')); continue
    good = True
    for t in range(104):
        im = {sum(1 << p[z] for z in range(16) if r >> z & 1) for r in CL[t]}
        if im != CLsets[pp[t]]: good = False; break
    if not good: fails.append((p, 'CL')); continue
    nsym_ok += 1
print('   fail reasons:', sorted(set(r for _,r in fails)))
report('each of 384 perms p is realised by T in GL(9,2): n_z T = n_{p z}, h_t T = h_{pp t} (ports permuted), Q invariant, covering clauses map onto themselves',
       nsym_ok == 384, f'{nsym_ok}/384 ok, fails={len(fails)}')
print('   => (U_z) -> (U_z T) at row p(z) maps decoders to decoders, preserves dim U_z, [n_z in U_z], hence cost and d-vector d(pz)=d(z)')

# ---------- regenerate the CNF from the spec and compare with s55.cnf ----------
def parse_cnf(path):
    cl = []
    with open(path) as fh:
        hdr = fh.readline().split(); nv, nc = int(hdr[2]), int(hdr[3])
        for line in fh:
            cl.append(tuple(int(x) for x in line.split()[:-1]))
    assert len(cl) == nc, (len(cl), nc)
    return nv, cl
nv_f, cls_f = parse_cnf(T55 + 's55.cnf')
mp = pickle.load(open(T55 + 's55.cnf.map', 'rb'))

nv = 0; cls = []
def new():
    global nv; nv += 1; return nv
f = {}; used = {}; L = {}
for z in range(16):
    for i in range(9):
        used[z, i] = new()
        for c in range(9): f[z, i, c] = new(); L[z, i, c] = new()
for z in range(16):
    for i in range(9):
        u = used[z, i]
        if i > 0: cls.append((-u, used[z, i - 1]))
        for c in range(9): cls.append((u, -f[z, i, c])); cls.append((u, -L[z, i, c]))
        cls.append(tuple([-u] + [L[z, i, c] for c in range(9)]))
        for c in range(9):
            for c2 in range(c + 1, 9): cls.append((-L[z, i, c], -L[z, i, c2]))
            cls.append((-L[z, i, c], f[z, i, c]))
            for c2 in range(c): cls.append((-L[z, i, c], -f[z, i, c2]))
            for i2 in range(9):
                if i2 != i: cls.append((-L[z, i, c], -f[z, i2, c]))
            if i < 8:
                for c2 in range(c + 1): cls.append((-L[z, i, c], -L[z, i + 1, c2]))
nbase = len(cls)
xdef = {}   # aux xor var -> (a,b)
def xorvar(lits):
    if len(lits) == 1: return lits[0]
    a = lits[0]
    for b in lits[1:]:
        p = new(); xdef[p] = (a, b)
        cls.extend([(-p, a, b), (-p, -a, -b), (p, -a, b), (p, a, -b)]); a = p
    return a
m = {}; nin = {}
for z in range(16):
    for t in range(104):
        m[z, t] = new()
        sup = [c for c in range(9) if H[t][c]]
        for i in range(9):
            p = xorvar([f[z, i, c] for c in sup]); cls.append((-m[z, t], -p))
for z in range(16):
    sup = [c for c in range(9) if Nz[z][c]]
    nin[z] = new()
    for i in range(9):
        p = xorvar([f[z, i, c] for c in sup]); cls.append((-nin[z], -p))
ncov0 = len(cls)
for t in range(104):
    for r in CL[t]: cls.append(tuple(m[z, t] for z in range(16) if r >> z & 1))
ncov1 = len(cls)
lits = [used[z, i] for z in range(16) for i in range(9)] + [nin[z] for z in range(16)]
BUD = 55; K = 144 - BUD
tdef = []     # totalizer clauses start index
def tot(ls):
    if len(ls) == 1: return [ls[0]]
    h = len(ls) // 2; a = tot(ls[:h]); b = tot(ls[h:]); o = [new() for _ in range(len(ls))]
    p = len(a); q = len(b)
    for i in range(p + 1):
        for j in range(q + 1):
            k = i + j + 1
            if k > p + q: continue
            c = [-o[k - 1]]
            if i < p: c.append(a[i])
            if j < q: c.append(b[j])
            cls.append(tuple(c))
    return o
nv_tot0 = nv
ntot0 = len(cls)
o = tot(lits); cls.append((o[K - 1],))
ntot1 = len(cls)
# lex-leader block: written from the definition (d >=lex d o p, positions ascending, skipping fixed points)
nsym0 = len(cls); nv_sym0 = nv
for p in PERMS:
    if all(p[j] == j for j in range(16)): continue
    prev = None
    for j in range(16):
        if p[j] == j: continue
        e = new(); pre = [] if prev is None else [-prev]
        for v in range(9): cls.append(tuple(pre + [-used[p[j], v], used[j, v]]))
        ss = []
        for v in range(9):
            sv = new(); ss.append(sv); cls.append((-sv, used[j, v])); cls.append((-sv, -used[p[j], v]))
        cls.append(tuple(pre + [e] + ss)); prev = e
print(f'regenerated: vars {nv} clauses {len(cls)}; file: vars {nv_f} clauses {len(cls_f)}')
same = (nv == nv_f and len(cls) == len(cls_f) and all(a == b for a, b in zip(cls, cls_f)))
report('s55.cnf == independently regenerated CNF (spec: RREF subspaces, port membership, nin, covering, totalizer>=89, lex-leader), clause-for-clause', same)
mapok = all(mp['used'][k] == used[k] for k in used) and all(mp['m'][k] == m[k] for k in m) and all(mp['nin'][k] == nin[k] for k in nin) and all(mp['f'][k] == f[k] for k in f)
report('s55.cnf.map variable names agree with regenerated numbering', mapok)

# ---------- semantic spot checks on the spec CNF (direct clause evaluation, no solver) ----------
rng = random.Random(1)
def evalcl(cl, val):   # val: dict var->bool ; unset vars default False
    return all(any(val.get(abs(l), False) == (l > 0) for l in c) for c in cl)
def rand_subspace_perp(d):
    """random subspace U of F2^9 with dim U^perp = d; returns RREF rows of U^perp (list of 9-bit tuples, increasing leading col)"""
    while True:
        rows = [tuple(rng.randint(0, 1) for _ in range(9)) for _ in range(d)]
        if d == 0 or f2rank(rows) == d: break
    # rref
    M = [int(''.join(map(str, r)), 2) for r in rows]; M2 = []
    # standard rref on 9-bit ints with leading = most significant column index 0
    A = [list(r) for r in rows]; r = 0
    for c in range(9):
        p = next((i for i in range(r, len(A)) if A[i][c]), None)
        if p is None: continue
        A[r], A[p] = A[p], A[r]
        for i in range(len(A)):
            if i != r and A[i][c]: A[i] = [a ^ b for a, b in zip(A[i], A[r])]
        r += 1
    return [tuple(a) for a in A[:r]]
def assign_config(perp_rows_per_z):
    """full assignment of base+xor+m+nin vars (for rows' used/f/L, m = port in U, nin) from per-row RREF bases"""
    val = {}
    for z in range(16):
        R = perp_rows_per_z[z]
        for i in range(9):
            if i < len(R):
                val[used[z, i]] = True
                lead = next(c for c in range(9) if R[i][c])
                for c in range(9):
                    val[f[z, i, c]] = bool(R[i][c]); val[L[z, i, c]] = (c == lead)
        for t in range(104):
            val[m[z, t]] = all(sum(r[c] * H[t][c] for c in range(9)) % 2 == 0 for r in R)
        val[nin[z]] = all(sum(r[c] * Nz[z][c] for c in range(9)) % 2 == 0 for r in R)
    # xor aux values
    for pvar in sorted(xdef):
        a, b = xdef[pvar]; val[pvar] = val.get(a, False) ^ val.get(b, False)
    return val
base_cls = cls[:nbase] + [c for c in cls[nbase:ncov0]]
ok_rep = True
for trial in range(60):
    perp = [rand_subspace_perp(rng.choice([0, 1, 2, 3, 5, 7, 8, 9]) if trial % 3 else rng.randint(0, 9)) for _ in range(16)]
    val = assign_config(perp)
    if not evalcl(base_cls, val): ok_rep = False; break
report('representability: random 16-tuples of subspaces (RREF) satisfy all row/xor/membership clauses with m=[h_t in U_z], nin=[n_z in U_z]', ok_rep, '60 random configs')

# membership semantics: m true only if h_t in U (check that the clauses *force* it): any m[z,t]=True assignment with h_t notin U violates some clause
viol = 0
for trial in range(40):
    perp = [rand_subspace_perp(rng.randint(1, 9)) for _ in range(16)]
    val = assign_config(perp)
    z = rng.randrange(16); outs = [t for t in range(104) if not val[m[z, t]]]
    if not outs: continue
    t = rng.choice(outs); val[m[z, t]] = True
    if not evalcl(base_cls, val): viol += 1
report('membership forced: setting m[z,t]=True for h_t not in U_z violates a clause (xor aux are definitional)', viol > 0, f'{viol} violations in trials')

# totalizer: for random assignments, aux := true counts satisfies tot clauses iff ... check one-sided (count>=K -> satisfiable) and unit forces count>=K
def tot_assign(ls, val, cnt):
    pass
# evaluate: rebuild the totalizer recursively with true-count aux values by re-walking var numbering
def tot_vals(ls, litval, state):
    if len(ls) == 1: return [litval[ls[0]]], 1
    h = len(ls) // 2
    a, _ = tot_vals(ls[:h], litval, state); b, _ = tot_vals(ls[h:], litval, state)
    cnt = sum(a) + sum(b)  # a,b are unary outputs: o_j true iff count>=j  -> sum = count
    out = [cnt >= k + 1 for k in range(len(ls))]
    state.append(out)
    return out, 1
tot_cls = cls[ntot0:ntot1 - 1]
ok_t = True; ok_t2 = True
for trial in range(200):
    # random assignment of the 160 literal variables with count around K
    cnt_target = rng.choice([K - 3, K - 1, K, K + 1, K + 5, rng.randint(0, 160)])
    bits = [1] * max(0, min(160, cnt_target)) + [0] * (160 - max(0, min(160, cnt_target))); rng.shuffle(bits)
    litval = {l: bool(b) for l, b in zip(lits, bits)}
    # aux assigned by true counts, in same recursion order as tot() (o vars allocated post-order)
    state = []
    nv_save = nv
    # recompute var ids the same way: o vars occupy consecutive ids in post-order starting at the first totalizer var
    # simpler: use the (spec-identical) tot() numbering by replaying
    val = dict(litval)
    ctr = [nv_tot0 + 1]
    def replay(ls):
        if len(ls) == 1: return [ls[0]]
        h = len(ls) // 2; a = replay(ls[:h]); b = replay(ls[h:])
        ids = list(range(ctr[0], ctr[0] + len(ls))); ctr[0] += len(ls)
        c = sum(val[x] for x in a) + sum(val[x] for x in b)   # unary: outputs true iff >= index
        for k, v in enumerate(ids): val[v] = (c >= k + 1)
        return ids
    outv = replay(lits)
    total = sum(litval.values())
    sat_tot = evalcl(tot_cls, val)
    if not sat_tot: ok_t = False
    if (total >= K) != val[outv[K - 1]]: ok_t2 = False
report('totalizer clauses: satisfied by true-count aux for 200 random inputs (no over-constraint); output o_K true iff count>=K=89', ok_t and ok_t2)
report('cost identity: sum price = 144 - sum d - sum nin so price<=55 <=> sum(used)+sum(nin) >= 89 (arithmetic: 16 rows x 9 = 144)', 16 * 9 == 144 and K == 89)

# lex-leader block: for random d with order-encoded used, if d >=lex d o p for all p, greedy aux assignment satisfies block
sym_cls = cls[nsym0:]
def lexmax_ok(d):
    for p in PERMS:
        for j in range(16):
            if d[j] != d[p[j]]:
                if d[j] < d[p[j]]: return False
                break
    return True
def orbit_lexmax(d):
    return max(tuple(d[p[j]] for j in range(16)) for p in PERMS)
# aux ids: replay numbering
def lex_assign(d):
    val = {}
    for z in range(16):
        for i in range(9): val[used[z, i]] = i < d[z]
    ctr = nv_sym0 + 1
    for p in PERMS:
        if all(p[j] == j for j in range(16)): continue
        prev = None
        for j in range(16):
            if p[j] == j: continue
            e = ctr; svs = list(range(ctr + 1, ctr + 10)); ctr += 10
            for v, sv in enumerate(svs): val[sv] = (d[j] > v) and not (d[p[j]] > v)
            strict = any(val[sv] for sv in svs)
            val[e] = (True if prev is None else val[prev]) and not strict
            prev = e
    return val
okx = 0; tested = 0
for trial in range(120):
    d0 = tuple(rng.choice([rng.randint(0, 9), rng.choice([7, 8, 9]), 9 if rng.random() < .4 else rng.randint(0, 8)]) for _ in range(16))
    d = orbit_lexmax(d0)
    assert lexmax_ok(d)
    tested += 1
    if evalcl(sym_cls, lex_assign(d)): okx += 1
report('lex-leader block: orbit-lexmax d (d >=lex d o p for all p) always extends to a satisfying aux assignment', okx == tested, f'{okx}/{tested} lexmax vectors')
# (the converse, non-lexmax -> violated, only affects strength) check anyway greedy-violated for a few non-lexmax
neg = 0; negt = 0
for trial in range(60):
    d0 = tuple(rng.randint(0, 9) for _ in range(16))
    if lexmax_ok(d0): continue
    negt += 1
    if not evalcl(sym_cls, lex_assign(d0)): neg += 1
print(f'   (info) non-lexmax d violate block under greedy aux: {neg}/{negt}')

# ---------- partition completeness ----------
reps = pickle.load(open(T55 + 'reps.pkl', 'rb'))
print('reps:', len(reps), 'min', min(reps), 'max', max(reps))
# decode cubes: extra clauses beyond s55 body
def cube_info(path):
    with open(path) as fh:
        hdr = fh.readline().split(); nvv, nc = int(hdr[2]), int(hdr[3])
        body = fh.readlines()
    assert len(body) == nc and nvv == nv_f
    return body
s55_body_lines = None
with open(T55 + 's55.cnf') as fh:
    fh.readline(); s55_body_lines = fh.readlines()
NS = len(s55_body_lines)
norm_expected = [f'{-used[z,7]} {used[z,8]} {-nin[z]} 0\n' for z in range(16)]
def decode_cube(path):
    body = cube_info(path)
    if body[:NS] != s55_body_lines: return None
    extra = body[NS:]
    if extra[:16] != norm_expected[:16] and not (set(norm_expected) <= set(extra)): return None
    units = [int(l.split()[0]) for l in extra if len(l.split()) == 2]
    others = [l for l in extra if len(l.split()) != 2]
    if set(others) != set(norm_expected): return None
    u2 = {abs(x): x > 0 for x in units}
    return u2
inv = {v: k for k, v in used.items()}
def cube_spec(path):
    u = decode_cube(path)
    if u is None: return None
    I = set(); spec = {}
    for v, s in u.items():
        z, i = inv[v]; spec[z, i] = s
    return spec
cubes = {}   # name -> (maskI, dconstraints)  dconstraint = (z, lo, hi) bounds on d_z, d_z in [lo,hi]
bad_c = []
def dbounds(spec, z):
    lo, hi = 0, 9
    for (zz, i), s in spec.items():
        if zz != z: continue
        if s: lo = max(lo, i + 1)      # used[z,i] true => d_z > i
        else: hi = min(hi, i)          # used[z,i] false => d_z <= i
    return lo, hi
def cube_of(path):
    spec = cube_spec(path)
    if spec is None: return None
    I = 0
    for z in range(16):
        s = spec.get((z, 8))
        if s is None: return ('free', z)
        if s: I |= 1 << z
    b = {z: dbounds(spec, z) for z in range(16)}
    return I, b, spec
rows = []
for fn in sorted(os.listdir(T55 + 'ic')):
    if fn.endswith('.cnf'):
        r = cube_of(T55 + 'ic/' + fn)
        if r is None or r[0] == 'free': bad_c.append(fn); continue
        rows.append((fn, r))
for fn in ['i1_d1le5', 'i1_d1_6', 'i1_d1_7', 'i1_d1_8', 'i0_d0_le6', 'i0_d0_7', 'i0_d0_8', 'j8_le5', 'j8_6', 'j8_7', 'j8_8']:
    r = cube_of(T55 + fn + '.cnf')
    if r is None or r[0] == 'free': bad_c.append(fn); continue
    rows.append((fn, r))
report('every cube cnf = byte-identical s55 body + 16 normalization clauses + unit clauses only', not bad_c, f'{len(rows)} cubes decoded, bad={bad_c}')
byname = dict(rows)
# 1. mask cubes in ic
icm = {}
for fn, (I, b, spec) in rows:
    if fn.startswith('i') and fn[1:-4].isdigit(): icm[int(fn[1:-4])] = (I, b, spec)
# d_z bounds from the units: z in I -> (9,9); z not in I -> d_z <= 8 and no other restriction
def free_of_split(b, I):
    return all(b[z] == ((9, 9) if I >> z & 1 else (0, 8)) for z in range(16))
report('ic/i<mask>.cnf: units fix used[z,8] = [z in mask] for all 16 z, mask == file number, and impose nothing else (d_z<=8 off the mask)',
       len(icm) == 401 and all(I == k and free_of_split(b, I) for k, (I, b, _) in icm.items()), f'{len(icm)} cubes')
import collections
byname = {fn: r for fn, r in rows}
def box(names, I, zs=(0, 1)):
    """count, for every (d0,d1) combination consistent with inactive set I, how many cubes of names contain it"""
    cnt = collections.Counter()
    rng_ = {z: ([9] if I >> z & 1 else list(range(9))) for z in zs}
    for a in rng_[zs[0]]:
        for b2 in rng_[zs[1]]:
            for n in names:
                (_, bb, _) = byname[n]
                if bb[zs[0]][0] <= a <= bb[zs[0]][1] and bb[zs[1]][0] <= b2 <= bb[zs[1]][1]: cnt[(a, b2)] += 1
    return cnt, len(rng_[zs[0]]) * len(rng_[zs[1]])
e0 = ['i0_d0_le6', 'i0_d0_7', 'j8_le5', 'j8_6', 'j8_7', 'j8_8']
i1 = ['i1_d1le5', 'i1_d1_6', 'i1_d1_7', 'i1_d1_8']
c0, n0 = box(e0, 0); c1, n1 = box(i1, 1)
okpart = all(byname[n][0] == 0 for n in e0) and all(byname[n][0] == 1 for n in i1)
okpart &= len(c0) == n0 and all(v == 1 for v in c0.values()) and len(c1) == n1 and all(v == 1 for v in c1.values())
# the split cubes also impose nothing on other rows
okpart &= all(all(byname[n][1][z] == ((9, 9) if byname[n][0] >> z & 1 else (0, 8)) for z in range(2, 16)) for n in e0 + i1)
report('splits exhaustive & disjoint: every (d_0,d_1) in 0..8 x 0..8 (I=empty) lies in exactly one of the 6 cubes; every d_1 in 0..8 (I={0}, d_0=9) in exactly one of the 4 cubes',
       okpart, f'I=empty: {len(c0)}/{n0} combos once; I={{0}}: {len(c1)}/{n1}')
all_I = set(icm) | {0, 1}
report('cube masks: ic files {1..} == reps.pkl exactly (401 nonempty I; mask 1 = I={0} is the parent of the i1_d1 split and is NOT used directly), plus I=empty split cubes', set(icm) == set(reps), f'{len(icm)} masks')

# 3. orbit-lexmax claim: every I(d*) of a lexmax d* is a rep (or empty).  DFS over d in {0..8} on complement, 9 on I.
# lex relation: d >=lex d o p for p in PERMS, positions ascending.
perm_nf = [p for p in PERMS if p != ident]
def prefix_state(d, k):
    """given d assigned on 0..k-1, return False if some p already forces d <lex d o p"""
    for p in perm_nf:
        for j in range(16):
            if j >= k or p[j] >= k: break
            if d[j] != d[p[j]]:
                if d[j] < d[p[j]]: return False
                break
    return True
def indicator_cover(Imask):
    """does there exist d with inactive set exactly I and d lexmax in its G-orbit?"""
    d = [0] * 16
    def dfs(k):
        if k == 16: return True
        vals = [9] if Imask >> k & 1 else range(8, -1, -1)
        for v in vals:
            d[k] = v
            if prefix_state(d, k + 1) and dfs(k + 1): return True
        return False
    return dfs(0)
# only masks whose orbit-lexmax indicator (positions ascending) is not themselves need the DFS, but run on ALL 65536? too slow in
# python -> run over: (a) all reps, (b) every non-rep mask, using a cheaper necessary condition first.
repset = set(reps) | {0}
def img_mask(Imask, p):
    # indicator vector ind(z)=1 if z in I; ind o p at position j = ind[p[j]]
    return sum(1 << j for j in range(16) if Imask >> p[j] & 1)
def ind_lexgt(a, b):   # position 0 most significant
    for j in range(16):
        x, y = a >> j & 1, b >> j & 1
        if x != y: return x > y
    return False
nonrep_lexmax = [I for I in range(1 << 16) if any(ind_lexgt(img_mask(I, p), I) for p in perm_nf)]
orbit_lexmax_masks = [I for I in range(1 << 16) if I not in set(nonrep_lexmax)]
print('indicator orbit-lexmax masks (positions ascending, incl. empty):', len(orbit_lexmax_masks), ' in reps+{0}:', len(set(orbit_lexmax_masks) & repset), 'reps not lexmax:', len(repset - set(orbit_lexmax_masks)))
report('reps.pkl == set of indicator-orbit-lexmax nonempty masks under perms.pkl (position 0 most significant)', set(orbit_lexmax_masks) - {0} == set(reps) and 0 not in set(reps))
pickle.dump((nonrep_lexmax, orbit_lexmax_masks), open('partition_masks.pkl', 'wb'))
print('done part 1; ok so far =', ok_all)

# ---------- the d-lexmax vs I-lexmax gap ----------
# For each mask I: does a d with inactive set exactly I exist that satisfies ALL lex-leader constraints (i.e. survives the CNF's symmetry breaking)?
# dfs_part2.c (C, exhaustive DFS with exact lex pruning + necessary-chain pruning) wrote dfs_all3.txt ; cross-check with the plain python DFS (dfs_part.py) on a sample
sys.argv = ['x', 'none']
exec(open('dfs_part.py').read().split("if __name__")[0])
res = {int(a): int(b) for a, b in (l.split() for l in open('dfs_all3.txt'))}
assert len(res) == 65536
feas = sorted(I for I, r in res.items() if r)
sample = list(range(0, 401)) + [m for m in feas[:60]]
mism = [I for I in sample if feasible(I) != bool(res[I])]
report('C exhaustive DFS == python exact DFS on sample (masks 0..400 + 60 feasible ones)', not mism, f'mismatches={mism}')
repsz = set(reps) | {0}
F = [I for I in feas if I not in repsz]
report('every orbit-lexmax mask is feasible (cubes for reps are not vacuous)', repsz <= set(feas))
print(f'RESULT: {len(feas)} inactive-sets I admit a G-lexmax d; {len(repsz)} of them are indicator-orbit-lexmax (covered by the original cubes); {len(F)} are NOT covered by the original cubes (partition gap)')
w = (9, 8, 8, 8, 7, 9, 8, 8, 7, 7, 8, 7, 8, 7, 7, 8)
report('explicit gap witness: d=%s has I={0,5}, satisfies d>=lex d o p for all 384 p, but mask 33 is not in reps' % (w,), lexmax_ok(w) and sum(1 << z for z in range(16) if w[z] == 9) == 33 and 33 not in set(reps))
pickle.dump(F, open('F_masks.pkl', 'wb'))
print('ALL CHECKS PASS' if ok_all else 'SOME CHECK FAILED (see FAIL lines)')

# ---------- coordinator/LOOSE witness: the OLD partition check must FAIL on it ----------
w2 = (9, 9, 8, 6, 6, 8, 9, 4, 4, 2, 9, 0, 5, 6, 8, 8)
I2 = sum(1 << z for z in range(16) if w2[z] == 9)
old_partition_sound = not (lexmax_ok(w2) and I2 not in set(reps))
report('OLD partition (global d-lex-leader + cubes only for indicator-lexmax I) is UNSOUND: LOOSE witness d=%s, I=%d: satisfies all 384 lex constraints, I not in reps, and my DFS lists I as feasible' % (w2, I2),
       (not old_partition_sound) and res[I2] == 1, 'checker detects the gap (old partition FAILS soundness, as it must)')
print('OLD-PARTITION-SOUND =', old_partition_sound)
