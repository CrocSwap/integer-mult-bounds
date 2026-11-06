#!/usr/bin/env python3
"""Bounded exact second-order controls; @CubeJerry/OpenAI assistance, Apache-2.0."""
from itertools import permutations, combinations
import json

def need(x,msg):
 if not x: raise ValueError(msg)
def mul(a,b):
 out=[]
 for row in a:
  v=0
  for k,other in enumerate(b):
   if row>>k&1:v^=other
  out.append(v)
 return tuple(out)
def pack(rows):return sum(v<<(5*i) for i,v in enumerate(rows))
def off(rows):return pack(rows)&~sum(1<<(6*i) for i in range(5))
J=(31,)*5;E=[tuple(1<<i if r==i else 0 for r in range(5))for i in range(4)]
A=[J]+E
basis=[]
for b in [off(J),1<<1,1<<13]:
 for p,v in basis:
  if b>>p&1:b^=v
 if b:basis.append((b.bit_length()-1,b));basis.sort(reverse=True)
def reduce(b):
 for p,v in basis:
  if b>>p&1:b^=v
 return b
K=[reduce(off(tuple(a^b for a,b in zip(mul(J,e),mul(e,J)))))for e in E]
need(len({0,*K})==5,'nonzero stars')
need(len({__import__('functools').reduce(int.__xor__,[K[i]for i in range(4)if mask>>i&1],0)for mask in range(16)})==16,'independent stars')

def quadratic(word):
 h=word.count(0);jseen=0
 # surviving variables: h-1 bridge variables, E1, E3; eliminate last J,E2,E4.
 substitutions=[]
 for t in word:
  if t==0:
   substitutions.append([jseen] if jseen<h-1 else list(range(h-1)));jseen+=1
  else:substitutions.append([h-1+(t>=3)])
 observed={}
 for a,b in combinations(range(len(word)),2):
  m=reduce(off(mul(A[word[a]],A[word[b]])))
  for x in substitutions[a]:
   for y in substitutions[b]:
    key=tuple(sorted((x,y)));observed[key]=observed.get(key,0)^m
 return {k:v for k,v in observed.items() if v}
counts=[]
for h in range(1,7):
 tested=admitted=0
 for coords in permutations(range(h+4),4):
  w=[0]*(h+4)
  for t,p in enumerate(coords,1):w[p]=t
  bad=quadratic(w);js=[i for i,t in enumerate(w)if t==0]
  adjacent=js[-1]-js[0]+1==h
  need((not bad)==adjacent,'quadratic condition differs from single bridge block')
  tested+=1;admitted+=not bad
 need(admitted==120,'all block orders')
 counts.append({'bridge_calls':h,'words':tested,'quadratic_admitted':admitted})
print('PASS_FIVE_CORE_WORD_QUADRATIC',json.dumps({'counts':counts,'total':sum(x['words']for x in counts),'scope':'Every tested word has one occurrence of each coordinate type. The all-length/multiplicity theorem uses the written proof.'},sort_keys=True))

# Full Laurent endpoint controls, separate from the augmentation relaxation.
def polynomial_product(a,b):
 out=set()
 for x in a:
  for y in b:out.symmetric_difference_update((tuple(i+j for i,j in zip(x,y)),))
 return out
def endpoint(calls):
 z=(0,0,0);out=[[{z}if i==j else set()for j in range(5)]for i in range(5)]
 for exponent,t in calls:
  n=A[t];new=[[v.copy()for v in row]for row in out]
  for i in range(5):
   for j in range(5):
    q=set()
    for k in range(5):
     if n[k]>>j&1:q.symmetric_difference_update(out[i][k])
    new[i][j].symmetric_difference_update(polynomial_product(q,{z,exponent}))
  out=new
 return out
a,b,c=(1,0,0),(0,1,0),(0,0,1);nc=(0,0,-1)
coords=[(a,1),(a,2),(b,3),(b,4)]
targets=[a,a,b,b,(0,0,0)];desired=[[{targets[i]}if i==j else set()for j in range(5)]for i in range(5)]
need(endpoint(coords+[(c,0),(nc,0)])==desired,'exact block cancellation endpoint')
interleaved=endpoint([(c,0)]+coords+[(nc,0)])
need(any(interleaved[i][j]for i in range(5)for j in range(5)if i!=j),'interleaved bridge violates exact endpoint')
need(interleaved[4][0],'required position(5,1) detects interleaving')
print('PASS_FIVE_CORE_WORD_EXACT',json.dumps({'positive_calls':6,'relation_rank':3,'nonzero_interleaved_entry_5_1':sorted(interleaved[4][0]),'scope':'Formal torsion-free endpoint only; no rank saving or physical supplier.'},sort_keys=True))
