"""Exact rank-one transport merge and zero-restored endpoint correction.
Rohan Arun with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def replay(w, stop=None):
    n = w['public']
    rows = [{i: Q(1)} if i < n else {} for i in range(n+w['owned_fields'])]
    frames = w['initial'] + [None]*w['owned_fields']
    for e in w['program'][:stop]:
        op, d = e[:2]
        if op == 'MOVE':
            need(frames[d] == e[2], 'MOVE source chart')
            frames[d] = e[3]
        elif op in ('INIT', 'CLEAR'):
            need(frames[d] is None if op == 'INIT' else frames[d] == e[2], 'Lifetime chart')
            rows[d] = {}
            frames[d] = e[2] if op == 'INIT' else None
        else:
            need(frames[d] == e[-1], 'Destination chart')
            q = Q(e[-2])
            if op == 'SCALE':
                rows[d] = {i: q*x for i, x in rows[d].items() if q*x}
            else:
                s = e[2]
                need(frames[s] == frames[d], 'Source chart')
                row = {} if op == 'COPY' else rows[d].copy()
                need(op in ('COPY', 'ADD'), 'Scalar opcode')
                for i, x in rows[s].items():
                    z = row.get(i, 0) + q*x
                    if z:
                        row[i] = z
                    else:
                        row.pop(i, None)
                rows[d] = row
    return rows


def construct(w):
    p = w['program']
    field, donor, cache = 400, 779, 781
    first = next(i for i,e in enumerate(p) if e == ['MOVE',field,1090,477,False])
    second = next(i for i,e in enumerate(p) if i > first and e == ['MOVE',field,477,127,False])
    injection = next(i+1 for i,e in enumerate(p) if first < i < second and e == ['MOVE',donor,477,1090,True])
    exports = []
    for i in range(first+1, second):
        e = p[i]
        if e[0] == 'ADD' and e[2] == field:
            exports.append(i)
        elif e[0] in ('ADD','COPY','SCALE') and e[1] == field:
            raise ValueError('Merged source written before final climb')
    value = replay(w, first)[field]
    raw = []
    for i, event in enumerate(p):
        if i == injection:
            raw.append(['ADD',donor,field,'1',1090])
        if i in {first, *exports}:
            continue
        e = event[:]
        if i == second:
            e[2] = 1090
        raw.append(e)
    packet = deepcopy(w)
    packet['program'] = raw
    baseline, actual = replay(w), replay(packet)
    pivot = next(i for i,v in value.items() if v)
    u = {}
    for i,(a,b) in enumerate(zip(actual,baseline)):
        diff = {j:a.get(j,0)-b.get(j,0) for j in set(a)|set(b) if a.get(j,0) != b.get(j,0)}
        c = diff.get(pivot,Q(0))/value[pivot]
        need(diff == {j:c*v for j,v in value.items() if c*v}, 'Rank-one suffix error')
        if c:
            u[i] = c
    cov = dict(value)
    for role in w['live']:
        c = value.get(role+112,0)
        if c:
            cov[role] = cov.get(role,0)-c
            if not cov[role]:
                cov.pop(role)
    den = 1+sum(cov.get(i,0)*x for i,x in u.items())
    need(den != 0, 'Invertible rank-one repair')
    need(all(w['final'][i] == 127 for i in set(cov)|set(u)), 'Free full-chart repair')
    need(not any(e[0] == 'CLEAR' and e[1] == cache and e[2] == 127 for e in p), 'Distinct new zero-exit obligation')
    cleanup = [['INIT',cache,127]]
    cleanup += [['ADD',cache,j,str(c),127] for j,c in sorted(cov.items())]
    cleanup += [['ADD',i,cache,str(-c/den),127] for i,c in sorted(u.items())]
    cleanup += [['ADD',cache,j,str(-den*c),127] for j,c in sorted(cov.items())]
    packet['program'] += cleanup
    need(not replay(packet)[cache], 'Cache zero before CLEAR')
    packet['program'].append(['CLEAR',cache,127])
    need(replay(packet) == baseline, 'Complete independent sparse endpoint')
    return packet
