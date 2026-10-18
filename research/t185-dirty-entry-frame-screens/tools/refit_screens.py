# SPDX-License-Identifier: Apache-2.0
"""Frame-refit screens inside one fixed BORROW-WORD scalar word (side check; see README scope).

Each register's paid climbs depend only on the frames of the gates it touches. Three exact move families are
screened, all subject to every pin (A/B warps, target levels, centre frames) and end frame:

* single gate: set one gate frame to any candidate between join(previous frames) and meet(next requirements)
  of its registers (candidates: both extremes and the neighbouring frames);
* forward cascade: raise a gate frame so one register's next climb merges into it, then raise each affected
  partner's next gate as needed until absorbed; an exact pin or end frame that would be exceeded rejects;
* backward cascade: lower a gate frame to a register's previous frame so its climb merges into the next one,
  lowering partners' previous gates as needed; reaching a pin or start frame rejects.

Cost of a register's climbs is sum H_d over its steps with H_d = d^p at the #2863 moment root (float); the
centre path is unchanged by gate frames and omitted. A move is reported only if it lowers the total.

Prepared for digitalis-p with Claude (Anthropic) assistance. Apache-2.0.
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wordlib as W  # noqa: E402

P = 1 - 0.001720100805416886


def H(d):
    return d ** P if d > 0 else 0.0


def build(x):
    """Per-register ordered events: ('gate', key) | ('pin', before, after) | ('end', frame)."""
    start, end = W.start_frames(x), W.end_frames(x)
    ev, gates = defaultdict(list), {}

    def addgate(key, g):
        regs = list(W.regs_of(g))
        gates[key] = dict(frame=W.basis(g[-1]), regs=regs)
        for r in regs:
            ev[r].append(('gate', key))

    for i, g in enumerate(x['A']):
        if g[0] == 'warp':
            ev[g[1]].append(('pin', W.basis(g[3]), W.basis(g[4])))
        else:
            addgate(('A', i), g)
    lev = {int(t): W.basis(u) for t, u in x.get('target_levels', {}).items()}
    for t in range(W.V):
        ev[W.V + t].append(('pin', lev.get(t, ()), lev.get(t, ())))
    for r, u in zip(x['centers'], x['center_frames']):
        ev[r].append(('pin', W.basis(u), W.basis(u)))
    bw = defaultdict(list)
    for rec in x['warps']:
        bw[rec[0]].append(rec)
    for p in range(len(x['B']) + 1):
        for rec in bw.get(p, []):
            ev[rec[1]].append(('pin', W.basis(rec[3]), W.basis(rec[4])))
        if p < len(x['B']):
            addgate(('B', p), x['B'][p])
    for i, g in enumerate(x['restore']):
        addgate(('R', i), g)
    live = set(range(W.NREG)) - set(x['removed'])
    for r in live:
        ev[r].append(('end', end[r]))
    pos = {(r, e[1]): i for r, lst in ev.items() for i, e in enumerate(lst) if e[0] == 'gate'}
    return start, ev, gates, live, pos


def regcost(r, start, ev, gates, over=None):
    over = over or {}
    cur, c = start[r], 0.0
    for e in ev[r]:
        if e[0] == 'gate':
            u = over.get(e[1], gates[e[1]]['frame'])
            if not W.contained(cur, u):
                return None
            c += H(len(u) - len(cur))
            cur = u
        elif e[0] == 'pin':
            if cur != e[1]:
                return None
            cur = e[2]
        else:
            if not W.contained(cur, e[1]):
                return None
            c += H(len(e[1]) - len(cur))
            cur = e[1]
    return c


def frame_at(r, i, start, ev, gates, over, prev=True):
    lst = ev[r]
    if prev:
        if i == 0:
            return start[r], 'start'
        e = lst[i - 1]
        return (over.get(e[1], gates[e[1]]['frame']), e[1]) if e[0] == 'gate' else (e[2], 'pin')
    if i + 1 >= len(lst):
        return None, None
    e = lst[i + 1]
    if e[0] == 'gate':
        return over.get(e[1], gates[e[1]]['frame']), e[1]
    return e[1], e[0]


def delta(touched, over, start, ev, gates, base):
    d = 0.0
    for r in touched:
        c = regcost(r, start, ev, gates, over)
        if c is None:
            return None
        d += c - base[r]
    return d


def screens(x):
    start, ev, gates, live, pos = build(x)
    base = {r: regcost(r, start, ev, gates) for r in live}
    if any(v is None for v in base.values()):
        raise W.LedgerError('input word violates its own frame chains')
    out: dict = dict(single=dict(tried=0, improving=[]), forward=dict(tried=0, feasible=0, improving=[]),
               backward=dict(tried=0, feasible=0, improving=[]))
    # single-gate moves
    for key, g in gates.items():
        info = []
        for r in g['regs']:
            i = pos[(r, key)]
            pf, _ = frame_at(r, i, start, ev, gates, {}, True)
            nf, _ = frame_at(r, i, start, ev, gates, {}, False)
            info.append((r, pf, nf))
        if any(nf is None for _, _, nf in info):
            continue
        lo, hi = W.join(*[pf for _, pf, _ in info]), None
        for _, _, nf in info:
            hi = nf if hi is None else W.meet(hi, nf)
        if not W.contained(lo, hi):
            continue
        cands = {lo, hi} | {f for _, pf, nf in info for f in (pf, nf) if W.contained(lo, f) and W.contained(f, hi)}
        for u in cands:
            if u == g['frame']:
                continue
            out['single']['tried'] += 1
            d = delta([r for r, _, _ in info], {key: u}, start, ev, gates, base)
            if d is not None and d < -1e-12:
                out['single']['improving'].append([str(key), list(u), d])
    # forward cascades
    for r in sorted(live):
        prev = None
        for e in ev[r]:
            if e[0] != 'gate':
                prev = None
                continue
            f = gates[e[1]]['frame']
            if prev is not None and len(f) > len(gates[prev]['frame']):
                out['forward']['tried'] += 1
                over, todo, touched, ok = {}, [(prev, f)], set(), True
                while todo and ok:
                    key, u = todo.pop()
                    cur = over.get(key, gates[key]['frame'])
                    nu = W.join(cur, u)
                    if nu == cur:
                        continue
                    over[key] = nu
                    for q in gates[key]['regs']:
                        touched.add(q)
                        nf, nk = frame_at(q, pos[(q, key)], start, ev, gates, over, False)
                        if nf is None or W.contained(nu, nf):
                            continue
                        if nk in ('pin', 'end'):
                            ok = False
                            break
                        todo.append((nk, nu))
                    if len(over) > 400:
                        ok = False
                if ok:
                    d = delta(touched, over, start, ev, gates, base)
                    if d is not None:
                        out['forward']['feasible'] += 1
                        if d < -1e-12:
                            out['forward']['improving'].append([r, str(prev), d])
            prev = e[1]
    # backward cascades
    for r in sorted(live):
        for i, e in enumerate(ev[r]):
            if e[0] != 'gate' or i + 1 >= len(ev[r]):
                continue
            pf, _ = frame_at(r, i, start, ev, gates, {}, True)
            if len(gates[e[1]]['frame']) <= len(pf):
                continue
            out['backward']['tried'] += 1
            over, todo, touched, ok = {}, [(e[1], pf)], set(), True
            while todo and ok:
                key, low = todo.pop()
                cur = over.get(key, gates[key]['frame'])
                nl = W.meet(cur, low)
                if nl == cur:
                    continue
                over[key] = nl
                for q in gates[key]['regs']:
                    touched.add(q)
                    qf, qk = frame_at(q, pos[(q, key)], start, ev, gates, over, True)
                    if W.contained(qf, nl):
                        continue
                    if qk in ('start', 'pin'):
                        ok = False
                        break
                    todo.append((qk, nl))
                if len(over) > 400:
                    ok = False
            if ok:
                d = delta(touched, over, start, ev, gates, base)
                if d is not None:
                    out['backward']['feasible'] += 1
                    if d < -1e-12:
                        out['backward']['improving'].append([r, str(e[1]), d])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--word', required=True, type=Path)
    a = ap.parse_args()
    x, digest = W.load(a.word)
    res: dict = screens(x)
    res['word_sha256'] = digest
    print(json.dumps(res))


if __name__ == '__main__':
    main()
