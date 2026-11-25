"""One bounded exact rational nine-factor masked-completion discovery pass.

Apache-2.0. Cinna Davis with substantial OpenAI Codex assistance.
The masked-decoder geometry, candidate ABI and independent rank oracle are
reused from the credited masked-e8-padding-transfer package.
"""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
from math import gcd,lcm
from hashlib import sha256
import argparse,importlib.util,json,random,time
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
OUT=args.output
OUT.mkdir(parents=True,exist_ok=False)
SOURCE=ROOT/'research/masked-e8-padding-transfer/verify.py'
PINS=json.loads((Path(__file__).parent/'SOURCES.json').read_text())
if sha256(SOURCE.read_bytes()).hexdigest()!=PINS['source_sha256']:
 raise ValueError('Changed exact masked-decoder source')
s=importlib.util.spec_from_file_location('mask',ROOT/'research/masked-e8-padding-transfer/verify.py');M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
R=M.LINES;B=M.PAIRING
fids=[i for i,r in enumerate(R) if any(set(j for j,v in enumerate(r)if v)=={2*k,2*k+1} for k in range(4))]
assert len(fids)==8
C=[[sum(a*b for a,b in zip(r,R[j]))//4 for j in fids]for r in R]
assert all(sum(x*x for x in r)==4 for r in C)
rng=random.Random(20261023)
start=time.monotonic();deadline=start+300
@lru_cache(maxsize=200000)
def cost(a,b):
 rows=[];basis={}
 while a:
  k=(a&-a).bit_length()-1;a&=a-1;x=B[k]&b
  while x:
   h=x.bit_length()-1
   if h in basis:x^=basis[h]
   else:basis[h]=x;break
 return len(basis)
def support(v):return sum(1<<i for i,x in enumerate(v)if x)
def term(p,q,w):
 for v in (p,q):
  g=0
  for x in v:g=gcd(g,abs(x))
  if g>1:
   for j in range(len(v)):v[j]//=g
   w*=g
  z=next((x for x in v if x),1)
  if z<0:
   for j in range(len(v)):v[j]=-v[j]
   w=-w
 return tuple(p),tuple(q),w
def combineq(qj,qi,wj,wi,alpha):
 a,b=wj,-alpha*wi;d=lcm(a.denominator,b.denominator)
 aa=a.numerator*(d//a.denominator);bb=b.numerator*(d//b.denominator)
 return tuple(aa*x+bb*y for x,y in zip(qj,qi)),Q(1,d)
def checksum(terms):
 return sha256(repr(terms).encode()).hexdigest()
def total(terms):return sum(cost(support(p),support(q))for p,q,w in terms if w)
results=[]
for domain in ('P112','P120'):
 live=[i for i in range(120)if domain=='P120'or i not in fids];baseline=64 if domain=='P112'else 72
 for case in range(4):
  if time.monotonic()>deadline:break
  anchor=live[(case*29)%len(live)];neighbors=[j for j in live if not(B[anchor]>>j&1)]
  chosen=rng.sample(neighbors,2+case%2)
  A=[i for i in live if all(not(B[i]>>j&1)for j in chosen)]
  D=[j for j in live if all(not(B[i]>>j&1)for i in A)]
  ka=max(range(8),key=lambda k:sum(C[i][k]!=0 for i in A));kb=max(range(8),key=lambda k:sum(C[i][k]!=0 for i in D))
  u=tuple(C[i][ka]if i in A else 0 for i in range(120));v=tuple(C[i][kb]if i in D else 0 for i in range(120))
  assert any(u)and any(v)and cost(support(u),support(v))==0
  terms=[term([C[i][k]if i in live else 0 for i in range(120)],[C[i][k]if i in live else 0 for i in range(120)],Q(1,4))for k in range(8)]
  terms.append(term(list(u),list(v),Q(1,4)))
  assert total(terms)==baseline
  initial=terms[:];current=best=baseline;moves=[];seen={checksum(terms)}
  for step in range(32):
   if time.monotonic()>deadline:break
   chosen_move=None;chosen_key=None
   for i in range(9):
    pi,qi,wi=terms[i]
    for j in range(9):
     if i==j:continue
     pj,qj,wj=terms[j]
     alphas={-Q(x,y)for x,y in zip(pi,pj)if x and y}
     alphas|={wj*x/(wi*y)for x,y in zip(qj,qi)if x and y}
     old=cost(support(pi),support(qi))+cost(support(pj),support(qj))
     for alpha in sorted(alphas):
      if max(abs(alpha.numerator).bit_length(),alpha.denominator.bit_length())>12:continue
      d,n=alpha.denominator,alpha.numerator
      np=tuple(d*x+n*y for x,y in zip(pi,pj));nq,nw=combineq(qj,qi,wj,wi,alpha)
      if not any(np)or not any(nq):continue
      if max(abs(x).bit_length()for x in (*np,*nq))>192:continue
      delta=cost(support(np),support(qi))+cost(support(pj),support(nq))-old
      if current+delta>baseline+2:continue
      # A fixed seeded tie break gives one pass, rather than automatic rerolls.
      key=(delta,rng.random())
      if chosen_key is not None and key>=chosen_key:continue
      ti=term(list(np),list(qi),wi/d);tj=term(list(pj),list(nq),nw)
      trial=terms[:];trial[i]=ti;trial[j]=tj;digest=checksum(trial)
      if digest in seen:continue
      chosen_key=key;chosen_move=(trial,digest,i,j,alpha,delta)
   if chosen_move is None:break
   terms,digest,i,j,alpha,delta=chosen_move;seen.add(digest);current+=delta;best=min(best,current)
   moves.append({'i':i,'j':j,'alpha':str(alpha),'cost':current})
   assert current==total(terms)
   if current<baseline:
    out={'domain':domain,'case':case,'cost':current,'terms':[[list(p),list(q),str(w)]for p,q,w in terms],'moves':moves}
    (OUT/'HIT.json').write_text(json.dumps(out,indent=2));print('HIT',domain,case,current,flush=True)
    # Independent full masked matrix and both binary-rank oracles.
    normalized=[(tuple(Q(x)for x in p),tuple(w*x for x in q))for p,q,w in terms]
    print(M.validate(live,normalized),flush=True);raise SystemExit(0)
  check=[(tuple(Q(x)for x in p),tuple(w*x for x in q))for p,q,w in terms]
  receipt=M.validate(live,check)
  row={'domain':domain,'case':case,'anchor':anchor,'rectangle_sizes':[len(A),len(D)],'nonzero_supports':[sum(bool(x)for x in u),sum(bool(x)for x in v)],'moves':moves,'minimum':best,'final':receipt,'matrix_sha256':checksum(terms)}
  results.append(row);print(domain,case,'best',best,'last',current,'steps',len(moves),'seconds',round(time.monotonic()-start,1),flush=True)
  (OUT/'CHECKPOINT.json').write_text(json.dumps({'seed':20261023,'seconds':time.monotonic()-start,'results':results},indent=2))
print('DONE_BOUNDED_DISCOVERY',len(results),'seconds',round(time.monotonic()-start,1),flush=True)
