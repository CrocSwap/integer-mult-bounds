#!/usr/bin/env python3
# Predecessors: navinor (PR1084, research/bit-orthogonal-pair-decoders: orthogonal-pair label decoders, F2 dual
# roots, section G method), eumemic (PR555, research/e8-bit-p111: gen_p3.py, the frozen L3 plan, eligibility and
# decoder rules, discovery/choose.py), DreamingOfClouds (PR589 tuned word, PR545 punctured-star unit and rank-mass
# identity); PR493 skeleton geometry (e8.py / geom.py line order and D4 partition) by eumemic.
# Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
"""Exact census of F2 dual roots over the admissible reader sets P of the frozen PR555 L3 punctured-star family.

Question.  PR1084 (section G) showed that for the shipped puncture P = [10, 15, 51, 53, 56, 66, 72, 89, 111] exactly
one of the nine F2 dual functionals of the label readers lambda_a (a in P) is a root label lambda_b with b live.
Puncturing that b gives P110 (decoder constant 62).  A reader set with j live root duals would give, by puncturing
all of them, a P_(111-j) label decoder of constant 63 - j; j = 9 is a P102 (54) system.  Which j are attainable by the
reader sets that PR555's generator gen_p3.py can host under the frozen plan data/plan-l3.json?

Admissibility of a 9-line reader set P (read from gen_p3.py, discovery/choose.py and research/e8-bit-p111/README.md):
  (E)  construction rule (gen_p3.build asserts it for every p in P before any gate is emitted):
       gen_p3.eligible -- both (z,z) cells of p's 4-frame contain p, and kline(p) is not in the cell {p, qhost(p)}.
       It reads keepline only at d-cells (set from kline, independent of the plan_thirds free lines).
  (Z)  construction rule (discovery/choose.py, README 'The word'): lines 0..7 stay live (PR493's frame-zero
       residual isometry uses them).
  (A)  decoder rule (necessary for ANY label decoder of the nine totals; gen_p3.decoder_rows asserts it after the
       word is built): the nine classes of P in E8/2E8 are affinely independent, equivalently B0[P,P] is invertible
       over F2, equivalently every live row (1 + B(t,.))|live lies in the span of the totals HYP[p]|live.
  (B2) "P meets at least two block pairs": implied by (A) (a complementary D4 pair has affine rank 7 < 9); checked.
  (F)  "one line per 4-frame": implied by (E) (both (z,z) cells of a frame contain p); checked.
  No other P-dependent rule is asserted by gen_p3.build before word construction; its later construction-time
  checks (mini-node keepers, block-node realisation, extra-carrier loop) are not replayed here (the pinned e8.py
  needs numpy, which this stdlib census does not use).

Census.  All C(19, 9) = 92378 nine-subsets of the eligible set are enumerated.  For each invertible B0[P,P] the
dual functionals s_k = sum_m inv[k][m] lambda_{a_m} (PR1084 section G) are compared with the 120 root labels.
j(P) = number of k whose s_k is lambda_b for a live b (b not in P; then automatically b perp a_k and
<a_j, b> = +-1 for j != k).  j_restricted(P) additionally requires b outside lines 0..7.

usage: python3 -I -B census.py [--out PATH] [--check]
  --check   regenerate and compare byte for byte with the existing CENSUS.json (no write)
Last stdout line: PASS_BIT_P102_ELIGIBLE_CENSUS ... ; exit status nonzero on any failed check.
"""
import argparse
import gzip
import hashlib
import itertools
import json
import sys
import types
from collections import Counter
from fractions import Fraction
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
N = 120
FULL = (1 << N) - 1

PINNED = {
    # executed verbatim (derive / eligible) with numpy-free stub dependencies
    'research/e8-bit-p111/code/gen_p3.py': '438b83f10d70ceca7cf78049420204b7de2dc61682f913c50a62596106ad84cd',
    'research/e8-bit-p111/code/planio.py': 'c0a687f61aed29455cea953d8a3e49a32136edb3cd4213c46880c146a6ca7fa3',
    # frozen PR555 inputs
    'research/e8-bit-p111/data/plan-l3.json': 'd5c2494b4baae801143049e172db303b3c8e25a002e9d9715a1d79dcb2d74c58',
    'research/e8-bit-p111/data/punct.json': 'dd371e1d6fe57602f242920b582ec4c133efc8ede4a849fd701ac90b7f6e1853',
    'research/e8-bit-carrier-skeleton/data/skeleton/d4part-pairs.json':
        'd69ffe3326140bc541b8f1639e02db43a5835ab8ca02cc742b5bee2bf2ef1ba9',
    # rule / ordering sources (hashed; their numpy code is re-implemented here, not executed)
    'research/e8-bit-p111/discovery/choose.py': '18d77e8f62ffc671b3b3d3e50626c03481a2eaf6fb4abbc131e08226feebc180',
    'research/e8-bit-p111/README.md': '481431e35bd831ec3d0bb8edc01abdfa49d5caeabebab67ac839a35053e9ef85',
    'research/e8-bit-carrier-skeleton/code/skeleton/e8.py':
        '721d859a6517d665ca84d03ef89668da3aae7433ffb0ee47faf37f2aeb85450e',
    'research/e8-bit-carrier-skeleton/code/skeleton/geom.py':
        'bb356568fa05e7bfd5fcd9012903611cf742729a99b4dc3a13685355b2678ae3',
    # the selected PR589 word (same SHA-256 as PR1084 SOURCES.json pricing_inputs) and PR1084's receipt
    'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz':
        'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f',
    'research/bit-orthogonal-pair-decoders/RESULTS.json':
        '7f3d6df3ab4dd9fd4a94ab36c444d777f1b45bf8a25ee880d6c1d8a363362e33',
    'research/bit-orthogonal-pair-decoders/verify.py':
        '512df34b78791155d15467d1036a4fe217b007f40126abdcdc8a31c24ca94b1b',
}
SHIPPED_P = [10, 15, 51, 53, 56, 66, 72, 89, 111]
R_SHIPPED = 439
JLIST = 4            # every admissible P with j >= JLIST is listed and replayed exactly

CHECKS = []


def check(tag, cond, info=''):
    ok = bool(cond)
    CHECKS.append([tag, ok])
    print(('PASS ' if ok else 'FAIL ') + tag + (': ' + info if info else ''), flush=True)
    return ok


_BYTES = {}


def read_pinned(rel):
    if rel not in _BYTES:
        data = (REPO / rel).read_bytes()
        got = hashlib.sha256(data).hexdigest()
        if got != PINNED[rel]:
            print('FAIL input-pin ' + rel + ' sha256 ' + got + ' != ' + PINNED[rel], flush=True)
            print('FAIL_BIT_P102_ELIGIBLE_CENSUS input pin mismatch', flush=True)
            sys.exit(2)
        _BYTES[rel] = data
    return _BYTES[rel]


# ---------------------------------------------------------------- geometry (e8.py order, exact integers)
def e8_lines_hamming():
    """Re-implementation of e8._roots_hamming + the LINES loop of the pinned e8.py (#370 order, E8COORD=ham)."""
    g = [(1, 1, 1, 1, 0, 0, 0, 0), (1, 1, 0, 0, 1, 1, 0, 0), (1, 0, 1, 0, 1, 0, 1, 0), (0, 1, 1, 0, 1, 0, 0, 1)]
    H = [tuple(sum(a[k] * g[k][i] for k in range(4)) % 2 for i in range(8)) for a in itertools.product((0, 1), repeat=4)]
    R = []
    for i in range(8):
        for sg in (2, -2):
            v = [0] * 8
            v[i] = sg
            R.append(tuple(v))
    for w in H:
        if sum(w) == 4:
            idx = [i for i in range(8) if w[i]]
            for sg in itertools.product((1, -1), repeat=4):
                v = [0] * 8
                for i, s_ in zip(idx, sg):
                    v[i] = s_
                R.append(tuple(v))
    lines, seen = [], set()
    for r in R:
        if r in seen:
            continue
        neg = tuple(-a for a in r)
        seen.add(r)
        seen.add(neg)
        lines.append(r if [a for a in r if a][0] > 0 else neg)
    return lines


LINES = e8_lines_hamming()


def ip(x, y):
    return sum(a * b for a, b in zip(x, y))


def gram_from_lines():
    out = []
    for x in LINES:
        row = []
        for y in LINES:
            d = ip(x, y)
            assert d % 2 == 0
            row.append(d // 2)                       # <x,y>/2, the word's 'form'
        out.append(row)
    return out


def bits(mask):
    out = []
    while mask:
        b = mask & -mask
        out.append(b.bit_length() - 1)
        mask ^= b
    return out


def mask_of(idx):
    m = 0
    for j in idx:
        m |= 1 << j
    return m


def b0_rows(G):
    """lambda_a codewords: ROW[a] bit b = (1 + G[a][b]) mod 2 (PR1084 B0)."""
    return [sum(((1 + G[a][b]) % 2) << b for b in range(N)) for a in range(N)]


def hyp_rows(G):
    return [sum(1 << b for b in range(N) if G[t][b] == 0) for t in range(N)]


def f2_rank(vecs):
    basis = []
    for v in vecs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def f2_span_reduce(basis, v):
    for b in basis:
        v = min(v, v ^ b)
    return v


def f2_inverse_bits(M):
    """M: list of n row bitmasks (bit k = column k).  Returns the inverse as row bitmasks, or None if singular."""
    n = len(M)
    a = [M[i] | (1 << (n + i)) for i in range(n)]
    for c in range(n):
        p = next((i for i in range(c, n) if a[i] >> c & 1), None)
        if p is None:
            return None
        a[c], a[p] = a[p], a[c]
        for i in range(n):
            if i != c and a[i] >> c & 1:
                a[i] ^= a[c]
    return [r >> n for r in a]


def gram_integrity(G):
    """Exact integrity of a Gram matrix against the line list (detects corrupted entries)."""
    ref = gram_from_lines()
    sym = all(G[i][j] == G[j][i] for i in range(N) for j in range(N))
    counts = all(sum(1 for b in range(N) if G[a][b] == 0) == 63 and sum(1 for b in range(N) if abs(G[a][b]) == 1) == 56
                 for a in range(N))
    return dict(equals_lines=(G == ref), symmetric=sym, orth63_odd56=counts, b0_f2_rank=f2_rank(b0_rows(G)))


def gram_digest(G):
    return hashlib.sha256(json.dumps(G, separators=(',', ':')).encode()).hexdigest()


# ---------------------------------------------------------------- exact rational ranks (cost verification)
def independent(vectors):
    echelon, out = [], []
    for v in vectors:
        r = [Fraction(x) for x in v]
        for p, b in echelon:
            if r[p]:
                f = r[p]
                r = [x - f * y for x, y in zip(r, b)]
        piv = next((i for i, x in enumerate(r) if x), None)
        if piv is not None:
            echelon.append((piv, [x / r[piv] for x in r]))
            out.append(v)
            if len(out) == 8:
                break
    return out


def rank_q(rows):
    rows = [[Fraction(x) for x in v] for v in rows]
    rank, ncol = 0, len(rows[0]) if rows else 0
    for c in range(ncol):
        piv = next((i for i in range(rank, len(rows)) if rows[i][c] != 0), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i][c] != 0:
                f = rows[i][c] / rows[rank][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def pair_cost(rmask, smask):
    """rank_Q of the Gram pairing between span(reader lines) and span(source lines) (PR446 Theorem C price)."""
    br = independent([LINES[i] for i in bits(rmask)])
    bs = independent([LINES[i] for i in bits(smask)])
    if not br or not bs:
        return 0
    return rank_q([[ip(x, y) for y in bs] for x in br])


# ---------------------------------------------------------------- geometry of the skeleton (geom.py subset)
class GeomLite:
    """The attributes of geom.Geom that gen_p3.derive / gen_p3.eligible read (blocks, blk, comp, frames4, phi,
    cells, cmask, cblk), rebuilt with exact integers from the pinned D4 partition (geom.py order)."""

    def __init__(self, D4, G):
        assert sorted(x for m in D4 for x in bits(m)) == list(range(N))
        self.blocks = list(D4)
        self.blk = {x: i for i, m in enumerate(D4) for x in bits(m)}

        def perp(mask):
            idx = bits(mask)
            return mask_of(b for b in range(N) if all(G[b][i] == 0 for i in idx))

        self.comp = {i: [j for j, m2 in enumerate(D4) if m2 == perp(m)][0] for i, m in enumerate(D4)}

        def d4_frames(m):
            ls = bits(m)
            out = [q for q in itertools.combinations(ls, 4)
                   if all(G[x][y] == 0 for x, y in itertools.combinations(q, 2))]
            assert len(out) == 3
            return out

        self.frames4 = [tuple(sorted(f)) for m in D4 for f in d4_frames(m)]
        self.phi = {x: f for f in self.frames4 for x in f}
        self.cells = [tuple(sorted(p)) for f in self.frames4 for p in itertools.combinations(f, 2)]
        self.cmask = {c: (1 << c[0]) | (1 << c[1]) for c in self.cells}
        self.cblk = {c: self.blk[c[0]] for c in self.cells}


class _GIView:
    def __init__(self, G):
        self.G = G

    def __getitem__(self, ij):
        return self.G[ij[0]][ij[1]]


def _unavailable(*a, **k):
    raise RuntimeError('not available in the numpy-free census stub')


def load_pinned_module(rel, name, extra_modules):
    """Execute the exact pinned bytes of a repository module with the given stub modules in sys.modules."""
    data = read_pinned(rel)
    mod = types.ModuleType(name)
    mod.__file__ = str(REPO / rel)
    saved_mods = {k: sys.modules.get(k) for k in extra_modules}
    saved_path = list(sys.path)
    try:
        sys.modules.update(extra_modules)
        exec(compile(data, str(REPO / rel), 'exec'), mod.__dict__)
    finally:
        sys.path[:] = saved_path
        for k, v in saved_mods.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return mod


def load_gen_p3(G, HYP):
    e8s = types.ModuleType('e8')
    e8s.V, e8s.GI, e8s.HYP, e8s.bits, e8s.FULL, e8s.LINES = N, _GIView(G), HYP, bits, FULL, LINES
    e8s.closure = e8s.dim = e8s.perp = _unavailable
    stubs = {'e8': e8s}
    for name, attrs in (('geom', ('Geom',)), ('gen', ('span_add',)), ('wordkit', ('save', 'solve_transform_lu')),
                        ('nodeopt', ('realise',)), ('pwordl', ('PWordL',))):
        m = types.ModuleType(name)
        for a in attrs:
            setattr(m, a, _unavailable)
        stubs[name] = m
    planio = load_pinned_module('research/e8-bit-p111/code/planio.py', 'planio', {})
    stubs['planio'] = planio
    gen_p3 = load_pinned_module('research/e8-bit-p111/code/gen_p3.py', 'gen_p3_pinned', stubs)
    return gen_p3, planio


# ---------------------------------------------------------------- the census core
def duals_of(P, ROW, ROWIDX):
    """PR1084 section G: s_k = sum_m inv(B0[P,P])[k][m] lambda_{a_m}.  Returns None if B0[P,P] is singular, else
    the list of (codeword s_k, root line b or None)."""
    M = [sum((ROW[a] >> c & 1) << k for k, c in enumerate(P)) for a in P]
    inv = f2_inverse_bits(M)
    if inv is None:
        return None
    out = []
    for k in range(9):
        acc = 0
        for m in range(9):
            if inv[k] >> m & 1:
                acc ^= ROW[P[m]]
        out.append((acc, ROWIDX.get(acc)))
    return out


def analyse(P, G, ROW, ROWIDX):
    """Exact per-P record: dual roots, live root duals (j), partner orthogonality, distinctness, lines 0..7."""
    d = duals_of(P, ROW, ROWIDX)
    if d is None:
        return None
    Pset = set(P)
    live_pairs, self_terms, nonroot = [], [], []
    for k, (cw, b) in enumerate(d):
        if b is None:
            nonroot.append(k)
        elif b in Pset:
            self_terms.append(k)
            assert b == P[k]                     # a dual in P can only be the term's own reader line
        else:
            live_pairs.append((P[k], b))
    # duality, orthogonality and distinctness, re-checked from the Gram matrix directly
    duality = all(((1 + G[P[jj]][b]) % 2) == (1 if P[jj] == a else 0) for a, b in live_pairs for jj in range(9))
    orth = all(G[a][b] == 0 for a, b in live_pairs)
    dead = sorted(b for _, b in live_pairs)
    distinct = len(set(dead)) == len(dead) and not (set(dead) & Pset)
    low = [b for b in dead if b < 8]
    return dict(j=len(live_pairs), j_restricted=len(dead) - len(low), pairs=sorted(live_pairs), dead=dead,
                self_terms=len(self_terms), nonroot_terms=len(nonroot), duality=duality, orth=orth,
                distinct=distinct, dead_in_0_7=low, codewords=[cw for cw, _ in d])


def decoder_rows_ok(P, ROW, HYP, extra=()):
    """gen_p3.decoder_rows condition, stdlib form: every live row (1 + B(t,.))|live lies in the F2 span of the nine
    totals HYP[p]|live."""
    live = FULL & ~mask_of(list(P) + list(extra))
    basis = []
    for p in P:
        v = f2_span_reduce(basis, HYP[p] & live)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return all(f2_span_reduce(basis, ROW[t] & live) == 0 for t in bits(live))


def exact_extension(P, rec, ROW):
    """Puncture P plus all live root duals; verify the label decoder identity on every live line and price each term
    by the exact rational pairing rank."""
    ext = list(P) + rec['dead']
    live = FULL & ~mask_of(ext)
    srcs = rec['codewords']
    ident = True
    for t in bits(live):
        acc = 0
        for k, a in enumerate(P):
            if ROW[a] >> t & 1:
                acc ^= srcs[k]
        if (acc ^ ROW[t]) & live:
            ident = False
            break
    costs = [pair_cost(ROW[a] & live, srcs[k] & live) for k, a in enumerate(P)]
    return dict(v=bin(live).count('1'), identity=ident, costs=costs, cst=sum(costs))


def class_affine_rank(lines, ROW):
    return f2_rank([ROW[a] for a in lines])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(HERE / 'CENSUS.json'))
    ap.add_argument('--check', action='store_true', help='compare with the existing CENSUS.json instead of writing')
    args = ap.parse_args(argv)
    if not __debug__:
        print('FAIL_BIT_P102_ELIGIBLE_CENSUS refuse -O (assertions are part of the checks)')
        sys.exit(2)

    for rel in PINNED:
        read_pinned(rel)
    check('pins', len(_BYTES) == len(PINNED), '%d input files match their pinned SHA-256' % len(PINNED))

    # ------------------------------------------------ geometry
    G = gram_from_lines()
    integ = gram_integrity(G)
    check('geom.lines', len(LINES) == N and len(set(LINES)) == N and all(ip(v, v) == 4 for v in LINES),
          '120 E8 lines in Hamming coordinates (e8.py order), norm 4, form <x,y>/2')
    check('geom.gram', integ['symmetric'] and integ['orth63_odd56'] and all(G[i][i] == 2 for i in range(N)),
          'Gram entries 2 / 0 / +-1; 63 orthogonal and 56 odd partners per line')
    ROW = b0_rows(G)
    HYP = hyp_rows(G)
    ROWIDX = {r: a for a, r in enumerate(ROW)}
    code = [0]
    basis = []
    for r in ROW:
        v = f2_span_reduce(basis, r)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    for b in basis:
        code += [w ^ b for w in code]
    weights = Counter(bin(w).count('1') for w in code)
    check('geom.b0', len(basis) == 9 and len(ROWIDX) == N and
          weights == Counter({0: 1, 56: 255, 64: 255, 120: 1}),
          'B0 = (1+G) mod 2: F2 rank 9, code 1 + 255z^56 + 255z^64 + z^120, 120 distinct root labels (PR1084 A)')
    check('geom.hyp', all(HYP[t] | (1 << t) == ROW[t] for t in range(N)),
          'HYP[p] | {p} = R(lambda_p), so a total HYP[p]|live equals lambda_p on the live lines')

    # the word's own labels pin the ordering
    word = json.loads(gzip.decompress(read_pinned('research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz')))
    check('geom.word-order', word['coords'] == 'ham' and word['form'] == '<x,y>/2' and word['v'] == 111 and
          word['R'] == R_SHIPPED and len(word['ports_geom']) == 111 and
          all(tuple(word['lines'][i]) == LINES[g] for i, g in enumerate(word['ports_geom'])) and
          sorted(set(range(N)) - set(word['ports_geom'])) == SHIPPED_P == sorted(word['punctured']),
          'PR589 word: its 111 labels are LINES[ports_geom] exactly; punctured = ' + str(SHIPPED_P) + ', R = 439')
    punct = json.loads(read_pinned('research/e8-bit-p111/data/punct.json'))
    check('geom.punct', sorted(punct['punctured']) == SHIPPED_P, 'frozen data/punct.json gives the same P')

    # ------------------------------------------------ skeleton geometry and eligibility
    D4 = [int(h, 16) for h in json.loads(read_pinned('research/e8-bit-carrier-skeleton/data/skeleton/d4part-pairs.json'))]
    GL = GeomLite(D4, G)
    check('geom.skeleton', len(GL.blocks) == 10 and len(GL.frames4) == 30 and len(GL.cells) == 180 and
          all(GL.comp[GL.comp[i]] == i != GL.comp[i] for i in range(10)),
          '10 D4 blocks in 5 complementary pairs, 30 orthogonal 4-frames, 180 cells')
    gen_p3, planio = load_gen_p3(G, HYP)
    plan_raw = json.loads(read_pinned('research/e8-bit-p111/data/plan-l3.json'))
    sol = planio.load_plan(str(REPO / 'research/e8-bit-p111/data/plan-l3.json'))
    sol_own = dict(partner={t: x for t, x in plan_raw['partner']}, kline={t: l for t, l in plan_raw['kline']},
                   qhost={t: x for t, x in plan_raw['qhost']})
    check('plan.load', all(sol[k] == sol_own[k] for k in sol_own) and all(len(sol_own[k]) == N for k in sol_own),
          'pinned planio.load_plan agrees with a direct parse of the hashed plan bytes (partner, kline, qhost)')
    dcellof, keepline, home, qhostD6, zz = gen_p3.derive(GL, sol)
    elig_g = [p for p in range(N) if gen_p3.eligible(GL, sol, dcellof, keepline, qhostD6, zz, p)[0]]
    # independence of the plan_thirds free lines: derive with every non-d-cell keeping its second line
    fl1 = {c: 1 for c in GL.cells}
    d1 = gen_p3.derive(GL, sol, fl1)
    elig_g1 = [p for p in range(N) if gen_p3.eligible(GL, sol, d1[0], d1[1], d1[3], d1[4], p)[0]]
    # independent re-implementation of the rule
    elig_own = []
    for p in range(N):
        f = GL.phi[p]
        hosted = {tuple(sorted((t, sol_own['qhost'][t]))) for t in f}
        zzf = [c for c in itertools.combinations(f, 2) if c not in hosted]
        kl = sol_own['kline'][p]
        if len(zzf) == 2 and all(p in c for c in zzf) and kl not in (p, sol_own['qhost'][p]):
            elig_own.append(p)
    ELIG = elig_g
    ELIG18 = [p for p in ELIG if p >= 8]
    LOW = [p for p in ELIG if p < 8]
    check('elig.gen_p3', elig_g == elig_own == elig_g1,
          'pinned gen_p3.eligible = independent re-implementation, and independent of the plan_thirds free lines')
    check('elig.count', len(ELIG) == 19 and len(ELIG18) == 18,
          '19 eligible lines, 18 outside 0..7 (README "The word"): ' + str(ELIG))
    check('elig.frames', len({GL.phi[p] for p in ELIG}) == len(ELIG),
          'at most one eligible line per 4-frame (both (z,z) cells contain p), so "one per 4-frame" is implied')
    check('elig.pr545-39', 39 not in ELIG, "#545's line 39 is not eligible under #543's plan (README)")
    check('elig.shipped', set(SHIPPED_P) <= set(ELIG18), 'shipped P is eligible and avoids lines 0..7')

    # class geometry claims of choose.py / README: block affine rank, complementary pair affine rank 7
    blk_ar = sorted({class_affine_rank(bits(m), ROW) for m in D4})
    pair_ar = sorted({class_affine_rank(bits(D4[i] | D4[GL.comp[i]]), ROW) for i in range(10)})
    check('geom.class-ranks', pair_ar == [7],
          'affine rank of E8/2E8 classes: each D4 block %s, each complementary pair %s (< 9: (A) implies >= 2 pairs)'
          % (blk_ar, pair_ar))

    BROW = [sum((G[t][b] & 1) << b for b in range(N)) for t in range(N)]

    def pairs_met(P):
        return len({min(GL.blk[p], GL.comp[GL.blk[p]]) for p in P})

    # ------------------------------------------------ enumeration
    universe = list(itertools.combinations(ELIG, 9))
    check('census.size', len(universe) == comb(19, 9) == 92378, 'C(19,9) = 92378 nine-subsets enumerated')
    stats = Counter()
    jdist, jdist_r, jdist19, jdist19_r = Counter(), Counter(), Counter(), Counter()
    selfdist, nonrootdist = Counter(), Counter()
    dead_freq = Counter()
    agree_affine = agree_choose = True
    implied_pairs = True
    per_p_ok = True
    table = []
    by_j = {}
    first_dependent = None
    for P in universe:
        P = list(P)
        uses_low = P[0] < 8
        ar = f2_rank([ROW[p] for p in P])
        ch = f2_rank([(1 << N) | BROW[p] for p in P])          # discovery/choose.py affine_ok
        rec = analyse(P, G, ROW, ROWIDX)
        if (rec is not None) != (ar == 9):
            agree_affine = False
        if (ch == 9) != (ar == 9):
            agree_choose = False
        if rec is None:
            stats['dependent_19'] += 1
            if not uses_low:
                stats['dependent_18'] += 1
                if first_dependent is None:
                    first_dependent = P
            if pairs_met(P) < 2:
                stats['fewer_than_two_pairs_19'] += 1
            continue
        if pairs_met(P) < 2:
            implied_pairs = False
        if not (rec['duality'] and rec['orth'] and rec['distinct']):
            per_p_ok = False
        stats['admissible_19'] += 1
        jdist19[rec['j']] += 1
        jdist19_r[rec['j_restricted']] += 1
        if uses_low:
            continue
        stats['admissible_18'] += 1
        jdist[rec['j']] += 1
        jdist_r[rec['j_restricted']] += 1
        selfdist[rec['self_terms']] += 1
        nonrootdist[rec['nonroot_terms']] += 1
        for b in rec['dead']:
            dead_freq[b] += 1
        table.append('%s:%s' % (','.join(map(str, P)), ','.join('%d-%d' % ab for ab in rec['pairs'])))
        by_j.setdefault(rec['j'], []).append(P)
    ADM = stats['admissible_18']
    check('census.affine', agree_affine and agree_choose,
          'B0[P,P] invertible <=> rank{lambda_p} = 9 <=> choose.py affine_ok, on all 92378 subsets')
    check('census.two-pairs', implied_pairs and stats['fewer_than_two_pairs_19'] <= stats['dependent_19'],
          'every affinely independent P meets >= 2 block pairs (the README rule is implied by (A))')
    check('census.partners', per_p_ok,
          'every live root dual b_k: B0[a_j,b_k] = delta_jk re-checked on G, a_k perp b_k (cost-6 pair), all distinct, '
          'none in P')
    check('census.counts', ADM == sum(jdist.values()) and stats['admissible_19'] == sum(jdist19.values()) and
          ADM + stats['dependent_18'] == comb(18, 9),
          'admissible (E,Z,A) = %d of C(18,9) = %d; decoder-only (E,A) on all 19 eligible = %d of 92378'
          % (ADM, comb(18, 9), stats['admissible_19']))
    jmax = max(jdist)
    jmax_r = max(jdist_r)
    jmax19 = max(jdist19)

    # ------------------------------------------------ examples with the largest j (lexicographic within j)
    examples = []
    for j in sorted(by_j, reverse=True):
        for P in sorted(by_j[j]):
            if len(examples) == 5:
                break
            rec = analyse(P, G, ROW, ROWIDX)
            ext = exact_extension(P, rec, ROW)
            dec = decoder_rows_ok(P, ROW, HYP) and decoder_rows_ok(P, ROW, HYP, rec['dead'])
            want = sorted([6] * rec['j'] + [7] * (9 - rec['j']))
            ok = ext['identity'] and sorted(ext['costs']) == want and ext['v'] == 111 - rec['j'] and dec
            check('example.%s' % '-'.join(map(str, P)), ok,
                  'j = %d, dead duals %s: decoder identity on %d live lines, costs %s, cst %d'
                  % (rec['j'], rec['dead'], ext['v'], sorted(ext['costs']), ext['cst']))
            examples.append(dict(P=P, j=rec['j'], j_restricted=rec['j_restricted'], dead_duals=rec['dead'],
                                 pairs=[list(ab) for ab in rec['pairs']], dead_in_0_7=rec['dead_in_0_7'],
                                 blocks=[GL.blk[p] for p in P], block_pairs_met=pairs_met(P),
                                 extension=dict(v=ext['v'], cst=ext['cst'], costs=ext['costs'],
                                                decoder_identity=ext['identity'], gen_p3_decoder_rows=dec),
                                 hosting_wall_R439_nine_stage=dict(capacity_4v=4 * ext['v'],
                                                                   holds=R_SHIPPED <= 4 * ext['v'])))

    # ------------------------------------------------ every admissible P with j >= JLIST: exact extension replay
    high = []
    high_ok = True
    for j in sorted(by_j, reverse=True):
        if j < JLIST:
            continue
        for P in sorted(by_j[j]):
            rec = analyse(P, G, ROW, ROWIDX)
            ext = exact_extension(P, rec, ROW)
            want = sorted([6] * rec['j'] + [7] * (9 - rec['j']))
            high_ok &= ext['identity'] and sorted(ext['costs']) == want and ext['v'] == 111 - j
            high.append(dict(P=P, j=j, j_restricted=rec['j_restricted'], dead_duals=rec['dead'], v=ext['v'],
                             cst=ext['cst'], block_pairs_met=pairs_met(P)))
    check('census.high-j-replay', high_ok and len(high) == sum(v for k, v in jdist.items() if k >= JLIST),
          'all %d admissible P with j >= %d: decoder identity on every live line of P + dead duals, exact rational '
          'pairing ranks = 6 on the j orthogonal pairs and 7 elsewhere (cst = 63 - j)' % (len(high), JLIST))

    # ------------------------------------------------ positive control: the shipped P (PR1084 section G)
    res1084 = json.loads(read_pinned('research/bit-orthogonal-pair-decoders/RESULTS.json'))['shipped']
    vec_index = {v: i for i, v in enumerate(LINES)}
    a_exp = vec_index[tuple(res1084['dual_root']['a'])]
    b_exp = vec_index[tuple(res1084['dual_root']['b'])]
    srec = analyse(SHIPPED_P, G, ROW, ROWIDX)
    sext = exact_extension(SHIPPED_P, srec, ROW)
    s111 = [pair_cost(ROW[a] & (FULL & ~mask_of(SHIPPED_P)), srec['codewords'][k] & (FULL & ~mask_of(SHIPPED_P)))
            for k, a in enumerate(SHIPPED_P)]
    orth_pairs = sum(1 for x in SHIPPED_P for y in SHIPPED_P if x != y and G[x][y] == 0)
    ship_ok = (srec['j'] == 1 and srec['pairs'] == [(a_exp, b_exp)] and
               sorted(tuple(LINES[p]) for p in SHIPPED_P) == sorted(tuple(v) for v in res1084['punctured']) and
               orth_pairs == res1084['ordered_orthogonal_pairs'] == 44 and s111 == [7] * 9 and
               sorted(sext['costs']) == sorted(res1084['P110_costs']) == [6] + [7] * 8 and sext['v'] == 110 and
               sext['identity'] and decoder_rows_ok(SHIPPED_P, ROW, HYP) and
               decoder_rows_ok(SHIPPED_P, ROW, HYP, srec['dead']) and sext['cst'] == 62)
    ship_ok = ship_ok and srec['j_restricted'] == 1 and SHIPPED_P in by_j.get(1, [])
    check('control.shipped', ship_ok,
          'shipped P: admissible, j = 1, dual pair (a, b) = (%d, %d) = PR1084 RESULTS dual_root %s / %s; 44 ordered '
          'orthogonal pairs; P111 costs 9 x 7; P110 costs %s, v = 110' %
          (a_exp, b_exp, res1084['dual_root']['a'], res1084['dual_root']['b'], sorted(sext['costs'])))
    shipped = dict(P=SHIPPED_P, j=srec['j'], dual_root=dict(a=a_exp, b=b_exp, a_vec=list(LINES[a_exp]),
                                                         b_vec=list(LINES[b_exp]), G_ab=G[a_exp][b_exp]),
                   P111_costs=s111, P110=dict(v=sext['v'], costs=sext['costs'], cst=sext['cst']),
                   ordered_orthogonal_pairs=orth_pairs)

    # ------------------------------------------------ negative controls
    def admissible(P):
        """(ok, reasons) under the full rule set (E), (Z), (A)."""
        reasons = []
        if len(set(P)) != 9:
            reasons.append('not nine distinct lines')
        bad = [p for p in P if not gen_p3.eligible(GL, sol, dcellof, keepline, qhostD6, zz, p)[0]]
        if bad:
            reasons.append('not eligible: %s' % bad)
        if any(p < 8 for p in P):
            reasons.append('uses lines 0..7')
        if duals_of(sorted(P), ROW, ROWIDX) is None:
            reasons.append('affinely dependent (B0[P,P] singular)')
        return (not reasons), reasons

    controls = {}
    ok_ship, _ = admissible(SHIPPED_P)
    # (1) a non-eligible line substituted into the shipped P, keeping affine independence
    sub = None
    for q in range(8, N):
        if q in ELIG or q in SHIPPED_P:
            continue
        P1 = sorted(SHIPPED_P[1:] + [q])
        if duals_of(P1, ROW, ROWIDX) is not None:
            sub = (q, P1)
            break
    ok1, why1 = admissible(sub[1])
    controls['non_eligible_substitution'] = dict(P=sub[1], substituted=sub[0], removed=SHIPPED_P[0],
                                                 rejected=not ok1, reasons=why1)
    c1 = ok_ship and not ok1 and why1 == ['not eligible: [%d]' % sub[0]]
    # (2) an affinely dependent P from the eligible set (first in lexicographic order)
    ok2, why2 = admissible(first_dependent)
    dec2 = decoder_rows_ok(first_dependent, ROW, HYP)
    controls['affinely_dependent'] = dict(P=first_dependent, rejected=not ok2, reasons=why2,
                                          gen_p3_decoder_rows_condition=dec2,
                                          f2_rank=f2_rank([ROW[p] for p in first_dependent]))
    c2 = not ok2 and why2 == ['affinely dependent (B0[P,P] singular)'] and not dec2
    # (3) a corrupted Gram entry: the shipped dual pair (a, b) made odd (G[a][b] = G[b][a] = 1)
    Gc = [row[:] for row in G]
    Gc[a_exp][b_exp] = Gc[b_exp][a_exp] = 1
    integ_c = gram_integrity(Gc)
    ROWc = b0_rows(Gc)
    ROWIDXc = {r: a for a, r in enumerate(ROWc)}
    rec_c = analyse(SHIPPED_P, Gc, ROWc, ROWIDXc)
    changed = rec_c is None or rec_c['pairs'] != srec['pairs']
    controls['corrupted_gram'] = dict(entry=[a_exp, b_exp], new_value=1, integrity=integ_c,
                                      shipped_j_after=None if rec_c is None else rec_c['j'],
                                      shipped_pairs_after=None if rec_c is None else [list(x) for x in rec_c['pairs']],
                                      flagged=(not integ_c['equals_lines']) and changed)
    c3 = (not integ_c['equals_lines']) and integ_c['b0_f2_rank'] != 9 and changed and gram_digest(Gc) != gram_digest(G)
    # (4) swapped partners: if some example has two live root duals, swapping them violates the duality
    c4 = True
    if jmax >= 2:
        P = sorted(by_j[jmax])[0]
        rec = analyse(P, G, ROW, ROWIDX)
        (a1, b1), (a2, b2) = rec['pairs'][:2]
        bad_pairs = [(a1, b2), (a2, b1)]
        swapped_ok = all(((1 + G[P[jj]][b]) % 2) == (1 if P[jj] == a else 0) for a, b in bad_pairs for jj in range(9))
        controls['swapped_partners'] = dict(P=P, pairs=[list(x) for x in bad_pairs], duality_holds=swapped_ok)
        c4 = not swapped_ok
    # (5) an eligible line of 0..7 substituted into the shipped P (rule Z alone)
    c5 = True
    for low in LOW:
        P5 = None
        for drop in SHIPPED_P:
            cand = sorted([x for x in SHIPPED_P if x != drop] + [low])
            if duals_of(cand, ROW, ROWIDX) is not None:
                P5 = cand
                break
        ok5, why5 = admissible(P5) if P5 else (True, [])
        controls['line_0_7_substitution_%d' % low] = dict(P=P5, rejected=not ok5, reasons=why5)
        c5 &= P5 is not None and not ok5 and why5 == ['uses lines 0..7']
    check('control.non-eligible', c1, 'line %d substituted for %d: rejected (%s)' % (sub[0], SHIPPED_P[0], why1))
    check('control.dependent', c2, 'P = %s rejected (%s); gen_p3 decoder-rows condition fails' % (first_dependent, why2))
    check('control.corrupted-gram', c3, 'G[%d][%d] := 1: integrity fails (B0 rank %d), shipped dual changes to %s'
          % (a_exp, b_exp, integ_c['b0_f2_rank'], controls['corrupted_gram']['shipped_pairs_after']))
    check('control.swapped-partners', c4, 'swapping two live root duals breaks B0[a_j,b_k] = delta_jk'
          if jmax >= 2 else 'not applicable (jmax < 2)')
    check('control.lines-0-7', c5, 'eligible line(s) %s substituted into the shipped P: rejected by rule Z only' % LOW)

    # ------------------------------------------------ assemble the receipt
    table_digest = hashlib.sha256('\n'.join(sorted(table)).encode()).hexdigest()
    jmax_sets = sorted(by_j[jmax])
    census = dict(
        package='research/bit-orthogonal-pair-stage-screen',
        script='census.py',
        claim_scope=('finite exact census of F2 dual roots for the fixed label-reader basis {lambda_a : a in P}; '
                     'P ranges over nine-subsets of the gen_p3.eligible lines of the frozen PR555 L3 plan; no word is '
                     'built, no hosting or pricing claim; no kappa'),
        inputs={rel: PINNED[rel] for rel in sorted(PINNED)},
        geometry=dict(lines=N, line_order='e8.py Hamming (#370) order; verified against the PR589 word ports_geom',
                      gram_sha256_json=gram_digest(G), b0_f2_rank=9, code_weights={str(k): v for k, v in
                                                                                   sorted(weights.items())},
                      d4_block_class_affine_ranks=blk_ar, complementary_pair_class_affine_ranks=pair_ar),
        eligibility=dict(
            rule=('gen_p3.eligible: both (z,z) cells of p\'s 4-frame contain p and kline(p) is not in {p, qhost(p)}; '
                  'independent of the plan_thirds free lines (checked)'),
            eligible=ELIG, eligible_outside_0_7=ELIG18, eligible_in_0_7=LOW,
            one_line_per_frame=True, pr545_line_39_eligible=39 in ELIG),
        admissibility_rules=[
            dict(id='E', kind='construction (gen_p3.build asserts before any gate)', rule='every p in P is eligible'),
            dict(id='Z', kind='construction (discovery/choose.py, README)',
                 rule='P avoids lines 0..7 (PR493 frame-zero residual isometry)'),
            dict(id='A', kind='decoder (necessary for any label decoder; gen_p3.decoder_rows)',
                 rule='E8/2E8 classes of P affinely independent <=> B0[P,P] invertible over F2'),
            dict(id='B2', kind='implied by A', rule='P meets at least two complementary block pairs'),
            dict(id='F', kind='implied by E', rule='at most one line of P per 4-frame')],
        counts=dict(subsets_19=comb(19, 9), subsets_18=comb(18, 9),
                    decoder_only_EA_19=stats['admissible_19'], dependent_19=stats['dependent_19'],
                    admissible_EZA_18=ADM, dependent_18=stats['dependent_18'],
                    fewer_than_two_block_pairs_19=stats['fewer_than_two_pairs_19']),
        j_distribution=dict(
            admissible_EZA={str(k): v for k, v in sorted(jdist.items())},
            admissible_EZA_dead_duals_outside_0_7={str(k): v for k, v in sorted(jdist_r.items())},
            decoder_only_EA_19={str(k): v for k, v in sorted(jdist19.items())},
            decoder_only_EA_19_dead_duals_outside_0_7={str(k): v for k, v in sorted(jdist19_r.items())},
            admissible_EZA_self_dual_terms={str(k): v for k, v in sorted(selfdist.items())},
            admissible_EZA_nonroot_dual_terms={str(k): v for k, v in sorted(nonrootdist.items())}),
        j_max=dict(admissible_EZA=jmax, admissible_EZA_dead_duals_outside_0_7=jmax_r, decoder_only_EA_19=jmax19,
                   number_of_admissible_P_at_jmax=len(jmax_sets), P102_reachable=(jmax == 9)),
        dead_dual_line_frequency={str(k): v for k, v in sorted(dead_freq.items())},
        best_examples=examples,
        admissible_P_with_j_at_least_4=None,
        shipped=shipped,
        controls=controls,
        per_P_table_sha256=table_digest,
        per_P_table_format='sorted lines "p1,...,p9:a-b,..." over admissible (E,Z,A) P; pairs = (reader a, live root dual b)',
        hosting_note=('the R <= 4v screen uses the shipped R = 439 for every example; R of a different P (extra carriers, '
                      'junk wires) is not computed here'),
        checks=None)
    census['admissible_P_with_j_at_least_4'] = high
    census['checks'] = [list(c) for c in CHECKS]
    failed = [t for t, ok in CHECKS if not ok]
    text = json.dumps(census, indent=1, sort_keys=True) + '\n'
    out = Path(args.out)
    if not failed:
        if args.check:
            same = out.exists() and out.read_text() == text
            if not check('receipt.byte-for-byte', same, str(out)):
                failed.append('receipt')
        else:
            out.write_text(text)
            print('wrote ' + str(out))
    if failed:
        print('FAIL_BIT_P102_ELIGIBLE_CENSUS failed=' + ','.join(failed))
        sys.exit(1)
    print('PASS_BIT_P102_ELIGIBLE_CENSUS eligible=%d admissible=%d jmax=%d jdist=%s at_jmax=%d jmax_duals_outside_0_7=%d '
          'eligible_outside_0_7=%d decoder_only_EA19=%d jmax_EA19=%d P102_reachable=%s shipped_j=1 shipped_dual=%d-%d '
          'P110_cst=%d controls=%d checks=%d'
          % (len(ELIG), ADM, jmax, ','.join('%d:%d' % kv for kv in sorted(jdist.items())), len(jmax_sets), jmax_r,
             len(ELIG18), stats['admissible_19'], jmax19, 'yes' if jmax == 9 else 'no', a_exp, b_exp, sext['cst'],
             len([t for t, _ in CHECKS if t.startswith('control.')]), len(CHECKS)))
    return census


if __name__ == '__main__':
    main()
