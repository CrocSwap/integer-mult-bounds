"""Apply a source-bound subset of PR435/417 response relations after PR434 resets."""
from pathlib import Path
import copy,hashlib,json,sys
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parent

def reconstruct(raw,s):
 assert hashlib.sha256(raw).hexdigest()==s['input_sha256'];c=json.loads(raw);w=copy.deepcopy(c);v=c['v'];n=2*v+c['R'];frames=[sum(1<<x for x in f) for f in c['frames']];fids={m:i for i,m in enumerate(frames)};response=Counter();first={}
 for f,d,ss in c['D']:
  assert not frames[f]
  for x in ss:response[x]^=1<<(d-v)
 for phase in ('A','B','C'):
  for f,d,ss in c[phase]:
   for x in [d]+ss:
    if x>=2*v and f:first.setdefault(x,frames[f])
 pivots={};donors={};by=defaultdict(list)
 for lines,p,ds in s['entries']:
  E=sum(1<<x for x in lines);assert E in fids and E and 2*v<=p<n and p not in c['ret'] and p not in pivots and p not in donors and c['start'][p]==0
  z=response[p]
  for d in ds:
   assert 2*v<=d<n and d not in c['ret'] and d not in pivots and d!=p and c['start'][d]==0
   assert donors.setdefault(d,E)==E;z^=response[d];by[d,E].append(p)
  assert not z and all(E&first[x]==E for x in [p]+ds)
  pivots[p]=E
 assert not set(pivots)&set(donors)
 for p,E in pivots.items():w['start'][p]=fids[E]
 w['D']=[[f,d,[x for x in ss if x not in pivots]] for f,d,ss in w['D']]
 w['A']=[[fids[E],d,sorted(ps)] for (d,E),ps in sorted(by.items())]+w['A'];w['C']+=[[c['final'][0],d,sorted(ps)] for (d,E),ps in sorted(by.items())]
 data=json.dumps(w,sort_keys=True,separators=(',',':')).encode();assert hashlib.sha256(data).hexdigest()==s['output_sha256'];return data

def retime(raw,s):
 assert hashlib.sha256(raw).hexdigest()==s['source_sha256']
 original=json.loads(raw);w=copy.deepcopy(original)
 for phase in ('D','A','B','C'):
  w[phase]=[[f,d,[x]] for f,d,ss in w[phase] for x in ss]
 seen=set()
 for z in s['changes']:
  phase,i=z['phase'],z['index'];assert phase in ('D','A','B','C') and (phase,i) not in seen;seen.add((phase,i))
  assert 0<=i<len(w[phase]) and w[phase][i][0]==z['old_frame'] and 0<=z['new_frame']<len(w['frames'])
  w[phase][i][0]=z['new_frame']
 for phase in ('D','A','B','C'):
  assert [(d,x) for _,d,ss in original[phase] for x in ss]==[(d,x) for _,d,ss in w[phase] for x in ss]
 data=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
 assert hashlib.sha256(data).hexdigest()==s['output_sha256'];return data

if __name__=='__main__':
 import importlib.util
 spec=importlib.util.spec_from_file_location('early_reset',ROOT.parent/'e8-early-reset-reuse/replay.py');reset=importlib.util.module_from_spec(spec);spec.loader.exec_module(reset)
 raw=Path(sys.argv[1]).read_bytes();out=Path(sys.argv[2]);s=json.loads((ROOT/'SELECTION.json').read_text());rs=json.loads((ROOT/'RESET12.json').read_text());ts=json.loads((ROOT/'RETIMING.json').read_text())
 reset_raw=reset.reconstruct(raw,rs);kernel_raw=reconstruct(reset_raw,s);data=retime(kernel_raw,ts)
 controls=[]
 for name in ('wrong reset source','missing reset parent','wrong insertion time'):
  bad=copy.deepcopy(rs);rr=raw
  if name=='wrong reset source':rr+=b' '
  elif name=='missing reset parent':bad['entries'][0]['parents'].pop()
  else:bad['entries'][0]['position']=0
  try:reset.reconstruct(rr,bad)
  except AssertionError:controls.append(name)
  else:raise AssertionError(name)
 for name in ('wrong kernel source','missing donor','duplicate pivot'):
  bad=copy.deepcopy(s);rr=reset_raw
  if name=='wrong kernel source':rr+=b' '
  elif name=='missing donor':bad['entries'][0][2].pop()
  else:bad['entries'][1][1]=bad['entries'][0][1]
  try:reconstruct(rr,bad)
  except AssertionError:controls.append(name)
  else:raise AssertionError(name)
 for name in ('wrong old frame','duplicate frame change'):
  bad=copy.deepcopy(ts)
  if name=='wrong old frame':bad['changes'][0]['old_frame']=-1
  else:bad['changes'].append(copy.deepcopy(bad['changes'][0]))
  try:retime(kernel_raw,bad)
  except AssertionError:controls.append(name)
  else:raise AssertionError(name)
 out.write_bytes(data)
 result=dict(status='PASS_FROZEN_RESET_KERNEL_RETIMING',input_sha256=rs['source_sha256'],reset_sha256=rs['word_sha256'],kernel_sha256=s['output_sha256'],output_sha256=ts['output_sha256'],entries=len(s['entries']),total_entrance_rank=s['total_entrance_rank'],donor_slots=s['donor_slots'],new_frames=0,frame_changes=len(ts['changes']),additional_resets=len(rs['entries']),controls=controls)
 (out.parent/'bit-kernel-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
