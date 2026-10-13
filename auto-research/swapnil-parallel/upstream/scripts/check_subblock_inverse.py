"""Numerical check of the recentred sub-block inverse against a direct solve. Args: s t alpha^2 Q_bits block_len P_digits."""
# Sub-blocked segmented inverse: cut segments into blocks of length lam, recentre the chirp
# per block (block Toeplitz T_c = G T G^{-1}), couple all cuts and wraps by Woodbury.
from decimal import Decimal as Dm, getcontext
from fractions import Fraction as F
import math, sys, random
s, t, a2, Qbits, lam, Pdig = [int(a) for a in sys.argv[1:]] or [60, 67, 9, 200, 3, 120]
getcontext().prec = 260
PI = Dm('3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196')
sig = F(t, s); th = sig - 1
q = lambda j: math.floor(F(t*j, s) + F(1, 2)); beta = lambda j: F(t*j, s) - q(j)
dec = lambda f: Dm(f.numerator) / Dm(f.denominator)
E = lambda x: (-PI*a2*dec(x)).exp()
N = [[Dm(0)]*s for _ in range(s)]
for l in range(s):
    for j in range(l-3*s, l+3*s):
        N[l][j % s] += E((sig*j - q(l))**2 - beta(j)**2)
wraps = [j for j in range(s) if q(j+1) - q(j) == 2]
segs = []
for i, w0 in enumerate(wraps):
    st = w0 + 1; en = wraps[(i+1) % len(wraps)] + (s if i+1 == len(wraps) else 0)
    segs.append(list(range(st, en+1)))
blocks = [g[k:k+lam] for g in segs for k in range(0, len(g), lam)]
def solve(A, bv):
    n = len(A); M = [row[:] + [bv[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c])); M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                for k in range(c, n+1): M[r][k] -= f*M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]
# check block = D_c T_c D_c^{-1} with T_c symbol exp(-pi a2 (sigma h^2 + 2 beta_c h)), centre c = first index
maxerr = Dm(0)
for g in blocks:
    c = g[0]; bc = beta(c)
    for a in g:
        for b in g:
            h = b - a; u = a - c; v = b - c
            Tc = E(sig*h*h + 2*bc*h)
            # exact: X = (sigma h + beta_a)^2 - beta_b^2 with beta linear in-segment
            X = (sig*h + beta(a))**2 - beta(b)**2
            Dfac = (PI*a2*dec(th*u*u)).exp() * (-PI*a2*dec(th*v*v)).exp()
            maxerr = max(maxerr, abs(Tc*Dfac - E(X)))
print('blocks', len(blocks), 'max |block - D_c T_c D_c^-1| = %.2e' % float(maxerr))
random.seed(1)
u = [Dm(random.uniform(-1, 1)) for _ in range(s)]
x = solve(N, u)
bid = {}
for k, g in enumerate(blocks):
    for j in g: bid[j % s] = k
thr = Dm(2)**(-Qbits - int(math.log2(s)) - 4)
def Minv(vec):
    out = [Dm(0)]*s
    for g in blocks:
        c = g[0]; bc = beta(c); L = len(g)
        getcontext().prec = Pdig
        T = [[+E(sig*(b-a)**2 + 2*bc*(b-a)) for b in range(L)] for a in range(L)]
        rhs = [+(vec[g[i] % s] * (-PI*a2*dec(th*i*i)).exp()) for i in range(L)]
        y = solve(T, rhs)
        getcontext().prec = 260
        for i in range(L): out[g[i] % s] = y[i] * (PI*a2*dec(th*i*i)).exp()
    return out
Delta = [[N[a][b] if bid[a] != bid[b] and N[a][b] > thr else Dm(0) for b in range(s)] for a in range(s)]
cols = sorted({b for a in range(s) for b in range(s) if Delta[a][b] != 0})
y = Minv(u)
MU = [Minv([Delta[r][c] for r in range(s)]) for c in cols]
C = [[(Dm(1) if i == j else Dm(0)) + MU[j][cols[i]] for j in range(len(cols))] for i in range(len(cols))]
z = solve(C, [y[c] for c in cols])
xs = [y[r] - sum(MU[j][r]*z[j] for j in range(len(cols))) for r in range(s)]
err = max(abs(xs[i] - x[i]) for i in range(s))
print('cuts+wraps', len(blocks), 'coupled cols', len(cols), 'err vs direct %.3e target %.3e' % (float(err), float(Dm(2)**-Qbits)),
      'PASS' if err < Dm(2)**-Qbits else 'FAIL')
