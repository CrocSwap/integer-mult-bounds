#!/usr/bin/env python3
"""Conservative first-source unpaid-prefix family for the pinned raw source.

Value dependencies are unions, never cancellations.  A paid-taint boolean is
ORed through each local operation and set after any paid operation, so selected
payloads have exactly one original public input and no prior paid operation on
any contributing field.  All chart checks are from the pinned native replay.
"""
from collections import Counter
import hashlib,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import constant_nested_witness as z
from math import log10

c,g,q,n=z.c,z.g,z.q,z.n; dims=z.dims
roots=[[1<<(r*q+p) for p in range(q)] for r in range(c['roles'])]
taint=[[False]*q for _ in range(c['roles'])]
tags=[('root',r,p) for r in range(c['roles']) for p in range(q)]
ranks=[1+7*len(c['diagonal'][r]['stages']) for r in range(c['roles']) for _ in range(q)]
candidates=[]; paid_count=0; allpaid=[]; call_count=0

def record(tag,paidrank,dep,risk):
    global paid_count
    if dep and not dep&(dep-1) and not risk:
        i=dep.bit_length()-1
        candidates.append((tag,paidrank,tags[i],ranks[i]))
    allpaid.append((tag,paidrank)); paid_count+=1

for clock,(op,*args) in enumerate(c['events']):
    if op=='LOCAL':
        stage,x,y=args
        v=dict(enumerate(roots[x]+roots[y])); t=dict(enumerate(taint[x]+taint[y]))
        for h in range(2*q,n):
            i=len(tags);tags.append(('helper',clock,h))
            rank=abs(dims[g['final'][h]]-dims[g['start'][h]])
            ranks.append(rank);v[h]=1<<i;t[h]=False
        for site,(local,d,*a) in enumerate(g['program']):
            if local=='INIT':
                assert d not in v;v[d]=0;t[d]=False
            elif local=='CLEAR':
                del v[d];del t[d]
            elif local=='ADD':
                s,chart=a;v[d]|=v[s];t[d]|=t[s]
            elif local=='SWAP':
                s,=a;v[d],v[s]=v[s],v[d];t[d],t[s]=t[s],t[d]
            elif local=='MOVE':
                src,dst=a;record(('move',clock,site,d),abs(dims[dst]-dims[src]),v[d],t[d]);t[d]=True
            else: raise AssertionError(local)
        assert set(v)==set(range(n))
        roots[x]=[v[i] for i in range(q)]; roots[y]=[v[q+i] for i in range(q)]
        taint[x]=[t[i] for i in range(q)];taint[y]=[t[q+i] for i in range(q)]
        call_count+=1
    elif op=='ADD':
        x,y=args
        roots[x]=[u|v for u,v in zip(roots[x],roots[y],strict=True)]
        taint[x]=[u or v for u,v in zip(taint[x],taint[y],strict=True)]
    elif op=='SWAP':
        x,y=args;roots[x],roots[y]=roots[y],roots[x];taint[x],taint[y]=taint[y],taint[x]
    elif op=='QUERY':
        x,y=args
        for p in range(q):
            record(('QUERY',clock,p),1,roots[y][p],taint[y][p])
            roots[x][p]|=roots[y][p];taint[x][p]=True
    elif op=='IDLE_ONE':
        x,stages=args
        for p in range(q):
            record(('IDLE_ONE',clock,p),7*len(stages),roots[x][p],taint[x][p])
            taint[x][p]=True
    else: raise AssertionError(op)
assert call_count==36 and len(tags)==18906 and paid_count==104904
assert allpaid[0]==(('move',4,2,630),1)
selected=[r for r in candidates if r[3]<=15 and r[1]<=12]
strict=[r for r in selected if r[3]<15]
equal=[r for r in selected if r[3]==15]
(Path(__file__).resolve().parent/'zero_raw_labels.json').write_text(json.dumps(selected))
assert (('move',4,2,630),1,('helper',4,222),8) in selected
counts=Counter((r[3],r[1],r[2][0]) for r in selected)
counts_all=Counter((r[3],r[1],r[2][0]) for r in candidates)
P=268
family=len(selected)**P-len(equal)**P
assert family>0
# At c=0, all emitted ranks <=12^268 and need no paid splitting.  This is the
# exact maximal rank sum for the *defined no-paid-taint single-source family*,
# not a maximality claim over all zero jobs.
rankmass=sum(r[1] for r in selected)**P-sum(r[1] for r in equal)**P
print(json.dumps({'source_graph_sha256':'74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326',
 'source_caller_sha256':'757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b',
 'productive_ports':len(tags),'paid_labels':len(allpaid),'no_paid_taint_single_source_total':len(candidates),
 'all_single_source_hist':[{'target_rank':a,'paid_rank':b,'target_kind':k,'count':v} for (a,b,k),v in sorted(counts_all.items())],
 'selected_target_rank_le15_paid_rank_le12':len(selected),
 'selected_target_rank_lt15':len(strict),'selected_target_rank_eq15':len(equal),
 'selected_hist':[{'target_rank':a,'paid_rank':b,'target_kind':k,'count':v} for (a,b,k),v in sorted(counts.items())],
 'selected_first_examples':selected[:20],
 'first_paid_label':allpaid[0], 'factor_power':P,'floor':15,
 'exact_zero_tuple_count_expression':f'{len(selected)}**{P} - {len(equal)}**{P}',
 'exact_zero_tuple_count_digits':len(str(family)),
 'exact_total_unpowered_rank_expression':f'{sum(r[1] for r in selected)}**{P} - {sum(r[1] for r in equal)}**{P}',
 'exact_rank_sum_digits':len(str(rankmass)),
 'zero_tuple_count_over_all_paid_tuple_bound_log10':P*log10(len(selected)/paid_count),
 'scope':'conservative no-prior-paid-path dataflow; no maximality among other zero jobs; single paid block per selected tuple'},indent=2))
print('PASS_NO_PAID_TAINT_SINGLE_SOURCE_SCAN')
