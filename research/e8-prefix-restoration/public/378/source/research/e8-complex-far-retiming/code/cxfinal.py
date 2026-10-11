"""Finalize an optimised split program: merge consecutive elementary gates of one phase that share kind, frame and the
read register (fan-out: same source, distinct targets) or the destination (fan-in: same destination, distinct sources),
drop unused appended frames, recompute the block histograms and N. usage: cxfinal.py IN(anneal/far output) ORIG OUT"""
import sys, os, gzip, json, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cxkernel import rehist
def finalize(c, c0):
    c = copy.deepcopy(c)
    for ph in ('A', 'B'):
        out = []
        for g in c[ph]:
            p = out[-1] if out else None
            if p and p[0] == g[0] == 'out' and p[1] == g[1] and p[2] == g[2] and not ({t for t, _, _ in g[3]} | set(g[4])) & ({t for t, _, _ in p[3]} | set(p[4])):
                p[3] = p[3] + g[3]; p[4] = p[4] + g[4]
            elif p and p[0] == g[0] == 'in' and p[1] == g[1] and p[2] == g[2] and not {s for s, _, _ in g[3]} & {s for s, _, _ in p[3]}:
                p[3] = p[3] + g[3]
            else: out.append(copy.deepcopy(g))
        c[ph] = out
    used = set(c['start']) | set(c['final']) | {g[1] for g in c['A'] + c['B']} | {f for _, _, f in c['ret']}
    keep = list(range(len(c0['frames']))) + [i for i in range(len(c0['frames']), len(c['frames'])) if i in used]
    ren = {o: n for n, o in enumerate(keep)}; c['frames'] = [c['frames'][i] for i in keep]
    for ph in ('A', 'B'):
        for g in c[ph]: g[1] = ren[g[1]]
    c['derived_from'] = c0['derived_from'] + ' | e8st far piece relocation + block retiming (chafreaky)'
    return rehist(c)
if __name__ == '__main__':
    x = json.load(gzip.open(sys.argv[1])); c = x['cert'] if 'cert' in x else x; c0 = json.load(gzip.open(sys.argv[2]))
    w = finalize(c, c0); print('gates A/B', len(w['A']), len(w['B']), 'frames', len(w['frames']))
    with gzip.GzipFile(sys.argv[3], 'wb', mtime=0) as f: f.write(json.dumps(w, separators=(',', ':')).encode())
