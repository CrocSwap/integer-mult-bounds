#!/usr/bin/env python3
"""Concave frame descent (retiming) on a gcert/1 complex program.

Model (the inherited invariant of both sides, checked on #346's program: 0 violations):
  * every register's frame chain is nested and strictly climbing; x start at the port line, y start at 0 and end at
    the cap, slots start at 0 and end at the full frame; retained slots sit at their (h-2)-dim frame at the scatter cut;
  * a gate's frame contains the F2 span of the port labels of the content support of every named x / s register
    (y roles excluded, as on the bit side);
  * cost = sum over climbs of phi(r) = r ln(m/r), m = 5h (first-order proxy of the moment root; exact root by moment.py).
Each gate may move to any frame in [lo, hi], lo = join(prev frames, spans), hi = meet(next frames); candidates are the
extremes and the joins/meets with single-register neighbours (concave objective => extremal optimum per gate).
Output: a new gcert/1 (frames table extended, blocks and N recomputed) plus a moves log.
"""
import argparse, gzip, json, math, sys, time
from collections import Counter, defaultdict
from fractions import Fraction as Fr


def load(p):
    return json.loads(gzip.decompress(open(p, 'rb').read())) if p.endswith('.gz') else json.load(open(p))


def rref(rows):
    piv = {}
    for x in rows:
        for k in sorted(piv, reverse=True):
            if x >> k & 1:
                x ^= piv[k]
        if x:
            k = x.bit_length() - 1
            for kk in list(piv):
                if piv[kk] >> k & 1:
                    piv[kk] ^= x
            piv[k] = x
    return tuple(piv[k] for k in sorted(piv, reverse=True))


def reduce(u, basis):
    for b in basis:
        if u >> (b.bit_length() - 1) & 1:
            u ^= b
    return u


def inside(a, b):
    return all(reduce(u, b) == 0 for u in a)


def join(*fs):
    rows = []
    for f in fs:
        rows.extend(f)
    return rref(rows)


def meet(a, b, h):
    """intersection of two subspaces of F2^h (rref tuples)"""
    if inside(a, b):
        return a
    if inside(b, a):
        return b
    # solve: vectors of span(a) that lie in span(b): parametrize span(a) by coefficients over its basis
    # x = sum c_i a_i ; reduce modulo b -> linear system over the c_i
    n = len(a)
    red = [reduce(u, b) for u in a]
    # find kernel of c -> sum c_i red_i   (bits of red_i as rows of an n-column system)
    # Gaussian elimination on the n vectors red_i with tracking of combinations
    vecs = [(red[i], 1 << i) for i in range(n)]
    pivots = {}
    kernel = []
    for val, comb in vecs:
        for k in sorted(pivots, reverse=True):
            if val >> k & 1:
                pv, pc = pivots[k]
                val ^= pv; comb ^= pc
        if val == 0:
            kernel.append(comb)
        else:
            pivots[val.bit_length() - 1] = (val, comb)
    out = []
    for comb in kernel:
        x = 0
        for i in range(n):
            if comb >> i & 1:
                x ^= a[i]
        out.append(x)
    return rref(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cert')
    ap.add_argument('out')
    ap.add_argument('--rounds', type=int, default=12)
    ap.add_argument('--moves', default=None)
    ap.add_argument('--freeze-y', action='store_true', help='never move a gate that names a y role')
    ap.add_argument('--freeze-x', action='store_true', help='never move a gate that names an x role')
    a = ap.parse_args()
    t0 = time.time()
    c = load(a.cert)
    h, v, R = c['h'], c['v'], c['R']
    n = 2 * v + R
    m = 5 * h
    ports = c['ports']
    frames = [tuple(f) for f in c['frames']]
    fid = {f: i for i, f in enumerate(frames)}

    def frame_id(f):
        if f not in fid:
            fid[f] = len(frames); frames.append(f)
        return fid[f]
    cls = lambda r: 'x' if r < v else 'y' if r < 2 * v else 's'
    G = c['A'] + c['B']
    nA = len(c['A'])
    gframe = [g[1] for g in G]

    def regs_of(g):
        return [g[2]] + [t for t, _, _ in g[3]] + (list(g[4]) if g[0] == 'out' else [])
    # ---- content replay: span requirement per (gate, register) for x / s roles
    reg = [({r: Fr(1)} if r < v else {}) for r in range(n)]

    def axpy(t, src, co):
        d = reg[t]
        for k, u in src.items():
            w = d.get(k, 0) + co * u
            if w:
                d[k] = w
            else:
                d.pop(k, None)
    span_req = [None] * len(G)   # rref of required span per gate (x/s named registers), union of before/after
    ret_frame = {s: f for _, s, f in c['ret']}
    for gi, g in enumerate(G):
        if gi == nA:
            tot = {k: dict(reg[s]) for k, s, _ in c['ret']}
            for t in range(v):
                for k in range(h):
                    co = Fr(1, 3) if ports[t] >> k & 1 else Fr(-1, 6)
                    axpy(v + t, tot[k], co)
        rs = regs_of(g)
        rows = set()
        for r in rs:
            if cls(r) != 'y':
                rows.update(ports[j] for j in reg[r])
        if g[0] == 'out':
            src = dict(reg[g[2]])
            for t, aa, bb in g[3]:
                axpy(t, src, Fr(aa, bb))
        else:
            for s, aa, bb in g[3]:
                axpy(g[2], reg[s], Fr(aa, bb))
        for r in rs:
            if cls(r) != 'y':
                rows.update(ports[j] for j in reg[r])
        span_req[gi] = rref(rows)
        assert inside(span_req[gi], frames[gframe[gi]]), ('span rule violated by the input program', gi)
    print('replay done', round(time.time() - t0, 1), 's', flush=True)
    # ---- per-register event chains: events are ('start'), gate indices, ('cut', frame) for ret slots, ('final')
    chain = defaultdict(list)       # r -> list of events; event = gate index (int) or ('S', fid) / ('F', fid)
    for r in range(n):
        chain[r].append(('S', c['start'][r]))
    for gi, g in enumerate(G):
        if gi == nA:
            for s, f in ret_frame.items():
                chain[s].append(('P', f))
        for r in regs_of(g):
            chain[r].append(gi)
    for r in range(n):
        chain[r].append(('F', c['final'][r]))
    pos = {}                         # (r, gi) -> index in chain[r]
    for r in range(n):
        for i, e in enumerate(chain[r]):
            if isinstance(e, int):
                pos[r, e] = i

    def ev_frame(e):
        return gframe[e] if isinstance(e, int) else e[1]

    def phi(r):
        return 0.0 if r == 0 else r * math.log(m / r)

    def dim(f):
        return len(frames[f])

    def cost_of(gi, f):
        """cost of the climbs into and out of gate gi for all its registers if it sits at frame id f"""
        tot = 0.0
        for r in regs_of(G[gi]):
            i = pos[r, gi]
            pf = ev_frame(chain[r][i - 1]); nf = ev_frame(chain[r][i + 1])
            tot += phi(dim(f) - dim(pf)) + phi(dim(nf) - dim(f))
        return tot
    frozen = set()
    for gi, g in enumerate(G):
        ks = {cls(r) for r in regs_of(g)}
        if (a.freeze_y and 'y' in ks) or (a.freeze_x and 'x' in ks):
            frozen.add(gi)
    total_moves = []
    J0 = None
    for rnd in range(a.rounds):
        moved = 0; gain = 0.0
        for gi, g in enumerate(G):
            if gi in frozen:
                continue
            rs = regs_of(g)
            prevs = []; nexts = []
            for r in rs:
                i = pos[r, gi]
                prevs.append(ev_frame(chain[r][i - 1])); nexts.append(ev_frame(chain[r][i + 1]))
            lo = join(span_req[gi], *[frames[p] for p in prevs])
            hi = frames[nexts[0]]
            for nf in nexts[1:]:
                hi = meet(hi, frames[nf], h)
            if not inside(lo, hi):
                raise AssertionError(('empty interval', gi))
            cur = gframe[gi]
            cands = {frame_id(lo), frame_id(hi), cur}
            # single-neighbour joins / meets
            for p in prevs:
                cands.add(frame_id(join(lo, frames[p])))
            for nf in nexts:
                cands.add(frame_id(meet(hi, frames[nf], h)))
            # also joins of lo with the next frames? (must be inside hi) and meets of hi with prev (must contain lo)
            extra = set()
            for f in list(cands):
                for p in prevs:
                    extra.add(frame_id(join(frames[f], frames[p])))
            for f in extra:
                if inside(lo, frames[f]) and inside(frames[f], hi):
                    cands.add(f)
            cands = [f for f in cands if inside(lo, frames[f]) and inside(frames[f], hi)]
            base = cost_of(gi, cur)
            best, bestc = cur, base
            for f in cands:
                if f == cur:
                    continue
                cc = cost_of(gi, f)
                if cc < bestc - 1e-9:
                    best, bestc = f, cc
            if best != cur:
                total_moves.append((gi, cur, best))
                gframe[gi] = best; moved += 1; gain += base - bestc
        # recompute J
        J = 0.0
        H = {k: Counter() for k in 'xysc'}
        curf = list(c['start'])
        for gi, g in enumerate(G):
            if gi == nA:
                for s, f in ret_frame.items():
                    assert curf[s] == f, ('retained slot moved before the cut', s)
                    H['c'][dim(f)] += 1
            f = gframe[gi]
            for r in regs_of(g):
                o = curf[r]
                if o != f:
                    assert dim(o) < dim(f) and inside(frames[o], frames[f]), ('nesting', gi, r)
                    H[cls(r)][dim(f) - dim(o)] += 1; curf[r] = f
        for r in range(n):
            f = c['final'][r]; o = curf[r]
            if o != f:
                assert dim(o) < dim(f) and inside(frames[o], frames[f]), ('final nesting', r)
                H[cls(r)][dim(f) - dim(o)] += 1
        J = sum(phi(r) * k for w in H.values() for r, k in w.items() if w is not H['c'])
        if J0 is None:
            J0 = J + gain   # J before this round's moves (approximately: gain is exact first-order)
        print('round %d: %d moves, gain %.3f, J %.3f, calls %d, frames %d, %.0fs' % (
            rnd, moved, gain, J, sum(sum(w.values()) for w in H.values()), len(frames), time.time() - t0), flush=True)
        if moved == 0:
            break
    # ---- emit
    out = dict(c)
    out['frames'] = [list(f) for f in frames]
    out['A'] = [[g[0], gframe[gi]] + g[2:] for gi, g in enumerate(G[:nA])]
    out['B'] = [[g[0], gframe[nA + gi]] + g[2:] for gi, g in enumerate(G[nA:])]
    out['blocks'] = {k: {str(r): kk for r, kk in sorted(w.items())} for k, w in H.items()}
    out['N'] = sum(r * kk for w in H.values() for r, kk in w.items())
    out['derived_from'] = c['derived_from'] + ' + concave frame descent (retime_gcert.py, %d moves)' % len(total_moves)
    data = json.dumps(out, separators=(',', ':')).encode()
    open(a.out, 'wb').write(gzip.compress(data) if a.out.endswith('.gz') else data)
    if a.moves:
        json.dump(dict(moves=total_moves, J=J), open(a.moves, 'w'))
    print('done: %d moves, N %d -> %d, J %.3f' % (len(total_moves), c['N'], out['N'], J))


if __name__ == '__main__':
    main()
