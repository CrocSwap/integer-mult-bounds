#!/usr/bin/env python3
"""Independent exact integer operator comparison for all twenty signed generalized twin changes.
All physical registers start as independent formal integer coordinates. No modular reductions.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,json,struct,time,hashlib
sha=lambda b:hashlib.sha256(b).hexdigest()
def replay(events,n):
 V=[{i:1}for i in range(n)]+[{}];open_source=None
 for op,a,b,c,f,z in events:
  if op==0:continue
  if op==1:
   assert 0<=a<n and 0<=b<=n and a!=b and(open_source is None or a!=open_source)
   if b==n:assert open_source is not None
   for i,x in V[b].items():
    y=V[a].get(i,0)+c*x
    if y:V[a][i]=y
    else:V[a].pop(i,None)
  elif op==2:assert open_source is None and b==n;V[n]=dict(V[a]);open_source=a
  elif op==3:assert open_source==a and b==n;V[n]={};open_source=None
  else:raise AssertionError('Unknown opcode')
 assert open_source is None and not V[n]
 return V

def run(source,candidate,output):
 source,candidate,output=map(Path,(source,candidate,output));assert not output.exists();start=time.monotonic();s=source.read_bytes();c=candidate.read_bytes();assert sha(s)=='2aa5b4af88e4295588079cf951a5655bdff861588d39ba8af43c185ee93d14b6'and sha(c)=='6e0fcf5dd38d18a057a841b5dca56a4ab9c2d0489f37bc72a54a277d3f068330';n=9530
 se=list(struct.iter_unpack('<6i',s));ce=list(struct.iter_unpack('<6i',c));original=replay(se,n);changed=replay(ce,n);assert original==changed,'Signed local operator changed over Z'
 tests=[]
 for entrycat,exitcat in ((44,45),(46,47)):
  entries=[i for i,x in enumerate(ce)if x[0]==1 and x[5]==entrycat];exits=[i for i,x in enumerate(ce)if x[0]==1 and x[5]==exitcat]
  assert len(entries)==len(exits)==(18 if entrycat==44 else 2)
  for kind,k in [('missing_entry',entries[0]),('missing_exit',exits[0]),('wrong_entry_sign',entries[0])]:
   if kind.startswith('missing'):bad=replay(ce[:k]+ce[k+1:],n)
   else:
    be=list(ce);row=list(be[k]);row[3]=-row[3];be[k]=tuple(row);bad=replay(be,n)
   count=sum(a!=b for a,b in zip(original,bad));assert count>0;tests.append(dict(name=kind,entry_category=entrycat,record=k,changed_rows=count,rejected=True))
 result=dict(status='PASS_EXACT_INTEGER_PR354_SIGNED_TWENTY_TWIN_OPERATOR_EQUIVALENCE',source_sha256=sha(s),candidate_sha256=sha(c),independent_integer_input_columns=n,output_rows_compared=n+1,all_output_rows_equal=True,source_nonzero_coefficients=sum(map(len,original)),max_abs_coefficient=max(abs(x)for row in original for x in row.values()),mutation_controls=tests,seconds=time.monotonic()-start,scope='Full local signed scalar operators agree exactly over Z, including arbitrary helper variables, source/target variables and COPY/ERASE. This preserves the predecessor integer lift; the intended transform remains its inherited F2 theorem. Frames, precision, paid calls and finite banks are separately audited.')
 output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS exact integer generalized twin operator and six controls',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--candidate',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.source,a.candidate,a.output)
