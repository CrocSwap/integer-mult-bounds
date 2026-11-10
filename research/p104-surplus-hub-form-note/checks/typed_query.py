"""Typed-query exact checks over the Gaussian rationals Q(i) (standard library only: fractions).
Run: python3.12 -I -B typed_query.py
H = H0/sqrt2 with H0 = [[1,1],[1,-1]]. Every identity below involves H only through H(x)H = (H0(x)H0)/2 or
H S H = (H0 S H0)/2, so no square root is needed and all arithmetic is exact."""
import itertools
from fractions import Fraction as Fr

class G:
    """Gaussian rational a + b i, exact."""
    __slots__ = ('a', 'b')
    def __init__(s, a=0, b=0): s.a = Fr(a); s.b = Fr(b)
    def __add__(s, o): o = g(o); return G(s.a + o.a, s.b + o.b)
    __radd__ = __add__
    def __sub__(s, o): o = g(o); return G(s.a - o.a, s.b - o.b)
    def __rsub__(s, o): return g(o) - s
    def __neg__(s): return G(-s.a, -s.b)
    def __mul__(s, o): o = g(o); return G(s.a*o.a - s.b*o.b, s.a*o.b + s.b*o.a)
    __rmul__ = __mul__
    def __truediv__(s, o):
        o = g(o); d = o.a*o.a + o.b*o.b
        return s * G(o.a/d, -o.b/d)
    def __rtruediv__(s, o): return g(o) / s
    def conj(s): return G(s.a, -s.b)
    def __eq__(s, o): o = g(o); return s.a == o.a and s.b == o.b
    def __hash__(s): return hash((s.a, s.b))
    def __repr__(s):
        if s.b == 0: return str(s.a)
        if s.a == 0: return f'{s.b}i'
        return f'({s.a}+{s.b}i)'
def g(x): return x if isinstance(x, G) else G(x)
I = G(0, 1); ONE = G(1); ZERO = G(0)

def M(rows): return [[g(x) for x in r] for r in rows]
def mm(A, B):
    Bt = list(zip(*B)); return [[sum((a*b for a, b in zip(r, c)), ZERO) for c in Bt] for r in A]
def madd(A, B): return [[a + b for a, b in zip(r, s)] for r, s in zip(A, B)]
def msub(A, B): return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]
def sc(c, A): return [[g(c)*a for a in r] for r in A]
def eye(n): return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]
def zeros(r, c): return [[ZERO]*c for _ in range(r)]
def kp(A, B):
    return [[A[i][j]*B[k][l] for j in range(len(A[0])) for l in range(len(B[0]))] for i in range(len(A)) for k in range(len(B))]
def dag(A): return [[A[j][i].conj() for j in range(len(A))] for i in range(len(A[0]))]
def is0(A): return all(x == ZERO for r in A for x in r)
def diag(*d): n = len(d); return [[g(d[i]) if i == j else ZERO for j in range(n)] for i in range(n)]
def minv(A):
    n = len(A); W = [A[i][:] + eye(n)[i] for i in range(n)]
    for c in range(n):
        p = next(r for r in range(c, n) if W[r][c] != ZERO); W[c], W[p] = W[p], W[c]
        pv = W[c][c]; W[c] = [x/pv for x in W[c]]
        for r in range(n):
            if r != c and W[r][c] != ZERO:
                f = W[r][c]; W[r] = [x - f*y for x, y in zip(W[r], W[c])]
    return [r[n:] for r in W]

H0 = M([[1, 1], [1, -1]]); S = diag(1, I); X = M([[0, 1], [1, 0]]); Z = diag(1, -1); I2 = eye(2)
a = (1 + I)/2; b = (1 - I)/2
C = sc(Fr(1, 2), mm(mm(H0, S), H0))                      # H S H
aIbX = madd(sc(a, I2), sc(b, X))
print("1. C=HSH == aI+bX:", is0(msub(C, aIbX)), "| C^2==X:", is0(msub(mm(C, C), X)), "| b/a =", b/a)

def mpow(P, k): return P if k else eye(len(P))
PH = (ONE, I, -ONE, -I)
def pauli_n(Mx, n):
    for xs in itertools.product((0, 1), repeat=n):
        for zs in itertools.product((0, 1), repeat=n):
            P = M([[1]])
            for q in range(n): P = kp(P, mm(mpow(X, xs[q]), mpow(Z, zs[q])))
            for ph in PH:
                if is0(msub(Mx, sc(ph, P))): return xs + zs
    return None
def symp(U, n):
    cols = []; Ui = minv(U)
    for kind in ('x', 'z'):
        for q in range(n):
            P = M([[1]])
            for r in range(n): P = kp(P, X if (kind == 'x' and r == q) else Z if (kind == 'z' and r == q) else I2)
            cols.append(pauli_n(mm(mm(U, P), Ui), n))
    return [list(r) for r in zip(*cols)]                  # 2n x 2n, columns = images of x_1..x_n, z_1..z_n
def rankF2(Mx):
    Mx = [[int(v) % 2 for v in row] for row in Mx]; r = 0; rows = len(Mx); cols = len(Mx[0]) if Mx else 0
    for c in range(cols):
        p = next((i for i in range(r, rows) if Mx[i][c]), None)
        if p is None: continue
        Mx[r], Mx[p] = Mx[p], Mx[r]
        for i in range(rows):
            if i != r and Mx[i][c]: Mx[i] = [(u + v) % 2 for u, v in zip(Mx[i], Mx[r])]
        r += 1
    return r
def Bblock(Sy, n): return [row[n:] for row in Sy[:n]]
S1 = symp(C, 1); print("   symplectic of C:", S1, "  B-block rank_F2 =", rankF2(Bblock(S1, 1)))

# free group F: monomial matrices with entries in {1,i,-1,-i}, 1 qubit
F1 = []
for perm in itertools.permutations(range(2)):
    for p in itertools.product(PH, repeat=2):
        Mx = zeros(2, 2)
        for r in range(2): Mx[r][perm[r]] = p[r]
        F1.append(Mx)
print("   |F_1| =", len(F1))
def prop(A, B):
    for i in range(len(A)):
        for j in range(len(A[0])):
            if B[i][j] != ZERO:
                lam = A[i][j]/B[i][j]; return is0(msub(A, sc(lam, B))) and lam != ZERO
    return False
inF = any(prop(C, f) for f in F1)
cell = any(prop(C, mm(mm(f1, H0), f2)) for f1 in F1 for f2 in F1)
print("1a. C in F (free)?", inF, "| C in F*H*F (one H-cell, C-rank 1)?", cell)

# field Bruhat (non-unitary): C = U(t1) W U(t2), U(t) = [[1,t],[0,1]], W antidiagonal [[0,w1],[w2,0]]
# U(t1) W U(t2) = [[w2 t1, w1 + t1 w2 t2],[w2, w2 t2]]: the four entries of C determine (t1,t2,w1,w2) uniquely.
Uu = lambda t: M([[1, t], [0, 1]])
w2 = C[1][0]; t2 = C[1][1]/w2; t1 = C[0][0]/w2; w1 = C[0][1] - t1*w2*t2
Wn = M([[0, w1], [w2, 0]])
chk = is0(msub(mm(mm(Uu(t1), Wn), Uu(t2)), C))
print("1b. field-Bruhat  C = U(t1) W U(t2), W antidiagonal: t1 =", t1, "t2 =", t2, "w1 =", w1, "w2 =", w2)
print("    check:", chk, "| U(t) unitary?", is0(msub(mm(dag(Uu(t1)), Uu(t1)), I2)),
      "| W monomial with non-unit entry:", Wn,
      "(shears have CONSTANT Gaussian coefficient t=i: Q-independent, non-Clifford, outside F and outside the symplectic lemma)")

# 2. K_P
H4 = sc(Fr(1, 2), kp(H0, H0))                               # H (x) H
CZ = diag(1, 1, 1, -1); SW = M([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
X1 = kp(X, I2); X2 = kp(I2, X)
KP = sc(Fr(1, 2), msub(madd(madd(eye(4), X1), X2), mm(X1, X2)))
print("2.  K_P == H(x)H diag((-1)^(x1x2)) H(x)H :", is0(msub(KP, mm(mm(H4, CZ), H4))))
print("    (H(x)H, normalised H=[[1,1],[1,-1]]/sqrt2) == CZ K_P CZ SWAP :", is0(msub(H4, mm(mm(mm(CZ, KP), CZ), SW))),
      "  [(H(x)H) here uses the sqrt2-normalised H; the unnormalised version differs by a factor 1/2 only]")
S2K = symp(KP, 2); S2C = symp(kp(C, C), 2); S2CI = symp(kp(C, I2), 2)
print("    rank_F2 B:  K_P =", rankF2(Bblock(S2K, 2)), "| C(x)C =", rankF2(Bblock(S2C, 2)), "| C(x)I =", rankF2(Bblock(S2CI, 2)))
nz = lambda A: [sum(1 for v in r if v != ZERO) for r in A]
print("    nonzeros per row: K_P", nz(KP), "| C(x)I", nz(kp(C, I2)), "-> K_P not in F*(C(x)I)*F (monomial maps preserve row support sizes)")
CC = kp(C, C)
def same_cell(A, B):
    for pr in itertools.permutations(range(4)):
        for pc in itertools.permutations(range(4)):
            Bp = [[B[pr[i]][pc[j]] for j in range(4)] for i in range(4)]
            if any((A[i][j] == ZERO) != (Bp[i][j] == ZERO) for i in range(4) for j in range(4)): continue
            Rr = [[A[i][j]/Bp[i][j] if Bp[i][j] != ZERO else ZERO for j in range(4)] for i in range(4)]
            base = Rr[0][0]; ok = True
            for i in range(4):
                for j in range(4):
                    if Rr[i][j] == ZERO: continue
                    pred = Rr[i][0]*Rr[0][j]/base
                    if Rr[i][j] != pred: ok = False; break
                    if (Rr[i][0]/base) not in PH: ok = False; break
                if not ok: break
            if ok and all((Rr[0][j]/base) in PH for j in range(4)): return True
    return False
print("    K_P in F*(C(x)C)*F (same Bruhat cell, rank 2)?", same_cell(KP, CC), "  -> K_P = a rank-2 plane job; NO rank drop vs C(x)C")
