"""Apply a frozen selection (shared-donor kernel + entrance gauges) to PR #433's complex word.  Apache-2.0.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
usage: gk_word.py BASE_FULL-WORD.json.gz SELECTION.json OUT_FULL-WORD.json.gz
An empty selection ({}) copies the input byte for byte (regression anchor).

selection = {"kernel": [{"E": [x], "donors": [h..], "pivots": [h..]}..], "gauge": {"h": [x..]}}   (h = helper index 0..R-1)
Kernel (PR #417/#435/#434/#440): a pivot starts at E; every donor receives  donor += -q * pivot  at frame E before the main
word, where col(pivot) = sum q_d col(d) are the exact dirty-response columns; the pivot's frame-zero compensation vanishes.
Gauge (#401/#408-#416): the compensation  target += -C[t,h] * helper  of helper h is executed at frame E_h as the first gates
of the main word; h starts at E_h and its targets climb to the level L_t = largest E over their entering helpers.
The exact verification is the arbitrary-dirt replay of audit_gk.py; this module also checks the structural conditions."""
import copy, gzip, hashlib, json, sys
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gk_common import *


def apply_op(e, rows):
    if e[0] == 'scale':
        _, t, a, b, *_ = e; q = Q(a, b); rows[t] = {j: q * x for j, x in rows[t].items()}
    else:
        _, t, s, a, b, *_ = e; q = Q(a, b)
        for j, x in list(rows[s].items()):
            z = rows[t].get(j, Q(0)) + q * x
            if z: rows[t][j] = z
            else: rows[t].pop(j, None)


def inverse(e, F):
    e = copy.deepcopy(e)
    if e[0] == 'add': e[3] *= -1
    else: e[2], e[3] = e[3], e[2]
    e[-1] = list(F); return e


def responses(word):
    """dirty-response columns col[h] = {target: coefficient} of the unmodified word (after the frame-zero preconditioner)"""
    R = word['report']['R']; n = 2 * V + R
    rows = [{r: Q(1)} for r in range(n)]
    for e in word['A'] + word['cut'] + word['B']: apply_op(e, rows)
    dirty = [{} for _ in range(n)]
    for r in range(V, 2 * V): dirty[r] = {j: x for j, x in rows[r].items() if j >= 2 * V}
    for e in word['precondition']: apply_op(e, dirty)
    col = [{} for _ in range(R)]
    for r in range(V, 2 * V):
        for j, x in dirty[r].items(): col[j - 2 * V][r - V] = x
    return col


def first_frames(word):
    first = {}
    for seq in (word['A'], word['B']):
        for e in seq:
            F = basis(e[-1])
            for r in [e[1]] + ([e[2]] if e[0] == 'add' else []):
                if r >= 2 * V: first.setdefault(r - 2 * V, F)
    return first


def solve_relation(col, donors, p):
    """exact rational c with col[p] = sum_d c_d col[d]; None if p is not in the span"""
    ts = sorted({t for d in donors for t in col[d]} | set(col[p]))
    idx = {t: i for i, t in enumerate(ts)}
    Mx = [[Q(0)] * (len(donors) + 1) for _ in ts]
    for ci, d in enumerate(donors):
        for t, x in col[d].items(): Mx[idx[t]][ci] = x
    for t, x in col[p].items(): Mx[idx[t]][-1] = x
    piv = []; r = 0
    for c in range(len(donors)):
        pr = next((i for i in range(r, len(Mx)) if Mx[i][c]), None)
        if pr is None: continue
        Mx[r], Mx[pr] = Mx[pr], Mx[r]; q = Mx[r][c]; Mx[r] = [x / q for x in Mx[r]]
        for i in range(len(Mx)):
            if i != r and Mx[i][c]:
                f = Mx[i][c]; Mx[i] = [a - f * b for a, b in zip(Mx[i], Mx[r])]
        piv.append(c); r += 1
    if any(Mx[i][-1] for i in range(r, len(Mx))): return None
    assert r == len(donors), 'donors must have independent response columns'
    return {donors[c]: Mx[i][-1] for i, c in enumerate(piv) if Mx[i][-1]}


def span(U):
    s = {0}
    for b in U: s |= {x ^ b for x in s}
    return s


def perp(x): return basis([z for z in range(1, 512) if not (x & z).bit_count() % 2])


def profile(word):
    """local paid profile of a gk word by direct simulation of the frame chains (second implementation: audit_gk.py)"""
    R = word['report']['R']; n = 2 * V + R; P = word['ports']
    cur = {}
    for r in range(n):
        cur[r] = (P[r],) if r < V else ((basis(word['start_extra'][str(r)]) if str(r) in word.get('start_extra', {}) else ()) if r >= 2 * V else ())
    paid = Counter()
    def climb(r, F):
        F = basis(F); o = cur[r]
        assert basis(list(o) + list(F)) == F, ('frame violation', r, o, F)
        if o != F: paid[len(F) - len(o)] += 1; cur[r] = F
    lev = {int(t): basis(E) for t, E in word.get('target_levels', {}).items()}
    for seq, part in ((word['A'], 'A'), (word['B'], 'B')):
        if part == 'B':
            for r, f in zip(word['centers'], word['center_frames']):
                assert cur[r] == basis(f), 'centre frame'
                served = sorted({lev.get(e[1] - V, ()) for e in word['cut'] if e[2] == r}, key=lambda E: -len(E))
                o = basis(f)
                for Lv in served:
                    assert span(Lv) <= span(o), 'served levels must descend inside the centre frame'
                    if Lv != o: paid[len(o) - len(Lv)] += 1; o = Lv
            for t in range(V): assert cur[V + t] == lev.get(t, ()), 'target level at the centre scatter'
        for e in seq:
            for r in [e[1]] + ([e[2]] if e[0] == 'add' else []): climb(r, e[-1])
    for r in range(n): climb(r, FULL if (r < V or r >= 2 * V) else perp(P[r - V]))
    return paid


def global_profile(local, widths):
    """unhosted nine-stage profile: local x (stages*replicas) + the 240*8 idle children per rank + bank pads"""
    live, pads = unhosted_stock(widths)
    g = Counter({r: z * L * T for r, z in local.items()})
    for r in (16, 8, 32, 8, 48, 8, 48, 32, 16): g[r] += 240 * T
    g.update(pads)
    return live, g


def build(word, sel, check=True):    # check=False only for the mutation controls that must be caught by the certifying scripts
    if not sel: return word
    w = copy.deepcopy(word); R = w['report']['R']
    col = responses(word); first = first_frames(word)
    gauge = {int(h): basis(E) for h, E in sel.get('gauge', {}).items()}
    classes = sel.get('kernel', [])
    pivots = {p for c in classes for p in c['pivots']}; donors = {d for c in classes for d in c['donors']}
    assert not (pivots & donors) and not (pivots | donors) & set(gauge) and len(pivots) == sum(len(c['pivots']) for c in classes)
    # --- structural conditions -------------------------------------------------------------------------------------
    for h, E in gauge.items():
        assert not check or span(E) <= span(first[h]), ('gauge entrance outside the first frame', h)
    levels = defaultdict(list)
    for h, E in gauge.items():
        for t in col[h]: levels[t].append(E)
    for t, Es in levels.items():                                   # pairwise nested comps per target
        for a in Es:
            for b in Es: assert not check or span(a) <= span(b) or span(b) <= span(a), ('non-nested gauges at target', t)
    lev = {t: max(Es, key=len) for t, Es in levels.items()}
    for k, r in enumerate(w['centers']):                              # chain per centre, inside the centre frame
        served = {lev.get(e[1] - V, ()) for e in w['cut'] if e[2] == r}
        for a in served:
            for b in served: assert not check or span(a) <= span(b) or span(b) <= span(a), ('centre chain', k)
        top = max(served, key=len)
        assert not check or span(top) <= span(basis(w['center_frames'][k])), ('level outside centre frame', k)
    # --- gates ----------------------------------------------------------------------------------------------------------
    gates = []
    for h, E in sorted(gauge.items(), key=lambda kv: (len(kv[1]), kv[0])):
        for t, x in sorted(col[h].items()):
            c = -x; gates.append(['add', V + t, 2 * V + h, c.numerator, c.denominator, list(E)])
    pre = []
    start = {2 * V + h: list(E) for h, E in gauge.items()}
    for cl in sorted(classes, key=lambda c: (len(c['E']), c['E'])):
        E = basis(cl['E'])
        for x in [*cl['donors'], *cl['pivots']]: assert span(E) <= span(first[x]), ('kernel entrance outside the first frame', x)
        for p in cl['pivots']:
            rel = solve_relation(col, cl['donors'], p)
            assert rel is not None, ('pivot response not in the donor span', p)
            start[2 * V + p] = list(E)
            for d, c in rel.items():
                q = -c; pre.append(['add', 2 * V + d, 2 * V + p, q.numerator, q.denominator, list(E)])
    w['A'] = gates + pre + w['A']
    w['cleanup'] = [inverse(e, FULL) for e in reversed(w['A'] + w['B']) if not V <= e[1] < 2 * V]
    w['start_extra'] = {str(r): list(E) for r, E in sorted(start.items())}
    w['target_levels'] = {str(t): list(E) for t, E in sorted(lev.items()) if E}
    if not check: return w
    prof = profile(w); widths = widths_of(w)
    live, g = global_profile(prof, widths)
    w['report']['local_profile'] = {str(k): z for k, z in sorted(prof.items())}
    w['report']['global_profile'] = {str(k): z for k, z in sorted(g.items())}
    w['report']['live'] = live
    w['report']['entrance_rank'] = sum(L - x for x in widths); w['report']['entering_helpers'] = sum(1 for x in widths if x < L)
    w['report']['selection_sha256'] = hashlib.sha256(json.dumps(sel, sort_keys=True).encode()).hexdigest()
    return w


def dump(w): return gzip.compress(json.dumps(w, sort_keys=True, separators=(',', ':')).encode(), mtime=0)


if __name__ == '__main__':
    src, selp, out = map(Path, sys.argv[1:4])
    sel = json.loads(selp.read_text())
    if not sel: out.write_bytes(src.read_bytes()); print('empty selection: copied byte for byte'); sys.exit(0)
    word = json.load(gzip.open(src)); w = build(word, sel); out.write_bytes(dump(w))
    print('gk word: entering helpers', w['report']['entering_helpers'], 'entrance rank', w['report']['entrance_rank'],
          'local profile', w['report']['local_profile'], 'unhosted live', w['report']['live'])
