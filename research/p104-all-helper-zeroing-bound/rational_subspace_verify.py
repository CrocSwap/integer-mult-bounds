#!/usr/bin/env python3
"""Fresh exact-Q source replay and all groupwise funding subset checks.
No matrix dump or prime-field zero is used by this author implementation.
"""
from collections import defaultdict
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import gzip,hashlib,json,time
HERE=Path(__file__).resolve().parent
PIN='acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
def need(ok,label):
    if not ok:raise ValueError(label)
@lru_cache(None)
def scalar(text):return F(text)
def add(dst,src,q):
    for i,v in src.items():
        z=dst.get(i,0)+(v if q==1 else -v if q==-1 else q*v)
        if z:dst[i]=z
        else:dst.pop(i,None)
def rank(rows):
    basis={}
    for row in rows:
        v=row.copy()
        while v:
            p=max(v)
            if p not in basis:
                q=1/v[p];basis[p]={i:x*q for i,x in v.items()};break
            add(v,basis[p],-v[p])
    return len(basis)
def run():
    started=time.monotonic()
    wordraw=(HERE/'inputs/WORD.json.gz').read_bytes()
    need(hashlib.sha256(wordraw).hexdigest()==PIN,'literal source pin')
    w=json.loads(gzip.decompress(wordraw));n=w['public']
    ar=(HERE/'ASSIGNMENT.json').read_bytes()
    assignment={r['event']:r for r in json.loads(ar)}
    cr=(HERE/'GROUP-COMPONENTS.json').read_bytes();parts={(g['entrance_frame'],g['exit_frame']):g['components'] for g in json.loads(cr)}
    mains=set(w['live'])|{i+112 for i in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
    members=defaultdict(set)
    for h in set(range(n))-mains:members[w['initial'][h],w['final'][h]].add(h)
    groupof={h:g for g,hs in members.items() for h in hs}
    rows=[{i:F(1)} if i<n else {} for i in range(n+w['owned_fields'])]
    charts=w['initial']+[None]*w['owned_fields'];families=defaultdict(dict)
    for event,e in enumerate(w['program']):
        op,a=e[:2]
        if op=='MOVE':
            need(charts[a]==e[2],'MOVE chart')
            if event in assignment:
                charge=assignment[event];h=charge['assigned_helper'];g=groupof[h]
                r=abs(len(w['frames'][e[3]])-len(w['frames'][e[2]]))
                R=abs(len(w['frames'][g[1]])-len(w['frames'][g[0]]))
                need(rows[a].get(h) and not(set(rows[a])&mains),'charged nonzero main-free row')
                need(r==charge['rank'] and R==charge['target_rank'] and 1<=r<=R<=9,'rank tariff')
                families[g][event]=({i:v for i,v in rows[a].items() if i in members[g]},r)
            charts[a]=e[3]
        elif op=='INIT':need(charts[a] is None,'fresh INIT');charts[a]=e[2];rows[a]={}
        elif op=='CLEAR':need(charts[a]==e[2],'CLEAR chart');charts[a]=None;rows[a]={}
        elif op=='SCALE':
            need(charts[a]==e[-1],'SCALE chart');q=scalar(e[2]);rows[a]={i:q*v for i,v in rows[a].items() if q*v}
        elif op in ('ADD','COPY'):
            need(charts[a]==charts[e[2]]==e[-1],'scalar cochart')
            if op=='COPY':need(not rows[a],'COPY zero');rows[a]={}
            add(rows[a],rows[e[2]],scalar(e[3]))
        else:raise ValueError(op)
    need(charts==w['final']+[None]*w['owned_fields'],'all endpoint/lifetime charts')
    need(sum(map(len,families.values()))==468,'all charged rows captured')
    return finish(w,families,parts,ar,cr,started)

def finish(w,families,parts,ar,cr,started):
    need(9*1000**100<1023**100,'price-envelope integer proof')
    need(rank([{0:F(1)},{0:F(2)}])==1,'parallel rank control')
    need(F(2)>rank([{0:F(1)},{0:F(2)}]),'overpriced pair control')
    need(rank([{0:F(1)}])+rank([{0:F(2)}])>rank([{0:F(1)},{0:F(2)}]),'false direct-sum control')
    summaries=[];checks=0;components=0;singletons=0;totalrank=0
    for g,family in sorted(families.items()):
        R=abs(len(w['frames'][g[1]])-len(w['frames'][g[0]]))
        pieces=parts.get(g,[[e] for e in sorted(family)])
        covered=[e for piece in pieces for e in piece]
        need(len(covered)==len(set(covered)) and set(covered)==set(family),'partition coverage')
        records=[];sumrank=0
        for events in pieces:
            need(1<=len(events)<=6,'small component bound');components+=1;singletons+=len(events)==1
            weights=[min(F(1),F(1023*family[e][1],1000*R)) for e in events]
            table=[0]
            for mask in range(1,1<<len(events)):
                chosen=[i for i in range(len(events)) if mask>>i&1]
                actual=rank([family[events[i]][0] for i in chosen])
                cost=sum((weights[i] for i in chosen),F(0));checks+=1
                need(cost<=actual,'projected subset rational funding')
                table.append(actual)
            sumrank+=table[-1]
            records.append(dict(events=events,paid_ranks=[family[e][1] for e in events],
                envelope_weights=list(map(str,weights)),subset_ranks_Q_binary_order=table))
        fullrank=rank([row for row,r in family.values()])
        need(fullrank==sumrank,'component spans direct sum over Q');totalrank+=fullrank
        summaries.append(dict(entrance_frame=g[0],exit_frame=g[1],target_rank=R,
            charged_rows=len(family),rank_Q=fullrank,components=records))
    result=dict(status='PASS_FRESH_SOURCE_EXACT_Q_GROUP_FUNDING',source_sha256=PIN,
        assignment_sha256=hashlib.sha256(ar).hexdigest(),component_partition_sha256=hashlib.sha256(cr).hexdigest(),
        kappa_interval=['0','1/100'],groups=len(families),charged_rows=sum(map(len,families.values())),
        components=components,singletons=singletons,nontrivial_components=components-singletons,
        nonempty_subset_checks=checks,rank_Q_total=totalrank,
        envelope='min(1,1023*r/(1000*R))',envelope_integer_test_passed=True,
        all_group_component_spans_direct_sum_Q=True,summaries=summaries,
        scope='Exact-Q author corroboration on fresh literal source. No modular-zero inference; no source build or new multiplication exponent.')
    return result
if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
