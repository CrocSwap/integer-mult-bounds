#!/usr/bin/env python3
"""Exact all-prefix Schur norm certificate for emitted actual reader adapters."""
import argparse,json,os,sys
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as Q
import reader_adapter as m

def certify(receipt):
 before=m.sha(receipt);d=json.loads(receipt.read_text());word=d['word'];ids=sorted({e[1]for e in word}|{e[2]for e in word if e[0]=='add'})
 rows={i:{i:Q(1)}for i in ids};best=Q(1);worst=0;records=[]
 for t,e in enumerate(word,1):
  rows=m.execute(rows,[e]);rowmax=max(sum(map(abs,row.values()))for row in rows.values());cols={}
  for row in rows.values():
   for k,v in row.items():cols[k]=cols.get(k,Q(0))+abs(v)
  colmax=max(cols.values());bound=rowmax*colmax;records.append(str(bound))
  if bound>best:best=bound;worst=t
 bits=0
 while(1<<(2*bits))<best:bits+=1
 assert m.sha(receipt)==before
 return dict(status='PASS_EXACT_EVERY_PREFIX_SCHUR_BOUND',reader_receipt_sha256=before,source_word_sha256=d['source_word_sha256'],prefix_count=len(word),max_squared_operator_norm_bound=str(best),first_worst_prefix=worst,euclidean_growth_bits=bits,unmentioned_spectators_identity=True,correlated_tensor_arrays_allowed=True,proof='For each prefix A, ||A||2^2<=||A||1||A||infinity. Sparse exact rational row and column sums certify every prefix; identity spectators add norm1. Tensoring with an identity leaves the operator norm unchanged.',invariant_endpoint_metric='For involution P, Q=I+P*P is positive definite and P*QP=Q. This does not assert a common metric with any other native endpoint or arbitrary owner-routing operator.',prefix_squared_bounds=records)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--reader-receipt',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();r=certify(a.reader_receipt);fd=os.open(str(a.out)+'.lock',os.O_CREAT|os.O_EXCL|os.O_WRONLY)
 try:assert not a.out.exists();a.out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
 finally:os.close(fd);Path(str(a.out)+'.lock').unlink()
 print(json.dumps({k:v for k,v in r.items()if k!='prefix_squared_bounds'},indent=2))
