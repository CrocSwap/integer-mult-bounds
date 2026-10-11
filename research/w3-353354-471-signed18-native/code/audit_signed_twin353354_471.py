#!/usr/bin/env python3
"""Independent exact integer operator comparison for the signed generalized twin change.
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
 source,candidate,output=map(Path,(source,candidate,output));assert not output.exists();start=time.monotonic();s=source.read_bytes();c=candidate.read_bytes();assert sha(s)=='d75fa9566e9a6b74e7b07966c4ddf5bd07e956e3119d5b1c150da1932d61511e'and sha(c)=='98007fb3a634ca671bcfea6bed8c1b33da190606ffbea748cd931399ecf65d2d';n=9530
 se=list(struct.iter_unpack('<6i',s));ce=list(struct.iter_unpack('<6i',c));original=replay(se,n);changed=replay(ce,n);assert original==changed,'Signed local operator changed over Z'
 tests=[]
 for category in(44,45):
  k=next(i for i,x in enumerate(ce)if x[0]==1 and x[5]==category);bad=replay(ce[:k]+ce[k+1:],n);count=sum(a!=b for a,b in zip(original,bad));assert count>0;tests.append(dict(name='missing_entry'if category==44 else'missing_exit',record=k,changed_rows=count,rejected=True))
 k=next(i for i,x in enumerate(ce)if x[0]==1 and x[5]==44);be=list(ce);row=list(be[k]);row[3]=-row[3];be[k]=tuple(row);bad=replay(be,n);count=sum(a!=b for a,b in zip(original,bad));assert count>0;tests.append(dict(name='wrong_entry_sign',record=k,changed_rows=count,rejected=True))
 result=dict(status='PASS_EXACT_INTEGER_GENERALIZED_TWIN_OPERATOR_EQUIVALENCE',source_sha256=sha(s),candidate_sha256=sha(c),independent_integer_input_columns=n,output_rows_compared=n+1,all_output_rows_equal=True,source_nonzero_coefficients=sum(map(len,original)),max_abs_coefficient=max(abs(x)for row in original for x in row.values()),mutation_controls=tests,seconds=time.monotonic()-start,scope='Full local signed scalar operators agree exactly over Z, including arbitrary helper variables, source/target variables and COPY/ERASE. This preserves the predecessor integer lift; the intended transform remains its inherited F2 theorem. Frames, precision, paid calls and finite banks are separately audited.')
 output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS exact integer generalized twin operator and three controls',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--candidate',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.source,a.candidate,a.output)
