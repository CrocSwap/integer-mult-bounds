from pathlib import Path
import json,sys,importlib.util,time,hashlib
from collections import Counter
import argparse, shutil
if not __debug__: raise SystemExit('Assertions required; refusing -O')
ap=argparse.ArgumentParser(); ap.add_argument('--base',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
P=args.base.resolve(); D=args.output.resolve(); D.mkdir(parents=True,exist_ok=False)
sys.dont_write_bytecode=True
sys.path.insert(0,str(P));start=time.monotonic()
def load(n):
 s=importlib.util.spec_from_file_location('export_gen4_'+n.replace('/','_'),P/(n+'.py'));m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
def save(n,j):(D/n).write_text(json.dumps(j,separators=(',',':'))+'\n')
c=load('prepare').prepare();print('PREPARED',time.monotonic()-start,flush=True)
p=load('code/physical527').run(c,c['SOURCE_TEXT'])
p=load('parity_transform').run(p)
records=p['records'];raw=records.tobytes();(D/'gen4-records.bin').write_bytes(raw)
final=dict(p['initial_state']);used=set(final.values());hist=Counter();adds=Counter()
for k in range(0,len(records),6):
 op,a,b,cc,f,z=records[k:k+6]
 if op==0:final[a]=cc;used.update((b,cc));hist[f]+=bool(f)
 elif op==1:used.add(f);adds[cc]+=1
 elif op in (2,3):used.update((cc,f));hist[z]+=op==2
n=len(p['initial_state']);v=c['W'].v
state=dict(initial=p['initial_state'],final=final,ZERO=p['ZERO'],FULL=p['FULL'],n=n,v=v,record_count=len(records)//6,record_sha256=hashlib.sha256(raw).hexdigest(),physical=p['physical'],regs=c['regs'],borrowed=list(c['borrow']),removed=list(c['removed']),source_owned_roles=sorted(c['borrow']),source_covectors=p['C'].cov)
save('gen4-states.json',state)
C=p['C'];save('frames.json',dict(h=24,frames={str(f):dict(B=C.B[f],A=C.A[f],dim=C.dimf[f])for f in sorted(used)}))
save('gen4-ownership.json',dict(donor_keys=sorted(c['W'].donor),phys=c['W'].phys,idx=c['idx'],pairs=c['W'].pairs))
save('EXPORT-RECEIPT.json',dict(status='FRESH_SOURCE_BOUND_EXPORT_NOT_FULL_VERIFICATION',head='d428ab0462b9dfd3131ab4e89999f0adcd6173dd',record_sha256=hashlib.sha256(raw).hexdigest(),n=n,v=v,frames=len(used),paid_histogram=dict(hist),adds=dict(adds),seconds=time.monotonic()-start))
print('EXPORTED',n,len(records)//6,len(used),time.monotonic()-start,flush=True)

assert state['record_sha256']=='60830cb24fbdd5a26942c4aa897d0ae30738ca5772ab83d6c57be666ddc95f7a'
for name in ['249-records.bin','COHORT249-RECORDS.bin']: shutil.copyfile(D/'gen4-records.bin',D/name)
shutil.copyfile(D/'gen4-states.json',D/'249-states.json')
save('COHORT249-INITIAL.json',state['initial']);save('COHORT249-FINAL.json',state['final']);save('COHORT249-FRAMES.json',{})
