"""Independent directional and COPY-guard audit of one exact helper cut after independently checked MOVE relocations.

@CubeJerry with substantial OpenAI assistance. Apache-2.0.
Written by the normalizer/owned-contract research agent independently of the
construction agent's forward prefix-row evaluator. The caller may construct
inputs using any producer; this module authenticates each witness's input
payload and imports no producer scientific code.
"""
from fractions import Fraction as Q
from hashlib import sha256
import json

def need(condition,message):
    if not condition:raise ValueError(message)


def update(row,key,change):
    value=row.get(key,Q(0))+change
    if value:row[key]=value
    else:row.pop(key,None)


def prefix_dual(events,a):
    result=dict(a)
    for event in reversed(events):
        op,target=event[:2]
        value=result.get(target,Q(0))
        if op in ('INIT','CLEAR'):
            result.pop(target,None)
        elif op=='SCALE':
            if value:result[target]=value*Q(event[-2])
        elif op=='ADD':
            if value:update(result,event[2],value*Q(event[-2]))
        elif op=='COPY':
            # Adjoint of the ideal source COPY. Its preceding zero invariant
            # makes this equal to the implemented ADD on source inputs.
            result.pop(target,None)
            if value:update(result,event[2],value*Q(event[-2]))
        else:need(op=='MOVE','known prefix opcode')
    return result


def suffix_direction(events,b):
    result=dict(b);copy_guards=0
    for event in events:
        op,target=event[:2]
        if op in ('INIT','CLEAR'):
            result.pop(target,None)
        elif op=='SCALE':
            if target in result:result[target]*=Q(event[-2])
        elif op in ('ADD','COPY'):
            if op=='COPY':
                need(not result.get(target,Q(0)),'new arbitrary cut input preserves COPY zero-destination precondition')
                copy_guards+=1
            update(result,target,Q(event[-2])*result.get(event[2],Q(0)))
        else:need(op=='MOVE','known suffix opcode')
    return result,copy_guards


def prepare(word,entry):
    """Independently relocate literal public MOVEs through contact-free windows."""
    from copy import deepcopy
    from collections import Counter
    hit=entry['witness'];cut=hit['cut'];events=word['program'];n=word['public']
    need(0<=cut<=len(events),'valid original cut')
    removed=set();before=[];after=[];roles=set()
    for path in hit['paths']:
        r,lo,hi=path['role'],path['lo'],path['hi']
        need(type(r) is int and 0<=r<n and r not in roles,'distinct public relocation owner');roles.add(r)
        need(path['private'] is False and len(path['moves'])==1,'one public MOVE')
        m=path['moves'][0];old,new,frame=path['old'],path['new'],path['frame']
        need(0<=lo<=cut<=hi<=len(events) and lo<=m<hi,'valid retiming interval')
        need(m not in removed and events[m]==['MOVE',r,old,new,False],'exact original paid operator')
        need(frame==hit['frame'] and frame in (old,new),'only unchanged-edge endpoint frame')
        for j in range(lo,hi):
            event=events[j]
            if j==m:continue
            need(event[1]!=r and not(event[0] in ('ADD','COPY') and event[2]==r),'no scalar or other operator incidence in relocation window')
        rank=abs(len(word['frames'][new])-len(word['frames'][old]))
        need(rank>0 and [x for x in path['old_paid'] if x]==[rank] and [x for x in path['new_paid'] if x]==[rank] and path['cost']==0,'unchanged rank and paid cost')
        removed.add(m);(before if frame==new else after).append(events[m][:])
    prefix=[event for j,event in enumerate(events[:cut]) if j not in removed]+before
    suffix=after+[event for j,event in enumerate(events[cut:],start=cut) if j not in removed]
    prepared=deepcopy(word);prepared['program']=prefix+suffix
    need(Counter(tuple(e) for e in events)==Counter(tuple(e) for e in prepared['program']),'every instruction retained once')
    need(entry['prepared_split']['cut_after']+1==len(prefix),'exact prepared cut')
    for key in ('a','b','c','d','frame','pivot','ranks'):
        need(entry['prepared_split'][key]==hit[key],'same mathematical cut data')
    return prepared,len(hit['paths'])


def check_cut(word,entry):
    payload=sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(payload==entry['source_payload_sha256'],'exact intermediate source payload')
    word,retimings=prepare(word,entry)
    prepared_payload=sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    witness=entry['prepared_split'];cut=witness['cut_after']+1;n=word['public']
    a,b,c,d=({int(k):Q(v) for k,v in witness[key].items()} for key in ('a','b','c','d'))
    need(sum(v*b.get(k,Q(0)) for k,v in a.items())==sum(v*d.get(k,Q(0)) for k,v in c.items())==1,'two exact unit pairings')
    mains=set(word['live'])|{r+112 for r in word['live']}|set(word['hosted']['X2'])|set(word['hosted']['Y2'])
    p=witness['pivot'];frame=witness['frame'];u,v=word['initial'][p],word['final'][p]
    need(p<n and p not in mains,'pivot is an independent public helper')
    need(all(r<n and r not in mains and word['initial'][r]==u and word['final'][r]==v for r in set(c)|set(d)),'boundary supports use only one autonomous public-helper block')
    current=word['initial'][:]+[None]*word['owned_fields']
    for event in word['program'][:cut]:
        if event[0]=='MOVE':current[event[1]]=event[3]
        elif event[0]=='INIT':current[event[1]]=event[2]
        elif event[0]=='CLEAR':current[event[1]]=None
    need(all(current[r]==frame for r in set(a)|set(b)|{p}),'entire middle basis is at one exact current chart')
    need(prefix_dual(word['program'][:cut],a)==c,'independent reverse-prefix functional on all inputs')
    direction,copies=suffix_direction(word['program'][cut:],b)
    need(direction==d,'exact full suffix direction including every owned return')
    altered=dict(a);first=min(altered);altered[first]+=1
    need(prefix_dual(word['program'][:cut],altered)!=c,'wrong cut functional actually rejected')
    return dict(source_payload_sha256=payload,prepared_payload_sha256=prepared_payload,retimed_MOVEs=retimings,cut=cut,pivot=p,frame=frame,
                middle_owned_labels=sorted(r for r in set(a)|set(b) if r>=n),
                future_COPY_zero_guards=copies)
