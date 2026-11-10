"""Independent direct-nullspace review; no construction/capacity/price imports.
@CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from math import gcd
from pathlib import Path
import argparse,ast,hashlib,json,time
HERE=Path(__file__).resolve().parent
SCALE=10**18;K=Q('0.00337180');N=18;PIVOT=8

def need(c,s):
 if not c:raise ValueError(s)
def eye(n):return [[Q(i==j)for j in range(n)]for i in range(n)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def mm(a,b):return [[dot(r,c)for c in zip(*b)]for r in a]
def rref(a,n):
 a=[[Q(v)for v in row]for row in a];piv=[];r=0
 for c in range(n):
  p=next((i for i in range(r,len(a))if a[i][c]),None)
  if p is None:continue
  a[r],a[p]=a[p],a[r];z=a[r][c];a[r]=[v/z for v in a[r]]
  for i in range(len(a)):
   if i!=r and a[i][c]:
    z=a[i][c];a[i]=[u-z*v for u,v in zip(a[i],a[r])]
  piv.append(c);r+=1
  if r==len(a):break
 return a,piv

def inverse(a):
 n=len(a);red,piv=rref([row+[Q(i==j)for j in range(n)]for i,row in enumerate(a)],n)
 need(len(piv)==n,'nonsingular query prefix');return [r[n:]for r in red]
@lru_cache(None)
def kernel(rows,n):
 red,piv=rref(rows,n);out=[]
 for j in range(n):
  if j in piv:continue
  v=[Q(0)]*n;v[j]=1
  for i,c in enumerate(piv):v[c]=-red[i][j]
  out.append(tuple(v))
 return tuple(out)
def normalize(row):
 d=0
 for v in row:d=gcd(d,abs(v))
 if not d:return ()
 sign=1 if next(v for v in row if v)>0 else -1
 return tuple(v*sign//d for v in row)

def root_geometry():
 hosts=[i for i in range(N)if i!=PIVOT];ix={h:j+1 for j,h in enumerate(hosts)};events=[]
 for i in range(N):
  x=[0]*N;y=[0]*N;y[0]=1
  if i<PIVOT:
   x[0]=1;x[ix[i]]=-1;y[ix[i]]=1
   for j in hosts:
    if j<i:x[ix[j]]=-2
   mask={0}|{ix[j]for j in hosts if j<=i}
  elif i>PIVOT:
   x[0]=-1;x[ix[i]]=1;y[ix[i]]=1
   for j in hosts:
    if j>i:x[ix[j]]=2
   mask={0}|{ix[j]for j in hosts if j>=i}
  else:
   for j in hosts:x[ix[j]]=-1 if j<PIVOT else 1
   mask=set(range(N))
  events.append((i,x,y,mask))
  if i==PIVOT:
   x=[0]*N;y=[0]*N;x[0]=-1;y[0]=2
   for j in hosts:
    if j>PIVOT:x[ix[j]]=2
    y[ix[j]]=(-1)**(j if j<PIVOT else N-1-j)
   events.append((None,x,y,set()))
 U=eye(N);alpha=[];beta=[];prefix=[];old=[]
 for site,x,y,mask in events:
  need(dot(x,y)==0,'nilpotent query')
  if site is not None:
   V=inverse(U);prefix.append((U,V));old.append(mask)
   ar=[dot(y,c)for c in zip(*U)];br=[dot(row,x)for row in V]
   need(all(v.denominator==1 for v in ar+br),'integral transported query coordinates')
   alpha.append(tuple(map(int,ar)));beta.append(tuple(map(int,br)))
   need(mm(U,V)==eye(N),'independently inverted prefix')
  T=[[Q(i==j)-2*x[i]*y[j]for j in range(N)]for i in range(N)];U=mm(T,U)
 need(U==[[-Q(i==j)for j in range(N)]for i in range(N)],'query root endpoint')
 return ix,events,prefix,old,alpha,beta
@lru_cache(None)
def log_bounds(n):
 k=n.bit_length()-1;z=Q(n-2**k,n+2**k)
 def series(z):
  term=z;total=Q(0)
  for j in range(110):total+=term/(2*j+1);term*=z*z
  tail=2*term/(221*(1-z*z));return 2*total,2*total+tail
 a,b=series(Q(1,3));c,d=series(z);return k*a+c,k*b+d

def exp_bounds(z):
 need(0<=z<1,'positive exponential range');s=term=Q(1)
 for j in range(1,33):term*=z/j;s+=term
 nxt=term*z/33;return s,s+nxt/(1-z/34)
@lru_cache(None)
def power(n):
 lo,hi=log_bounds(n);elo,_=exp_bounds(K*lo);_,ehi=exp_bounds(K*hi)
 return Q(n)/ehi,Q(n)/elo

def interval_sum(hist):
 lo=hi=Q(0)
 for n,c in hist.items():
  a,b=power(n)
  if c>=0:lo+=c*a;hi+=c*b
  else:lo+=c*b;hi+=c*a
 return lo,hi

def native(path):
 out={}
 for node in ast.parse(path.read_text()).body:
  if isinstance(node,ast.Assign):
   for name in node.targets:
    if isinstance(name,ast.Name)and name.id in('HELPERS','LOCAL_PAID'):out[name.id]=Counter(ast.literal_eval(node.value))
 need(len(out)==2,'native histogram literal source');return out['HELPERS'],out['LOCAL_PAID']

def run_case(cert,geom,nt,np):
 ix,events,prefix,old,alpha,beta=geom;kl,kr=cert['kl'],cert['kr'];ms=[s.copy()for s in old]
 for i in range(PIVOT):ms[i]|={ix[j]for j in range(PIVOT+1,PIVOT+1+kr)}
 for i in range(PIVOT+1,N):ms[i]|={ix[j]for j in range(PIVOT-kl,PIVOT)}
 for i,(U,V)in enumerate(prefix):
  mask=ms[i];Pi=[[Q(r==c and r in mask)for c in range(N)]for r in range(N)]
  need(mm(V,mm(Pi,U))==Pi,'actual query-conjugated mask equals coordinate mask')
 d=[len(s)-2 for s in ms];weights=cert['weights'];need(len(weights)==N,'dual dimension')
 price=[0]
 for m in range(1,N+1):
  lo,hi=power(8*m);a=(lo*SCALE).__floor__();b=(hi*SCALE).__floor__();need(a==b,'independent exact price floor');price.append(a)
 masks=[sum(1<<c for c in s)for s in ms];cache={};prepared={};counts=Counter();feasible=violating=0
 def capacity(mask,subset):
  if not mask:return 0
  if mask not in prepared:
   cs=[c for c in range(N)if mask>>c&1]
   prepared[mask]=(cs,[normalize([row[c]for c in cs])for row in alpha],[normalize([row[c]for c in cs])for row in beta])
  cs,ar,br=prepared[mask];inds=[i for i in range(N)if subset>>i&1]
  aa=tuple(sorted({ar[i]for i in inds if ar[i]}));bb=tuple(sorted({br[i]for i in inds if br[i]}));key=(mask,aa,bb)
  if key not in cache:
   u=kernel(aa,len(cs));v=kernel(bb,len(cs))
   gram=[[dot(a,b)for b in v]for a in u]
   cache[key]=len(rref(gram,len(v))[1]) if u and v else 0
  return cache[key]
 size=1<<N;common=[0]*size;sums=[0]*size;common[0]=(1<<N)-1
 for subset in range(1,size):
  bit=subset&-subset;i=bit.bit_length()-1;rest=subset^bit
  common[subset]=common[rest]&masks[i];sums[subset]=sums[rest]+weights[i]
  c=capacity(common[subset],subset);counts[c]+=1
  if c:
   feasible+=1
   need(sums[subset]<=price[subset.bit_count()],f'dual infeasibility {(kl,kr,subset)}')
  if sums[subset]>price[subset.bit_count()]:violating+=1;need(c==0,'excluded underpriced subset')
 need(feasible==cert['feasible_jobs'],'independent all-subset feasible count')
 value=sum(a*b for a,b in zip(d,weights));need(value==cert['paid_lower_units'],'dual demand objective')
 target=Counter(1+8*sum(c in s for s in ms)for c in range(N));base=Counter({r:18*c for r,c in nt.items()});base.subtract({r:18*c for r,c in np.items()});base.update({r:104*c for r,c in target.items()});base[1]-=104
 mass=sum(r*c for r,c in base.items())-104*8*sum(d);need(mass==760,'complete rank mass with every idle incidence')
 lo,hi=interval_sum(base);lo-=104*Q(value,SCALE);hi-=104*Q(value,SCALE)
 need(hi<0,'independent complete negative margin');need(hi<=Q(cert['margin_upper_units'],SCALE),'published rounded margin upper valid')
 return dict(kl=kl,kr=kr,subsets=size-1,feasible_jobs=feasible,capacity_histogram=dict(counts),exact_nullspace_cache=len(cache),price_violating_subsets=violating,paid_lower_units=value,complete_margin_upper_units=(hi*SCALE).__ceil__(),margin_diagnostic=float(hi),rank_surplus=mass)
def controls(geom):
 def pairing(a,b,n):
  u=kernel(tuple(map(tuple,a)),n);v=kernel(tuple(map(tuple,b)),n)
  return len(rref([[dot(x,y)for y in v]for x in u],len(v))[1])if u and v else 0
 need(pairing([[1,0]],[[1,0]],2)==1,'product term is necessary')
 need(pairing([[1,0]],[[0,1]],2)==0,'dual annihilation is necessary')
 ix,events,prefix,old,alpha,beta=geom;ms=[s.copy()for s in old]
 for i in range(8):ms[i]|={ix[j]for j in range(9,14)}
 for i in range(9,18):ms[i]|={ix[j]for j in range(3,8)}
 sites=(4,8,9);cs=sorted(set.intersection(*(ms[i]for i in sites)))
 rawx=[e[1]for e in events if e[0]is not None];rawy=[e[2]for e in events if e[0]is not None]
 true=pairing([[alpha[i][c]for c in cs]for i in sites],[[beta[i][c]for c in cs]for i in sites],len(cs))
 wrong=pairing([[rawy[i][c]for c in cs]for i in sites],[[rawx[i][c]for c in cs]for i in sites],len(cs))
 need((true,wrong)==(5,4),'omitting query conjugation changes the capacity')
 return dict(product_term_needed=True,dual_annihilation_needed=True,conjugation_counterexample=dict(kl=5,kr=5,sites=list(sites),transported_capacity=true,untransported_capacity=wrong))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root-package',type=Path,required=True);ap.add_argument('--duals',type=Path,default=HERE/'DUALS.json');ap.add_argument('--emit',action='store_true');args=ap.parse_args()
 pins=json.loads((HERE/'REVIEW-SOURCE-PINS.json').read_bytes())
 for path,key in[(args.duals,'duals_sha256'),(args.root_package/'check.py','root_source_sha256'),(args.root_package/'accounting/retained/pricing-6833.py','native_source_sha256')]:need(hashlib.sha256(path.read_bytes()).hexdigest()==pins[key],'review source SHA256 '+key)
 document=json.loads(args.duals.read_bytes());need(document['scale']==SCALE and document['kappa']=='0.00337180','dual parameters');certs=document['cases'];chosen=[(0,0),(5,5),(7,8),(8,9)];geom=root_geometry();nt,np=native(args.root_package/'accounting/retained/pricing-6833.py');results=[]
 for pair in chosen:
  cert=next(c for c in certs if(c['kl'],c['kr'])==pair);t=time.time();r=run_case(cert,geom,nt,np);results.append(r);print(pair,r['feasible_jobs'],r['margin_diagnostic'],'seconds',time.time()-t,flush=True)
 receipt=dict(status='PASS_INDEPENDENT_ENLARGED_MASK_REVIEW',controls=controls(geom),selected_cases=results,dual_snapshot_sha256=hashlib.sha256(args.duals.read_bytes()).hexdigest(),root_source_sha256=hashlib.sha256((args.root_package/'check.py').read_bytes()).hexdigest(),source_native_sha256=hashlib.sha256((args.root_package/'accounting/retained/pricing-6833.py').read_bytes()).hexdigest(),limits='All-subset direct-nullspace checks for four selected certificates; benchmark-only, no derivative/reentry or whole-multiplier proof.')
 receipt=json.loads(json.dumps(receipt))
 if args.emit:(HERE/'REVIEW-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 else:need(receipt==json.loads((HERE/'REVIEW-RESULT.json').read_bytes()),'exact independent receipt')
 print(receipt['status'])
if __name__=='__main__':main()
