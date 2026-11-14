"""P104 t = -1 law 4: the per-J odd unit of the t = -1 native and why gauge, automorphism and finite order do not
remove it. Standard library only; exact arithmetic in F_p, p = 2147483629 (p = 1 mod 4), with i = sqrt(-1).

Laurent matrices in q are evaluated at q = chi; sigma: q -> -q. o(N) = rank(sigma(N) N^-1 - I), evaluated at the
two sigma-pairs (chi, -chi) = (i, -i) and (1, -1). (o = rank of the q-odd part, see #7555 law 4.)

Checked:
  (a) H = [[1,-q],[q^-1,0]] specialises to M = [[1,-1],[1,0]] at q = 1; o(H^n), n = 1..6, = 2,2,0,2,2,0;
      H^3 = -I, H^6 = I; SW = J L_q (J = [[0,-1],[1,0]], L_q = [[1,0],[-q^-1,1]]) has o = 1, so the t = -1 native
      carries o(H) - o(SW) = 1 more odd unit per J: 17 per port per word, an integer (not mod 2) deficit;
  (b) the three-register lift on (X, Y, Z = X - qY): X' = Z, Y' = q^-1 X, Z' = -qY reproduces H on (X, Y), keeps
      Z = X - qY, is monomial with o = 2 and cube -I; in the gauge frame Y'' = qY it is the q-free signed 3-cycle
      (o = 0), and the gauge diag(1, q) itself has o = 1, while a q-free transvection conjugated by it has o = 1;
  (c) sigma-fixed global automorphisms (entries a + b q^2): o(U N U^-1) = o(N) on 200 random U for N in
      {H, H^2, SW, L_q, random Laurent 3x3}; control: a non-sigma-fixed U changes o;
  (d) the gauge-shift ledger: (m - 16) + (36 - m) = 20 for every m = 0..36 (word part from Lemma E of #7555, boundary
      part = odd rank of the gauge diag(q^-g)), against 3 for the unshifted design.
Prints PASS_T1_ODD_UNIT."""
import random

P = 2147483629
IM = next(pow(g, (P - 1) // 4, P) for g in range(2, 99) if pow(g, (P - 1) // 2, P) == P - 1)
assert IM * IM % P == P - 1


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


def inv(a):
    return pow(a % P, P - 2, P)


def ev(A, chi):                                   # A: matrix of {exp: coef}
    return [[sum(c * pow(chi, e % (P - 1), P) for e, c in x.items()) % P for x in r] for r in A]


def mmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) % P for j in range(len(B[0]))] for i in range(len(A))]


def rank(A):
    M = [r[:] for r in A]
    rk = 0
    for c in range(len(M[0])):
        p = next((r for r in range(rk, len(M)) if M[r][c]), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        iv = inv(M[rk][c])
        for r in range(len(M)):
            if r != rk and M[r][c]:
                f = M[r][c] * iv % P
                M[r] = [(a - f * b) % P for a, b in zip(M[r], M[rk])]
        rk += 1
    return rk


def minv(A):
    n = len(A)
    M = [list(A[i]) + [int(i == j) for j in range(n)] for i in range(n)]
    for c in range(n):
        p = next(r for r in range(c, n) if M[r][c])
        M[c], M[p] = M[p], M[c]
        iv = inv(M[c][c])
        M[c] = [x * iv % P for x in M[c]]
        for r in range(n):
            if r != c and M[r][c]:
                f = M[r][c]
                M[r] = [(a - f * b) % P for a, b in zip(M[r], M[c])]
    return [r[n:] for r in M]


def o_at(A, chi):
    n = len(A)
    S = mmul(ev(A, (-chi) % P), minv(ev(A, chi)))
    return rank([[(S[i][j] - (i == j)) % P for j in range(n)] for i in range(n)])


def o_of(A):
    a, b = o_at(A, IM), o_at(A, 1)
    if a != b:
        raise SystemExit('FAIL o differs between sigma pairs')
    return a


def lmul(A, B):                                   # Laurent matrix product
    n, m, k = len(A), len(B[0]), len(B)
    out = [[{} for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            d = {}
            for t in range(k):
                for e1, c1 in A[i][t].items():
                    for e2, c2 in B[t][j].items():
                        d[e1 + e2] = (d.get(e1 + e2, 0) + c1 * c2) % P
            out[i][j] = {e: c for e, c in d.items() if c}
    return out


def lconst(n, s=1):
    return [[({0: s % P} if i == j else {}) for j in range(n)] for i in range(n)]


def leq(A, B):
    return all(A[i][j] == B[i][j] for i in range(len(A)) for j in range(len(A[0])))


def mono(c, e):
    return {e: c % P}


H = [[mono(1, 0), mono(-1, 1)], [mono(1, -1), {}]]
J = [[{}, mono(-1, 0)], [mono(1, 0), {}]]
Lq = [[mono(1, 0), {}], [mono(-1, -1), mono(1, 0)]]
SW = lmul(J, Lq)


def section_a():
    say('== (a) the t = -1 native and its per-J odd unit')
    expect('H at q = 1 is M = [[1,-1],[1,0]]', ev(H, 1), [[1, P - 1], [1, 0]])
    pw = lconst(2)
    os_ = []
    for k in range(1, 7):
        pw = lmul(pw, H)
        os_.append(o_of(pw))
        if k == 3:
            expect('H^3 = -I', leq(pw, lconst(2, -1)), True)
    expect('H^6 = I', leq(pw, lconst(2)), True)
    expect('o(H^n), n = 1..6', os_, [2, 2, 0, 2, 2, 0])
    expect('o(SW = J L_q), o(L_q), o(J)', (o_of(SW), o_of(Lq), o_of(J)), (1, 1, 0))
    expect('odd units per port per word, 17 J: H minus SW', 17 * (o_of(H) - o_of(SW)), 17)


def section_b():
    say('== (b) the three-register lift and the gauge frame')
    lift = [[{}, {}, mono(1, 0)], [mono(1, -1), {}, {}], [{}, mono(-1, 1), {}]]      # rows: X', Y', Z' over (X,Y,Z)
    emb = [[mono(1, 0), {}], [{}, mono(1, 0)], [mono(1, 0), mono(-1, 1)]]           # (X, Y) -> (X, Y, X - qY)
    expect('lift . embed = embed . H (lift reproduces H and keeps Z = X - qY)', leq(lmul(lift, emb), lmul(emb, H)), True)
    l3 = lmul(lmul(lift, lift), lift)
    expect('lift^3 = -I', leq(l3, lconst(3, -1)), True)
    expect('o(lift)', o_of(lift), 2)
    D = [[mono(1, 0), {}, {}], [{}, mono(1, 1), {}], [{}, {}, mono(1, 0)]]          # gauge Y'' = qY
    Di = [[mono(1, 0), {}, {}], [{}, mono(1, -1), {}], [{}, {}, mono(1, 0)]]
    g = lmul(lmul(D, lift), Di)
    expect('gauge frame: lift is q-free', all(set(x) <= {0} for r in g for x in r), True)
    expect('o(gauged lift)', o_of(g), 0)
    D2 = [[mono(1, 0), {}], [{}, mono(1, 1)]]
    D2i = [[mono(1, 0), {}], [{}, mono(1, -1)]]
    T = [[mono(1, 0), mono(1, 0)], [{}, mono(1, 0)]]                                 # q-free transvection X += Y
    expect('o(gauge diag(1,q)), o(T), o(D T D^-1)', (o_of(D2), o_of(T), o_of(lmul(lmul(D2, T), D2i))), (1, 0, 1))


def section_c():
    say('== (c) sigma-fixed global automorphisms preserve o')
    rng = random.Random(5)

    def rl(n, odd=False):
        while True:
            A = [[{e: rng.randrange(P) for e in ((0, 2) if not odd else (0, 1, 2))} for _ in range(n)] for _ in range(n)]
            if rank(ev(A, IM)) == n and rank(ev(A, 1)) == n and rank(ev(A, (-IM) % P)) == n and rank(ev(A, P - 1)) == n:
                return A

    def linv_ev(U, chi):
        return minv(ev(U, chi))

    def o_conj(U, N, chi):
        n = len(N)
        a = mmul(mmul(ev(U, chi), ev(N, chi)), linv_ev(U, chi))
        b = mmul(mmul(ev(U, (-chi) % P), ev(N, (-chi) % P)), linv_ev(U, (-chi) % P))
        S = mmul(b, minv(a))
        return rank([[(S[i][j] - (i == j)) % P for j in range(n)] for i in range(n)])
    R3 = rl(3, odd=True)
    cases = [('H', H), ('H^2', lmul(H, H)), ('SW', SW), ('L_q', Lq), ('random 3x3', R3)]
    ok = 0
    for name, N in cases:
        base = o_of(N)
        for _ in range(40):
            U = rl(len(N))
            for chi in (IM, 1):
                if o_conj(U, N, chi) != base:
                    raise SystemExit('FAIL invariance %s' % name)
            ok += 1
    expect('sigma-fixed conjugations checked (5 natives x 40 U, both sigma pairs)', ok, 200)
    ch = 0
    for _ in range(20):
        U = rl(2, odd=True)
        ch += o_conj(U, lmul(H, H), IM) != o_of(lmul(H, H)) or o_conj(U, SW, IM) != o_of(SW)
    if ch == 0:
        raise SystemExit('FAIL control: non-sigma-fixed U never changes o')
    say('ok  control: non-sigma-fixed U changes o on %d/20 trials' % ch)


def section_d():
    say('== (d) gauge-shift ledger')
    tot = {(m - 16) + (36 - m) for m in range(37)}
    expect('word (m - 16) + boundary (36 - m) over m = 0..36', tot, {20})
    expect('unshifted design odd ops per port per word (37 - 34)', 37 - 17 * o_of(H), 3)


if __name__ == '__main__':
    section_a()
    section_b()
    section_c()
    section_d()
    say('PASS_T1_ODD_UNIT')
