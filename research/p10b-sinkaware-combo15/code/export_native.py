#!/usr/bin/env python3
"""Export an actual p10 candidate with physical-role-derived prefix endpoint mapping.
Input exports are read-only. Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,json,struct,hashlib,shutil
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True)+'\n')
def frames(path):
 f=read(path);return f.get('frames',f)
def validate(src):
 m=read(src/'meta.json');regs=read(src/'regs.json') if (src/'regs.json').exists() else m['regs'];i=read(src/'initial.json');f=read(src/'final.json');fs=frames(src/'frames.json');n=m['n'];v=m['v'];raw=src/'records.bin'
 assert n==2*v+len(regs) and len(set(regs))==len(regs) and set(i)==set(f)==set(map(str,range(n)))
 assert all(str(k)in fs for k in set(i.values())|set(f.values()))
 for key in ['word_sha','word_sha256','record_sha256','raw_sha256']:
  if key in m:assert sha(raw)==m[key]
 assert raw.stat().st_size%24==0
 return m,regs,i,f,fs

def run(base_input,candidate_input,output,h=20):
 bs,cs=map(lambda x:Path(x).resolve(),(base_input,candidate_input));out=Path(output).resolve();assert not out.exists() and not out.is_relative_to(bs) and not out.is_relative_to(cs);out.mkdir(parents=True);base=out/'base';cand=out/'candidate';base.mkdir();cand.mkdir()
 bm,br,bi,bf,bfs=validate(bs);cm,cr,ci,cf,cfs=validate(cs);v=cm['v'];n=cm['n'];assert bm['v']==v==960 and h==20 and set(cr)<=set(br)
 assert cm['ZERO']==bm['ZERO'] and cm['FULL']==bm['FULL']
 lookup={r:2*v+j for j,r in enumerate(cr)};rolemap={i:i for i in range(2*v)};rolemap.update({2*v+j:lookup[r]for j,r in enumerate(br)if r in lookup});assert set(rolemap.values())==set(range(n))
 assert all(bfs[k]==cfs[k]for k in set(bfs)&set(cfs)), 'Shared frame ID changed'
 used=set(ci.values())|set(cf.values());raw=(cs/'records.bin').read_bytes()
 for op,a,b,c,f,z in struct.iter_unpack('<6i',raw):
  assert 0<=a<=n
  if op==0:used.update((b,c))
  elif op==1:assert 0<=b<=n;used.add(f)
  elif op in (2,3):assert 0<=b<=n;used.update((c,f))
  else:raise AssertionError('Unknown opcode')
 fs={str(k):cfs[str(k)]for k in sorted(used)};nf={k:f for k,f in fs.items()if k not in bfs}
 assert all(len(r)==h for f in fs.values()for r in f['A']+f['B'])
 st=dict(n=n,v=v,h=h,R=len(cr),ZERO=cm['ZERO'],FULL=cm['FULL'],regs=cr,initial=ci,final=cf,record_sha256=hashlib.sha256(raw).hexdigest())
 for name,value in [('249-states',st),('frames',dict(h=h,frames=fs)),('COHORT249-INITIAL',ci),('COHORT249-FINAL',cf),('COHORT249-FRAMES',nf),('COHORT249-SELECTION',{})]:write(cand/(name+'.json'),value)
 (cand/'COHORT249-RECORDS.bin').write_bytes(raw)
 if (cs/'physical.json').exists():shutil.copyfile(cs/'physical.json',cand/'physical.json')
 oldst=dict(st,initial={str(rolemap[int(i)]):f for i,f in bi.items()if int(i)in rolemap},final={str(rolemap[int(i)]):f for i,f in bf.items()if int(i)in rolemap},record_sha256=sha(bs/'records.bin'))
 write(base/'249-states.json',oldst);write(base/'frames.json',dict(h=h,frames=bfs));shutil.copyfile(bs/'records.bin',base/'COHORT249-RECORDS.bin');write(out/'ROLE-MAP.json',rolemap)
 sources=[p/n for p in (bs,cs) for n in ('meta.json','regs.json','initial.json','final.json','frames.json','records.bin') if (p/n).exists()]
 result=dict(status='PASS_NATIVE_EXPORT_FROM_ACTUAL_PHYSICAL_REGISTERS',base_n=bm['n'],candidate_n=n,R=len(cr),v=v,h=h,removed_physical_registers=sorted(set(br)-set(cr)),base_word_sha256=oldst['record_sha256'],candidate_word_sha256=st['record_sha256'],all_used_frames=len(fs),new_used_frames=len(nf),input_hashes={str(p):sha(p)for p in sources},role_map_sha256=sha(out/'ROLE-MAP.json'),base_raw_scope='Full prefix raw is used only for MOVE-pair census; candidate native legality uses the survivor-compacted prefix endpoints.')
 write(out/'EXPORT.json',result);print('PASS dynamic export',n,len(cr),len(fs),len(nf),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--candidate',required=True);ap.add_argument('--output',required=True);ap.add_argument('--h',type=int,default=20);a=ap.parse_args();run(a.base,a.candidate,a.output,a.h)
