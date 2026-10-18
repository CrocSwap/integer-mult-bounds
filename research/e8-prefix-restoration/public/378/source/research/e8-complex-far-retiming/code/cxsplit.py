"""Split every multi-addition gate of a gcert/1 program into elementary single-addition gates in the same order (same
scalar operator: fan-out pieces read an unchanged source, fan-in pieces add into one destination), then run block and
single-gate retiming (cxretime) on the split program, then re-merge adjacent pieces of one original gate that kept a
common frame. usage: cxsplit.py CERT.json.gz GXDIR OUT.json.gz [K] [sweeps] [seed]"""
import sys, os, gzip, json, math, random, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cxretime import *
from cxretime import sweep as block_sweep


def split(c):
    c = copy.deepcopy(c); tag = []
    for ph in ('A', 'B'):
        out = []
        for gi, g in enumerate(c[ph]):
            if g[0] == 'out' and len(g[3]) + len(g[4]) > 1:
                pieces = [['out', g[1], g[2], [x], []] for x in g[3]]
                if g[4]: pieces[0][4] = list(g[4]) if pieces else None
                for p_ in pieces: out.append(p_); tag.append((ph, gi))
            elif g[0] == 'in' and len(g[3]) > 1:
                for x in g[3]: out.append(['in', g[1], g[2], [x]]); tag.append((ph, gi))
            else: out.append(g); tag.append((ph, gi))
        c[ph] = out
    return c, tag


def merge(c, tag):
    c = copy.deepcopy(c); k = 0
    for ph in ('A', 'B'):
        out = []; prev = None
        for g in c[ph]:
            t = tag[k]; k += 1
            if prev is not None and prev[0] == t and out[-1][0] == g[0] and out[-1][1] == g[1] and out[-1][2] == g[2]:
                out[-1][3] = out[-1][3] + g[3]
                if g[0] == 'out': out[-1][4] = out[-1][4] + g[4]
            else: out.append(copy.deepcopy(g))
            prev = (t,)
        c[ph] = out
    return c


def single_sweep(M, a, m, rng):
    d = lambda f: len(M.fr[f]); chi = lambda r: 0.0 if r <= 0 else r * (math.exp(a * math.log(m / r)) - 1)
    moved = 0; gain = 0.0; idx = list(range(len(M.gates))); rng.shuffle(idx)
    for gi in idx:
        old = M.gf[gi]; parts = [(M.F(r, i - 1), M.F(r, i + 1)) for r, i in M.where[gi].items()]
        loE = echelon(list(M.lb[gi]) + [u for p, _ in parts for u in M.fr[p]])
        hiV = None
        for _, q in parts:
            vs = span_vecs(M.fr[q]); hiV = vs if hiV is None else hiV & vs
        if not all(u in hiV for u in loE): continue
        cands = {M.fid(loE), M.fid(echelon(sorted(hiV)))} | {p for p, _ in parts} | {q for _, q in parts}
        loS = span_vecs(loE)
        for u in sorted(hiV - loS): cands.add(M.fid(echelon(loE + [u])))
        def ok(F): return all(inside(M.fr[p], M.fr[F]) and inside(M.fr[F], M.fr[q]) for p, q in parts) and inside(loE, M.fr[F])
        def score(F): return sum(chi(d(F) - d(p)) + chi(d(q) - d(F)) for p, q in parts)
        base = score(old); best, bs = old, base
        for F in cands:
            if F != old and ok(F):
                sc = score(F)
                if sc < bs - 1e-12: best, bs = F, sc
        if best != old: M.gf[gi] = best; moved += 1; gain += base - bs
    return moved, gain


def prune_frames(c):
    """drop unused appended frames (keep the original table prefix), renumber"""
    return c


if __name__ == '__main__':
    c0 = json.load(gzip.open(sys.argv[1])); sys.path.insert(0, sys.argv[2]); import gx
    K = int(sys.argv[4]) if len(sys.argv) > 4 else 3; sw = int(sys.argv[5]) if len(sys.argv) > 5 else 30
    rng = random.Random(int(sys.argv[6]) if len(sys.argv) > 6 else 1)
    h = c0['h']; m = (2 * K + 1) * h; b0 = price(c0, K); print('start b', b0, float(b0))
    c, tag = split(c0); M = CX(c); a = float(b0)
    for s in range(sw):
        m1, g1 = single_sweep(M, a, m, rng); m2, g2 = block_sweep(M, a, m, rng)
        print('sweep', s, 'single', m1, 'block', m2, 'chi/a %.4f' % ((g1 + g2) / a), flush=True)
        if not (m1 or m2): break
    w = to_cert(M); w = rehist(merge(w, tag))
    # drop unused frames beyond the original table
    used = set(w['start']) | set(w['final']) | {g[1] for g in w['A'] + w['B']} | {f for _, _, f in w['ret']}
    keep = list(range(len(c0['frames']))) + [i for i in range(len(c0['frames']), len(w['frames'])) if i in used]
    ren = {o: n for n, o in enumerate(keep)}; w['frames'] = [w['frames'][i] for i in keep]
    for ph in ('A', 'B'):
        for g in w[ph]: g[1] = ren[g[1]]
    w = rehist(w)
    print('span violations', CX(w).span_ok(), '| gates A/B', len(w['A']), len(w['B']), 'vs', len(c0['A']), len(c0['B']), '| new frames', len(w['frames']) - len(c0['frames']))
    st = {}; gx.check1(w, scalar=True, stats=st); print('gx.check1 PASS (E0-E7, exact scalar E5)')
    for K2 in (2, 3): b = price(w, K2); print('b(B_%d) =' % K2, b, float(b))
    json.dump(w, gzip.open(sys.argv[3], 'wt'))
