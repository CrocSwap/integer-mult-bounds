#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Part I, the odd unit paid per grading: exact checks of the contract identities. Standard library only.

A grading sigma_p flips the sign of one port variable q_p (q -> -q).  For a matrix N(q) of Laurent entries,
R(N) = sigma(N) N^-1 is its sigma-factor and o(N) = rank(R - I) its odd-unit count.  Matrices are evaluated
exactly over Q at two generic rational points; sigma is evaluation at -q.  Checked:

  I1  o(N) = rank Odd(N), Odd(N) = (N - sigma N)/2, for random 2x2..4x4 coupled matrices in two port variables,
      in both gradings (any size, any coupling).
  I2  Cayley form: with E, O the sigma-even/odd parts, dim ker(R + I) = dim ker E (t = -1 <=> E singular).
  I3  per port N = [[c, a q], [b/q, d]]: det R = 1, tr R = 2(cd+ab)/(cd-ab), det(R + I) = -4cd/(ab - cd), so
      t_eff = ab/(cd - ab) and t_eff = -1 <=> cd = 0 (the park); HOST(alpha, beta) has t_eff = alpha*beta.
  I4  coupled singular pencil: E_a singular while E_0 = I, and the q_b-odd entries are o_b = 2 junk in ledger b.
  I5  the isotropic kernel a + b q_a^2 q_b^2 is even in both gradings (o_a = o_b = 0); the monomial q_a q_b is odd in
      both (o_a = o_b = 1).
  I6  a q-free coupling P^-1 T P of the per-port target T = diag(1/q_a, 1/q_a, 1/q_b, 1/q_b) leaves m_a = 2.
  I7  the merged plane M45 = [[1,-q],[1/q,1]]: M45 = U_q + L_q - I, H = L_q U_q, o(M45) = 2, R^2 = -I,
      M45^2 = 2 J_q, M45^4 = -4I, det 2, diag(1,1/2) M45 = HOST(-1, 1/2) (t = -1/2), H M45^-1 = [[1,0],[1/(2q),1/2]]
      has o = 1 (the park as a caller op).
  I8  dressing invariance: R(A N B) = A R(N) A^-1 for sigma-fixed A, B (tr R invariant), 200 random cases;
      control: a q-odd A changes tr R.
  I9  the b-family X = x - y, Y = x + b y: t = bc/det = -1/(1+b) for b not in {0,-1}; t = -1 only at b = 0, where
      the window scalar (1+b)/b has a simple pole; t is invariant under both diagonal gauges.
Prints PASS_ODD_UNIT_PER_GRADING."""
import random
from fractions import Fraction as Fr

PTS = [(Fr(7, 3), Fr(-5, 11)), (Fr(13, 2), Fr(3, 17))]


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


def rank(M):
    A = [list(r) for r in M]
    r = 0
    cols = len(A[0]) if A else 0
    for c in range(cols):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c] / A[r][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        r += 1
    return r


def mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def inv(A):
    n = len(A)
    M = [list(A[i]) + [Fr(int(i == j)) for j in range(n)] for i in range(n)]
    for c in range(n):
        p = next(i for i in range(c, n) if M[i][c] != 0)
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        M[c] = [x / piv for x in M[c]]
        for i in range(n):
            if i != c and M[i][c] != 0:
                f = M[i][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[c])]
    return [r[n:] for r in M]


def det(A):
    A = [list(r) for r in A]
    n, d = len(A), Fr(1)
    for c in range(n):
        p = next((i for i in range(c, n) if A[i][c] != 0), None)
        if p is None:
            return Fr(0)
        if p != c:
            A[c], A[p] = A[p], A[c]
            d = -d
        d *= A[c][c]
        for i in range(c + 1, n):
            f = A[i][c] / A[c][c]
            A[i] = [x - f * y for x, y in zip(A[i], A[c])]
    return d


def eye(n):
    return [[Fr(int(i == j)) for j in range(n)] for i in range(n)]


def add(A, B, s=1):
    return [[x + s * y for x, y in zip(r, t)] for r, t in zip(A, B)]


def ev(M, qa, qb):
    return [[Fr(f(qa, qb)) for f in r] for r in M]


SIG = {'a': lambda qa, qb: (-qa, qb), 'b': lambda qa, qb: (qa, -qb)}


def o(M, g):
    best = 0
    for qa, qb in PTS:
        N = ev(M, qa, qb)
        S = ev(M, *SIG[g](qa, qb))
        best = max(best, rank(add(mul(S, inv(N)), eye(len(N)), -1)))
    return best


def r_odd(M, g):
    best = 0
    for qa, qb in PTS:
        N = ev(M, qa, qb)
        S = ev(M, *SIG[g](qa, qb))
        best = max(best, rank([[(x - y) / 2 for x, y in zip(r, t)] for r, t in zip(S, N)]))
    return best


MON = [lambda a, b: 1, lambda a, b: -1, lambda a, b: 2, lambda a, b: a, lambda a, b: -a, lambda a, b: 1 / a,
       lambda a, b: a * b, lambda a, b: b, lambda a, b: 1 / b, lambda a, b: 0]


def random_matrix(rng):
    d = rng.choice([2, 3, 4])
    M = [[rng.choice(MON) for _ in range(d)] for _ in range(d)]
    if any(det(ev(M, qa, qb)) == 0 for qa, qb in PTS):
        return None
    return M


def main():
    rng = random.Random(1)
    # I1
    ok = n = 0
    while n < 40:
        M = random_matrix(rng)
        if M is None:
            continue
        n += 1
        ok += (o(M, 'a') == r_odd(M, 'a')) and (o(M, 'b') == r_odd(M, 'b'))
    expect('I1 o(N) = rank Odd(N), random coupled 2-4x4, both gradings', (ok, n), (40, 40))
    # I2 (include matrices with a singular even part by construction)
    ok = n = sing = 0
    while n < 40:
        M = random_matrix(rng)
        if M is None:
            continue
        qa, qb = PTS[0]
        N = ev(M, qa, qb)
        S = ev(M, -qa, qb)
        E = [[(x + y) / 2 for x, y in zip(r, t)] for r, t in zip(N, S)]
        R = mul(S, inv(N))
        a = len(N) - rank(add(R, eye(len(N))))
        b = len(N) - rank(E)
        n += 1
        ok += a == b
        sing += b > 0
    expect('I2 Cayley dim ker(R+I) = dim ker E (random)', (ok, n), (40, 40))
    say('    (of which with singular E: %d)' % sing)
    for c_, d_ in [(0, 1), (1, 0), (0, 0)]:
        # park examples: per-port N with cd = 0 must have a -1 eigenvalue
        M = [[lambda qa, qb, c_=c_: c_, lambda qa, qb: qa], [lambda qa, qb: 1 / qa, lambda qa, qb, d_=d_: d_]]
        qa, qb = PTS[0]
        N, S = ev(M, qa, qb), ev(M, -qa, qb)
        if det(N) == 0:
            continue
        expect('I2 park c=%d d=%d: dim ker(R+I) = dim ker E' % (c_, d_),
               2 - rank(add(mul(S, inv(N)), eye(2))), 2 - rank([[(x + y) / 2 for x, y in zip(r, t)] for r, t in zip(N, S)]))
    # I3 per-port law, exact at random rational points
    bad = 0
    for _ in range(300):
        a, b, c, d, q = (Fr(rng.randint(-9, 9), rng.randint(1, 7)) for _ in range(5))
        if q == 0 or c * d - a * b == 0 or a * b - c * d == 0:
            continue
        N = [[c, a * q], [b / q, d]]
        S = [[c, -a * q], [-b / q, d]]
        R = mul(S, inv(N))
        D = c * d - a * b
        bad += det(R) != 1
        bad += R[0][0] + R[1][1] != 2 * (c * d + a * b) / D
        bad += det(add(R, eye(2))) != -4 * c * d / (a * b - c * d)
        # t_eff from tr R = tr W = 2 + 4t
        t = ((R[0][0] + R[1][1]) - 2) / 4
        bad += t != a * b / (c * d - a * b)
        bad += (t == -1) != (c * d == 0)
    expect('I3 per-port R, det R = 1, det(R+I) = -4cd/(ab-cd), t_eff = ab/(cd-ab), t_eff=-1 <=> cd=0 (300 points)', bad, 0)
    bad = 0
    for _ in range(100):
        al, be = Fr(rng.randint(-9, 9), rng.randint(1, 5)), Fr(rng.randint(-9, 9), rng.randint(1, 5))
        a, b, c, d = al, be, Fr(1), 1 + al * be
        if c * d - a * b == 0:
            continue
        bad += a * b / (c * d - a * b) != al * be
    expect('I3 HOST(alpha,beta) = [[1, alpha q],[beta/q, 1+alpha beta]] has t_eff = alpha*beta', bad, 0)
    # I4 coupled singular pencil
    Na = [[lambda qa, qb: 1, lambda qa, qb: qb + qa], [lambda qa, qb: 1 / qb - 1 / qa, lambda qa, qb: 1]]
    qa, qb = PTS[0]
    N = ev(Na, qa, qb)
    Sa = ev(Na, -qa, qb)
    Sb = ev(Na, qa, -qb)
    Sab = ev(Na, -qa, -qb)
    Ea = [[(w + x) / 2 for w, x in zip(r, s)] for r, s in zip(N, Sa)]
    E0 = [[(w + x + y + z) / 4 for w, x, y, z in zip(r, s, t, u)] for r, s, t, u in zip(N, Sa, Sb, Sab)]
    expect('I4 coupled block: det E_a, det E_0, o_a, o_b', (det(Ea), det(E0), o(Na, 'a'), o(Na, 'b')), (0, 1, 2, 2))
    # I5 isotropic kernel
    A, B = Fr(1, 2), Fr(1, 3)
    Cw = [[lambda qa, qb: A + B * qa ** 2 * qb ** 2]]
    Mono = [[lambda qa, qb: qa * qb]]
    expect('I5 C_{qa+qb} = a + b qa^2 qb^2: (o_a, o_b); monomial qa qb: (o_a, o_b)',
           (o(Cw, 'a'), o(Cw, 'b'), o(Mono, 'a'), o(Mono, 'b')), (0, 0, 1, 1))
    # I6 q-free coupling keeps m_a = 2
    P = [[1, 2, 0, 1], [0, 1, 1, 0], [3, 0, 1, 0], [0, 0, 1, 1]]
    P = [[Fr(x) for x in r] for r in P]
    Pi = inv(P)
    qa, qb = PTS[0]

    def W(qa, qb):
        T = [[Fr(0)] * 4 for _ in range(4)]
        T[0][0] = T[1][1] = 1 / qa
        T[2][2] = T[3][3] = 1 / qb
        return mul(mul(Pi, T), P)
    Wn, Ws = W(qa, qb), W(-qa, qb)
    R = mul(Ws, inv(Wn))
    expect('I6 coupled target: dim ker(R_a + I), rank(R_a - I)', (4 - rank(add(R, eye(4))), rank(add(R, eye(4), -1))), (2, 2))
    # I7 the merged plane M45
    bad = 0
    for q in [Fr(7, 3), Fr(-5, 2), Fr(11, 13)]:
        M45 = [[Fr(1), -q], [1 / q, Fr(1)]]
        Uq = [[Fr(1), -q], [Fr(0), Fr(1)]]
        Lq = [[Fr(1), Fr(0)], [1 / q, Fr(1)]]
        H = [[Fr(1), -q], [1 / q, Fr(0)]]
        Jq = [[Fr(0), -q], [1 / q, Fr(0)]]
        bad += add(add(Uq, Lq), eye(2), -1) != M45
        bad += mul(Lq, Uq) != H
        S = [[Fr(1), q], [-1 / q, Fr(1)]]
        R = mul(S, inv(M45))
        bad += rank(add(R, eye(2), -1)) != 2
        bad += mul(R, R) != [[-1, 0], [0, -1]]
        M2 = mul(M45, M45)
        bad += M2 != [[2 * x for x in r] for r in Jq]
        bad += mul(M2, M2) != [[-4, 0], [0, -4]]
        bad += det(M45) != 2
        bad += mul([[Fr(1), Fr(0)], [Fr(0), Fr(1, 2)]], M45) != [[Fr(1), -q], [1 / (2 * q), Fr(1, 2)]]
        HM = mul(H, inv(M45))
        bad += HM != [[1, 0], [1 / (2 * q), Fr(1, 2)]]
        SHM = [[Fr(1), Fr(0)], [-1 / (2 * q), Fr(1, 2)]]
        bad += rank(add(mul(SHM, inv(HM)), eye(2), -1)) != 1
    expect('I7 M45 = U+L-I, H = L U, o = 2, R^2 = -I, M^2 = 2J, M^4 = -4I, det 2, diag(1,1/2)M = HOST(-1,1/2), o(H M^-1) = 1', bad, 0)
    # HOST(-1, 1/2) has t = -1/2
    expect('I7 t_eff(M45) via I3 (a=-1,b=1,c=d=1)', Fr(-1) * 1 / (1 * 1 - Fr(-1) * 1), Fr(-1, 2))
    # I8 dressing invariance
    bad = ctrl = 0
    for _ in range(200):
        q = Fr(rng.randint(1, 9), rng.randint(1, 9)) * rng.choice([1, -1])
        rnd = lambda: Fr(rng.randint(-5, 5), rng.randint(1, 4))
        while True:
            A = [[rnd(), rnd()], [rnd(), rnd()]]
            B = [[rnd(), rnd()], [rnd(), rnd()]]
            c, d, a, b = rnd(), rnd(), rnd(), rnd()
            if det(A) and det(B) and c * d - a * b:
                break
        N = [[c, a * q], [b / q, d]]
        S = [[c, -a * q], [-b / q, d]]
        R = mul(S, inv(N))
        ANB, sANB = mul(mul(A, N), B), mul(mul(A, S), B)
        R2 = mul(sANB, inv(ANB))
        bad += R2 != mul(mul(A, R), inv(A))
        # control: q-odd dressing A' = [[1, q],[0,1]] (sigma(A') != A')
        Ao, sAo = [[Fr(1), q], [Fr(0), Fr(1)]], [[Fr(1), -q], [Fr(0), Fr(1)]]
        R3 = mul(mul(sAo, S), inv(mul(Ao, N)))
        ctrl += (R3[0][0] + R3[1][1]) != (R[0][0] + R[1][1])
    expect('I8 R(ANB) = A R(N) A^-1 for sigma-fixed A,B (200)', bad, 0)
    say('ok  I8 control: q-odd dressing changes tr R on %d/200' % ctrl)
    if ctrl < 100:
        raise SystemExit('FAIL I8 control too weak')
    # I9 b-family
    bad = 0
    for b in [Fr(1), Fr(1, 2), Fr(-1, 2), Fr(-2), Fr(1, 1000), Fr(1, 10 ** 6), Fr(-2, 3)]:
        C = [[Fr(1), Fr(-1)], [Fr(1), b]]
        t = C[0][1] * C[1][0] / det(C)
        bad += t != -1 / (1 + b)
        for g1, g2 in [(Fr(2), Fr(3)), (Fr(-1, 5), Fr(7))]:
            for Cg in (mul([[g1, 0], [0, g2]], C), mul(C, [[g1, 0], [0, g2]])):
                bad += Cg[0][1] * Cg[1][0] / det(Cg) != t
                bad += Cg[0][0] * Cg[1][1] / det(Cg) != 1 + t
    expect('I9 b-family t = -1/(1+b), gauge-invariant t and 1+t (7 b values x 4 gauges)', bad, 0)
    expect('I9 table t at b = 1, 1/2, -1/2, -2', [str(-1 / (1 + b)) for b in [Fr(1), Fr(1, 2), Fr(-1, 2), Fr(-2)]],
           ['-1/2', '-2/3', '-2', '1'])
    C0 = [[Fr(1), Fr(-1)], [Fr(1), Fr(0)]]
    expect('I9 b = 0 (t = -1): t, zero diagonal entry', (C0[0][1] * C0[1][0] / det(C0), C0[1][1]), (-1, 0))
    expect('I9 window scalar |(1+b)/b| at b = 1, 1/2, -1/2, -2, 1e-3, 1e-6 (simple pole at b = 0)',
           [str(abs((1 + b) / b)) for b in [Fr(1), Fr(1, 2), Fr(-1, 2), Fr(-2), Fr(1, 1000), Fr(1, 10 ** 6)]],
           ['2', '3', '1', '1/2', '1001', '1000001'])
    say('PASS_ODD_UNIT_PER_GRADING')


if __name__ == '__main__':
    main()
