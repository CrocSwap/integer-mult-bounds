#!/usr/bin/env python3
"""Exact cumulative destination-history filter for49 source-span MOVEs.
Historical values across different cuts are only an exclusion relaxation.
"""
from collections import Counter,defaultdict
from fractions import Fraction as F
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,sys,time
ROOT=Path(__file__).resolve().parent;HERE=ROOT
WORD=ROOT/'inputs/WORD.json.gz'
sys.dont_write_bytecode=True
sp=importlib.util.spec_from_file_location('K',ROOT/'kernel_screen.py')
K=importlib.util.module_from_spec(sp);sp.loader.exec_module(K)
PIN=K.PIN

def need(ok,label):
    if not ok:raise ValueError(label)

def insert(basis,row,representative):
    value,rep=row.copy(),representative.copy()
    while value:
        p=max(value)
        if p not in basis:
            q=1/value[p];basis[p]=({i:v*q for i,v in value.items()},
                                  {i:v*q for i,v in rep.items()});return True
        old,mask=basis[p];q=-value[p];K.add(value,old,q);K.add(rep,mask,q)
    return False

def solve(basis,row):
    value,rep=row.copy(),{}
    while value:
        p=max(value)
        if p not in basis:return None
        old,mask=basis[p];q=value[p];K.add(value,old,-q);K.add(rep,mask,q)
    return rep

def run(source=WORD,prior=None,seconds=60,output=None):
    started=time.monotonic();deadline=started+seconds
    raw=source.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==PIN,'source pin')
    w=json.loads(gzip.decompress(raw));n=w['public'];classes=[K.span(f) for f in w['frames']]
    need(prior is not None and prior.get('source_sha256')==PIN,'complete source census input')
    candidates={z['event']:z for z in prior['records'] if z['source']['inside']}
    need(len(candidates)==49,'complete source-span candidate set')
    target_charts={classes[w['program'][i][3]] for i in candidates}
    history={f:{} for f in target_charts};generators=[]
    rows=[{i:F(1)} if i<n else {} for i in range(n+w['owned_fields'])]
    charts=w['initial']+[None]*w['owned_fields']
    def observe(event,owner,frame):
        f=classes[frame]
        if f not in history or not rows[owner]:return
        index=len(generators)
        record=dict(event=event,owner=owner,frame=frame,row={str(i):str(v) for i,v in rows[owner].items()})
        if insert(history[f],rows[owner],{index:F(1)}):generators.append(record)
    for a,f in enumerate(w['initial']):observe(-1,a,f)
    records=[];complete=False;last=-1
    try:
        for event,e in enumerate(w['program']):
            last=event
            if event%128==0 and time.monotonic()>deadline:raise TimeoutError
            op,a=e[:2]
            if op=='MOVE':
                need(charts[a]==e[2],'MOVE entrance')
                if event in candidates:
                    check={}
                    for i,q in candidates[event]['source']['witness'].items():K.add(check,rows[int(i)],F(q))
                    need(check==rows[a],'independent exact source witness replay')
                    f=classes[e[3]];rep=solve(history[f],rows[a])
                    r=dict(event=event,owner=a,owned=bool(e[4]),rank=candidates[event]['rank'],
                           destination=e[3],historical_rank=len(history[f]),cumulative_span_hit=rep is not None)
                    if rep is not None:
                        r['target_row']={str(i):str(v) for i,v in rows[a].items()}
                        r['history_witness']={str(i):str(v) for i,v in rep.items()}
                    records.append(r)
                charts[a]=e[3];observe(event,a,e[3])
            elif op=='INIT':charts[a]=e[2];rows[a]={}
            elif op=='CLEAR':need(charts[a]==e[2],'CLEAR chart');charts[a]=None;rows[a]={}
            elif op=='SCALE':
                q=K.rational(e[2]);rows[a]={i:q*v for i,v in rows[a].items() if q*v}
            elif op in ('ADD','COPY'):
                need(charts[a]==charts[e[2]]==e[-1],'scalar cochart')
                if op=='COPY':need(not rows[a],'COPY zero');rows[a]={}
                K.add(rows[a],rows[e[2]],K.rational(e[3]))
            else:raise ValueError(op)
        complete=True;need(charts==w['final']+[None]*w['owned_fields'],'all endpoints')
    except TimeoutError:pass
    hits=[z for z in records if z['cumulative_span_hit']]
    result=dict(status='COMPLETE_EXACT_CUMULATIVE_HISTORY_FILTER' if complete else 'TIME_LIMIT_PARTIAL_HISTORY_FILTER',source_sha256=PIN,checked_candidates=len(records),expected_candidates=49,last_event=last,destination_classes=len(target_charts),independent_history_generators=len(generators),cumulative_hits=len(hits),hit_ranks=dict(Counter(z['rank'] for z in hits)),records=records,generators=generators,seconds=time.monotonic()-started,
                scope='Generous cumulative span of all earlier destination-chart values. No simultaneous availability or one-cache construction follows from a hit; actual earlier bank cut must be proved.')
    if output is not None:output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('records','generators')},indent=2))
    print('hits',[(z['event'],z['owner'],z['rank']) for z in hits])
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,default=WORD)
    p.add_argument('--kernel-result',type=Path,required=True)
    p.add_argument('--output',type=Path)
    p.add_argument('--seconds',type=float,default=60)
    a=p.parse_args()
    run(a.source,json.loads(a.kernel_result.read_text()),a.seconds,a.output)
