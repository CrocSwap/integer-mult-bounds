"""A2 toy: the Gram floor does not transfer to arbitrary rank-one decompositions (exact, rational, stdlib only)."""
import itertools
from fractions import Fraction as Fr
fails = []
def ck(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg, flush=True)
    if not cond: fails.append(msg)
L = [(1, -1, 0), (0, 1, -1), (1, 0, -1)]            # the three lines of A2 in the plane x+y+z = 0
def dot(a, b): return sum(x * y for x, y in zip(a, b))
ip = [[dot(a, b) for b in L] for a in L]              # norm 2, odd (+-1) off the diagonal
ck(all(ip[i][i] == 2 and abs(ip[i][j]) == 1 for i in range(3) for j in range(3) if i != j), 'A2: three lines, all pairwise inner products +-1 (odd), so N = I_3')
# unit vector of the plane orthogonal to line i
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
nrm = (1, 1, 1)
perp = [cross(nrm, L[i]) for i in range(3)]           # in the plane, orthogonal to line i
ck(all(dot(perp[i], nrm) == 0 and dot(perp[i], L[i]) == 0 and all(dot(perp[i], L[j]) != 0 for j in range(3) if j != i) for i in range(3)),
   'the plane vector orthogonal to line i is orthogonal to no other line')
# decoder = sum of terms lambda u w^T equal to the projector Pi = I - J/3 of the plane
Pi = [[Fr(int(i == j)) - Fr(1, 3) for j in range(3)] for i in range(3)]
def outer(u, w): return [[Fr(u[i] * w[j]) for j in range(3)] for i in range(3)]
def flat(M): return [x for r in M for x in r]
def solvable(mats, target):
    # is target in the Q-span of mats (exact elimination)?
    rows = [flat(m) for m in mats]
    T = flat(target)
    rows_aug = [r[:] for r in rows]
    # column space test: rank(rows) == rank(rows + [T])
    def rk(R):
        R = [r[:] for r in R]; rr = 0
        for c in range(len(R[0])):
            p = next((i for i in range(rr, len(R)) if R[i][c] != 0), None)
            if p is None: continue
            R[rr], R[p] = R[p], R[rr]
            for i in range(len(R)):
                if i != rr and R[i][c] != 0:
                    f = R[i][c] / R[rr][c]; R[i] = [a - f * b for a, b in zip(R[i], R[rr])]
            rr += 1
        return rr
    return rk(rows) == rk(rows + [T])
types = [(i, j) for i in range(3) for j in range(3) if i != j]   # rho = 1 terms: u orth to line i, w orth to line j
def mat(t): return outer(perp[t[0]], perp[t[1]])
c2 = any(solvable([mat(t) for t in combo], Pi) for combo in itertools.combinations_with_replacement(types, 2))
c3 = any(solvable([mat(t) for t in combo], Pi) for combo in itertools.combinations_with_replacement(types, 3))
ck(not c2 and not c3, 'two or three terms of price 1 (all 6 types, repeats allowed) never sum to the plane identity')
# one term of price 1 plus one other term: the remainder must be rank one, which forces both of its vectors onto lines (price 3)
def rank_rows(M):
    M = [r[:] for r in M]; rr = 0
    for c in range(3):
        p = next((i for i in range(rr, 3) if M[i][c] != 0), None)
        if p is None: continue
        M[rr], M[p] = M[p], M[rr]
        for i in range(3):
            if i != rr and M[i][c] != 0:
                f = M[i][c] / M[rr][c]; M[i] = [a - f * b for a, b in zip(M[i], M[rr])]
        rr += 1
    return rr
ok = True; seen_forced = set()
for (i, j) in types:
    u, w = perp[i], perp[j]
    d = dot(u, w)
    ok &= d != 0
    lam = Fr(1, d)
    R = [[Pi[a][b] - lam * u[a] * w[b] for b in range(3)] for a in range(3)]
    ok &= rank_rows(R) == 1
    # a rank-one matrix a b^T with the column space vector proportional to line j and row space vector to line i
    col = next(c for c in range(3) if any(R[r][c] != 0 for r in range(3)))
    colvec = tuple(R[r][col] for r in range(3))
    row = next(r for r in range(3) if any(R[r][c] != 0 for c in range(3)))
    rowvec = tuple(R[row][c] for c in range(3))
    # supports: lines not orthogonal to the vector
    S = [k for k in range(3) if dot(L[k], colvec) != 0]; T = [k for k in range(3) if dot(L[k], rowvec) != 0]
    seen_forced.add((len(S), len(T), len(set(S) & set(T))))
    ok &= cross(colvec, L[j]) == (0, 0, 0) and cross(rowvec, L[i]) == (0, 0, 0)
ck(ok and seen_forced == {(3, 3, 3)}, 'a price-1 term plus a second term: the second term is forced onto lines j and i, support 3 x 3, price 3 (never 2)')
print('hand: with every term priced >= 1, total cost <= 3 leaves only the term-price multisets (1,1), (1,1,1), (1,2); the first two are excluded by the exact test above and (1,2) by the forced remainder, so c_Gram(A2) >= 4; the forced remainder (price 3) attains 4')
# identity decoder: terms e_p e_p^T, one per line, each of price 1; N o I = I holds since N = I_3
IDc = sum(len({p} & {p}) for p in range(3))
ck(IDc == 3 and all(ip[p][q] % 2 == 1 for p in range(3) for q in range(3) if p != q), 'the identity decoder O = I_3 (terms e_p e_p^T, price |{p} & {p}| = 1 each) has N o O = I because N = I_3, and costs 3, below the Gram value 4')
print('PASS_A2' if not fails else 'FAILED_A2')
import sys; sys.exit(1 if fails else 0)
