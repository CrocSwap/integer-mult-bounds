"""P104 t = -1 laws 1 and 5 (part): the charge law, the corrected anchored deficiency law and Y-atom counting.

Standard library only, exact rational arithmetic. Contract per port: M = [[1,-1],[1,0]], X = x - y, Y = x.

Geometry A_m (toy): ports q_ij = e_i + e_j + e_{m+1} in F2^(m+2), roots e_i - e_j, G = Gram of the roots (rank m),
partner cells (p,t) = {p != t, G_pt odd}, Z = G/2 - I on partner cells. E8/P104: the Gram of the 104 live lines
D T^T / 2 of the PR968 decoder file research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt
(SHA256 pinned below).

Relay model (frame-free exact algebra, the d = 0 MONOHUB relay family): owned U = rows sum_t B_tj Y_t (product
-G/2), owned L = rows sum_s B_sj X_s; every partner cell (p,t) has a relay R_pt (lump -y_t, read by X_p, re-add)
and an L-side helper H_tp; cell (p,t) in the early set E re-adds a parked owned copy O_t of pure y_t, every other
cell re-adds Y_t^final (settled). D = rank(arrivals + targets) - rank(arrivals) at V.

Checked:
  (a) all cells settled: D = n - r (A3: 3, A4: 6) -- GLIFT's charge deficiency;
  (b) the corrected anchored law D = dim{(k,k'): k' in ker G, (I+Z^S)k + Z^E k' = 0} - dim ker G equals the model's
      D on 60 random early sets at A3 and 30 at A4, with Y exact on every run;
  (c) control: the per-cell form dim(ker G cap ker Z^E) disagrees with the model on some of those sets;
  (d) E8/P104: rank G = 8, G^2 = 26 G, 48 partners per port, dim ker G = 96; law (b): all settled D = 96, three
      random perfect partner matchings D = 0; early cells on c columns give D >= 96 - c (printed);
  (e) Y-atom counting: for every column set N at A3 (64) and A4 (1,024), dim{k in ker G : k_N = 0} >= n - r - |N|,
      with equality attained at every |N| <= n - r, and some sets of size n - r not spanning (D > 0).
Prints PASS_T1_CHARGE_LAW."""
import hashlib, itertools, os, random, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PR968 = 'research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt'
PR968_SHA256 = '8e0178db02c14e1b29058cdbdbd50aac22f2b55a1ba21dc82f417610c9932526'


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


def rank(rows):
    """Exact rank of a list of sparse rows {key: Fraction}."""
    piv = {}                                   # pivot key -> normalised row
    r = 0
    for row in rows:
        v = {k: Fr(x) for k, x in row.items() if x}
        while v:
            k = min(v)
            if k in piv:
                c = v[k]
                for kk, xx in piv[k].items():
                    nv = v.get(kk, 0) - c * xx
                    if nv:
                        v[kk] = nv
                    else:
                        v.pop(kk, None)
            else:
                c = v[k]
                piv[k] = {kk: xx / c for kk, xx in v.items()}
                r += 1
                break
    return r


def dense_rank(M):
    return rank([{j: x for j, x in enumerate(row) if x} for row in M])


def nullspace(M):
    """Basis of {v : M v = 0} (M dense list of lists, rationals)."""
    n = len(M[0])
    A = [[Fr(x) for x in row] for row in M]
    pivc = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        A[r] = [x / A[r][c] for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        pivc.append(c)
        r += 1
    free = [c for c in range(n) if c not in pivc]
    out = []
    for f in free:
        v = [Fr(0)] * n
        v[f] = Fr(1)
        for i, c in enumerate(pivc):
            v[c] = -A[i][f]
        out.append(v)
    return out


# ---------------------------------------------------------------------------------------------- geometry
def geometry(m):
    pairs = list(itertools.combinations(range(m + 1), 2))
    roots = [[(1 if k == i else -1 if k == j else 0) for k in range(m + 1)] for i, j in pairs]
    ports = [(1 << i) | (1 << j) | (1 << (m + 1)) for i, j in pairs]
    n = len(roots)
    G = [[sum(a * b for a, b in zip(roots[s], roots[t])) for t in range(n)] for s in range(n)]
    B = [[Fr(r[k]) for k in range(m)] for r in roots]
    IJ = [[Fr(1 + (a == b)) for b in range(m)] for a in range(m)]
    C = [[sum(B[t][a] * IJ[a][j] for a in range(m)) / 2 for j in range(m)] for t in range(n)]
    for s in range(n):
        for t in range(n):
            assert sum(C[s][j] * B[t][j] for j in range(m)) == Fr(G[s][t], 2)
            even_label = bin(ports[s] & ports[t]).count('1') % 2 == 0
            assert (G[s][t] % 2 == 1) == (s != t and even_label)      # partner cells = odd Gram = label pairing
    Z = {(s, t): Fr(G[s][t], 2) for s in range(n) for t in range(n) if s != t and G[s][t] % 2}
    return n, G, B, C, Z


def relay_model(m, E):
    n, G, B, C, Z = geometry(m)
    r = m
    pub, own = {}, {}
    X = ['X%d' % p for p in range(n)]
    Y = ['Y%d' % t for t in range(n)]
    for p in range(n):
        pub[X[p]] = {'x%d' % p: Fr(1)}
    for t in range(n):
        pub[Y[t]] = {'y%d' % t: Fr(1)}
    rel = {k: 'R%d_%d' % k for k in Z}
    hel = {k: 'H%d_%d' % k for k in Z}
    for v in list(rel.values()) + list(hel.values()):
        pub[v] = {v: Fr(1)}

    def reg(a):
        return pub[a] if a in pub else own[a]

    def add(d, c, s):
        dd = reg(d)
        for k, v in list(reg(s).items()):
            nv = dd.get(k, 0) + c * v
            if nv:
                dd[k] = nv
            else:
                dd.pop(k, None)
    U = ['U%d' % j for j in range(r)]
    L = ['L%d' % j for j in range(r)]
    for j in range(r):
        own[U[j]] = {}
        own[L[j]] = {}
        for t in range(n):
            add(U[j], B[t][j], Y[t])
            add(L[j], B[t][j], X[t])
    for (p, t), R in rel.items():
        add(R, -1, Y[t])                                   # relay lump -y_t
    for (t, p), H in hel.items():
        add(H, -1, Y[p])                                   # L-side helper lump
    for t in range(n):
        own['O%d' % t] = {}
        add('O%d' % t, 1, Y[t])                            # parked owned copy of pure y_t (anchor)
    for t in range(n):
        add(Y[t], -1, 'O%d' % t)                           # zero-Y by parking
    for j in range(r):
        for t in range(n):
            add(Y[t], C[t][j], L[j])                       # L deposit G/2 x (charge-neutral)
    for (t, p), H in hel.items():
        add(Y[t], Z[(t, p)], H)                            # L-side give
    for (t, p), H in hel.items():
        add(H, 1, X[p])                                    # receive pure x_p
    for (p, t), R in rel.items():
        add(X[p], -Z[(p, t)], R)                           # X reads relay
    for (p, t), R in rel.items():
        if (p, t) in E:
            add(R, 1, 'O%d' % t)                           # early re-add from the anchor
    for (t, p), H in hel.items():
        add(Y[t], -Z[(t, p)], H)                           # L-side second reads
    for (p, t), R in rel.items():
        if (p, t) not in E:
            add(R, 1, Y[t])                                # settled re-add against Y_t final
    Vregs = X + list(rel.values()) + list(hel.values())
    T = {}
    for p in range(n):
        T[X[p]] = {'x%d' % p: Fr(1), 'y%d' % p: Fr(-1)}
    for v in list(rel.values()) + list(hel.values()):
        T[v] = {v: Fr(1)}
    arr = [pub[v] for v in Vregs] + [own[u] for u in U]
    D = rank(arr + [T[v] for v in Vregs]) - rank(arr)
    yok = all(pub[Y[t]] == {'x%d' % t: Fr(1)} for t in range(n))
    return D, yok


def corrected_law(n, G, Z, E, K):
    """dim{(k, c) : (I + Z^S) k + Z^E K c = 0} - dim ker G."""
    d = len(K)
    M = []
    for p in range(n):
        row = {}
        for u in range(n):
            v = Fr(int(p == u))
            if (p, u) in Z and (p, u) not in E:
                v += Z[(p, u)]
            if v:
                row[u] = v
        for j in range(d):
            v = sum((Z[(p, u)] * K[j][u] for u in range(n) if (p, u) in E), Fr(0))
            if v:
                row[n + j] = v
        M.append(row)
    return (n + d - rank(M)) - d


def percell_form(n, Z, E, K):
    """GLIFT's per-cell extension dim(ker G cap ker Z^E) (control)."""
    d = len(K)
    cols = [[sum((Z[(p, u)] * K[j][u] for u in range(n) if (p, u) in E), Fr(0)) for p in range(n)] for j in range(d)]
    return d - dense_rank(cols)


def section_toys():
    say('== (a)-(c) relay model on A3 and A4')
    total_bad_percell = 0
    for m, trials in ((3, 60), (4, 30)):
        n, G, B, C, Z = geometry(m)
        K = nullspace([[Fr(x) for x in r] for r in G])
        expect('A%d: n, rank G, dim ker G, partner cells' % m, (n, dense_rank(G), len(K), len(Z)),
               {3: (6, 3, 3, 24), 4: (10, 4, 6, 60)}[m])
        D0, yok = relay_model(m, set())
        expect('A%d all cells settled: D = n - r, Y exact' % m, (D0, yok), (n - m, True))
        cells = sorted(Z)
        rng = random.Random(7)
        ok = bad = 0
        hist = {}
        for _ in range(trials):
            E = set(rng.sample(cells, rng.randint(0, len(cells) // 2)))
            D, yok = relay_model(m, E)
            law = corrected_law(n, G, Z, E, K)
            assert yok, 'Y not exact'
            if D != law:
                raise SystemExit('FAIL corrected law: model %d law %d' % (D, law))
            ok += 1
            bad += percell_form(n, Z, E, K) != D
            hist[D] = hist.get(D, 0) + 1
        expect('A%d corrected anchored law = model D on random early sets' % m, ok, trials)
        say('    A%d D histogram %s; per-cell form wrong on %d/%d' % (m, dict(sorted(hist.items())), bad, trials))
        total_bad_percell += bad
    if total_bad_percell == 0:
        raise SystemExit('FAIL control: per-cell form never disagreed')
    say('ok  control: per-cell form dim(ker G cap ker Z^E) disagrees on %d/90 sets (misses k outside ker G)' % total_bad_percell)


# ---------------------------------------------------------------------------------------------- E8 / P104
def load_e8():
    path = os.path.join(ROOT, PR968)
    raw = open(path, 'rb').read()
    expect('SHA256 of %s' % PR968, hashlib.sha256(raw).hexdigest(), PR968_SHA256)
    L = raw.decode().split('\n')
    Dr = [[int(x) for x in l[3:].split()] for l in L if l.startswith(' d:')]
    Tr = [[int(x) for x in l[3:].split()] for l in L if l.startswith(' t:')]
    n = len(Dr[0])
    g = [[sum(Dr[k][i] * Tr[k][j] for k in range(8)) // 2 for j in range(n)] for i in range(n)]
    return n, g


def section_e8():
    say('== (d) E8 / P104')
    n, G = load_e8()
    expect('ports', n, 104)
    expect('rank G', dense_rank(G), 8)
    G2 = [[sum(G[i][k] * G[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    expect('G^2 = 26 G', all(G2[i][j] == 26 * G[i][j] for i in range(n) for j in range(n)), True)
    Z = {(p, t): Fr(G[p][t], 2) for p in range(n) for t in range(n) if p != t and G[p][t] % 2}
    part = {t: [p for p in range(n) if (p, t) in Z] for t in range(n)}
    expect('partners per port', sorted({len(v) for v in part.values()}), [48])
    K = nullspace([[Fr(x) for x in r] for r in G])
    expect('dim ker G', len(K), 96)
    expect('all cells settled: D', corrected_law(n, G, Z, set(), K), 96)
    rng = random.Random(3)

    def matching(cols):
        for _ in range(5000):
            order = list(cols)
            rng.shuffle(order)
            used, sig = set(), {}
            for t in order:
                c = [p for p in part[t] if p not in used]
                if not c:
                    break
                p = rng.choice(c)
                used.add(p)
                sig[t] = p
            else:
                return sig
        raise SystemExit('no matching found')
    for tr in range(3):
        sig = matching(range(n))
        expect('perfect partner matching %d (one early cell per column): D' % tr,
               corrected_law(n, G, Z, {(sig[t], t) for t in sig}, K), 0)
    for c in (8, 48, 90, 96):
        sig = matching(rng.sample(range(n), c))
        D = corrected_law(n, G, Z, {(sig[t], t) for t in sig}, K)
        if D < 96 - c:
            raise SystemExit('FAIL atom bound at c=%d: D=%d' % (c, D))
        say('ok  early cells on %3d columns: D = %d >= %d' % (c, D, max(0, 96 - c)))


def section_atoms():
    say('== (e) Y-atom counting: dim{k in ker G : k_N = 0} >= n - r - |N|')
    for m in (3, 4):
        n, G, B, C, Z = geometry(m)
        d = n - m
        best = {}
        nonspan = 0
        for mask in range(1 << n):
            N = [i for i in range(n) if mask >> i & 1]
            Cc = [i for i in range(n) if not mask >> i & 1]
            dim = len(Cc) - (dense_rank([[G[i][j] for j in Cc] for i in range(n)]) if Cc else 0)
            if dim < d - len(N):
                raise SystemExit('FAIL atom bound')
            best[len(N)] = min(best.get(len(N), 99), dim)
            nonspan += (len(N) == d and dim > 0)
        expect('A%d min over |N| = 0..%d' % (m, d), [best[k] for k in range(d + 1)], list(range(d, -1, -1)))
        if nonspan == 0:
            raise SystemExit('FAIL control: every (n-r)-set spans')
        say('ok  A%d: %d column sets of size n - r = %d leave D > 0 (not every n - r columns suffice)' % (m, nonspan, d))


if __name__ == '__main__':
    section_toys()
    section_atoms()
    section_e8()
    say('PASS_T1_CHARGE_LAW')
