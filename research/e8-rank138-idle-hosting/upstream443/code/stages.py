"""Transcript stages on the E8 bit word (bitE8/1), applied from frozen selections, each bound to the exact input word.

retime  (our #329 descent2 / #287 concave retiming, ported to E8 frames): every selected gate g gets a new frame F with
        close(LB_g + prev frames of its participants) <= F <= rootspan(AND of their next frames), where LB_g is the
        x-support of the non-target operands (source-span rule); pinned: D gates (frame 0), y at frame 0 at the scatter,
        retained totals at FULL at COPY, start and final frames. Checked on the joint retimed configuration.
kernel  (our #320/#329 shared-donor response kernel; #272/#299/#319 lineage): entry = pivot p, entrance E, donors D with
        resp(p) = XOR resp(D) over F2, where resp(h) = the targets whose frame-0 completion (D) gates read h; E inside the
        first frame of p and of every donor. p starts at E and leaves the D gates; each donor climbs to E at the start of
        A and pays d += (its pivots) at E; after C it pays d += (its pivots) again at FULL (F2: d -= p).
        Exclusivity: pivots are never donors, a donor serves one entrance. Total entrance rank = 0 mod 8 (integral
        B_4 width W; the residuals then tile width-72 banks with 9 replicas, checked separately).

usage: stages.py retime|kernel IN.json.gz OUT.json.gz SELECTION.json
After applying, the full exact replay of e8core (legality, F2 on all columns, source spans) must pass and the output
must equal the frozen output content hash. (This package uses the kernel stage only: on PR #376's word our retiming
descent finds no move, before or after the kernel.)
Chafik Boukhalfa (chafreaky) with Anthropic Claude assistance; Apache-2.0."""
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e8core import *


def content_sha(c):
    return hashlib.sha256(json.dumps(c, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class Framer:
    def __init__(self, c):
        self.fl = c['frames']; self.key = {}; self.v = c['v']
        for k, fr in enumerate(self.fl): self.key.setdefault(sum(1 << i for i in fr), k)
    def fid(self, m):
        if m not in self.key: self.key[m] = len(self.fl); self.fl.append([i for i in range(self.v) if m >> i & 1])
        return self.key[m]


def mask_of(lines): return sum(1 << i for i in lines)


def occurrences(c, masks):
    """per register: list of (kind, ref) with pins ('p', mask) and gates ('g', (phase, k)) in time order"""
    v = c['v']; n = 2 * v + c['R']; FULL = (1 << v) - 1
    occ = [[('p', masks[c['start'][r]])] for r in range(n)]
    for ph in ('D', 'A'):
        for k, (f, d, s) in enumerate(c[ph]):
            for x in [d] + s: occ[x].append(('g', (ph, k)))
    for t in range(v): occ[v + t].append(('p', 0))
    for q in c['ret']: occ[q].append(('p', FULL))
    for ph in ('B', 'C'):
        for k, (f, d, s) in enumerate(c[ph]):
            for x in [d] + s: occ[x].append(('g', (ph, k)))
    for r in range(n): occ[r].append(('p', masks[c['final'][r]]))
    return occ


def lower_bounds(c, L):
    v = c['v']; n = 2 * v + c['R']; sup = [1 << i if i < v else 0 for i in range(n)]; lb = {}
    for ph in ('D', 'A', 'B', 'C'):
        for k, (f, d, srcs) in enumerate(c[ph]):
            need = 0
            for s in srcs:
                sup[d] |= sup[s]
                if s < v or s >= 2 * v: need |= sup[s]
            if d >= 2 * v: need |= sup[d]
            lb[(ph, k)] = L.close(need) if need else 0
    return lb


def retime(c, sel):
    L = Lat(c['lines']); masks = to_masks(c, L); occ = occurrences(c, masks); lb = lower_bounds(c, L)
    gm = {(ph, k): masks[g[0]] for ph in ('D', 'A', 'B', 'C') for k, g in enumerate(c[ph])}
    pos = {}
    for r, o in enumerate(occ):
        for i, (kind, x) in enumerate(o):
            if kind == 'g': pos.setdefault(x, []).append((r, i))
    def fr(r, i):
        kind, x = occ[r][i]; return x if kind == 'p' else gm[x]
    seen = set()
    for ph, k, old_lines, new_lines in sel:
        g = (ph, k); assert ph != 'D' and g not in seen; seen.add(g)
        assert gm[g] == L.close(mask_of(old_lines)), ('selection not bound to this word', g)
        F = L.close(mask_of(new_lines)); assert F == mask_of(new_lines), 'frame given as all its root lines'
        gm[g] = F
    for g in seen:  # the joint retimed configuration: every moved gate inside its feasible interval
        F = gm[g]; lo = lb[g]; hi = (1 << c['v']) - 1
        for r, i in pos[g]: lo |= fr(r, i - 1); hi &= fr(r, i + 1)
        assert lo & ~F == 0 and F & ~hi == 0, ('outside the feasible interval', g)
    out = json.loads(json.dumps(c)); fm = Framer(out)
    for ph in ('D', 'A', 'B', 'C'):
        out[ph] = [[fm.fid(gm[(ph, k)]), d, list(s)] for k, (f, d, s) in enumerate(c[ph])]
    return out


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
    assert tot % 8 == 0, 'total entrance rank 0 mod 8'
    out = json.loads(json.dumps(c)); fm = Framer(out)
    for p, E in pivots.items(): out['start'][p] = fm.fid(E)
    out['D'] = [[f, t, [s for s in srcs if s not in pivots]] for f, t, srcs in c['D']]
    byd = {}
    for E_lines, p, D in sel:
        for d in D: byd.setdefault((d, mask_of(E_lines)), []).append(p)
    out['A'] = [[fm.fid(E), d, sorted(ps)] for (d, E), ps in sorted(byd.items())] + out['A']
    out['C'] = out['C'] + [[fm.fid(FULL), d, sorted(ps)] for (d, E), ps in sorted(byd.items())]
    return out, len(sel), tot, len(byd)


if __name__ == '__main__':
    st, inp, outp, selp = sys.argv[1:5]
    c = load_word(inp); sel = json.load(open(selp))
    assert sel['input_sha256'] == content_sha(c), 'selection bound to a different input word'
    if st == 'retime':
        w = retime(c, sel['gates']); info = '%d gates retimed' % len(sel['gates'])
    else:
        w, ne, tot, nd = kernel(c, sel['entries']); info = '%d entries, total entrance rank %d, %d donor slots' % (ne, tot, nd)
    r = replay(w, span_mode='z'); assert not r['viol'], r['viol'][:5]
    assert content_sha(w) == sel['output_sha256'], 'output differs from the frozen stage output'
    save_word(w, outp)
    print('   stage %s: %s | exact replay PASS (legality, F2 on %d columns, source spans) | local histogram %s | output sha %s'
          % (st, info, r['n'], dict(sorted(r['H'].items())), sel['output_sha256'][:16]))
