"""Numerical check of the recentred sub-block inverse through the reuse path.

One inverse of the base Toeplitz matrix T_lambda (symbol exp(-pi a2 (sigma h^2 - h))) is
computed per block length at high precision, then stored with P significant digits (floating
point). Every block applies T_c^{-1} = G_c T_lambda^{-1} G_c^{-1}, with
G_c = diag(rho_c^{-i}) and rho_c = exp(-pi a2 (2 beta_c + 1)). Segments are split into
near-equal blocks of length at least 2w. Cuts and wraps are coupled by Woodbury, and the
capacitance system is solved by elimination without pivoting. The result is compared with a
direct solve of N.
Args: s t alpha^2 Q_bits P_digits [1 = fixed-point storage, expected to fail].
"""
from decimal import Decimal as Dm, getcontext, Context
from fractions import Fraction as F
import math, sys, random

argv = [int(a) for a in sys.argv[1:]] or [241, 256, 17, 150, 60]
s, t, a2, Qbits, Pdig = argv[:5]
FIXED_POINT = len(argv) > 5 and argv[5] == 1     # negative control: absolute precision storage
getcontext().prec = 140
PI = Dm('3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196442881097566593344612847564823378678316527120190914564856692346034861045432664821339360726024914127372458700660631558817488152092096282925409171536436789259036001133053054882046652138414695194151160943305727036575959195309218611738193261179310511854807446237996274956735188575272489122793818301194912983367336244065664308602139494639522473719070217986094370277053921717629317675238467481846766940513200056812714526356082778577134275778960917363717872146844090122495343014654958537105079227968925892354201995611212902196086403441815981362977477130996051870721134999999837297804995105973173281609631859502445945534690830264252230825334468503526193118817101000313783875288658753320838142061717766914730359825349042875546873115956286388235378759375195778185778053217122680661300192787661119590921642019893809525720106548586327')
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

def inverse(A):
    n = len(A)
    cols = [solve(A, [Dm(1) if i == j else Dm(0) for i in range(n)]) for j in range(n)]
    return [[cols[j][i] for j in range(n)] for i in range(n)]

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
base = {}
for L in lengths:
    getcontext().prec = Pdig + int(9.06 * a2 * L / 3.32) + 20      # absolute precision P + 9.06 a2 L bits
    T = [[E(sig*(b-a)**2 - (b-a)) for b in range(L)] for a in range(L)]
    Ti = inverse(T)
    getcontext().prec = 140
    ctx = Context(prec=Pdig)
    if FIXED_POINT:
        unit = Dm(10) ** -Pdig
        base[L] = [[(v / unit).to_integral_value() * unit for v in row] for row in Ti]
    else:
        base[L] = [[ctx.plus(v) for v in row] for row in Ti]      # floating point, P significant digits
random.seed(2)
u = [Dm(random.uniform(-1, 1)) for _ in range(s)]
x = solve(N, u)
bid = {}
for k, g in enumerate(blocks):
    for j in g: bid[j % s] = k

def Minv(vec):
    out = [Dm(0)]*s
    for g in blocks:
        c = g[0]; bc = beta(c); L = len(g)
        rho = (-PI*a2*dec(2*bc + 1)).exp()
        Ti = base[L]
        rhs = [vec[g[i] % s] * (-PI*a2*dec(th*i*i)).exp() for i in range(L)]
        y = [sum(rho**(b - a) * Ti[a][b] * rhs[b] for b in range(L)) for a in range(L)]   # G T^-1 G^-1
        for i in range(L): out[g[i] % s] = y[i] * (PI*a2*dec(th*i*i)).exp()
    return out

thr = Dm(2)**(-Qbits - int(math.log2(s)) - 4)
Delta = [[N[a][b] if bid[a] != bid[b] and N[a][b] > thr else Dm(0) for b in range(s)] for a in range(s)]
cols = sorted({b for a in range(s) for b in range(s) if Delta[a][b] != 0})
y = Minv(u)
MU = [Minv([Delta[r][c] for r in range(s)]) for c in cols]
C = [[(Dm(1) if i == j else Dm(0)) + MU[j][cols[i]] for j in range(len(cols))] for i in range(len(cols))]
offdiag = max(abs(C[i][j]) for i in range(len(cols)) for j in range(len(cols)) if i != j)
z = solve(C, [y[c] for c in cols], pivot=False)
xs = [y[r] - sum(MU[j][r]*z[j] for j in range(len(cols))) for r in range(s)]
err = max(abs(xs[i] - x[i]) for i in range(s))
target = Dm(2)**-Qbits
print(f'theta={float(th):.4f} alpha2*theta={a2*float(th):.2f} w={w} block lengths={lengths} blocks={len(blocks)} '
      f'max|C-I| offdiag={float(offdiag):.2e} err={float(err):.3e} target={float(target):.3e}',
      'PASS' if err < target else 'FAIL')
if err >= target: raise SystemExit(1)
