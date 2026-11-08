"""Schur law for owned lifetimes and the per-register leak identity: exact rational arithmetic, stdlib only."""
import random, sys
from fractions import Fraction as Q
fails = []
def ck(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg, flush=True)
    if not cond: fails.append(msg)
def mm(A, B):
    Bt = list(zip(*B)); return [[sum(a * b for a, b in zip(r, c)) for c in Bt] for r in A]
def eye(n): return [[Q(int(i == j)) for j in range(n)] for i in range(n)]
def inv(A):
    n = len(A); M = [A[i][:] + eye(n)[i] for i in range(n)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None: return None
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]; M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c]; M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return [r[n:] for r in M]
def sub(M, R, C): return [[M[i][j] for j in C] for i in R]
def sm(A, B): return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]
rng = random.Random(4)
def rand_inv(n):
    while True:
        M = [[Q(rng.randint(-3, 3)) for _ in range(n)] for _ in range(n)]
        if inv(M) is not None: return M
# Schur law: T_f invertible on cells P + O.  Rows (outputs) = P_r + O_d, columns (inputs) = P_c + O_b.
nP, nO = 5, 3
okS = okI = True; cases = 0; singular_seen = 0
for trial in range(60):
    n = nP + nO
    Tf = rand_inv(n)
    P = list(range(nP)); O = list(range(nP, n))
    Tpub = sub(Tf, P, P)
    Ti = inv(Tf)                                  # rows indexed by inputs, columns by outputs
    Dd = sub(Ti, O, O)                            # Tinv_f[O_b, O_d]
    Dinv = inv(Dd)
    Tp_inv = inv(Tpub)
    # invertible iff the owned block of the inverse is invertible
    okI &= ((Tp_inv is not None) == (Dinv is not None))
    if Tp_inv is not None and Dinv is not None:
        rhs = sm(sub(Ti, P, P), mm(mm(sub(Ti, P, O), Dinv), sub(Ti, O, P)))
        okS &= (Tp_inv == rhs); cases += 1
    else:
        singular_seen += 1
# force singular cases: make the owned block of the inverse singular
for trial in range(20):
    n = nP + nO
    Tf = rand_inv(n)
    Ti = inv(Tf)
    # modify T_f so that Tinv[O,O] has a zero column: set the last owned column of Ti on O rows to 0 via Tf = inv(Ti')
    for r in range(nP, n): Ti[r][n - 1] = Q(0)
    Tf2 = inv(Ti)
    if Tf2 is None: continue
    Tpub = sub(Tf2, list(range(nP)), list(range(nP)))
    okI &= (inv(Tpub) is None) and (inv(sub(Ti, list(range(nP, n)), list(range(nP, n)))) is None)
    singular_seen += 1
ck(okS and cases >= 30, f'Schur law Tinv_pub = Tinv[P,P] - Tinv[P,O_d] Tinv[O_b,O_d]^-1 Tinv[O_b,P] exact on {cases} random invertible T_f (5 public cells, 3 owned lifetimes)')
ck(okI and singular_seen >= 10, f'T_pub = T_f[P,P] is invertible exactly when Tinv_f[O_b,O_d] is, including {singular_seen} singular cases')
# Leak identity: T = B A at a cut; per register i four rank-one terms
okL = okSum = True
for trial in range(40):
    n = 7; nX = 3
    A = rand_inv(n); B = rand_inv(n)
    Ai = inv(A); Bi = inv(B)
    T = mm(B, A); Ti = inv(T)
    Xp = list(range(nX)); Yp = list(range(nX, 2 * nX))
    f = [[sum(B[y][i] * A[i][x] for i in range(n)) for x in Xp] for y in Yp]
    r = [[sum(Ai[x][i] * Bi[i][y] for i in range(n)) for y in Yp] for x in Xp]
    okSum &= (f == [[T[y][x] for x in Xp] for y in Yp]) and (r == [[Ti[x][y] for y in Yp] for x in Xp])
    LXs = [[sum(Ai[x][i] * A[i][xp] for i in range(n)) for xp in Xp] for x in Xp]
    LYs = [[sum(B[y][i] * Bi[i][yp] for i in range(n)) for yp in Yp] for y in Yp]
    okSum &= (LXs == [[Q(int(a == b)) for b in range(nX)] for a in range(nX)]) and (LYs == [[Q(int(a == b)) for b in range(nX)] for a in range(nX)])
    for i in range(n):
        for x in Xp:
            for xp in Xp:
                for y in range(nX):
                    for yp in range(nX):
                        fi = B[Yp[y]][i] * A[i][xp]; ri = Ai[x][i] * Bi[i][Yp[yp]]
                        lx = Ai[x][i] * A[i][xp]; ly = B[Yp[y]][i] * Bi[i][Yp[yp]]
                        okL &= (lx * ly == ri * fi)
    # invariance under a diagonal rescaling of register i (A -> D A, B -> B D^-1)
ck(okSum, 'sums over registers: sum f_i = T[Y,X], sum r_i = Tinv[X,Y], sum L_X,i = I, sum L_Y,i = I (40 random cuts, exact)')
ck(okL, 'leak identity L_X,i[x,x\'] L_Y,i[y,y\'] = r_i[x,y\'] f_i[y,x\'] for every register i, every index quadruple (40 random cuts, 7 registers)')
# gauge invariance of each of the four terms under diagonal rescaling of one register
A = rand_inv(6); B = rand_inv(6); Ai = inv(A); Bi = inv(B)
lam = [Q(1), Q(2), Q(-3), Q(5), Q(1, 7), Q(4)]
A2 = [[lam[i] * A[i][j] for j in range(6)] for i in range(6)]; B2 = [[B[i][j] / lam[j] for j in range(6)] for i in range(6)]
A2i = inv(A2); B2i = inv(B2)
same = True
for i in range(6):
    for x in range(3):
        for xp in range(3):
            for y in range(3):
                same &= (B[3 + y][i] * A[i][xp] == B2[3 + y][i] * A2[i][xp]) and (Ai[x][i] * A[i][xp] == A2i[x][i] * A2[i][xp]) and (B[3 + y][i] * Bi[i][3 + y] == B2[3 + y][i] * B2i[i][3 + y])
ck(same, 'f_i, L_X,i and L_Y,i are invariant under a diagonal rescaling of the registers (A -> D A, B -> B D^-1)')
print('PASS_SCHUR_LEAK' if not fails else 'FAILED_SCHUR_LEAK')
sys.exit(1 if fails else 0)
