"""Literal-lowerer pair-grid and complete-word checks; Apache-2.0.

Philipp / GPT-6 Astra. Does not call the arrangement census or its f objective.
Reuses explicitly credited PR1263 primitive utilities and PR696 literal lowerer.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations
import json
import random
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('coupled_verify',Path(__file__).with_name('verify.py'))
v=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(v)


def check():
    v.sources()  # Authenticate all reused bytes before importing.
    utils=v.load_module('credited_pr1263_primitives',v.HERE/'vendor/pr1263/independent.py')
    utils.ROOT=v.ROOT
    word,programs=utils.source()
    lower=v.load_module('credited_pr696_lower',v.ROOT/'research/complex-dyadic-lowering/lower.py')
    cert=json.loads((v.HERE/'CERTIFICATE.json').read_bytes())
    allowed=set(range(224,704))-set(word['centers'])
    for stream in programs.values():
        for event in stream:
            if event[0]=='residual_adapter':allowed.discard(event[2])
            if event[0]=='scalar' and event[1][0] in ('copy','clear'):
                for register in event[1][1:]:
                    if isinstance(register,list) and register[0]=='L':allowed.discard(register[1])
    helpers=sorted(h for h in allowed if word['start'][h]==0 and word['final'][h]==1)
    v.need(helpers==cert['eligible_helpers'] and len(helpers)==237,'independent eligibility contract')
    result={}
    @lru_cache(None)
    def price(n,d,k):
        q=F(n,d)*F(2)**k
        return len(lower.lower(['add',['L',0],['L',1],q.numerator,q.denominator]))
    for orientation in ('forward','backward'):
        row=cert['orientations'][orientation]
        gauges={int(h):k for h,k in row['gauges'].items()}
        candidate=utils.reconstruct(word,programs[orientation],gauges)
        v.need(v.sha(v.canonical(candidate))==row['candidate_sha256'],'separate ratio reconstruction')
        ops=[op for e in candidate if e[0]=='scalar' for op in lower.lower(e[1])]
        v.need(len(ops)==row['candidate']['real_primitives'],'literal price')
        registers=[('L',i) for i in range(704)]+[('C',i) for i in range(8)]+[('W',0)]
        rng=random.Random(35)
        for case in range(3):
            initial={r:F(rng.randrange(-10000,10001),2**rng.randrange(6)) for r in registers}
            if case==1:initial.update({('L',i):F(0) for i in range(224)})
            expected=initial.copy()
            for i in range(112):
                if orientation=='forward':expected['L',112+i]+=initial['L',i]
                else:expected['L',i]-=initial['L',112+i]
            expected.update({('C',i):F(0) for i in range(8)});expected['W',0]=F(0)
            final,_=utils.execute(ops,initial)
            v.need(final==expected,'literal primitive dirty-state endpoint')
        _,peak=utils.execute(ops,{r:F(1) for r in registers},positive=True)
        v.need(str(peak)==row['candidate']['prefix_l1'],'complete positive envelope')
        depth=utils.denominator_depth(ops,registers)
        # Enumerate complete integer rectangles containing every arrangement
        # vertex. The written face-descent proof extends these exact minima to Z^2.
        terms=Counter()
        for e in programs[orientation]:
            if e[0]!='scalar' or e[1][0]!='add':continue
            g=e[1];t=g[1][1] if g[1][0]=='L' and g[1][1] in helpers else -1
            s=g[2][1] if g[2][0]=='L' and g[2][1] in helpers else -1
            if t!=-1 or s!=-1:terms[g[3],g[4],t,s]+=1
        incident={h:[] for h in helpers};shared={}
        for (n,d,t,s),count in terms.items():
            shift=gauges.get(t,0)-gauges.get(s,0)
            for h,sign in ((t,1),(s,-1)):
                if h!=-1:incident[h].append((n,d,shift,sign,count))
            if t!=-1 and s!=-1:
                a,b=sorted((t,s));shared.setdefault((a,b),[]).append((n,d,shift,1 if t==a else -1,count))
        radius=max(abs(k) for k in gauges.values())+2*max(abs(utils.valuation(F(n,d))+shift) for items in incident.values() for n,d,shift,_,_ in items)+1
        values=range(-radius,radius+1)
        singles={h:{x:2*(abs(gauges.get(h,0)+x)-abs(gauges.get(h,0)))+
                 sum(c*(price(n,d,k+sign*x)-price(n,d,k)) for n,d,k,sign,c in terms_h)
                    for x in values} for h,terms_h in incident.items()}
        minima={};evaluations=0
        for a,b in combinations(helpers,2):
            edges=shared.get((a,b),[])
            if not edges:
                minimum=min(singles[a].values())+min(singles[b].values())
                evaluations+=2*len(values)
            else:
                # Shared corrections remove the twice charged individual terms.
                tables=[]
                for n,d,k,sign,count in edges:
                    both={delta:count*price(n,d,k+sign*delta) for delta in range(-2*radius,2*radius+1)}
                    ax={x:count*price(n,d,k+sign*x) for x in values}
                    by={y:count*price(n,d,k-sign*y) for y in values}
                    tables.append((both,ax,by,count*price(n,d,k)))
                minimum=min(singles[a][x]+singles[b][y]+sum(both[x-y]-ax[x]-by[y]+base for both,ax,by,base in tables)
                            for x in values for y in values)
                evaluations+=len(values)**2
            minima[a,b]=minimum
        encoded=[[a,b,m] for (a,b),m in sorted(minima.items())]
        v.need(v.sha(v.canonical(encoded))==row['trace'][-1]['pair_minima_sha256'] and len(minima)==27966 and set(minima.values())=={0},'all-pair literal grid minima')
        result[orientation]={'radius':radius,'integer_assignments':evaluations,'pairs':len(minima),'interacting_pairs':len(shared),
                            'literal_real_primitives':len(ops),'dirty_fixtures':3,'positive_prefix_bits':peak.numerator.bit_length()-peak.denominator.bit_length()+1,
                            'denominator_depth':depth}
    return {'status':'PASS_INDEPENDENT_LITERAL_PAIR_GRID','orientations':result}

if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
