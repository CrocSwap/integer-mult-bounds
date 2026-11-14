"""P104 t = -1: counterexample to the literal "neutral period" wording of premise PA (Lemma A, law 5).

Standard library only, exact rational arithmetic. See ADDENDUM.md.

Design ("wasted line contamination" on the sigma-anchor schedule). One early cell (sigma(t), t) per column on a
perfect partner matching sigma; every other cell settled. Change one thing per column t: before its snapshot, Y_t
visits the line of a partner source s(t) != sigma(t) and takes -Z_ts x_s from a PURE X_s (through a two-read window
W_ts). Y_t is then snapshotted, O_t = Y_t = y_t - Z_ts x_s (owned COPY, unmoved, free), and parked (Y_t -= O_t);
the early relay re-adds O_t. So every column's atom leaves while Y_t holds public x-charge: N_neutral = 0. No owned
register is moved: N_owned = 0 owned units. The literal law-5 bound is then D >= n - r = 96 on E8/P104.

Checked:
  (a) the witness formula D(sigma, s) (exact, over Q) equals the full frame-free simulation (all registers
      written out, D = rank(arrivals + targets) - rank(arrivals), Y exact) on random A3/A4 designs in the
      modes clean / x-contaminated / co-read;
  (b) E8/P104 (Gram from the pinned PR968 file): settled D = 96, clean sigma anchors D = 0 (agrees with law 1's
      corrected_law), and the contaminated design with every one of the 104 columns contaminated by sources
      concentrated on few partners gives D = 7 (7 sources, seeded greedy map), D = 9 (9 sources) and D = 5
      (5 sources, deterministic greedy cover), all < 96: the literal bound fails;
  (c) controls: contamination by the sigma cell itself (s(t) = sigma(t)) gives D = 96, and contamination
      through an injective second matching gives D = 96 (contamination is not harmless in general; it is charged
      per distinct source); the empirical law D <= rho_K(sources) holds on every E8 design run here.
Prints PASS_T1_COUNTEREXAMPLE."""
import hashlib, itertools, os, random, sys
from fractions import Fraction as Fr

sys.setrecursionlimit(10000)
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
    piv = {}
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
    """A_m toy (same as charge_law.py): n, G, B (roots in a basis), C (L deposit coefficients), Z."""
    pairs = list(itertools.combinations(range(m + 1), 2))
    roots = [[(1 if k == i else -1 if k == j else 0) for k in range(m + 1)] for i, j in pairs]
    n = len(roots)
    G = [[sum(a * b for a, b in zip(roots[s], roots[t])) for t in range(n)] for s in range(n)]
    B = [[Fr(r[k]) for k in range(m)] for r in roots]
    IJ = [[Fr(1 + (a == b)) for b in range(m)] for a in range(m)]
    C = [[sum(B[t][a] * IJ[a][j] for a in range(m)) / 2 for j in range(m)] for t in range(n)]
    for s in range(n):
        for t in range(n):
            assert sum(C[s][j] * B[t][j] for j in range(m)) == Fr(G[s][t], 2)
    Z = {(s, t): Fr(G[s][t], 2) for s in range(n) for t in range(n) if s != t and G[s][t] % 2}
    return n, G, B, C, Z


def load_e8():
    path = os.path.join(ROOT, PR968)
    raw = open(path, 'rb').read()
    expect('SHA256 of %s' % PR968, hashlib.sha256(raw).hexdigest(), PR968_SHA256)
    L = raw.decode().split('\n')
    Dr = [[int(x) for x in l[3:].split()] for l in L if l.startswith(' d:')]
    Tr = [[int(x) for x in l[3:].split()] for l in L if l.startswith(' t:')]
    n = len(Dr[0])
    return n, [[sum(Dr[k][i] * Tr[k][j] for k in range(8)) // 2 for j in range(n)] for i in range(n)]


def zcells(n, G):
    return {(p, t): Fr(G[p][t], 2) for p in range(n) for t in range(n) if p != t and G[p][t] % 2}


def partners(n, Z):
    return [[s for s in range(n) if (t, s) in Z] for t in range(n)]


def matching(n, part, rng, forbid=None):
    """Perfect partner matching column t -> row sigma(t) (augmenting paths), avoiding forbid[t]."""
    forbid = forbid or {}
    match, rowof = {}, {}

    def aug(t, seen):
        cand = [p for p in part[t] if p != forbid.get(t)]
        rng.shuffle(cand)
        for p in cand:
            if p in seen:
                continue
            seen.add(p)
            if p not in rowof or aug(rowof[p], seen):
                match[t] = p
                rowof[p] = t
                return True
        return False
    for t in range(n):
        if not aug(t, set()):
            raise SystemExit('FAIL no perfect matching')
    return match


# ---------------------------------------------------------------------------------------------- witness formula
def witness_D(n, Z, K, sig, pre, cr=None):
    """Exact D for the sigma-anchor design with contaminated snapshots.
    Witness = (a on x, b = K beta on y, theta on tokens). Row p: a_p + sum_t Z_pt rho_pt = 0 with
    rho_pt = a_t (settled) or b_t - sum_{s in pre_t minus cr_t} Z_ts a_s (early, p = sig[t]).
    Window tokens force sum_{s in pre_t minus cr_t} Z_ts a_s = 0 on the early relay token.
    D = dim(witnesses) - dim(trivial witnesses a = b, all relay tokens 0) = rank(M + extra) - rank(M)."""
    cr = cr or {}
    d = len(K)
    M = []
    for p in range(n):
        row = {p: Fr(1)}
        for t in range(n):
            z = Z.get((p, t))
            if not z:
                continue
            if sig.get(t) == p:
                for j in range(d):
                    if K[j][t]:
                        row[n + j] = row.get(n + j, 0) + z * K[j][t]
                for s in pre.get(t, ()):
                    if s not in cr.get(t, ()):
                        row[s] = row.get(s, 0) - z * Z[(t, s)]
            else:
                row[t] = row.get(t, 0) + z
        M.append(row)
    extra = []
    for p in range(n):
        row = {p: Fr(1)}
        for j in range(d):
            if K[j][p]:
                row[n + j] = -K[j][p]
        extra.append(row)
    for t in sig:
        row = {}
        for s in pre.get(t, ()):
            if s not in cr.get(t, ()):
                row[s] = row.get(s, 0) + Z[(t, s)]
        if row:
            extra.append(row)
    return rank(M + extra) - rank(M)


# ---------------------------------------------------------------------------------------------- full simulation
def simulate(m, mode, S, sig, first):
    """Every register written out (frame-free, exact). Modes for columns t in S:
    clean: O_t = y_t; xcont: O_t = Y_t after window (t, first[t]) completed against pure X_s (= y_t - Z_ts x_s);
    coread: as xcont, then O_t += Z_ts X_s (strip). Returns (D, Y exact)."""
    n, G, B, C, Z = geometry(m)
    r = m
    reg = {}

    def new(k, v):
        reg[k] = dict(v)

    def add(dst, c, src):
        dd = reg[dst]
        for a, v in list(reg[src].items()):
            nv = dd.get(a, 0) + c * v
            if nv:
                dd[a] = nv
            else:
                dd.pop(a, None)
    X = ['X%d' % p for p in range(n)]
    Y = ['Y%d' % t for t in range(n)]
    for p in range(n):
        new(X[p], {'x%d' % p: Fr(1)})
    for t in range(n):
        new(Y[t], {'y%d' % t: Fr(1)})
    rel = {(p, t): 'R%d_%d' % (p, t) for (p, t) in Z}
    win = {(t, s): 'W%d_%d' % (t, s) for (t, s) in Z}
    hel = list(rel.values()) + list(win.values())
    for k in hel:
        new(k, {k: Fr(1)})
    U = []
    for j in range(r):
        new('U%d' % j, {})
        new('L%d' % j, {})
        for t in range(n):
            add('U%d' % j, B[t][j], Y[t])
            add('L%d' % j, B[t][j], X[t])
        U.append('U%d' % j)
    for (p, t), R in rel.items():
        add(R, -1, Y[t])                                   # relays lump pure y_t
    for (t, s), W in win.items():
        add(W, -1, Y[s])                                   # windows lump pure y_s
    for t in range(n):
        new('P%d' % t, {})
        add('P%d' % t, 1, Y[t])                            # pure park (keeps Y exact)
    done = set()
    for t in range(n):
        new('O%d' % t, {})
        s = first[t]
        W = win[(t, s)]
        if t in S and mode in ('xcont', 'coread'):
            add(Y[t], Z[(t, s)], W)
            add(W, 1, X[s])                                # X_s still pure
            add(Y[t], -Z[(t, s)], W)
            done.add((t, s))
            add('O%d' % t, 1, Y[t])                        # snapshot y_t - Z_ts x_s
            if mode == 'coread':
                add('O%d' % t, Z[(t, s)], X[s])
        else:
            add('O%d' % t, 1, Y[t])
    for (t, s), W in win.items():
        if (t, s) not in done:
            add(Y[t], Z[(t, s)], W)
            add(W, 1, X[s])
            add(Y[t], -Z[(t, s)], W)
    for (p, t), R in rel.items():
        add(X[p], -Z[(p, t)], R)                           # X reads relays
    for t in range(n):
        for j in range(r):
            add(Y[t], C[t][j], 'L%d' % j)                  # L deposit G/2 x
        add(Y[t], -1, 'P%d' % t)
    for (p, t), R in rel.items():
        add(R, 1, 'O%d' % t if p == sig[t] else Y[t])      # early re-add O_t, settled re-add Y_t final
    yok = all(reg[Y[t]] == {'x%d' % t: Fr(1)} for t in range(n))
    T = [{'x%d' % p: Fr(1), 'y%d' % p: Fr(-1)} for p in range(n)] + [{h: Fr(1)} for h in hel]
    arr = [reg[v] for v in X + hel] + [reg[u] for u in U]
    return rank(arr + T) - rank(arr), yok


def section_crossval():
    say('== (a) witness formula = full simulation on A3/A4')
    tot = 0
    for m, seeds in ((3, 12), (4, 6)):
        n, G, B, C, Z = geometry(m)
        part = partners(n, Z)
        K = nullspace([[Fr(x) for x in r] for r in G])
        seen = set()
        for seed in range(seeds):
            rng = random.Random(seed)
            sig = matching(n, part, rng)
            S = set(rng.sample(range(n), rng.randint(1, n)))
            first = {t: rng.choice(part[t]) for t in range(n)}
            for mode in ('clean', 'xcont', 'coread'):
                d1, yok = simulate(m, mode, S, sig, first)
                pre = {t: [first[t]] for t in S} if mode != 'clean' else {}
                cr = {t: [first[t]] for t in S} if mode == 'coread' else {}
                d2 = witness_D(n, Z, K, sig, pre, cr)
                if d1 != d2 or not yok:
                    raise SystemExit('FAIL A%d seed %d %s: sim %d formula %d Yexact %s' % (m, seed, mode, d1, d2, yok))
                seen.add((mode, d1))
                tot += 1
        say('ok  A%d: formula = simulation, Y exact, on %d designs; (mode, D) seen %s'
            % (m, 3 * seeds, sorted(x for x in seen)))
    if not any(mode == 'xcont' and d > 0 for mode, d in seen):
        raise SystemExit('FAIL control: x-contamination never changed D on the toys')
    expect('cross-validated designs', tot, 54)


def rho_K(K, S):
    return rank([{j: K[j][s] for j in range(len(K)) if K[j][s]} for s in sorted(S)]) if S else 0


def section_e8():
    say('== (b) E8 / P104: every column contaminated, D far below the literal bound')
    n, G = load_e8()
    expect('ports', n, 104)
    Z = zcells(n, G)
    part = partners(n, Z)
    expect('partners per port', sorted({len(v) for v in part}), [48])
    K = nullspace([[Fr(x) for x in r] for r in G])
    r = n - len(K)
    expect('rank G', r, 8)
    expect('settled: D', witness_D(n, Z, K, {}, {}), 96)
    sig = matching(n, part, random.Random(1))
    expect('sigma is a perfect partner matching', sorted(sig.values()) == list(range(n))
           and all((sig[t], t) in Z for t in range(n)), True)
    expect('clean sigma anchors: D', witness_D(n, Z, K, sig, {}), 0)
    # contamination sources concentrated on few partners: greedy cover, smallest index on ties
    cover = {s: {t for t in range(n) if (t, s) in Z and sig[t] != s} for s in range(n)}
    S, left = [], set(range(n))
    while left:
        s = max(range(n), key=lambda x: (len(cover[x] & left), -x))
        S.append(s)
        left -= cover[s]
    src = {t: min(s for s in S if t in cover[s]) for t in range(n)}
    pre = {t: [src[t]] for t in range(n)}
    expect('every column contaminated (N_neutral = 0), s(t) partner of t, s(t) != sigma(t)',
           all((t, src[t]) in Z and src[t] != sig[t] for t in range(n)) and len(pre) == n, True)
    lit = n - r - 0 - 0
    expect('literal law-5 bound n - r - N_neutral - N_owned', lit, 96)
    for seed, want in ((0, 7), (29, 9)):
        # seeded greedy-few map (each column reuses an already-used source when it can); the LEMMAA schedule
        rng = random.Random(seed)
        s7 = {}
        order = list(range(n))
        rng.shuffle(order)
        for t in order:
            cand = [x for x in part[t] if x != sig[t]]
            used = [x for x in cand if x in s7.values()]
            s7[t] = rng.choice(used) if used else rng.choice(cand)
        expect('greedy-few seed %d: all 104 columns contaminated, distinct sources' % seed,
               (len(s7), len(set(s7.values()))), (n, want))
        D7 = witness_D(n, Z, K, sig, {t: [v] for t, v in s7.items()})
        expect('greedy-few seed %d: D (literal bound 96)' % seed, D7, want)
        expect('D <= rho_K(sources)', D7 <= rho_K(K, set(s7.values())), True)
    expect('deterministic greedy cover: distinct sources', len(set(src.values())), 5)
    D = witness_D(n, Z, K, sig, pre)
    expect('deterministic greedy cover: D (literal bound 96)', D, 5)
    if not D < lit:
        raise SystemExit('FAIL: no counterexample')
    expect('D <= rho_K(sources)', D <= rho_K(K, set(src.values())), True)
    say('    cover sources %s; rho_K = %d' % (sorted(set(src.values())), rho_K(K, set(src.values()))))
    say('== (c) controls on E8: contamination does cost when sources spread')
    preline = {t: [sig[t]] for t in range(n)}
    expect('contamination by the sigma cell itself: D', witness_D(n, Z, K, sig, preline), 96)
    sig2 = matching(n, part, random.Random(2), forbid=sig)
    expect('second matching injective, avoids sigma', len(set(sig2.values())) == n
           and all(sig2[t] != sig[t] for t in range(n)), True)
    D2 = witness_D(n, Z, K, sig, {t: [sig2[t]] for t in range(n)})
    expect('contamination through an injective second matching: D', D2, 96)
    expect('D <= rho_K(sources) (second matching)', D2 <= rho_K(K, set(sig2.values())), True)


if __name__ == '__main__':
    section_crossval()
    section_e8()
    say('PASS_T1_COUNTEREXAMPLE')
