"""Discovery search: exact triangle (Steinberg 3->2) rewrites of the z-program of
the fixed PR1122 A/B/star-D bit word, with unchanged frame paths and frame-label profile.

Research package research/r439-abc-zrewrite-seed16 (bit-supplier track, assignment seed 16).
Adapted from navinor's PR1127 discovery, prepared with help from opencode.
Seed 16 adaptation prepared with substantial OpenAI Codex assistance. Apache-2.0.

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
register frame paths are identical to the base word, and (iv) the frame-label cardinality
bookkeeping is identical. This is not the E8 paid rank profile; the unchanged
ordered frame paths are checked independently by the package verifier.
D/A/scatter/B/C phase maps must also remain identical. Output: MOVES.json
(witness), CANDIDATE-WORD.json, SEARCH-LOG.json (complete coverage census).

usage: python3 -I -B research/r439-abc-zrewrite-seed16/search.py
"""
import gzip, json, hashlib, collections, copy, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASE_WORD = PACKAGE / 'vendor/pr1122/candidate.json.gz'
SEED = 16

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

        phase_maps = {}
        gates('D'); phase_maps['D'] = tuple(val)
        gates('A'); phase_maps['A'] = tuple(val)
        tops = [dim[cur[q]] for q in w['ret']]
        snap = [val[q] for q in w['ret']]
        for t, ks in enumerate(w['scatter']):
            for k in ks:
                val[V + t] ^= snap[k]
        phase_maps['scatter'] = tuple(val)
        gates('B'); phase_maps['B'] = tuple(val)
        gates('C'); phase_maps['C'] = tuple(val)
        for r, f in enumerate(w['final']):
            climb(r, f)
        ok = all(val[r] == ((1 << r) ^ (1 << (r - V)) if V <= r < 2 * V else 1 << r)
                 for r in range(N))
        prof = dict(sorted((H + collections.Counter(tops)).items()))
        return [tuple(p) for p in paths], prof, ok, phase_maps

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
        return any(not tau_commutes(a, x, payload[0], src) for src in payload[1])
    return a in payload  # SNAP

def find_triangles(w, M):
    """Exhaust every distinct-register triangle occurrence in this snapshot.

    A candidate is retained only within one section and after strict register
    commutation with every intervening elementary transvection/barrier.
    """
    stream = z_stream(w, M)
    pos = collections.defaultdict(list)
    for idx, (kind, payload) in enumerate(stream):
        if kind == 'T':
            pos[(payload[0], payload[1])].append(idx)
    outgoing = collections.defaultdict(list)
    for b, x in sorted(pos):
        outgoing[b].append(x)
    out = []
    census = collections.Counter({key: 0 for key in (
        'distinct_register_triangles', 'triangle_occurrences', 'cross_section',
        'noncommuting_window', 'clear_same_section')})
    for b in sorted(outgoing):
        for a in outgoing[b]:
            for x in outgoing[b]:
                if len({a, b, x}) != 3 or (a, x) not in pos:
                    continue
                census['distinct_register_triangles'] += 1
                for p_bx in pos[(b, x)]:
                    for p_ba in pos[(b, a)]:
                        for p_ax in pos[(a, x)]:
                            ps = [p_bx, p_ba, p_ax]
                            census['triangle_occurrences'] += 1
                            secs = {stream[i][1][2][0] for i in ps}
                            if len(secs) != 1:
                                census['cross_section'] += 1
                                continue
                            lo, hi = min(ps), max(ps)
                            blocked = False
                            for i in range(lo + 1, hi):
                                if i in ps:
                                    continue
                                if any(blocks(dst, src, stream[i])
                                       for dst, src in ((b, x), (b, a), (a, x))):
                                    blocked = True
                                    break
                            if blocked:
                                census['noncommuting_window'] += 1
                                continue
                            census['clear_same_section'] += 1
                            out.append({'b': b, 'a': a, 'x': x,
                                        'pos': ps, 'mapA': p_ba < p_ax,
                                        'window': [lo, hi], 'sec': secs.pop()})
    return out, stream, dict(sorted(census.items()))

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

    i_bx = gate_by_identity(mv['g_bx'], mv['occ_bx'])
    i_ba = gate_by_identity(mv['g_ba'], mv['occ_ba'])
    i_ax = gate_by_identity(mv['g_ax'], mv['occ_ax'])
    g_bx, g_ba, g_ax = L[i_bx], L[i_ba], L[i_ax]
    # 1. delete edge (b,x)
    g_bx[2] = [s for s in g_bx[2] if s != x]
    if not g_bx[2] and g_bx is not g_ba and g_bx is not g_ax:
        L.pop(next(i for i, g in enumerate(L) if g is g_bx))
    # 2. extract edge (a,x) into its own gate at the same frame
    if g_ax is g_ba:
        raise AssertionError('triangle degenerate: (a,x) and (b,a) same gate')
    rest = [s for s in g_ax[2] if s != x]
    moved = [g_ax[0], a, [x]]
    if rest:
        g_ax[2] = rest
        anchor_is_moved = False
    else:
        L.pop(next(i for i, g in enumerate(L) if g is g_ax))
    # 3. swap relative order: place moved (a,x) on the other side of (b,a)
    j_ba = next(i for i, g in enumerate(L) if g is g_ba)
    if mv['mapA']:
        L.insert(j_ba, moved)          # (a,x) now before (b,a)
    else:
        L.insert(j_ba + 1, moved)      # (a,x) now after (b,a)
    w['C'] = M.rebuild_C(w)
    return w

# ----------------------------------------------------------------- main search
def main():
    if sys.flags.optimize:
        raise RuntimeError('discovery must run unoptimized; replay assertions are required')
    w0 = load_word(BASE_WORD)
    M = Model(w0)
    base_hash = hashlib.sha256(canon(w0)).hexdigest()
    bp, bprof, bok, bphase = M.replay(w0)
    if not bok:
        raise ValueError('base endpoint failed')
    if w0['C'] != M.rebuild_C(w0):
        raise ValueError('base C is not the literal reverse z cleanup')
    base_adds = M.add_count(w0)
    stream0 = z_stream(w0, M)
    occ = collections.defaultdict(list)
    for idx, (kind, payload) in enumerate(stream0):
        if kind == 'T':
            occ[(payload[0], payload[1])].append(idx)
    dup = {k: v for k, v in occ.items() if len(v) > 1}

    work = copy.deepcopy(w0)
    moves, rounds = [], []
    rejected = collections.Counter()
    stopping_rule = '60-round cap'
    for round_no in range(1, 61):
        clear, stream, census = find_triangles(work, M)
        # Snapshot exact gate identities before any accepted mutation.  Windows
        # are traversed right to left so disjoint earlier gates keep their index.
        prepared = []
        for mv in clear:
            sec = mv['sec']
            L = work[sec]
            m = dict(mv)
            for label, position in zip(('bx', 'ba', 'ax'), mv['pos']):
                gi = stream[position][1][2][1]
                ident = gate_identity(L[gi])
                m['g_' + label] = ident
                m['occ_' + label] = sum(gate_identity(g) == ident for g in L[:gi])
                m['index_' + label] = gi
            lo, hi = sorted((m['index_ba'], m['index_ax']))
            m['moved_edge_frame'] = m['g_ax'][0]
            m['crossed_gate_frames'] = sorted({g[0] for g in L[lo:hi + 1]})
            m['crosses_distinct_frame'] = any(f != m['moved_edge_frame']
                                               for f in m['crossed_gate_frames'])
            prepared.append(m)
        def order(m):
            tie = hashlib.sha256(('16:' + str(m['b']) + ':' + str(m['a']) + ':' + str(m['x'])).encode()).hexdigest()
            return (-m['window'][1], -m['window'][0], tie)
        applied = 0
        used_windows = []
        used_edges = set()
        for m in sorted(prepared, key=order):
            edges = [(m['b'], m['x']), (m['b'], m['a']), (m['a'], m['x'])]
            if any(e in used_edges for e in edges):
                rejected['edge-consumed'] += 1
                continue
            lo, hi = m['window']
            if any(not (hi < a or b < lo) for a, b in used_windows):
                rejected['window-overlap'] += 1
                continue
            # Each witness occurrence must still identify its exact current gate.
            for label in ('bx', 'ba', 'ax'):
                ident = m['g_' + label]
                hits = [i for i, g in enumerate(work[m['sec']]) if gate_identity(g) == ident]
                if len(hits) <= m['occ_' + label] or hits[m['occ_' + label]] != m['index_' + label]:
                    raise ValueError('snapshot index drift for accepted-order trial')
            trial = copy.deepcopy(work)
            try:
                apply_move(trial, M, m)
                tp, tprof, tok, tphase = M.replay(trial)
            except (AssertionError, ValueError, IndexError) as ex:
                rejected['apply-or-replay:' + type(ex).__name__] += 1
                continue
            if not tok:
                rejected['endpoint'] += 1
                continue
            if tphase != bphase:
                rejected['phase-maps'] += 1
                continue
            if tp != bp:
                rejected['frame-paths'] += 1
                continue
            if tprof != bprof:
                rejected['frame-label-profile'] += 1
                continue
            if M.add_count(work) - M.add_count(trial) != 2:
                raise ValueError('accepted move must save exactly two ADDs')
            work = trial
            moves.append(m)
            applied += 1
            used_edges.update(edges)
            used_windows.append((lo, hi))
        rounds.append({'round': round_no, 'coverage': census,
                       'applied': applied,
                       'rejected_cumulative': dict(sorted(rejected.items()))})
        print('round %d: clear=%d applied=%d moves=%d' % (round_no, len(clear), applied, len(moves)), flush=True)
        if applied == 0:
            stopping_rule = 'fixed point under stated filters'
            break
    tp, tprof, tok, tphase = M.replay(work)
    if not (tok and tp == bp and tprof == bprof and tphase == bphase):
        raise ValueError('final preservation check failed')
    cand_adds = M.add_count(work)
    cand_hash = hashlib.sha256(canon(work)).hexdigest()
    clear_end, _, end_census = find_triangles(work, M)
    common = {
        'base_word': str(BASE_WORD.relative_to(ROOT)),
        'base_source_pin': 'a2551e70fce0cc34348f50f1a94e7cc4c80bbcbf',
        'base_canonical_sha256': base_hash,
        'candidate_canonical_sha256': cand_hash,
        'base_ADDs': base_adds, 'candidate_ADDs': cand_adds,
        'saved_ADDs': base_adds - cand_adds,
        'n_moves': len(moves), 'seed': SEED,
        'track': 'bit supplier (00-19)',
        'accepted_filter': ['same section', 'strict window commutation',
                            'exact endpoint on 661 basis columns',
                            'D/A/scatter/B/C phase maps identical',
                            '661 register frame paths identical',
                            'frame-label profile identical', 'literal reverse C'],
        'frame_label_profile': bprof,
        'stopping_rule': stopping_rule,
        'round_cap': 60,
        'tie_order': 'descending window endpoints, SHA256 of 16:b:a:x',
        'cross_frame_moves': sum(m['crosses_distinct_frame'] for m in moves),
        'scope': 'finite circuit rewrite only; no new kappa or improved frame-label profile',
    }
    record = dict(common)
    record['moves'] = moves
    log = dict(common)
    log.update({'rounds': rounds, 'rejected': dict(sorted(rejected.items())),
                'initial_duplicate_edges': len(dup),
                'initial_duplicate_extra_occurrences': sum(len(v) - 1 for v in dup.values()),
                'final_coverage': end_census,
                'clear_instances_at_stop': len(clear_end)})
    (PACKAGE / 'MOVES.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    (PACKAGE / 'SEARCH-LOG.json').write_text(json.dumps(log, indent=2, sort_keys=True) + '\n')
    (PACKAGE / 'CANDIDATE-WORD.json').write_text(canon(work).decode() + '\n')
    print('ADDs %d -> %d (saved %d), moves %d, cross-frame %d, %s' %
          (base_adds, cand_adds, base_adds - cand_adds, len(moves),
           common['cross_frame_moves'], stopping_rule), flush=True)
    print('rejected: ' + json.dumps(dict(sorted(rejected.items()))), flush=True)

if __name__ == '__main__':
    main()
