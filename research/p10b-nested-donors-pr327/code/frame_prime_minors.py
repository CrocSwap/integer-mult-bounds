#!/usr/bin/env python3
"""Exact full-row-rank witnesses for actual new frame bases and annihilators.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
A nonzero integer minor of magnitude below 2^80 stays nonzero over every
prime field of characteristic greater than 2^80. No factorization oracle.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
import argparse,hashlib,json
from pathlib import Path
P=2147483647

def columns(rows):
 if not rows:return []
 a=[[int(x)%P for x in row]for row in rows];m=len(a);n=len(a[0]);r=0;cols=[]
 for c in range(n):
  k=next((k for k in range(r,m)if a[k][c]),None)
  if k is None:continue
  a[k],a[r]=a[r],a[k];iv=pow(a[r][c],-1,P);a[r]=[iv*x%P for x in a[r]]
  for k in range(r+1,m):
   if a[k][c]:z=a[k][c];a[k]=[(x-z*y)%P for x,y in zip(a[k],a[r])]
  cols.append(c);r+=1
  if r==m:return cols
 raise AssertionError('Frame rows fail independent modular witness')

def determinant(a):
 n=len(a)
 if not n:return 1
 a=[list(row)for row in a];sign=1;prev=1
 for k in range(n-1):
  pivot=next((i for i in range(k,n)if a[i][k]),None)
  if pivot is None:return 0
  if pivot!=k:a[k],a[pivot]=a[pivot],a[k];sign=-sign
  p=a[k][k]
  for i in range(k+1,n):
   for j in range(k+1,n):
    value=a[i][j]*p-a[i][k]*a[k][j];assert value%prev==0;a[i][j]=value//prev
   a[i][k]=0
  prev=p
 return sign*a[-1][-1]

def witness(rows):
 c=columns(rows);d=determinant([[int(row[k])for k in c]for row in rows]);assert 0<abs(d)<2**80
 return c,d

def run(path,out):
 path=Path(path);frames=json.loads(path.read_text());frames=frames.get('frames',frames);rows=[];maximum=1;cache={}
 for f,data in sorted(frames.items(),key=lambda x:int(x[0])):
  dim=data['dim'];assert len(data['B'])==dim and len(data['A'])==20-dim
  for kind in ('B','A'):
   M=data[kind];assert all(len(row)==20 and all(isinstance(x,int)for x in row)for row in M)
   key=tuple(map(tuple,M))
   if key not in cache:cache[key]=witness(M)
   cols,d=cache[key];maximum=max(maximum,abs(d));rows.append(dict(frame=int(f),kind=kind,row_rank=len(M),columns=cols,determinant=str(d)))
  assert all(sum(x*y for x,y in zip(a,b))==0 for a in data['A']for b in data['B'])
 nonempty=next((data['A']or data['B']for data in frames.values()if data['A']or data['B']),None);assert nonempty
 bad=[list(row)for row in nonempty];bad[0]=[0]*20
 try:witness(bad)
 except AssertionError:control=True
 else:raise AssertionError('Zero row accepted')
 result=dict(status='PASS_EXACT_FRAME_AND_ANNIHILATOR_MINORS_FOR_ALL_PRIMES_ABOVE_2_POWER_80',input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),frames=len(frames),basis_witnesses=len(rows),distinct_integer_bases=len(cache),max_abs_minor=str(maximum),max_minor_bits=maximum.bit_length(),zero_row_control_rejected=control,scope='Every reported full-row-rank integer minor is recomputed exactly and nonzero with magnitude below2^80; exact A-B orthogonality also checked. Nondegenerate weighted projector and bank chart pivots are separately audited.',witnesses=rows)
 Path(out).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS exact minors',len(frames),'frames',len(cache),'distinct bases',maximum.bit_length(),'max bits',flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('frames');ap.add_argument('output');a=ap.parse_args();run(a.frames,a.output)
