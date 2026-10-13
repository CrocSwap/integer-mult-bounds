"""Numerical check of the Gohberg--Semencul (GS) path for the recentred sub-block inverse.

Each block applies M_c^{-1} = D_c T_c^{-1} D_c^{-1}, T_c = G_c T_lambda G_c^{-1}, with T_c^{-1} in
GS form  x0^{-1} (L(x_c) U(yt_c) - L(Zy_c) U(Zxt_c))  and four triangular Toeplitz products done in
fixed point at P decimal digits (exact products, then rounding, as packed integer multiplication does).
Here x = T^{-1} e_0, y = T^{-1} e_{n-1}, yt = reversed y, Z = down shift.

Modes (how the four vectors of T_c are produced):
  0  two-frame fixed point (proposed): store x_+ = T_{+1/2}^{-1} e_0 and y = T_lambda^{-1} e_{n-1},
     both bounded, in fixed point at P digits; every per-block rescale factor is <= 1.  Expect PASS.
  1  claimed path, balanced: GS vectors of T_lambda at high precision, stored floating point
     (P significant digits), rescaled per block with the rho_c^{+-n} balance between the two
     factors of the second product, then converted to fixed point.  Expect PASS.
  2  claimed path, unbalanced: as 1 but each factor is conjugated by G_c on its own, so the second
     pair carries rho_c^{-n} and rho_c^{+n}: one factor needs ~9.06 alpha^2 n extra integer
     bits and the other underflows, dropping the second product.
  3  negative control: GS vectors of T_lambda stored in fixed point at P digits.  Expect FAIL.
  4  negative control: mode 0 at P = Q + 2 log2(lambda) + 8 bits, i.e. without the chirp reserve
     R_D.  Expect FAIL.
Mode 2 is reported only; mode 3 is asserted to fail only where its predicted loss exceeds 2^-Q.
Args: s t alpha^2 Q_bits [P_digits]  (P defaults to the bound Q + R_D + 2 log2(lambda) + 8 bits).
Exit status is nonzero if any mode disagrees with its expectation.
"""
from decimal import Decimal as Dm, getcontext, Context, localcontext
from fractions import Fraction as F
import math, sys, random

argv = [int(a) for a in sys.argv[1:]] or [241, 256, 17, 150]
s, t, a2, Qbits = argv[:4]
getcontext().prec = 160
BIG = Context(prec=3000)          # fixed-point work context: wide enough that no integer part overflows
PI = Dm('3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148086513282306647093844609550582231725359408128481117450284102701938521105559644622948954930381964428810975665933446128475648233786783165271201909145648566923460348610454326648213393607260249141273724587006606315588174881520920962829254091715364367892590360011330530548820466521384146951941511609433057270365759591953092186117381932611793105118548074462379962749567351885752724891227938183011949129833673362440656643086021394946395224737190702179860943702770539217176293176752384674818467669405132000568127145263560827785771342757789609173637178721468440901224953430146549585371050792279689258923542019956112129021960864034418159813629774771309960518707211349999998372978049951059731732816096318595024459455346908302642522308253344685035261931188171010003137838752886587533208381420617177669147303598253490428755468731159562863882353787593751957781857780532171226806613001927876611195909216420198938095257201065485863278')
sig = F(t, s); th = sig - 1
q = lambda j: math.floor(F(t*j, s) + F(1, 2)); beta = lambda j: F(t*j, s) - q(j)
dec = lambda f: Dm(f.numerator) / Dm(f.denominator)
E = lambda x: (-PI*a2*dec(x)).exp()

def solve(A, bv, pivot=True):
    n = len(A); M = [row[:] + [bv[i]] for i, row in enumerate(A)]
    for c in range(n):
        if pivot:
            p = max(range(c, n), key=lambda r: abs(M[r][c])); M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                for k in range(c, n+1): M[r][k] -= f*M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]

# --- the operator N, its wraps and its blocks (same construction as check_reuse_inverse.py) ---
N = [[Dm(0)]*s for _ in range(s)]
for l in range(s):
    for j in range(l - 2*s, l + 2*s):
        X = (sig*j - q(l))**2 - beta(j)**2
        if X < 60:
            N[l][j % s] += E(X)
wraps = [j for j in range(s) if q(j+1) - q(j) == 2]
w = 1 + math.isqrt(int(Qbits / (4.53 * a2)) + 1)
blocks = []
for i, w0 in enumerate(wraps):
    st = w0 + 1; en = wraps[(i+1) % len(wraps)] + (s if i+1 == len(wraps) else 0)
    seg = list(range(st, en + 1))
    nb = max(1, len(seg) // (2*w))
    cuts = [round(k * len(seg) / nb) for k in range(nb + 1)]
    blocks += [seg[cuts[k]:cuts[k+1]] for k in range(nb)]
lengths = sorted({len(g) for g in blocks})
assert min(lengths) >= 2*w, (lengths, w)
lam = max(lengths)
RD = 4.5324 * a2 * float(th) * (lam - 1)**2           # chirp D_c span in bits inside one block
Pdig = argv[4] if len(argv) > 4 else math.ceil((Qbits + RD + 2*math.log2(lam) + 8) / math.log2(10))
PREC = {'d': Pdig}                                      # current working precision, switched per mode
fix = lambda v: BIG.quantize(v, Dm(10) ** -PREC['d'])   # fixed point: absolute precision 10^-P
flt = lambda v: Context(prec=PREC['d']).plus(v)         # floating point: P significant digits

def toeplitz(L, b):     # T_c for beta = b: symbol exp(-pi a2 (sigma h^2 + 2 b h))
    return [[E(sig*(c-a)**2 + 2*b*(c-a)) for c in range(L)] for a in range(L)]

def gs_vectors(A):
    n = len(A)
    x = solve(A, [Dm(int(i == 0)) for i in range(n)])
    y = solve(A, [Dm(int(i == n-1)) for i in range(n)])
    return x, y

# --- setup, once per block length ---
base = {}
for L in lengths:
    with localcontext() as ctx:                          # absolute precision P + 9.06 a2 L bits
        ctx.prec = Pdig + int(9.06 * a2 * L / 3.32) + 30
        x, y = gs_vectors(toeplitz(L, F(-1, 2)))
        T = toeplitz(L, F(-1, 2))
        # GS reconstruction check against a dense inverse at this precision
        yt = y[::-1]; Zy = [Dm(0)] + y[:-1]; Zxt = [Dm(0)] + x[::-1][:-1]
        Ti = [solve(T, [Dm(int(i == j)) for i in range(L)]) for j in range(L)]
        rec = max(abs(sum(x[a-k]*yt[b-k] - Zy[a-k]*Zxt[b-k] for k in range(min(a, b)+1)) / x[0]
                      - Ti[b][a]) for a in range(L) for b in range(L))
        assert rec < Dm(10) ** -(Pdig + 5), rec
    with localcontext() as ctx:                          # proposed: only P (+ guard) digits
        ctx.prec = Pdig + 20
        xp, _ = gs_vectors(toeplitz(L, F(1, 2)))         # frame beta = +1/2: x_+ = rho_+^{-i} x_i
        _, ym = gs_vectors(toeplitz(L, F(-1, 2)))        # frame beta = -1/2: T_lambda itself
    base[L] = dict(x=x, y=y, xp=[fix(v) for v in xp], ym=[fix(v) for v in ym],
                   xf=[flt(v) for v in x], yf=[flt(v) for v in y],
                   xq=[fix(v) for v in x], yq=[fix(v) for v in y])

def powers(r, n, store):         # r^0..r^{n-1} by repeated multiplication, stored as given
    out = [Dm(1)]
    for _ in range(n - 1): out.append(store(BIG.multiply(out[-1], r)))
    return out

def block_vectors(L, bc, mode):
    """Return the four GS vectors of T_c (x_c, yt_c, Zy_c, Zxt_c) in fixed point."""
    B = base[L]; n = L
    rho = (-PI*a2*dec(2*bc + 1)).exp()                   # <= 1
    if mode in (0, 4):
        rr = fix((-PI*a2*dec(1 - 2*bc)).exp())           # rho_+/rho_c <= 1
        pr, pc = powers(rr, n + 1, fix), powers(fix(rho), n + 1, fix)
        X, Y = [fix(v) for v in B['xp']], [fix(v) for v in B['ym']]
        xc = [fix(pr[i]*X[i]) for i in range(n)]
        ytc = [fix(pc[k]*Y[n-1-k]) for k in range(n)]
        Zyc = [Dm(0)] + [fix(pc[n-k]*Y[k-1]) for k in range(1, n)]
        Zxtc = [Dm(0)] + [fix(pr[n-k]*X[n-k]) for k in range(1, n)]
        return xc, ytc, Zyc, Zxtc
    X, Y = (B['xq'], B['yq']) if mode == 3 else (B['xf'], B['yf'])
    st = fix if mode == 3 else flt
    up = powers(flt(rho), n + 1, flt); dn = powers(flt(1/rho), n + 1, flt)   # rho^{+-i}, floating
    xc = [fix(dn[i]*X[i]) for i in range(n)]
    ytc = [fix(up[k]*Y[n-1-k]) for k in range(n)]
    if mode == 2:                                       # each factor conjugated by G_c separately
        Zyc = [Dm(0)] + [fix(dn[k]*Y[k-1]) for k in range(1, n)]
        Zxtc = [Dm(0)] + [fix(up[k]*X[n-k]) for k in range(1, n)]
    else:                                               # balanced: rho^{n-k} and rho^{-(n-k)}
        Zyc = [Dm(0)] + [fix(up[n-k]*Y[k-1]) for k in range(1, n)]
        Zxtc = [Dm(0)] + [fix(dn[n-k]*X[n-k]) for k in range(1, n)]
    return xc, ytc, Zyc, Zxtc

lowmul = lambda v, z: [fix(sum(v[a-k]*z[k] for k in range(a+1))) for a in range(len(z))]
upmul = lambda v, z: [fix(sum(v[b-a]*z[b] for b in range(a, len(z)))) for a in range(len(z))]

def apply_gs(vecs, z):
    xc, ytc, Zyc, Zxtc = vecs
    p1 = lowmul(xc, upmul(ytc, z)); p2 = lowmul(Zyc, upmul(Zxtc, z))
    return [fix((p1[i] - p2[i]) / xc[0]) if xc[0] != 0 else Dm(0) for i in range(len(z))]

# --- bound checks on the exact rescaled factors (Lemma: entry envelope of T_c^{-1}) ---
worst_env = 0.0; worst_p = 0.0
for g in blocks[:40]:
    L = len(g); bc = beta(g[0]); n = L; B = base[L]
    rho = (-PI*a2*dec(2*bc + 1)).exp()
    kp = 2*(-PI*a2*dec(sig + 2*bc)).exp(); km = 2*(-PI*a2*dec(sig - 2*bc)).exp()
    env = lambda h: min(Dm('1.12'), Dm('2.0001') * (kp**h if h > 0 else km**(-h)) if h else Dm('1.12'))
    x, y = B['x'], B['y']
    xc = [x[i] * rho**(-i) for i in range(n)]; ytc = [y[n-1-k] * rho**k for k in range(n)]
    Zyc = [Dm(0)] + [y[k-1] * rho**(n-k) for k in range(1, n)]
    Zxtc = [Dm(0)] + [x[n-k] * rho**(k-n) for k in range(1, n)]
    for i in range(n):
        worst_env = max(worst_env, float(abs(xc[i]) / env(-i)), float(abs(ytc[i]) / env(i)))
        if i: worst_env = max(worst_env, float(abs(Zyc[i]) / env(n-i)), float(abs(Zxtc[i]) / env(-(n-i))))
    for a in range(n):
        for b in range(n):
            m = min(a, b)
            s1 = sum(abs(xc[a-k]*ytc[b-k]) for k in range(m+1))
            s2 = sum(abs(Zyc[a-k]*Zxtc[b-k]) for k in range(m+1))
            worst_p = max(worst_p, float(s1 / (Dm('1.13')*env(b-a))), float(s2 / (Dm(4)*kp*km*env(b-a))))
print(f'envelope check: max |factor entry| / envelope = {worst_env:.3f}, '
      f'max partial-product term sum / bound = {worst_p:.3f}', 'OK' if worst_env <= 1 and worst_p <= 1 else 'VIOLATED')
ok = worst_env <= 1 and worst_p <= 1

# --- full solve per mode ---
random.seed(2)
u = [Dm(random.uniform(-1, 1)) for _ in range(s)]
xdir = solve(N, u)
bid = {}
for k, g in enumerate(blocks):
    for j in g: bid[j % s] = k
thr = Dm(2)**(-Qbits - int(math.log2(s)) - 4)
Delta = [[N[a][b] if bid[a] != bid[b] and N[a][b] > thr else Dm(0) for b in range(s)] for a in range(s)]
cols = sorted({b for a in range(s) for b in range(s) if Delta[a][b] != 0})
target = Dm(2)**-Qbits
# Fixed-point storage of T_lambda's vectors loses min(10^-P, |x_i|) on x_i (y is O(1), so it keeps
# relative precision).  The rescale rho_c^{-i} and the chirp ratio D_a/D_b, largest for
# (a, b) = (L-1, L-1-i), amplify that loss.  Predict whether it exceeds the target here.
def fp_loss_bits(g):
    L = len(g); x = base[L]['x']; lr = math.pi * a2 * float(2*beta(g[0]) + 1)
    return max(math.log2(10) * min(-Pdig, float(abs(x[i]).log10()))
               + math.log2(math.e) * (lr * i + math.pi * a2 * float(th) * ((L-1)**2 - (L-1-i)**2))
               for i in range(1, L))
amp = max(fp_loss_bits(g) for g in blocks)
fp_fails = amp > -Qbits
Plow = math.ceil((Qbits + 2*math.log2(lam) + 8) / math.log2(10))     # drops the chirp reserve R_D
print(f's,t=({s},{t}) theta={float(th):.4f} alpha2*theta={a2*float(th):.2f} w={w} lengths={lengths} '
      f'R_D={RD:.0f} bits Q={Qbits} P={Pdig} digits ({Pdig*math.log2(10):.0f} bits)')
for mode, pd, expect in ((0, Pdig, True), (1, Pdig, True), (2, Pdig, None),
                         (3, Pdig, False if fp_fails else None), (4, Plow, False)):
    PREC['d'] = pd; cache = {}
    def Minv(vec):
        out = [Dm(0)]*s
        for k, g in enumerate(blocks):
            L = len(g)
            if k not in cache: cache[k] = block_vectors(L, beta(g[0]), mode)
            z = [fix(vec[g[i] % s] * (-PI*a2*dec(th*i*i)).exp()) for i in range(L)]
            yv = apply_gs(cache[k], z)
            for i in range(L): out[g[i] % s] = yv[i] * (PI*a2*dec(th*i*i)).exp()
        return out
    y0 = Minv(u)
    MU = [Minv([Delta[r][c] for r in range(s)]) for c in cols]
    C = [[(Dm(1) if i == j else Dm(0)) + MU[j][cols[i]] for j in range(len(cols))] for i in range(len(cols))]
    try:
        z = solve(C, [y0[c] for c in cols], pivot=False)
        xs = [y0[r] - sum(MU[j][r]*z[j] for j in range(len(cols))) for r in range(s)]
        err = max(abs(xs[i] - xdir[i]) for i in range(s))
    except Exception:
        err = Dm(1)
    passed = err < target
    if expect is not None: ok &= passed == expect
    extra = ''
    if mode == 2:   # integer headroom the unbalanced factor L(rho^-k Zy) needs in fixed point
        extra = f' unbalanced factor max log2|entry|={max(float(abs(v).ln()/Dm(2).ln()) for vs in cache.values() for v in vs[2] if v):.0f}'
    if mode == 3: extra = f' predicted loss=2^{amp:.0f}'
    if mode == 4: extra = f' (P={pd} digits, no chirp reserve)'
    exp = 'report only' if expect is None else ('expected PASS' if expect else 'expected FAIL')
    print(f'  mode {mode}: err={float(err):.3e} {"PASS" if passed else "FAIL"} ({exp}){extra}')
if not ok: raise SystemExit(1)
