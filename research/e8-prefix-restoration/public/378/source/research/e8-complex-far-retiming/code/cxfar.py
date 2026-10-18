"""Far piece relocation on a split gcert/1 program: an elementary piece (out: u += c s with s only read; in: s += c u with
u only read) moves forward/backward across gates that commute with it as scalar operations (they touch neither u, nor
write the read register; for an in-piece, other gates may only ADD into s from sources other than u, never read s),
within its phase, and gets its own best frame between the new neighbours. Greedy best move per pass.
usage: cxfar.py CERT(.json.gz or anneal output) GXDIR OUT [passes]"""
import sys, os, gzip, json, math, copy, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cxpiece import *
from cxretime import sweep as bsweep


def rw(g):
    """(reads, writes) of a gate"""
    if g[0] == 'neg': return {g[2]}, {g[2]}
    if g[0] == 'out': return {g[2]} | {t for t, _, _ in g[3]} | set(g[4]), {t for t, _, _ in g[3]}
    return {g[2]} | {s for s, _, _ in g[3]}, {g[2]}


def far_pass(c, tag, a, m):
    M = CX(c); d = lambda f: len(M.fr[f]); chi = lambda r: 0.0 if r <= 0 else r * (math.exp(a * math.log(m / r)) - 1)
    G = M.gates; best = None
    for i, (ph, g) in enumerate(G):
        if g[0] == 'out' and len(g[3]) == 1 and not g[4]: u = g[3][0][0]; s = g[2]; kind = 'out'
        elif g[0] == 'in' and len(g[3]) == 1: u = g[2]; s = g[3][0][0]; kind = 'in'   # u written (dst), s read
        else: continue
        # registers: w = written register (u for out, u for in): naming: wreg written, rreg read
        wreg, rreg = u, s
        iw, ir = M.where[i][wreg], M.where[i][rreg]
        f_i = M.gf[i]
        pw, nw = M.F(wreg, iw - 1), M.F(wreg, iw + 1)
        a_r, b_r = M.F(rreg, ir - 1), M.F(rreg, ir + 1)
        rem_r = chi(d(f_i) - d(a_r)) + chi(d(b_r) - d(f_i)) - chi(d(b_r) - d(a_r))
        for step in (1, -1):
            j = i
            while True:
                j += step
                if j < 0 or j >= len(G) or G[j][0] != ph: break
                rj, wj = rw(G[j][1])
                if wreg in rj or rreg in wj: break   # does not commute (another addition into wreg also breaks: keep simple)
                if rreg not in rj: continue          # read register untouched: same neighbours
                # new position just after j (forward) or just before j (backward): rreg neighbours change
                jr = M.where[j][rreg]
                if step == 1: ps, ns = M.F(rreg, jr), M.F(rreg, jr + 1) if jr + 1 != ir else b_r
                else: ps, ns = (M.F(rreg, jr - 1) if jr - 1 != ir else a_r), M.F(rreg, jr)
                if step == 1 and jr + 1 == ir: continue
                loE = echelon(list(M.lb[i]) + list(M.fr[ps]) + list(M.fr[pw]))
                hiV = span_vecs(M.fr[ns]) & span_vecs(M.fr[nw])
                if not all(x in hiV for x in loE): continue
                cands = {M.fid(loE), M.fid(echelon(sorted(hiV))), ps, ns, pw, nw}
                for x in sorted(hiV - span_vecs(loE))[:64]: cands.add(M.fid(echelon(loE + [x])))
                old_w = chi(d(f_i) - d(pw)) + chi(d(nw) - d(f_i))
                for F in cands:
                    if not (inside(M.fr[ps], M.fr[F]) and inside(M.fr[F], M.fr[ns]) and inside(M.fr[pw], M.fr[F]) and inside(M.fr[F], M.fr[nw]) and inside(loE, M.fr[F])): continue
                    gain = old_w - chi(d(F) - d(pw)) - chi(d(nw) - d(F)) + rem_r - (chi(d(F) - d(ps)) + chi(d(ns) - d(F)) - chi(d(ns) - d(ps)))
                    if gain > 1e-9 and (best is None or gain > best[0]): best = (gain, i, j, step, F)
    if best is None: return c, tag, 0.0
    gain, i, j, step, F = best
    gates = [copy.deepcopy(x) for x in G]
    for k in range(len(gates)): gates[k][1][1] = M.gf[k]
    gates[i][1][1] = F
    order = [k for k in range(len(gates)) if k != i]
    pos = order.index(j) + (1 if step == 1 else 0); order.insert(pos, i)
    c2 = copy.deepcopy(c); c2['frames'] = [list(x) for x in M.fr]; c2['A'] = []; c2['B'] = []; tag2 = []
    for k in order:
        c2[gates[k][0]].append(gates[k][1]); tag2.append(list(tag[k][:2]) + (['far', k] if k == i else list(tag[k][2:])))
    return rehist(c2), tag2, gain


if __name__ == '__main__':
    src = json.load(gzip.open(sys.argv[1])); sys.path.insert(0, sys.argv[2]); import gx
    if 'cert' in src: c, tag = src['cert'], [tuple(t) for t in src['tag']]
    else: c, tag = split(src)
    K = 3; h = c['h']; m = (2 * K + 1) * h; b0 = price(c, K); a = float(b0); rng = random.Random(1)
    print('start b3', b0, float(b0)); passes = int(sys.argv[4]) if len(sys.argv) > 4 else 100
    for p in range(passes):
        c, tag, g = far_pass(c, tag, a, m)
        M = CX(c)
        for s in range(10):
            m1, _ = single_sweep(M, a, m, rng); m2, _ = bsweep(M, a, m, rng)
            if not (m1 or m2): break
        c = rehist(to_cert(M)); c, tag, g2 = piece_pass(c, tag, a, m)
        b = price(c, K); print('pass', p, 'far gain/a %.3f piece %.3f' % (g / a, g2 / a), 'b3', b, '%.12e' % float(b), flush=True)
        if g == 0 and g2 == 0: break
    gx.check1(c, scalar=True); print('gx.check1 PASS')
    json.dump(dict(cert=c, tag=[list(t) for t in tag]), gzip.open(sys.argv[3], 'wt'))
