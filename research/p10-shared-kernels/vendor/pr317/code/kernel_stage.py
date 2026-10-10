#!/usr/bin/env python3
"""Regenerate immutable PR315 input then apply the frozen p10 response kernels.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
Inherited kernel authorship and AI notices remain in kernel_transform.py.
"""
import sys
if not __debug__:raise SystemExit('assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,hashlib,json,importlib.util

def main():
 ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('selection',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
 src=a.source.resolve();out=a.output;assert not out.exists();out.mkdir(parents=True);sys.path.insert(0,str(src))
 def load(n,p):
  s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
 ctx=load('p10k_prepare',src/'prepare.py').prepare();p=load('p10k_physical',src/'code/physical527.py').run(ctx,ctx['SOURCE_TEXT'],output_dir=out/'producer-bit');p=load('p10k_parity',src/'parity_transform.py').run(p,output_dir=out/'parity')
 oldsha=hashlib.sha256(p['records'].tobytes()).hexdigest();assert oldsha=='ac0ea3a6163471235d4532492953c98b19e7c008a8522dc004d987e541189a33'
 baseline=set(ctx['C'].B);r=load('p10k_kernel',Path(__file__).with_name('kernel_transform.py')).run(p,output_dir=out,selection_path=a.selection)
 W,C=r['W'],r['C'];raw=r['records'].tobytes();digest=hashlib.sha256(raw).hexdigest();ini=r['initial_state'];fin=dict(ini)
 for k in range(0,len(r['records']),6):
  op,x,y,c,f,z=r['records'][k:k+6]
  if op==0:fin[x]=c
 st=dict(n=len(ini),v=W.v,h=W.h,initial=ini,final=fin,ZERO=r['ZERO'],FULL=r['FULL'],regs=ctx['regs'],source_owned_roles=sorted(W.source.values()),physical=r['physical'],source_covectors=C.cov,record_count=len(raw)//24,record_sha256=digest)
 fs={str(f):dict(dim=C.dimf[f],B=C.B[f],A=C.A[f])for f in C.B}
 def save(n,x):(out/n).write_text(json.dumps(x,sort_keys=True)+'\n')
 for n in ['249-records.bin','COHORT249-RECORDS.bin']:(out/n).write_bytes(raw)
 save('249-states.json',st);save('COHORT249-INITIAL.json',ini);save('COHORT249-FINAL.json',fin);(out/'frames.json').write_text(json.dumps(dict(h=W.h,frames=fs))+'\n');save('COHORT249-FRAMES.json',{f:z for f,z in fs.items() if int(f) not in baseline});save('249-DONOR-OWNERSHIP.json',dict(donor_keys=sorted(W.donor)));save('COHORT249-SELECTION.json',[])
 save('SOURCE-BINDING.json',dict(status='PASS_FRESH_PR315_AND_KERNEL_STAGE',word_sha256=digest,base_word_sha256=oldsha,active_helpers=len(ctx['regs']),freed_roles=[],record_count=len(raw)//24))
 print('PASS kernel p10',digest,flush=True)
if __name__=='__main__':main()
