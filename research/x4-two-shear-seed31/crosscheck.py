#!/usr/bin/env python3
"""Independent Fraction/primitive census and exact linear replay.

Written for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
Imports no producer or predecessor implementation; this is not human review.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


@lru_cache(None)
def lowering(q):
    # Independent direct emission of the original emitter's real primitives.
    # Registers: source=0, target=1, work=2.
    if q == 0:
        return ()
    word = [('clear',2), ('add',2,0,1)]
    for digit in bin(abs(q.numerator))[3:]:
        word.append(('add',2,2,1))
        if digit == '1':
            word.append(('add',2,0,1))
    d = q.denominator
    while d > 1:
        need(d % 2 == 0, 'non-dyadic coefficient')
        word.append(('half',2))
        d //= 2
    word.extend([('add',1,2,1 if q>0 else -1), ('clear',2)])
    return tuple(word)


def source():
    with tarfile.open(ROOT/'research/community-frontier799-audit/integrated799-replay.tar.gz','r:gz') as archive:
        raw = gzip.decompress(archive.extractfile('native/local/CANONICAL-WORD.json.gz').read())
    need(hashlib.sha256(raw).hexdigest() == '1c0e9da767d4418f70016af599e4a447a3f7777acabe930318459c0fbbd260aa', 'source payload')
    rows = {i:{} for i in range(112,224)}
    for kind,t,s,n,d,f in json.loads(raw)['compensation']:
        need(kind == 'add' and f == 0 and t in rows and 224<=s<728, 'panel operations')
        need(s not in rows[t], 'duplicate target/helper entry')
        rows[t][s] = Q(n,d)
    return rows


def census(rows):
    values = [Q(n,2) for n in (-4,-2,-1,1,2,4)]
    alphabet = [Q(n,4) for n in range(-4,5)]
    # Work from elementary matrices: S21(b) S12(a), then exchange labels
    # to obtain the second chronological orientation.
    prices = {}
    for direction,a,b in itertools.product(range(2),values,values):
        matrix = ((1,a),(b,1+a*b)) if direction == 0 else ((1+a*b,b),(a,1))
        for x,y in itertools.product(alphabet,repeat=2):
            prices[direction,a,b,x,y] = sum(len(lowering(row[0]*x+row[1]*y)) for row in matrix)
    histogram = Counter()
    floors = []
    improving = profitable = count = 0
    for i,j in itertools.combinations(rows,2):
        groups = Counter((rows[i].get(s,Q(0)),rows[j].get(s,Q(0))) for s in rows[i].keys()|rows[j].keys())
        original = sum(n*(len(lowering(x))+len(lowering(y))) for (x,y),n in groups.items())
        singles = [original]
        for d,a in itertools.product(range(2),values):
            singles.append(2*len(lowering(a))+sum(n*(len(lowering(x+a*y))+len(lowering(y))) if d==0
                else n*(len(lowering(x))+len(lowering(y+a*x))) for (x,y),n in groups.items()))
        single = min(singles)
        doubles = []
        for d,a,b in itertools.product(range(2),values,values):
            cost = 2*(len(lowering(a))+len(lowering(b))) + sum(n*prices[d,a,b,x,y] for (x,y),n in groups.items())
            doubles.append(cost)
            histogram[str(single-cost)] += 1
            count += 1
            improving += cost < single
            profitable += cost < original
        floors.append([[i,j],single,min(doubles)])
    return {'candidates':count, 'better_than_best_single':improving,
            'profitable_over_identity':profitable, 'saving_histogram':dict(histogram),
            'cost_floor_sha256':hashlib.sha256(encoded(floors)).hexdigest()}


def emit(macros, width):
    result = []
    for dst,src,q in macros:
        mapping = (src,dst,width)
        for op in lowering(q):
            result.append((op[0],mapping[op[1]]) if len(op)==2 else
                          (op[0],mapping[op[1]],mapping[op[2]],op[3]))
    return result


def replay(word, width):
    # Sparse exact rows simultaneously cover every independent data/helper/work input.
    rows = [{i:Q(1)} for i in range(width+1)]
    peak = Q(1)
    majorants = [Q(1)]*(width+1)
    majorant_peak = Q(1)
    for op in word:
        d=op[1]
        if op[0]=='clear':
            rows[d]={}
            majorants[d]=Q(0)
        elif op[0]=='half':
            rows[d]={k:v/2 for k,v in rows[d].items()}
            majorants[d]/=2
        else:
            updated=rows[d].copy()
            for k,v in rows[op[2]].items():
                updated[k]=updated.get(k,Q(0))+op[3]*v
            rows[d]={k:v for k,v in updated.items() if v}
            majorants[d]+=abs(op[3])*majorants[op[2]]
        peak=max(peak,sum(abs(v) for v in rows[d].values()))
        majorant_peak=max(majorant_peak,majorants[d])
    return rows,(peak,majorant_peak)


def matrix_replay(rows):
    targets=(121,173)
    helpers=sorted(set().union(*(r.keys() for r in rows.values())))
    indices={s:k+2 for k,s in enumerate(helpers)}
    width=2+len(helpers)
    a,b=Q(-1),Q(1,2)
    left,right=(rows[t] for t in targets)
    base=[(d,indices[s],q) for d,row in enumerate((left,right)) for s,q in sorted(row.items())]
    transformed=({s:left.get(s,Q(0))+a*right.get(s,Q(0)) for s in helpers},
        {s:b*left.get(s,Q(0))+(1+a*b)*right.get(s,Q(0)) for s in helpers})
    candidate=[(0,1,a),(1,0,b)] + [(d,indices[s],q) for d,row in enumerate(transformed) for s,q in sorted(row.items()) if q]
    candidate += [(1,0,-b),(0,1,-a)]
    costs={}
    peaks={}
    for name,baseword,newword in [('forward',base,candidate),
            ('inverse_transpose',[(s,t,-q) for t,s,q in base],[(s,t,-q) for t,s,q in candidate])]:
        old,old_peak=replay(emit(baseword,width),width)
        new,new_peak=replay(emit(newword,width),width)
        need(new==old and new[-1]=={}, 'arbitrary-input local map or dirty work failed')
        costs[name]={'old':len(emit(baseword,width)),'candidate':len(emit(newword,width))}
        peaks[name]={'old_exact':str(old_peak[0]),'candidate_exact':str(new_peak[0]),
                     'old_cancellation_free':str(old_peak[1]),'candidate_cancellation_free':str(new_peak[1])}
    need(costs['forward']=={'old':648,'candidate':356}, 'candidate full primitive invoice')
    mutations={
        'omit preparation':candidate[1:],
        'omit restoration':candidate[:-1],
        'wrong restore order':candidate[:-2]+list(reversed(candidate[-2:])),
        'wrong half sign':[(t,s,-q if k==1 else q) for k,(t,s,q) in enumerate(candidate)],
        'wrong transformed row':candidate[:2]+base+candidate[-2:],
        'omit panel read':candidate[:3]+candidate[4:],
    }
    expected,_=replay(emit(base,width),width)
    for label,mutant in mutations.items():
        need(replay(emit(mutant,width),width)[0]!=expected,'vacuous control: '+label)
    cleanword=emit(candidate,width)
    need(replay(cleanword[:-1],width)[0]!=expected,'final work-clear control')
    wrongdual=list(reversed([(s,t,-q) for t,s,q in candidate]))
    dualexpected,_=replay(emit([(s,t,-q) for t,s,q in base],width),width)
    need(replay(emit(wrongdual,width),width)[0]!=dualexpected,'dual chronology control')
    return {'targets':list(targets),'columns_including_dirty_work':width+1,'costs_per_component':costs,
            'local_prefix_row_l1':peaks,'controls_rejected':list(mutations)+['final work clear','dual chronology']}


def main():
    expected=json.loads((HERE/'EXPECTED.json').read_text())
    rows=source()
    actual=census(rows)
    for key,value in actual.items():
        need(encoded(value)==encoded(expected[key]),'independent census mismatch: '+key)
    result=matrix_replay(rows)
    path=HERE/'MATRIX-REPLAY.json'
    import sys
    if '--write' in sys.argv:
        with path.open('x') as stream:
            json.dump(result,stream,sort_keys=True,indent=2)
            stream.write('\n')
    else:
        need(encoded(result)==encoded(json.loads(path.read_text())),'matrix receipt mismatch')
    print('PASS_X4_TWO_SHEAR_INDEPENDENT candidates=447552 columns=219 controls=8 no_new_kappa')


if __name__=='__main__':
    main()
