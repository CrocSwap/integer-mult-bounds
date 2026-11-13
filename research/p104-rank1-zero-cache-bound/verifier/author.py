#!/usr/bin/env python3
"""Source-only exact all18 singleton rank-one helper-zero certificate."""
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict,Counter
from hashlib import sha256
from datetime import datetime,timezone
import argparse,gzip,json,math,time
HERE=Path(__file__).resolve().parent
PIN='acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
NEW_HELPERS=(451,746,750,769,1254,1459)
PRIME=1000033
DEADLINE=None
def bounded():
    if DEADLINE is not None and time.time()>=DEADLINE:raise TimeoutError('task UTC deadline')
def need(ok,label):
    if not ok:raise ValueError(label)
def add(a,b,q):
    for h,v in b.items():
        z=a.get(h,0)+q*v
        if z:a[h]=z
        else:a.pop(h,None)
def framekey(frame):
    s={0}
    for u in frame:
        need(0<u<512 and u not in s,'independent frame basis');s|={v^u for v in s}
    return tuple(sorted(s))
def column_rank(columns,expected):
    """Full-size modular minor certificate; exact row-count is the Q upper bound."""
    basis={};pivots=[]
    for h,col in sorted(columns.items(),key=lambda x:(len(x[1]),x[0])):
        v=col.copy()
        while v:
            p=max(v)
            if p not in basis:
                a=v[p];iv=pow(a,PRIME-2,PRIME);basis[p]={j:t*iv%PRIME for j,t in v.items()};pivots.append([h,p,a]);break
            q=v[p]
            for j,t in basis[p].items():
                z=(v.get(j,0)-q*t)%PRIME
                if z:v[j]=z
                else:v.pop(j,None)
        if len(basis)==expected:break
    return {'rank_mod':len(basis),'literal_row_upper_bound':expected,'full_row_rank':len(basis)==expected,'pivot_columns_rows_values':pivots}
def exact_basis(bank):
    basis={};lifts={}
    for i,o in enumerate(bank):
        if i%128==0:bounded()
        v=o['row'].copy();w={i:Q(1)}
        for p in sorted(basis,reverse=True):
            if v.get(p):q=v[p];add(v,basis[p],-q);add(w,lifts[p],-q)
        need(v,'original exact independence')
        p=max(v);q=1/v[p];basis[p]={h:a*q for h,a in v.items()};lifts[p]={j:a*q for j,a in w.items()}
    return basis,lifts
def exact_unit_expression(bank,h,cache,key):
    for i,o in enumerate(bank):
        if len(o['row'])==1 and h in o['row']:return {i:1/o['row'][h]},{}
    if key not in cache:cache[key]=exact_basis(bank)
    basis,lifts=cache[key];v={h:Q(1)};answer={}
    for p in sorted(basis,reverse=True):
        if v.get(p):q=v[p];add(v,basis[p],-q);add(answer,lifts[p],q)
    actual={}
    for i,q in answer.items():add(actual,bank[i]['row'],q)
    add(actual,v,Q(1));need(actual=={h:Q(1)},'direct exact unit reduction identity')
    return answer,v
def encode(row):return {str(h):str(a) for h,a in sorted(row.items())}
def verify(source):
    start=time.monotonic();bounded();raw=source.read_bytes();need(sha256(raw).hexdigest()==PIN,'source pin');w=json.loads(gzip.decompress(raw))
    need(all(PRIME%d for d in range(2,math.isqrt(PRIME)+1)),'prime by trial division')
    classes=list(map(framekey,w['frames']));aliases=defaultdict(list)
    for f,k in enumerate(classes):aliases[k].append(f)
    n=w['public'];mains=set(w['live'])|{h+112 for h in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2']);helpers=set(range(n))-mains
    HELPERS=tuple(sorted(h for h in helpers if abs(len(w['frames'][w['initial'][h]])-len(w['frames'][w['final'][h]]))==1))
    need(len(HELPERS)==18,'fresh all18 rank-one original helpers')
    need(all(abs(len(w['frames'][w['initial'][h]])-len(w['frames'][w['final'][h]]))==1 for h in HELPERS),'actual target ranks all one')
    rows=[{h:Q(1)} for h in range(n)]+[None]*w['owned_fields'];cur=w['initial'].copy()+[None]*w['owned_fields'];banks=defaultdict(list);moves={};zeros={h:[] for h in HELPERS}
    def observe(event,a,f,kind):banks[classes[f]].append({'event':event,'owner':a,'frame':f,'kind':kind,'row':rows[a].copy()})
    for a,f in enumerate(w['initial']):observe(-1,a,f,'initial')
    for event,e in enumerate(w['program']):
        if event%256==0:bounded()
        op,a=e[:2]
        if op=='MOVE':
            old,new=e[2:4];need(cur[a]==old and rows[a] and bool(e[4])==(a>=n),'live owned/public MOVE')
            left,right=set(classes[old]),set(classes[new]);need(left<right if a<n else left<right or right<left,'strict nested MOVE')
            r=abs(len(w['frames'][old])-len(w['frames'][new]));need(r>0,'paid positive rank');moves[event]={'event':event,'literal':e,'rank':r,'row':rows[a].copy()}
            if len(rows[a])==1:
                h=next(iter(rows[a]))
                if h in zeros:zeros[h].append(event)
            cur[a]=new;observe(event,a,new,'arrival')
        elif op=='INIT':need(a>=n and cur[a] is None and rows[a] is None,'fresh INIT');cur[a]=e[2];rows[a]={}
        elif op=='CLEAR':need(a>=n and cur[a]==e[2] and rows[a] is not None,'owned CLEAR');cur[a]=None;rows[a]=None
        elif op=='SCALE':
            need(cur[a]==e[-1] and Q(e[2]),'coframed SCALE');q=Q(e[2]);rows[a]={h:q*v for h,v in rows[a].items()}
        elif op in ['ADD','COPY']:
            b=e[2];need(a!=b and cur[a]==cur[b]==e[-1],'coframed contact')
            if op=='COPY':need(a>=n and not rows[a],'COPY into zero')
            add(rows[a],rows[b],Q(e[3]))
        else:raise ValueError(op)
    need(cur==w['final']+[None]*w['owned_fields'] and len(moves)==6279,'complete endpoints and all cuts')
    need(all(rows[h]=={h:Q(1)} for h in HELPERS),'all18 autonomous original helper endpoints')
    need(sum(map(len,banks.values()))==7780,'complete observation stock')
    neutral=tuple(h for h in HELPERS if len(zeros[h])==1 and moves[zeros[h][0]]['rank']==1)
    other=tuple(h for h in HELPERS if h not in neutral)
    need(len(neutral)==12 and other==NEW_HELPERS,'fresh12neutral6nonneutral partition')
    inverses={};originals=[];cases={h:{'helper':h,'target_rank':1,'zero_MOVE_events':zeros[h],'hits':[],'coframes':[]} for h in HELPERS};basis_cache={};rank_total=0
    def mod(q):
        if q.denominator not in inverses:
            need(q.denominator%PRIME,'source denominator invertible');inverses[q.denominator]=pow(q.denominator%PRIME,PRIME-2,PRIME)
        return q.numerator*inverses[q.denominator]%PRIME
    def label(o):return {k:v for k,v in o.items() if k!='row'}
    for ix,(key,bank) in enumerate(sorted(banks.items(),key=lambda x:aliases[x[0]][0])):
        bounded();frame=aliases[key][0];m=len(bank);columns=defaultdict(dict);support=set();digest=sha256()
        for i,o in enumerate(bank):
            support.update(o['row']);digest.update((json.dumps([label(o),encode(o['row'])],sort_keys=True,separators=(',',':'))+'\n').encode())
            for h,q in o['row'].items():
                value=mod(q)
                if value:columns[h][i]=value
        original=column_rank(columns,m);need(original['full_row_rank'],'full row count certifies exact original rank')
        need(len(set(o['frame'] for o in bank))==1,'no used nonidentical frame aliases')
        originals.append({'frame':frame,'row_count':m,'matrix_sha256':digest.hexdigest(),'full_row_rank_certificate':original});rank_total+=m
        for h in HELPERS:
            bounded();d={'frame':frame,'original_rows':m}
            if h not in support:
                d.update(relation_in_final_span=False,certificate={'method':'original_minor_plus_exact_new_unit_column','original_frame_certificate':frame,'new_column':h,'new_pivot_row':m,'new_pivot_value':1,'exact_rational_rank':m+1,'literal_row_upper_bound':m+1})
            else:
                augmented={j:v.copy() for j,v in columns.items()};augmented.setdefault(h,{})[m]=1;cert=column_rank(augmented,m+1)
                d['certificate']=cert
                if cert['full_row_rank']:d['relation_in_final_span']=False
                else:
                    need(cert['rank_mod']==m,'unit extension rank at least original rank');answer,residual=exact_unit_expression(bank,h,basis_cache,key)
                    if residual:
                        d.update(relation_in_final_span=False,exact_Q_remainder=encode(residual),exact_Q_basis_row_count=m)
                    else:
                        d['relation_in_final_span']=True
                        d['unique_expression']=[{'observation':label(bank[i]),'coefficient':str(q)} for i,q in sorted(answer.items())]
                        last=max(answer,key=lambda i:(bank[i]['event'],i));o=bank[last]
                        if o['kind']=='arrival':
                            e=o['event'];q=answer[last];providers=[{'observation':label(bank[i]),'coefficient':str(-a/q)} for i,a in sorted(answer.items()) if i!=last]
                            need(all(p['observation']['event']<e for p in providers),'strict provider timing')
                            actual=moves[e]['row'].copy()
                            for i,a in answer.items():
                                if i!=last:add(actual,bank[i]['row'],a/q)
                            need(actual=={h:1/q},'direct exact target/history/unit identity')
                            hit={'event':e,'literal':moves[e]['literal'],'rank':moves[e]['rank'],'zero':e in zeros[h],'relation_coefficient':str(1/q),'target_row':encode(moves[e]['row']),'providers':providers}
                            cases[h]['hits'].append(hit);d['latest_support_MOVE']=e
            cases[h]['coframes'].append(d)
    need(rank_total==7780 and len(originals)==979,'complete shared source/rank certificate')
    for h,c in cases.items():
        events=sorted(set(c['zero_MOVE_events'])|{x['event'] for x in c['hits']});credit=Counter(moves[e]['rank'] for e in events);gain=credit.copy();gain.subtract({1:1})
        need(set(c['zero_MOVE_events'])<={x['event'] for x in c['hits']},'exact zeros included among all quotient circuit hits')
        need(len(events)==1 and credit==Counter({1:1}),'exact one rank1 credit per singleton')
        c.update(classification='prior_neutral_singleton' if h in neutral else 'new_public_cache_singleton',eligible_MOVE_events_union=events,credit_histogram=dict(credit),native_gain_profile={r:n for r,n in gain.items() if n},new_nonzero_cache_events=sorted(x['event'] for x in c['hits'] if not x['zero']),history_circuit_hits=len(c['hits']))
    out={'status':'COMPLETE_ALL18_SINGLE_RANK1_ZERO_PROMISE_CENSUS','source_sha256':PIN,'source_payload_sha256':sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'helpers_tested':list(HELPERS),'neutral_rank1_helpers':list(neutral),'nonneutral_rank1_helpers':list(other),'joint_helper_promises_tested':False,'all_original_MOVEs_per_helper':6279,'coframes_per_helper':979,'exact_observations':7780,'prime':PRIME,'original_coframe_certificates':originals,'cases':[cases[h] for h in HELPERS],'unfinished_helpers':[],'source_only_exact_replay':True,'distinct_denominators':len(inverses),'scope':'Only all18 SINGLE rank-one coordinate-zero promises, unchanged original source/strict histories/coframes, no decoded target prices. Every benefit is an optimistic whole-MOVE credit; physical interfaces, ordinary work and stock remain obligations.'}
    return out
