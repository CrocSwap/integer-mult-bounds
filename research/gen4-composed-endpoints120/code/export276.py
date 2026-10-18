from pathlib import Path
import json,sys,importlib.util,time,hashlib,gzip
from collections import Counter
P=Path(sys.argv[1]).resolve();D=Path(sys.argv[2]).resolve();D.mkdir(parents=True,exist_ok=True);sys.dont_write_bytecode=True;sys.path.insert(0,str(P));start=time.monotonic()
def load(n):
 s=importlib.util.spec_from_file_location('temporal249_'+n,P/(n+'.py'));m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
def save(n,j):(D/n).write_text(json.dumps(j,separators=(',',':'))+'\n',encoding='utf8')
def export(n,p):
 records=p['records'];(D/(n+'-records.bin')).write_bytes(records.tobytes());(D/(n+'-records.bin.gz')).write_bytes(gzip.compress(records.tobytes(),mtime=0));final=dict(p['initial_state']);F=set(final.values())
 for k in range(0,len(records),6):
  op,a,b,c,f,z=records[k:k+6]
  if op==0:final[a]=c;F.update((b,c))
  elif op==1:F.add(f)
  elif op in(2,3):F.update((c,f))
 save(n+'-states.json',dict(initial=p['initial_state'],final=final,ZERO=p['ZERO'],FULL=p['FULL'],n=p['physical']['physical_registers'],v=1760,record_count=len(records)//6,record_sha256=hashlib.sha256(records.tobytes()).hexdigest(),physical=p['physical'],regs=p['context']['regs'],borrowed=list(p['context']['borrow']),removed=list(p['context']['removed']),source_owned_roles=sorted(p['context']['borrow']),source_covectors=p['C'].cov))
 return F

c=load('prepare').prepare();print('PREPARED',time.monotonic()-start,flush=True)
p=load('code/physical527').run(c,c['SOURCE_TEXT']);p=load('parity_transform').run(p);used=export('249',p)
C=p['C'];save('frames.json',dict(h=24,frames={str(f):dict(B=C.B[f],A=C.A[f],dim=C.dimf[f])for f in sorted(used)}))
save('249-DONOR-OWNERSHIP.json',dict(donor_keys=sorted(c['W'].donor),source_owned_roles=sorted(c['borrow'])))
save('EXPORT-RECEIPT.json',dict(status='PASS_EXACT_EMITTER_PARITY_EXPORT_NOT_FULL9_REPLAY',head='d428ab0462b9dfd3131ab4e89999f0adcd6173dd',frames=len(used),word='gen4',record_sha256=hashlib.sha256(p['records'].tobytes()).hexdigest(),seconds=time.monotonic()-start,scope='PR276 untouched physical emitter and parity filter. Compatibility filename249 does not assert identical word or applicability of old indices.'))
print('COMPLETE gen4 compatibility export',len(used),'frames',time.monotonic()-start,flush=True)
