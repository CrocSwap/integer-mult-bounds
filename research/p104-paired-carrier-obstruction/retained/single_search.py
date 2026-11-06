"""Distributed existing-carrier response-span screen on exact PR6702 word.

Jerry Chen / @CubeJerry with OpenAI Codex assistance. Apache-2.0.
Finite modular screen only; exact construction is a separate obligation.
"""
import bisect
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

MOD = 65521
SOURCE = Path(sys.argv[1])
OUT = Path(sys.argv[2])
WORD_SHA = 'e8c7a9d54d98a4cfa27e15593016b3908afed303e0f480076ed3f596192e5a4d'
SOURCE_NAMES={WORD_SHA:'PR6702', 'e64cc53ea0088191423045cb8563b5bc87a34f6b992baa1593c7917d95a07820':'PR6453'}
source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
if source_sha not in SOURCE_NAMES:raise ValueError('Unrecognized pinned source bytes')
source_name=SOURCE_NAMES[source_sha]
w = json.load(gzip.open(SOURCE))
p, n = w['program'], w['public']
N = n + w['owned_fields']
full = {r for r,f in enumerate(w['final']) if f == 127}

def scalar(x):
    q=Fraction(x)
    if q.denominator & (q.denominator-1):raise ValueError('Source scalar is not dyadic')
    return q.numerator * pow(q.denominator, -1, MOD) % MOD

def axpy(a,b,q):
    for k,v in b.items():
        z=(a.get(k,0)+q*v)%MOD
        if z: a[k]=z
        else: a.pop(k,None)

writes=defaultdict(list)
reads=defaultdict(list)
for i,e in enumerate(p):
    writes[e[1]].append((i,e))
    if e[0] in ('ADD','COPY'): reads[e[2]].append(i)
intervals=[]
export_to=defaultdict(list)
main=set(w['live'])|{r+112 for r in w['live']}
for r in (r for r in range(n) if r not in main):
    t=writes[r]
    for k,(i,e) in enumerate(t):
        if e[0]!='MOVE': continue
        j=next((j for j in range(k+1,len(t)) if t[j][1][0]=='MOVE'),None)
        if j is None or any(v[0]!='SCALE' for _,v in t[k+1:j]): continue
        b,f=t[j]
        exports=[z for z in reads[r] if i<z<b]
        if not exports: continue
        if any(p[z][0] != 'ADD' for z in exports):raise ValueError('The pinned scope requires ADD-only exports')
        scales=[(ii,scalar(v[2])) for ii,v in t[k+1:j]]
        ranks=[len(w['frames'][e[3]])-len(w['frames'][e[2]]),len(w['frames'][f[3]])-len(w['frames'][f[2]])]
        lo=next((t[q][0]+1 for q in range(k-1,-1,-1) if t[q][1][0]!='SCALE'),0)
        hi=next((t[q][0] for q in range(j+1,len(t)) if t[q][1][0]!='SCALE'),len(p))
        move_lo=max([lo]+[z+1 for z in reads[r] if lo<=z<i])
        move_hi=min([hi]+[z for z in reads[r] if b<z<hi])
        item=dict(role=r,first=i,second=b,lo=lo,hi=hi,move_lo=move_lo,move_hi=move_hi,E=e[2],F=e[3],G=f[3],exports=exports,scales=scales,paid_ranks_before=ranks,paid_rank_after=sum(ranks),target={},nodes=[])
        idx=len(intervals); intervals.append(item)
        for z in exports:
            q=scalar(p[z][3])
            for si,sq in scales:
                if si<z: q=q*sq%MOD
            export_to[z].append((idx,q))
# Check the actual old-input coordinate map modulo p. This also rules out
# a vacuous obstruction caused by the held source row vanishing modulo p.
rows=[{r:1} if r<n else {} for r in range(N)]
source_rows={c['first']:c['role'] for c in intervals}
copy_checks=0
for j,e in enumerate(p):
    if j in source_rows and not rows[source_rows[j]]:
        raise ValueError('Held old-input source row vanishes modulo p')
    op,r=e[:2]
    if op in ('INIT','CLEAR'):rows[r]={}
    elif op=='SCALE':
        q=scalar(e[2])
        if not q:raise ValueError('A source SCALE is not a modular unit')
        rows[r]={k:q*v%MOD for k,v in rows[r].items()}
    elif op in ('ADD','COPY'):
        if op=='COPY':
            if rows[r]:raise ValueError('Source COPY target is not zero')
            copy_checks+=1
        axpy(rows[r],rows[e[2]],scalar(e[3]))
expected=[{r:1} if r<n else {} for r in range(N)]
for r in w['live']:expected[r+112][r]=1
if rows!=expected:raise ValueError('Source endpoint fails modulo p')
source_validation=dict(public_inputs=n,owned_fields=N-n,nonzero_held_rows=len(source_rows),copy_zero_checks=copy_checks,endpoint_rows=N)
print('intervals',len(intervals),'proper outputs',n-len(full),flush=True)
byframe=defaultdict(list)
for idx,c in enumerate(intervals):
    byframe[c['E']].append((idx,'E',c['lo'],c['move_hi']))
    byframe[c['G']].append((idx,'G',c['move_lo'],c['hi']))
# Columns of the scalar suffix map to all proper public outputs and future
# COPY-zero observables. Full-output cleanup is checked only after a nomination.
cols=[{r:1} if r<n and r not in full else {} for r in range(N)]
frames=w['final']+[None]*w['owned_fields']
ends=[len(p)]*N
nodes=0

def save(r,lo,hi):
    global nodes
    if lo>hi or frames[r] is None or not cols[r]: return
    f=frames[r]
    relevant=[(idx,kind,a,b) for idx,kind,a,b in byframe[f] if r != intervals[idx]['role'] and max(lo,a)<=min(hi,b)]
    if not relevant:return
    vec=cols[r].copy(); nodes+=1
    for idx,kind,a,b in relevant:
        left,right=max(lo,a),min(hi,b)
        # An E injection should be as early as possible; G as late as possible.
        cut=left if kind=='E' else right
        intervals[idx]['nodes'].append((cut,r,vec,kind))

monitor=n
for i in range(len(p)-1,-1,-1):
    e=p[i];op,r=e[:2]
    affected={r}
    if op in ('ADD','COPY'):affected.add(e[2])
    for s in affected:
        save(s,i+1,ends[s]);ends[s]=i
    for idx,q in export_to[i]: axpy(intervals[idx]['target'],cols[r],q)
    if op=='MOVE':frames[r]=e[2]
    elif op=='SCALE':cols[r]={k:v*scalar(e[2])%MOD for k,v in cols[r].items()}
    elif op in ('ADD','COPY'):
        axpy(cols[e[2]],cols[r],scalar(e[3]))
        if op=='COPY':cols[r][monitor]=1;monitor+=1
    elif op in ('INIT','CLEAR'):
        cols[r]={}
        frames[r]=None if op=='INIT' else e[2]
    else:raise ValueError(op)
for r in range(N):save(r,0,ends[r])
print('candidate nodes',nodes,'COPY monitors',monitor-n,flush=True)

def solve(nodes,target):
    basis={}
    used=set()
    for j,node in enumerate(nodes):
        vec=node[2]
        v=vec.copy(); coeff={j:1}
        while v:
            k=min(v)
            if k not in basis:
                a=pow(v[k],-1,MOD)
                v={i:q*a%MOD for i,q in v.items()};coeff={i:q*a%MOD for i,q in coeff.items()}
                basis[k]=(v,coeff);break
            b,c=basis[k];q=-v[k]
            axpy(v,b,q);axpy(coeff,c,q)
    v=target.copy();out={}
    while v:
        k=min(v)
        if k not in basis:return None,len(basis)
        b,c=basis[k];q=v[k]
        axpy(v,b,-q);axpy(out,c,q)
    return out,len(basis)

hits=[];stats=Counter()
for idx,c in enumerate(intervals):
    # Duplicate vectors do not expand the space. Their earliest legal site is retained.
    first=c['move_lo'];last=c['move_hi']
    nominations=[]
    cuts=sorted({first,last}|{node[0] for node in c['nodes'] if first<=node[0]<=last})
    maxrank=0
    for t in cuts:
        seen=set();unique=[]
        for node in sorted(c['nodes'],key=lambda x:(x[0],x[1])):
            if node[3]=='E' and node[0]>t:continue
            if node[3]=='G' and node[0]<t:continue
            key=tuple(sorted(node[2].items()))
            if key not in seen:seen.add(key);unique.append(node)
        sol,rank=solve(unique,c['target']);maxrank=max(maxrank,rank)
        if sol is not None:
            h={k:v for k,v in c.items() if k not in ('nodes','target')}
            h.update(move_cut=t,nodes=len(unique),rank=rank,injections=[dict(cut=unique[j][0],receiver=unique[j][1],frame=unique[j][3],coefficient_mod=q) for j,q in sol.items()],target_nonzero=bool(c['target']))
            nominations.append(h);break
    stats['cut_systems']+=len(cuts)
    stats['intervals']+=1;stats['with_nodes']+=bool(c['nodes']);stats['max_rank']=max(stats['max_rank'],maxrank)
    if nominations:
        hits.append(nominations[0]);print('HIT',json.dumps(nominations[0]),flush=True)

result=dict(source_sha256=source_sha,source_name=source_name,modulus=MOD,scope='distributed E-before/G-after injections across extended constant-up-to-scale helper intervals; proper output and COPY-zero observables',source_validation=source_validation,stats=stats,hits=sorted(hits,key=lambda c:c['role']))
OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('DONE',dict(stats),'hits',len(hits),flush=True)
