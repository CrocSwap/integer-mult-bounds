#!/usr/bin/env python3
"""Cumulative earlier-B and later-A filters for16 owned source-nonspan cuts.
No actual single-cut provider or physical two-cache word is asserted here.
"""
from collections import defaultdict,Counter
from fractions import Fraction as F
from pathlib import Path
import gzip,hashlib,importlib.util,json,sys,time
ROOT=Path(__file__).resolve().parent;HERE=ROOT
sys.dont_write_bytecode=True
sp=importlib.util.spec_from_file_location('H',ROOT/'history_filter.py')
H=importlib.util.module_from_spec(sp);sp.loader.exec_module(H);K=H.K
def need(ok,label):
    if not ok:raise ValueError(label)
def run(source=ROOT/'inputs/WORD.json.gz', prior=None, seconds=60):
    started=time.monotonic();deadline=started+seconds
    raw=source.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==K.PIN,'source pin')
    w=json.loads(gzip.decompress(raw));n=w['public'];classes=[K.span(f) for f in w['frames']]
    need(prior is not None and prior['source_sha256']==K.PIN,'complete pinned source census')
    targets={r['event']:r for r in prior['records'] if r['owned'] and not r['source']['inside']}
    need(len(targets)==16,'owned source-nonspan set')
    Bs={classes[w['program'][e][3]] for e in targets};As={classes[w['program'][e][2]] for e in targets}
    past={f:{} for f in Bs};pastgens=[];reverse=[];records={}
    rows=[{i:F(1)} if i<n else {} for i in range(n+w['owned_fields'])]
    charts=w['initial']+[None]*w['owned_fields']
    def observe(bases,gens,event,owner,frame,row,kind):
        f=classes[frame]
        if f not in bases or not row:return
        index=len(gens)
        if H.insert(bases[f],row,{index:F(1)}):gens.append(dict(event=event,owner=owner,frame=frame,kind=kind,row={str(i):str(v) for i,v in row.items()}))
    for a,f in enumerate(w['initial']):observe(past,pastgens,-1,a,f,rows[a],'entrance')
    complete=False;last=-1
    try:
        for event,e in enumerate(w['program']):
            last=event
            if event%128==0 and time.monotonic()>deadline:raise TimeoutError
            op,a=e[:2]
            if op=='MOVE':
                need(charts[a]==e[2],'MOVE chart')
                if event in targets:
                    rep=H.solve(past[classes[e[3]]],rows[a])
                    records[event]=dict(event=event,owner=a,rank=targets[event]['rank'],source=e[2],destination=e[3],
                        target_row={str(i):str(v) for i,v in rows[a].items()},earlier_B_hit=rep is not None,
                        earlier_B_rank=len(past[classes[e[3]]]),earlier_witness=None if rep is None else {str(i):str(v) for i,v in rep.items()})
                if classes[e[2]] in As:reverse.append((event,a,e[2],rows[a].copy(),'departure'))
                charts[a]=e[3];observe(past,pastgens,event,a,e[3],rows[a],'arrival')
            elif op=='INIT':need(charts[a] is None,'fresh INIT');charts[a]=e[2];rows[a]={}
            elif op=='CLEAR':
                need(charts[a]==e[2],'CLEAR chart')
                if classes[e[2]] in As:reverse.append((event,a,e[2],rows[a].copy(),'retirement'))
                charts[a]=None;rows[a]={}
            elif op=='SCALE':
                need(charts[a]==e[-1],'SCALE chart');q=K.rational(e[2]);need(q!=0,'invertible SCALE')
                rows[a]={i:q*v for i,v in rows[a].items()}
            elif op in ('ADD','COPY'):
                need(a!=e[2] and charts[a]==charts[e[2]]==e[-1],'invertible coframed scalar contact')
                if op=='COPY':need(not rows[a],'COPY zero');rows[a]={}
                K.add(rows[a],rows[e[2]],K.rational(e[3]))
            else:raise ValueError(op)
        need(charts==w['final']+[None]*w['owned_fields'],'all endpoints')
        future={f:{} for f in As};futuregens=[]
        for a,f in enumerate(w['final']):observe(future,futuregens,len(w['program']),a,f,rows[a],'final')
        reverse.sort(reverse=True,key=lambda z:z[0]);cursor=0
        for event in sorted(records,reverse=True):
            if time.monotonic()>deadline:raise TimeoutError
            while cursor<len(reverse) and reverse[cursor][0]>event:
                j,a,f,row,kind=reverse[cursor];observe(future,futuregens,j,a,f,row,kind);cursor+=1
            rec=records[event];row={int(i):F(v) for i,v in rec['target_row'].items()}
            rep=H.solve(future[classes[rec['source']]],row)
            rec.update(later_A_hit=rep is not None,later_A_rank=len(future[classes[rec['source']]]),
                later_witness=None if rep is None else {str(i):str(v) for i,v in rep.items()})
            rec['survives_both']=rec['earlier_B_hit'] and rec['later_A_hit']
        complete=True
    except TimeoutError:futuregens=[]
    result=dict(status='COMPLETE_EXACT_TEMPORAL_TWO_CACHE_FILTER' if complete else 'TIME_LIMIT_PARTIAL_TWO_CACHE_FILTER',
        source_sha256=K.PIN,expected_candidates=16,forward_candidates=len(records),future_candidates=sum('later_A_hit' in r for r in records.values()),
        last_event=last,earlier_B_hits=sum(r['earlier_B_hit'] for r in records.values()),
        later_A_hits=sum(r.get('later_A_hit',False) for r in records.values()),
        survivors=[r for r in records.values() if r.get('survives_both')],records=list(records.values()),
        earlier_generators=pastgens,later_generators=futuregens,seconds=time.monotonic()-started,
        scope='Generous cumulative earlier destination and strictly later source spans on unchanged arbitrary-input native history. A survivor is not a single-cut provider or physical word.')
    print(json.dumps({k:v for k,v in result.items() if k not in ('records','earlier_generators','later_generators','survivors')},indent=2))
    print('survivors',[(r['event'],r['owner'],r['rank']) for r in result['survivors']])
    return result
# Called read-only by verify.py with a fresh complete source census.
