# Prepared with substantial OpenAI Codex assistance; Apache-2.0.
# Second kernel mechanism: PR254/268/272 and gen4 multi-donor stage.
# New shared-donor selection: exact F2 maximum-weight closure and compatible-group packing.
# Usage: shared_kernel_stage.py INPUT SELECTION OUTPUT EXACT_CHECKER HIGHER_KERNEL_MODULE
import sys,json,hashlib,importlib.util,math,shutil,struct
from pathlib import Path
from array import array
from collections import Counter
from types import SimpleNamespace
sys.dont_write_bytecode=True
P, SELP, O, CHECKER, MODULE=map(Path,sys.argv[1:6]);O.mkdir(parents=True,exist_ok=True);assert P.resolve()!=O.resolve()
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
L=load('exactframe',CHECKER)
s=json.loads((P/'249-states.json').read_text());fj=json.loads((P/'frames.json').read_text());R=array('i');R.frombytes((P/'COHORT249-RECORDS.bin').read_bytes());n,v,h=s['n'],s['v'],s['h'];I={int(k):f for k,f in s['initial'].items()};FINAL={int(k):f for k,f in s['final'].items()};F={int(k):f for k,f in fj['frames'].items()};C=L.Checker.__new__(L.Checker);C.h=h;C.A={f:x['A']for f,x in F.items()};C.B={f:x['B']for f,x in F.items()};C.dimf={f:x['dim']for f,x in F.items()};C.cc={};lookup={json.dumps(B,separators=(',',':')):f for f,B in C.B.items()}
W=SimpleNamespace(v=v,h=h,module=L,gauge={s['regs'][r-2*v]:{'frame':f}for r,f in I.items()if r>=2*v and f!=s['ZERO']},donor={r:None for r in json.loads((P/'249-DONOR-OWNERSHIP.json').read_text())['donor_keys']},w={'gauges':[]})
W.register=lambda B:lookup[json.dumps(B,separators=(',',':'))]
meta=dict(s['physical']);hist=Counter();adds=0
for k in range(0,len(R),6):
 op,a,b,c,f,z=R[k:k+6]
 if op==0 and f:hist[f]+=1
 elif op==2:hist[z]+=1
 elif op==1:adds+=1
meta.update(paid_histogram=dict(hist),paid_rank_mass=sum(d*c for d,c in hist.items()),weighted_scalar_events=adds)
producer=dict(W=W,C=C,records=R,initial_state=I,final_state=FINAL,physical=meta,context={'regs':s['regs'],'borrow':{}},ZERO=s['ZERO'],FULL=s['FULL'])
sel=json.loads(SELP.read_text());assert sel['input_raw_sha256']==hashlib.sha256(R.tobytes()).hexdigest()==s['record_sha256']
K=load('higherkernel',MODULE);out=K.run(producer,output_dir=O,selection_path=SELP)
for p in P.iterdir():
 if p.is_file() and not p.name.startswith('kernel'):shutil.copy2(p,O/p.name)
# Rename the second-stage receipt and retain the first-stage receipt separately.
(O/'HIGHER-KERNEL-STAGE.json').write_bytes((O/'kernel.json').read_bytes())
for p in list(O.iterdir()):
 if p.name.startswith('kernel'):
  shutil.copy2(p,O/('HIGHER-'+p.name.upper()))
for p in P.iterdir():
 if p.is_file() and p.name.startswith('kernel'):shutil.copy2(p,O/p.name)
shutil.copy2(SELP,O/'HIGHER-KERNEL-SELECTION.json')
raw=out['records'].tobytes();sha=lambda b:hashlib.sha256(b).hexdigest();s.update(initial=out['initial_state'],physical=out['physical'],record_count=len(raw)//24,record_sha256=sha(raw));(O/'249-states.json').write_text(json.dumps(s,sort_keys=True,indent=2)+'\n');(O/'COHORT249-INITIAL.json').write_text(json.dumps(out['initial_state']));(O/'COHORT249-FINAL.json').write_text(json.dumps(FINAL))
for name in('COHORT249-RECORDS.bin','249-records.bin'):(O/name).write_bytes(raw)
if(P/'SOURCE-BINDING.json').exists():
 bind=json.loads((P/'SOURCE-BINDING.json').read_text());freed=set(bind['freed_roles']);mp={r:i for i,r in enumerate(r for r in range(n)if r not in freed)};mp[n]=len(mp)
 compact=b''.join(struct.pack('<6i',op,mp[a],b if op==0 else mp[b],c,f,z)for op,a,b,c,f,z in struct.iter_unpack('<6i',raw));(O/'COMPACT-RECORDS.bin').write_bytes(compact);bind.update(word_sha256=sha(raw),compact_word_sha256=sha(compact));(O/'SOURCE-BINDING.json').write_text(json.dumps(bind,indent=2)+'\n')
# Exact integer source-span check, independent of F2 row replay.
content=[[0]*h for _ in range(n+1)]
for i in range(v):content[i]=list(C.B[I[i]][0])
cache={};checked=bad=0
for k in range(0,len(out['records']),6):
 op,a,b,c,f,z=out['records'][k:k+6]
 if op==1:
  for r in(a,b):
   if v<=r<2*v or r==n:continue
   key=(f,tuple(content[r]))
   if key not in cache:cache[key]=all(L.dot(ar,content[r])==0 for ar in C.A[f])
   checked+=1;bad+=not cache[key]
  content[a]=[x+c*y for x,y in zip(content[a],content[b])]
 elif op==2:content[n]=list(content[a])
 elif op==3:content[n]=[0]*h
assert bad==0
receipt=json.loads((O/'HIGHER-KERNEL-STAGE.json').read_text());receipt.update(source_span_checked=checked,source_span_violations=bad,standalone_final_raw_sha256=sha(raw),wrapper_sha256=sha(Path(__file__).read_bytes()),exact_checker_sha256=sha(CHECKER.read_bytes()));(O/'HIGHER-KERNEL-STAGE.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS standalone source span',checked,'final',sha(raw),len(raw)//24,flush=True)
