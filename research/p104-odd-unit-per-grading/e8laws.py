"""E8/P104 structural laws, exact checker. Standard library only; run as `python3 -I -B e8laws.py` from any cwd.

Data: data/lines120.json (120 E8 lines, first 104 = P104 ports; F2^9 labels + integer Gram), data/iso968.json (PR968
isomorphism), data/ports_B.json (the 8 non-D ports of the #7546 hosted word, as labels), data/half18_frames.json (HALF18
frame partitions). Label convention: odd cell (t,s) <=> dot(q_t,q_s)=1 <=> G_ts even (so every diagonal cell is odd,
q.q = 1; G_ts = +-1 <=> dot = 0 off the diagonal).
All arithmetic is exact (ints, Fractions, Bareiss ranks over Z). Sections:
  0 data + PR968 isomorphism      5 HALF18  frame partitions (E8 rank 15, P104 rank 13)
  1 HANDT1  G^2=26G, twin, -12 I  6 EARLYCAP rank/Frobenius cap, T1CANCEL res=0
  2 XRECALL/XBIRTH geometry       7 BYPASS  rank_K{e_t} = 95
  3 LIFTTD  orthogonal sets/cliques 8 FACTORSWAP exactly 10 rank-8 decompositions
  4 XDEC    joint-decoder rank 8k  9 H9CERT Lemma A (acyclic) toy
Prints PASS_E8_LAWS."""
import hashlib, json, random, itertools, time
from pathlib import Path
from fractions import Fraction as Fr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR968 = 'research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt'
PR968_SHA256 = '8e0178db02c14e1b29058cdbdbd50aac22f2b55a1ba21dc82f417610c9932526'
SHA = {
    'lines120.json': '4a91033b56fe23feb897b90e6259b33dfbe428ff07ad7ce511a73835074f2708',
    'iso968.json': 'fd3fb6b90918d6802c7b22b7fe2efdf3a3979e4bc50bb610437957a84b702e1f',
    'ports_B.json': '96daa0f02363e2fc1fd1ab5c9098db66eab448d1a588660781dfbcc4b0e1b5f7',
    'half18_frames.json': 'e62a80221d167f59c208fb3ae8b18f5aff739bffa4093e03fe061c08a506a00a',
}
PAIRS = [(117, 107), (114, 106), (111, 108), (104, 110), (115, 109), (112, 119), (105, 118), (116, 113)]  # (d_j, d'_j)
N = 104
P = list(range(N))
T0 = time.time()


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


def dot(a, b):
    return bin(a & b).count('1') & 1


def rank2(vs):
    basis = []
    for v in vs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def span(vs):
    s = {0}
    for v in vs:
        if v not in s:
            s |= {x ^ v for x in s}
    return s


def pairing_rank(Dl, Sl):
    Sl = sorted(set(Sl))
    return rank2([sum(dot(t, s) << i for i, s in enumerate(Sl)) for t in set(Dl)])


def irank(M):
    """exact rank over Q of an integer matrix: fraction-free (Bareiss) elimination with column skipping."""
    A = [[int(x) for x in r] for r in M]
    m = len(A)
    if m == 0:
        return 0
    n = len(A[0])
    r = 0
    prev = 1
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        piv = A[r][c]
        for i in range(r + 1, m):
            ai = A[i]
            f = ai[c]
            ar = A[r]
            for j in range(c + 1, n):
                ai[j] = (piv * ai[j] - f * ar[j]) // prev
            ai[c] = 0
        prev = piv
        r += 1
        if r == m:
            break
    return r


def qrank(M):
    A = [[Fr(x) for x in r] for r in M]
    r = 0
    for c in range(len(A[0]) if A else 0):
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


def nullspace(M):
    A = [[Fr(x) for x in r] for r in M]
    m = len(A[0])
    piv = []
    r = 0
    for c in range(m):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        A[r] = [x / A[r][c] for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        piv.append(c)
        r += 1
    out = []
    for fc in (c for c in range(m) if c not in piv):
        v = [Fr(0)] * m
        v[fc] = Fr(1)
        for i, pc in enumerate(piv):
            v[pc] = -A[i][fc]
        out.append(v)
    return out


def maxclique(adj):
    """exact maximum clique (branch and bound with greedy colouring) on bitmask adjacency; returns (size, members)."""
    n = len(adj)
    best = [0, []]

    def colour(Pm):
        order, col = [], []
        c = 0
        Um = Pm
        while Um:
            c += 1
            Qm = Um
            while Qm:
                v = (Qm & -Qm).bit_length() - 1
                Qm &= ~(1 << v)
                Qm &= ~adj[v]
                Um &= ~(1 << v)
                order.append(v)
                col.append(c)
        return order, col

    def expand(R, Pm):
        order, col = colour(Pm)
        for i in range(len(order) - 1, -1, -1):
            if len(R) + col[i] <= best[0]:
                return
            v = order[i]
            R.append(v)
            NP = Pm & adj[v]
            if NP:
                expand(R, NP)
            elif len(R) > best[0]:
                best[0], best[1] = len(R), R[:]
            R.pop()
            Pm &= ~(1 << v)

    expand([], (1 << n) - 1)
    return best[0], best[1]


def graph(labels, want, idx=None):
    """bitmask graph on `idx` positions (default all): edge i~j (i!=j) iff dot(labels_i,labels_j)==want."""
    idx = list(range(len(labels))) if idx is None else list(idx)
    return [sum(1 << b for b, j in enumerate(idx) if j != i and dot(labels[i], labels[j]) == want) for i in idx]


def selftest():
    rnd = random.Random(1)
    for _ in range(30):
        m, n = rnd.randint(1, 7), rnd.randint(1, 7)
        M = [[rnd.choice((0, 0, 1, -1, 2, 3)) for _ in range(n)] for _ in range(m)]
        assert irank(M) == qrank(M)
    for _ in range(30):
        n = rnd.randint(2, 12)
        E = {(i, j) for i in range(n) for j in range(i + 1, n) if rnd.random() < 0.5}
        adj = [sum(1 << j for j in range(n) if (min(i, j), max(i, j)) in E) for i in range(n)]
        bf = max((len(c) for k in range(1, n + 1) for c in itertools.combinations(range(n), k)
                  if all((a, b) in E for a, b in itertools.combinations(c, 2))), default=0)
        assert maxclique(adj)[0] == bf
    say('ok  self-tests: Bareiss rank == Fraction rank, branch-and-bound clique == brute force (60 random cases)')


def main():
    selftest()
    raws = {f: (HERE / 'data' / f).read_bytes() for f in SHA}
    for f in SHA:
        expect('SHA256 data/' + f, hashlib.sha256(raws[f]).hexdigest(), SHA[f])
    d = json.loads(raws['lines120.json'])
    U, G = d['labels'], d['gram']
    G4 = [r[:N] for r in G[:N]]
    Ul = U[:N]
    odd_off = [(t, s) for t in P for s in P if t != s and dot(U[t], U[s])]
    even_off = [(t, s) for t in P for s in P if t != s and not dot(U[t], U[s])]

    # ------------------------------------------------------------------ 0
    say('== 0. data and PR968 isomorphism')
    expect('120 lines: odd distinct labels, dot = G+1 mod 2 on all 120^2 pairs, G_ts in {0,+-1}, rank 8, G^2=30G',
           (len(set(U)), all(dot(U[i], U[i]) for i in range(120)),
            all(dot(U[i], U[j]) == (G[i][j] + 1) % 2 for i in range(120) for j in range(120)),
            all(G[i][j] in (0, 1, -1) for i in range(120) for j in range(120) if i != j),
            irank(G),
            all(sum(G[i][k] * G[k][j] for k in range(120)) == 30 * G[i][j] for i in range(120) for j in range(120))),
           (120, True, True, True, 8, True))
    raw = (ROOT / PR968).read_bytes()
    expect('SHA256 of PR968 decoder file', hashlib.sha256(raw).hexdigest(), PR968_SHA256)
    ls = raw.decode().split('\n')
    Dr = [[int(x) for x in l[3:].split()] for l in ls if l.startswith(' d:')]
    Tr = [[int(x) for x in l[3:].split()] for l in ls if l.startswith(' t:')]
    GP = [[sum(Dr[k][i] * Tr[k][j] for k in range(8)) // 2 for j in P] for i in P]
    iso = json.loads(raws['iso968.json'])
    perm, eps = iso['perm'], iso['eps']
    expect('PR968 Gram = eps eps G104(perm) on all 104^2 entries',
           all(GP[u][v] == eps[u] * eps[v] * G[perm[u]][perm[v]] for u in P for v in P), True)

    # ------------------------------------------------------------------ 1  HANDT1
    say('== 1. HANDT1: odd cells, G^2 = 26 G, twin decoder, composition residue -12 I')
    expect('q_t.q_t = 1 for all 104 (diagonal odd)', all(dot(U[t], U[t]) == 1 for t in P), True)
    expect('odd off-diagonal cells of P104, all with G=0', (len(odd_off), all(G[t][s] == 0 for t, s in odd_off)), (5720, True))
    expect('even off-diagonal cells, all with G != 0 (G=+-1)',
           (len(even_off), all(G[t][s] in (1, -1) for t, s in even_off)), (4992, True))
    G2 = [[sum(G4[t][k] * G4[k][s] for k in P) for s in P] for t in P]
    expect('G104^2 = 26 G104 exactly', all(G2[t][s] == 26 * G4[t][s] for t in P for s in P), True)
    expect('control: G104^2 != 30 G104 (the 120-line constant), and rank G104 = 8',
           (all(G2[t][s] == 30 * G4[t][s] for t in P for s in P), irank(G4)), (False, 8))
    # G/26 idempotent of trace 8  => G/2 = 13 * proj(range G)
    Pj = [[Fr(G4[t][s], 26) for s in P] for t in P]
    expect('proj = G/26 symmetric, idempotent, trace 8 (so G/2 = 13 proj)',
           (all(sum(Pj[t][k] * Pj[k][s] for k in P) == Pj[t][s] for t in P for s in P), sum(Pj[t][t] for t in P)), (True, 8))
    rows = []
    for dd, dp in PAIRS:
        c = G[dd][dp]
        assert dd >= N and dp >= N and c in (1, -1)
        rows.append(([G[p][dd] for p in P], [c * G[s][dp] for s in P], dd, dp))   # w, u2 = 2u (u = G/(2c))
    expect('UP decoder: sum_k w_k u_k^T = G/2 on all 104^2 cells',
           all(sum(w[t] * u2[s] for w, u2, _, _ in rows) == G4[t][s] for t in P for s in P), True)
    expect('transposed twin L (deposit u_k, gather w_k): M_L = sum u_k w_k^T = G/2 on all 104^2 cells',
           all(sum(u2[t] * w[s] for w, u2, _, _ in rows) == G4[t][s] for t in P for s in P), True)
    leg = all(all(dot(U[t], U[dp]) == 0 for t in P if u2[t]) and all(dot(U[s], U[dd]) == 0 for s in P if w[s])
              for w, u2, dd, dp in rows)
    tight = all({t for t in P if u2[t]} == {t for t in P if dot(U[t], U[dp]) == 0} and
                {s for s in P if w[s]} == {s for s in P if dot(U[s], U[dd]) == 0} for w, u2, dd, dp in rows)
    swapped = sum(1 for w, u2, dd, dp in rows if any(dot(U[s], U[dp]) for s in P if w[s]))
    expect('L rows frame-legal (deposit labels in z^perp for <z> = U[d\'], gather labels in U[d]^perp), supports exactly the perps',
           (leg, tight), (True, True))
    expect('control: gather/deposit frames swapped is illegal on all 8 rows', swapped, 8)
    ip = lambda a, b: sum(x * y for x, y in zip(a, b))
    WU = [[Fr(ip(rows[k][0], rows[j][1]), 2) for j in range(8)] for k in range(8)]
    expect('W^T U = 13 I (8x8)', WU, [[Fr(13) if k == j else Fr(0) for j in range(8)] for k in range(8)])
    UUm = [[Fr(ip(rows[k][1], rows[j][1]), 4) for j in range(8)] for k in range(8)]
    WWm = [[ip(rows[k][0], rows[j][0]) for j in range(8)] for k in range(8)]
    offd = lambda M: any(M[k][j] != 0 for k in range(8) for j in range(8) if k != j)
    expect('U^T U (diag 13) and W^T W (diag 52) are NOT diagonal',
           (offd(UUm), offd(WWm), {UUm[k][k] for k in range(8)}, {WWm[k][k] for k in range(8)}), (True, True, {Fr(13)}, {52}))
    # full composition M_L M_U and M_U M_L (each M = G/2 so 4 M_L M_U = sum_kj u2_k (w_k.w_j) u2_j^T)
    y = [[sum(WWm[k][j] * rows[j][1][s] for j in range(8)) for s in P] for k in range(8)]
    X = [[sum(rows[k][1][t] * y[k][s] for k in range(8)) for s in P] for t in P]       # = 4 M_L M_U
    z = [[sum(UUm[j][k] * 4 * rows[k][0][s] for k in range(8)) for s in P] for j in range(8)]
    X2 = [[sum(rows[j][0][t] * z[j][s] for j in range(8)) for s in P] for t in P]      # = 4 M_U M_L
    for nm, XX in (('M_L after M_U', X), ('M_U after M_L', X2)):
        res_diag = {Fr(1) - Fr(XX[t][t], 4) for t in P}
        odd_nz = sum(1 for t, s in odd_off if XX[t][s] != 0)
        expect('full composition %s: C-cell residue I - M_L M_U = -12 on the diagonal, odd cells nonzero' % nm,
               (res_diag, odd_nz), ({Fr(-12)}, 0))
        expect('   and 4 M_L M_U = G^2 = 26 G, i.e. the composition is 13 G/2 on all 104^2 cells', all(XX[t][s] == 26 * G4[t][s] for t in P for s in P), True)
    cnts = set()
    for w, u2, _, _ in rows:
        cnts.add(sum(1 for t in P for s in P if w[t] * w[s] != 0 and (t == s or dot(U[t], U[s]))))
    expect('partial order: one same-index pair term w_k w_k^T touches this many diag+odd cells (each of the 8 rows)', cnts, {1360})
    expect('control: a full-support term would touch 104+5720 C-cells; 1360 < 5824', (1360 < 104 + 5720,), (True,))

    # ------------------------------------------------------------------ 2  XRECALL / XBIRTH
    say('== 2. XRECALL/XBIRTH geometry: <q_b> not inside q_b^perp')
    expect('<q_b> not inside q_b^perp for all 104 (q_b.q_b = 1)', all(dot(q, q) == 1 for q in Ul), True)
    ev = [Ul[i] ^ Ul[j] for i in range(5) for j in range(i + 1, 5)]
    expect('control: an even vector (q_i+q_j, norm 0) IS inside its own perp', all(dot(v, v) == 0 for v in ev), True)
    part_ok = all(span([Ul[s] for s in P if s != t and G4[t][s]]) == {x for x in range(512) if not dot(x, Ul[t])} for t in P)
    expect('T1CANCEL frame fact: the 48 partner labels of t span t^perp (dim 8 of 9) for all 104 t, and q_t not in t^perp',
           (part_ok, all(dot(Ul[t], Ul[t]) for t in P)), (True, True))
    expect('for a != b: <q_b> inside q_a^perp iff q_a.q_b = 0 (so q_a in q_b^perp is irrelevant to x_b)',
           all((dot(Ul[a], Ul[b]) == 0) == (G4[a][b] != 0) for a in P for b in P if a != b), True)

    # ------------------------------------------------------------------ 3  LIFTTD
    say('== 3. LIFTTD: orthogonal port sets and the non-orthogonal clique number')
    B_labels = json.loads(raws['ports_B.json'])['B_labels']
    Bidx = sorted(Ul.index(x) for x in B_labels)
    Aidx = [i for i in P if i not in Bidx]
    expect('8 non-D ports found among the 104 labels; 96 A ports', (len(Bidx), len(Aidx)), (8, 96))
    w0, c0 = maxclique(graph(Ul, 0))
    expect('max pairwise F2-orthogonal (dot 0) port set on P104', w0, 8)
    expect('  example set is pairwise orthogonal with q.q=1, so its Gram over F2 is I: F2 rank', rank2([Ul[i] for i in c0]), 8)
    expect('  independence argument: n orthogonal odd labels are independent (<=9 in F2^9); exact max is 8, no 9-set', (w0 <= 9, w0), (True, 8))
    w0A, _ = maxclique(graph(Ul, 0, Aidx))
    expect('max pairwise-orthogonal set on the 96 A ports', w0A, 8)
    w1, c1 = maxclique(graph(Ul, 1))
    expect('clique number of the non-orthogonal (dot 1, i.e. odd-cell) graph on all 104', w1, 8)
    w1A, _ = maxclique(graph(Ul, 1, Aidx))
    expect('clique number of the non-orthogonal graph on the 96 A ports', w1A, 8)
    adjA = graph(Ul, 1, Aidx)
    degs = [bin(a).count('1') for a in adjA]
    expect('non-orth degree min/max on the 96', (min(degs), max(degs)), (48, 54))
    pl = [sum(1 << j for j in range(12) if j != i and (i < 8) == (j < 8) and (i < 8 or (i + j) % 2 == 1)) for i in range(12)]
    expect('control: clique search on a planted graph (K8 plus a 4-vertex bipartite part) finds 8', maxclique(pl)[0], 8)

    # ------------------------------------------------------------------ 4  XDEC
    say('== 4. XDEC: joint (cross-call) decoder rank >= 8k')
    cl = c1
    expect('a port and its copy form an odd cell (same label)', all(dot(Ul[t], Ul[t]) == 1 for t in P), True)
    for k in (2, 3):
        pts = [(i, a) for i in cl for a in range(k)]
        Tg = [[1 if p == q else 0 for q in pts] for p in pts]    # target: diagonal 1, every (odd) cell 0
        allodd = all(dot(Ul[p[0]], Ul[q[0]]) == 1 for p in pts for q in pts)
        expect('k=%d: 8-clique x %d copies is pairwise odd (%d points), target block = identity; exact rank' % (k, k, 8 * k),
               (allodd, len(pts), irank(Tg)), (True, 8 * k, 8 * k))
        # clique number of the k-copy multiset graph: projection argument gives <= k*omega = 8k; constructive 8k above
    rnd = random.Random(7)
    L = list(Ul)
    pos = [v for v in range(1, 512) if bin(v).count('1') % 2 == 0]
    perm9 = list(range(9))
    rnd.shuffle(perm9)
    trans = [rnd.choice(pos) for _ in range(12)]

    def iso9(x):
        yv = 0
        for i in range(9):
            if x >> i & 1:
                yv |= 1 << perm9[i]
        for v in trans:
            if dot(yv, v):
                yv ^= v
        return yv
    L2 = [iso9(x) for x in L]
    assert all(dot(L2[i], L2[j]) == dot(L[i], L[j]) for i in range(0, N, 3) for j in range(N))
    ov = len(set(L) & set(L2))
    allL = L + L2
    wj, _ = maxclique(graph(allL, 1))
    expect('relabelled second call (random O(9,2) isometry, overlap %d labels): clique of L u sigma(L) in the odd graph' % ov, wj, 16)
    wm, _ = maxclique(graph(L + L, 1))
    expect('identical second call: clique of L u L (multiset, 208 vertices)', wm, 16)
    expect('control: a single call has clique 8 < 16 = 8k', w1, 8)

    # ------------------------------------------------------------------ 5  HALF18
    say('== 5. HALF18: exact rank certificates (CORRECTS the earlier "min rank ~ 18 = 2h" claim)')
    fr = json.loads(raws['half18_frames.json'])

    def frame_cert(name, blocks, m):
        ok_part = sorted(x for b in blocks for x in b) == list(range(m))
        Z = [[0] * m for _ in range(m)]
        for b in blocks:
            for a in b:
                for c in b:
                    Z[a][c] += 1
        ev_zero = all(Z[a][c] == 0 for a in range(m) for c in range(m) if a != c and dot(U[a], U[c]) == 0)
        dnz = all(Z[a][a] != 0 for a in range(m))
        pw = all(dot(U[a], U[c]) == 1 for b in blocks for a in b for c in b)
        return ok_part, pw, ev_zero, dnz, irank(Z), Z
    ok_part, pw, ev0, dnz, rk, Z120 = frame_cert('E8', fr['E8_120'], 120)
    expect('E8-120: 15 frames partition the 120 lines, each pairwise odd(dot 1, G=0), Z=0 on even cells, diag nonzero, exact rank',
           (len(fr['E8_120']), [len(b) for b in fr['E8_120']] == [8] * 15, ok_part, pw, ev0, dnz, rk), (15, True, True, True, True, True, 15))
    ok_part, pw, ev0, dnz, rk, Z104 = frame_cert('P104', fr['P104'], 104)
    expect('P104: 13 frames partition the 104 ports, same properties, exact rank',
           (len(fr['P104']), ok_part, pw, ev0, dnz, rk), (13, True, True, True, True, 13))
    w120, _ = maxclique(graph(U, 1))
    a120, _ = maxclique(graph(U, 0))
    expect('omega(odd graph): E8-120 and P104 (frames have <= 8 lines so >= 15 resp. 13 frames; both certificates meet it)',
           (w120, w1, -(-120 // w120), -(-104 // w1)), (8, 8, 15, 13))
    expect('alpha = max pairwise-even (dot 0) set: E8-120 and P104 (8 even labels give a nonsingular diagonal block, so rank >= 8)',
           (a120, w0), (8, 8))
    c0e = maxclique(graph(Ul, 0))[1]
    Zs = [[Z104[a][c] for c in c0e] for a in c0e]
    expect('lower bound 8: the Z block on the 8 pairwise-even ports is diagonal, nonzero, rank', (irank(Zs), all(Zs[i][j] == 0 for i in range(8) for j in range(8) if i != j)), (8, True))
    badZ = [r[:] for r in Z104]
    bad = next((a, c) for a in P for c in P if a != c and dot(U[a], U[c]) == 0)
    badZ[bad[0]][bad[1]] = 1
    expect('control: Z with one extra nonzero on an even cell is detected', all(badZ[a][c] == 0 for a in P for c in P if a != c and dot(U[a], U[c]) == 0), False)
    say('   range for min rank of Z (nonzero diag, zero on even cells) on P104: [8, 13]; exact infeasibility of <=12 NOT claimed')

    # ------------------------------------------------------------------ 6  EARLYCAP / T1CANCEL
    say('== 6. EARLYCAP: rank(2I + C_F) <= d + 8 and |E| <= 5408 - 43264/(d+8); T1CANCEL res = 0')
    part_cells = [(t, s) for t in P for s in P if t != s and G4[t][s]]
    pairs_u = [(t, s) for t, s in part_cells if t < s]
    expect('partner cells: 4992 ordered (2496 pairs), entries +-1', (len(part_cells), len(pairs_u)), (4992, 2496))
    rnd = random.Random(11)

    def case(name, Eset):
        E = set()
        for t, s in Eset:
            E.add((t, s))
            E.add((s, t))
        CE = [[G4[t][s] if (t, s) in E else 0 for s in P] for t in P]
        Nm = [[(2 if t == s else 0) + (G4[t][s] if (t != s and G4[t][s] and (t, s) not in E) else 0) for s in P] for t in P]
        d = irank(CE + G4) - 8          # rank(C_E K), K = ker G (dim 96), via rank [C_E; G] = 8 + rank(C_E K)
        rN = irank(Nm)
        nE = len(E)
        nF = 4992 - nE
        cs_ok = rN * (416 + nF) >= 208 * 208
        cap_ok = Fr(nE) <= 5408 - Fr(43264, d + 8)
        say('   %-22s |E|=%4d d=%2d rank N=%3d  rank<=d+8: %s  Cauchy-Schwarz rankN>=208^2/(416+|F|): %s  |E|<=cap: %s' %
            (name, nE, d, rN, rN <= d + 8, cs_ok, cap_ok))
        assert rN <= d + 8 and cs_ok and cap_ok, name
        return nE, d, rN
    r_empty = case('E empty', [])
    r_all = case('E all (control d=96)', pairs_u)
    expect('E empty: rank N = rank G = 8, d = 0; E all: N = 2I rank 104, d = 96', (r_empty[1:], r_all[1:]), ((0, 8), (96, 104)))
    rnd2 = random.Random(5)
    half = [pc for pc in pairs_u if rnd2.random() < 0.5]
    r_half = case('random half', half)
    expect('control: a random half-early set has rank(C_E K) = d = 96 (no cap violation)', r_half[1], 96)
    case('random 5%', [pc for pc in pairs_u if rnd2.random() < 0.05])
    tab = []
    for dd in range(1, 9):
        cap = 5408 - Fr(43264, dd + 8)
        tab.append((dd, float(cap), float(cap / dd)))
    say('   d, cap on |E|, cells per rank: ' + '; '.join('%d: %.1f, %.1f' % t for t in tab))
    expect('cells per rank at d=2,3,4,8 (the 577 gate)',
           [round(float((5408 - Fr(43264, dd + 8)) / dd), 1) for dd in (2, 3, 4, 8)], [540.8, 491.6, 450.7, 338.0])
    expect('cells per rank < 577 for all d >= 2 (up to 96) and strictly decreasing from d=1; d=1 cap |E| <= floor 600.9',
           (all(((5408 - Fr(43264, dd + 8)) / dd) < 577 for dd in range(2, 97)),
            all(((5408 - Fr(43264, dd + 8)) / dd) > ((5408 - Fr(43264, dd + 9)) / (dd + 1)) for dd in range(1, 96)),
            int(5408 - Fr(43264, 9))), (True, True, 600))
    # T1CANCEL: exact res and rank N0 on random sigma matchings (E8)
    part = {t: [s for s in P if s != t and G4[t][s]] for t in P}
    rng = random.Random(2)

    def rand_matching():
        match, rowof = {}, {}

        def aug(t, seen):
            c = part[t][:]
            rng.shuffle(c)
            for q in c:
                if q in seen:
                    continue
                seen.add(q)
                if q not in rowof or aug(rowof[q], seen):
                    match[t] = q
                    rowof[q] = t
                    return True
            return False
        for t in rng.sample(P, N):
            assert aug(t, set())
        return match
    idx = []
    for i in P:
        if irank([G4[j] for j in idx + [i]]) > len(idx):
            idx.append(i)
        if len(idx) == 8:
            break
    Rg = [G4[i] for i in idx]
    for trial in range(2):
        sig = rand_matching()
        M0 = [[G4[sig[t]][t] * G4[sig[t]][j] - (1 if j == t else 0) for j in P] for t in P]
        A2 = [[G4[t][j] - 2 * M0[t][j] for j in P] for t in P]
        cond = [[sum(A2[i][j] * Rg[k][i] for i in P) for k in range(8)] for j in P]
        res = 8 - irank(cond)
        N0 = [[Fr(G4[p][t], 2) - (Fr(G4[p][t], 2) if sig[t] == p else 0) for t in P] for p in P]
        rN0 = irank([[int(2 * x) for x in r] for r in N0])
        expect('T1CANCEL E8 sigma %d (perfect partner matching): exact res(C_eff=G/2) and rank N0' % trial, (res, rN0), (0, 104))
    say('   (T1CANCEL A3/A4 toy part not ported: needs the lane simulators)')

    # ------------------------------------------------------------------ 7  BYPASS
    say('== 7. BYPASS: rank_K{e_t}')
    K = nullspace(G4)
    expect('dim K = dim ker G104', len(K), 96)
    rA = irank([[int(k[t] * 1) if k[t].denominator == 1 else 0 for t in Aidx] for k in K]) if all(k[t].denominator == 1 for k in K for t in Aidx) else None
    if rA is None:
        rA = qrank([[k[t] for t in Aidx] for k in K])
    rB = qrank([[k[t] for t in Bidx] for k in K])
    expect('rank_K{e_t : t in A (96 ports)} = rank of the kernel basis restricted to A', rA, 95)
    expect('formula cross-check: 96 - (|B| - rank G[:,B]) = rank_K A; rank G[:,B]', (96 - (8 - irank([[G4[t][b] for b in Bidx] for t in P])), irank([[G4[t][b] for b in Bidx] for t in P])), (95, 7))
    expect('rank_K{e_t : t in B (8 ports)}', rB, 8)
    expect('control: all 104 ports give rank_K = 96 = dim K', qrank([[k[t] for t in P] for k in K]), 96)

    # ------------------------------------------------------------------ 8  FACTORSWAP
    say('== 8. FACTORSWAP: rank-8 decompositions G/2 = sum_j c_j v_dj v_ej^T on the 16 lines F0 u F1')
    S16 = sorted(d for pr in PAIRS for d in pr)
    expect('S16 = the 16 non-port lines 104..119', S16, list(range(104, 120)))
    price = {}
    for dl in S16:
        for el in S16:
            price[(dl, el)] = pairing_rank([U[t] for t in P if G[t][dl]], [U[s] for s in P if G[s][el]])
    from collections import Counter
    expect('row price histogram over all 16x16 (deposit line, gather line)', dict(Counter(price.values())), {7: 64, 8: 192})
    Gs = [[G[a][b] for b in S16] for a in S16]
    found = []
    for sub in itertools.combinations(range(16), 8):
        if irank([[Gs[a][b] for b in sub] for a in sub]) < 8:
            continue
        ok = []
        for j in range(8):
            m = [e for e in range(16) if Gs[e][sub[j]] != 0 and all(Gs[e][sub[k]] == 0 for k in range(8) if k != j)]
            if not m:
                break
            ok.append(m)
        else:
            found.append((sub, ok))
    tot = Counter(sum(price[(S16[i], S16[o[0]])] for i, o in zip(sub, ok)) for sub, ok in found)
    expect('independent 8-subsets of S16 with a dual-basis row on an S16 line for every j', len(found), 10)
    expect('total price histogram (8 decompositions at C=56, 2 at 64)', dict(tot), {56: 8, 64: 2})
    expect('gather choices per row are unique (multiplicity)', Counter(len(o) for s, ok in found for o in ok), Counter({1: 80}))
    rs = list(PAIRS)
    expect('control: the native pairing (d_j, d\'_j) rows each price 7 (total 56)', (sum(price[p] for p in rs), sorted({price[p] for p in rs})), (56, [7]))

    # ------------------------------------------------------------------ 9  H9CERT
    say('== 9. H9CERT Lemma A (acyclic): n <= sum_k rank Z[D_k, S_k] for every valid Z (exact decoder: odd cells of M are 0)')
    Dk = [[t for t in P if w[t]] for w, _, _, _ in rows]
    Sk = [[s for s in P if u2[s]] for _, u2, _, _ in rows]
    Mx = [[Fr(G4[t][s], 2) for s in P] for t in P]
    Zq = [[dot(Ul[a], Ul[b]) for b in P] for a in P]
    Zi = [[1 if a == b else 0 for b in P] for a in P]
    for nm, Zm in (('frame-partition Z (rank 13)', Z104), ('Z = I', Zi), ('Z = Q (dot matrix)', Zq)):
        valid = all(Zm[a][a] != 0 for a in P) and all(Zm[a][b] == 0 for a in P for b in P if a != b and dot(Ul[a], Ul[b]) == 0)
        had = all(Zm[t][s] * Mx[t][s] == (Zm[t][t] if t == s else 0) for t in P for s in P)
        ranks = [irank([[Zm[t][s] for s in Sk[k]] for t in Dk[k]]) for k in range(8)]
        say('   %s: valid %s, Z o M = diag(Z_pp) %s, block ranks %s sum %d >= 104: %s' % (nm, valid, had, ranks, sum(ranks), sum(ranks) >= 104))
        assert valid and had and sum(ranks) >= 104
    zinv = [r[:] for r in Z104]
    zinv[0][0] = 0
    ranks = [irank([[zinv[t][s] for s in Sk[k]] for t in Dk[k]]) for k in range(8)]
    say('   control (invalid Z, port 0 diagonal zeroed): Z o M diagonal singular, block rank sum %d (bound no longer required)' % sum(ranks))
    say('   (ACYCDEC lb.py not ported)')

    say('elapsed %.1fs' % (time.time() - T0))
    say('PASS_E8_LAWS')


if __name__ == '__main__':
    main()
