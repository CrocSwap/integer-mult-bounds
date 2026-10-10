#!/usr/bin/env python3
"""Regenerate PR315 parity-fused word and export its full exact registry.
Prepared with OpenAI Codex assistance; Apache-2.0, upstream provenance retained.
"""
import sys
if not __debug__:raise SystemExit('assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,importlib.util,json,hashlib

def main():
 ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
 src=a.source.resolve();out=a.output;assert not out.exists();out.mkdir(parents=True);sys.path.insert(0,str(src))
 def load(name,path):
  z=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(z);sys.modules[name]=m;z.loader.exec_module(m);return m
 ctx=load('p10_export_prepare',src/'prepare.py').prepare();W,C=ctx['W'],ctx['C']
 raw=load('p10_export_physical',src/'code/physical527.py').run(ctx,ctx['SOURCE_TEXT'],output_dir=out/'producer-bit')
 bit=load('p10_export_parity',src/'parity_transform.py').run(raw,output_dir=out/'parity')
 records=bit['records'];initial=bit['initial_state'];final=dict(initial)
 for k in range(0,len(records),6):
  op,x,y,c,f,z=records[k:k+6]
  if op==0:final[x]=c
 fs={str(f):dict(dim=C.dimf[f],B=C.B[f],A=C.A[f])for f in C.B}
 sha=hashlib.sha256(records.tobytes()).hexdigest()
 assert W.h==20 and W.v==960 and len(initial)==10150 and sha=='ac0ea3a6163471235d4532492953c98b19e7c008a8522dc004d987e541189a33'
 st=dict(n=len(initial),v=W.v,h=W.h,initial=initial,final=final,ZERO=bit['ZERO'],FULL=bit['FULL'],regs=ctx['regs'],source_owned_roles=sorted(W.source.values()),physical=bit['physical'],source_covectors=C.cov,record_sha256=sha,record_count=len(records)//6)
 def save(name,x):(out/name).write_text(json.dumps(x,sort_keys=True)+'\n')
 save('249-states.json',st);save('frames.json',dict(h=W.h,frames=fs));save('COHORT249-INITIAL.json',initial);save('COHORT249-FINAL.json',final);save('COHORT249-FRAMES.json',{})
 for name in ['249-records.bin','COHORT249-RECORDS.bin']:(out/name).write_bytes(records.tobytes())
 save('SOURCE-BINDING.json',dict(status='PASS_FRESH_PR315_PARITY_WORD_EXPORT',word_sha256=sha,record_count=len(records)//6,active_helpers=len(ctx['regs']),freed_roles=[]))
 print('PASS source export',sha,len(fs),flush=True)
if __name__=='__main__':main()
