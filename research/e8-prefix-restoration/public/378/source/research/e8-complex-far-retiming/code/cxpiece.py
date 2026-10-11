"""Piece relocation on a split gcert/1 program: a fan-out piece (s -> t) or fan-in piece (t += s) of an original gate
moves to the end (frame F >= the group frame) or the start (F <= the group frame) of its group, with its own frame
F between the outside neighbours of the shared register and of its own register (source-span rule kept).
Pieces of one original gate commute (fan-out pieces read an unchanged source; fan-in pieces add into one destination)."""
import sys, os, gzip, json, math, random, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cxsplit import *


def piece_pass(c, tag, a, m, eps=1e-9):
    M = CX(c); d = lambda f: len(M.fr[f]); chi = lambda r: 0.0 if r <= 0 else r * (math.exp(a * math.log(m / r)) - 1)
    groups = {}
    for gi, t in enumerate(tag): groups.setdefault(tuple(t[:2]), []).append(gi)
    best = None
    for t, gis in groups.items():
        if len(gis) < 2: continue
        f = M.gf[gis[0]]
        if any(M.gf[g] != f for g in gis): continue
        g0 = M.gates[gis[0]][1]; shared = g0[2]
        if any(M.gates[g][1][2] != shared for g in gis): continue
        ish = [M.where[x][shared] for x in gis]
        info = []
        for gi in gis:
            uniq = [r for r in M.where[gi] if r != shared]
            if len(uniq) != 1: info.append(None); continue
            u = uniq[0]; iu = M.where[gi][u]; info.append((u, M.F(u, iu - 1), M.F(u, iu + 1)))
        for side in ('end', 'start'):
            if side == 'end': ps, ns = f, M.F(shared, max(ish) + 1)
            else: ps, ns = M.F(shared, min(ish) - 1), f
            cands = set()
            for k, gi in enumerate(gis):
                if info[k] is None: continue
                u, pu, nu = info[k]
                loE = echelon(list(M.lb[gi]) + list(M.fr[ps]) + list(M.fr[pu]))
                hiV = span_vecs(M.fr[ns]) & span_vecs(M.fr[nu])
                if not all(x in hiV for x in loE): continue
                cands |= {M.fid(loE), M.fid(echelon(sorted(hiV))), ps, ns, pu, nu}
                for x in sorted(hiV - span_vecs(loE)): cands.add(M.fid(echelon(loE + [x])))
            for F in cands:
                if not (inside(M.fr[ps], M.fr[F]) and inside(M.fr[F], M.fr[ns])): continue
                chosen = []; gain = 0.0
                for k, gi in enumerate(gis):
                    if info[k] is None: continue
                    u, pu, nu = info[k]
                    if not (inside(M.fr[pu], M.fr[F]) and inside(M.fr[F], M.fr[nu]) and inside(M.lb[gi], M.fr[F])): continue
                    du = chi(d(f) - d(pu)) + chi(d(nu) - d(f)) - chi(d(F) - d(pu)) - chi(d(nu) - d(F))
                    if du > eps: chosen.append(gi); gain += du
                if not chosen or len(chosen) == len(gis): continue
                gain -= chi(d(F) - d(ps)) + chi(d(ns) - d(F)) - chi(d(ns) - d(ps))
                if gain > eps and (best is None or gain > best[0]): best = (gain, chosen, side, F, gis)
    if best is None: return c, tag, 0.0
    g_, chosen, side, F, gis = best
    gates = [copy.deepcopy(M.gates[i]) for i in range(len(M.gates))]
    for i in range(len(gates)): gates[i][1][1] = M.gf[i]
    for gi in chosen: gates[gi][1][1] = F
    rest = [i for i in range(len(gates)) if i not in set(chosen)]
    anchor = max(set(gis) - set(chosen)) if side == 'end' else min(set(gis) - set(chosen))
    pos = rest.index(anchor) + (1 if side == 'end' else 0)
    order = rest[:pos] + sorted(chosen) + rest[pos:]
    c2 = copy.deepcopy(c); c2['frames'] = [list(x) for x in M.fr]; c2['A'] = []; c2['B'] = []; tag2 = []
    for i in order:
        c2[gates[i][0]].append(gates[i][1])
        tag2.append(list(tag[i][:2]) + ([side, len(tag)] if i in chosen else []))
    return rehist(c2), tag2, g_
