"""Rebuild the shared-carrier input-lift word from the PR6372 word.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
The source word, the native input-lift move class and the checkers retain
their credits in NOTICE.

Each lift cluster has an entrance frame F, a list of anchors and a list of
carriers. An anchor q is an unwritten Z-born full helper. It starts at F
instead of the preparation frame Z. Its Z-column response a = A h is
  - delivered at F to the carriers (carrier detour Z -> F, ADDs, F -> old
    first destination), placed before every anchor of the cluster departs;
  - delivered at the anchor's first-destination frame G_q to the other
    recipients in that group, right after their arrival;
  - restored at the final frame by c += -h_c q.
Every response, restore and carrier trip is an ordinary ADD or MOVE. All
arithmetic is exact (Fractions) and every assumption is asserted.
"""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as Fr

from support import need

Z, OMEGA = 3, 127


def fstr(x):
    x = Fr(x)
    return str(x.numerator) if x.denominator == 1 else f'{x.numerator}/{x.denominator}'


def span_mask(gens):
    """Bitmask over the 512 vectors of the span of the generators."""
    S = {0}
    for g in gens:
        if g not in S:
            S |= {s ^ g for s in S}
    m = 0
    for s in S:
        m |= 1 << s
    return m


def frame_masks(w):
    return [span_mask(f) for f in w['frames']]


def prep(w):
    """Value of every Z-born register (sparse rows over the inputs) when it
    first leaves Z, and the first destination frame of each."""
    P, ini = w['program'], w['initial']
    val = {r: {r: Fr(1)} for r in range(w['public']) if ini[r] == Z}
    G = {}
    for e in P:
        op = e[0]
        if op == 'INIT' and e[-1] == Z:
            val[e[1]] = {}
        elif op == 'ADD' and e[-1] == Z:
            d, s, c = e[1], e[2], Fr(e[3])
            vd = val.setdefault(d, {})
            for k, x in val[s].items():
                y = vd.get(k, 0) + c * x
                if y:
                    vd[k] = y
                else:
                    vd.pop(k, None)
        elif op == 'SCALE' and e[-1] == Z:
            c = Fr(e[2])
            val[e[1]] = {k: c * x for k, x in val[e[1]].items()}
        elif op == 'COPY' and e[-1] == Z:
            raise ValueError('COPY at Z')
        elif op == 'MOVE' and e[2] == Z and e[1] not in G:
            G[e[1]] = e[3]
    return val, G


def lift(word, spec):
    w = deepcopy(word)
    P = w['program']
    val, G = prep(word)
    Mk = frame_masks(word)
    mv_from_Z = {}
    for i, e in enumerate(P):
        if e[0] == 'MOVE' and e[2] == Z and e[1] not in mv_from_Z:
            mv_from_Z[e[1]] = i
    zmax = defaultdict(int)
    for i, e in enumerate(P):
        if e[-1] == Z and e[0] in ('ADD', 'SCALE'):
            zmax[e[1]] = max(zmax[e[1]], i)
            if e[0] == 'ADD':
                zmax[e[2]] = max(zmax[e[2]], i)
    hoisted, delete, restore = set(), set(), []
    pre_carr, insert_before = defaultdict(list), defaultdict(list)
    for cl in spec['clusters']:
        F = cl['F']
        anchors = {int(q): {int(k): Fr(v) for k, v in d['h'].items()} for q, d in cl['anchors'].items()}
        carriers = [int(c) for c in cl['carriers']]
        for q, h in anchors.items():
            need(word['initial'][q] == Z and word['final'][q] == OMEGA, 'Anchor must be a Z-born full helper')
            need(h[q] == 1 and all(h.get(q2, 0) == 0 for q2 in anchors if q2 != q), 'Unit anchor coordinates')
            need(Mk[F] & ~Mk[G[q]] == 0, 'Entrance frame inside the first destination')
        resp = {}
        for q, h in anchors.items():
            for r, row in val.items():
                a = sum(row.get(k, 0) * c for k, c in h.items())
                if a != 0:
                    resp.setdefault(r, {})[q] = a
        Gq = {q: G[q] for q in anchors}
        Tq = {q: mv_from_Z[q] for q in anchors}
        writes = {}
        for q in anchors:
            ws = [(i, e[2], e[3]) for i, e in enumerate(P) if e[-1] == Z and e[0] == 'ADD' and e[1] == q]
            need(not [i for i, e in enumerate(P) if e[-1] == Z and e[0] == 'SCALE' and e[1] == q],
                 'No SCALE of an anchor at Z')
            for i, sr, cf in ws:
                need(G.get(sr) == G[q], 'Postponed source lies in the first-destination group')
                need(not any(e[-1] == Z and e[0] in ('ADD', 'SCALE') and e[1] == sr for e in P[i + 1:]),
                     'Source unchanged at Z after the write')
                need(not any(e[-1] == Z and e[0] == 'ADD' and e[2] == q and j > i for j, e in enumerate(P)),
                     'Anchor not read at Z after being written')
                need(sr not in anchors, 'Source is not an anchor')
                Tq[q] = min(Tq[q], mv_from_Z[sr])
            writes[q] = ws
        recipients = defaultdict(list)
        carr_resp = defaultdict(dict)
        for r, d in resp.items():
            for q, a in d.items():
                if r == q:
                    need(a == 1, 'Unit self response')
                    continue
                if r in carriers:
                    carr_resp[r][q] = a
                elif G.get(r, -1) == Gq[q]:
                    recipients[q].append((r, a))
                else:
                    raise ValueError(f'Unplaced response row {r} of anchor {q}')
        deps = {q: [r for r, a in recipients[q]] + [sr for i, sr, cf in writes[q]] for q in anchors}
        for q in anchors:
            for d in deps[q]:
                Tq[q] = min(Tq[q], mv_from_Z[d])
        X = min(Tq.values())
        for q, h in anchors.items():
            for i, e in enumerate(P):
                if e[-1] == Z and e[0] == 'ADD' and e[2] == q:
                    delete.add(i)
            w['initial'][q] = F
            iq = mv_from_Z[q]
            need(P[iq] == ['MOVE', q, Z, Gq[q], False], 'Anchor departure event')
            delete.add(iq)
            insert_before[Tq[q]].append(['MOVE', q, F, Gq[q], False])
            seq = []
            for d in dict.fromkeys(deps[q]):
                idd = mv_from_Z[d]
                need(P[idd][3] == Gq[q] and P[idd][2] == Z, 'Dependent departs to the same group')
                need(zmax[d] < Tq[q], 'Dependent unused at Z after the hoist')
                if d not in hoisted:
                    seq.append(['MOVE', d, Z, Gq[q], False])
                    hoisted.add(d)
                    delete.add(idd)
            for r, a in recipients[q]:
                seq.append(['ADD', r, q, fstr(a), Gq[q]])
            for i, sr, cf in writes[q]:
                delete.add(i)
                seq.append(['ADD', q, sr, cf, Gq[q]])
            insert_before[Tq[q]].extend(seq)
            for c, cf in h.items():
                if c != q:
                    restore.append(['ADD', c, q, fstr(-cf), OMEGA])
        for c in carriers:
            ic = mv_from_Z[c]
            need(P[ic][0] == 'MOVE' and P[ic][2] == Z, 'Carrier departure event')
            delete.add(ic)
            pos = min(ic, X)
            need(pos > zmax[c], 'Carrier unused at Z after the hoist position')
            blk = [['MOVE', c, Z, F, False]]
            blk += [['ADD', c, q, fstr(a), F] for q, a in sorted(carr_resp[c].items())]
            blk += [['MOVE', c, F, P[ic][3], False]]
            pre_carr[pos].extend(blk)
    out = []
    for i, e in enumerate(P):
        out.extend(pre_carr.get(i, []))
        out.extend(insert_before.get(i, []))
        if i not in delete:
            out.append(e)
    out.extend(restore)
    w['program'] = out
    return w


def construct(source, lifts):
    """Apply the lift rounds in order; return the word."""
    word = source
    for spec in lifts['rounds']:
        word = lift(word, spec)
    return word
