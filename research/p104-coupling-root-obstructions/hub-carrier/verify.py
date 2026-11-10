"""Exact complementary pure-hub carrier audit for the parent construction.
Prepared for @CubeJerry with substantial OpenAI ChatGPT/Codex assistance.
Apache-2.0. The source construction retains the parent package's attribution.
"""
from fractions import Fraction as Q
import json
N=20

def need(x,m):
 if not x:raise ValueError(m)
def e(i):return [Q(j==i)for j in range(N)]
def dot(x,y):return sum(a*b for a,b in zip(x,y))
def outer(x,y):return [[a*b for b in y]for a in x]
def add(A,B,c=1):return [[x+c*y for x,y in zip(a,b)]for a,b in zip(A,B)]
def mul(A,B):return [[dot(a,b)for b in zip(*B)]for a in A]
def ident():return [[Q(i==j)for j in range(N)]for i in range(N)]
def rank(a):
 a=[r[:]for r in a];k=0
 for j in range(N):
  p=next((i for i in range(k,N)if a[i][j]),None)
  if p is None:continue
  a[k],a[p]=a[p],a[k];q=a[k][j];a[k]=[x/q for x in a[k]]
  for i in range(k+1,N):
   q=a[i][j];a[i]=[x-q*y for x,y in zip(a[i],a[k])]
  k+=1
 return k
Z=[[Q(0)]*N for _ in range(N)];I=ident()
hub=add(outer(e(0),e(0)),outer(e(1),e(1)))
us=[e(0),e(1),e(1),[-x for x in e(0)]]
vs=[[a-b for a,b in zip(e(0),e(1))]]*2+[[a+b for a,b in zip(e(0),e(1))]]*2
sizes=[4,4,5,5];starts=[2,6,10,15];sigmas=[1,-1,1,-1]
projectors=[];sites=[];chains=[];arms=[]
for arm,(u,v,g,start,sigma)in enumerate(zip(us,vs,sizes,starts,sigmas)):
 E=add(hub,outer(u,v),-Q(1,sigma));projectors.append(E)
 need(mul(E,E)==E,'hub idempotent');M=I
 for i in range(g):
  current=start+i
  older=list(range(start,current))if sigma==1 else list(range(current+1,start+g))
  x=[a+b for a,b in zip(u,e(current))]
  for j in older:x=[a+2*b for a,b in zip(x,e(j))]
  y=[a-sigma*b for a,b in zip(v,e(current))]
  P=hub
  for j in [current]+older:P=add(P,outer(e(j),e(j)))
  Pi=add(P,E,-1)
  for j in older:
   gamma=[a-2*sigma*b for a,b in zip(e(j),v)]
   G=outer(e(j),gamma);chains.append((arm,G));Pi=add(Pi,G,-1)
  R=outer(x,y)
  need(mul(Pi,Pi)==Pi and sum(Pi[j][j]for j in range(N))==2,'actual active plane rank2')
  need(mul(Pi,R)==mul(R,Pi)==R,'query inside actual active plane')
  need(mul(E,Pi)==mul(Pi,E)==Z and mul(E,R)==mul(R,E)==Z,'both-sided own hub invariance')
  sites.append((arm,x,y,Pi,R));M=mul(add(I,R,-2),M)
 arms.append(M)
for i,(_,x,y,_,_)in enumerate(sites):
 for j,(_,xx,yy,_,_)in enumerate(sites):need(dot(y,xx)==(i>j)-(i<j),'full query sign Gram')
for a,b in[(0,1),(2,3)]:
 E,F=projectors[a],projectors[b];H=add(F,E,-1)
 need(E!=F and H!=Z,'distinct hub duals')
 need(mul(E,F)==F and mul(F,E)==E,'common image')
 need(mul(H,H)==Z and mul(H,E)==Z and mul(E,H)==H,'nilpotent discarded shear')
 for arm,G in chains:
  if arm in(a,b):need(mul(E,G)==mul(G,E)==mul(F,G)==mul(G,F)==Z,'chain idles commute both hub projectors')
 product={(0,0):mul(add(I,F,-1),add(I,E,-1)),(1,0):mul(add(I,F,-1),E),(0,1):mul(F,add(I,E,-1)),(1,1):mul(F,E)}
 need(product=={(0,0):add(I,F,-1),(1,0):Z,(0,1):H,(1,1):E},'exact polynomial coefficients')
 residual={(0,0):mul(add(I,H,-1),add(I,E,-1)),(1,0):Z,(0,1):mul(H,add(I,E,-1)),(1,1):mul(add(I,H,-1),E)}
 need(product==residual,'exact residual factorization')


def rejected(action,label):
 try:action()
 except ValueError:return label
 raise ValueError('control unexpectedly accepted: '+label)

def same_image(E,F):
 need(mul(E,E)==E and mul(F,F)==F,'idempotent carrier required')
 need(mul(E,F)==F and mul(F,E)==E,'common image required')

E,F=projectors[0],projectors[1];H=add(F,E,-1)
controls=[]
controls.append(rejected(lambda:need(add(I,F,-2)==add(I,E,-2),'U=1,V=-1 detects omitted residual'),'naive fusion on exact Gaussian character'))
controls.append(rejected(lambda:need(mul(I,add(I,E,-1))==add(I,F,-1),'constant coefficient needs residual minus-I term'),'residual missing minus-I'))
controls.append(rejected(lambda:need(mul(add(I,E,-1),H)==H,'wrong-order residual has wrong V coefficient'),'residual order reversed'))
controls.append(rejected(lambda:same_image(E,outer(e(0),e(0))),'different-image projectors'))
controls.append(rejected(lambda:same_image(add(E,E),F),'non-idempotent carrier'))
# Equal duals are a positive control: constant+UV E, with no V coefficient.
need(mul(E,add(I,E,-1))==Z and mul(E,E)==E,'equal-dual fusion positive control')
# Whole-job central normalization has S=+1 at Q=1,i; normalized thin bridges
# are therefore the identity in this valid sector, independent of R.
sectors=[(q%2-q)%4 for q in range(4)]
need(sectors==[0,0,2,2],'retained normalized central sectors')
need(len(controls)==5,'all targeted controls executed')
print(json.dumps({'status':'PASS_HUB_CARRIER_DEFECT','shape':sizes,'full_sites':len(sites),'sign_gram_entries':len(sites)**2,'hub_pairs':2,'nonzero_V_shear_coefficients':2,'chain_factor_checks':len(chains),'negative_controls':controls,'positive_control':'equal duals fuse correctly','new_kappa':False,'scope':'Fixed pure-hub carriers and isolated scalar-wrapper replacement; changed supports/native reuse remain open.'},sort_keys=True))
