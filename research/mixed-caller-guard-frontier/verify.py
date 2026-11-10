"""Check the complete guard frontier, exact source envelope and tariff regimes.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
from itertools import product
from pathlib import Path
from random import Random
import json
import runpy
import sys

P=Path(__file__).resolve().parent
G=runpy.run_path(str(P/'guards.py'));need=G['need']
CLASSES=('scalar','local','query','idle')


def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x


def authenticate(raw,pin):
    need(sha256(raw).hexdigest()==pin['sha256'],'Frozen SHA256')
    need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'Frozen Git blob')


def reject(f):
    try:f()
    except ValueError:return
    raise ValueError('Invalid case accepted')


def integer_oracle(a,cap,eliminate=None):
    # Use a common integer grid, in a different coordinate order from frontier().
    d=max(x.denominator.bit_length()-1 for x in a);unit=1<<(cap+d)
    terms=[[x.numerator*((1<<d)//x.denominator)*(1<<(cap-g)) for g in range(cap+1)] for x in a]
    m=len(a);out=[];inspected=0;boundary=None
    if eliminate is None:
        candidates=product(range(cap+1),repeat=m)
    else:
        indices=[i for i in range(m) if i!=eliminate]
        def generate():
            for rest in product(range(cap+1),repeat=m-1):
                partial=sum(terms[i][g] for i,g in zip(indices,rest))
                if partial>=unit:continue
                last=next((g for g in range(cap+1) if partial+terms[eliminate][g]<unit),None)
                if last is not None:
                    v=[0]*m;v[eliminate]=last
                    for i,g in zip(indices,rest):v[i]=g
                    yield tuple(v)
        candidates=generate()
    for g in candidates:
        s=sum(terms[i][x] for i,x in enumerate(g));inspected+=1
        if s==unit:boundary=g
        if s<unit and all(x==0 or s+terms[i][x]>=unit for i,x in enumerate(g)):
            out.append(g)
    return sorted(out),inspected,boundary


def meter(events):
    fields={k:Q(0) for k in CLASSES};sites={k:0 for k in CLASSES};opcodes=Counter()
    for e in events:
        opcodes[e[0]]+=1
        if e[0] in ('ADD','SCALE'):
            fields['scalar']+=1;sites['scalar']+=1
        elif e[0]=='LAMBDA':
            fields['scalar']+=4*Q(1,2);sites['scalar']+=4
        elif e[0]=='LOCAL':
            fields['local']+=2;sites['local']+=2
        elif e[0]=='QUERY':
            fields['query']+=1;sites['query']+=1
        elif e[0] in ('IDLE','IDLE_ONE'):
            r=2 if e[0]=='IDLE' else 1;fields['idle']+=r;sites['idle']+=r
        else:need(e[0] in ('SWAP','Q_POWER'),'Complete caller opcode')
    return dict(opcodes=opcodes,error_sites=sites,field_equivalents=fields)


def run():
    pins=json.loads((P/'SOURCES.json').read_text())['retained_predecessors']
    for pin in pins:
        raw=(P/pin['local']).read_bytes();authenticate(raw,pin)
        reject(lambda raw=raw,pin=pin:authenticate(bytes([raw[0]^1])+raw[1:],pin))
    B=runpy.run_path(str(P/'inputs/pr6473/bounds.py'))
    computed=B['calculate']();source=json.loads((P/'inputs/pr6473/RESULT.json').read_text())
    need(all(computed[k]==source[k] for k in computed),'Exact source envelope regeneration')
    a=tuple(Q(computed['errors'][k][0]) for k in CLASSES)
    need(a==(Q(795,2),Q(28),Q(18),Q(28)),'Exact four-class coefficients')
    need(all(Q(x)<=a[j] for j,k in enumerate(CLASSES) for x in computed['errors'][k]),'One row dominates all four classes')
    cap,front=G['frontier'](a);oracle,inspected,_=integer_oracle(a,cap,eliminate=0)
    need(cap==39 and len(front)==61 and front==oracle,'Complete frontier by two methods')
    need(max(max(g) for g in front)==16,'Actual largest minimal exponent')
    neighbors=0
    for g in front:
        need(G['value'](a,g)<1,'Strict source feasibility')
        for i in range(4):
            bad=list(g);bad[i]-=1
            need(G['value'](a,bad)>=1,'Every precision decrease fails the envelope');neighbors+=1
        for row in range(34):
            need(sum(Q(computed['errors'][k][row])*Q(2)**(-g[i]) for i,k in enumerate(CLASSES))<1,'Every caller output bound')
    micro=[]
    for m in (1,2,3):
        for coefficients in product((Q(1,4),Q(1,2),Q(1),Q(2)),repeat=m):
            bound,got=G['frontier'](coefficients);want,cases,boundary=integer_oracle(coefficients,bound+2)
            need(got==want,'Independent micro enumeration beyond the proved cap')
            micro.append(dict(coefficients=coefficients,bound=bound,points=len(got),cases=cases))
    word=json.loads((P/'inputs/pr6473/inputs/CONTROLLER.json').read_text());counts=meter(word['events'])
    need(len(word['events'])==570 and word['roles']==34 and word['stages']==18,'Exact caller binding')
    weights=tuple(int(counts['field_equivalents'][k]) for k in CLASSES)
    need(weights==(397,36,17,30) and tuple(counts['error_sites'][k] for k in CLASSES)==(437,36,17,30),'All half-field normalizer and native error sites')
    # Independent count from opcode totals, without the event meter's accumulation.
    op=Counter(e[0] for e in word['events'])
    need(weights==(op['ADD']+op['SCALE']+2*op['LAMBDA'],2*op['LOCAL'],op['QUERY'],2*op['IDLE']+op['IDLE_ONE']),'Separate opcode tariff count')
    regions,ends=G['tariff_intervals'](front,weights)
    need([r['guards'] for r in regions]==[((9,8,9,9),),((10,7,7,7),),((11,6,7,7),),((13,6,6,7),)],'Exact tariff policies')
    need([r['hi'] for r in regions]==[Q(397,130),Q(397,36),Q(794,17),None],'Exact rational breakpoints')
    samples=set(Q(i,7) for i in range(1,151))|{Q(1),Q(10),Q(100),Q(1000)}
    for r in regions:
        if r['hi'] is not None:samples.update((r['hi'],r['hi']-Q(1,100000),r['hi']+Q(1,100000)))
    sample_results=[]
    for t in sorted(samples):
        cost=lambda g:weights[0]*g[0]+t*sum(w*x for w,x in zip(weights[1:],g[1:]))
        best=min(map(cost,oracle));winners=tuple(g for g in oracle if cost(g)==best)
        if str(t) in ends:need(winners==ends[str(t)],'Every threshold tie')
        else:
            r=next(r for r in regions if r['lo']<t and (r['hi'] is None or t<r['hi']))
            need(winners==r['guards'],'Independent tariff winner')
        if t in (1,10,100,1000):sample_results.append(dict(relative_native_price=t,guards=winners,cost=best,uniform_cost=cost((9,9,9,9)),envelope=G['value'](a,winners[0])))
    random=Random(416473);arbitrary=0
    for _ in range(128):
        w=tuple(random.randrange(1,10001) for i in range(4))
        need(min(sum(x*y for x,y in zip(w,g)) for g in front)==min(sum(x*y for x,y in zip(w,g)) for g in oracle),'Arbitrary positive tariff');arbitrary+=1
    need(G['value'](a,(9,8,8,9))>=1,'Two cheap native reductions can fail')
    need(G['value'](a,(9,8,9,9))<1,'One cheaper native class passes')
    need(any(max(g)>15 for g in front),'An arbitrary fifteen-bit cap misses valid minimal policies')
    need(sum(Q(computed['errors'][k][0]) for k in CLASSES)==Q(943,2),'Inherited uniform envelope')
    for bad in [(),(Q(0),),(Q(-1),),(Q(1,3),)]:reject(lambda bad=bad:G['frontier'](bad))
    reject(lambda:G['value'](a,(9,8,9,-1)))
    reject(lambda:G['value'](a,(9,8,9)))
    reject(lambda:G['tariff_intervals'](front,(0,36,17,30)))
    # A common error budget bounds the intermediate caller, independent of allocation.
    need(Q(18)*Q(943,2)==8487,'Retained prefix propagation constant')
    return dict(status='PASS_COMPLETE_MIXED_GUARD_FRONTIER',classes=CLASSES,coefficients=a,
                source_head='15a7e8d2e90f23977393613e6d0889614b144ad7',proved_cap=cap,frontier=front,
                neighbor_failures=neighbors,integer_oracle_candidates=inspected,micro_domains=micro,
                micro_guard_tuples=sum(x['cases'] for x in micro),meter=counts,tariff_regions=regions,
                threshold_ties=ends,tariff_samples=len(samples),sample_results=sample_results,
                arbitrary_positive_tariffs=arbitrary,invalid_controls=7,source_corruptions=len(pins),
                uniform_digit_volume=4320,best_unit_digit_volume=4284,
                minimum_native_slope=528,uniform_native_slope=747,asymptotic_model_saving=Q(73,249),
                prefix_bound='18*M+18*2^-p',normalizer_internal_bound='Pair-compatible only: 36*M+36*2^-p+8*2^(-p-g_scalar)',
                scope='Complete optimum for the inherited sufficient envelope and declared digit-volume tariffs; not a physical or true-error optimum, and no kappa claim.')


if __name__=='__main__':
    result=encode(run())
    if '--write-result' in sys.argv:(P/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(result==json.loads((P/'RESULT.json').read_text()),'Exact result receipt')
    print(json.dumps({k:result[k] for k in ('status','proved_cap','neighbor_failures','micro_guard_tuples','tariff_regions','sample_results')},sort_keys=True))
