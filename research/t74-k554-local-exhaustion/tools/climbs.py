import sys, json, gzip, collections
import _paths
import harness as H, frames as F
from word import inline, span, dimension
from writeback import write_back

def climbs(w):
    """list of climbs per register: (section, index, from_dim, to_dim) using recount logic (A, B, early tails, ends)."""
    v = 112; R = w['report']['R']; n = 2 * v + R; full = frozenset(range(512))
    cur = [frozenset((0, p)) for p in w['ports']] + [frozenset((0,))] * (n - v)
    for r, vecs in w['start_extra'].items(): cur[int(r)] = span(tuple(vecs))
    out = collections.defaultdict(list)
    def climb(r, T, tag):
        assert cur[r] <= T, ('nonmono', tag, r)
        if T != cur[r]: out[r].append((tag, dimension(cur[r]), dimension(T)))
        cur[r] = T
    for sec in ('A', 'B'):
        for i, e in enumerate(w[sec]):
            T = span(tuple(e[-1]))
            for r in (e[1:3] if e[0] == 'add' else e[1:2]): climb(r, T, (sec, i))
    for j, (idx, vecs) in enumerate(w['early_cleanup']):
        e = w['cleanup'][idx]; T = span(tuple(vecs))
        for r in (e[1:3] if e[0] == 'add' else e[1:2]): climb(r, T, ('T', j))
    ends = [full] * v + [frozenset(x for x in range(512) if (x & p).bit_count() % 2 == 0) for p in w['ports']] + [full] * R
    for r, vecs in w['helper_final'].items(): ends[int(r)] = span(tuple(vecs))
    for r in range(n): climb(r, ends[r], ('END',))
    return out

def solved(P, ed):
    w1 = H.compile_edits(P.base, ed)
    caps, comp = H.cone_caps(w1) if ed.get('insert') or ed.get('tail') else (P.caps, None)
    g = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=caps, cut_equality=True)
    r = F.optimal_frames(inline(w1, True), P.costs, check_literal=False, graph=g)
    return write_back(w1, g, r['assign']), r

if __name__ == '__main__':
    word = sys.argv[1]; P = H.Pricer(word)
    ed = json.load(open(sys.argv[2]))
    ed = ed.get('edit', ed)
    wd, rd = solved(P, dict(delete=ed['delete']))
    wk, rk = solved(P, ed)
    print('deleted-only', rd['cost'] - P.base_cost, 'kernel', rk['cost'] - P.base_cost)
    cd, ck = climbs(wd), climbs(wk)
    for r in sorted(set(cd) | set(ck)):
        a = [(x[1], x[2]) for x in cd.get(r, [])]; b = [(x[1], x[2]) for x in ck.get(r, [])]
        if a != b: print(r, 'DEL', cd.get(r), '\n    KER', ck.get(r))
