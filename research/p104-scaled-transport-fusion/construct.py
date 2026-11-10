"""Fuse two transports across a scalar rescaling and restore the output basis.

The donor transport method is by Rohan Arun, PR6399. The extension to scaled
intervals and the joint correction are by Ali Romman, with OpenAI Codex.
Apache-2.0. The complete source word keeps its original credit.
"""
from copy import deepcopy
from fractions import Fraction as Q
from fusion_support import need

FULL = 127


def add(target, source, coefficient):
    for k, value in tuple(source.items()):
        result = target.get(k, Q(0))+coefficient*value
        if result:
            target[k] = result
        else:
            target.pop(k, None)


def endpoint(word):
    """Return rows in the desired output coordinates, with exact chart checks."""
    n, owned = word['public'], word['owned_fields']
    rows = [{r: Q(1)} if r < n else {} for r in range(n+owned)]
    for r in word['live']:
        rows[r+112][r] = Q(-1)
    frames = word['initial']+[None]*owned
    for index, event in enumerate(word['program']):
        op, r = event[:2]
        if op == 'MOVE':
            need(frames[r] == event[2], 'Transport source at '+str(index))
            frames[r] = event[3]
        elif op in ('INIT', 'CLEAR'):
            need(frames[r] is None if op == 'INIT' else frames[r] == event[2], 'Owned frame at '+str(index))
            rows[r] = {}
            frames[r] = event[2] if op == 'INIT' else None
        else:
            need(frames[r] == event[-1], 'Scalar destination at '+str(index))
            q = Q(event[-2])
            if op == 'SCALE':
                rows[r] = {k: q*v for k, v in rows[r].items() if q*v}
            else:
                need(op in ('ADD', 'COPY') and frames[event[2]] == event[-1], 'Scalar source at '+str(index))
                if op == 'COPY':
                    need(not rows[r], 'COPY into zero at '+str(index))
                add(rows[r], rows[event[2]], q)
    need(frames == word['final']+[None]*owned, 'Complete final frames')
    return rows


def construct(source, specification):
    word = deepcopy(source)
    n, owned = word['public'], word['owned_fields']
    expected = [{r: Q(1)} for r in range(n)]+[{}]*owned
    need(endpoint(source) == expected, 'Exact source endpoint')
    omit, scales, second, injections = set(), {}, {}, {}
    program = source['program']
    for item in specification:
        r, a, b = item['role'], item['first'], item['second']
        e, f, g = item['E'], item['F'], item['G']
        need(program[a] == ['MOVE', r, e, f, False]
             and program[b] == ['MOVE', r, f, g, False], 'Exact source transports')
        need([len(source['frames'][x]) for x in (e, f, g)] == [4, 8, 9], 'Source transport ranks')
        exports, rescalings = [], []
        for i in range(a+1, b):
            event = program[i]
            if event[0] in ('ADD', 'COPY') and event[2] == r:
                exports.append(i)
            if event[1] == r:
                need(event[0] == 'SCALE', 'No intermediate source write')
                rescalings.append(i)
        need(exports == item['exports'] and rescalings == item['scales'], 'Every removed use and scalar change')
        omit.update([a]+exports)
        for i in rescalings:
            need(i not in scales, 'Disjoint scalar changes')
            scales[i] = e
        need(b not in second, 'Disjoint final transports')
        second[b] = e
        cut, receiver = item['injection']
        need(a < cut <= b, 'Injection inside the held interval')
        coefficient = Q(1)
        for i in rescalings:
            if i < cut:
                coefficient /= Q(program[i][2])
        injections.setdefault(cut, []).append(['ADD', receiver, r, str(coefficient), e])
    raw = []
    for i, event in enumerate(program):
        raw.extend(injections.get(i, []))
        if i in omit:
            continue
        event = event.copy()
        if i in second:
            event[2] = second[i]
        if i in scales:
            event[-1] = scales[i]
        raw.append(event)
    word['program'] = raw
    rows = endpoint(word)
    full = {r for r in range(n) if word['final'][r] == FULL}
    need(all(rows[r] == {r: Q(1)} for r in range(n) if r not in full), 'All proper-frame outputs')
    need(all(set(rows[r]) <= full for r in full), 'Closed full-frame output block')
    need(not any(rows[n:]), 'Owned exits')
    changed = sorted(r for r in full if rows[r] != {r: Q(1)})
    correction, done = [], set()
    for j in sorted(full):
        if not rows[j].get(j):
            k = next((k for k in sorted(full-done-{j}) if rows[k].get(j)), None)
            need(k is not None, 'Invertible full output block')
            rows[j], rows[k] = rows[k], rows[j]
            correction.extend([['ADD', j, k, '1', FULL], ['ADD', k, j, '-1', FULL],
                               ['ADD', j, k, '1', FULL], ['SCALE', k, '-1', FULL]])
        pivot = rows[j][j]
        if pivot != 1:
            q = 1/pivot
            need(q.denominator & (q.denominator-1) == 0, 'Dyadic pivot inverse')
            rows[j] = {k: q*v for k, v in rows[j].items()}
            correction.append(['SCALE', j, str(q), FULL])
        for r in sorted(full-{j}):
            q = -rows[r].get(j, Q(0))
            if q:
                need(q.denominator & (q.denominator-1) == 0, 'Dyadic correction')
                add(rows[r], rows[j], q)
                correction.append(['ADD', r, j, str(q), FULL])
        done.add(j)
    need(rows == expected, 'Reduced full output block')
    raw_count = len(raw)
    word['program'].extend(correction)
    need(endpoint(word) == expected, 'Literal corrected endpoint')
    return word, {'changed_full_rows': changed, 'correction': correction,
                  'correction_count': len(correction), 'raw_event_count': raw_count}
