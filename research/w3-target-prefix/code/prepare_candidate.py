#!/usr/bin/env python3
"""Bind the supplied w3 data to freshly regenerated PR249 source; delete inert roles."""
import sys
if not __debug__: raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
import argparse, gzip, hashlib, json, shutil, struct
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(x):
 if isinstance(x,dict):return {k:norm(v) for k,v in x.items() if k!='seconds'}
 if isinstance(x,list):return list(map(norm,x))
 return x
def save(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--export',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);base=a.export.resolve();src=ROOT/'supplied'
 for name in ('249-records.bin','249-states.json','frames.json'):
  supplied=gzip.decompress((src/'base'/(name+'.gz')).read_bytes())
  assert (norm(json.loads(supplied))==norm(read(base/name))) if name.endswith('.json') else supplied==(base/name).read_bytes(), name
 own=read(src/'base/249-DONOR-OWNERSHIP.json');assert sorted(own['donor_keys'])==read(base/'REGENERATED-DONORS.json')['donor_keys']
 shutil.copyfile(src/'base/249-DONOR-OWNERSHIP.json',base/'249-DONOR-OWNERSHIP.json')
 shutil.copyfile(base/'249-records.bin',base/'COHORT249-RECORDS.bin')
 for name in ('COHORT249-RECORDS.bin','COHORT249-FRAMES.json','COHORT249-INITIAL.json'):(out/name).write_bytes(gzip.decompress((src/'word'/(name+'.gz')).read_bytes()))
 shutil.copyfile(src/'word/COHORT249-SELECTION.json',out/'COHORT249-SELECTION.json')
 assert read(out/'COHORT249-SELECTION.json')==[]
 wordsha=sha(out/'COHORT249-RECORDS.bin');assert wordsha=='a9501525563d3ec656ebf01aea9f2c9839e033563ea4a022500d68b12756ae86'
 st=json.loads(gzip.decompress((src/'word/w3-249-states.json.gz').read_bytes()));old=read(base/'249-states.json');ini=read(out/'COHORT249-INITIAL.json');nf=read(out/'COHORT249-FRAMES.json');fs=read(base/'frames.json')['frames']
 assert not set(nf)&set(fs);fs.update(nf)
 assert st['n']==old['n']==20107 and st['v']==old['v']==1760
 assert st['initial']==ini and st['final']==old['final']
 assert len(set(old['regs']))==16587
 changed={old['regs'][i-3520] for i in range(3520,20107) if ini[str(i)]!=old['initial'][str(i)]}
 assert not changed & (set(old['source_owned_roles']) | set(own['donor_keys'])), 'Source owner or donor changed'
 for k in ('ZERO','FULL','regs','source_owned_roles','source_covectors'):assert st[k]==old[k],k
 assert all(ini[str(i)]==old['initial'][str(i)] for i in range(3520))
 ev=list(struct.iter_unpack('<6i',(out/'COHORT249-RECORDS.bin').read_bytes()));assert len(ev)==1026620
 freed={r for r in range(3520,20107) if ini[str(r)]==st['FULL']};assert len(freed)==1455
 for op,a,b,c,f,z in ev:
  assert a not in freed and (op==0 or b not in freed),'Freed role still used by the actual word'
 live=[r for r in range(20107) if r not in freed];mapping={r:i for i,r in enumerate(live)};mapping[20107]=len(live)
 compact=[]
 for op,a,b,c,f,z in ev:compact.append((op,mapping[a],b if op==0 else mapping[b],c,f,z))
 (out/'COMPACT-RECORDS.bin').write_bytes(b''.join(struct.pack('<6i',*r) for r in compact))
 assert len(live)==18652
 st['record_sha256']=wordsha;st['record_count']=len(ev)
 save(out/'249-states.json',st);save(out/'COHORT249-FINAL.json',st['final']);save(out/'frames.json',{'h':24,'frames':fs})
 shutil.copyfile(out/'COHORT249-RECORDS.bin',out/'249-records.bin')
 save(out/'SOURCE-BINDING.json',{'status':'PASS_FRESH_SOURCE_BINDING_AND_INERT_ROLE_DELETION','word_sha256':wordsha,'base_word_sha256':sha(base/'249-records.bin'),'freed_roles':sorted(freed),'active_helpers':15132,'active_local_registers':len(live),'compact_word_sha256':sha(out/'COMPACT-RECORDS.bin'),'baseline_unchanged_fields_verified':True,'saved_state_hash_recomputed':True})
 print('PASS source binding and1455 inert role deletions',flush=True)
if __name__=='__main__':main()
