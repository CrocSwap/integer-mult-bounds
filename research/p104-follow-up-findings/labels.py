#!/usr/bin/env python3
"""LABELS checker: exact label/graph facts of the 120 E8 lines and the P104 port set.  Tags: [C] exact.

Own code (DreamingOfClouds with Claude Opus 5.5), standard library only.  data/lines120.json (sha256 pinned below) is our
derived data from the PR968 P104 decoder input (research/complex-frame-pair-decoders/inputs/pr717/P104_HIT_flip_3a.txt),
as in #7583/#7606: 120 F2^9 labels (first 104 = P104 ports) and the integer Gram of the 120 E8 lines.
Convention: label dot q.q' = popcount(q&q') mod 2; "odd" cells (dot 1) are exactly the integer-orthogonal pairs (G=0).

Checks
  1. Orthogonality (label-odd) graph on 120 is SRG(120,63,30,36), complement SRG(120,56,28,24) (direct counting; this corrects
     LITSWEEP2's parameters); on P104 degrees 55 (orthogonal) and 48 (non-orthogonal); 104*55 = 5720 odd cells.
  2. Ranks: Q = A_odd + I has GF(2) rank 9 and rational rank 120 (120x120) / 104 (P104; exact mod two large primes);
     G mod 2 has GF(2) rank 8.
  3. Orthogonal 8-frames: 2025 8-cliques on 120 lines, each orthogonal pair in exactly 15; max clique 8 (no 9-clique);
     759 frames inside P104; every frame's labels span a dim-4 F2 subspace.
  4. In P104 the max pairwise-odd set and the max pairwise-even set both have size 8.
  5. P104 is an exact cover by 13 pairwise-disjoint orthogonal 8-frames (found by DFS); M = sum 1_F 1_F^T has diagonal 1 and
     is zero on all 4992 ordered non-orthogonal off-diagonal cells.
  6. G104 (104x104 Gram block): integer, rational rank 8, diagonal 2, 0 on all 5720 odd cells, +-1 on all 4992 non-orthogonal
     cells; alpha = 8 = rank, so the minimum hub count is 8 (numbers only).
  Controls: a one-label perturbation breaks the SRG parameters; a non-frame 8-set fails the clique test; a random 8-set is not a cover.
Prints PASS_LABEL_FACTS.
"""
import hashlib, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIN = '4a91033b56fe23feb897b90e6259b33dfbe428ff07ad7ce511a73835074f2708'
P1, P2 = (1 << 61) - 1, (1 << 31) - 1


def fail(msg):
    print('FAIL:', msg); sys.exit(1)


def expect(name, got, want):
    ok = got == want
    print(('ok   ' if ok else 'FAIL ') + name + ': ' + str(got))
    if not ok:
        fail('%s: got %r want %r' % (name, got, want))


b = open(os.path.join(HERE, 'data', 'lines120.json'), 'rb').read()
if hashlib.sha256(b).hexdigest() != PIN:
    fail('sha256 mismatch for lines120.json')
D = json.loads(b)
L, G = D['labels'], D['gram']
N, NP = 120, 104


def dot(a, c): return bin(a & c).count('1') & 1


def adj_masks(labels, odd=True):
    n = len(labels)
    return [sum(1 << j for j in range(n) if j != i and (dot(labels[i], labels[j]) == 1) == odd) for i in range(n)]


def pc(x): return bin(x).count('1')


def srg(masks):
    """return (set of degrees, set of lambda, set of mu) by direct counting"""
    n = len(masks)
    deg, lam, mu = set(), set(), set()
    for i in range(n):
        deg.add(pc(masks[i]))
        for j in range(i + 1, n):
            c = pc(masks[i] & masks[j])
            (lam if masks[i] >> j & 1 else mu).add(c)
    return deg, lam, mu


def rank_f2(rows):
    basis = []
    for r in rows:
        for v in basis:
            r = min(r, r ^ v)
        if r:
            basis.append(r)
    return len(basis)


def rank_mod(M, p):
    M = [[x % p for x in r] for r in M]
    rk = 0
    nc = len(M[0])
    for c in range(nc):
        piv = next((i for i in range(rk, len(M)) if M[i][c]), None)
        if piv is None: continue
        M[rk], M[piv] = M[piv], M[rk]
        inv = pow(M[rk][c], p - 2, p)
        M[rk] = [x * inv % p for x in M[rk]]
        for i in range(len(M)):
            if i != rk and M[i][c]:
                f = M[i][c]
                M[i] = [(x - f * y) % p for x, y in zip(M[i], M[rk])]
        rk += 1
    return rk


def rrank(M):
    a, b2 = rank_mod(M, P1), rank_mod(M, P2)
    if a != b2: fail('rank disagreement mod primes %d %d' % (a, b2))
    return a


def cliques(masks, size, within=None):
    """all `size`-cliques as tuples (bitset recursion, ascending order)"""
    n = len(masks)
    out = []
    full = (1 << n) - 1 if within is None else within

    def rec(cur, cand):
        if len(cur) == size:
            out.append(tuple(cur)); return
        while cand:
            v = (cand & -cand).bit_length() - 1
            cand &= cand - 1
            rec(cur + [v], cand & masks[v])
    rec([], full)
    return out


def max_clique(masks, within=None):
    best = [0]
    n = len(masks)

    def rec(size, cand):
        if size > best[0]: best[0] = size
        while cand:
            if size + pc(cand) <= best[0]: return
            v = (cand & -cand).bit_length() - 1
            cand &= cand - 1
            rec(size + 1, cand & masks[v])
    rec(0, (1 << n) - 1 if within is None else within)
    return best[0]


# ---- data sanity
expect('shape', (len(L), len(G), len(G[0])), (120, 120, 120))
expect('symmetric Gram', all(G[i][j] == G[j][i] for i in range(N) for j in range(N)), True)
expect('diag G = 2', {G[i][i] for i in range(N)}, {2})
expect('G entries', sorted({x for r in G for x in r}), [-1, 0, 1, 2])
expect('labels in F2^9', all(0 <= q < 512 for q in L), True)
expect('label-odd == (G=0) off-diagonal',
       all((dot(L[i], L[j]) == 1) == (G[i][j] == 0) for i in range(N) for j in range(N) if i != j), True)

# ---- 1. SRG
odd = adj_masks(L, True)
even = adj_masks(L, False)
expect('1 odd graph (deg, lambda, mu)', tuple(map(sorted, srg(odd))), ([63], [30], [36]))
expect('1 even graph (deg, lambda, mu)', tuple(map(sorted, srg(even))), ([56], [28], [24]))
P = (1 << NP) - 1
oddP = [m & P for m in odd[:NP]]
evenP = [m & P for m in even[:NP]]
expect('1 P104 odd degrees', sorted({pc(m) for m in oddP}), [55])
expect('1 P104 non-orthogonal degrees', sorted({pc(m) for m in evenP}), [48])
expect('1 odd cells on P104', sum(pc(m) for m in oddP), 5720)
expect('1 non-orthogonal ordered cells on P104', sum(pc(m) for m in evenP), 4992)

# control: perturb one label
Lp = list(L); Lp[7] ^= 0b100000001
bad = adj_masks(Lp, True)
expect('1 control: flipped label breaks SRG', tuple(map(sorted, srg(bad))) == ([63], [30], [36]), False)

# ---- 2. ranks
Qm = [[(1 if (i == j or odd[i] >> j & 1) else 0) for j in range(N)] for i in range(N)]
expect('2 Q GF(2) rank (120)', rank_f2([sum(Qm[i][j] << j for j in range(N)) for i in range(N)]), 9)
expect('2 Q rational rank (120)', rrank(Qm), 120)
QP = [r[:NP] for r in Qm[:NP]]
expect('2 Q GF(2) rank (P104)', rank_f2([sum(r[j] << j for j in range(NP)) for r in QP]), 9)
expect('2 Q rational rank (P104)', rrank(QP), 104)
expect('2 G mod 2 GF(2) rank', rank_f2([sum((x & 1) << j for j, x in enumerate(r)) for r in G]), 8)

# ---- 3. frames
fr = cliques(odd, 8)
expect('3 number of 8-cliques of odd graph', len(fr), 2025)
expect('3 no 9-clique (max clique)', max_clique(odd), 8)
cnt = {}
for f in fr:
    for a in range(8):
        for c in range(a + 1, 8):
            cnt[(f[a], f[c])] = cnt.get((f[a], f[c]), 0) + 1
expect('3 odd pairs covered by frames', len(cnt), 120 * 63 // 2)
expect('3 frames per orthogonal pair', sorted(set(cnt.values())), [15])
expect('3 frame label span dims', sorted({rank_f2([L[v] for v in f]) for f in fr}), [4])
frP = [f for f in fr if f[-1] < NP]
expect('3 frames inside P104', len(frP), 759)
nonframe = (0, 1, 2, 3, 4, 5, 6, 7)
expect('3 control: non-frame 8-set fails clique test',
       all(odd[a] >> c & 1 for a in nonframe for c in nonframe if a != c) or nonframe in set(fr), False)
expect('3 control: a true frame passes', all(odd[a] >> c & 1 for a in fr[0] for c in fr[0] if a != c), True)

# ---- 4. alpha
expect('4 max pairwise-odd set in P104', max_clique(oddP, P), 8)
expect('4 max pairwise-even set in P104', max_clique(evenP, P), 8)

# ---- 5. exact cover
byel = [[] for _ in range(NP)]
fm = [sum(1 << v for v in f) for f in frP]
for k, m in enumerate(fm):
    for v in frP[k]:
        byel[v].append(k)


def cover(mask, chosen):
    if mask == P: return chosen
    v = (~mask & P & (mask + 1)).bit_length() - 1  # lowest uncovered
    for k in byel[v]:
        if not fm[k] & mask:
            r = cover(mask | fm[k], chosen + [k])
            if r: return r
    return None


ch = cover(0, [])
if ch is None: fail('no exact cover found')
expect('5 exact cover size', len(ch), 13)
expect('5 cover disjoint & complete', sorted(v for k in ch for v in frP[k]) == list(range(NP)), True)
M = [[0] * NP for _ in range(NP)]
for k in ch:
    for a in frP[k]:
        for c in frP[k]:
            M[a][c] += 1
expect('5 M diagonal', {M[i][i] for i in range(NP)}, {1})
nonorth = [(i, j) for i in range(NP) for j in range(NP) if i != j and not oddP[i] >> j & 1]
expect('5 non-orthogonal ordered cells', len(nonorth), 4992)
expect('5 M zero on all non-orthogonal cells', {M[i][j] for i, j in nonorth}, {0})
rnd = random.Random(1)
rs = rnd.sample(range(NP), 8)
expect('5 control: random 8-set is not a frame', all(oddP[a] >> c & 1 for a in rs for c in rs if a != c), False)
expect('5 control: 13 random 8-sets are not a cover',
       sorted(sum((rnd.sample(range(NP), 8) for _ in range(13)), [])) == list(range(NP)), False)

# ---- 6. G104
G104 = [r[:NP] for r in G[:NP]]
expect('6 G104 rational rank', rrank(G104), 8)
expect('6 G104 diagonal', {G104[i][i] for i in range(NP)}, {2})
oddcells = [(i, j) for i in range(NP) for j in range(NP) if i != j and oddP[i] >> j & 1]
expect('6 G104 zero on odd cells (count)', (len(oddcells), {G104[i][j] for i, j in oddcells}), (5720, {0}))
expect('6 G104 +-1 on non-orthogonal cells', (len(nonorth), sorted({G104[i][j] for i, j in nonorth})), (4992, [-1, 1]))
expect('6 alpha = rank = hub count', (max_clique(oddP, P), rrank(G104)), (8, 8))

print('PASS_LABEL_FACTS')
