#!/usr/bin/env python3
"""Exact B030 minimum-noise versus sparse native section comparison."""
import argparse,json,os,sys
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as Q
import reader_adapter as m

def compare(path):
 before=m.sha(path);w=m.load(path);R,hs=m.extract(w)
 G=[[sum(R[i].get(h,Q(0))*R[j].get(h,Q(0))for h in hs)for j in range(8)]for i in range(8)]
 A=[G[i][:]+[Q(i==j)for j in range(8)]for i in range(8)]
 for c in range(8):
  k=next(k for k in range(c,8)if A[k][c]);A[c],A[k]=A[k],A[c];v=A[c][c];A[c]=[x/v for x in A[c]]
  for i in range(8):
   if i!=c:
    v=A[i][c];A[i]=[x-v*y for x,y in zip(A[i],A[c])]
 inv=[row[8:]for row in A];V=[[Q((i==a)-(i==b))for a,b in[(4,5),(6,7)]]for i in range(8)]
 B=[[sum(inv[i][k]*V[k][j]for k in range(8))for j in range(2)]for i in range(8)]
 J=[[sum(R[i].get(h,Q(0))*B[i][j]for i in range(8))for j in range(2)]for h in hs]
 assert [[sum(R[i].get(h,Q(0))*row[j]for h,row in zip(hs,J))for j in range(2)]for i in range(8)]==V
 non=[(h,j,x)for h,row in zip(hs,J)for j,x in enumerate(row)if x and(x.denominator&(x.denominator-1))]
 assert non,'the previously observed native alphabet falsifier changed'
 assert m.sha(path)==before
 return dict(status='PASS_EXACT_WEIGHTED_SECTION_COMPARISON_NOT_NATIVE_GAIN',source_word_sha256=before,gram=[[str(x)for x in row]for row in G],minimal_section_squared_frobenius=str(sum(x*x for row in J for x in row)),sparse_section_squared_frobenius='1',dense_section_nonzero_entries=sum(bool(x)for row in J for x in row),first_nondyadic_entry={'helper':non[0][0],'column':non[0][1],'coefficient':str(non[0][2])},right_inverse_on_two_difference_directions_exact=True,decision='Minimum-noise section is an exact constructive decoder but has nondyadic coefficients; retain234-operation sparse dyadic native primitive. Neither construction deletes recursive children.')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();r=compare(a.word);fd=os.open(str(a.out)+'.lock',os.O_CREAT|os.O_EXCL|os.O_WRONLY)
 try:assert not a.out.exists();a.out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
 finally:os.close(fd);Path(str(a.out)+'.lock').unlink()
 print(r['status'])
