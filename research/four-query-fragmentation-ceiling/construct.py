#!/usr/bin/env python3
"""Exact four-query equal-orientation binary module.
Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Native/binary lineage: Cinna Davis, Ali Romman #6348/#6398,
thu-nmrc #6716, zxv #6726. Three-query obstruction: #6764.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

def need(x,message):
 if not x:raise ValueError(message)
def construct():
 return [('IDLE',0,'L'),('IDLE',1,'L'),('NATIVE','L',3,2),('SCALE',2,-1),('QUERY',2,3),('ADD',2,3,-1),('ADD',3,2,1),('QUERY',2,3),('SCALE',2,-1),('ADD',2,3,1),('NATIVE','R',0,1),('IDLE',4,'R'),('IDLE',5,'R')]
def plus(a,b,c=1):
 out=a.copy()
 for k,v in b.items():
  z=out.get(k,0)+c*v
  if z:out[k]=z
  elif k in out:del out[k]
 return out
def shift(a,body=None,central=False):
 out={}
 for(s,l,r),v in a.items():
  k=(s^int(central),l+int(body=='L'),r+int(body=='R'));out[k]=out.get(k,0)+v
 return {k:v for k,v in out.items()if v}
def replay(word):
 A=[[{(0,0,0):1}if i==j else {}for j in range(6)]for i in range(6)]
 for e in word:
  op=e[0]
  if op=='ADD':
   _,d,s,c=e;A[d]=[plus(x,y,c)for x,y in zip(A[d],A[s])]
  elif op=='SCALE':A[e[1]]=[{k:e[2]*v for k,v in x.items()}for x in A[e[1]]]
  elif op=='QUERY':
   _,d,s=e;A[d]=[plus(x,shift(y,central=True))for x,y in zip(A[d],A[s])]
  elif op=='NATIVE':
   _,body,d,s=e;A[d]=[plus(x,shift(y,central=True))for x,y in zip(A[d],A[s])]
   for role in(d,s):A[role]=[shift(x,body=body)for x in A[role]]
  elif op=='IDLE':A[e[1]]=[shift(x,body=e[2])for x in A[e[1]]]
  else:raise ValueError(op)
 return A
def target():
 A=[[{}for _ in range(6)]for _ in range(6)]
 for i in(0,1):A[i][i]={(0,1,1):1}
 A[0][1]={(1,1,1):1}
 for i in(2,3):A[i][i]={(1,1,0):1}
 for i in(4,5):A[i][i]={(0,0,1):1}
 return A
def expanded(word):
 out=[]
 for e in word:
  if e[0]in('QUERY','NATIVE'):
   d,s=e[-2:];out.append(['LAMBDA',d,-1]);out.append(['QUERY',d,s,-1]if e[0]=='QUERY'else['LOCAL',1 if e[1]=='L'else 2,s,d]);out.append(['LAMBDA',d,1])
  elif e[0]=='IDLE':out.append(['IDLE_ONE',e[1],[1 if e[2]=='L'else 2]])
  else:out.append(list(e))
 return out
def zadd(a,b):return a[0]+b[0],a[1]+b[1]
def zmul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def cpadd(a,b,c=(Q(1),Q(0))):
 out=a.copy()
 for k,v in b.items():
  z=zadd(out.get(k,(Q(0),Q(0))),zmul(c,v))
  if z!=(0,0):out[k]=z
  elif k in out:del out[k]
 return out
def cpshift(a,dq=0,l=0,r=0):return {((k[0]+dq)%4,k[1]+l,k[2]+r):v for k,v in a.items()}
def complex_replay(events):
 A=[[{(0,0,0):(Q(1),Q(0))}if i==j else {}for j in range(6)]for i in range(6)]
 for e in events:
  op=e[0]
  if op=='ADD':A[e[1]]=[cpadd(a,b,(Q(e[3]),Q(0)))for a,b in zip(A[e[1]],A[e[2]])]
  elif op=='SCALE':A[e[1]]=[{k:zmul((Q(e[2]),Q(0)),v)for k,v in a.items()}for a in A[e[1]]]
  elif op in('QUERY','LOCAL'):
   if op=='QUERY':_,d,s,dq=e;stage=None
   else:_,stage,s,d=e;dq=-1
   A[d]=[cpadd(a,cpshift(b,dq))for a,b in zip(A[d],A[s])]
   if stage:
    for role in(d,s):A[role]=[cpshift(a,l=int(stage==1),r=int(stage==2))for a in A[role]]
  elif op=='IDLE_ONE':A[e[1]]=[cpshift(a,l=int(1 in e[2]),r=int(2 in e[2]))for a in A[e[1]]]
  elif op=='LAMBDA':
   sign=e[2];A[e[1]]=[cpadd({k:zmul((Q(1,2),Q(sign,2)),v)for k,v in a.items()},cpshift(a,2),(Q(1,2),Q(-sign,2)))for a in A[e[1]]]
  else:raise ValueError(op)
 return A
def complex_target():
 out=[]
 for row in target():
  result=[]
  for a in row:
   b={}
   for(s,l,r),v in a.items():
    if not s:b[(0,l,r)]=(Q(v),Q(0))
    else:b[(3,l,r)]=(Q(v,2),Q(v,2));b[(1,l,r)]=(Q(v,2),Q(-v,2))
   result.append(b)
  out.append(result)
 return out
def main():
 source=Path(__file__).resolve().parent/'frozen'/'caller6726.py'
 need(sha256(source.read_bytes()).hexdigest()=='e99e4287091c6ce4ec9a563cb9ac6f45be35ff1ef421b4efa8c200cb9d639d6c','Pinned source interface bytes')
 word=construct();want=target();need(replay(word)==want,'All36 arbitrary-input formal entries')
 events=expanded(word);need(complex_replay(events)==complex_target(),'All q^4/Gaussian coefficients')
 final_events=events+[['LAMBDA',2,-1],['LAMBDA',3,-1]]
 final=complex_target()
 final[2][2]=final[3][3]={(3,1,0):(Q(1),Q(0))}
 need(complex_replay(final_events)==final,'Auxiliary target phase normalization')
 prefix=replay(word[:10]);need(prefix[2][2]=={(1,1,0):1}and prefix[3][3]=={(1,1,0):1},'Two completed SL prefixes')
 need(all(prefix[r][j]==({(0,0,0):1}if r==j else {})for r in(4,5)for j in range(6)),'Fresh inputs untouched')
 controls=[]
 for i,e in enumerate(word):
  need(replay(word[:i]+word[i+1:])!=want,'Omitted literal gate rejected');controls.append('omit_'+str(i)+'_'+e[0])
 for i,e in enumerate(events):
  if e[0]=='LAMBDA':
   bad=deepcopy(events);bad[i][-1]*=-1;need(complex_replay(bad)!=complex_target(),'Wrong absolute phase rejected');controls.append('wrong_lambda_'+str(i))
 for a,b in((8,8),(8,32),(16,8),(8,8*(1<<80))):
  T=Counter();P=Counter()
  for r,c in((a+1,2),(b,2),(a+b+1,-2)):T[r]+=c
  for r,c in((a,2),(b,2),(1,1),(a+b,-2)):P[r]+=c
  T.subtract(P);formula=Counter()
  for r,c in((a+1,2),(a,-2),(a+b+1,-2),(a+b,2),(1,-1)):formula[r]+=c
  need(all(T[x]==formula[x]for x in set(T)|set(formula)),'Complete signed tariff')
 receipt={'schema':'four-query-equal-fragment-module/1','normalized_gates':word,'complex_events':events,'auxiliary_target_normalizers':[['LAMBDA',2,-1],['LAMBDA',3,-1]],'source_interface_sha256':sha256(source.read_bytes()).hexdigest(),'native_calls':2,'thin_queries':2,'header_queries':4,'arbitrary_inputs':6,'body_idles':{'L':2,'R':2},'controls':controls,'endpoint':'LR(X+SY), LR Y, SL A, SL B, R E, R F','local_signed_change':'2*(i(a)-i(a+b))-1','scope':'Exact atomic-supplier module; no complete supplier admission or new kappa.'}
 text=json.dumps(receipt,indent=2,sort_keys=True)+'\n';print(text,end='');print('CERTIFICATE_SHA256',sha256(text.encode()).hexdigest());print('PASS_FOUR_QUERY_EQUAL_FRAGMENTS')
if __name__=='__main__':main()
