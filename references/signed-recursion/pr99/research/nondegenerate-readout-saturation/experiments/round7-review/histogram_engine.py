#!/usr/bin/env python3
"""Independent round-seven histogram reconstruction and safe readout ablations.

No upstream implementation is imported. Frame dimensions are frozen inputs;
the separate exact frame check is needed to qualify the original construction.
An ablation moves chosen deferred garbage readouts to frame zero and keeps all
V releases unchanged. Its remaining target chains are subsequences of the
original nested chains, so containment is preserved. New high-rank steps still
need the generic-pivot check before qualification.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from itertools import combinations
import json
from math import comb, exp, log
from pathlib import Path
import random
import time

import check_arithmetic as ar
from scalar_engine import coefficients, load_schedule

HERE=Path(__file__).resolve().parent


def load(path):
    with gzip.open(path,'rt') as f:return json.load(f)


def inner(r,h):
    assert 0<=r<=h
    if 2*r<=h:return Counter({1:r})
    out=Counter({1:h-r});out[2*r-h]+=1
    return out


def add(H,profile,mult):
    for w,n in profile.items():
        if n:H[w]+=n*mult


def chains(W,D):
    args={int(n):a for n,a in W['args'].items()}
    late={int(n):el for n,el in W['late'].items()}
    nd=dict(D['node_dims']);ld={(n,tuple(suffix)):d for n,suffix,d in D['late_dims']}
    vd={s:len(B) for s,B in zip(D['vleaf_slots'],D['vleaf_start'])}
    sd={s:len(B) for s,B in zip(D['readout_order'],D['sigma'])}
    piv={op[3]:op[1] for op in D['ops'] if op[0]=='add'}
    roots={s:D['h']-1 for s,*_ in D['out']+D['ret']}
    cc=[]
    for s,hold in enumerate(D['hold']):
        n=hold[0]
        if args[n] is None:d=vd[s]
        else:
            k=D['start'][s][2];dec=late.get(n)
            d=nd[n] if dec is None or k in dec[0] else ld[n,tuple(dec[1][dec[1].index(k):])]
        ds=[sd.get(s,0),d]
        for i,n in enumerate(hold):
            if i:ds.append(nd[n])
            if args[n] is not None and piv.get(n)==s and n in late:
                suffix=late[n][1]
                ds.extend(ld[n,tuple(suffix[i:])] for i in range(len(suffix)-1))
        if s in roots:ds.append(roots[s])
        ds.append(D['h'])
        assert all(b>=a for a,b in zip(ds,ds[1:])),(s,ds)
        cc.append(ds)
    return cc,sd,vd


def histogram(W,D,cov,removed=(),stair=True,prepared=None):
    h,R=D['h'],D['R'];v=comb(h,3);m=h*h;N=v*v;Wc=2*N+2*v*R
    cc,sd,vd=prepared or chains(W,D);removed=set(removed)
    sf={s:f for s,f in sd.items() if f not in removed}
    parts={name:Counter() for name in ('auxiliary','slot_corners','slot_chains','centre','targets','sources','entrance','copy_correction')}
    rk=Counter()
    for s,ds0 in enumerate(cc):
        ds=[sf.get(s,0)]+ds0[1:]
        for a,b in zip(ds,ds[1:]):rk[b-a]+=1
        r=h-sf.get(s,0)
        parts['auxiliary'][m-2*r]+=2*v
        add(parts['slot_corners'],inner(r,h),2*v)
    for r,n in rk.items():add(parts['slot_chains'],inner(r,h),2*v*n)
    add(parts['centre'],inner(h-1,h),2*v*h)
    levels=[set() for _ in range(v)]
    for s,f in sf.items():
        for t in cov[s]:levels[t].add(f)
    for lev in levels:
        ds=sorted(lev|{0,h-1})
        for a,b in zip(ds,ds[1:]):add(parts['targets'],inner(b-a,h),2*v)
    for n,slots in D['xs_order']:
        ds=[1]+[vd[s] for s in slots]+[h]
        assert all(b>=a for a,b in zip(ds,ds[1:]))
        for a,b in zip(ds,ds[1:]):add(parts['sources'],inner(b-a,h),2*v)
    parts['entrance'][m-4*h+2]+=2*N
    for w in ([h-2,h-5]+[1]*6 if stair else [h-2]+[1]*(h+1)):parts['entrance'][w]+=2*N
    parts['copy_correction'][1]+=N
    H=sum(parts.values(),Counter());H={w:n for w,n in H.items() if n}
    L=2*v*h*(h-1);s=Wc*m-N+L
    assert sum(w*n for w,n in H.items())==s
    c=dict(h=h,m=m,v=v,N=N,W=Wc,L=L,s=s,R=R,hist=[list(p) for p in sorted(H.items())])
    return c,parts


def float_root(c):
    lo,hi=0.,.001
    for _ in range(55):
        a=(lo+hi)/2
        f=sum(n*w/c['m']/c['W']*exp(a*log(c['m']/w)) for w,n in c['hist'])
        if f<1:lo=a
        else:hi=a
    return (lo+hi)/2


def summary(c,parts):
    return dict(root_float=float_root(c),weighted_log_cost=sum(n*w/c['m']/c['W']*log(c['m']/w) for w,n in c['hist']),
        child_occurrences=sum(n for w,n in c['hist']),
        components={name:dict(rank=sum(w*n for w,n in H.items()),children=sum(H.values()),
            weighted_log_cost=sum(n*w/c['m']/c['W']*log(c['m']/w) for w,n in H.items()),hist=sorted(H.items())) for name,H in parts.items()})


class FastAblations:
    """Compressed exact histograms: dimension classes plus target level masks."""
    def __init__(self,W,D,cov,prepared):
        self.D=D;h=D['h'];v=comb(h,3);self.h=h;self.v=v
        cc,sd,vd=prepared;self.dims=sorted(set(sd.values()))
        self.bit={f:1<<i for i,f in enumerate(self.dims)}
        c,parts=histogram(W,D,cov,prepared=prepared);self.c=c
        self.fixed=Counter(dict(c['hist']));self.fixed.subtract(parts['targets'])
        self.delta={f:Counter() for f in self.dims}
        for s,f in sd.items():
            dd=self.delta[f];dd[h*h-2*h]+=2*v;dd[h*h-2*(h-f)]-=2*v
            add(dd,inner(h,h),2*v);add(dd,inner(h-f,h),-2*v)
            first=cc[s][1];add(dd,inner(first,h),2*v);add(dd,inner(first-f,h),-2*v)
        levels=[0]*v
        for s,f in sd.items():
            for t in cov[s]:levels[t]|=self.bit[f]
        self.patterns=Counter(levels);self.ycache={}
        self.gap={r:inner(r,h) for r in range(h+1)}
    def mask(self,rem):return sum(self.bit[f] for f in rem)
    def removed(self,mask):return [f for f in self.dims if mask&self.bit[f]]
    def yprofile(self,mask):
        if mask not in self.ycache:
            ds=[0]+[f for f in self.dims if mask&self.bit[f] and f!=self.h-1]+[self.h-1]
            out=Counter()
            for a,b in zip(ds,ds[1:]):add(out,self.gap[b-a],2*self.v)
            self.ycache[mask]=out
        return self.ycache[mask]
    def profile(self,removedmask):
        H=self.fixed.copy()
        for f in self.removed(removedmask):H.update(self.delta[f])
        for mask,n in self.patterns.items():H.update({w:c*n for w,c in self.yprofile(mask&~removedmask).items()})
        return {w:n for w,n in H.items() if n}
    def measure(self,H,a):
        return sum(n*w/self.c['m']/self.c['W']*exp(a*log(self.c['m']/w)) for w,n in H.items())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,default=HERE/'vendor/certificates/round7/deferred_23.json.gz')
    ap.add_argument('--witness',type=Path,default=HERE/'vendor/certificates/round7/witness_23.json.gz');ap.add_argument('--search',action='store_true')
    ap.add_argument('--random-trials',type=int,default=10000)
    args=ap.parse_args();tic=time.time();W,D=load(args.witness),load(args.data);ss=load_schedule(args.data);cov=coefficients(ss);prepared=chains(W,D)
    upstream=json.loads((HERE/'vendor/lean/round7-histograms.json').read_text());rows={}
    for key,stair in [('bit',True),('bitplain',False)]:
        c,parts=histogram(W,D,cov,stair=stair,prepared=prepared)
        for k in ('m','W','s','hist'):assert c[k]==upstream[key][k],(key,k,c[k],upstream[key][k])
        a=Q(*upstream[key]['a']);lo,hi=ar.exact_moment(c,a);assert hi<1
        rows[key]=dict(summary(c,parts),histogram=c,certified_saving=str(a),exact_moment_upper=float(hi),matches_published=True)
    if args.search:
        fast=FastAblations(W,D,cov,prepared);dims=fast.dims;trials=[];best=rows['bit']['root_float'];bestset=[]
        for rem in ([],dims,dims[::2],dims[1::2],[dims[0]]):
            slow,_=histogram(W,D,cov,rem,prepared=prepared)
            assert fast.profile(fast.mask(rem))==dict(slow['hist'])
        # Every singleton removal, every prefix/suffix, and greedy local search.
        sets={tuple([d]) for d in dims}|{tuple(dims[:i]) for i in range(len(dims)+1)}|{tuple(dims[i:]) for i in range(len(dims)+1)}
        def trial(rem):
            H=fast.profile(fast.mask(rem));c=dict(fast.c,hist=sorted(H.items()));r=float_root(c)
            assert sum(w*n for w,n in c['hist'])==c['s']
            return dict(removed_dimensions=list(rem),root_float=r,
                weighted_log_cost=sum(n*w/c['m']/c['W']*log(c['m']/w) for w,n in c['hist']))
        cache={}
        for rem in sorted(sets):
            row=trial(rem);cache[rem]=row;trials.append(row)
            if row['root_float']>best:best=row['root_float'];bestset=list(rem)
        while True:
            improved=False
            for d in dims:
                rem=tuple(sorted(set(bestset)^{d}))
                row=cache.get(rem)
                if row is None:row=trial(rem);cache[rem]=row;trials.append(row)
                if row['root_float']>best+1e-15:best=row['root_float'];bestset=list(rem);improved=True;break
            if not improved:break
        rng=random.Random(20261009);base_a=rows['bit']['root_float'];top=[];seen=set(cache)
        for i in range(args.random_trials):
            # Dense, sparse, and uniform masks; independently reproducible seed.
            p=(rng.random() if i%3==0 else .5 if i%3==1 else .05)
            rem=tuple(f for f in dims if rng.random()<p)
            if rem in seen:continue
            seen.add(rem);H=fast.profile(fast.mask(rem));score=fast.measure(H,base_a)
            top.append((score,rem))
            if len(top)>40:top=sorted(top)[:20]
        for score,rem in sorted(top)[:20]:
            row=trial(rem);cache[rem]=row;trials.append(row)
            if row['root_float']>best:best=row['root_float'];bestset=list(rem)
        rows['ablations']=dict(trials=trials,distinct_physical_profiles_tested=len(seen),random_seed=20261009,
            target_level_patterns=len(fast.patterns),best_removed_dimensions=bestset,best_root_float=best,
            base_root_float=rows['bit']['root_float'],qualified_new_physical_witness=False,
            reason='Any nontrivial ablation needs the new high-rank generic-pivot check; V release order preserved.')
    rows['seconds']=time.time()-tic;(HERE/'histogram-results.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps({k:({kk:vv for kk,vv in val.items() if kk not in ('histogram','components','trials')} if isinstance(val,dict) else val) for k,val in rows.items()},indent=2),flush=True)


if __name__=='__main__':main()
