"""Independent verification of research/r439-z3to2-seed13 (research package,
bit-supplier track, assignment seed 13). Prepared with help from opencode.
Apache-2.0. Standard library only; Python 3.11+.

usage: python3 -I -B research/r439-z3to2-seed13/verify.py

Checks (imports no search code):
  1. base word canonical SHA-256 equals the pin in SOURCES.json;
  2. re-apply every witness move of MOVES.json from scratch and compare the
     rebuilt candidate word byte-for-byte with CANDIDATE-WORD.json;
  3. per-move obligations: three distinct registers, the three edges present in
     the base word, the exact 3-register F2 identity before == after, and the
     window commutation condition recomputed on the base stream;
  4. independent exact replay of base and candidate on all 2v+R = 661 basis
     columns (the full F2 word map, hence J = I and the helper matrix K and D
     are unchanged);
  5. the z-program product U (550 x 550 over F2) is identical base vs candidate;
  6. all 661 register frame paths identical, and the paid profile identical;
  7. exact record accounting (ADD/MOVE/COPY/ERASE) from the words, cross-checked
     against the repository exporter export_records.py run on both words;
  8. six negative controls must each be rejected;
  9. the recomputed summary equals CERTIFICATE.json.
"""
import gzip, json, hashlib, collections, copy, subprocess, sys, tempfile, struct, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_WORD = ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
EXPORT = ROOT / 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'

def canon(w):
    return json.dumps(w, sort_keys=True, separators=(',', ':')).encode()

def sha(w):
    return hashlib.sha256(canon(w)).hexdigest()

def need(cond, msg):
    if not cond:
        raise SystemExit('FAIL: ' + msg)

# ------------------------------------------------------------ independent replay
class Replay:
    def __init__(self, w):
        self.V, self.R = w['v'], w['R']
        self.N = 2 * self.V + self.R
        self.dim = [len(f) for f in w['frames']]
        self.mask = [sum(1 << i for i in f) for f in w['frames']]

    def run(self, w, strict=True):
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
            if not (mask[a] & mask[f] == mask[a]):
                raise ValueError(('climb', r, a, f))
            if dim[f] > dim[a]:
                H[dim[f] - dim[a]] += 1
            cur[r] = f
            paths[r].append(f)

        val = [1 << i for i in range(N)]

        def gates(sec):
            for f, t, ss in w[sec]:
                if len({t, *ss}) != 1 + len(ss):
                    raise ValueError(('dup', sec, t, ss))
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

# ------------------------------------------------------- z product (550 x 550)
def z_product(w):
    V, R = w['v'], w['R']
    zids = [r for r in range(2 * V + R) if r < V or r >= 2 * V]
    zidx = {r: i for i, r in enumerate(zids)}
    Z = len(zids)
    cols = [1 << i for i in range(Z)]
    def apply_tau(a, x):
        ai, xi = zidx[a], zidx[x]
        for j in range(Z):
            if (cols[j] >> xi) & 1:
                cols[j] ^= 1 << ai
    for sec in ('A', 'B'):
        for f, t, ss in w[sec]:
            if t in zidx:
                for s in ss:
                    apply_tau(t, s)
    return cols

# ------------------------------------------------------- move re-application
def rebuild_C(w, V):
    full = next(i for i, f in enumerate(w['frames']) if len(f) == V)
    z = [g for g in w['A'] + w['B'] if g[1] < V or g[1] >= 2 * V]
    return [[full, t, list(ss)] for f, t, ss in reversed(z)]

def stream_of(w):
    """z-edge stream with gate identities and barriers, for the window check."""
    V = w['v']
    stream = []
    for gi, g in enumerate(w['A']):
        for s in g[2]:
            stream.append(('T', (g[1], s, ('A', gi))))
    stream.append(('SNAP', tuple(sorted(w['ret']))))
    for gi, g in enumerate(w['B']):
        if g[1] < V or g[1] >= 2 * V:
            for s in g[2]:
                stream.append(('T', (g[1], s, ('B', gi))))
        else:
            stream.append(('Y', tuple(g[2])))
    return stream

def window_check(w, mv):
    """Recompute the conservative commutation window of one move on the
    current stream; also check that mapA matches the observed edge order."""
    stream = stream_of(w)
    hits = {}
    for idx, (k, p) in enumerate(stream):
        if k != 'T':
            continue
        dst, src, key = p
        for name, ident, e in (('bx', mv['g_bx'], (mv['b'], mv['x'])),
                               ('ba', mv['g_ba'], (mv['b'], mv['a'])),
                               ('ax', mv['g_ax'], (mv['a'], mv['x']))):
            if (dst, src) == e and list(w[key[0]][key[1]]) == list(ident):
                hits[name] = idx
    if sorted(hits) != ['ax', 'ba', 'bx']:
        raise ValueError('move edges not uniquely located at application time')
    ps = [hits['bx'], hits['ba'], hits['ax']]
    if len(set(ps)) < 3:
        raise ValueError('move edges coincide')
    if (hits['ba'] < hits['ax']) != bool(mv['mapA']):
        raise ValueError('mapA disagrees with observed edge order')
    lo, hi = min(ps), max(ps)

    def blocks(a, x, item):
        k, payload = item
        if k == 'T':
            b, y, _ = payload
            if a == b:
                return False
            return (a == y) or (b == x)
        if k == 'Y':
            return a in payload
        return a in payload

    for i in range(lo + 1, hi):
        if i in ps:
            continue
        for e in ((mv['b'], mv['x']), (mv['b'], mv['a']), (mv['a'], mv['x'])):
            if blocks(e[0], e[1], stream[i]):
                raise ValueError('window not clear at application time')
    return True

def apply_moves(w, moves):
    w = copy.deepcopy(w)
    V = w['v']
    for mv in moves:
        sec, b, a, x = mv['sec'], mv['b'], mv['a'], mv['x']
        L = w[sec]
        window_check(w, mv)
        def find(ident):
            hits = [i for i, g in enumerate(L)
                    if g[0] == ident[0] and g[1] == ident[1] and list(g[2]) == list(ident[2])]
            if len(hits) != 1:
                raise ValueError('move gate identity must be unique: %r' % (ident,))
            return hits[0]
        i_bx, i_ba, i_ax = find(mv['g_bx']), find(mv['g_ba']), find(mv['g_ax'])
        g_bx, g_ba, g_ax = L[i_bx], L[i_ba], L[i_ax]
        if not (g_bx[1] == b and x in g_bx[2] and g_ba[1] == b and a in g_ba[2]
                and g_ax[1] == a and x in g_ax[2] and g_ax is not g_ba):
            raise ValueError('move edge mismatch')
        # delete edge (b,x)
        g_bx[2] = [s for s in g_bx[2] if s != x]
        if not g_bx[2]:
            if g_bx is g_ba:
                raise ValueError('deleted edge gate still needed')
            L.remove(g_bx)
        # extract (a,x) into its own gate and swap it across (b,a)
        rest = [s for s in g_ax[2] if s != x]
        if rest:
            g_ax[2] = rest
        else:
            L.remove(g_ax)
        moved = [g_ax[0], a, [x]]
        j_ba = L.index(g_ba)
        if mv['mapA']:
            L.insert(j_ba, moved)
        else:
            L.insert(j_ba + 1, moved)
        w['C'] = rebuild_C(w, V)
    return w

def tri_identity_ok(b, a, x, mapA):
    """The 3-register F2 map of the triple equals that of the kept pair."""
    def ev(prog):
        va, vb, vx = 1, 2, 4  # basis images of a, b, x as bit triples (a,b,x)
        st = {'a': 1, 'b': 2, 'x': 4}
        for dst, src in prog:
            st[dst] ^= st[src]
        return (st['a'], st['b'], st['x'])
    if mapA:
        before = [('b', 'x'), ('b', 'a'), ('a', 'x')]
        after = [('a', 'x'), ('b', 'a')]
    else:
        before = [('a', 'x'), ('b', 'a'), ('b', 'x')]
        after = [('b', 'a'), ('a', 'x')]
    return ev(before) == ev(after)

def record_counts(w, rp):
    V = w['v']
    adds = sum(len(g[2]) for g in w['D'] + w['A'] + w['B'] + w['C']) + sum(len(x) for x in w['scatter'])
    moves_ = sum(len(p) - 1 for p in rp[0])
    copies = len(w['ret'])
    erases = len(w['ret'])
    return {'ADDs': adds, 'MOVEs': moves_, 'COPYs': copies, 'ERASEs': erases,
            'records': adds + moves_ + copies + erases}

def exporter_counts(word_path, outdir):
    out = Path(outdir) / 'exp'
    r = subprocess.run([sys.executable, '-I', '-B', str(EXPORT), str(word_path), str(out)],
                       capture_output=True, text=True)
    need(r.returncode == 0, 'exporter failed: %s' % r.stderr[-400:])
    data = (out / '249-records.bin').read_bytes()
    n = len(data) // 24
    cnt = collections.Counter()
    for i in range(n):
        rec = struct.unpack('<6i', data[24 * i:24 * i + 24])
        cnt[rec[0]] += 1
    return {'MOVEs': cnt[0], 'ADDs': cnt[1], 'COPYs': cnt[2], 'ERASEs': cnt[3], 'records': n}

# --------------------------------------------------------------------- main
def main():
    src_pin = json.loads((HERE / 'SOURCES.json').read_text())
    mv_doc = json.loads((HERE / 'MOVES.json').read_text())
    cert = None
    if '--write-certificate' not in sys.argv:
        cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
    base = json.load(gzip.open(BASE_WORD, 'rt'))
    need(sha(base) == src_pin['base_word']['canonical_sha256'], 'base word hash pin')
    need(sha(base) == mv_doc['base_canonical_sha256'], 'MOVES.json base pin')

    # 2. re-apply moves
    cand = apply_moves(base, mv_doc['moves'])
    need(len(mv_doc['moves']) == mv_doc['n_moves'], 'move count')
    need(sha(cand) == mv_doc['candidate_canonical_sha256'], 'rebuilt candidate hash')
    committed = json.loads((HERE / 'CANDIDATE-WORD.json').read_text())
    need(canon(committed) == canon(cand), 'committed candidate bytes')

    # 3. per-move obligations (window commutation is recomputed inside
    #    apply_moves at each move's application state)
    for mv in mv_doc['moves']:
        need(len({mv['b'], mv['a'], mv['x']}) == 3, 'move registers distinct')
        need(tri_identity_ok(mv['b'], mv['a'], mv['x'], mv['mapA']), 'triangle identity')

    # 4-6. independent replay
    RP = Replay(base)
    bp, bprof, bok = RP.run(base)
    need(bok, 'base replay endpoint')
    cp, cprof, cok = RP.run(cand)
    need(cok, 'candidate replay endpoint on all %d columns' % RP.N)
    need(cp == bp, 'frame paths differ')
    need(cprof == bprof, 'paid profile differs')
    zb, zc = z_product(base), z_product(cand)
    need(zb == zc, 'z-program product U differs')

    # 7. record accounting
    cb = record_counts(base, RP.run(base))
    cc = record_counts(cand, RP.run(cand))
    need(cb['ADDs'] == 24305, 'base ADDs')
    need(cc['ADDs'] == cb['ADDs'] - 2 * mv_doc['n_moves'], 'ADD saving is 2 per move')
    need(cc['MOVEs'] == cb['MOVEs'] and cc['COPYs'] == cb['COPYs']
         and cc['ERASEs'] == cb['ERASEs'], 'non-ADD records changed')
    with tempfile.TemporaryDirectory() as td:
        bp_path = Path(td) / 'base.json'
        cp_path = Path(td) / 'cand.json'
        bp_path.write_text(canon(base).decode())
        cp_path.write_text(canon(cand).decode())
        eb = exporter_counts(bp_path, td)
        ec = exporter_counts(cp_path, td)
    need(eb == cb, 'own/exporter base counts disagree: %r vs %r' % (eb, cb))
    need(ec == cc, 'own/exporter candidate counts disagree: %r vs %r' % (ec, cc))

    # 8. negative controls: each tamper must be rejected by some check
    controls = []
    def reject(name, fn):
        try:
            got = fn()
        except Exception:
            got = 'rejected'
        need(got == 'rejected', 'control not rejected: ' + name)
        controls.append(name)

    def try_run(w2):
        try:
            _, _, ok = RP.run(w2)
        except Exception:
            return 'rejected'
        return 'rejected' if not ok else 'accepted'

    def c1():
        w2 = copy.deepcopy(cand)
        w2['A'][5][2][0] ^= 1
        return try_run(w2)
    def c2():
        w2 = copy.deepcopy(cand)
        w2['C'].pop(3)
        return try_run(w2)
    def c3():
        w2 = copy.deepcopy(cand)
        w2['C'] = w2['C'][:-1]
        return try_run(w2)
    def c4():
        m2 = copy.deepcopy(mv_doc['moves'])
        m2[0]['x'] = m2[0]['x'] ^ 1
        apply_moves(base, m2)
        return 'accepted'
    def c5():
        w2 = copy.deepcopy(cand)
        A = w2['A']
        i = next(i for i, g in enumerate(A) if g[1] < w2['v'] and g[2] and g[2][0] < w2['v'])
        j = next(j for j, g in enumerate(A) if g[1] == A[i][2][0] and A[i][1] in g[2])
        A[i], A[j] = A[j], A[i]
        return try_run(w2)  # no C rebuild: cleanup no longer inverts the z-program
    def c6():
        w2 = copy.deepcopy(base)
        w2['D'][0][2] = w2['D'][0][2][:-1]
        return try_run(w2)
    for name, fn in (('c1-source-corruption', c1), ('c2-cleanup-gate-deleted', c2),
                     ('c3-cleanup-truncated', c3), ('c4-tampered-move-list', c4),
                     ('c5-noncommuting-swap-no-c-rebuild', c5), ('c6-dirt-gate-truncated', c6)):
        reject(name, fn)
    need(len(controls) == 6, 'all six controls must reject')

    summary = {
        'base_word': 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz',
        'base_canonical_sha256': sha(base),
        'candidate_canonical_sha256': sha(cand),
        'n_moves': mv_doc['n_moves'],
        'base_ADDs': cb['ADDs'],
        'candidate_ADDs': cc['ADDs'],
        'saved_ADDs': cb['ADDs'] - cc['ADDs'],
        'base_records': cb['records'],
        'candidate_records': cc['records'],
        'MOVEs': cb['MOVEs'],
        'COPYs': cb['COPYs'],
        'ERASEs': cb['ERASEs'],
        'frame_paths_identical': True,
        'paid_profile_identical': True,
        'paid_profile': bprof,
        'z_product_identical': True,
        'columns_checked': RP.N,
        'controls_rejected': len(controls),
        'exporter_cross_check': True,
    }
    summary = json.loads(json.dumps(summary))
    if '--write-certificate' in sys.argv:
        (HERE / 'CERTIFICATE.json').write_text(json.dumps(summary, indent=1, sort_keys=True))
        print('wrote CERTIFICATE.json')
    else:
        need(summary == cert, 'certificate mismatch:\n got %r\n want %r' % (summary, cert))
    print('PASS_R439_Z3TO2 moves=%d ADDs=%d->%d records=%d->%d columns=%d paths=%d '
          'profile=identical U=identical controls=%d/%d exporter=ok no_new_kappa'
          % (summary['n_moves'], cb['ADDs'], cc['ADDs'], cb['records'], cc['records'],
             RP.N, RP.N, len(controls), 6))

if __name__ == '__main__':
    main()
