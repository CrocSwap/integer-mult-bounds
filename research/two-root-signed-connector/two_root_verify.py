#!/usr/bin/env python3
"""Exact two-dirty-root connector witness. Apache-2.0.
Prepared for Charles Bethin with substantial OpenAI Codex assistance.
Credits: Ross Richardson PR944, martinxxx9 PR1088, Hanson Sun PR1526/1556.
"""
import json,sys,random,argparse
from pathlib import Path
from collections import Counter
M=((1,1,1),(1,1,-1),(1,-1,0))
# (kind, operator or root coefficient, sign, root).
WORD=[('B',0,1,0),('A',2,1,0),('B',1,1,0),('R',-1,1,0),('A',0,1,0),('R',2,1,0),('A',1,1,0),('R',-1,1,0),('B',0,-1,0),('A',2,-1,0),('B',1,-1,0),('B',2,1,1),('R',-1,1,0),('A',0,-1,0),('R',2,1,0),('A',1,-1,0),('R',-1,1,0),('B',2,-1,1)]

def req(c,s):
 if not c:raise ValueError(s)

def symbolic(word):
 state=[{('x'+str(j),):1} for j in range(3)]+[{('y'+str(i),):1} for i in range(3)]+[{('z0',):1},{('z1',):1}]
 for kind,op,sign,root in word:
  if kind=='B':dst=6+root;src=op;scale=sign;prefix=('B'+str(op),)
  elif kind=='A':dst=3+op;src=6+root;scale=sign;prefix=('A'+str(op),)
  else:dst=6;src=7;scale=op*sign;prefix=()
  for term,value in list(state[src].items()):
   key=prefix+term;state[dst][key]=state[dst].get(key,0)+scale*value
   if state[dst][key]==0:del state[dst][key]
 return state

def expected_symbolic():
 out=[{('x'+str(j),):1} for j in range(3)]+[{('y'+str(i),):1} for i in range(3)]+[{('z0',):1},{('z1',):1}]
 for i in range(3):
  for j in range(3):
   if M[i][j]:out[3+i][('A'+str(i),'B'+str(j),'x'+str(j))]=M[i][j]
 return out

def identity(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def mul(A,B):
 n=len(A);R=[[0]*n for _ in range(n)]
 for i,row in enumerate(A):
  for k,a in enumerate(row):
   if a:
    for j,b in enumerate(B[k]):R[i][j]+=a*b
 return R

def dense(word,L,F):
 # Independently construct each full elementary matrix and multiply it.
 n=8*L;out=identity(n)
 for kind,op,sign,root in word:
  E=identity(n)
  if kind=='R':
   for a in range(L):E[6*L+a][7*L+a]=op*sign
  else:
   dst=(6+root if kind=='B' else 3+op)*L
   src=(op if kind=='B' else 6+root)*L
   block=F[kind+str(op)]
   for a in range(L):
    for b in range(L):E[dst+a][src+b]=sign*block[a][b]
  out=mul(E,out)
 return out

def expected_dense(L,F):
 out=identity(8*L)
 for i in range(3):
  for j in range(3):
   block=mul(F['A'+str(i)],F['B'+str(j)])
   for a in range(L):
    for b in range(L):out[(3+i)*L+a][j*L+b]=M[i][j]*block[a][b]
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
 req(symbolic(WORD)==expected_symbolic(),'free noncommutative map')
 counts=Counter((k,o,s) for k,o,s,r in WORD if k!='R');req(len(counts)==12 and set(counts.values())=={1},'one query of each sign/operator')
 inv=[(k,o,-s,r) for k,o,s,r in reversed(WORD)]
 req(symbolic(WORD+inv)==symbolic([]),'symbolic inverse')
 checked=0;noncommuting=0;rng=random.Random(20)
 for L in range(1,6):
  for fixture in range(4):
   F={k+str(i):[[rng.randrange(-3,4) for b in range(L)] for a in range(L)] for k in 'AB' for i in range(3)}
   A=dense(WORD,L,F);E=expected_dense(L,F);req(A==E,'dense independent expected map')
   req(mul(dense(inv,L,F),A)==identity(8*L),'dense inverse')
   checked+=8*L
   if mul(F['A0'],F['B0'])!=mul(F['B0'],F['A0']):noncommuting+=1
 controls=[]
 for idx in range(len(WORD)):
  mutated=WORD[:idx]+WORD[idx+1:]
  req(symbolic(mutated)!=expected_symbolic(),'omission '+str(idx));controls.append('omit event '+str(idx))
 bad=[(k,o,-s if i==13 else s,r) for i,(k,o,s,r) in enumerate(WORD)]
 req(symbolic(bad)!=expected_symbolic(),'wrong read sign');controls.append('wrong read sign')
 # Bind B2 to the wrong root; both root rows still exist in this control.
 aliased=[(k,o,s,0) if k in ('A','B') else (k,o,s,r) for k,o,s,r in WORD]
 req(symbolic(aliased)!=expected_symbolic(),'wrong B2 root binding');controls.append('wrong B2 root binding')
 costs=[]
 for c in [1,4,5,10,100]:
  # Abstract complete prices: each child c, each root scan one; admission equal.
  old14=14*c;old13=13*c+2;new=12*c+6
  costs.append(dict(child_price=c,old14=old14,dyadic13=old13,two_root12=new))
 result=dict(status='PASS_TWO_ROOT_CONNECTOR_LOCAL',sys_version=sys.version,sys_executable=sys.executable,seed=20,word=WORD,target=M,complete_child_queries=12,root_passes=6,root_pass_coefficients=[o*s for k,o,s,r in WORD if k=='R'],symbolic_map=[{','.join(k):v for k,v in x.items()} for x in symbolic(WORD)],dense_cases=20,dense_basis_columns=checked,noncommuting_cases=noncommuting,controls=controls,abstract_tariff_examples=costs,scope='All-input symbolic identity and separate finite dense matrix verification. Six root passes, extra root admission, all child costs and dispatch must be paid. No supplier admission, measured runtime, root-pass optimum or kappa claim.')
 args.out.write_text(json.dumps(result,indent=2)+'\n')
 print('PASS_TWO_ROOT_CONNECTOR_LOCAL queries=12 root_passes=6 dense_cases=20 dense_columns='+str(checked)+' controls='+str(len(controls))+' noncommuting='+str(noncommuting))
if __name__=='__main__':main()
