#!/usr/bin/env python3
"""Independent exact profile/moment reconstruction for changed binary DAGs.

Two-stage physical classes, copied centers and ordinary profiles are adopted
from icekylinx PR36. Reversed (h,h+2) data corners are James Chang PR34,
specialized in Rohan Arun PR37. This checker changes the producer records,
reconstructs every charged class and independently encloses logarithms and
exponentials. The separately pinned balanced assembly is attributed upstream.
Arithmetic acceptance does not establish producer/frame correctness.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import importlib.util
import json
from math import comb
from pathlib import Path


def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [js(v) for v in x]
    return x


def read(p):
    return json.loads(Path(p).read_text())


def local(row):
    h,R=row['h'],row['R'];hist=list(row['histogram'])
    assert row['v']==comb(h,3) and row['loss']==h*(h-1)
    assert R==row['c']+row['q']-row.get('matched',row.get('matching',0))
    assert len(hist)==h+1 and min(hist)>=0 and hist[h]>=h
    assert sum(r*n for r,n in enumerate(hist))==h*R+2*row['loss']
    hist[1]+=h;hist[h]-=h
    assert sum(r*n for r,n in enumerate(hist))==h*R+row['loss']
    return hist


def reconstruct(rows,phase=False):
    a,b=[r['h'] for r in rows];m=a*b;N=rows[0]['v']*rows[1]['v']
    banks=[N//r['v']*r['R'] for r in rows];W=2*N+sum(banks)
    L=sum(N//r['v']*r['loss'] for r in rows);parts={}
    for k,(row,B) in enumerate(zip(rows,banks)):
        h=row['h'];count=N//row['v'];internal=Counter()
        for rank,n in enumerate(local(row)):
            if not rank or not n:continue
            if phase:internal[rank]+=count*n
            elif 2*rank<=h:internal[1]+=count*n*rank
            else:internal[1]+=count*n*(h-rank);internal[2*rank-h]+=count*n
        parts[f'local_{k}']=+internal
        parts[f'exterior_{k}']=Counter({m-h:B}) if phase else Counter({h:B,m-2*h:B})
        parts[f'growth_{k}']=Counter({h-1:2*N}) if phase else Counter({1:2*N,h-2:2*N})
    if phase:parts['data']=Counter({(a-1)*(b-1):2*N})
    else:
        assert b==a+2 and a>=7
        d=a+b-1
        parts['data']=Counter({1:18*N,a-2:2*N,a-6:2*N,m-2*d:2*N})
    parts['paid_endpoint']=Counter({1:N})
    hist=sum(parts.values(),Counter());hist={t:n for t,n in sorted(hist.items()) if n}
    s=sum(t*n for t,n in hist.items());assert s==W*m-N+L
    assert all(0<t<m and n>0 for t,n in hist.items())
    return dict(dimensions=[a,b],m=m,N=N,banks=banks,W=W,L=L,total_rank=s,
                deficit=N-L,maxchild=max(hist),parts=parts,child_multiplicities=hist)


@lru_cache(None)
def logs(x):
    x=Q(x);k=0
    while x>2:x/=2;k+=1
    def small(y):
        z=(y-1)/(y+1)
        lo=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(40)),Q())
        return lo,lo+2*z**81/(81*(1-z*z))
    lo,hi=small(x);l2,h2=small(Q(2));lo+=k*l2;hi+=k*h2
    scale=10**40
    return Q((lo*scale).numerator//(lo*scale).denominator,scale),Q(-(-(hi*scale).numerator//(hi*scale).denominator),scale)


def moment(profile,a):
    lo=Q();hi=Q()
    for t,n in profile['child_multiplicities'].items():
        lower,upper=logs(Q(profile['m'],t));u,v=a*lower,a*upper
        assert 0<=u<=v<1
        elo=sum((u**j/Q([1,1,2,6,24,120][j]) for j in range(6)),Q())
        ehi=1+v+v*v/2+v**3/6+v**4/(24*(1-v/5))
        weight=Q(n*t,profile['m']*profile['W']);lo+=weight*elo;hi+=weight*ehi
    return dict(saving=a,lower=lo,upper=hi,strict_gap=1-hi)


def choose(profile):
    grid=10**14;low,high=0,10**11
    while high-low>1:
        mid=(low+high)//2
        if moment(profile,Q(mid,grid))['upper']<1:low=mid
        else:high=mid
    exact=moment(profile,Q(low,grid));nxt=moment(profile,Q(high,grid))
    assert exact['strict_gap']>0
    return dict(**exact,next_grid=high,next_grid_lower=nxt['lower'],next_grid_upper=nxt['upper'],
                next_grid_excluded=nxt['lower']>1,grid=grid)


def degree(m,r):
    d=1
    while m**d<=2*r**d:d+=1
    return d


def bridge(bit,phase,phase_rows):
    m,W,s,N=[phase[k] for k in ('m','W','total_rank','N')]
    terms=[]
    for row in phase_rows:
        h,v,c=[row[k] for k in ('h','v','c')]
        upper=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8
        terms.append(dict(h=h,v=v,c=c,invocations=N//v,local_group_upper=upper,copied_center_extra_groups=2*h))
    G=N+sum(t['invocations']*(t['local_group_upper']+t['copied_center_extra_groups']) for t in terms)
    E=64*(W+m+G+1)**3;B=s+E;literal=2*G*W*W+8*s+4*W+4+32*m
    bits={}
    for name,row in (('bit',bit),('complex',phase)):
        bits[name]=dict(m=row['m'],W=row['W'],maxchild=row['maxchild'],halving_degree=degree(row['m'],row['maxchild']),wire_bits=row['W'].bit_length())
    bits['complex'].update(s=s,scalar_group_upper=G,scalar_terms=terms)
    coefficient=sum(row['halving_degree']*row['wire_bits'] for row in bits.values())
    stock=1000*((coefficient*51)//25000+1)
    return dict(**bits,semantic=dict(E=E,B=B,C0=32*m*B*B,C1=1,literal_charge=literal,
                strict_literal_gap=E-literal,induction_gap=2*B*(m-phase['maxchild'])-s-E),
                rows=dict(coefficient=coefficient,degree=stock,degree_gap=stock-Q(51,25)*coefficient,suffix_slope=4*stock))


def main():
    p=argparse.ArgumentParser();p.add_argument('--axes',type=Path,required=True)
    p.add_argument('--phase',type=Path,required=True);p.add_argument('--assembly',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    axes=read(args.axes);phase_input=read(args.phase)
    bit=reconstruct(axes);phase=reconstruct([phase_input,phase_input],True)
    bm=choose(bit);cm=moment(phase,Q(717,10**7));assert cm['strict_gap']>0
    f=bridge(bit,phase,[phase_input,phase_input])
    sp=importlib.util.spec_from_file_location('pinned_balanced',args.assembly);assembly=importlib.util.module_from_spec(sp);sp.loader.exec_module(assembly)
    a=bm['saving'];h=Q(1,10**12);q=a*(1-2*h);margin=(1-h)*q/(1+q)
    k=Q((margin*10**14).numerator//(margin*10**14).denominator,10**14)
    assert k<margin
    assembled=assembly.assembly(f,a,k);eventual=assembly.cutoffs(f,assembled)
    result=dict(status='Exact complete conditional arithmetic; changed finite producer/frame acceptance separate',
        bit=bit,phase=phase,bit_moment=bm,phase_moment=cm,finite_bridge=f,
        assembly=assembled,eventual=eventual,kappa=k,previous_PR37=Q(3850771033,10**14),
        ratio_to_PR37=k/Q(3850771033,10**14),input_sha256={str(v):sha256(v.read_bytes()).hexdigest() for v in (args.axes,args.phase,args.assembly)},
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Adopts credited PR34/36/37 interfaces; no formal verification, unconditional theorem or practical performance claim')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(js(result),indent=2)+'\n')
    print(json.dumps(dict(a_bit=str(a),kappa=str(k),ratio_to_PR37=float(result['ratio_to_PR37']),strict_constraints=len(assembled['constraints']),row_degree=f['rows']['degree'])))


if __name__=='__main__':main()
