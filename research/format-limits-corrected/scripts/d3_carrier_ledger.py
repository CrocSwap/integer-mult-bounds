"""D3. The register ledger of PR #531's 504 helpers, rebuilt from tile objects on the geometry P112, and the carrier-neutrality identity.

Geometry (PR #531).  The 112 sources are the root lines 8..119 of the file inputs/hamming/PROTOTYPE.json; two sources are
adjacent (a reader t "reads" a source s) when their root lines have inner product +-2; Gm[t, s] = (root_t . root_s)/2 in {0, +-1}
is the signed adjacency; every reader reads 52 sources.  The sources fall into 14 blocks of 8 (the support of the root
line), each block into 2 tetrads of 4 (parity of the number of minus signs).  The F_2 label of a source is its port in F_2^9.

Tile objects.  A "face" is a set B of 4 sources of one block together with a sign pattern; its reach is the number of readers
t that read all four sources with that pattern (Gm[t, B] proportional to the pattern).  A "key" is a pair of faces of two
different blocks, disjoint in sources, that have at least 3 readers in common with a consistent relative sign.  For a key with
reader set T and source set S (8 sources) two readers are mates if their common neighbourhood with consistent sign has at least
|S| + 8 sources; mu is the size of a maximum matching of mates among T.

Ledger.  The helper registers needed by a hierarchy of faces and keys are counted by births = sum over object instances of
(uses - 1):
   carriers   2 N2 - 112 + waste   (N2 faces, each built from two edge objects, "waste" = edges used with only one sign variant),
   face copies  2 K - N2           (K keys, each face used by two keys),
   M copies     R - K              (R = key hosts = sum over keys of (|T| - mu), minus the 56 slots borrowed from the output pairs),
so that  B = N2 + K + R - 112 + waste.  For PR #531 the objects are the 168 block-local planes (faces of reach 8 whose four ports
add to 0), their 168 tetrad edges, and 168 keys; the ledger gives 224 + 168 + 112 = 504 = the helper count R of the word.
A butterfly (an edge object with both sign variants) is register-neutral, so the ledger depends on the edge cover only through
`waste`: rebuilt from edges joining the two tetrads of a block the same planes cost 168 more registers (12 wasted single-variant
butterflies per block), while the tetrad edges waste nothing.  Upstream: PR #531 (word and geometry).
"""
import sys

sys.dont_write_bytecode = True

import itertools
from collections import Counter, defaultdict

from ortools.sat.python import cp_model

import d_geometry as dg
from report import check, finish

# ---------------------------------------------------------------------------------------------------------------
# Expected values (hard-coded; each is the exact outcome of the computation below)
# ---------------------------------------------------------------------------------------------------------------
EXPECTED = dict(
    faces=168, faces_per_block=12, face_reach=8, face_rank=3,        # block-local planes
    edges=168, edge_degree=3, carriers=224,                          # tetrad edges, each source in 3, births of the sources
    keys=168, key_readers={4: 168}, face_uses={2: 168}, key_rank={5: 168},
    nested_width={2: 168}, face_copies=168,                          # consumer frames of the two keys of a face are never nested
    mate_matching={2: 168}, borrowed=56, hosts=280, m_copies=112,
    total=504, classes=(224, 168, 112),
    cross_block_best=(28, 12, 12, 16, 12),                           # per block: (births, wasted butterflies, edges, births_0, births_1)
    cross_total=392, cross_extra=168, cross_waste=12,
    waste_min=0, candidate_edges=392,
)


# ---------------------------------------------------------------------------------------------------------------
# Faces, keys
# ---------------------------------------------------------------------------------------------------------------
def block_local_faces(P):
    """all faces of reach 8 inside one block: for each 4-subset B of a block (sources in increasing order) and each sign
    pattern (signs of Gm[t, B] normalised so that the first is +1) count the readers t with that pattern.  Returns the list of
    faces (B, pattern, {reader: sign at B[0]}), sorted, and the census {(reach): number of (B, pattern)}."""
    Gm, ADJ, blk = P['Gm'], P['ADJ'], P['blk']
    faces, census = [], Counter()
    for b in range(P['nblocks']):
        srcs = [s for s in range(P['n']) if blk[s] == b]
        for B in itertools.combinations(srcs, 4):
            readers = [t for t in range(P['n']) if all(ADJ[t, s] for s in B)]
            groups = defaultdict(dict)
            for t in readers:
                v = [int(Gm[t, s]) for s in B]
                groups[tuple(x * v[0] for x in v)][t] = v[0]
            for pat, rd in groups.items():
                census[len(rd)] += 1
                if len(rd) == EXPECTED['face_reach']:
                    faces.append((B, pat, rd))
    return sorted(faces, key=lambda f: (f[0], f[1])), census


def keys_of(faces, P):
    """keys = pairs of faces of different blocks without common source, with relative sign rho = +-1 on at least 3 common
    readers.  Returns [(i, j, rho, sorted tuple of the common readers with that relative sign)]."""
    blk = P['blk']
    out = []
    for i, j in itertools.combinations(range(len(faces)), 2):
        Bi, _, Ri = faces[i]
        Bj, _, Rj = faces[j]
        if blk[Bi[0]] == blk[Bj[0]] or set(Bi) & set(Bj):
            continue
        common = set(Ri) & set(Rj)
        for rho in (1, -1):
            rd = [t for t in common if Ri[t] * Rj[t] == rho]
            if len(rd) >= 3:
                out.append((i, j, rho, tuple(sorted(rd))))
    return out


def f2_rank(vs):
    return len(dg.f2_reduce(vs))


def mate_matching(P, S8, T):
    """size (0, 1 or 2) of a maximum matching of mates among the (four) readers T of a key with source set S8."""
    Gm, ADJ, n = P['Gm'], P['ADJ'], P['n']

    def mate(t1, t2):
        r = Gm[t1, S8[0]] * Gm[t2, S8[0]]
        a = [s for s in range(n) if ADJ[t1, s] and ADJ[t2, s] and Gm[t1, s] * Gm[t2, s] == r]
        return len(a) >= len(S8) + 8

    G = [(a, b) for a, b in itertools.combinations(T, 2) if mate(a, b)]
    if any(len(set(p) | set(q)) == 4 for p, q in itertools.combinations(G, 2)):
        return 2
    return 1 if G else 0


# ---------------------------------------------------------------------------------------------------------------
# Edge covers and waste
# ---------------------------------------------------------------------------------------------------------------
def block_births(options):
    """options[f] = list of candidate splits of face f into two edge-variants; a split is [(edge, variant), (edge, variant)].
    For every choice of one split per face (exhaustively) compute: waste = number of edges used with exactly one sign variant,
    births_0 = sum over sources of (number of distinct edges at the source - 1), births_1 = sum over used edge variants of
    (number of faces using it - 1).  Returns the list of (births, waste, edges, births_0, births_1) over all choices."""
    res = []
    for ch in itertools.product(*[range(len(o)) for o in options]):
        used = defaultdict(set)
        cnt = Counter()
        for o, c in zip(options, ch):
            for e, v in o[c]:
                used[e].add(v)
                cnt[(e, v)] += 1
        deg = Counter(x for e in used for x in e)
        b0 = sum(d - 1 for d in deg.values())
        b1 = sum(u - 1 for u in cnt.values())
        res.append((b0 + b1, sum(1 for v in used.values() if len(v) == 1), len(used), b0, b1))
    return res


def face_splits(P, faces, kind):
    """per block: for each face of the block, its splits into two edge-variants, where an edge is a pair of sources and its
    variant the product of the face signs at its two ends.  kind 'tetrad': the one split into two pairs inside the two
    tetrads of the face; kind 'cross': the two splits whose pairs join the two tetrads."""
    tet = P['tet']
    byblk = defaultdict(list)
    for B, pat, rd in faces:
        s = dict(zip(B, pat))
        a = [x for x in B if tet[x] == tet[B[0]]]
        c = [x for x in B if tet[x] != tet[B[0]]]
        assert len(a) == 2 and len(c) == 2
        if kind == 'tetrad':
            splits = [[(a[0], a[1]), (c[0], c[1])]]
        else:
            splits = [[(a[0], c[0]), (a[1], c[1])], [(a[0], c[1]), (a[1], c[0])]]
        byblk[int(P['blk'][B[0]])].append([[(tuple(sorted(e)), s[e[0]] * s[e[1]]) for e in sp] for sp in splits])
    return byblk


def waste_min_all_splits(faces, tl=120):
    """CP-SAT: choose one of the 3 splits of every face into two pairs (the tetrad split and the two cross splits) so that the
    number of edges used with exactly one sign variant is minimal.  Returns (optimum, status name, number of candidate edges)."""
    m = cp_model.CpModel()
    var = {0: {}, 1: {}}                      # variant +1 -> 0, -1 -> 1 : edge -> Bool "variant used"

    def v(variant, e):
        d = var[0 if variant == 1 else 1]
        if e not in d:
            d[e] = m.NewBoolVar('')
        return d[e]

    for B, pat, rd in faces:
        s = dict(zip(B, pat))
        opts = []
        for part in ((0, 1), (0, 2), (0, 3)):
            e1 = tuple(sorted((B[part[0]], B[part[1]])))
            rest = [i for i in range(4) if i not in part]
            e2 = tuple(sorted((B[rest[0]], B[rest[1]])))
            z = m.NewBoolVar('')
            opts.append(z)
            for e in (e1, e2):
                m.AddImplication(z, v(s[e[0]] * s[e[1]], e))
        m.AddExactlyOne(opts)
    edges = set(var[0]) | set(var[1])
    obj = []
    for e in edges:
        a, b = v(1, e), v(-1, e)
        both = m.NewBoolVar('')
        m.Add(both <= a)
        m.Add(both <= b)
        obj.append(a + b - 2 * both)
    m.Minimize(sum(obj))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tl
    solver.parameters.num_workers = 4
    solver.parameters.random_seed = 1
    status = solver.Solve(m)
    return int(round(solver.ObjectiveValue())), solver.StatusName(status), len(edges)


def main():
    P = dg.p112()
    n, ports, Gm, ADJ, blk, tet = P['n'], P['ports'], P['Gm'], P['ADJ'], P['blk'], P['tet']
    word = dg.word531()
    ok = (all(int(ADJ[t].sum()) == 52 for t in range(n)) and Counter(blk.tolist()) == Counter({b: 8 for b in range(14)})
          and Counter(tet.tolist()) == Counter({x: 4 for x in range(28)})
          and all((bin(ports[s] & ports[t]).count('1') % 2 == 0) == bool(ADJ[t, s]) for s in range(n) for t in range(n) if s != t))
    check('D3.geometry', ok, '112 sources in 14 blocks of 8 (28 tetrads of 4), 52 readers each; two sources are adjacent iff their ports are orthogonal in F_2^9')

    # ===== faces: the block-local planes ========================================================================
    faces, census = block_local_faces(P)
    per_block = Counter(int(blk[f[0][0]]) for f in faces)
    ranks = Counter(f2_rank([ports[s] for s in f[0]]) for f in faces)
    tet_shape = Counter(tuple(sorted(Counter(int(tet[s]) for s in f[0]).values())) for f in faces)
    plane = all(ports[f[0][0]] ^ ports[f[0][1]] ^ ports[f[0][2]] ^ ports[f[0][3]] == 0 for f in faces)
    ok = (len(faces) == EXPECTED['faces'] and per_block == Counter({b: EXPECTED['faces_per_block'] for b in range(14)})
          and ranks == Counter({EXPECTED['face_rank']: 168}) and tet_shape == Counter({(2, 2): 168}) and plane
          and max(census) == EXPECTED['face_reach'])
    check('D3.faces', ok,
          '%d block-local faces of reach %d (%d per block; no block-local 4-set has a larger reach), four ports adding to 0 (rank %d), each made '
          'of 2 sources in each tetrad of its block' % (len(faces), EXPECTED['face_reach'], EXPECTED['faces_per_block'], EXPECTED['face_rank']))

    edges = {tuple(sorted(s for s in f[0] if tet[s] == t)) for f in faces for t in {int(tet[s]) for s in f[0]}}
    deg = Counter(s for e in edges for s in e)
    births0 = sum(d - 1 for d in deg.values())
    ok = (len(edges) == EXPECTED['edges'] and set(deg.values()) == {EXPECTED['edge_degree']} and len(deg) == 112 and births0 == EXPECTED['carriers'])
    check('D3.edges', ok, '%d tetrad edges, every source in %d of them: births of the sources %d = 2 x %d - 112'
          % (len(edges), EXPECTED['edge_degree'], births0, len(edges)))

    # ===== keys ================================================================================================
    kl = keys_of(faces, P)
    keys = [(tuple(sorted(faces[i][0] + faces[j][0])), i, j, rho, T) for i, j, rho, T in kl]
    uses = Counter()
    for _, i, j, _, _ in keys:
        uses[i] += 1
        uses[j] += 1
    kr = Counter(len(T) for *_, T in keys)
    krank = Counter(f2_rank([ports[s] for s in S8]) for S8, *_ in keys)
    ok = len(keys) == EXPECTED['keys'] and dict(kr) == EXPECTED['key_readers'] and Counter(uses.values()) == Counter(EXPECTED['face_uses']) \
        and len(uses) == 168 and dict(krank) == EXPECTED['key_rank']
    check('D3.keys', ok, '%d keys = pairs of planes of two blocks with 4 common readers (the only plane pairs with >= 3 common readers); '
          'every plane lies in exactly 2 keys; key frames have rank 5' % len(keys))

    def contains(Fa, Fb):
        return f2_rank(Fb + Fa) == f2_rank(Fb)

    cons = defaultdict(list)
    for S8, i, j, rho, T in keys:
        fr8 = [ports[s] for s in S8]
        cons[i].append(fr8)
        cons[j].append(fr8)
    width = Counter()
    for i, (a, b) in ((i, l[:2]) for i, l in cons.items()):
        width[2 if not (contains(a, b) or contains(b, a)) else 1] += 1
    copies = sum(w - 1 for w, c in width.items() for _ in range(c))
    ok = dict(width) == EXPECTED['nested_width'] and copies == EXPECTED['face_copies']
    check('D3.face-copies', ok, 'the frames of the two keys using a plane are not nested for %d/168 planes: %d face copies (= 2K - N2 = 2 x %d - %d)'
          % (width[2], copies, len(keys), len(faces)))

    mu = Counter(mate_matching(P, S8, list(T)) for S8, i, j, rho, T in keys)
    hosts = sum(len(T) - mate_matching(P, S8, list(T)) for S8, i, j, rho, T in keys) - word['report']['borrowed_output_pairs']
    ok = dict(mu) == EXPECTED['mate_matching'] and word['report']['borrowed_output_pairs'] == EXPECTED['borrowed'] and hosts == EXPECTED['hosts']
    check('D3.hosts', ok, 'the mates of the 4 readers of a key form a matching of size 2 for %d/168 keys: hosts R = sum(|T| - mu) - %d = %d'
          % (mu[2], EXPECTED['borrowed'], hosts))

    # ===== the ledger ==========================================================================================
    N2, K, R, waste = len(faces), len(keys), hosts, 0
    scratch, face, mcop = 2 * N2 - 112 + waste, 2 * K - N2, R - K
    B = N2 + K + R - 112 + waste
    ok = ((scratch, face, mcop) == EXPECTED['classes'] and B == scratch + face + mcop == EXPECTED['total'] == word['report']['R']
          and scratch == births0 and face == copies and len(edges) * 2 - 112 == scratch)
    check('D3.ledger', ok, 'B = N2 + K + R - 112 + waste = %d + %d + %d - 112 + %d = %d = helper count of the word of PR #531; classes: %d scratch '
          '(carriers), %d face copies, %d M copies; the identity agrees with the direct counts %d (source births) and %d (face copies)'
          % (N2, K, R, waste, B, scratch, face, mcop, births0, copies))

    # ===== carriers are register-neutral ==========================================================================
    tet_b = face_splits(P, faces, 'tetrad')
    cross_b = face_splits(P, faces, 'cross')
    base = [block_births(tet_b[b]) for b in range(14)]
    best_tet = [min(r) for r in base]
    cross = [block_births(cross_b[b]) for b in range(14)]
    best = [min(r) for r in cross]
    identity = all(r[0] == 2 * 12 - 8 + r[1] for blk_res in (base + cross) for r in blk_res)       # births = 2 N2 - 8 + waste, per block
    total_tet = sum(x[0] for x in best_tet)
    total_cross = sum(x[0] for x in best)
    ok = (tuple(best[0]) == EXPECTED['cross_block_best'] and len(set(best)) == 1 and total_tet == EXPECTED['carriers']
          and total_cross == EXPECTED['cross_total'] and total_cross - total_tet == EXPECTED['cross_extra']
          and all(x[1] == 0 for x in best_tet) and sum(x[1] for x in best) == 14 * EXPECTED['cross_waste'] and identity)
    check('D3.carriers-neutral', ok,
          'the same 168 planes rebuilt from edges joining the two tetrads of a block cost %d registers instead of %d: +%d (%d wasted single-variant '
          'butterflies per block, optimal over all 2^12 choices of split); for every choice births = 2 N2 - 112 + waste, tetrad edges waste 0'
          % (total_cross, total_tet, total_cross - total_tet, best[0][1]))

    opt, status, nedges = waste_min_all_splits(faces)
    check('D3.waste-min', (opt, status, nedges) == (EXPECTED['waste_min'], 'OPTIMAL', EXPECTED['candidate_edges']),
          'CP-SAT over all 3 splits of every plane (%d candidate edges): minimum waste %d, status %s (the tetrad splits attain it)'
          % (nedges, opt, status))


main()
finish()
