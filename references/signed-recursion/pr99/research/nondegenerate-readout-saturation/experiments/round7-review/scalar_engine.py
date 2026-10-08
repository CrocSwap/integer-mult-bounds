#!/usr/bin/env python3
"""Independent exact linear replay of the deferred-readout word.

Packed bits carry every data and arbitrary-dirty scratch basis vector at once.
No vendor implementation is imported. This verifies the finite scalar F2 word;
frame containment, projector ranks and all-size tape compilation are separate.
"""
import argparse
from collections import defaultdict
import gzip
from itertools import combinations
import json
from pathlib import Path
import random
import time


def load_schedule(path):
    with gzip.open(path, 'rt') as f:
        d = json.load(f)
    h, R = d['h'], d['R']
    trip = list(combinations(range(h), 3)); tid = {t:i for i,t in enumerate(trip)}
    return dict(h=h, R=R, v=len(trip), trip=trip, ops=d['ops'],
                out={s:tid[tuple(t)] for s,c,t in d['out']}, ret={s:c for s,c in d['ret']},
                deferred=d['readout_order'], late_v=d['deferred_v_order'],
                early_v=[s for n,us in d['xs_order'] for s in us if s not in set(d['deferred_v_order'])])


def touches(op):
    return op[1:3] if op[0]=='add' else [op[1]]+op[2] if op[0]=='fan' else []


def closure(s):
    previous, pred, last = {}, {}, {}
    for i,op in enumerate(s['ops']):
        pred[i] = []
        for u in touches(op):
            if u in previous: pred[i].append(previous[u])
            previous[u]=i; last[u]=i
    stack = [last[u] for u in s['ret']]; phase=set()
    while stack:
        i=stack.pop()
        if i not in phase: phase.add(i); stack.extend(pred[i])
    return phase


def coefficients(s):
    """Compute the exact integer transpose-sweep C=J L independently."""
    c=[{} for _ in range(s['R'])]
    for u,t in s['out'].items(): c[u][t]=c[u].get(t,0)+1
    for u,q in s['ret'].items():
        for t,T in enumerate(s['trip']):
            if q in T: c[u][t]=c[u].get(t,0)+1
    for op in reversed(s['ops']):
        if op[0]=='add': pairs=[(op[2],op[1])]
        elif op[0]=='fan': pairs=[(op[1],g) for g in op[2]]
        else: continue
        for dst,src in pairs:
            for t,a in c[src].items(): c[dst][t]=c[dst].get(t,0)+a
    return c


def replay(s, c, control=None, ring=2, seed=0):
    """F2: entire linear map; Z: independent integer samples, explicitly labeled."""
    v,R=s['v'],s['R']; sel=set(s['deferred']); src={o[1]:o[2]-1 for o in s['ops'] if o[0]=='src'}
    phase=closure(s)
    assert not any(sel.intersection(touches(s['ops'][i])) for i in phase)
    assert set(s['late_v']) == sel.intersection(src)
    ph1=[i for i,o in enumerate(s['ops']) if i in phase and o[0]!='src']
    rest=[i for i,o in enumerate(s['ops']) if i not in phase and o[0]!='src']
    if ring==2:
        x=[1<<i for i in range(v)]; a0=[1<<(v+i) for i in range(R)]
    else:
        rng=random.Random(seed); x=[rng.randrange(-100,101) for _ in range(v)]
        a0=[rng.randrange(-100,101) for _ in range(R)]
    a=a0[:]; y=[0]*v
    def add(dst,idx,value,sgn=1):
        if ring==2: dst[idx]^=value
        else: dst[idx]+=sgn*value
    def read(u):
        for t,k in c[u].items():
            if control=='drop_readout' and u==s['deferred'][0] and t==min(c[u]): continue
            if ring==2:
                if k&1: y[t]^=a[u]
            else: y[t]-=k*a[u]
    def op_run(op,inverse=False):
        if op[0]=='add': add(a,op[1],a[op[2]],-1 if inverse else 1)
        elif op[0]=='fan':
            for g in op[2]: add(a,g,a[op[1]],-1 if inverse else 1)
    for u in range(R):
        if u not in sel: read(u)
    for u in s['early_v']: add(a,u,x[src[u]])
    if control=='V_before_readout': add(a,s['late_v'][0],x[src[s['late_v'][0]]])
    for i in ph1: op_run(s['ops'][i])
    for u,q in s['ret'].items():
        for t,T in enumerate(s['trip']):
            if q in T: add(y,t,a[u])
    for u in s['deferred']: read(u)
    for u in s['late_v']:
        if control=='V_before_readout' and u==s['late_v'][0]: continue
        add(a,u,x[src[u]])
    for i in rest: op_run(s['ops'][i])
    for u,t in s['out'].items(): add(y,t,a[u])
    done=ph1+rest
    for i in reversed(done): op_run(s['ops'][i],True)
    for u,n in src.items(): add(a,u,x[n],-1)
    dirty_bad=sum(p!=q for p,q in zip(a,a0))
    if ring==2: want=x
    else:
        want=[sum((int(len(set(S)&set(T))==1)+len(set(S)&set(T)))*x[j]
                  for j,S in enumerate(s['trip'])) for T in s['trip']]
    output_bad=sum(p!=q for p,q in zip(y,want))
    return dict(ok=dirty_bad==output_bad==0, dirty_failures=dirty_bad,
                output_failures=output_bad, basis_columns=v+R if ring==2 else None,
                phase1_ops=len(ph1), rest_ops=len(rest), deferred_slots=len(sel))


def small_schedule(h):
    """Independent simple producer. Each root sums private leaf-use slots.

    This deliberately small fixture tests arbitrary dirty scratch and per-use V
    release. It does not claim the community producer's role count or exponent.
    """
    trip=list(combinations(range(h),3)); v=len(trip); ops=[]; out={};ret={}; R=0
    def root(indices):
        nonlocal R
        slots=[]
        for i in indices: slots.append(R);ops.append(['src',R,i+1]);R+=1
        assert slots
        p=slots[0]
        for u in slots[1:]: ops.append(['add',p,u,None])
        return p
    for t,T in enumerate(trip):
        for q in T:
            out[root([i for i,S in enumerate(trip) if set(S)&set(T)=={q}])]=t
    for q in range(h): ret[root([i for i,S in enumerate(trip) if q in S])]=q
    s=dict(h=h,v=v,R=R,trip=trip,ops=ops,out=out,ret=ret)
    ph=closure(s); touched={u for i in ph for u in touches(ops[i])}
    s['deferred']=[u for u in range(R) if u not in touched]
    s['late_v']=s['deferred'][:]; s['early_v']=[u for u in range(R) if u in touched]
    return s


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path)
    ap.add_argument('--small',action='store_true');ap.add_argument('--output',type=Path)
    args=ap.parse_args();results=[]
    before=None
    if args.data is not None:
        import audit_evidence
        before=audit_evidence.snapshot('scalar',args.data)
    ss=[small_schedule(h) for h in range(5,10)] if args.small else [load_schedule(args.data)]
    for s in ss:
        tic=time.time();c=coefficients(s)
        r=replay(s,c); assert r['ok'],r
        controls={k:replay(s,c,k) for k in ('drop_readout','V_before_readout')}
        assert all(not x['ok'] for x in controls.values())
        z=[replay(s,c,ring=0,seed=j) for j in range(4)];assert all(x['ok'] for x in z)
        row=dict(h=s['h'],R=s['R'],v=s['v'],ops=len(s['ops']),
                 exact_F2=r,integer_random_trials=4,negative_controls=controls,
                 integer_readout_entries=sum(map(len,c)),seconds=time.time()-tic)
        results.append(row);print(json.dumps(row),flush=True)
    if args.output: args.output.write_text(json.dumps(results,indent=2)+'\n')
    if before is not None:
        checks=dict(full_basis=all(r['exact_F2']['ok'] for r in results),
            scratch_restored=all(r['exact_F2']['dirty_failures']==0 for r in results),
            outputs_exact=all(r['exact_F2']['output_failures']==0 for r in results),
            negative_controls_detected=all(not c['ok'] for r in results for c in r['negative_controls'].values()),
            integer_samples=all(r['integer_random_trials']==4 for r in results))
        audit_evidence.record('scalar',args.data,before,checks,[args.output] if args.output else [])


if __name__=='__main__': main()
