"""Discovery search: exact triangle (Steinberg 3->2) rewrites of the z-program of
the PR589 tuned bit word, with unchanged frame paths and paid profile.

Research package research/r439-z3to2-seed13 (bit-supplier track, assignment seed 13).
Prepared with help from opencode. Apache-2.0.

The rewrite (a, b, x distinct registers; edges (b,x), (b,a), (a,x) all present in
the z-program): delete edge (b,x) and swap the relative order of edges (b,a) and
(a,x).  As a contiguous identity (gate order left to right, over F2):

    [b += x] [b += a] [a += x]   ==   [a += x] [b += a]      (p(b,a) < p(a,x))
    [a += x] [b += a] [b += x]   ==   [b += a] [a += x]      (p(a,x) < p(b,a))

so one forward source edge disappears; the rebuilt literal-reverse cleanup C
loses its mirror edge as well: 2 ADDs per accepted rewrite.

A candidate instance is accepted only if (i) every gate strictly between the
earliest and the latest of the three edges commutes with all three edges at the
register level (multi-source gates are groups of same-destination transvections
and commute internally), (ii) the rewritten word with rebuilt C passes an exact
replay of the F2 endpoint on all 2v+R = 661 basis columns, (iii) all 661
register frame paths are identical to the base word, and (iv) the wlib-style
paid profile is identical.  Output: MOVES.json (witness), CANDIDATE.json /
certificate counts, SEARCH-LOG.json (complete coverage census).

usage: python3 -I -B research/r439-z3to2-seed13/search.py
"""
import gzip, json, hashlib, collections, copy, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_WORD = ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'

def load_word(p):
    return json.load(gzip.open(p, 'rt'))

def canon(w):
    return json.dumps(w, sort_keys=True, separators=(',', ':')).encode()

# ---------------------------------------------------------------- replay core
class Model:
    def __init__(self, w):
        self.w = w
        self.V, self.R = w['v'], w['R']
        self.N = 2 * self.V + self.R
        self.frames = w['frames']
        self.dim = [len(f) for f in self.frames]
        self.mask = [sum(1 << i for i in f) for f in self.frames]

    def is_z(self, t):
        return t < self.V or t >= 2 * self.V

    def replay(self, w):
        V, N, dim, mask = self.V, self.N, self.dim, self.mask
        cur = list(w['start'])
        H = collections.Counter()
        paths = [[] for _ in range(N)]
        for r, f in enumerate(cur):
            paths[r].append(f)

        def climb(r, f):
            a = cur[r]
            if a == f:
                return
            assert mask[a] & mask[f] == mask[a], ('climb', r, a, f)
            if dim[f] > dim[a]:
                H[dim[f] - dim[a]] += 1
            cur[r] = f
            paths[r].append(f)

        val = [1 << i for i in range(N)]

        def gates(sec):
            for f, t, ss in w[sec]:
                assert len({t, *ss}) == 1 + len(ss), ('dup src', sec, f, t, ss)
                for r in [t, *ss]:
                    climb(r, f)
                for s in ss:
                    val[t] ^= val[s]

        gates('D'); gates('A')
        tops = [dim[cur[q]] for q in w['ret']]
        snap = [val[q] for q in w['ret']]
        for t, ks in enumerate(w['scatter']):
            for k in ks:
                val[V + t] ^= snap[k]
        gates('B'); gates('C')
        for r, f in enumerate(w['final']):
            climb(r, f)
        ok = all(val[r] == ((1 << r) ^ (1 << (r - V)) if V <= r < 2 * V else 1 << r)
                 for r in range(N))
        prof = dict(sorted((H + collections.Counter(tops)).items()))
        return [tuple(p) for p in paths], prof, ok

    def rebuild_C(self, w):
        full = next(i for i, f in enumerate(w['frames']) if len(f) == self.V)
        z = [g for g in w['A'] + w['B'] if self.is_z(g[1])]
        return [[full, t, list(ss)] for f, t, ss in reversed(z)]

    def add_count(self, w):
        return (sum(len(g[2]) for g in w['D'] + w['A'] + w['B'] + w['C'])
                + sum(len(x) for x in w['scatter']))

# ------------------------------------------------------- z stream and triangles
def z_stream(w, M):
    """stream of ('T', (dst, src, gate_key)) and barriers ('Y', ...) / ('SNAP', ...).
    gate_key = (section, index-of-gate-in-section-list-at-snapshot)."""
    stream = []
    for gi, (f, t, ss) in enumerate(w['A']):
        for s in ss:
            stream.append(('T', (t, s, ('A', gi))))
    stream.append(('SNAP', tuple(sorted(w['ret']))))
    for gi, (f, t, ss) in enumerate(w['B']):
        if M.is_z(t):
            for s in ss:
                stream.append(('T', (t, s, ('B', gi))))
        else:
            stream.append(('Y', (t, tuple(ss), ('B', gi))))
    return stream

def tau_commutes(a, x, b, y):
    if a == b:
        return True
    return (a != y) and (b != x)

def blocks(a, x, item):
    k, payload = item
    if k == 'T':
        b, y, _ = payload
        return not tau_commutes(a, x, b, y)
    if k == 'Y':
        return a in payload[1]
    return a in payload  # SNAP

def find_triangles(w, M):
    stream = z_stream(w, M)
    pos = collections.defaultdict(list)
    for idx, (k, p) in enumerate(stream):
        if k == 'T':
            pos[(p[0], p[1])].append(idx)
    edges = set(pos)
    out = []
    for (b, a) in sorted(edges):
        if a == b:
            continue
        for (b2, x) in sorted(edges):
            if b2 != b or x == a or x == b:
                continue
            if (a, x) not in edges:
                continue
            for p_bx in pos[(b, x)]:
                for p_ba in pos[(b, a)]:
                    for p_ax in pos[(a, x)]:
                        ps = [p_bx, p_ba, p_ax]
                        if len(set(ps)) < 3:
                            continue
                        lo, hi = min(ps), max(ps)
                        ok = True
                        for i in range(lo + 1, hi):
                            if i in ps:
                                continue
                            for e in ((b, x), (b, a), (a, x)):
                                if blocks(e[0], e[1], stream[i]):
                                    ok = False
                                    break
                            if not ok:
                                break
                        if ok:
                            out.append({'b': b, 'a': a, 'x': x,
                                        'pos': [p_bx, p_ba, p_ax],
                                        'mapA': p_ba < p_ax,
                                        'window': [lo, hi]})
    return out, stream, pos

# --------------------------------------------------------------- apply a move
def gate_identity(g):
    return [g[0], g[1], list(g[2])]

def apply_move(w, M, mv):
    """Delete edge (b,x); move the gate holding (a,x) across the gate holding
    (b,a) so the kept pair swaps relative order.  Gates are identified by their
    exact (frame, dst, src-list) identity captured at search time."""
    b, a, x = mv['b'], mv['a'], mv['x']
    sec = mv['sec']
    L = w[sec]

    def gate_by_identity(ident, occ):
        hits = [i for i, g in enumerate(L)
                if g[0] == ident[0] and g[1] == ident[1] and list(g[2]) == list(ident[2])]
        if len(hits) <= occ:
            raise AssertionError('gate identity not found: %r' % (ident,))
        return hits[occ]

    i_bx = gate_by_identity(mv['g_bx'], 0)
    i_ba = gate_by_identity(mv['g_ba'], 0)
    i_ax = gate_by_identity(mv['g_ax'], 0)
    g_bx, g_ba, g_ax = L[i_bx], L[i_ba], L[i_ax]
    # 1. delete edge (b,x)
    g_bx[2] = [s for s in g_bx[2] if s != x]
    if not g_bx[2] and g_bx is not g_ba and g_bx is not g_ax:
        L.remove(g_bx)
    # 2. extract edge (a,x) into its own gate at the same frame
    if g_ax is g_ba:
        raise AssertionError('triangle degenerate: (a,x) and (b,a) same gate')
    rest = [s for s in g_ax[2] if s != x]
    moved = [g_ax[0], a, [x]]
    if rest:
        g_ax[2] = rest
        anchor_is_moved = False
    else:
        L.remove(g_ax)
    # 3. swap relative order: place moved (a,x) on the other side of (b,a)
    j_ba = L.index(g_ba)
    if mv['mapA']:
        L.insert(j_ba, moved)          # (a,x) now before (b,a)
    else:
        L.insert(j_ba + 1, moved)      # (a,x) now after (b,a)
    w['C'] = M.rebuild_C(w)
    return w

# ----------------------------------------------------------------- main search
def main():
    t0 = time.time()
    w0 = load_word(BASE_WORD)
    M = Model(w0)
    base_hash = hashlib.sha256(canon(w0)).hexdigest()
    bp, bprof, bok = M.replay(w0)
    assert bok
    base_adds = M.add_count(w0)

    # duplicate-pair census (paired-transvection class) for the coverage record
    stream0 = z_stream(w0, M)
    occ = collections.defaultdict(list)
    for idx, (k, p) in enumerate(stream0):
        if k == 'T':
            occ[(p[0], p[1])].append(idx)
    dup = {k: v for k, v in occ.items() if len(v) > 1}

    work = copy.deepcopy(w0)
    moves = []
    rounds = []
    tri_total = tri_clear_total = 0
    rejected = collections.Counter()
    while True:
        tris, stream, pos = find_triangles(work, M)
        tri_total_this = len({(t['b'], t['a'], t['x']) for t in tris})
        clear = tris  # find_triangles returns only clear instances
        tri_total += 0
        applied_this_round = 0
        used_edges = set()
        used_windows = []
        for mv in sorted(clear, key=lambda t: (-t['window'][1], -t['window'][0], t['b'], t['a'], t['x'])):
            key = (mv['b'], mv['a'], mv['x'])
            if any(e in used_edges for e in [(mv['b'], mv['x']), (mv['b'], mv['a']), (mv['a'], mv['x'])]):
                rejected['edge-consumed'] += 1
                continue
            lo, hi = mv['window']
            if any(not (hi < ulo or uhi < lo) for ulo, uhi in used_windows):
                rejected['window-overlap'] += 1
                continue
            # derive section from stream entries at the three positions
            secs = {stream[i][1][2][0] for i in mv['pos']}
            if len(secs) != 1:
                rejected['cross-section'] += 1
                continue
            sec = secs.pop()
            L = work[sec]
            try:
                gi_bx = stream[mv['pos'][0]][1][2][1]
                gi_ba = stream[mv['pos'][1]][1][2][1]
                gi_ax = stream[mv['pos'][2]][1][2][1]
                m = {'b': mv['b'], 'a': mv['a'], 'x': mv['x'], 'sec': sec,
                     'g_bx': gate_identity(L[gi_bx]),
                     'g_ba': gate_identity(L[gi_ba]),
                     'g_ax': gate_identity(L[gi_ax]),
                     'mapA': mv['mapA'], 'window': mv['window']}
                trial = copy.deepcopy(work)
                apply_move(trial, M, m)
                tp, tprof, tok = M.replay(trial)
            except Exception as ex:
                rejected['apply-or-replay:%s' % type(ex).__name__] += 1
                continue
            if not tok:
                rejected['endpoint'] += 1
                continue
            if tp != bp:
                rejected['frame-paths'] += 1
                continue
            if tprof != bprof:
                rejected['profile'] += 1
                continue
            work = trial
            moves.append(m)
            used_edges.update([(m['b'], m['x']), (m['b'], m['a']), (m['a'], m['x'])])
            used_windows.append((lo, hi))
            applied_this_round += 1
        rounds.append({'clear_instances': len(clear),
                       'distinct_triangles': tri_total_this,
                       'applied': applied_this_round,
                       'rejected_cumulative': dict(rejected)})
        print('round %d: clear instances %d, distinct triangles %d, applied %d, total moves %d'
              % (len(rounds), len(clear), tri_total_this, applied_this_round, len(moves)))
        if applied_this_round == 0:
            break
        if len(rounds) >= 60:
            break

    tp, tprof, tok = M.replay(work)
    assert tok and tp == bp and tprof == bprof
    cand_adds = M.add_count(work)
    cand_hash = hashlib.sha256(canon(work)).hexdigest()

    # final census on the fixed point
    tris_end, stream_end, _ = find_triangles(work, M)

    rec = {
        'base_word': str(BASE_WORD.relative_to(ROOT)).replace('\\', '/'),
        'base_canonical_sha256': base_hash,
        'candidate_canonical_sha256': cand_hash,
        'base_ADDs': base_adds,
        'candidate_ADDs': cand_adds,
        'saved_ADDs': base_adds - cand_adds,
        'moves': moves,
        'n_moves': len(moves),
        'rounds': rounds,
        'duplicate_edges': len(dup),
        'duplicate_extra_occurrences': sum(len(v) - 1 for v in dup.values()),
        'clear_triangles_at_fixed_point': len(tris_end),
        'accepted_filter': ['window commutation', 'exact endpoint on 661 columns',
                            '661 frame paths identical', 'paid profile identical'],
        'seed': 13,
        'track': 'bit supplier (00-19)',
    }
    out = Path(__file__).resolve().parent
    (out / 'MOVES.json').write_text(json.dumps(rec, indent=1, sort_keys=True))
    (out / 'CANDIDATE-WORD.json').write_text(canon(work).decode())
    print('ADDs %d -> %d (saved %d) moves %d  elapsed %.1fs'
          % (base_adds, cand_adds, base_adds - cand_adds, len(moves), time.time() - t0))
    print('rejected:', dict(rejected))

if __name__ == '__main__':
    main()
