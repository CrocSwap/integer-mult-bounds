#!/usr/bin/env python3
"""Conditional bit-network improvement by zero-loss stage-1/stage-3 reuse."""
from fractions import Fraction as Q
from itertools import combinations
import hashlib
import json
from pathlib import Path

from certify import (A, LOG_BOUND, Parameters, certify_parameters,
                     certify_rational_network, dyadic, network, require, verify_sources)
from search_network import log_integer_bounds

ROOT=Path(__file__).resolve().parents[1]
BIT_SAVING=Q(27,10**12)


def triple_matching(h):
    """Explicit bijection pi on triples with |T intersect pi(T)|=1; h even >=6.

    Pair consecutive ground points. With a full pair in T, keep its singleton
    and cycle the full pair among all pairs other than the singleton's pair.
    Otherwise keep the point in the least indexed pair and flip the other two.
    """
    require(h>=6 and h%2==0,'Need an even ground-set size at least six')
    triples=list(combinations(range(h),3))
    index={t:i for i,t in enumerate(triples)}
    images=[]
    for t in triples:
        groups=[x//2 for x in t]
        if len(set(groups))==3:
            keep=min(groups)
            image=tuple(sorted(x if x//2==keep else x^1 for x in t))
        else:
            full=next(g for g in groups if groups.count(g)==2)
            singleton=next(x for x in t if x//2!=full)
            cycle=[g for g in range(h//2) if g!=singleton//2]
            new=cycle[(cycle.index(full)+1)%len(cycle)]
            image=tuple(sorted((2*new,2*new+1,singleton)))
        require(len(set(t)&set(image))==1,'Matching is not an orthogonal pair')
        images.append(index[image])
    require(len(set(images))==len(triples),'Matching is not bijective')
    return triples,images


def counts(h=46):
    n=network(h)
    require(h%2==0,'Use the explicit even-h matching')
    merged=n['N']*n['zb']
    W=n['Wb']-merged
    s=n['sb']-merged*n['m']
    require(W*n['m']-s==n['N']-2*n['Lb'],'Rank deficit changed')
    return dict(h=h,m=n['m'],v=n['v'],N=n['N'],z=n['zb'],L=n['Lb'],
                old_W=n['Wb'],old_s=n['sb'],merged_roles=merged,W=W,s=s,
                eta=Q(W*n['m']-s,W*n['m']))


def parameters():
    a=BIT_SAVING
    return Parameters(1-a,1-A,Q(1,21),9*a/10,1-19*a*a/20,
                      1-9*a*a/10,dyadic(75),beta=Q(9,10))


def certificate():
    n=counts()
    triples,pi=triple_matching(46)
    log_lo,log_hi=log_integer_bounds(n['m'])
    require(log_hi<LOG_BOUND,'Log bound failed')
    require(n['eta']>BIT_SAVING*LOG_BOUND,'Insufficient bit saving')
    p=parameters()
    cert=certify_parameters(p,generalized_beta=True,strict_margin=True,
                            layout_model='nonadjacent')
    require(Q(cert['minimum_margin'])==3*BIT_SAVING**2/70,'Unexpected final margin')
    # Removed edges: E->F and 0->H. Added edge E->H, E subset H.
    m=n['m']; h=46
    removed_rank=(m-h)+(h*h-1)
    added_rank=h*h-1-h
    require(removed_rank-added_rank==m,'Wrong per-merge edge saving')
    return {
      'scope':'Conditional on the written stage-sharing proof and upstream algorithmic interfaces; not independent proof of the upstream theorem',
      'upstream_commit':verify_sources(),
      'bit_counts':{k:str(v) for k,v in n.items()},
      'bit_saving':str(BIT_SAVING),
      'log_m_upper':str(LOG_BOUND),'deficit_slack':str(n['eta']-BIT_SAVING*LOG_BOUND),
      'matching':{'h':46,'triples':len(triples),'distinct_images':len(set(pi)),
                  'all_intersections_one':True,
                  'image_index_sha256':hashlib.sha256(json.dumps(pi,separators=(',',':')).encode()).hexdigest()},
      'new_edge':{'tail_dimension':h,'head_dimension':h*h-1,
                  'rank':added_rank,'old_two_edge_rank':removed_rank,
                  'rank_reduction_per_merged_role':m},
      'complex_network_unchanged':certify_rational_network(),
      'witness':cert,
      'verification_boundary':'Scalar role reuse, frame nesting and all-role endpoint identity require the written proof; the certificate checks counts and parameter implications.'}


def scalar_model(h=6, seed=1):
    """Execute the entire shared-scratch scalar network at a small even h.

    Integer payload bits model many GF(2) inputs simultaneously. The side
    indexing is stage-specific and implements the role bijection in the proof.
    This is a finite scalar test, not an implementation of the tape algorithm.
    """
    triples,pi=triple_matching(h)
    v=len(triples); N=v**3
    neighbors=[[j for j,t in enumerate(triples) if len(set(s)&set(t))==1]
               for s in triples]
    z=len(neighbors[0])
    require(all(len(row)==z for row in neighbors),'Irregular neighbor graph')
    inverse=[0]*v
    for i,j in enumerate(pi):inverse[j]=i
    def payload(i):
        return ((i*2654435761+seed*2246822519) ^ (i*i*97)) & 0xffffffff
    X=[payload(i) for i in range(N)]
    Y=[payload(N+i) for i in range(N)]
    side0=[payload(2*N+i) for i in range(N*z)]
    side1=[payload(2*N+N*z+i) for i in range(N*z)]
    center=[payload(2*N+2*N*z+i) for i in range(3*v*v*h)]
    originals=[list(a) for a in (X,Y,side0,side1,center)]
    def flat(a,b,c):return (a*v+b)*v+c
    for stage in range(3):
        for a in range(v):
            for b in range(v):
                idx=[flat(t,a,b) if stage==0 else flat(a,t,b) if stage==1
                     else flat(a,b,t) for t in range(v)]
                bank=side1 if stage==1 else side0
                # Physical channel joins Y_S to X_T for all stages.
                edges=[]
                for S,row in enumerate(neighbors):
                    for j,T in enumerate(row):
                        k=(((a*v+b)*v+S)*z+j if stage<2 else
                           ((inverse[b]*v+S)*v+a)*z+j)
                        edges.append((S,T,k))
                cbase=(stage*v*v+a*v+b)*h
                def copy():
                    for S,T,k in edges:
                        bank[k] ^= Y[idx[S]] if stage==1 else X[idx[T]]
                def side():
                    for S,T,k in edges:
                        if stage==1:X[idx[T]] ^= bank[k]
                        else:Y[idx[S]] ^= bank[k]
                def gather():
                    source=Y if stage==1 else X
                    for t,coords in enumerate(triples):
                        value=source[idx[t]]
                        for q in coords:center[cbase+q] ^= value
                def scatter():
                    target=X if stage==1 else Y
                    for t,coords in enumerate(triples):
                        for q in coords:target[idx[t]] ^= center[cbase+q]
                ops=(side,scatter,copy,gather,scatter,side,gather,copy)
                for op in reversed(ops) if stage==1 else ops:op()
    require(X==originals[1] and Y==originals[0],'Scalar bank exchange failed')
    require([side0,side1,center]==originals[2:],'Arbitrary scratch not restored')
    return {'h':h,'data_roles':2*N,'shared_side_roles':2*N*z,
            'center_roles':3*v*v*h,'payload_bits':32,
            'bank_exchange':True,'scratch_restored':True}


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/stage-reuse.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS conditional stage-sharing witness 2^-75; minimum',result['witness']['minimum_margin'])
