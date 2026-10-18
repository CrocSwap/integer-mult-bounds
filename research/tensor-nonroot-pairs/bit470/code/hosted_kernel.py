"""PR417 response kernel with every local response and frame check retained.
Bank integrality is replaced by complete idle-host ownership in the global audit.
Generalization by chafreaky with OpenAI Codex assistance; Apache-2.0.
"""
from stages import Lat, to_masks, occurrences, Framer, mask_of, json

def kernel(c, sel):
    L = Lat(c['lines']); masks = to_masks(c, L); v = c['v']; n = 2 * v + c['R']; FULL = (1 << v) - 1
    occ = occurrences(c, masks)
    gm = {(ph, k): masks[g[0]] for ph in ('D', 'A', 'B', 'C') for k, g in enumerate(c[ph])}
    first = {}
    for h in range(2 * v, n):
        assert masks[c['start'][h]] == 0
        first[h] = next(x if kind == 'p' else gm[x] for kind, x in occ[h][1:] if (x if kind == 'p' else gm[x]) != 0)
    resp = {}
    for f, t, srcs in c['D']:
        assert masks[f] == 0
        for s in srcs: resp[s] = resp.get(s, 0) ^ (1 << (t - v))
    ret = set(c['ret']); pivots = {}; donor_at = {}; tot = 0
    for E_lines, p, D in sel:
        E = L.close(mask_of(E_lines)); assert E == mask_of(E_lines) and E != 0
        assert p not in ret and p not in pivots and p not in donor_at and 2 * v <= p < n
        x = resp.get(p, 0)
        for d in D:
            assert d not in ret and d not in pivots and 2 * v <= d < n
            assert donor_at.setdefault(d, E) == E, 'donor serves one entrance'
            x ^= resp.get(d, 0)
        assert x == 0, ('response relation fails', p)
        for h in [p] + D: assert E & ~first[h] == 0, ('entrance not inside first frame', h)
        pivots[p] = E; tot += L.dim(E)
    assert not set(pivots) & set(donor_at)
    out = json.loads(json.dumps(c)); fm = Framer(out)
    for p, E in pivots.items(): out['start'][p] = fm.fid(E)
    out['D'] = [[f, t, [s for s in srcs if s not in pivots]] for f, t, srcs in c['D']]
    byd = {}
    for E_lines, p, D in sel:
        for d in D: byd.setdefault((d, mask_of(E_lines)), []).append(p)
    out['A'] = [[fm.fid(E), d, sorted(ps)] for (d, E), ps in sorted(byd.items())] + out['A']
    out['C'] = out['C'] + [[fm.fid(FULL), d, sorted(ps)] for (d, E), ps in sorted(byd.items())]
    return out, len(sel), tot, len(byd)
