#!/usr/bin/env python3
"""Deterministic exact-rational component descent from the pinned PR163 plan.

Only reads prerequisite inputs. Apache-2.0; prepared with OpenAI Codex.
"""
import argparse
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent

def build(root):
    base=root/'research/paired-cube-balanced-161'
    sys.path.insert(0,str(base/'bit'));sys.path.insert(0,str(base/'arithmetic'))
    from word import Candidate
    from interval_moment import log_interval,exp_interval
    c=Candidate([]);C=c.C;N=len(c.ops);h=c.h
    C.decoder();C.geometry();c.row()
    def canon(rows):
        out,_=c.module.reduce_rows(rows,h)
        return tuple(map(tuple,sorted(out,key=lambda r:next(i for i,x in enumerate(r) if x))))
    canonical={f:canon(B) for f,B in C.B.items()};known={b:f for f,b in canonical.items()}
    c.opframe=[known[canonical[f]] for f in c.opframe]
    starts={b:c.w['source_frame'][a] for a,b in c.source.items()}
    starts.update({b:z['frame'] for b,z in c.gauge.items()})
    prev=[None]*N;nxt=[[] for _ in range(N)];last={b:-f-1 for b,f in starts.items()};zero=c.register([])
    for i,(a,b,x) in enumerate(c.ops):
        prev[i]=[last.get(a,-zero-1),last.get(b,-zero-1)]
        for p in prev[i]:
            if p>=0:nxt[p].append(i)
        last[a]=last[b]=i
    for j,b in enumerate(c.w['rootroles']):
        if last[b]>=0:nxt[last[b]].append(-c.w['root_frame'][j]-1)
        last[b]=-c.w['root_frame'][j]-1
    for p in last.values():
        if p>=0:nxt[p].append(-c.w['full_frame']-1)
    assert all(len(x)==2 for x in nxt)
    a=Q(37165860768041,62500000000000000)
    power=[(Q(0),Q(0))]
    for r in range(1,h+1):
        lo,hi=log_interval(Q(r));el,eu=exp_interval(a*lo,a*hi);power.append((Q(r)/eu,Q(r)/el))
    def fid(n):return c.opframe[n] if n>=0 else -n-1
    def nondeg(B):
        ss=list(map(sum,B));M=[[9*sum(x*y for x,y in zip(u,v))-ss[i]*ss[j] for j,v in enumerate(B)] for i,u in enumerate(B)]
        return len(c.module.reduce_rows(M,len(B))[0])==len(B)
    accepted=[]
    for sweep in range(8):
        parent=list(range(N))
        def find(i):
            while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
            return i
        def union(i,j):
            i,j=find(i),find(j)
            if i!=j:parent[i]=j
        for i in range(N):
            for p in prev[i]:
                if p>=0 and c.opframe[p]==c.opframe[i]:union(i,p)
        groups=defaultdict(list)
        for i in range(N):groups[find(i)].append(i)
        count=0
        for group in sorted(groups.values(),key=lambda g:g[0]):
            fs=c.opframe[group[0]];d=C.dimf[fs]
            if d<=1:continue
            inside=set(group);incoming=[p for i in group for p in prev[i] if p not in inside]
            outgoing=[p for i in group for p in nxt[i] if p not in inside]
            lower=[fid(p) for p in incoming]
            if any(C.dimf[f]==d for f in lower):continue
            B=canon([v for f in sorted(set(lower)) for v in C.B[f]])
            if len(B)>=d:continue
            bits=0
            for i in group:bits|=C.sup[c.ops[i][2]]
            while bits and len(B)<d:
                low=bits&-bits;bits-=low;B=canon(list(B)+[C.chi[low.bit_length()-1]])
            if len(B)>=d:continue
            choices=[B]
            if not nondeg(B):
                choices=[]
                for v in C.B[fs]:
                    BB=canon(list(B)+[v])
                    if len(BB)<d and nondeg(BB):choices.append(BB)
            if not choices:continue
            B=min(choices,key=len);nd=len(B)
            old=[d-C.dimf[f] for f in lower]+[C.dimf[fid(p)]-d for p in outgoing]
            new=[nd-C.dimf[f] for f in lower]+[C.dimf[fid(p)]-nd for p in outgoing]
            gain_lower=sum(power[r][0] for r in old)-sum(power[r][1] for r in new)
            if gain_lower<=0:continue
            f=c.register(B)
            assert C.sub(f,fs) and all(C.sub(z,f) for z in lower) and all(C.sub(f,fid(z)) for z in outgoing)
            for i in group:c.opframe[i]=f
            count+=1;accepted.append(dict(operations=group,old_dimension=d,new_dimension=nd))
        print('exact descent sweep',sweep,'accepted components',count,file=sys.stderr,flush=True)
        if not count:break
    else:raise ValueError('descent did not stabilize in the stated sweep bound')
    changed=[i for i in range(N) if not(C.sub(c.opframe[i],c.nf[c.ops[i][2]]) and C.sub(c.nf[c.ops[i][2]],c.opframe[i]))]
    c.row()
    return dict(p=12,frames=[[i,C.B[c.opframe[i]]] for i in changed],provenance=dict(
        prerequisite='PR163 paired-cube-balanced-161',
        prerequisite_manifest_sha256=sha256((base/'SOURCE.json').read_bytes()).hexdigest(),
        prerequisite_descent_sha256=sha256((base/'bit/descent.json').read_bytes()).hexdigest(),
        trial_saving=str(a),accepted_components=accepted,
        rule='Exact interval improvement of the complete boundary child cost after lowering equal-frame components; no optimality claim.'))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=HERE.parents[1]);p.add_argument('--write',action='store_true');args=p.parse_args()
    assert not sys.flags.optimize
    plan=json.loads(json.dumps(build(args.source)));path=HERE/'descent.json'
    if args.write:path.write_text(json.dumps(plan,separators=(',',':'),sort_keys=True)+'\n')
    else:assert plan==json.loads(path.read_text()),'Deterministic frame plan changed'
    print('PASS deterministic exact frame plan:',len(plan['frames']),'operations')

if __name__=='__main__':main()
