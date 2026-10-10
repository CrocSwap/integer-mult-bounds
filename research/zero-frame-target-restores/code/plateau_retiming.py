"""Local PR270 retiming adapter: optional metadata copies and exact expected call delta replace the predecessor zero-call-delta restriction. All geometry/projection/rank/delta assertions retained; native and source-span checks required."""
#!/usr/bin/env python3
import argparse,json,hashlib,shutil,sys
from pathlib import Path
from array import array
from collections import Counter
if not __debug__:raise SystemExit('assertions are required')
assert sys.byteorder=='little' and array('i').itemsize==4
ap=argparse.ArgumentParser();ap.add_argument('export',type=Path);ap.add_argument('lead',type=Path);ap.add_argument('scan',type=Path);ap.add_argument('output',type=Path);args=ap.parse_args()
X,L,O=args.export,args.lead,args.output;O.mkdir()
for name in ('COHORT249-INITIAL.json','COHORT249-SELECTION.json','descent-selection.json',
             'DESCENT-RETIMING.json','DESCENT-REBIND-EVIDENCE.json'):
 if (L/name).exists():shutil.copy2(L/name,O/name)
fs={int(k):v for k,v in json.loads((X/'frames.json').read_text())['frames'].items()};new={int(k):v for k,v in json.loads((L/'COHORT249-FRAMES.json').read_text()).items()};fs.update(new)
scan=json.loads(args.scan.read_text());added={int(k):v for k,v in scan.get('newframes',{}).items()}
assert not set(added)&set(fs),'plateau frame ID collision'
from verify_frames import validate
for frame in added.values():validate(frame)
fs.update(added)
chosen=[];roles=set();mutations={};expected=Counter()
for c in scan['candidates']:
 assert not set(c['roles'])&roles,'frozen plateau roles overlap'
 chosen.append(c);roles.update(c['roles']);expected.update({int(k):v for k,v in c['delta'].items()})
 for g in c['gates']:assert g not in mutations;mutations[g]=(c['old_frame'],c['new_frame'])
 if str(c['new_frame']) in scan.get('newframes',{}):new[c['new_frame']]=fs[c['new_frame']]
print('selected',len(chosen),'gates',len(mutations),'entropy_gain',sum(c['entropy_gain'] for c in chosen),'delta',dict(expected),flush=True)
raw=array('i');raw.frombytes((L/'COHORT249-RECORDS.bin').read_bytes());events=[tuple(raw[k:k+6]) for k in range(0,len(raw),6) if raw[k]]
assert len(raw)%6==0
assert hashlib.sha256(raw.tobytes()).hexdigest()==scan['input_sha256'],'frozen plateau input mismatch'
st=json.loads((X/'249-states.json').read_text());n=st['n'];initial={int(k):v for k,v in json.loads((L/'COHORT249-INITIAL.json').read_text()).items()};final={int(k):v for k,v in st['final'].items()};state=dict(initial);out=array('i');cache={};hist=Counter();copy=None
def sub(a,b):
 if a==b:return True
 if (a,b) not in cache:cache[a,b]=fs[a]['dim']<=fs[b]['dim'] and all(sum(x*y for x,y in zip(u,v))==0 for u in fs[a]['B'] for v in fs[b]['A'])
 return cache[a,b]
def move(s,f):
 p=state[s]
 if p==f:return
 assert sub(p,f),(s,p,f)
 r=fs[f]['dim']-fs[p]['dim'];out.extend((0,s,p,f,r,0));state[s]=f
 if r:hist[r]+=1
for i,(op,a,b,c,f,z) in enumerate(events):
 if op==1:
  if i in mutations:
   old,fnew=mutations[i];assert old==f;f=fnew
  move(a,f);move(b,f);out.extend((op,a,b,c,f,z))
 elif op==2:
  assert copy is None and b==n;move(a,c);state[b]=f;copy=(a,b,c,f);hist[z]+=1;out.extend((op,a,b,c,f,z))
 else:
  assert op==3 and copy==(a,b,c,f) and state[a]==c and state[b]==f;del state[b];copy=None;out.extend((op,a,b,c,f,z))
for s in sorted(final):move(s,final[s])
assert copy is None and state==final
def projection(a):return hashlib.sha256(b''.join(a[k:k+4].tobytes()+a[k+5:k+6].tobytes() for k in range(0,len(a),6) if a[k])).hexdigest()
assert projection(raw)==projection(out)
replay=json.loads((L/'COHORT249-REPLAY.json').read_text());oldH=Counter({int(k):v for k,v in replay['histogram'].items()});delta=Counter(hist);delta.subtract(oldH);delta={k:v for k,v in delta.items() if v};expected={k:v for k,v in expected.items() if v};assert delta==expected,(delta,expected)
assert delta=={int(k):v for k,v in scan['expected_delta'].items() if v}
assert set(mutations)<=set(range(len(events))) and all(events[g][0]==1 for g in mutations)
assert sum(k*v for k,v in hist.items())==sum(k*v for k,v in oldH.items())
assert sum(hist.values())-sum(oldH.values())==sum(expected.values())
total=Counter({int(k):v for k,v in replay['delta'].items()});total.update(delta)
replay.update(new_rank_mass=sum(k*v for k,v in hist.items()),actual_kernel_entrance_rank=1762,pricing_stock_adjustment=1980,status='EXPERIMENTAL_CONNECTED_PLATEAU_RETIMING',histogram={str(k):v for k,v in sorted(hist.items())},delta={str(k):v for k,v in sorted(total.items()) if v},plateau_histogram_delta=delta,new_records=len(out)//6)
(O/'COHORT249-REPLAY.json').write_text(json.dumps(replay,indent=2)+'\n');(O/'COHORT249-RECORDS.bin').write_bytes(out.tobytes());(O/'COHORT249-FRAMES.json').write_text(json.dumps(new)+'\n')
receipt=dict(status='FINITE_TRANSCRIPT_REWRITE_CHECKED_NATIVE_CHECKERS_PENDING',selected=chosen,delta=delta,unchanged_scalar_copy_projection=projection(raw),input_sha256=hashlib.sha256(raw.tobytes()).hexdigest(),output_sha256=hashlib.sha256(out.tobytes()).hexdigest(),paid_calls=sum(hist.values()),rank_mass=sum(k*v for k,v in hist.items()))
(O/'PLATEAU-RETIMING.json').write_text(json.dumps(receipt,indent=2)+'\n');print('wrote',O,'calls',sum(hist.values()),flush=True)
