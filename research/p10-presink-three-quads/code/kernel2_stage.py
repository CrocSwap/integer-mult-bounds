#!/usr/bin/env python3
"""Regenerate frozen PR320's final word and append three exact rank-two kernel entries.
Prepared with substantial OpenAI Codex assistance; Apache-2.0. Vendor sources stay immutable.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'vendor/predecessor';sys.path.insert(0,str(SRC))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

def export(run,dest,old_frames=None):
 dest=Path(dest);dest.mkdir();raw=run['records'];C=run['C'];W=run['W'];n=2*W.v+len(run['context']['regs']);initial=dict(run['initial_state']);final=dict(initial);used=set(initial.values())
 for k in range(0,len(raw),6):
  op,a,b,c,f,z=raw[k:k+6]
  if op==0:final[a]=c;used.update((b,c))
  elif op==1:used.add(f)
  elif op in (2,3):used.update((c,f))
 used.update(final.values());frames={str(f):dict(A=C.A[f],B=C.B[f],dim=C.dimf[f])for f in sorted(used)}
 state=dict(n=n,v=W.v,h=W.h,R=len(run['context']['regs']),ZERO=run['ZERO'],FULL=run['FULL'],regs=run['context']['regs'],initial=initial,final=final,record_sha256=hashlib.sha256(raw.tobytes()).hexdigest())
 (dest/'COHORT249-RECORDS.bin').write_bytes(raw.tobytes())
 for name,value in [('249-states',state),('frames',dict(h=W.h,frames=frames)),('COHORT249-INITIAL',initial),('COHORT249-FINAL',final),('COHORT249-FRAMES',{k:v for k,v in frames.items()if old_frames is None or k not in old_frames}),('COHORT249-SELECTION',{}),('physical',run['physical'])]:
  (dest/(name+'.json')).write_text(json.dumps(value,sort_keys=True)+'\n')
 if old_frames is not None:assert all(v==old_frames[k]for k,v in frames.items()if k in old_frames)
 return frames,state

def main(out):
 out=Path(out);pin=read(ROOT/'SOURCE.json');baseline=out/'predecessor'
 # Capture the return value of the unchanged final source stage. The hook only
 # stores that object and returns it unchanged; all strict source stages finish
 # before this wrapper inspects or transforms it. No source replay is skipped.
 verifier=load('frozen_presink_verify',SRC/'verify.py');original_load=verifier.load;captured={}
 def source_load(name):
  module=original_load(name)
  if name=='portable_bit':
   bit_load=module.load
   def observe_load(name,path):
    child=bit_load(name,path)
    if name=='portable527_reorder':
     original_run=child.run
     def observe_run(*args,**kwargs):
      value=original_run(*args,**kwargs);captured['run']=value;return value
     child.run=observe_run
    return child
   module.load=observe_load
  return module
 verifier.load=source_load;saved_argv=sys.argv;sys.argv=[str(SRC/'verify.py'),'--output',str(baseline)]
 try:verifier.main()
 finally:sys.argv=saved_argv
 ver=read(baseline/'verification.json');assert ver['inputs_unchanged'] and ver['manifest_sha256']==pin['predecessor']['manifest_sha256']
 import word_pins
 assert word_pins.RECORD is None
 run=captured['run']
 assert hashlib.sha256(run['records'].tobytes()).hexdigest()==pin['base_word_sha256']
 assert gzip.decompress((baseline/'reorder-records.bin.gz').read_bytes())==run['records'].tobytes(),'Separate strict source replays disagree'
 frames,oldstate=export(run,out/'base');selection=ROOT/'stages/kernel2-selection.json';kt=load('portable527_kernel_extra',SRC/'kernel_transform.py')
 receipts=out/'kernel2';result=kt.run(run,output_dir=receipts,selection_path=selection,tag='kernel2')
 _,newstate=export(result,out/'candidate',frames);assert newstate['record_sha256']==pin['final_word_sha256']
 assert word_pins.RECORD is None and oldstate['regs']==newstate['regs']
 print('PASS source-bound kernel2 stage '+newstate['record_sha256'],flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('output');main(ap.parse_args().output)
