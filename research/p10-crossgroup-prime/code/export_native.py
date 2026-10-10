#!/usr/bin/env python3
"""Export actual crossgroup word and sink-compacted prefix endpoints for native audits."""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
import json,struct,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True)+'\n')
def run(out):
 out=Path(out);src=out/'materialized';base=out/'base';cand=out/'candidate';base.mkdir();cand.mkdir();pin=read(ROOT/'SOURCE.json')
 bf=read(src/'target-baseline/frames.json');fs=read(src/'final/frames.json');ini=read(src/'final/initial.json');fin=read(src/'final/final.json');raw=(src/'final/records.bin').read_bytes();used=set(ini.values())|set(fin.values())
 for op,a,b,c,f,z in struct.iter_unpack('<6i',raw):
  if op==0:used.update((b,c))
  elif op==1:used.add(f)
  elif op in (2,3):used.update((c,f))
  else:raise AssertionError('Unknown event')
 assert all(bf[k]==fs[k]for k in set(bf)&set(fs))
 fs={str(k):fs[str(k)]for k in sorted(used)};nf={k:v for k,v in fs.items()if k not in bf};meta=read(src/'final/meta.json');regs=read(src/'final/regs.json');v=meta['v'];rolemap={int(k):v for k,v in read(src/'role-map.json').items()};oldregs=read(src/'target-baseline/regs.json')
 assert len(set(regs))==len(regs)==8223 and meta['n']==2*v+len(regs)==10143 and v==960
 assert {old:regs[new-2*v]for old,new in rolemap.items()if old>=2*v}=={old:oldregs[old-2*v]for old in rolemap if old>=2*v}
 st=dict(n=meta['n'],v=v,h=20,R=len(regs),ZERO=meta['ZERO'],FULL=meta['FULL'],regs=regs,initial=ini,final=fin,record_sha256=hashlib.sha256(raw).hexdigest());assert st['record_sha256']==pin['final_word_sha256']
 for name,value in [('249-states',st),('frames',dict(h=20,frames=fs)),('COHORT249-INITIAL',ini),('COHORT249-FINAL',fin),('COHORT249-FRAMES',nf),('COHORT249-SELECTION',{}),('physical',read(src/'final/physical.json'))]:write(cand/(name+'.json'),value)
 (cand/'COHORT249-RECORDS.bin').write_bytes(raw)
 oldst=dict(st,initial=read(src/'baseline-compacted-initial.json'),final=read(src/'baseline-compacted-final.json'),record_sha256=hashlib.sha256((src/'target-baseline/records.bin').read_bytes()).hexdigest());assert oldst['record_sha256']==pin['target_prefix_sha256']
 write(base/'249-states.json',oldst);write(base/'frames.json',dict(h=20,frames=bf));shutil.copyfile(src/'target-baseline/records.bin',base/'COHORT249-RECORDS.bin')
 receipt=dict(status='PASS_ACTUAL_WORD_AND_PREFIX_ENDPOINT_EXPORT',candidate_word_sha256=st['record_sha256'],prefix_word_sha256=oldst['record_sha256'],n=st['n'],R=st['R'],new_used_frames=len(nf),all_used_frames=len(fs),surviving_role_map_sha256=hashlib.sha256((src/'role-map.json').read_bytes()).hexdigest(),base_raw_scope='The full 10150-role prefix is used only to census unchanged MOVE projector pairs; native endpoints are mapped into the final 10143-role namespace. Prefix raw is not replayed against compacted state.')
 write(out/'EXPORT.json',receipt);print('PASS native export',len(fs),'frames',len(nf),'new',flush=True)
if __name__=='__main__':run(sys.argv[1])
