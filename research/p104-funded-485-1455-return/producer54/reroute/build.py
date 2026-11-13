"""Exact #7480 changed producer, independent root emitter.

Original event indices are zero based. No source input is downloaded or changed.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import gzip, hashlib, importlib.util, json, sys, time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'inputs/pr7480/WORD.json.gz'
W=json.load(gzip.open(SOURCE,'rt'))
P=W['program']
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
assert hashlib.sha256(canonical(W)).hexdigest()=='5044adee019f073f286789ccb688ffca76d42b60518242bb4daea818d33d337a'

SPLICE=[
 ['ADD',212,1455,'1',3],
 ['ADD',1455,976,'1',3],
 ['ADD',485,1455,'-2',3],
 ['ADD',1455,485,'2/3',3],
 ['MOVE',1455,3,721,False],
 ['ADD',824,1455,'-3/2',721],
 ['ADD',824,54,'-1',721],
 ['ADD',1455,54,'1/2',721],
 ['MOVE',1455,721,724,False],
 ['MOVE',485,3,724,False],
 ['ADD',1455,485,'-2/3',724],
 ['ADD',485,1455,'2',724],
 ['MOVE',1455,724,904,False],
]
SKIP={33163,33164,33165,33172,33186,33191,33200,33201,33203,33205}
Q=[];mapping={}
for i,e in enumerate(P):
 if i==33163:Q.extend(SPLICE)
 mapping[i]=len(Q)
 if i not in SKIP:Q.append(e)
NEW={**W,'program':Q}

def add(a,b,c):
 z=a.copy()
 for k,v in b.items():
  z[k]=z.get(k,F(0))+c*v
  if not z[k]:del z[k]
 return z

def replay(local):
 rows=[{i:F(1)} for i in range(W['public']+W['owned_fields'])]
 for e in local:
  op,q=e[:2]
  if op in ('INIT','CLEAR'):rows[q]={}
  elif op=='SCALE':rows[q]={k:F(e[2])*v for k,v in rows[q].items()}
  elif op=='ADD':rows[q]=add(rows[q],rows[e[2]],F(e[3]))
  elif op=='COPY':rows[q]=rows[e[2]].copy()
 return rows

lo,hi=33163,33219
original_rows=replay(P[lo:hi])
changed_rows=replay(SPLICE+[P[i]for i in range(lo,hi)if i not in SKIP])
errors={str(q):{str(k):str(v) for k,v in add(changed_rows[q],original_rows[q],-1).items()}for q in range(len(original_rows))if changed_rows[q]!=original_rows[q]}
assert not errors,errors

def span(b):
 s={0}
 for x in b:s|={x^y for y in tuple(s)}
 return s
spaces=list(map(span,W['frames']))
def frames(program):
 active=W['initial']+[None]*W['owned_fields'];paid=Counter();ops=Counter();peak=live=lifetimes=0
 for i,e in enumerate(program):
  op,q=e[:2];ops[op]+=1
  if op=='MOVE':
   a,b,owned=e[2:]
   assert active[q]==a,(i,e,active[q])
   assert owned==(q>=W['public'])
   assert spaces[a]<spaces[b] or owned and spaces[b]<spaces[a],(i,e)
   paid[abs(len(W['frames'][b])-len(W['frames'][a]))]+=1;active[q]=b
  elif op=='INIT':
   assert active[q] is None
   active[q]=e[2];live+=1;lifetimes+=1;peak=max(peak,live)
  elif op=='CLEAR':
   assert active[q]==e[2]
   active[q]=None;live-=1
  else:
   for j in (e[1:3] if op in ('ADD','COPY') else e[1:2]):assert active[j]==e[-1],(i,e,j,active[j])
 assert active==W['final']+[None]*W['owned_fields']
 return dict(paid=paid,operations=ops,lifetimes=lifetimes,peak=peak)
old=frames(P);new=frames(Q)
delta=lambda a,b:{str(k):b[k]-a[k]for k in sorted(set(a)|set(b),key=str)if a[k]!=b[k]}
result={'status':'EXACT_LOCAL_ALL_ROWS_AND_COMPLETE_FRAMES_PASS_PENDING_COMPLETE_INVOICE',
 'source_canonical_sha256':hashlib.sha256(canonical(W)).hexdigest(),
 'candidate_canonical_sha256':hashlib.sha256(canonical(NEW)).hexdigest(),
 'source_compressed_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'insert_before_old_index':33163,'splice':SPLICE,'removed_old_indices':sorted(SKIP),
 'original_local_interval':[lo,hi],'exact_local_all_row_errors':errors,
 'old_events':len(P),'new_events':len(Q),'paid_delta':delta(old['paid'],new['paid']),
 'productive_endpoint_delta':{},'operation_delta':delta(old['operations'],new['operations']),
 'old_lifetimes':old['lifetimes'],'new_lifetimes':new['lifetimes'],
 'old_peak':old['peak'],'new_peak':new['peak'],
 'final_boundary_unchanged':NEW['final']==W['final'],'initial_boundary_unchanged':NEW['initial']==W['initial'],
}
if '--native' in sys.argv:
 spec=importlib.util.spec_from_file_location('retained',ROOT/'engines/retained_independent.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 started=time.time();r=mod.native(NEW);result['native_seconds']=time.time()-started
 result['native_result']=r
 assert not r['bad_inputs'],r
 result['status']='EXACT_COMPLETE_NATIVE_PASS_PENDING_COMPLETE_INVOICE'
with gzip.GzipFile(HERE/'WORD.json.gz','wb',mtime=0)as f:f.write(canonical(NEW))
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
(HERE/'OLD-TO-NEW.json').write_text(json.dumps(mapping,separators=(',',':'))+'\n')
print(json.dumps(result,indent=2,default=str))
