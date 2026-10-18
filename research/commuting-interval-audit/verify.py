#!/usr/bin/env python3
"""Free interval algebra versus literal pinned dispatch and dense matrices.
Charles Bethin, substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import random
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent

def require(ok,msg):
 if not ok: raise ValueError(msg)

def emit(n):
 # Construct complete child words, then invert their instruction lists.
 def rec(lo,k,x,y,d):
  if k==1:return [(x,y,lo,1)]
  m=k//2;u=rec(lo,m,x,d+2,d+1);v=rec(lo+m,k-m,d+2,y,d+1)
  return u+v+[(x,y,j,-s) for x,y,j,s in reversed(u)]+[(x,y,j,-s) for x,y,j,s in reversed(v)]
 return rec(0,n,0,1,0)

def source_word(n,sign):
 raw=(HERE/'vendor/dirty.py').read_text();tree=ast.parse(raw)
 fs=[a for a in tree.body if isinstance(a,ast.FunctionDef) and a.name=='compose']
 require(len(fs)==1,'source compose missing')
 ports=[[0] for _ in range((n-1).bit_length()+2)];ids={id(p):i for i,p in enumerate(ports)};out=[]
 def leaf(x,y,factor,phases,beta,bits,d,sgn,stats):out.append((ids[id(x)],ids[id(y)],factor,sgn))
 env={'c':SimpleNamespace(need=require,norm2=lambda x:x*x),'leaf':leaf}
 exec(compile(ast.Module(body=fs,type_ignores=[]),'pinned-compose','exec'),env)
 env['compose'](ports[0],ports[1],list(range(n)),ports[2:],[1],F(1,2),64,1,sign)
 return out

def identity(d):return [[{():1} if i==j else {} for j in range(d)] for i in range(d)]

def step(M,op):
 x,y,j,s=op
 for k,p in enumerate(M[x]):
  q=M[y][k]
  for mon,c in p.items():
   t=(j,)+mon # Free words, with repetitions retained. No squarefree quotient.
   q[t]=q.get(t,0)+s*c
   if q[t]==0:del q[t]

def properties(M):
 mass=0
 for row in M:
  mass=max(mass,sum(abs(c) for p in row for c in p.values()))
  for p in row:
   for mon in p:require(len(mon)==len(set(mon)),'repeated factor survives: '+str(mon))
 return mass

def interval(ops,a,b,d):
 M=identity(d)
 word=ops[a:b] if a<=b else [(x,y,j,-s) for x,y,j,s in reversed(ops[b:a])]
 for op in word:step(M,op)
 return M

def mm(A,B):
 return [[sum((x*y for x,y in zip(r,c)),F(0)) for c in zip(*B)] for r in A]

def eye(d):return [[F(i==j) for j in range(d)] for i in range(d)]

def inv(A):
 d=len(A);M=[r[:]+s for r,s in zip(A,eye(d))]
 for j in range(d):
  k=next(i for i in range(j,d) if M[i][j]);M[j],M[k]=M[k],M[j]
  q=M[j][j];M[j]=[x/q for x in M[j]]
  for i in range(d):
   if i!=j:
    q=M[i][j];M[i]=[x-q*y for x,y in zip(M[i],M[j])]
 return [r[d:] for r in M]

def dense_prefixes(ops,factors,d):
 P=[eye(d)]
 for x,y,j,s in ops:
  E=eye(d);E[y][x]=s*factors[j]
  P.append(mm(E,P[-1]))
 return P

def eval_poly(M,factors):
 def val(mon,c):
  for j in mon:c*=factors[j]
  return c
 return [[sum((val(m,F(c)) for m,c in p.items()),F(0)) for p in row] for row in M]

def block_dense(ops,factors,d,a,b):
 # Full matrix multiplication at every leaf; inverses use Gauss-Jordan.
 P=eye(2*d);cuts={0:P}
 for k,(x,y,j,s) in enumerate(ops,1):
  E=eye(2*d)
  for r in range(2):
   for c in range(2):E[2*y+r][2*x+c]+=s*factors[j][r][c]
  P=mm(E,P)
  if k in (a,b):cuts[k]=P
 return mm(cuts[b],inv(cuts[a]))

def eval_blocks(M,factors):
 d=len(M);out=[[F(0) for _ in range(2*d)] for _ in range(2*d)]
 for i,row in enumerate(M):
  for j,p in enumerate(row):
   for mon,c in p.items():
    term=eye(2)
    for index in mon:term=mm(term,factors[index])
    for r in range(2):
     for s in range(2):out[2*i+r][2*j+s]+=c*term[r][s]
 return out

def main():
 pins=json.loads((HERE/'SOURCES.json').read_text())
 expected={'vendor/'+s for s in ('dirty.py','PR905-PROOF.md','PR905-NOTICE.md','PR628-NOTICE.md','PR1085-PROOF.md','PR1244-README.md','LICENSE')}
 require(set(pins['sha256'])==expected,'source inventory mismatch')
 require({r['vendor_path'] for r in pins['files']}==expected,'Git inventory mismatch')
 for p,h in pins['sha256'].items():require(hashlib.sha256((HERE/p).read_bytes()).hexdigest()==h,'source drift '+p)
 for row in pins['files']:
  raw=(HERE/row['vendor_path']).read_bytes()
  require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source Git blob drift')
 rng=random.Random(64);rows=[];cases=0;dispatch=0
 for n in range(1,25):
  d=(n-1).bit_length()+2;maxmass=0;count=0
  for sign in (1,-1):
   ops=source_word(n,sign);expected=emit(n)
   if sign==-1:expected=[(x,y,j,-s) for x,y,j,s in reversed(expected)]
   require(ops==expected,'independent dispatcher mismatch');dispatch+=1
   for a in range(len(ops)):
    M=identity(d)
    for b in range(a,len(ops)):
     step(M,ops[b]);maxmass=max(maxmass,properties(M));count+=1
  rows.append(dict(n=n,intervals=count,max_coefficient_mass=maxmass));cases+=count
  print('checked',n,count,flush=True,file=sys.stderr)
 sampled=0;sample_words=[]
 for n in (31,32,33,63,64,65,127,128,129):
  ops=source_word(n,1);require(ops==emit(n),'large dispatcher mismatch');dispatch+=1;d=(n-1).bit_length()+2
  for _ in range(12):
   a=rng.randrange(len(ops)+1);b=rng.randrange(len(ops)+1)
   properties(interval(ops,a,b,d));sampled+=1;sample_words.append([n,a,b])
 dense=0
 for n in (1,2,3,4,5,7,8,9,16):
  d=(n-1).bit_length()+2;ops=source_word(n,1)
  # Fraction scalars commute. Dense multiplication and Gauss-Jordan do not use
  # polynomial row updates or the independently constructed traversal.
  factors=[F(rng.choice((-3,-2,-1,1,2,3)),rng.choice((1,2,3))) for _ in range(n)]
  P=dense_prefixes(ops,factors,d)
  for _ in range(16):
   a=rng.randrange(len(ops)+1);b=rng.randrange(len(ops)+1)
   literal=mm(P[b],inv(P[a]));symbolic=eval_poly(interval(ops,a,b,d),factors)
   require(literal==symbolic,'dense two-cut mismatch');dense+=1
 block_cases=0
 for n in (4,7,9):
  d=(n-1).bit_length()+2;ops=source_word(n,1)
  factors=[[[F(rng.randrange(-2,3)) for _ in range(2)] for _ in range(2)] for _ in range(n)]
  for a,b in ((0,len(ops)),(len(ops)//3,2*len(ops)//3),(2*len(ops)//3,len(ops)//3)):
   require(eval_blocks(interval(ops,a,b,d),factors)==block_dense(ops,factors,d,a,b),'noncommuting dense mismatch')
   block_cases+=1
 controls=[]
 # A real repeated-factor circuit must fail; squares cannot be erased silently.
 bad=identity(2)
 for op in [(0,1,0,1),(1,0,1,1),(0,1,0,1)]:step(bad,op)
 try:properties(bad)
 except ValueError:controls.append('repeated_factor_detected')
 else:raise ValueError('squarefree detector accepted repeated factor')
 # Reuse one connector at every depth: illegal alias must be visible.
 ops=[(0 if x==0 else 1 if x==1 else 2,0 if y==0 else 1 if y==1 else 2,j,s) for x,y,j,s in emit(4)]
 require(any(x==y for x,y,j,s in ops),'alias control did not collide');controls.append('connector_alias_detected')
 # PR1244 noncommuting witness: a subset budget is not a permutation budget.
 J=[[F(0),F(3)],[F(-1,3),F(0)]];D=[[F(1,3),F(0)],[F(0),F(3)]]
 norm=lambda M:max(sum(abs(x) for x in r) for r in M)
 require(norm(mm(D,J))==1 and norm(mm(J,D))==9,'order witness');controls.append('commutation_required')
 # Preserve the known wrong-order block from the predecessor's witness.
 ops=source_word(7,1);factors=[eye(2) for _ in range(7)];factors[1]=J;factors[4]=D
 M=interval(ops,13,27,5);value=eval_blocks(M,factors)
 require(value[8][8]==1 and value[8][9]==-9,'retained noncommuting witness')
 controls.append('wrong_order_interval_preserved')
 # A generic copied-register identity must detect a missing restoration leaf.
 ops=emit(4);factors=[F(1)]*4;P=dense_prefixes(ops,factors,4)[-1]
 broken=dense_prefixes(ops[:-1],factors,4)[-1]
 require(P!=broken,'restoration omission is invisible');controls.append('restoration_omission')
 receipt=dict(status='PASS_COMMUTING_INTERVAL_AUDIT',exhaustive=rows,intervals=cases,sampled=sampled,sample_cuts=sample_words,dispatcher_cases=dispatch,dense_cases=dense,noncommuting_block_cases=block_cases,controls=controls,seed=64)
 parser=argparse.ArgumentParser();parser.add_argument('--write',type=Path);args=parser.parse_args()
 if args.write:
  with args.write.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
 else:require(receipt==json.loads((HERE/'CERTIFICATE.json').read_text()),'certificate mismatch')
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
