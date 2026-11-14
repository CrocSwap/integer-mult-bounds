"""P104 method: range-G pre-loads (the owned gauge L' = G (x/2 + mu* y)). Standard library only, exact Fractions.

Geometry: the 104 live lines of E8/P104 with Gram G = D T^T / 2 from the PR968 decoder file
research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt (SHA256 pinned below); rank G = 8, G^2 = lam G with
lam = 26, partners p != t <=> G_pt odd (48 per port), Z = G/2 - I (Z_su = G_su/2 - delta_su).

Model (per column t, contract X = x - y, Y = x as in the T = -1 package): the carrier column is
    Y_t = [y_t anchor] + L'_t + sum_{s partner of t} c_s K_s,   K_s = x_s + sum_u Z_su y_u (COMPLETE junk),
    c_s = -G_ts/2,   L'_t = sum_u G_tu (x_u/2 + mu y_u)   (rank-8 owned rows).
Proof [P]: x-part  G_tu/2 + c_u [u partner] = delta_ut.  y-part for u != t:  mu G_tu - (lam-2)/4 G_tu + G_tu/2, using
sum_{s partner of t} G_ts G_su = (lam - 2) G_tu (the s = t term of G^2 is 2 G_tu); for u = t: 1 + 2 mu - (lam-2)/2.
Both vanish iff mu = mu* = (lam-2)/4 - 1/2 = 11/2.  Legality core [P]: G = (D^T T)/2 so G_t.y = 1/2 sum_k D_kt (T_k.y) is a
combination of the eight owned U rows T_k.y; checked below as an exact identity.
Checked (all 104 columns, Fractions):
  (a) PR968 hash, 104 ports, rank 8, G^2 = 26 G, 48 partners per port, mu* = 11/2;
  (b) gauge mu*: Y_t = x_t with every y cancelled, 0/104 misses, no zero-Y park; owned rank of rows G(x/2 + mu* y) is 8;
  (c) controls: mu = 0 -> 104/104 misses, residual exactly -11/2 G_t on all coordinates (so on every window N_p, all
      104 x 48 (t,p) pairs); zero-Y park with mu* -> 104/104 misses; one partial-junk carrier (20 of its 48 cells) -> 28 missed
      coordinates in every column; wrong mu (mu* + 1/4) -> 104/104 misses;
  (d) closed form: residual y of the mu-family equals (mu - mu*) G_t for the [y_t-anchored] column;
  (e) legality identity G_t.y = 1/2 sum_k D_kt T_k.y on a fixed integer y, all t; and G_t.y with y in span of the 8 U rows.
Prints PASS_METHODS_PRELOAD."""
import hashlib, os, sys, random
from pathlib import Path
from fractions import Fraction as Fr

ROOT = Path(__file__).resolve().parents[2]
PR968 = 'research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt'
PR968_SHA256 = '8e0178db02c14e1b29058cdbdbd50aac22f2b55a1ba21dc82f417610c9932526'


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


def load_e8():
    raw = (ROOT / PR968).read_bytes()
    expect('SHA256 of %s' % PR968, hashlib.sha256(raw).hexdigest(), PR968_SHA256)
    L = raw.decode().split('\n')
    Dr = [[int(x) for x in l[3:].split()] for l in L if l.startswith(' d:')]
    Tr = [[int(x) for x in l[3:].split()] for l in L if l.startswith(' t:')]
    n = len(Dr[0])
    g = [[sum(Dr[k][i] * Tr[k][j] for k in range(8)) // 2 for j in range(n)] for i in range(n)]
    return n, g, Dr, Tr


def rank(M):
    A = [[Fr(x) for x in r] for r in M]
    r = 0
    for c in range(len(A[0])):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        piv = A[r][c]
        A[r] = [x / piv for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        r += 1
    return r


def main():
    n, G, Dr, Tr = load_e8()
    expect('ports', n, 104)
    expect('G symmetric, diag 2', all(G[i][j] == G[j][i] for i in range(n) for j in range(n)) and all(G[i][i] == 2 for i in range(n)), True)
    expect('rank G', rank(G), 8)
    G2 = [[sum(G[i][k] * G[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    lam = 26
    expect('G^2 = 26 G', all(G2[i][j] == lam * G[i][j] for i in range(n) for j in range(n)), True)
    P = [[s for s in range(n) if s != t and G[t][s] % 2] for t in range(n)]
    expect('partners per port', sorted({len(v) for v in P}), [48])
    mu_star = Fr(lam - 2, 4) - Fr(1, 2)
    expect('mu*', mu_star, Fr(11, 2))
    Z = lambda s, u: Fr(G[s][u], 2) - (1 if s == u else 0)

    def column(t, mu, park=False, partial=None):
        """returns (x, y) final content of Y_t."""
        x = [Fr(0)] * n
        y = [Fr(0)] * n
        if not park:
            y[t] += 1
        for u in range(n):
            x[u] += Fr(G[t][u], 2)
            y[u] += mu * G[t][u]
        for s in P[t]:
            c = Fr(-G[t][s], 2)
            x[s] += c
            for u in range(n):
                if partial and s == partial[0] and u not in partial[1]:
                    continue
                y[u] += c * Z(s, u)
        return x, y

    def misses(t, mu, **kw):
        x, y = column(t, mu, **kw)
        return sum(1 for u in range(n) if x[u] != (1 if u == t else 0)) + sum(1 for u in range(n) if y[u] != 0), x, y

    say('== (b) gauge mu*')
    expect('gauge mu*: columns with Y_t != x_t', sum(1 for t in range(n) if misses(t, mu_star)[0]), 0)
    M = [[Fr(G[t][u], 2) for u in range(n)] + [mu_star * G[t][u] for u in range(n)] for t in range(n)]
    expect('owned L rank, rows G(x/2 + mu* y)', rank(M), 8)

    say('== (c) controls')
    bad0 = 0
    resid_ok = True
    for t in range(n):
        m, x, y = misses(t, Fr(0))
        bad0 += 1 if m else 0
        resid_ok &= all(y[u] == -mu_star * G[t][u] for u in range(n))
    expect('control mu = 0: columns missing', bad0, 104)
    expect('control mu = 0: residual = -11/2 G_t on all coords', resid_ok, True)
    wincount = 0
    wok = True
    for t in range(n):
        _, _, y = misses(t, Fr(0))
        for p in P[t]:
            Np = [u for u in range(n) if G[p][u] % 2 == 0]
            wincount += 1
            wok &= all(y[u] == -mu_star * G[t][u] for u in Np) and any(y[u] != 0 for u in Np)
    expect('window N_p residual -11/2 G_t, nonzero, (t,p) pairs', (wok, wincount), (True, 104 * 48))
    expect('control zero-Y park + mu*: columns missing', sum(1 for t in range(n) if misses(t, mu_star, park=True)[0]), 104)
    rng = random.Random(0)
    allmiss = set()
    for t in range(n):
        s = P[t][1]
        cells = set(rng.sample(P[s], 20))
        allmiss.add(misses(t, mu_star, partial=(s, cells))[0])
    expect('control one partial-junk carrier (20/48 cells): miss coords per column', sorted(allmiss), [28])
    expect('control wrong mu = mu* + 1/4: columns missing', sum(1 for t in range(n) if misses(t, mu_star + Fr(1, 4))[0]), 104)

    say('== (d) closed form')
    cf = True
    for mu in (Fr(0), Fr(3), Fr(-7, 3), mu_star):
        for t in (0, 17, 103):
            _, _, y = misses(t, mu)
            cf &= all(y[u] == (mu - mu_star) * G[t][u] for u in range(n))
    expect('residual y = (mu - mu*) G_t', cf, True)

    say('== (e) legality core')
    rg = random.Random(5)
    yv = [rg.randint(-9, 9) for _ in range(n)]
    Urows = [sum(Tr[k][u] * yv[u] for u in range(n)) for k in range(8)]
    ok = all(sum(G[t][u] * yv[u] for u in range(n)) == Fr(1, 2) * sum(Dr[k][t] * Urows[k] for k in range(8)) for t in range(n))
    expect('G_t.y = 1/2 sum_k D_kt (T_k.y), all t', ok, True)
    rows_y = [[Fr(Tr[k][u]) for u in range(n)] for k in range(8)]
    expect('rank of the 8 owned U rows', rank(rows_y), 8)
    expect('G rows lie in span of the U-row coefficient vectors (rank [T;G])', rank(rows_y + [[Fr(x) for x in r] for r in G]), 8)
    say('PASS_METHODS_PRELOAD')


if __name__ == '__main__':
    main()
