#!/usr/bin/env python3
"""Exact delivery-cut connector optimum; woklerx/Codex, Apache-2.0."""
import hashlib
import heapq
import itertools
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,message):
    if not ok: raise ValueError(message)

def construct(rows,n):
    q=0; word=[]
    for i,mask in enumerate(rows):
        if mask:
            word.append(('A',i))
            for j in range(n):
                if mask>>j&1: word.append(('B',j)); q^=1<<j
            word.append(('A',i))
        word.append(('D',i))
    for j in range(n):
        if q>>j&1: word.append(('B',j))
    return word

def formula(rows,prices,aprice):
    counts=[sum(mask>>j&1 for mask in rows) for j in range(len(prices))]
    return sum(c*(k+k%2) for c,k in zip(prices,counts))+sum(2*c for c,m in zip(aprice,rows) if m)

def replay(rows,n,word,cuts=True):
    # Formal independent dirty/source columns; operators A_i B_j need no
    # commutation because each output only reads the shared connector.
    q=0; dirt=[0]*len(rows); masks=[0]*len(rows); next_row=0
    for kind,j in word:
        if kind=='B': q^=1<<j
        elif kind=='A':
            need(not cuts or j==next_row,'write outside requested output interval')
            dirt[j]^=1; masks[j]^=q
        else:
            need(j==next_row and dirt[j]==0 and masks[j]==rows[j],'bad delivered output')
            next_row+=1
    need(q==0 and dirt==[0]*len(rows) and masks==list(rows),'final dirty map')
    need(not cuts or next_row==len(rows),'undelivered output')

def oracle(rows,prices,aprice):
    # Dijkstra explores every query word in the finite exact quotient, without
    # a two-readout restriction. State: request index, connector source mask,
    # current output source mask, current output dirt parity.
    n=len(prices); start=(0,0,0,0); dist={start:0}; queue=[(0,start)]
    while queue:
        value,state=heapq.heappop(queue)
        if value!=dist[state]: continue
        i,q,a,dirt=state
        if i==len(rows) and q==0: return value,len(dist)
        edges=[((i,q^(1<<j),a,dirt),prices[j]) for j in range(n)]
        if i<len(rows):
            edges.append(((i,q,a^q,dirt^1),aprice[i]))
            if a==rows[i] and dirt==0: edges.append(((i+1,q,0,0),0))
        for nxt,cost in edges:
            new=value+cost
            if new<dist.get(nxt,10**30): dist[nxt]=new; heapq.heappush(queue,(new,nxt))
    raise ValueError('no schedule')

def run():
    for entry in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if entry['usage']=='input':
            need(hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256'],'source drift')
    cases=states=0
    for n,maxlength in [(1,5),(2,4),(3,2)]:
        for length in range(maxlength+1):
            for rows in itertools.product(range(1<<n),repeat=length):
                for prices in [tuple(range(1,n+1)),tuple(2*j+3 for j in range(n))]:
                    ap=tuple(2*i+1 for i in range(length))
                    cost,visited=oracle(rows,prices,ap)
                    need(cost==formula(rows,prices,ap),'Dijkstra disagrees with exact optimum')
                    word=construct(rows,n); replay(rows,n,word)
                    actual=sum(prices[j] if op=='B' else ap[j] if op=='A' else 0 for op,j in word)
                    need(actual==cost,'attaining word invoice')
                    cases+=1; states+=visited
    rows=list(range(1,32)); word=construct(rows,5); replay(rows,5,word)
    counts={k:sum(op==k for op,j in word) for k in ['A','B','D']}
    need(counts=={'A':62,'B':80,'D':31},'five-source exact invoice')
    source=json.loads((ROOT/'research/universal-connector-boundary/CERTIFICATE.json').read_text())
    offline=source['schedules']['five_extra_source']['word']
    replay(rows,5,offline,cuts=False)
    controls={}
    tests={'offline-writes-before-request':(rows,5,offline),
           'early-delivery':([3],2,[('D',0)]+construct([3],2)),
           'missing-terminal-restoration':([1],1,construct([1],1)[:-1]),
           'post-delivery-write':([1],1,construct([1],1)+[('A',0)])}
    for name,args in tests.items():
        try: replay(*args)
        except ValueError as exc: controls[name]=str(exc)
        else: raise ValueError('control accepted: '+name)
    return dict(status='PASS_CONNECTOR_DELIVERY_CUT_OPTIMUM',exact_quotient_price_cases=cases,
                quotient_states_visited=states,five_source_all_masks=counts,
                unit_query_cost=dict(persistent=142,separate_row_stars=222,offline=74),
                five_source_word=word,controls=controls)

if __name__=='__main__':
    result=run(); receipt=HERE/'EXPECTED.json'
    if receipt.exists(): need(json.loads(receipt.read_text())==json.loads(json.dumps(result)),'receipt mismatch')
    print(json.dumps(result,indent=2,sort_keys=True))
