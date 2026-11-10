"""Exact scoped geometry/invoice checks. @CubeJerry/OpenAI assistance. Apache-2.0.
No native, physical-fragment, compiler or theorem-admission replay is claimed.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import hashlib,importlib.util,json,sys
HERE=Path(__file__).resolve().parent

def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
L=load(HERE/'linear.py','pair_linear')
for name in ('mat','eye','tr','mm','add','rank','span','inv','canonical','closure','lin_solve'):globals()[name]=getattr(L,name)
def need(ok,msg):
 if not ok:raise ValueError(msg)
def outer(u,v):return mm(tr([u]),[v])
def scale(M,c):return [[c*x for x in r]for r in M]
def zero():return [[F(0)]*8 for _ in range(8)]
def nz(M):return any(any(r)for r in M)
def null(rows):return lin_solve(rows,[F(0)]*len(rows))[1]
def dot(u,v):return sum(x*y for x,y in zip(u,v))
def col(M,u):return tr(mm(M,tr([u])))[0]
def row(v,M):return mm([v],M)[0]
def pbuild(z,a):
 P=zero()
 for i in range(3):P[i][i]=1;P[i][3:]=[(-1)**i*x for x in a]
 for i in range(5):P[i+3][3:]=[z[i]]*5
 need(sum(z)==1 and dot(a,z)==0,'P parameter constraints')
 need(mm(P,P)==P and rank(P)==4,'P idempotent rank4')
 return P

def fixture(z3,s):
 z3,s=F(z3),F(s);z4=1-z3;delta=s+1;need(delta,'Nonzero pairing')
 z=[z3,z4,F(0),F(0),F(0)];a=[z4,-z3,s,s,s];P=pbuild(z,a)
 w=[s,-s,s]+z;c=[F(1)]*3+[x+1 for x in a];T=scale(outer(w,c),1/delta);Q=add(add(I,P,-1),T)
 def endpoint(u,v,E):
  X=add(E,T,-1);x=col(X,u);y=row(v,X);g=dot(x,y);need(g,'Endpoint pairing')
  return add(T,scale(outer(x,y),1/g))
 return [endpoint(us[0],vs[0],P),P,Q,endpoint(us[8],vs[8],Q)]

def inventory(Ps):
 result={}
 for mask in range(16):
  E=I
  for j,P in enumerate(Ps):E=mm(E,P if mask>>j&1 else add(I,P,-1))
  if rank(E):result[mask]=rank(E)
 return result

def stage_identity(stages,character):
 # Coefficients in independent formal body variables; all input columns remain.
 def body(word,bit,P):
  out={}
  for mask,M in word.items():
   for dest,N in ((mask,mm(add(I,P,-1),M)),(mask|(1<<bit),mm(P,M))):out[dest]=add(out.get(dest,zero()),N)
  return {m:M for m,M in out.items()if nz(M)}
 word={0:I}
 for site,R in enumerate(Rs):
  query=add(I,R,character-1);word={mask:mm(query,M)for mask,M in word.items()}
  if site in stages:word=body(word,*stages[site])
 expected={0:scale(I,F(character))}
 for _,(bit,P)in sorted(stages.items()):expected=body(expected,bit,P)
 return word==expected

def full_invoice(helpers,paid,idles):
 T=Counter({r:18*n for r,n in helpers.items()});P=Counter({r:18*n for r,n in paid.items()})
 for size,count in {2:8,4:4}.items():T[8*size+1]+=208*count;P[8*size]+=208*count
 # Build main targets from the independently checked joint eigenspaces.
 Ps=fixture(1,0);invty=inventory(Ps);group_leaves=(4,5,5,4)
 for mask,multiplicity in invty.items():
  size=sum(n for j,n in enumerate(group_leaves)if mask>>j&1)
  T[8*size+1]+=104*multiplicity
 # Grant exactly one pure-bank fragment each: debit its old target first.
 for pure_mask in (2,4):
  need(invty.get(pure_mask,0)>=1,'Fragment requires an actual independent pure-bank target')
  T[41]-=104;T[32]+=104;T[9]+=104
 expected_idles=(rank(Ps[1])-2-1)+(rank(Ps[2])-2-1)
 need(idles==expected_idles,'Every remaining whole idle must be paid')
 P[1]+=(9-6+18-6)*104
 P[40]+=idles*104;P[32]+=208;P[8]+=208
 return T,P

def encode(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [encode(v)for v in x]
 return x

if (HERE/'FROZEN.json').exists():
 frozen=json.loads((HERE/'FROZEN.json').read_text())
 for relative,digest in frozen['sha256'].items():
  need(hashlib.sha256((HERE/relative).read_bytes()).hexdigest()==digest,'Frozen package file: '+relative)
sources=json.loads((HERE/'ORIGINS.json').read_text())
for s in sources['files']:
 data=(HERE/s['local']).read_bytes()
 if 'commit' in s:need('git_blob' in s and 'repository' in s,'Original source requires exact repository and Git blob')
 need(hashlib.sha256(data).hexdigest()==s['sha256'],'Retained source SHA256')
 if 'git_blob' in s:
  git_header=b'blob '+str(len(data)).encode()+b'\0'
  need(hashlib.sha1(git_header+data).hexdigest()==s['git_blob'],'Retained source Git blob')
theorem_source=sources['inherited_theorems']
retained_theorem=next(s for s in sources['files']if s['local']==theorem_source['local'])
need(all(theorem_source[k]==retained_theorem[k]for k in ('repository','commit','path','git_blob','sha256')),'Inherited theorem pin matches retained exact source')
us,vs,Rs,Bs=canonical(8);I=eye(8)
# Source positive control: frozen mixed-orientation pair placement remains legal.
root=json.loads((HERE/'inputs/pr6726-ROOT.json').read_text());oldR=[mat(M)for M in root['queries']];oldB=[];M=I
for R in oldR:M=mm(add(I,R,-2),M);oldB.append(M)
need(M==scale(I,F(-1)),'Original shortest-query scalar endpoint')
need(all(rank(R)==1 and not nz(mm(R,R))for R in oldR),'Original rank-one nilpotent queries')
oldP=[]
for site,mask in zip(root['full_sites'],root['masks']):
 P=[[F(i==j and(mask>>i&1))for j in range(8)]for i in range(8)]
 need(mm(P,oldR[site])==oldR[site]and mm(oldR[site],P)==oldR[site],'Original local compatibility')
 need(mm(P,oldB[site])==mm(oldB[site],P),'Original actual prefix');oldP.append(P)
need(root['full_sites']==[0,1,2,6,7,8]and oldP[1]==oldP[2]and oldP[3]==oldP[4],'Original pair sites')
need(rank(oldP[1])==rank(oldP[3])==4,'Mixed-orientation positive control')
# Actual reduced spectral block underlying the universal forced-E argument.
u4,v4,R4,B4=canonical(4);J4=eye(4)
rker=null(add(B4[1],J4)+add(B4[2],J4));lker=null(tr([x+y for x,y in zip(add(B4[1],J4),add(B4[2],J4))]))
A4,C4=closure(u4[1:3],v4[1:3],B4[1:3])
need(len(rker)==len(lker)==1,'Common minus-one eigenspaces')
need(nz(mm(C4,tr(rker)))and nz(mm(lker,A4)),'No off-diagonal spectral mixing')
need(len(A4[0])+len(C4)-rank(mm(C4,A4))==4,'Reduced block forced full rank')
E=zero()
for i in range(5):
 for j in range(5):E[i][j]=F((-1)**i)
for i in range(5,8):E[i][i]=1
need(mm(E,E)==E and rank(E)==4,'Forced pair-five projector')
for zz,aa in [([0,0,1,0,0],[0,0,0,0,0]),([1,0,0,0,0],[0,-1,2,3,4]),([0,1,0,0,0],[1,0,0,1,-1]),([F(1,2),F(1,2),0,0,0],[1,-1,2,-2,1])]:
 P=pbuild(list(map(F,zz)),list(map(F,aa)))
 need(all(mm(P,Rs[j])==Rs[j]and mm(Rs[j],P)==Rs[j]and mm(P,Bs[j])==mm(Bs[j],P)for j in(1,2)),'General P fixtures satisfy actual prefixes')
 rk=null(P+E);lk=null(tr([r+s for r,s in zip(P,E)]))
 need(len(rk)<=1 and len(lk)<=1 and all(not dot(x,y)for x in rk for y in lk),'Common-kernel dimensions and zero pairing')
fixture_receipts=[]
for z3,s in [(1,0),(0,1),(F(1,2),F(-1,2)),(F(-1,2),-2)]:
 Ps=fixture(z3,s);left,P,Q,right=Ps
 need([rank(X)for X in Ps]==[2,4,5,2]and all(mm(X,X)==X for X in Ps),'Fixture ranks/idempotence')
 need(all(mm(X,Y)==mm(Y,X)for X in Ps for Y in Ps),'All four projectors commute')
 need(mm(Q,E)==E and mm(E,Q)==E and mm(Q,add(I,P,-1))==add(I,P,-1),'Forced containment and kernel identity')
 stages={0:(0,left),1:(1,P),2:(2,P),5:(3,Q),6:(4,Q),8:(5,right)}
 for site,(_,X)in stages.items():
  need(mm(X,Rs[site])==Rs[site]and mm(Rs[site],X)==Rs[site],'All local queries supported')
  need(mm(X,Bs[site])==mm(Bs[site],X),'All actual prefix conditions')
 invty=inventory(Ps);need(invty=={2:2,3:1,4:3,12:1,15:1},'Complete target incidence')
 need(stage_identity(stages,1)and stage_identity(stages,-1),'Every formal stage and arbitrary-input matrix coefficient')
 fixture_receipts.append({'z3':z3,'s':s,'inventory':invty,'formal_coefficients_per_character':4096})
# A locally compatible rank-five candidate that omits the actual prefix premise.
z=list(map(F,[1,0,1,-1,0]));a=list(map(F,[0,-1,-1,-1,-2]));P=pbuild(z,a)
w=[F(-1),F(1),F(-1)]+z;c=[F(1)]*3+[x+2 for x in a];Q=add(add(I,P,-1),outer(w,c))
need(mm(Q,Q)==Q and rank(Q)==5 and mm(P,Q)==mm(Q,P),'Failed-prefix fixture passes local rank/commutation')
need(all(mm(Q,Rs[j])==Rs[j]and mm(Rs[j],Q)==Rs[j]for j in(5,6)),'Failed-prefix fixture passes both local supports')
need(any(mm(Q,Bs[j])!=mm(Bs[j],Q)for j in(5,6)),'Actual prefix rejects local-only fixture')
bad={1:(0,P),2:(1,P),5:(2,Q),6:(3,Q)}
need(stage_identity(bad,1)and not stage_identity(bad,-1),'Formal central endpoint rejects local-only fixture')
pricing=load(HERE/'inputs/pr6726-pricing.py','retained_price');local={'helpers':pricing.HELPERS,'paid':pricing.LOCAL_PAID}
oldT,oldPaid=pricing.formula_invoice(local);T,paid=full_invoice(local['helpers'],local['paid'],3)
delta=Counter(T);delta.subtract(paid);delta.subtract(oldT);delta.update(oldPaid);delta={r:n for r,n in delta.items()if n}
need(delta=={41:104,40:-104,1:-104},'Exact complete invoice delta with full target debit')
need(sum(T.values())==13670 and sum(paid.values())==66956,'Complete granted target/paid census')
need(sum(r*n for r,n in T.items())-sum(r*n for r,n in paid.items())==760,'Full rank-mass surplus')
try:full_invoice(local['helpers'],local['paid'],2)
except ValueError:missing_idle_rejected=True
else:missing_idle_rejected=False
need(missing_idle_rejected,'Missing third idle negative control')
receipt={'status':'PASS_SCOPED_SCALAR_PAIR_RANK5_INVOICE_OBSTRUCTION','source_head':sources['predecessor']['head'],
 'scope':'Eight fields; pair(1,2) rank4; pair(5,6) rank4 or5; actual prefixes; rank2 endpoints; exactly one optimistically granted fragment in each pure paired bank. No new kappa.',
 'rank5_fixtures':fixture_receipts,'source_positive_control':'Frozen #6726 mixed pairs(1,2),(6,7), ranks4,4',
 'negative_controls':{'local_only_prefix_rejected':True,'wrong_central_endpoint_rejected':True,'missing_third_idle_rejected':missing_idle_rejected},
 'candidate_granted_invoice':{'targets':T,'paid':paid,'productive_fields':sum(T.values()),'paid_requests':sum(paid.values()),'rank_mass_surplus':760},
 'exact_signed_delta':delta,'universal_price_comparison':'candidate-reference = 104*(H(8(d+e)+1)-H(8(d+e))-1)<0 for 0<k<1',
 'not_checked':['physical paid fragments','native supplier scientific replay','ordinary compiler qualification','all-size framework assumptions']}
rendered=json.dumps(encode(receipt),indent=2,sort_keys=True)+'\n'
if '--write'in sys.argv:(HERE/'RESULT.json').write_text(rendered)
else:need((HERE/'RESULT.json').read_text()==rendered,'Retained receipt matches exact replay')
print(rendered,end='')
