#!/usr/bin/env python3
"""Independent exact sector-root audit. Imports no construction/author checker."""
import argparse,hashlib,json
from pathlib import Path
from fractions import Fraction as F
from collections import Counter

def ident(n):return [{i:F(1)} for i in range(n)]
def add(a,b,c=F(1)):
 d=a.copy()
 for k,v in b.items():
  z=d.get(k,F(0))+c*v
  if z:d[k]=z
  else:d.pop(k,None)
 return d
def scale(A,c):return [{j:c*v for j,v in r.items() if c*v} for r in A]
def plus(A,B,c=F(1)):return [add(a,b,c) for a,b in zip(A,B)]
def mul(A,B):
 C=[]
 for a in A:
  r={}
  for k,v in a.items():r=add(r,B[k],v)
  C.append(r)
 return C
def outer(x,y):return [{j:a*b for j,b in enumerate(y) if a*b} for a in x]
def dot(x,y):return sum((a*b for a,b in zip(x,y)),F(0))
def rank(A):
 A=[r.copy() for r in A];piv={}
 for r in A:
  while r:
   k=min(r)
   if k in piv:r=add(r,piv[k],-r[k])
   else:
    z=r[k];piv[k]={j:v/z for j,v in r.items()};break
 return len(piv)
def unit(rows,x,y,c):
 r={}
 for j,v in enumerate(y):
  if v:r=add(r,rows[j],v)
 return [add(row,r,c*x[i]) if x[i] else row.copy() for i,row in enumerate(rows)]
def all_D(d,sign,drop_mask=False,wrong_order=False):
 n=d['n'];X=[[F(x) for x in r] for r in d['X']];Y=[[F(x) for x in r] for r in d['Y']]
 rows=[{(i,0):F(1)} for i in range(n)]
 after={max(st['units']):j for j,st in enumerate(d['stages'])};assert len(after)==len(d['stages'])
 # Every D occurs once, on one diagonal layer. Hence no lane exceeds degree 1.
 assert len(after)<256
 for k,(x,y) in enumerate(zip(X,Y)):
  if wrong_order and k==0:x,y=X[1],Y[1]
  rows=unit(rows,x,y,F(sign-1))
  if k in after:
   j=after[k];mask=d['stages'][j]['mask']
   if drop_mask and j==0:mask=mask[1:]
   for i in mask:
    assert all(((pow>>(8*j))&255)==0 for src,pow in rows[i])
    rows[i]={(src,pow+(1<<(8*j))):v for (src,pow),v in rows[i].items()}
 expected=[]
 for i in range(n):
  mon=sum(1<<(8*j) for j,st in enumerate(d['stages']) if i in st['mask'])
  expected.append({(i,mon):F(sign)})
 return rows==expected,sum(map(len,rows)),len(set(k[1] for row in rows for k in row))
def audit(path):
 raw=Path(path).read_bytes();d=json.loads(raw);n=d['n'];N=d['N'];stages=d['stages'];L=len(stages)
 X=[[F(x) for x in r] for r in d['X']];Y=[[F(x) for x in r] for r in d['Y']]
 assert N==n+1==2*L+3 and len(X)==len(Y)==N and all(len(r)==n for r in X+Y)
 assert all(x.denominator==1 for row in X+Y for x in row)
 assert all(dot(Y[i],X[j])==F((i>j)-(i<j)) for i in range(N) for j in range(N))
 pairs=[u for st in stages for u in st['units']];assert len(pairs)==len(set(pairs))==2*L
 I=ident(n);zero=[{} for _ in range(n)];pref=[I]
 for x,y in zip(X,Y):pref.append(unit(pref[-1],x,y,F(-2)))
 assert pref[-1]==scale(I,F(-1))
 details=[]
 for j,st in enumerate(stages):
  u,v=st['units'];mask=set(st['mask']);assert v==u+1 and len(mask)==len(st['mask'])
  assert all(0<=i<n for i in mask)
  assert all(not X[k][i] and not Y[k][i] for k in [u,v] for i in range(n) if i not in mask)
  H=plus(outer(X[u],Y[v]),outer(X[v],Y[u]),F(-1));P=[{i:F(1)} if i in mask else {} for i in range(n)];R=plus(P,H,F(-1))
  assert mul(H,H)==H and mul(R,R)==R and mul(H,R)==mul(R,H)==zero
  assert plus(H,R)==P and rank(H)==2 and rank(R)==len(mask)-2
  assert all(not dot(Y[k],[R[i].get(c,F(0)) for i in range(n)]) for k in [u,v] for c in range(n))
  assert all(not sum((a*X[k][c] for c,a in row.items()),F(0)) for k in [u,v] for row in R)
  for cut in [u,v+1]:assert mul(P,pref[cut])==mul(pref[cut],P)
  M=unit(unit(I,X[u],Y[u],F(-2)),X[v],Y[v],F(-2))
  assert mul(M,R)==R and mul(R,M)==R and mul(M,H)==mul(H,M)
  details.append({'stage':j,'units':[u,v],'mask':sorted(mask),'host_rank':rank(H),'idle_rank':rank(R),'support_Y':sum(bool(Y[u][i] or Y[v][i]) for i in range(n))})
 assert all(any(i in st['mask'] for st in stages) for i in range(n))
 assert all(0 in st['mask'] for st in stages)
 formal={str(s):all_D(d,s) for s in [1,-1]};assert all(z[0] for z in formal.values())
 assert not all_D(d,-1,drop_mask=True)[0] and not all_D(d,-1,wrong_order=True)[0]
 # A deliberate header change must invalidate at least one sign-Gram condition.
 bad=[r[:] for r in X];bad[0][0]+=1
 assert any(dot(Y[i],bad[j])!=F((i>j)-(i<j)) for i in range(N) for j in range(N))
 membership=Counter(sum(i in st['mask'] for st in stages) for i in range(n))
 target=Counter({1+8*k:v for k,v in membership.items()});idle=sum(len(st['mask'])-2 for st in stages);thin=N-2*L
 paid=Counter({8:idle,1:thin});ideal=paid+Counter({8:2*L})
 mass=lambda a:sum(k*v for k,v in a.items())
 assert mass(target)-mass(ideal)==n-thin
 if n==38:assert mass(target)-mass(ideal)==35
 return {'status':'PASS','root_sha256':hashlib.sha256(raw).hexdigest(),'n':n,'N':N,'L':L,'sector_semantics':'I+(S-1) X_i Y_i; S^2=1','integral_header':True,'connected_header':'every offdiagonal Gram entry is nonzero','connected_masks':'all masks share coordinate0 and their union covers all n fields','complete_sign_Gram_entries':N*N,'minus_endpoint':'-I','mask_prefix_commutators':2*L,'stages':details,'formal_all_D':formal,'negative_controls':['first mask coordinate omitted','first unit replaced','one header coefficient changed'],'thin_units':sorted(set(range(N))-set(pairs)),'target_profile':dict(sorted(target.items())),'unbundled_paid_excluding_HOST':dict(sorted(paid.items())),'hypothetical_ideal_paid_with_2H8_per_HOST':dict(sorted(ideal.items())),'mask_incidence':sum(len(st['mask']) for st in stages),'target_mass':mass(target),'unbundled_nonnative_mass':mass(paid),'hypothetical_ideal_mass':mass(ideal),'hypothetical_ideal_surplus':mass(target)-mass(ideal),'unbuilt_obligations':[str(L)+' resonant t=-1 HOST supplier calls with their actual full T/P invoice','all scalar basis/gauge/wrapper operations and exact alphabet checks','native all-width correctness, rounding, finite compiler and outer admission; no kappa claim']}
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();r=audit(a.root);s=json.dumps(r,indent=2)+'\n';Path(a.out).write_text(s);print(s)
