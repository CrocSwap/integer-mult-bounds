"""(B') Propagated-pin lower bound on helper touch-span log-mass (fixed gate list and order, any frame refit).

For every frame assignment of the same gate list (audit_local frame calculus: a framed gate g runs at one
frame F_g; each register's frame is monotone and equals F_g right after g; start(q) <= frame(q) <= end(q);
centres sit exactly at U_c and targets exactly at their level lev(t) (default ()) at the A/B boundary;
a source's frame contains its port line outside warp episodes):
    F_g >= lo(g) := span( static lower pins of g's registers, lo(previous gate on each register of g) )
    F_g <= hi(g) := meet( static upper pins of g's registers,  hi(next gate on each register of g) )
by induction along each register's gate sequence (forward for lo, backward for hi). Warps are barriers
(no information carried across). Hence on every helper stream, dim F_g in [dim lo(g), dim hi(g)],
nondecreasing, and the touch-span DP (start/end free) over these intervals lower-bounds the log-mass
of its frame chain between first and last touch; summing over helpers lower-bounds the helper inventory
cost of every frame refit of the word. Positive control: the word's own gate frames lie in [lo, hi].
usage: propbound.py WORD.json.gz
"""
import sys, json, math, functools
from collections import Counter, defaultdict
from wordmodel import Word, basis, contained, regs

M = 73
f = lambda r: r * math.log(M / r) if r > 0 else 0.0


@functools.lru_cache(maxsize=None)
def ann(U, h=9):
    return basis([y for y in range(1, 1 << h) if all((y & x).bit_count() % 2 == 0 for x in U)])


@functools.lru_cache(maxsize=None)
def meet(a, b):
    return ann(basis(list(ann(a)) + list(ann(b))))


def span(*xs):
    return basis([z for x in xs for z in x])


def dp_span(lo, hi):
    INF = (float('inf'), 10 ** 9)
    best = {d: (0.0, 0) for d in range(lo[0], hi[0] + 1)}
    for a, b in list(zip(lo, hi))[1:]:
        nb = {}
        for d0, (c0, k0) in best.items():
            for d in range(max(a, d0), b + 1):
                c = (c0 + f(d - d0), k0 + (d > d0))
                if c < nb.get(d, INF):
                    nb[d] = c
        best = nb
    return min(best.values())


def dp_full(lo, hi, s, e):
    """fixed start/end dims; returns (cost, Counter of climb ranks) of an optimal sequence"""
    INF = float('inf')
    best = {s: (0.0, ())}
    for a, b in list(zip(lo, hi)) + [(e, e)]:
        nb = {}
        for d0, (c0, rk) in best.items():
            for d in range(max(a, d0), b + 1):
                c = c0 + f(d - d0)
                if c < nb.get(d, (INF,))[0]:
                    nb[d] = (c, rk + ((d - d0,) if d > d0 else ()))
        best = nb
    c, rk = best[e]
    return c, Counter(rk)


def main():
    Wd = Word(sys.argv[1])
    w = Wd.w; v = Wd.v; FULL = Wd.full; ports = w['ports']
    lev = {int(t): basis(U) for t, U in w.get('target_levels', {}).items()}
    cU = {q: basis(U) for q, U in zip(w['centers'], w['center_frames'])}
    import os
    CONE = os.environ.get('CONE_ONLY') == '1'
    if CONE:
        # pure data-flow cone: only source port lines (lower) and target hyperplanes (upper)
        cU = {}
        Wd.start = [s if q < v else () for q, s in enumerate(Wd.start)]
        Wd.end = [e if v <= q < 2 * v else FULL for q, e in enumerate(Wd.end)]
    ev = Wd.events
    bnd = min(t for t, (s, e) in enumerate(ev) if s == 'cut')     # A/B boundary
    framed = [t for t in range(len(ev)) if t in Wd.gateframe]

    def stat_lo(q, warped):
        if warped:
            return ()
        return span(Wd.start[q], (ports[q],)) if q < v else Wd.start[q]

    # forward pass
    lo_reg = {}
    warped = set()
    lo = {}
    crossed = False
    for t, (s, e) in enumerate(ev):
        if not crossed and t >= bnd:
            crossed = True
            for q, U in cU.items():
                lo_reg[q] = span(lo_reg.get(q, stat_lo(q, q in warped)), U)
            for tt, U in (lev.items() if not CONE else []):
                lo_reg[v + tt] = span(lo_reg.get(v + tt, ()), U)
        if e[0] == 'warp':
            warped.add(e[1]); lo_reg[e[1]] = (); continue
        if t not in Wd.gateframe:
            continue
        rs = regs(e)
        L = span(*[lo_reg.get(q, stat_lo(q, q in warped)) for q in rs])
        lo[t] = L
        for q in rs:
            lo_reg[q] = L
    # backward pass
    hi_reg = {}
    hi = {}
    crossed = False
    lastwarp = {}
    for t in range(len(ev) - 1, -1, -1):
        s, e = ev[t]
        if not crossed and t < bnd:
            crossed = True
            for q, U in cU.items():
                hi_reg[q] = meet(hi_reg.get(q, Wd.end[q]), U)
            for tt in range(v):
                if not CONE:
                    hi_reg[v + tt] = meet(hi_reg.get(v + tt, Wd.end[v + tt]), lev.get(tt, ()))
        if e[0] == 'warp':
            hi_reg[e[1]] = FULL; lastwarp[e[1]] = t; continue
        if t not in Wd.gateframe:
            continue
        rs = regs(e)
        H = FULL
        for q in rs:
            H = meet(H, hi_reg.get(q, Wd.end[q] if q not in lastwarp else FULL))
        hi[t] = H
        for q in rs:
            hi_reg[q] = H
    bad = [t for t in lo if not contained(lo[t], hi[t])]
    ctrl = [t for t in lo if not (contained(lo[t], Wd.gateframe[t]) and contained(Wd.gateframe[t], hi[t]))]
    assert not ctrl, ('positive control failed', ctrl[:5])
    # helper streams (split at B warps)
    lend_t = {}
    for t, (s, e) in enumerate(ev):
        if s == 'Bwarp':
            lend_t.setdefault(e[1], t)
    rows = []
    for r in Wd.live:
        if v <= r < 2 * v:
            continue
        tt = [t for t, s in Wd.touches.get(r, []) if t in Wd.gateframe]
        parts = [('', tt)]
        if r in lend_t:
            parts = [('pre', [t for t in tt if t < lend_t[r]]), ('post', [t for t in tt if t > lend_t[r]])]
        for part, ts in parts:
            if not ts or (r < v and part != 'post'):
                continue
            dims = []
            for t in ts:
                d = len(Wd.gateframe[t])
                if not dims or d != dims[-1]:
                    dims.append(d)
            act = sum(f(b - a) for a, b in zip(dims, dims[1:]))
            c, k = dp_span([len(lo[t]) for t in ts], [len(hi[t]) for t in ts])
            rows.append(dict(reg=r, part=part, actual=act, climbs=len(dims) - 1, lb=c, lb_climbs=k,
                             width=len(Wd.end[r]) - len(Wd.start[r])))
    out = dict(word=sys.argv[1], framed_gates=len(lo), infeasible_gates=len(bad), streams=len(rows),
               span_actual=sum(x['actual'] for x in rows), span_lb=sum(x['lb'] for x in rows),
               actual_climbs=sum(x['climbs'] for x in rows), lb_climbs=sum(x['lb_climbs'] for x in rows),
               lb_climb_hist=dict(sorted(Counter(x['lb_climbs'] for x in rows).items())),
               gate_slack_hist=dict(sorted(Counter(len(hi[t]) - len(lo[t]) for t in lo).items())))
    out['ratio'] = out['span_lb'] / out['span_actual']
    if not CONE:
        # full chains (fixed start/end pins), priced
        prof = Counter(Wd.paid)
        act_full = lb_full = 0.0
        for r in Wd.helpers + [x for x in Wd.live if x < v and any(e[1] == x for _, e in ev if e[0] == 'warp')]:
            if r < v:
                continue  # source lenders: data climbs kept as is
            for c in Wd.climbs.get(r, []):
                prof[c[1]] -= 1
                act_full += f(c[1])
            ts = [t for t, s in Wd.touches.get(r, []) if t in Wd.gateframe]
            c, rk = dp_full([len(lo[t]) for t in ts], [len(hi[t]) for t in ts], len(Wd.start[r]), len(Wd.end[r]))
            lb_full += c
            prof += rk
        prof = +prof
        sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),*(['..']*6),'research','complex-local-word-ceiling'))
        import ceiling as CE
        from fractions import Fraction as Q
        g = Q(1, 10 ** 12)
        b0 = CE.ceiling(dict(Wd.paid), 73, 896, 9, 64, grid=g)[1]
        b1 = CE.ceiling(dict(prof), 73, 896, 9, 64, grid=g)[1]
        out['full_chain'] = dict(actual=act_full, lb=lb_full, lb_profile=dict(sorted(prof.items())),
                                 ceiling_base=float(b0), ceiling_lb=float(b1), ratio=float(b1 / b0))
        if w['warps']:
            from chains import price_root
            out['full_chain']['t74_root_kappa'] = price_root(dict(Wd.paid), dict(prof))
    byw = defaultdict(lambda: [0, 0.0, 0.0, 0, 0])
    for x in rows:
        b = byw[x['width']]; b[0] += 1; b[1] += x['actual']; b[2] += x['lb']; b[3] += x['climbs']; b[4] += x['lb_climbs']
    out['by_width'] = {k: dict(n=b[0], actual=round(b[1], 1), lb=round(b[2], 1), climbs=b[3], lb_climbs=b[4]) for k, b in sorted(byw.items())}
    print(json.dumps(out, indent=1))
    json.dump(rows, open('prop-rows-%s.json' % sys.argv[1].split('/')[-1].split('.')[0], 'w'))


if __name__ == '__main__':
    main()
