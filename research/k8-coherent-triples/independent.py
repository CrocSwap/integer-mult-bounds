"""Direct cut/literal oracle; no call to new curves, census, f or transform.

Reuses and credits PR1263's separate source reader and literal interpreter,
plus Sagar Thakrar's PR696 lowerer. New exact complete graph/cut enumeration.
Philipp / GPT-6 Astra; Apache-2.0. Both implementations AI-assisted.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations
import hashlib
import importlib.util
import json
from pathlib import Path
import random

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def direct_census(events,helpers,gauges,lower):
    H=set(helpers);edges=[];touch={h:set() for h in helpers};adj={h:set() for h in helpers}
    for event in events:
        if event[0]!='scalar' or event[1][0]!='add':continue
        g=event[1];t,s=(r[1] if r[0]=='L' and r[1] in H else None for r in g[1:3])
        if t is None and s is None:continue
        q=F(g[3],g[4])*F(2)**(gauges.get(t,0)-gauges.get(s,0))
        idx=len(edges);edges.append((q,t,s))
        for h in (t,s):
            if h in H:touch[h].add(idx)
        if t in H and s in H:adj[t].add(s);adj[s].add(t)
    # Independent valuation, and a dense integer interval strictly enclosing
    # every boundary-scale kink and every possible crossing-edge kink.
    def val(q):
        q=abs(q);e=0
        while q.denominator>1:q*=2;e-=1
        while q.numerator%2==0:q/=2;e+=1
        return e
    R=1+max([abs(k) for k in gauges.values()]+[abs(val(q)) for q,_,_ in edges])
    grid=tuple(range(-R,R+1));zero=grid.index(0)
    @lru_cache(None)
    def literal(q):return len(lower.lower(['add',['L',0],['L',1],q.numerator,q.denominator]))
    @lru_cache(None)
    def changes(q,sign):
        before=literal(q)
        return [literal(q*F(2)**(sign*d))-before for d in grid]
    boundary={h:[len(lower.lower(['scale',['L',0],(F(2)**(gauges.get(h,0)+d)).numerator,(F(2)**(gauges.get(h,0)+d)).denominator]))*2-2*abs(gauges.get(h,0)) for d in grid] for h in helpers}
    evaluations=0
    def minimum(subset):
        nonlocal evaluations
        chosen=set(subset);cut=Counter()
        for i in set().union(*(touch[h] for h in subset)):
            q,t,s=edges[i];sign=int(t in chosen)-int(s in chosen)
            if sign:cut[q,sign]+=1
        values=[sum(boundary[h][i] for h in subset) for i in range(len(grid))]
        for (q,sign),count in cut.items():
            row=changes(q,sign)
            for i in range(len(grid)):values[i]+=count*row[i]
        need(values[zero]==0,'zero shift')
        need(values[0]>values[1] and values[-1]>values[-2],'strict outward tails')
        evaluations+=len(grid)
        return min(values)
    singles=[[h,minimum((h,))] for h in helpers]
    pairs=[[a,b,minimum((a,b))] for a,b in combinations(helpers,2)]
    digest=hashlib.sha256();connected=0;disconnected=0;wins=[]
    # Different coverage implementation: visit all binomial(237,3) labeled
    # triples, rather than generate and deduplicate length-two wedges.
    for a,b,c in combinations(helpers,3):
        if sum((b in adj[a],c in adj[a],c in adj[b]))<2:
            disconnected+=1;continue
        connected+=1;best=minimum((a,b,c))
        digest.update(canonical([a,b,c,best])+b'\n')
        if best<0:wins.append([a,b,c,best])
    return {'radius':R,'integer_evaluations':evaluations,'single_minima':singles,
        'pair_minima_sha256':hashlib.sha256(canonical(pairs)).hexdigest(),
        'triple_minima_sha256':digest.hexdigest(),'connected_triples':connected,
        'disconnected_triples':disconnected,'wins':wins}

def run():
    independent=load('credited_pr1263_independent',HERE/'vendor/pr1310/vendor/pr1263/independent.py');independent.ROOT=ROOT
    word,programs=independent.source();lower=load('credited_pr696_lowerer',ROOT/'research/complex-dyadic-lowering/lower.py')
    prior=json.loads((HERE/'vendor/pr1310/CERTIFICATE.json').read_bytes());receipt=json.loads((HERE/'CERTIFICATE.json').read_bytes())
    H=set(range(224,704))-set(word['centers'])
    for stream in programs.values():
        for event in stream:
            if event[0]=='residual_adapter':H.discard(event[2])
            if event[0]=='scalar' and event[1][0] in ('copy','clear'):
                for reg in event[1][1:]:
                    if isinstance(reg,list) and reg[0]=='L':H.discard(reg[1])
    helpers=sorted(h for h in H if word['start'][h]==0 and word['final'][h]==1)
    need(helpers==receipt['eligible_helpers'],'separate domain')
    results={}
    for orientation in ('forward','backward'):
        data=receipt['orientations'][orientation];events=programs[orientation];rows={}
        for label,raw,expected in [('initial',prior['orientations'][orientation]['gauges'],data['trace'][0]),('final',data['gauges'],data['trace'][-1])]:
            gauges={int(h):k for h,k in raw.items()};row=direct_census(events,helpers,gauges,lower)
            for key in ['pair_minima_sha256','triple_minima_sha256','connected_triples','disconnected_triples']:
                need(row[key]==expected[key],'direct '+label+' '+key)
            need(all(value==0 for _,value in row['single_minima']),'direct single stationarity')
            rows[label]=row
        gauges={int(h):k for h,k in data['gauges'].items()};candidate=independent.reconstruct(word,events,gauges)
        need(hashlib.sha256(canonical(candidate)).hexdigest()==data['candidate_sha256'],'separate reconstruction')
        ops=[op for e in candidate if e[0]=='scalar' for op in lower.lower(e[1])]
        need(len(ops)==data['candidate']['real_primitives'],'literal complete cost')
        registers=[('L',i) for i in range(704)]+[('C',i) for i in range(8)]+[('W',0)]
        rng=random.Random(37)
        for case in range(3):
            initial={r:F(rng.randrange(-10000,10001),2**rng.randrange(5)) for r in registers}
            if case==1:initial.update({('L',i):F((-1)**i*(i+1)**3,8) for i in range(224,704)})
            if case==2:initial.update({('L',i):F(0) for i in range(224)})
            expected=dict(initial)
            for i in range(112):
                if orientation=='forward':expected['L',112+i]+=initial['L',i]
                else:expected['L',i]-=initial['L',112+i]
            expected.update({('C',i):F(0) for i in range(8)});expected['W',0]=F(0)
            need(independent.execute(ops,initial)[0]==expected,'literal dirty endpoint')
        _,peak=independent.execute(ops,{r:F(1) for r in registers},positive=True)
        need(str(peak)==data['candidate']['prefix_l1'],'literal positive envelope')
        rows['literal']={'real_primitives':len(ops),'dirty_cases':3,'prefix_l1':str(peak),
            'denominator_depth':independent.denominator_depth(ops,registers)}
        results[orientation]=rows
    return {'status':'PASS_INDEPENDENT_COHERENT_TRIPLES','orientations':results}

if __name__=='__main__':
    import sys
    result=run();path=HERE/'INDEPENDENT.json'
    if '--write' in sys.argv:
        need(not path.exists(),'refusing overwrite');path.write_bytes(canonical(result)+b'\n')
    else:need(canonical(result)==canonical(json.loads(path.read_bytes())),'independent receipt equality')
    print(result['status'])
