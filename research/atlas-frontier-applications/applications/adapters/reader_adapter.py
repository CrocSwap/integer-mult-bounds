#!/usr/bin/env python3
"""Exact current-source reader adapter. No recursive child/complete kappa claim."""
import argparse,collections,copy,gzip,hashlib,json,os
from fractions import Fraction as Q
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def add(a,b,c):
 z=dict(a)
 for k,v in b.items():
  z[k]=z.get(k,Q(0))+c*v
  if not z[k]:del z[k]
 return z
def execute(rows,word):
 rows=copy.deepcopy(rows)
 for op,d,*args in word:
  if op=='add':s,n,den,_=args;rows[d]=add(rows[d],rows[s],Q(n,den))
  elif op=='scale':n,den,_=args;rows[d]={k:v*Q(n,den)for k,v in rows[d].items()if v*Q(n,den)}
  else:raise ValueError('non-scalar adapter')
 return rows

def extract(w):
 helpers=sorted(set(range(224,704))-set(w['removed']));rows={i:({i:Q(1)}if i in helpers else{})for i in range(704)}
 # Prelude acts only on data/target ports; the literal scalar reader starts here.
 rows=execute(rows,w['A'][w.get('prelude_events',0):])
 R=[rows[i]for i in w['centers']]
 return R,helpers

def reflection(R,p,q,s):
 a,b=(4,5)if s==-1 else(6,7)
 d=add(R[a],R[b],Q(-1));assert d[p]==2 and d[q]==2*s
 v=[R[i].get(p,Q(0))/2+s*R[i].get(q,Q(0))/2 for i in range(8)]
 assert v==[Q((i==a)-(i==b))for i in range(8)]
 word=[['add',p,q,1,1,[]],['scale',q,-1,1,[]],['add',q,p,1,1,[]],['add',p,q,-1,1,[]]]
 if s==1:word +=[['scale',p,-1,1,[]],['scale',q,-1,1,[]]]
 for h,c in sorted(d.items()):
  if h in(p,q):continue
  for dest,coef in[(p,-c/2),(q,-s*c/2)]:word.append(['add',dest,h,coef.numerator,coef.denominator,[]])
 return word

def check(R,helpers,word):
 I={h:{h:Q(1)}for h in helpers};P=execute(I,word)
 PR=[]
 for row in R:
  z={}
  for h,c in row.items():z=add(z,P[h],c)
  PR.append(z)
 permutation=[0,1,2,3,5,4,7,6]
 assert PR==[R[i]for i in permutation],'reader covariance'
 assert execute(P,word)==I,'involution/full arbitrary-dirty endpoint'
 return P

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 before=sha(a.word);w=load(a.word);R,helpers=extract(w)
 word=reflection(R,435,432,-1)+reflection(R,432,447,1)
 P=check(R,helpers,word)
 touched={e[1]for e in word}|{e[2]for e in word if e[0]=='add'}
 assert all(w['start_extra'].get(str(h),[])==[]for h in touched),'nonzero entrance frame'
 # Rank-zero primitives at a shared zero frame preserve that frame at every prefix.
 assert all(e[-1]==[]for e in word)
 tests={}
 for name,mutate in [('wrong_coefficient',lambda v:v[4].__setitem__(3,v[4][3]+1)),('missing_final_gate',lambda v:v.pop()),('wrong_source',lambda v:v[4].__setitem__(2,224))]:
  bad=copy.deepcopy(word);mutate(bad)
  try:check(R,helpers,bad)
  except(AssertionError,KeyError):tests[name]='REJECTED'
  else:raise AssertionError('negative control accepted:'+name)
 assert sha(a.word)==before
 result=dict(status='PASS_EXACT_SOURCE_BOUND_READER_ADAPTER_NOT_KAPPA_GAIN',source_word_sha256=before,source_kind=w.get('kind'),centres=w['centers'],centre_source_permutation=[0,1,2,3,5,4,7,6],scalar_operations=len(word),positive_rank_children=0,new_scratch_fields=0,all_prefixes_zero_frame=True,arbitrary_dirty_endpoint=True,negative_controls=tests,word=word,scope='Literal scalar-reader covariance and arbitrary-dirty helper endpoint. Actual selected centre Fourier/gauge adapters and complete consumer are not composed here; eight rank8 children remain.')
 a.out.parent.mkdir(parents=True,exist_ok=True);fd=os.open(str(a.out)+'.lock',os.O_CREAT|os.O_EXCL|os.O_WRONLY)
 try:
  assert not a.out.exists();a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
 finally:os.close(fd);Path(str(a.out)+'.lock').unlink()
 print(json.dumps({k:v for k,v in result.items()if k!='word'},indent=2))
if __name__=='__main__':main()
