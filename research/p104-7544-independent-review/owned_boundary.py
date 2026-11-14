# SPDX-License-Identifier: Apache-2.0
"""Separate sparse rational replay, retaining each operand BEFORE erasure.

Written for the #7544 review; imports no construction or source replay code.
MOVE is interpreted in the normalized coordinates supplied by the retained
physical-frame premise. This checker does not establish that premise.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def encoded(row):
    return [[i, str(q)] for i, q in sorted(row.items()) if q]


def plus(row, source, q):
    for k, v in source.items():
        t = row.get(k, 0) + q * v
        if t:
            row[k] = t
        else:
            row.pop(k, None)


def targets(word):
    n = word['public']
    answer = [{i: Fraction(1)} for i in range(n)]
    direct = set(word['hosted']['Dports'])
    for i, x in enumerate(word['live']):
        y = x + 112
        if i in direct:
            answer[y][x] = Fraction(1)
        else:
            answer[x][y] = Fraction(-1)
            answer[y] = {x: Fraction(1, 2), y: Fraction(1, 2)}
    for x, y in zip(word['hosted']['X2'], word['hosted']['Y2'], strict=True):
        answer[x][y] = Fraction(-1)
    return answer


def trace(word):
    n, m = word['public'], word['public'] + word['owned_fields']
    require(len(word['initial']) == len(word['final']) == n, 'Boundary lengths')
    rows = [{i: Fraction(1)} for i in range(n)] + [{} for _ in range(m-n)]
    frames = list(word['initial']) + [None] * (m-n)
    spans = []
    for basis in word['frames']:
        span = {0}
        for v in basis:
            require(type(v) is int and 0 < v < 512 and v not in span, 'Binary basis')
            span |= {v ^ x for x in span}
        spans.append(span)
    ordinal, opened, records = Counter(), {}, []
    paid, rises, census = Counter(), Counter(), Counter()
    owned_stream, copy, coefficient = [], [], {}
    peak = 0
    for clock, event in enumerate(word['program']):
        op, r = event[:2]
        require(type(r) is int and 0 <= r < m, f'Role at {clock}')
        census[op] += 1
        if op in ('INIT', 'CLEAR') or (op == 'MOVE' and r >= n):
            owned_stream.append(event)
        if op == 'INIT':
            require(r >= n and frames[r] is None and not rows[r], f'Fresh INIT at {clock}')
            require(0 <= event[2] < len(spans), f'INIT chart at {clock}')
            ordinal[r] += 1
            opened[r] = dict(role=r, ordinal=ordinal[r], init_clock=clock,
                             init_frame=event[2], writes=[], reads=[], moves=[], read_values=[])
            frames[r] = event[2]
            peak = max(peak, len(opened))
            continue
        require(frames[r] is not None, f'Inactive target at {clock}')
        if op == 'CLEAR':
            require(r >= n and frames[r] == event[2] and r in opened, f'Owned CLEAR at {clock}')
            rec = opened.pop(r)
            rec.update(clear_clock=clock, clear_frame=event[2], row=dict(rows[r]),
                       coframed_at_CLEAR=[j for j,f in enumerate(frames) if f==event[2]])
            records.append(rec)
            rows[r], frames[r] = {}, None
            continue
        if op == 'MOVE':
            a, b, owned = event[2:]
            require(frames[r] == a and owned == (r >= n), f'MOVE source/owner at {clock}')
            require(spans[a] < spans[b] or (owned and spans[b] < spans[a]), f'MOVE inclusion at {clock}')
            rank = abs(len(word['frames'][b])-len(word['frames'][a]))
            paid[rank] += 1
            if r >= n:
                opened[r]['moves'].append([clock, event])
                if spans[a] < spans[b]:
                    rises[rank] += 1
            frames[r] = b
            continue
        require(op in ('SCALE', 'ADD', 'COPY') and frames[r] == event[-1], f'Scalar chart at {clock}')
        text = event[2] if op == 'SCALE' else event[3]
        if text not in coefficient:
            q = Fraction(text)
            require(abs(q.numerator).bit_length() <= 24 and q.denominator.bit_length() <= 20,
                    f'Coefficient format at {clock}')
            coefficient[text] = q
        q = coefficient[text]
        if op == 'SCALE':
            rows[r] = {k:q*v for k,v in rows[r].items() if q*v}
        else:
            s = event[2]
            require(type(s) is int and 0 <= s < m and r != s and frames[s] == event[-1],
                    f'Source chart at {clock}')
            if op == 'COPY':
                require(not rows[r], f'Dirty COPY at {clock}')
                copy.append(clock)
            if s >= n:
                opened[s]['reads'].append([clock, event])
            if s == 1557:
                opened[s]['read_values'].append(dict(clock=clock,event=event,source=dict(rows[s]),target_before=dict(rows[r])))
            plus(rows[r], rows[s], q)
            if s == 1557:
                opened[s]['read_values'][-1]['target_after']=dict(rows[r])
        if r >= n:
            opened[r]['writes'].append([clock, event])
    require(not opened and frames == word['final'] + [None] * (m-n), 'Final frames/retirement')
    require(rows[:n] == targets(word), 'Complete arbitrary-public-input endpoint')
    require(all(not row for row in rows[n:]), 'Retired rows')
    return dict(records=records, paid=paid, rises=rises, census=census,
                owned_stream=owned_stream, copy=copy, peak=peak,
                endpoint_sha256=sha256(canonical([encoded(row) for row in rows[:n]])).hexdigest())


def paired(old, new, allowed):
    """Require the complete lifetime stream and exactly the declared row deltas."""
    before, after = trace(old), trace(new)
    require(before['owned_stream'] == after['owned_stream'], 'Ordered owned lifecycle/MOVE stream')
    a = {(r['role'],r['ordinal']): r for r in before['records']}
    b = {(r['role'],r['ordinal']): r for r in after['records']}
    require(a.keys() == b.keys(), 'Every lifetime paired')
    changes, operands = [], []
    for key in sorted(a):
        x,y = a[key],b[key]
        for field in ('init_frame','clear_frame'):
            require(x[field] == y[field], f'Paired {field}')
        for field in ('writes','reads','moves'):
            require([e for _,e in x[field]] == [e for _,e in y[field]], f'Paired owned {field}')
        operands.append(dict(role=key[0],ordinal=key[1],before_clock=x['clear_clock'],after_clock=y['clear_clock'],
                             frame=y['clear_frame'],before_terms=len(x['row']),after_terms=len(y['row']),
                             before_sha256=sha256(canonical(encoded(x['row']))).hexdigest(),
                             after_sha256=sha256(canonical(encoded(y['row']))).hexdigest()))
        delta = dict(y['row']); plus(delta,x['row'],Fraction(-1))
        require(delta == allowed.get(key, {}), f'Unexpected pre-CLEAR delta at {key}')
        if delta:
            observations=[]
            for v,w in zip(x['read_values'],y['read_values'],strict=True):
                require(v['event']==w['event'],'Same owned1557 observer')
                def difference(field):
                    d=dict(w[field]);plus(d,v[field],Fraction(-1));return d
                source_delta=difference('source')
                require(source_delta==delta,'Actual owned1557 row delta at each observer')
                pre,post=difference('target_before'),difference('target_after')
                effect=dict(post);plus(effect,pre,Fraction(-1))
                require(effect=={k:Fraction(w['event'][3])*q for k,q in delta.items()},'Actual observer contribution')
                observations.append(dict(before_clock=v['clock'],after_clock=w['clock'],event=w['event'],
                                         source_delta=encoded(source_delta),target_before_delta=encoded(pre),target_after_delta=encoded(post)))
            changes.append(dict(role=key[0],ordinal=key[1],delta=encoded(delta),
                                before_clock=x['clear_clock'],after_clock=y['clear_clock'],
                                frame=y['clear_frame'],before_row=encoded(x['row']),
                                after_row=encoded(y['row']),reads=y['reads'],writes=y['writes'],
                                coframed_at_CLEAR=y['coframed_at_CLEAR'],observations=observations))
    require(set(allowed) == {(r['role'],r['ordinal']) for r in changes}, 'All expected deltas present')
    require(before['endpoint_sha256'] == after['endpoint_sha256'], 'Same full endpoint')
    return dict(lifetimes=len(a),unchanged_pre_CLEAR_rows=len(a)-len(changes),changes=changes,
                erasure_operands=operands,before_nonzero_erasure_rows=sum(bool(x['row']) for x in a.values()),
                after_nonzero_erasure_rows=sum(bool(x['row']) for x in b.values()),
                before_peak=before['peak'],after_peak=after['peak'],
                public_input_columns=old['public'],public_output_rows=new['public'],
                owned_stream_sha256=sha256(canonical(after['owned_stream'])).hexdigest(),
                endpoint_sha256=after['endpoint_sha256'],before_COPY=before['copy'],after_COPY=after['copy'],
                paid_before=dict(sorted(before['paid'].items())),paid_after=dict(sorted(after['paid'].items())),
                owned_rises=dict(sorted(after['rises'].items())),opcodes=dict(after['census']))


def controls():
    # Erasure conceals a changed scratch value from the terminal public map.
    w=dict(public=2,owned_fields=1,frames=[[]],initial=[0,0],final=[0,0],
           live=[],hosted=dict(Dports=[],X2=[],Y2=[]),
           program=[['INIT',2,0],['ADD',2,0,'1',0],['CLEAR',2,0]])
    import copy
    v=copy.deepcopy(w)
    v['program'].insert(1,['SCALE',0,'2',0])
    v['program'].insert(3,['SCALE',0,'1/2',0])
    ok=paired(w,v,{(2,1):{0:Fraction(1)}})
    require(ok['changes'][0]['delta']==[[0,'1']], 'Toy hidden delta observed')
    rejected={}
    for tag, fn in (
        ('equal_erasure_operand_required',lambda:paired(w,v,{})),
        ('wrong_erasure_delta',lambda:paired(w,v,{(2,1):{1:Fraction(1)}})),
    ):
        try:fn()
        except ValueError as exc:rejected[tag]=str(exc)
        else:raise ValueError('Boundary control survived: '+tag)
    dirty=copy.deepcopy(w);dirty['program'].insert(1,['COPY',0,1,'1',0])
    try:trace(dirty)
    except ValueError as exc:
        require(str(exc).startswith('Dirty COPY'), 'Wrong COPY control failure')
        rejected['dirty_COPY']=str(exc)
    else:raise ValueError('Dirty COPY survived')
    return dict(hidden_erasure_delta_positive=True,rejections=rejected)
