"""Gram-class floor checks (stdlib only). Prints OMEGA_FLOOR lines; final marker PASS_OMEGA_FLOOR."""
import os, sys, json, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e8lib as E
from fractions import Fraction as Fr
HERE = os.path.dirname(os.path.abspath(__file__))
n = E.n
fails = []
def ck(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg, flush=True)
    if not cond: fails.append(msg)

# (1) basic structure: rank_F2 N = 9, labels realise N, tight frame
ck(E.rank2(E.NR) == 9, 'rank_F2 N = 9 on the 120 lines (N = even root inner product)')
ck(all(E.form(E.LABEL[i], E.LABEL[j]) == ((E.NR[i] >> j) & 1) for i in range(n) for j in range(n)),
   'labels in F2^9 with the form <(a,v),(b,w)> = ab + v C w reproduce N on all 120 x 120 pairs')
S = [[sum(l[i] * l[j] for l in E.LINES) for j in range(8)] for i in range(8)]
ck(all(S[i][j] == (120 if i == j else 0) for i in range(8) for j in range(8)), 'sum over the 120 lines of l l^T = 120 I (tight frame, norm 8 coordinates): trace constant 120/8 = 15 per unit term')

# (2) census: cost_a(r) = |T(r)| - max over codim-a subspaces W of F2^9 of #{labels of T(r) inside W}, a = 1, 2, all 8 ray types
def popc(x): return bin(x).count('1')
def par(x): return popc(x) & 1
costs = []
for w in E.WEIGHTS:
    T = [i for i in range(n) if E.dot(E.LINES[i], w) != 0]
    masks = {}
    for f in range(1, 512):
        masks[f] = sum(1 << k for k, i in enumerate(T) if par(f & E.LABEL[i]) == 0)
    full = (1 << len(T)) - 1
    c1 = len(T) - max(popc(m) for m in masks.values())
    best2 = 0
    for f in range(1, 512):
        mf = masks[f]
        for g in range(f + 1, 512):
            if g == f: continue
            c = popc(mf & masks[g])
            if c > best2: best2 = c
    c2 = len(T) - best2
    costs.append((len(T), c1, c2))
print('ray types (|T|, cost_1, cost_2):', costs)
ck(len(set(E.WEIGHTS)) == 8, 'eight fundamental-weight rays')
ck(min(c[2] for c in costs) == 25, 'min over the eight ray types of cost_2 is 25 (so a >= 2 needs at least 25 deleted lines)')
ck(min(c[1] for c in costs) == 1 and sorted(c[1] for c in costs)[1] >= 14, 'cost_1: exactly one ray type has cost 1 (the root ray), every other type costs at least 14')
root_ray = [c for c in costs if c[0] == 57]
ck(len(root_ray) == 1 and root_ray[0][1:] == (1, 25), 'root ray (|T| = 57): cost_1 = 1, cost_2 = 25')

# (3) exact designs: biorthogonal root-pair design (P104-type), generic basis (P120), orthoframe (P112)
def supp(u, D): return [p for p in range(n) if p not in D and E.dot(E.LINES[p], u) != 0]
def price(U, W, D):
    rs = [E.rho(supp(u, D), supp(w, D)) for u, w in zip(U, W)]
    return sum(rs), rs
pairs = json.load(open(os.path.join(os.path.dirname(HERE), 'data', 'p104_pairs.json')))
ys, zs = pairs['ys'], pairs['zs']
IP = E.IP
ck(all((IP[ys[k]][zs[l]] == 0) == (k != l) for k in range(8) for l in range(8)) and all(abs(IP[ys[k]][zs[k]]) == 1 for k in range(8)) and len(set(ys + zs)) == 16,
   'data/p104_pairs.json: 16 distinct lines, y_k.z_l = 0 for k != l, y_k.z_k = +-1 (eight A2-adjacent pairs)')
U = [E.LINES[y] for y in ys]
Wd = E.solve_dual(U)
Wd = [E.scale_int(c) for c in Wd]
ck(all(all(Wd[k][i] * E.LINES[zs[k]][j] == Wd[k][j] * E.LINES[zs[k]][i] for i in range(8) for j in range(8)) for k in range(8)), 'dual basis of the y_k is proportional to the z_k')
D16 = set(ys) | set(zs)
c, rs = price(U, Wd, D16)
ck(c == 56 and rs == [7] * 8, 'P104-type design (16 lines deleted, eight terms): c = 56, every rho_k = 7')
c120, rs120 = price(U, Wd, set())
ck(c120 == 72 and rs120 == [9] * 8, 'same eight terms on all 120 lines: c = 72, every rho_k = 9')
random.seed(3)
def rand_basis():
    while True:
        B = [tuple(random.randint(-3, 3) for _ in range(8)) for _ in range(8)]
        try:
            Wb = [E.scale_int(cc) for cc in E.solve_dual(B)]
            return B, Wb
        except StopIteration:
            continue
B, Wb = rand_basis()
ck(price(B, Wb, set())[0] == 72, 'generic dual bases on 120 lines: c = 72')
fr = []
cand = list(range(n)); random.shuffle(cand)
for p in cand:
    if all(IP[p][q] == 0 for q in fr): fr.append(p)
ck(len(fr) == 8, 'eight mutually orthogonal roots exist'); 
cf, rf = price([E.LINES[p] for p in fr], [E.LINES[p] for p in fr], set(fr))
ck(cf == 64, 'orthoframe on the 112 lines (frame deleted): c = 64')

# (4) Theorem O on random Gram-class designs: Cauchy-Binet subset, Sylvester bound, a_k <= 1 when |D| <= 24
def rank_real_rows(vs):
    M = [[Fr(x) for x in v] for v in vs]; r = 0
    for cidx in range(len(M[0]) if M else 0):
        p = next((i for i in range(r, len(M)) if M[i][cidx] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        for i in range(len(M)):
            if i != r and M[i][cidx] != 0:
                f = M[i][cidx] / M[r][cidx]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    return r
def codim(S_):  # a = 9 - dim span of labels
    return 9 - E.rank2([E.LABEL[i] for i in S_])
def rand_vec(kind):
    if kind == 0: return E.LINES[random.randrange(n)]
    if kind == 1: return tuple(random.randint(-2, 2) for _ in range(8))
    if kind == 2:  # sum of two lines
        a, b = E.LINES[random.randrange(n)], E.LINES[random.randrange(n)]
        return tuple(x + y for x, y in zip(a, b))
    return E.WEIGHTS[random.randrange(8)]
random.seed(9)
ntests = 0; minc = 10**9; ok_a = ok_cb = ok_syl = True
for trial in range(300):
    p = random.randint(16, 24)
    if trial % 3 == 0:   # adversarial: start from the 16 pair lines
        D = set(D16)
    else:
        D = set()
    while len(D) < p: D.add(random.randrange(n))
    m = random.randint(8, 11)
    for _ in range(50):
        Us = [rand_vec(random.choice((0, 0, 1, 2, 3))) for _ in range(m)]
        Ws = [rand_vec(random.choice((0, 0, 1, 2, 3))) for _ in range(m)]
        if all(any(v) for v in Us + Ws): break
    # M = sum u_k w_k^T; use only if invertible
    Mx = [[sum(Us[k][i] * Ws[k][j] for k in range(m)) for j in range(8)] for i in range(8)]
    if rank_real_rows(Mx) != 8: continue
    ntests += 1
    Ss = [supp(u, D) for u in Us]; Ts = [supp(w, D) for w in Ws]
    rk = [E.rho(a, b) for a, b in zip(Ss, Ts)]
    ak = [codim(a) for a in Ss]; bk = [codim(b) for b in Ts]
    ok_a &= all(x <= 1 for x in ak + bk)
    ok_syl &= all(rk[k] >= 9 - ak[k] - bk[k] for k in range(m))
    # Cauchy-Binet: a subset K of 8 terms with both U_K and W_K invertible exists
    found = False
    for K in itertools.combinations(range(m), 8):
        if rank_real_rows([Us[k] for k in K]) == 8 and rank_real_rows([Ws[k] for k in K]) == 8:
            found = True; break
    ok_cb &= found
    minc = min(minc, sum(rk))
ck(ntests >= 100, f'{ntests} random Gram-class designs with 16 <= |D| <= 24 and invertible M')
ck(ok_cb, 'Cauchy-Binet: every one of them contains 8 terms with both top and bottom vectors a basis')
ck(ok_a, 'every top and bottom has a <= 1 (codim of the label span of its support), as the census forces for |D| <= 24')
ck(ok_syl, 'Sylvester: rho_k >= 9 - a_k - b_k on every term of every design')
ck(minc >= 56, f'cost of every random design >= 56 (minimum seen {minc})')
print('PASS_OMEGA_FLOOR' if not fails else 'FAILED_OMEGA_FLOOR')
sys.exit(1 if fails else 0)
