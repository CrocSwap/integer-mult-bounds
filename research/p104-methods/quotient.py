"""P104 method: the O+(8,2) quotient structure of the 104 ports and the c-trick. Standard library only, exact.

Data (data/, SHA256 pinned below): ports104.json = {"lines": 104 F2^9 port vectors, "gram": signed 104x104 Gram} (our derived
data: charts of the #7334 word + reflection closure, REBASET1/gram104.py), packing8.json (8 port-disjoint 12-port blocks),
triples33.json (33 disjoint c-sum triples), iso968.json (port permutation + diagonal signs mapping the PR968 Gram onto the
vendored Gram).  c = all-ones in F2^9.
Checked (names as in the printed lines):
  (a) data hashes; Gram: symmetric, diagonal 2, rank 8, G^2 = 26 G, 48 partners per port, partners <=> G odd <=> dot(q_p,q_t)=0;
      the vendored Gram equals the PR968 Gram under the vendored permutation with diagonal +-1 switching (every entry);
  (b) every port has q.c = 1; W = c^perp/<c> (even-weight representatives q+c), omega = dot is symplectic (8 dim);
      a quadratic form with polar omega taking value 1 on all 104 ports exists; it has 120 nonsingular and 135 singular
      nonzero points, the ports are 104 of the nonsingular points, 16 missing;
  (c) two-graph sign law: over all mutually-partner triples, G_py G_yt G_pt = -1 iff q_p+q_y+q_t = c (704 triples, all other
      products +1; control: no non-c-sum triple has product -1); c-sum triples number 704 and all their pairs are partners;
  (d) pair law (3-stop absorber fact): partner pairs split 2,112 with 24 common partners and exactly one sign-wrong cell, which
      is the port t* with q_t* = q_p + q_y + c, and 384 with 22 common partners and no wrong cell (p-bar + y-bar is one of the
      16 missing points);
  (e) 4-dim quotient spaces (all 200,787 enumerated): exactly 282 contain 12 ports; in each the 3 non-ports are a line and the
      12 ports carry 16 c-sum triples;
  (f) the vendored packing: 8 blocks, each one of the 282, pairwise disjoint, covering 96 ports, with the 8 leftover ports
      containing no c-sum triple (this packing only; controls: a perturbed packing fails disjointness, a random 12-subset is
      not a block);
  (g) c-trick: for every port p and every vector a, {partners of p not perp <p,a>} = U<p,a+c> (ports perp to p and a+c); on the
      33 vendored triples (disjoint, c-sum, pairs partners) with A2(p) = <p,q>, bottom(p) = U<p,x> of size 24, and the
      (reader, host) pair has exactly one sign-wrong column, namely the third triple member (4,224 ordered pairs).
Not re-checked: the order-384 stabiliser (lane qgrp.py), orbit sizes 32/48/24.  Prints PASS_METHODS_QUOTIENT."""
import hashlib, itertools, json, random, collections
from pathlib import Path
from fractions import Fraction as Fr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR968 = 'research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt'
PR968_SHA256 = '8e0178db02c14e1b29058cdbdbd50aac22f2b55a1ba21dc82f417610c9932526'
SHA = {
    'ports104.json': '0299f8f7165835231b057e1c6151ad0a8333efcb61a06a0a2aea045aa391c381',
    'packing8.json': 'a4bd773ede969488aacdf8feb38487b97ce3daf48d836bbb1bd48f6fd356e12e',
    'triples33.json': 'f9007e39cf6ce94915848e9c810f28572dc423c929e3c3f4d874301b8359d12e',
    'iso968.json': 'fd3fb6b90918d6802c7b22b7fe2efdf3a3979e4bc50bb610437957a84b702e1f',
}
C = 511


def say(s):
    print(s, flush=True)


def expect(name, got, want):
    if got != want:
        raise SystemExit('FAIL %s: got %r want %r' % (name, got, want))
    say('ok  %s: %r' % (name, got))


def dot(a, b):
    return bin(a & b).count('1') & 1


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


def wrong_cells(com, G, p, y):
    """cells t in com where sign(G_pt G_yt) is the minority class (rows p, y proportional up to these cells)."""
    pos = [t for t in com if G[p][t] * G[y][t] > 0]
    neg = [t for t in com if G[p][t] * G[y][t] < 0]
    if len(pos) == len(neg) and pos:
        raise SystemExit('FAIL tie in sign classes')
    return sorted(min(pos, neg, key=len))


def span(vs):
    s = {0}
    for v in vs:
        if v not in s:
            s |= {x ^ v for x in s}
    return s


def main():
    raws = {}
    for f in SHA:
        raws[f] = (HERE / 'data' / f).read_bytes()
        expect('SHA256 data/' + f, hashlib.sha256(raws[f]).hexdigest(), SHA[f])
    d = json.loads(raws['ports104.json'])
    L, G = d['lines'], d['gram']
    n = len(L)
    expect('ports (distinct)', (n, len(set(L))), (104, 104))
    expect('port range', all(0 <= v < 512 for v in L), True)

    say('== (a) Gram')
    expect('G symmetric, diag 2', all(G[i][j] == G[j][i] for i in range(n) for j in range(n)) and all(G[i][i] == 2 for i in range(n)), True)
    expect('rank G', rank(G), 8)
    G2 = [[sum(G[i][k] * G[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    expect('G^2 = 26 G', all(G2[i][j] == 26 * G[i][j] for i in range(n) for j in range(n)), True)
    partner = [[t for t in range(n) if t != p and G[p][t] % 2] for p in range(n)]
    expect('partners per port', sorted({len(v) for v in partner}), [48])
    expect('partner <=> dot(q_p,q_t) = 0', all((G[p][t] % 2 == 1) == (dot(L[p], L[t]) == 0) for p in range(n) for t in range(n) if p != t), True)
    # PR968 cross-check
    raw = (ROOT / PR968).read_bytes()
    expect('SHA256 of %s' % PR968, hashlib.sha256(raw).hexdigest(), PR968_SHA256)
    ls = raw.decode().split('\n')
    Dr = [[int(x) for x in l[3:].split()] for l in ls if l.startswith(' d:')]
    Tr = [[int(x) for x in l[3:].split()] for l in ls if l.startswith(' t:')]
    GP = [[sum(Dr[k][i] * Tr[k][j] for k in range(8)) // 2 for j in range(n)] for i in range(n)]
    iso = json.loads(raws['iso968.json'])
    perm, eps = iso['perm'], iso['eps']
    expect('iso968: perm is a permutation, eps = +-1', (sorted(perm) == list(range(n)), set(eps) <= {1, -1}), (True, True))
    expect('PR968 Gram = eps eps G104(perm) on all 104^2 entries',
           all(GP[u][v] == eps[u] * eps[v] * G[perm[u]][perm[v]] for u in range(n) for v in range(n)), True)
    wrong_perm = perm[:]
    wrong_perm[0], wrong_perm[1] = wrong_perm[1], wrong_perm[0]
    expect('control: swapped permutation fails', all(GP[u][v] == eps[u] * eps[v] * G[wrong_perm[u]][wrong_perm[v]] for u in range(n) for v in range(n)), False)

    say('== (b) quotient form')
    expect('every port has q.c = 1', all(dot(v, C) == 1 for v in L), True)
    Q = [v ^ C for v in L]
    expect('quotient reps even weight', all(bin(v).count('1') % 2 == 0 for v in Q), True)
    EV = [v for v in range(1, 512) if bin(v).count('1') % 2 == 0]
    expect('even-weight nonzero vectors (c^perp minus 0, 8-dim)', len(EV), 255)
    # omega nondegenerate on even space: radical of dot on even vectors is {0, c}; c is odd weight (9) so not in it
    radical = [v for v in EV if all(dot(v, w) == 0 for w in EV)]
    expect('omega nondegenerate on even space', radical, [])
    # quadratic forms with polar omega: q_a(v) = wt(v)/2 + a.v (v even)
    sols = [a for a in range(256) if all((bin(v).count('1') // 2 + dot(a, v)) % 2 == 1 for v in Q)]
    expect('forms q_a (a in F2^8 mod c) equal to 1 on all 104 ports', len(sols), 1)
    a0 = sols[0]
    qf = lambda v: (bin(v).count('1') // 2 + dot(a0, v)) % 2
    nonsing = [v for v in EV if qf(v) == 1]
    expect('nonsingular / singular nonzero points', (len(nonsing), 255 - len(nonsing)), (120, 135))
    Qs = set(Q)
    expect('ports inside nonsingular points', Qs <= set(nonsing), True)
    missing = [v for v in nonsing if v not in Qs]
    expect('missing nonsingular points', len(missing), 16)
    expect('partner <=> omega(p-bar, t-bar) = 1', all((G[p][t] % 2 == 1) == (dot(Q[p], Q[t]) == 1) for p in range(n) for t in range(n) if p != t), True)

    say('== (c) two-graph sign law')
    part = [set(x) for x in partner]
    neg = pos = negok = posok = 0
    cs = []
    for p in range(n):
        for y in partner[p]:
            if y < p:
                continue
            for t in part[p] & part[y]:
                if t < y:
                    continue
                prod = G[p][y] * G[y][t] * G[p][t]
                csum = (L[p] ^ L[y] ^ L[t]) == C
                if prod == -1:
                    neg += 1
                    negok += csum
                else:
                    pos += 1
                    posok += (not csum)
                if csum:
                    cs.append((p, y, t))
    say('    mutually-partner triples: %d with sign -1, %d with sign +1' % (neg, pos))
    expect('product -1 iff c-sum (704 triples)', (neg, negok, pos == posok), (704, 704, True))
    expect('control: non-c-sum triples with product -1', neg - negok, 0)
    # c-sum triples among ports, regardless of partnerness
    QI = {v: i for i, v in enumerate(Q)}
    TRI = [(p, q, QI[Q[p] ^ Q[q]]) for p, q in itertools.combinations(range(n), 2) if (Q[p] ^ Q[q]) in QI and QI[Q[p] ^ Q[q]] > q]
    expect('c-sum triples (q_p+q_q+q_x = c)', len(TRI), 704)
    expect('their pairs are all partners', all(b in part[a] for t in TRI for a, b in itertools.combinations(t, 2)), True)
    expect('they are exactly the sign -1 triples', sorted(map(tuple, map(sorted, TRI))) == sorted(cs), True)

    say('== (d) pair law / 3-stop absorber')
    st = collections.Counter()
    tstar_ok = True
    miss_ok = True
    missing_s = set(missing)
    for p in range(n):
        for y in partner[p]:
            if y < p:
                continue
            com = sorted(part[p] & part[y])
            wr = wrong_cells(com, G, p, y)
            st[(len(com), len(wr))] += 1
            x = Q[p] ^ Q[y]
            if len(wr) == 1:
                tstar_ok &= (wr[0] == QI.get(x, -1))
            else:
                miss_ok &= (x in missing_s)
    expect('partner pairs by (common partners, sign-wrong cells)', dict(st), {(24, 1): 2112, (22, 0): 384})
    expect('wrong cell is the port with q = q_p+q_y+c; else p-bar+y-bar is missing', (tstar_ok, miss_ok), (True, True))

    say('== (e) 12-port 4-dim quotient spaces')
    Q8 = {v & 255: i for i, v in enumerate(Q)}              # linear iso of even-weight space with F2^8: drop bit 8
    expect('8-bit coordinates injective on ports', len(Q8), 104)
    blocks = {}
    hist = collections.Counter()
    nsub = 0
    for piv in itertools.combinations(range(8), 4):
        free = [[c for c in range(piv[i] + 1, 8) if c not in piv] for i in range(4)]
        nf = sum(len(f) for f in free)
        for m in range(1 << nf):
            rows = []
            k = 0
            for i in range(4):
                r = 1 << piv[i]
                for c in free[i]:
                    if (m >> k) & 1:
                        r |= 1 << c
                    k += 1
                rows.append(r)
            nsub += 1
            els = span(rows)
            ports = frozenset(Q8[v] for v in els if v in Q8)
            hist[len(ports)] += 1
            if len(ports) == 12:
                blocks[ports] = els
    expect('4-dim subspaces of F2^8 enumerated', nsub, 200787)
    say('    ports-per-4-space histogram: %s' % sorted(hist.items()))
    expect('4-spaces containing exactly 12 ports', len(blocks), 282)
    line_ok = tri_ok = True
    for ports, els in blocks.items():
        non = [v for v in els if v and v not in Q8]
        line_ok &= (len(non) == 3 and non[0] ^ non[1] == non[2])
        pv = sorted(v for v in els if v in Q8)
        tri_ok &= sum(1 for a, b in itertools.combinations(pv, 2) if (a ^ b) in Q8 and (a ^ b) > b) == 16
    expect('the 3 non-ports of each form a line', line_ok, True)
    expect('each carries 16 c-sum triples', tri_ok, True)

    say('== (f) packing of 8 blocks')
    pk = json.loads(raws['packing8.json'])
    blk = [frozenset(b) for b in pk['blocks']]
    left = sorted(pk['leftover'])
    expect('packing: 8 blocks of 12 ports', (len(blk), sorted({len(b) for b in blk})), (8, [12]))
    expect('each is one of the 282 blocks', all(frozenset(Q8[Q[p] & 255] for p in b) in blocks for b in blk), True)
    cover = set().union(*blk)
    expect('pairwise disjoint, covering 96 ports', (sum(len(b) for b in blk), len(cover)), (96, 96))
    expect('leftover = the other 8 ports', left, sorted(set(range(n)) - cover))
    TS = set(map(frozenset, TRI))
    expect('triples inside the leftover', sum(1 for t in itertools.combinations(left, 3) if frozenset(t) in TS), 0)
    # controls
    bad = [set(b) for b in blk]
    swap_out = sorted(bad[0])[0]
    swap_in = sorted(bad[1])[0]
    bad[0].remove(swap_out)
    bad[0].add(swap_in)
    expect('control: perturbed packing fails disjointness', sum(len(b) for b in bad) == len(set().union(*bad)), False)
    expect('control: perturbed block is not a 12-port 4-space', frozenset(Q8[Q[p] & 255] for p in bad[0]) in blocks, False)
    rg = random.Random(1)
    rnd = frozenset(rg.sample(range(n), 12))
    expect('control: random 12-subset is not a block', frozenset(Q8[Q[p] & 255] for p in rnd) in blocks, False)
    expect('control: a random 12-subset spans more than 4 dims', len(span([Q[p] for p in rnd])) > 16, True)
    t0 = TRI[0]
    expect('control: an 8-set containing a c-sum triple is detected by the leftover test',
           sum(1 for t in itertools.combinations(sorted(list(t0) + left[:5]), 3) if frozenset(t) in TS) >= 1, True)

    say('== (g) c-trick')
    bottomok = True
    for p in range(n):
        for a in range(512):
            bottom = {t for t in partner[p] if dot(L[t], a)}
            U = {t for t in range(n) if dot(L[t], L[p]) == 0 and dot(L[t], a ^ C) == 0}
            bottomok &= (bottom == U)
    expect('bottom(p,a) = U<p,a+c> for all ports p, all a in F2^9', bottomok, True)
    tr = [tuple(t) for t in json.loads(raws['triples33.json'])['triples']]
    expect('33 triples, 99 distinct ports', (len(tr), len({v for t in tr for v in t})), (33, 99))
    expect('all c-sum', all((L[a] ^ L[b] ^ L[c_]) == C for a, b, c_ in tr), True)
    expect('all pairs partners', all(b in part[a] for t in tr for a, b in itertools.combinations(t, 2)), True)
    ok24 = True
    one_wrong = 0
    ordered = 0
    for t in tr:
        for p, q in itertools.permutations(t, 2):
            x = [v for v in t if v not in (p, q)][0]
            bottom = {u for u in partner[p] if dot(L[u], L[q])}               # A2(p) = <p,q>
            U_px = {u for u in range(n) if dot(L[u], L[p]) == 0 and dot(L[u], L[x]) == 0}
            ok24 &= (bottom == U_px and len(bottom) == 24)
            # (reader p, host x): common partners, sign-wrong cells
            com = sorted(part[p] & part[x])
            wr = wrong_cells(com, G, p, x)
            ordered += 1
            one_wrong += (wr == [q])
    expect('bottom(p) = U<p,x>, size 24, all ordered (p,q) in the 33 triples', ok24, True)
    expect('sign-wrong column of (reader p, host x) is the third member q (ordered pairs)', (one_wrong, ordered), (198, 198))
    allord = sum(1 for t in TRI for p, x in itertools.permutations(t, 2)
                 if wrong_cells(sorted(part[p] & part[x]), G, p, x) == [[v for v in t if v not in (p, x)][0]])
    expect('same for all 704 c-sum triples, ordered (reader, host) pairs', allord, 4224)
    # control: a non-c-sum mutually partner triple does not have this property
    nonc = next((p, y, t) for p in range(n) for y in partner[p] for t in part[p] & part[y] if (L[p] ^ L[y] ^ L[t]) != C)
    p, y, t = nonc
    expect('control: non-c-sum partner triple product', G[p][y] * G[y][t] * G[p][t] > 0, True)
    badtri = (tr[0][0], tr[0][1], left[0])
    expect('control: perturbed triple is not c-sum', (L[badtri[0]] ^ L[badtri[1]] ^ L[badtri[2]]) == C, False)
    say('PASS_METHODS_QUOTIENT')


if __name__ == '__main__':
    main()
