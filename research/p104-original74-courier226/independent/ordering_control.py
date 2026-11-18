#!/usr/bin/env python3
"""Price-preserving wrong-order control, suggested by ChatGPT Pro.

Courier mechanism: DreamingOfClouds #7617 (and credited funded-return predecessors).
Compares the frozen strict #7645 candidate and its actual original input with a
legal, equal-invoice, reordered candidate, using the shipped independent exact interpreter.
"""
import argparse, collections, copy, gzip, hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from exact import Interpreter, diff
p=argparse.ArgumentParser()
p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--manifest',type=Path,required=True);p.add_argument('--invoice',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args(); start=time.monotonic()
def load(path): return json.loads(gzip.decompress(path.read_bytes()))
def sha(w):return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pairs(e):return e[1:3] if e[0] in ('ADD','COPY') else e[1:2]
base=load(a.baseline); good=load(a.candidate);manifest=json.loads(a.manifest.read_text());invoice=json.loads(a.invoice.read_text())
assert sha(base)=='6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf'
assert sha(good)=='450c7e544efb5258c4b8b4858b49cbd7482d14f206cdda1a71833fc73343ac66'
assert manifest['source_word_sha256']==sha(base) and manifest['candidate_word_sha256']==sha(good)
align={int(i):j for i,j in manifest['aligned_origins'].items()}
assert all(base['program'][i]==good['program'][j] for i,j in align.items())
mut=copy.deepcopy(good); tape=mut['program']; loc=41465
old=[['ADD',990,473,'-1',719],['MOVE',226,260,719,False],['ADD',473,226,'1',719],['ADD',990,226,'-1',719]]
assert tape[loc:loc+4]==old
tape[loc:loc+4]=[old[1],old[2],old[0],old[3]]
assert collections.Counter(map(tuple,tape))==collections.Counter(map(tuple,good['program']))
assert all(good[k]==mut[k] for k in good if k!='program')
N=base['public']; watching={i:j for i,j in align.items() if max(pairs(base['program'][i]))>=N or base['program'][i][0]=='COPY'}
assert len(watching)==630

def run(w,watch):
 q=Interpreter(w);reads={};clears=[];owned=[];paid=collections.Counter();dims=list(map(len,w['frames']))
 for i,e in enumerate(w['program']):
  if i in watch:reads[i]=[(r,q.rows[r].copy()) for r in pairs(e)]
  if e[0]=='CLEAR':clears.append((e[1],e[2],q.rows[e[1]].copy()))
  if any(r>=N for r in pairs(e)):owned.append(e)
  if e[0]=='MOVE':paid[abs(dims[e[3]]-dims[e[2]])]+=1
  q.step(i)
 q.end();return q,reads,clears,owned,paid
print('begin independent exact baseline',flush=True)
x,xr,xc,xo,xp=run(base,set(watching));print('baseline completed',round(time.monotonic()-start,2),flush=True)
y,yr,yc,yo,yp=run(good,set(watching.values()));print('positive completed',round(time.monotonic()-start,2),flush=True)
assert x.rows==y.rows and xc==yc and xo==yo and all(xr[i]==yr[j] for i,j in watching.items())
assert len(xc)==len(yc)==74
z,zr,zc,zo,zp=run(mut,set(watching.values()));print('mutant completed',round(time.monotonic()-start,2),flush=True)
assert yp==zp and yo==zo and len(zc)==74 and len(yc)==74
# Fixed-caller charges consist of 17 occurrences of the equal native histogram,
# plus the authenticated unchanged outer charges and targets of this invoice.
assert sum(invoice['paid'].values())==110281 and sum(invoice['targets'].values())==22461
assert all(v>=17*yp[int(k)] for k,v in invoice['paid'].items() if int(k) in yp)
observed=[]
for i,j in watching.items():
 for (role,u),(role2,v) in zip(yr[j],zr[j]):
  assert role==role2
  d=diff(v,u)
  if d:observed.append({'candidate_clock':j,'baseline_clock':i,'event':good['program'][j],'role':role,'mutant_minus_candidate':d})
clear=[]
for index,(u,v) in enumerate(zip(yc,zc)):
 assert u[:2]==v[:2]
 d=diff(v[2],u[2])
 if d:clear.append({'index':index,'role':u[0],'chart':u[1],'mutant_minus_candidate':d})
outputs=[]
for r,(u,v) in enumerate(zip(y.rows[:N],z.rows[:N])):
 d=diff(v,u)
 if d:outputs.append({'role':r,'mutant_minus_candidate':d,'candidate_coefficient':str(u.get(d['input_column'],0)),'mutant_coefficient':str(v.get(d['input_column'],0))})
assert observed or clear or outputs
out={'status':'PASS_ORDERING_NEGATIVE_CONTROL','credits':['ChatGPT Pro suggested the price-preserving ordering mutation','DreamingOfClouds #7617 and credited funded-return predecessors'], 'baseline_sha256':sha(base),'candidate_sha256':sha(good),'mutant_sha256':sha(mut),'source_head':'8ee7e6869b57ce445dbebd1d720366eab1f8ca40','ordering_clock':loc,'source_events':old,'mutant_events':tape[loc:loc+4], 'positive':{'public_rows':N,'protected_observations':len(watching),'ordered_clears':len(yc),'owned_events':len(yo),'exact_positive_matches_baseline':True},'mutation':{'lawful_interpreter_complete':True,'native_paid_equal':dict(sorted(yp.items())),'full_invoice_unchanged':True,'full_paid_count':sum(invoice['paid'].values()),'full_target_count':sum(invoice['targets'].values()),'first_protected_witness':observed[0] if observed else None,'protected_mismatch_count':len(observed),'first_clear_witness':clear[0] if clear else None,'clear_mismatch_count':len(clear),'first_public_output_witness':outputs[0] if outputs else None,'public_output_mismatch_count':len(outputs)},'elapsed_seconds':round(time.monotonic()-start,3)}
a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2),flush=True)
