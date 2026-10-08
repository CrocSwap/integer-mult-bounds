#!/usr/bin/env python3
"""Portable exact rectangular record. Only the Python standard library is needed.

Log/exponential enclosures and physical counts adapted from icekylinx PR18 and Zhihao Chen PR21.
Semantic assembly adapted from Zhihao Chen PR23. All geometric and analytic
claims remain conditional on the attributed written proofs and their review.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from math import comb,prod,log
from hashlib import sha256
import argparse,json
from semantic_arithmetic import assembly,cutoffs,halving,ceil,js
HERE=Path(__file__).resolve().parent

def log_upper(value):
    value = Q(value)
    assert value >= 1
    power = 0
    while value > 2:
        value /= 2
        power += 1
    def series(x):
        z = (x-1)/(x+1)
        return 2*sum((z**(2*j+1)/(2*j+1) for j in range(24)), Q(0)) + 2*z**49/(49*(1-z*z))
    scaled = (power*series(Q(2)) + series(value))*10**12
    return Q(-(-scaled.numerator//scaled.denominator), 10**12)

def tree(edges,n):
 if len(edges)!=n-1 or len(set(edges))!=len(edges):return False
 adj=[set() for _ in range(n)]
 for x,y in edges:adj[x].add(y);adj[y].add(x)
 seen={0};todo=[0]
 while todo:
  for y in adj[todo.pop()]-seen:seen.add(y);todo.append(y)
 return len(seen)==n

def basis(a,b,k):
 s=k-2*a;H=a*b;n=k+a
 if not(0<s<a and 2*n<=H and H>2*k and a%b and k%b):return None
 I=list(range(a));S=list(range(s));R=I+S+I+I;C=I+I+S+I
 assert len(R)==len(C)==n
 maps=[]
 for beta in range(b):
  prescribed={}
  pairs=[(i//b,col) for i,col in enumerate(R) if i%b==beta]
  pairs += [(i//b,col) for j,col in enumerate(C) if (i:=H-n+j)%b==beta]
  for row,col in pairs:
   if row in prescribed and prescribed[row]!=col:return None
   if col in prescribed.values() and prescribed.get(row)!=col:return None
   prescribed[row]=col
  unused=iter(x for x in range(a) if x not in prescribed.values())
  maps.append([prescribed[r] if r in prescribed else next(unused) for r in range(a)])
 size=a+b-1
 forward=[(R[i],a+i%b) for i in range(size)]
 dual=[(C[j],a+(H-n+j)%b) for j in range(n-size,n)]
 if not(tree(forward,a+b) and tree(dual,a+b)):return None
 return dict(dims=[a,b,k],s=s,n=n,R=R,C=C,permutations=maps,A5_forward=forward,A5_dual=dual,
             scope='Prescription completion and A5 trees only; A1/A3 simultaneous minors not independently proved')

def counts(dims,ps):
 a,b,k=dims;H=a*b;m=H*k;v=[comb(h,3) for h in dims];N=prod(v)
 B1,B2,B3=[N//vi*ps[str(h)]['roles'] for h,vi in zip(dims,v)]
 E=B3-B1
 if E<0:return None
 W=2*N+B2+B3;L=N*sum((Q(6,h-2) for h in dims),Q());assert L.denominator==1
 rank=W*m-2*N+2*int(L);rows=Counter();s=k-2*a
 profiles=[(B1,(a,s,a,a,m-2*(a+k))),(E,(k,m-2*k)),(B2,(b,m-2*b)),
           (2*N,(k-2,H-2*k+2,m-2*H-2*k+2)),(2*N,(H-2*(a+b-1),))]
 rows[1]+=2*N*((2*k-1)+(a+b-1))
 for h in dims:rows[1]+=2*N;rows[h-2]+=2*N
 for number,widths in profiles:
  for w in widths:assert 0<w<m;rows[w]+=number
 for h,vi in zip(dims,v):
  p=ps[str(h)];assert sum(r*c for r,c in enumerate(p['histogram']))==h*p['roles']+2*h*(h-1)
  for r,c in enumerate(p['histogram']):
   copies=N//vi*c;block=max(0,2*r-h);rows[1]+=copies*(r-block)
   if block:rows[block]+=copies
 rows=Counter({t:c for t,c in rows.items() if c})
 assert sum(t*c for t,c in rows.items())==rank
 eta=1-Q(rank,W*m)
 if eta<=0:return None
 slope=sum(float(Q(t*c,W*m))*log(m/t) for t,c in rows.items())
 return dict(dims=list(dims),m=m,W=W,N=N,B1=B1,B2=B2,B3=B3,E=E,L=int(L),s=rank,eta=eta,rows=rows,linear_screen=float(eta)/slope)

def exact(n):
 weights={t:Q(t*c,n['W']*n['m']) for t,c in n['rows'].items()};logs={t:log_upper(Q(n['m'],t)) for t in weights}
 def moment(a):
  total=Q()
  for t,w in weights.items():
   u=a*logs[t];assert 0<=u<1
   total+=w*(1+u+u*u/(2*(1-u/3)))
  return total
 lo,hi=0,100000000
 while hi-lo>1:
  mid=(lo+hi)//2
  if moment(Q(mid,10**12))<1:lo=mid
  else:hi=mid
 return dict(saving=Q(lo,10**12),moment_upper=moment(Q(lo,10**12)),gap=1-moment(Q(lo,10**12)),next_moment=moment(Q(hi,10**12)))

def finite_bridge(n,inputs):
    inherited=inputs['semantic_PR23']['finite_bridge']
    co=dict(inherited['complex']);m,W,s=co['m'],co['W'],co['s']
    v=comb(28,3);G=3*v*v*(4*co['active_nodes']+4*v+4)
    assert G==co['scalar_group_upper']
    E=64*(W+m+1)**3;charge=2*G*W*W+8*s+4*W+4+32*m
    assert charge<E
    B=s+E;C0=32*m*B*B;M=co['maxchild']
    assert 2*B*(m-M)>=s+E and 2*B+18<C0
    semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,B=B,C0=C0,C1=1,induction_gap=2*B*(m-M)-s-E)
    assert semantic==inherited['semantic']
    mb,Wb,Mb=n['m'],n['W'],max(n['rows'])
    db,dc=halving(mb,Mb),halving(m,M)
    wb,wc=Wb.bit_length(),W.bit_length()
    coefficient=wb*db+wc*dc;degree=1000*ceil(Q(coefficient*51,25000))
    assert degree>Q(coefficient*51,25)
    return dict(bit=dict(m=mb,W=Wb,maxchild=Mb,halving_degree=db,wire_bits=wb),complex=co,semantic=semantic,rows=dict(coefficient=coefficient,degree=degree,suffix_slope=4*degree,degree_gap=degree-Q(coefficient*51,25),contract='W_complex^D_complex * W_bit^D_bit; leading prefix, padding and nested bit factors restored'))

def run():
    inputs=json.loads((HERE/'inputs.json').read_text());dims=(28,27,57)
    ps={h:item['record'] for h,item in inputs['producers'].items()}
    for h,p in ps.items():
        h=int(h);assert p['v']==comb(h,3) and p['loss']==h*(h-1)
        assert p['roles']==p['additions']+p['outputs']-p['matches']
        assert sum(r*c for r,c in enumerate(p['histogram']))==h*p['roles']+2*p['loss']
    pre=basis(*dims);assert pre
    pre['scope']='Explicit consistent partial permutations and two A5 trees; general simultaneous-basis argument is in the accompanying audited text.'
    n=counts(dims,ps);a,b,k=dims;H=a*b
    old=exact(n)
    n['rows'][1]-=2*n['N']*(b-2);n['rows'][b-2]+=2*n['N']
    assert n['rows'][1]>0 and sum(r*c for r,c in n['rows'].items())==n['s']
    assert n['W']*n['m']-n['s']==2*n['N']-2*n['L']>0
    # This floating screening value described the pre-A5 profile and is omitted.
    n.pop('linear_screen')
    bit=exact(n);saving=bit['saving']
    assert bit['gap']>0 and bit['next_moment']>=1
    bridge=finite_bridge(n,inputs)
    h=Q(1,10**8);q=saving*(1-2*h);c=q*(1+h);eps=(1-h)/(1+c+q)
    limiting=eps*q;scale=10**12;kappa=Q((limiting*scale).numerator//(limiting*scale).denominator,scale)
    assert kappa<limiting
    assembled=assembly(bridge,saving,kappa);eventual=cutoffs(bridge,assembled)
    assert len(assembled['constraints'])==47 and len(assembled['margins'])==7
    negatives=[]
    for name,kwargs in [('old_quadratic_guard',dict(old_guard=True)),('old_separate_exposure',dict(old_exposures=True)),('next_kappa_grid',dict(kappa=kappa+Q(1,scale)))]:
        try:assembly(bridge,saving,kwargs.pop('kappa',kappa),**kwargs)
        except AssertionError:negatives.append(name)
        else:raise AssertionError('Negative control did not reject: '+name)
    assert old['saving']<saving
    negatives.extend(['next_bit_grid_fails_same_enclosure','omitting_A5_block_lowers_certified_saving'])
    profiles=dict(A1=dict(copies=n['B1'],blocks=[a,k-2*a,a,a,n['m']-2*(a+k)]),A3=dict(copies=2*n['N'],singletons=2*k-1,blocks=[k-2,H-2*k+2,n['m']-2*H-2*k+2]),A5=dict(copies=2*n['N'],singletons=a+1,blocks=[b-2,H-2*(a+b-1)]),translated_auxiliary=dict(copies=n['B2'],blocks=[b,n['m']-2*b]))
    hashed=['record.py','semantic_arithmetic.py','inputs.json','compatibility-theorem.txt','a3-dimension-free-proof.txt','a5-28-27-proof.txt','independent-proof-audit.txt']
    return dict(status='CHECKED CONDITIONAL RECTANGULAR CANDIDATE; UNPUBLISHED; NOT FORMAL VERIFICATION',dimensions=dims,profiles=profiles,prescribed_basis=pre,counts=n,bit=bit,without_A5_saving=old['saving'],finite_bridge=bridge,assembly=assembled,eventual_bounds=eventual,negative_controls=negatives,controls=inputs['controls'],source_sha256=inputs['source_sha256'],record_sha256={name:sha256((HERE/name).read_bytes()).hexdigest() for name in hashed},producer_evidence=inputs['producers'],attribution=inputs['attribution'],proof_status='Written general A1/A3/A5 compatibility argument and two independent agent audits; exact Q A1/A5 and modular finite controls supplement the argument. Inherited PR18/21 physical source-frame and PR23 semantic/tape assumptions remain. Changed tuple has not received a full-repository rerun. No global optimality claim.',comparison=dict(PR25=Q(11447067,10**12),ratio_to_PR25=kappa/Q(11447067,10**12)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=HERE/'certificate.json');args=p.parse_args()
    result=run();args.output.write_text(json.dumps(js(result),indent=2,sort_keys=True)+'\n')
    print('PASS conditional bit='+str(result['bit']['saving'])+'; kappa='+str(result['assembly']['parameters']['kappa']))
    print('47 strict constraints, 7 margins; row degree='+str(result['finite_bridge']['rows']['degree']))
