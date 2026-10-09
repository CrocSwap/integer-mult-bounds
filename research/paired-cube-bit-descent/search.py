#!/usr/bin/env python3
"""Exact paid-moment descent and ascent along causal operation-frame closures.

Search is untrusted; verify.py independently checks its exported finite word.
Apache-2.0; prepared with OpenAI Codex.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
import word
from interval_moment import log_interval,exp_interval

HERE=Path(__file__).resolve().parent
TRIAL=Q(1,1600)

def build(root):
    word.BASE=root/'research/paired-cube-bit'
    initial=json.loads((HERE/'initial.json').read_text())
    c=word.Candidate(plan=initial);C=c.C;h=c.h;N=len(c.ops)
    C.decoder();C.geometry();c.exact_frames();before=c.row()
    def canon(rows):
        out,_=c.module.reduce_rows(rows,h)
        return tuple(map(tuple,sorted(out,key=lambda r:next(i for i,x in enumerate(r) if x))))
    canonical={f:canon(B) for f,B in C.B.items()};known={B:f for f,B in canonical.items()}
    c.opframe=[known[canonical[f]] for f in c.opframe]
    c.frame_ids=dict(known)
    start={b:c.w['source_frame'][a] for a,b in c.source.items()}
    start.update({b:z['frame'] for b,z in c.gauge.items()})
    prev=[None]*N;nxt=[[] for _ in range(N)];last={b:-f-1 for b,f in start.items()};zero=c.register([])
    for i,(a,b,_) in enumerate(c.ops):
        prev[i]=[last.get(a,-zero-1),last.get(b,-zero-1)]
        for p in prev[i]:
            if p>=0:nxt[p].append(i)
        last[a]=last[b]=i
    for j,b in enumerate(c.w['rootroles']):
        if last[b]>=0:nxt[last[b]].append(-c.w['root_frame'][j]-1)
        last[b]=-c.w['root_frame'][j]-1
    for p in last.values():
        if p>=0:nxt[p].append(-c.w['full_frame']-1)
    assert all(len(v)==2 for v in nxt)
    power=[(Q(0),Q(0))]
    for r in range(1,h+1):
        lo,hi=log_interval(Q(r));el,eu=exp_interval(TRIAL*lo,TRIAL*hi)
        power.append((Q(r)/eu,Q(r)/el))
    fallback=Q(32*(3*h)**2,10**16)
    def fid(n):return c.opframe[n] if n>=0 else -n-1
    def closure(i,edges):
        f=c.opframe[i];s=set();todo=[i]
        while todo:
            j=todo.pop()
            if j in s:continue
            s.add(j);todo.extend(p for p in edges[j] if p>=0 and c.opframe[p]==f)
        return sorted(s)
    def nondeg(B):
        return C.nondeg(c.register(B))
    support_cache={}
    def support_basis(bits):
        if bits not in support_cache:
            vectors=[];remaining=bits
            while remaining:
                low=remaining&-remaining;remaining-=low;vectors.append(C.chi[low.bit_length()-1])
            support_cache[bits]=canon(vectors)
        return support_cache[bits]
    accepted=[];sweeps=[]
    for sweep in range(8):
        sweep_count=0
        for direction in ('down','up'):
            counts=Counter();seen=set();edges=prev if direction=='down' else nxt
            order=range(N) if direction=='down' else reversed(range(N))
            for i in order:
                group=closure(i,edges);key=tuple(group)
                if key in seen:continue
                seen.add(key);counts['tested_closures']+=1
                fs=c.opframe[i];d=C.dimf[fs];inside=set(group)
                incoming=[p for j in group for p in prev[j] if p not in inside]
                outgoing=[p for j in group for p in nxt[j] if p not in inside]
                lower=[fid(p) for p in incoming];upper=[fid(p) for p in outgoing]
                if direction=='down':
                    if any(C.dimf[f]==d for f in lower):continue
                    B=canon([v for f in sorted(set(lower)) for v in C.B[f]])
                    if len(B)>=d:continue
                    bits=0
                    for j in group:bits|=C.sup[c.ops[j][2]]
                    B=canon(list(B)+list(support_basis(bits)))
                    if len(B)>=d:continue
                    choices=[B] if nondeg(B) else [BB for v in C.B[fs]
                        if len(BB:=canon(list(B)+[v]))<d and nondeg(BB)]
                else:
                    if any(C.dimf[f]==d for f in upper):continue
                    B=canon(c.module.kernel([v for f in sorted(set(upper)) for v in C.A[f]],h)[0])
                    if len(B)<=d:continue
                    choices=[B] if nondeg(B) else [BB for v in B
                        if len(BB:=canon(list(C.B[fs])+[v]))>d and nondeg(BB)]
                counts['geometrically_movable']+=1
                if not choices:continue
                B=(min if direction=='down' else max)(choices,key=len);nd=len(B)
                old=[d-C.dimf[f] for f in lower]+[C.dimf[f]-d for f in upper]
                new=[nd-C.dimf[f] for f in lower]+[C.dimf[f]-nd for f in upper]
                # Each boundary jump produces three children. The common factor
                # 3*m**a/(W*m) is positive and cancels; pay the changed fallback.
                gain=sum(power[r][0] for r in old)-sum(power[r][1] for r in new)
                gain+=fallback*(sum(r>0 for r in old)-sum(r>0 for r in new))
                if gain<=0:continue
                f=c.register(B)
                assert (C.sub(f,fs) if direction=='down' else C.sub(fs,f))
                assert all(C.sub(z,f) for z in lower) and all(C.sub(f,z) for z in upper)
                for j in group:c.opframe[j]=f
                counts['accepted']+=1;sweep_count+=1
                accepted.append(dict(direction=direction,operations=group,old_dimension=d,
                                     new_dimension=nd,paid_gain_lower=str(gain)))
            sweeps.append(dict(sweep=sweep,direction=direction,**counts))
            print('frame search',sweep,direction,dict(counts),file=sys.stderr,flush=True)
        if not sweep_count:break
    else:raise ValueError('Search did not stabilize in eight sweeps')
    changed=[i for i in range(N) if not(C.sub(c.opframe[i],c.nf[c.ops[i][2]])
               and C.sub(c.nf[c.ops[i][2]],c.opframe[i]))]
    c.changed_frames=changed;c.row()
    return dict(p=12,frames=[[i,C.B[c.opframe[i]]] for i in changed],provenance=dict(
        initial_sha256=sha256((HERE/'initial.json').read_bytes()).hexdigest(),trial_saving=str(TRIAL),
        accepted=accepted,sweeps=sweeps,rule='Exact complete boundary child moment including changed 1e-16 fallback bill; causal prefixes and suffixes; no optimality claim.'))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=HERE.parents[1])
    p.add_argument('--write',action='store_true');args=p.parse_args();assert not sys.flags.optimize
    record=json.loads(json.dumps(build(args.source)));target=HERE/'frames.json'
    if args.write:target.write_text(json.dumps(record,separators=(',',':'),sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:assert record==json.loads(target.read_text()),'Deterministic frame search changed'
    print('PASS deterministic paid frame search:',len(record['frames']),'changed operations')

if __name__=='__main__':main()
