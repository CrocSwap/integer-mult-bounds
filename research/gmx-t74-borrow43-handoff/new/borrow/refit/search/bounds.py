"""Exact per-gate frame bounds lo(g) <= F_g <= hi(g) over ALL refits of a fixed BORROW-WORD gate list
(audit_local frame calculus, exact pins: start/end, A/B-boundary equality pins for targets (levels) and
centres (U_c) applied to the last A gate itself, warp U equality on the lender's preceding gate and E as
lower bound after). The solution set is a lattice (pointwise meet/join), and constraints only point
forward in time, so lo and hi are attained and can be mixed across any time cut.
"""
import sys, json, gzip, functools
from collections import defaultdict
import os as _os,sys as _sys;_H=_os.path.dirname(_os.path.abspath(__file__));_sys.path[:0]=[_H,_os.path.join(_H,'..','..'),_os.path.join(_H,'..','..','prelife','search')]   # this dir, new/borrow, prelife/search (wordmodel)
from wordmodel import Word, basis, contained, regs

H = 9


@functools.lru_cache(maxsize=None)
def ann(U):
    return basis([y for y in range(1, 1 << H) if all((y & x).bit_count() % 2 == 0 for x in U)])


@functools.lru_cache(maxsize=None)
def meet(a, b):
    return ann(basis(list(ann(a)) + list(ann(b))))


def span(*xs):
    return basis([z for x in xs for z in x])


class Bounds:
    def __init__(s, path):
        Wd = Word(path); s.Wd = Wd
        w = Wd.w; v = Wd.v; s.v = v
        ev = Wd.events; s.ev = ev
        s.bnd = min(t for t, (sec, e) in enumerate(ev) if sec == 'cut')
        lev = {int(t): basis(U) for t, U in w.get('target_levels', {}).items()}
        pin = {v + t: lev.get(t, ()) for t in range(v)}
        for q, U in zip(w['centers'], w['center_frames']):
            pin[q] = basis(U)
        s.pin = pin
        warps = w['warps']
        # per-register event list (framed gates and warps), with times
        byreg = defaultdict(list)
        for t, (sec, e) in enumerate(ev):
            if sec in ('precondition', 'compensation', 'cut'):
                continue
            if e[0] == 'warp':
                if sec == 'A':
                    _, r, op, fr, to = e
                    byreg[r].append((t, 'warp', basis(fr), basis(to)))
                else:
                    _, r, op = e
                    rec = warps[op - 1]
                    byreg[r].append((t, 'warp', basis(rec[3]), basis(rec[4])))
            else:
                for q in regs(e):
                    byreg[q].append((t, 'gate'))
        s.byreg = byreg
        xlo = defaultdict(tuple); xhi = defaultdict(lambda: Wd.full)
        stat_bad = []
        for r, L in byreg.items():
            # start lower pin on the first gate (if before any warp)
            prevg = None; cur_lo = Wd.start[r]
            for x in L:
                if x[1] == 'warp':
                    if prevg is None:
                        if Wd.start[r] != x[2]:
                            stat_bad.append(('warp-start', r))
                    else:
                        xlo[prevg] = span(xlo[prevg], x[2]); xhi[prevg] = meet(xhi[prevg], x[2])
                    prevg = None
                else:
                    prevg = x[0]
            # boundary equality pins
            if r in pin:
                lastA = [x[0] for x in L if x[0] < s.bnd and x[1] == 'gate']
                if lastA:
                    g = lastA[-1]
                    xlo[g] = span(xlo[g], pin[r]); xhi[g] = meet(xhi[g], pin[r])
        s.stat_bad = stat_bad
        # forward pass
        lo = {}; lo_reg = {}
        crossed = False
        for t, (sec, e) in enumerate(ev):
            if not crossed and t >= s.bnd:
                crossed = True
                for q, U in pin.items():
                    lo_reg[q] = span(lo_reg.get(q, Wd.start[q]), U)
            if sec in ('precondition', 'compensation', 'cut'):
                continue
            if e[0] == 'warp':
                r = e[1]
                E = basis(e[4]) if sec == 'A' else basis(warps[e[2] - 1][4])
                lo_reg[r] = E; continue
            rs = regs(e)
            Lw = span(xlo[t], *[lo_reg.get(q, Wd.start[q]) for q in rs])
            lo[t] = Lw
            for q in rs:
                lo_reg[q] = Lw
        hi = {}; hi_reg = {}
        crossed = False
        for t in range(len(ev) - 1, -1, -1):
            sec, e = ev[t]
            if not crossed and t < s.bnd:
                crossed = True
                for q, U in pin.items():
                    hi_reg[q] = meet(hi_reg.get(q, Wd.end[q]), U)
            if sec in ('precondition', 'compensation', 'cut'):
                continue
            if e[0] == 'warp':
                r = e[1]
                U = basis(e[3]) if sec == 'A' else basis(warps[e[2] - 1][3])
                hi_reg[r] = U; continue
            rs = regs(e)
            Hh = xhi[t]
            for q in rs:
                Hh = meet(Hh, hi_reg.get(q, Wd.end[q]))
            hi[t] = Hh
            for q in rs:
                hi_reg[q] = Hh
        s.lo, s.hi = lo, hi
        gf = Wd.gateframe
        s.infeasible = [t for t in lo if not contained(lo[t], hi[t])]
        s.ctrl_bad = [t for t in lo if not (contained(lo[t], gf[t]) and contained(gf[t], hi[t]))]
        assert not s.ctrl_bad, s.ctrl_bad[:5]
        assert not s.infeasible


if __name__ == '__main__':
    b = Bounds(sys.argv[1])
    from collections import Counter
    print('gates', len(b.lo), 'slack hist', dict(sorted(Counter(len(b.hi[t]) - len(b.lo[t]) for t in b.lo).items())), 'static bad', b.stat_bad)
