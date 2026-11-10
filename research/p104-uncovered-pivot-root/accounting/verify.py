#!/usr/bin/env python3
"""Exact complete-invoice audit of minimal uncovered-pivot roots.
By @CubeJerry with substantial OpenAI GPT-6 assistance. Apache-2.0.
Native data and predecessor mechanisms retain attribution in README.md.
"""
from __future__ import annotations
import ast
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
CAP = Q('0.0034')
BENCHMARK = Q('0.00337180')
LOWER = Q('0.0033334095468')
UPPER = Q('0.0033334095470')

def need(condition, message):
    if not condition: raise ValueError(message)

def authenticate(raw,row):
    need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA256')
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    need(blob==row['git_blob'],'source Git blob')

def source_census():
    """Authenticate retained bytes; parse literal dictionaries without executing."""
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    for row in pins['sources']:
        raw = (HERE / row['retained_path']).read_bytes()
        authenticate(raw,row)
        try:authenticate(raw+b'corrupt',row)
        except ValueError:pass
        else:raise ValueError('source corruption control failed')
    tree = ast.parse((HERE / 'retained/pricing-6833.py').read_text())
    got = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for name in node.targets:
                if isinstance(name, ast.Name) and name.id in ('HELPERS', 'LOCAL_PAID'):
                    got[name.id] = ast.literal_eval(node.value)
    need(set(got) == {'HELPERS', 'LOCAL_PAID'}, 'native census literals')
    return Counter(got['HELPERS']), Counter(got['LOCAL_PAID'])

def mask_data(a, b):
    """L=a+b+1 sites; A plus one singleton-host field except at pivot a."""
    L = a+b+1
    fields = [(min(i,a), max(i,a), i) for i in range(L) if i!=a]
    sizes = [1+sum(lo<=i<=hi for lo,hi,host in fields) for i in range(L)]
    demands = [size-2 for size in sizes]
    need(demands == list(range(a))+[a+b-1]+list(reversed(range(b))), 'physical idle dimensions')
    targets = Counter({8*L+1:1})
    targets.update(8*(hi-lo+1)+1 for lo,hi,host in fields)
    naive = Counter(range(1,a+1)); naive.update(range(1,b+1))
    need(naive[1]>0, 'nonempty pivot arms')
    optimum=naive.copy(); optimum[1]-=1; optimum+=Counter()
    need(sum(length*count for length,count in optimum.items())==sum(demands), 'repaired idle mass')
    paid=Counter({1:1}); paid.update({8*length:count for length,count in optimum.items()})
    need(sum(r*c for r,c in targets.items())-sum(r*c for r,c in paid.items())==17*L-1,
         'fixed rank-two shortest-root mass invariant')
    return fields,demands,targets,paid,optimum

def partition_bound(a,b,k):
    """Top-k incidence relaxation; no job touches both strict arms."""
    return max(sum(min(left,j) for j in range(a))+sum(min(right,j) for j in range(b))+min(k,a+b-1)
               for left in range(k+1) for right in range(k-left+1))

def top_sums(counter):
    out=[0]
    for value in sorted(counter.elements(),reverse=True): out.append(out[-1]+value)
    return out

def cover_controls():
    checked=0
    for L in range(2,23):
        for a in range(L):
            b=L-1-a
            fields,demands,targets,paid,optimum=mask_data(a,b)
            partial=top_sums(optimum)
            for k in range(L+2):
                need(partition_bound(a,b,k)==partial[min(k,len(partial)-1)], 'top-k combinatorial identity')
                checked+=1
            for i in range(a):
                mi={0}|{host+1 for lo,hi,host in fields if lo<=i<=hi}
                for j in range(a+1,L):
                    mj={0}|{host+1 for lo,hi,host in fields if lo<=j<=hi}
                    need(mi & mj == {0}, 'cross-arm support obstruction')
    _,d,T,P,V=mask_data(8,9)
    relaxed=Counter(sum(x>=level for x in d) for level in range(1,max(d)+1))
    need(sum(r*c for r,c in relaxed.items())==sum(d), 'cross-arm control preserves mass')
    need(max(relaxed)>max(V), 'dropping arm separation defeats majorization')
    phantom=P.copy(); phantom[8]+=1
    need(sum(r*c for r,c in T.items())-sum(r*c for r,c in phantom.items())==297,
         'phantom pivot idle detected by mass invariant')
    return checked,dict(sorted(relaxed.items()))

def matrix_rank(rows):
    rows=[[Q(x) for x in row] for row in rows]
    if not rows:return 0
    rank=0
    for col in range(len(rows[0])):
        pivot=next((i for i in range(rank,len(rows)) if rows[i][col]),None)
        if pivot is None:continue
        rows[rank],rows[pivot]=rows[pivot],rows[rank]
        lead=rows[rank][col]
        rows[rank]=[x/lead for x in rows[rank]]
        for i in range(rank+1,len(rows)):
            factor=rows[i][col]
            if factor:rows[i]=[x-factor*y for x,y in zip(rows[i],rows[rank])]
        rank+=1
        if rank==len(rows):break
    return rank


def transport_controls():
    """Independently test source-idle -> destination-mask intersection at S=-1.

    No root package is imported. These are finite controls for the endpoint proof.
    """
    checked=0
    for L in (4,6,18):
        for a in range(L):
            hosts=[i for i in range(L) if i!=a]
            index={host:j+1 for j,host in enumerate(hosts)}
            sites=[]
            for i in range(L):
                x=[0]*L;y=[0]*L;y[0]=1
                if i<a:
                    x[0]=1;x[index[i]]=-1;y[index[i]]=1
                    for j in hosts:
                        if j<i:x[index[j]]=-2
                    mask={0}|{index[j] for j in hosts if j<=i}
                elif i>a:
                    x[0]=-1;x[index[i]]=1;y[index[i]]=1
                    for j in hosts:
                        if j>i:x[index[j]]=2
                    mask={0}|{index[j] for j in hosts if j>=i}
                else:
                    for j in hosts:x[index[j]]=-1 if j<a else 1
                    mask=set(range(L))
                sites.append((x,y,mask,i))
                if i==a:
                    u=2 if a%2==0 else 0
                    tx=[0]*L;ty=[0]*L;tx[0]=-1;ty[0]=u
                    for j in hosts:
                        if j>a:tx[index[j]]=2
                        ty[index[j]]=(u-1)*(-1)**(j if j<a else L-1-j)
                    sites.append((tx,ty,None,None))
            for source in range(a):
                source_mask=sorted(sites[source][2]);source_y=sites[source][1]
                for dest in range(a+1,L):
                    dest_time=dest+1; dest_mask=sites[dest_time][2]
                    columns=[]
                    for c in source_mask:
                        v=[int(j==c) for j in range(L)]
                        for x,y,mask,label in sites[source+1:dest_time]:
                            coefficient=sum(yi*vi for yi,vi in zip(y,v))
                            v=[vi-2*coefficient*xi for xi,vi in zip(x,v)]
                        columns.append(v)
                    constraints=[[source_y[c] for c in source_mask]]
                    constraints.extend([[column[row] for column in columns] for row in range(L) if row not in dest_mask])
                    need(matrix_rank(constraints)==len(source_mask),'no conjugated cross-arm primal carrier')
                    need(matrix_rank(constraints[1:])<len(source_mask),'omitted source neutrality admits false transport')
                    checked+=1
            if a>=3:
                # Adjacent left sites 1,2: F_0 is a genuine neutral primal line.
                v=[int(c==index[0]) for c in range(L)]
                for time in (1,2):
                    _,y,mask,_=sites[time]
                    need(sum(u*w for u,w in zip(y,v))==0 and all(not v[c] for c in range(L) if c not in mask),
                         'same-arm positive idle-line control')
    return checked


def add_interval(a,b): return a[0]+b[0],a[1]+b[1]
def scale_interval(a,c): return (c*a[0],c*a[1]) if c>=0 else (c*a[1],c*a[0])

@lru_cache(None)
def log_bounds(n):
    need(n>=1, 'positive logarithm argument')
    shift=n.bit_length()-1; y=Q(n,2**shift)
    def series(z):
        total=Q(0); term=z
        for j in range(80): total+=term/(2*j+1);term*=z*z
        return 2*total,2*total+2*term/(161*(1-z*z))
    return add_interval(scale_interval(series(Q(1,3)),shift),series((y-1)/(y+1)))

def exp_negative(z):
    """Alternating Taylor encloses exp(-z) for 0<=z<1."""
    need(0<=z<1, 'alternating exponential range')
    total=Q(1);term=Q(1);lower=upper=None
    for k in range(1,21):
        term*=-z/k; total+=term
        if k==19:lower=total
        if k==20:upper=total
    return lower,upper

@lru_cache(None)
def power_bounds(r,kappa):
    need(0<=kappa<=CAP, 'certified exponent range')
    lo,hi=log_bounds(r)
    return r*exp_negative(kappa*hi)[0],r*exp_negative(kappa*lo)[1]

def moment(hist,kappa):
    ans=(Q(0),Q(0))
    for r,c in hist.items():ans=add_interval(ans,scale_interval(power_bounds(r,kappa),c))
    return ans

def complete(outer_t,outer_p,native_t,native_p):
    T=Counter({r:18*c for r,c in native_t.items()});P=Counter({r:18*c for r,c in native_p.items()})
    T.update({r:104*c for r,c in outer_t.items()});P.update({r:104*c for r,c in outer_p.items()})
    need(sum(r*c for r,c in T.items())-sum(r*c for r,c in P.items())==760, 'complete source-bound mass760')
    signed=T.copy();signed.subtract(P)
    return T,P,signed

def decimal_floor(x,digits=18):
    scale=10**digits;q=(x.numerator*scale)//x.denominator
    sign='-' if q<0 else '';q=abs(q)
    return f'{sign}{q//scale}.{q%scale:0{digits}d}'

def display(interval):
    return [decimal_floor(interval[0]),decimal_floor(interval[1]+Q(1,10**18))]

def main():
    native_t,native_p=source_census()
    checked,cross_relaxed=cover_controls()
    transport_checked=transport_controls()
    fields,demands,t,p,lengths=mask_data(8,9)
    T,P,signed=complete(t,p,native_t,native_p)
    margins={name:moment(signed,k) for name,k in [('lower',LOWER),('upper',UPPER),('benchmark',BENCHMARK),('BIT_cap',CAP)]}
    need(margins['lower'][0]>0 and margins['upper'][1]<0, 'exact optimistic crossing bracket')
    need(margins['benchmark'][1]<0 and margins['BIT_cap'][1]<0, 'complete negative benchmark signs')
    derivative_upper=Q(0)
    for r,c in signed.items():
        log_lo,log_hi=log_bounds(r)
        derivative_upper += -c*power_bounds(r,CAP)[0]*log_lo if c>=0 else -c*r*log_hi
    need(derivative_upper<0, 'no reentry through admitted BIT cap')
    balanced=moment(signed,BENCHMARK);shape_checks=0
    for a in range(18):
        _,_,at,ap,_=mask_data(a,17-a)
        _,_,shape=complete(at,ap,native_t,native_p)
        if a not in (8,9):need(moment(shape,BENCHMARK)[1]<balanced[0], 'balanced complete gain')
        shape_checks+=1
    baseline_t=Counter({1:1,145:1});baseline_t.update({8*s+1:2 for s in range(1,10)})
    baseline_p=Counter({1:3});baseline_p.update({8*s:2 for s in range(1,9)})
    _,_,base=complete(baseline_t,baseline_p,native_t,native_p)
    source_bracket=[Q('.0033718004754'),Q('.0033718004755')]
    need(moment(base,source_bracket[0])[0]>0 and moment(base,source_bracket[1])[1]<0, 'source caller crossing')
    no_native=Counter({r:104*c for r,c in t.items()});no_native.subtract({r:104*c for r,c in p.items()})
    need(moment(no_native,BENCHMARK)[0]>0, 'omitting native bill gives false favorable control')
    for r in (1,2,8,17,81,145):need(power_bounds(r,Q(0))==(Q(r),Q(r)), 'exact zero-loss power')
    result={
      'status':'PASS_PIVOT_CALLER_AUDIT',
      'scope':'Minimal coordinate singleton-host uncovered-pivot roots; independent rank-two full stages; one-field whole-idle jobs including conjugation through literal queries; no new kappa.',
      'L':18,'arms':[8,9],'targets_per_port':dict(sorted(t.items())),
      'optimistic_paid_per_port':dict(sorted(p.items())),
      'optimistic_idle_lengths':dict(sorted(lengths.items())),
      'idle_dimensions':demands,'complete_targets':dict(sorted(T.items())),
      'complete_paid':dict(sorted(P.items())),
      'complete_target_count':sum(T.values()),'complete_paid_count':sum(P.values()),
      'complete_target_rank_mass':sum(r*c for r,c in T.items()),
      'complete_paid_rank_mass':sum(r*c for r,c in P.items()),
      'rank_mass_surplus':760,'raw_upper_crossing':[str(LOWER),str(UPPER)],
      'certified_margins':{name:display(value) for name,value in margins.items()},
      'uniform_derivative_upper':decimal_floor(derivative_upper+Q(1,10**18)),
      'source_crossing_reconstructed':[str(x) for x in source_bracket],
      'top_k_control_cases':checked,'benchmark_shape_checks':shape_checks,'cross_arm_transport_cases':transport_checked,
      'cross_arm_control_lengths':cross_relaxed,
      'inherited_assumptions':['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
      'limitations':['Paid relaxation need not be attainable.','No native operator or physical compiler replay claimed.','Enlarged masks, new outputs, changed query words and changed native rank contracts are outside this cover proof.'],
    }
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if '--write-result' in sys.argv:(HERE/'RESULT.json').write_text(encoded)
    else:need((HERE/'RESULT.json').read_text()==encoded, 'exact retained result agreement')
    print(encoded,end='');print('PASS_PIVOT_CALLER_AUDIT')

if __name__=='__main__':main()
