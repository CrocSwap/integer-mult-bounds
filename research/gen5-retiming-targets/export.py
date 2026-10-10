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
save('EXPORT-RECEIPT.json',dict(status='PASS_EXACT_EMITTER_PARITY_EXPORT_NOT_FULL9_REPLAY',head='b40c1a3d8f40ee3764b9f13fe850f663f2d8c834',frames=len(used),word='gen5',record_sha256=hashlib.sha256(p['records'].tobytes()).hexdigest(),seconds=time.monotonic()-start,scope='PR285 untouched physical emitter and parity filter. Compatibility filename249 does not assert identical word or applicability of old indices.'))
print('COMPLETE gen5 compatibility export',len(used),'frames',time.monotonic()-start,flush=True)

# Native stages consume the same baseline word through the cohort interface.
import shutil
st=json.loads((D/'249-states.json').read_text());assert (st['n'],st['v'])==(19406,1760)
import struct
es=list(struct.iter_unpack('<6i',(D/'249-records.bin').read_bytes()))
H=Counter(e[4] for e in es if e[0]==0 and e[4]);H.update(e[5] for e in es if e[0]==2)
assert sum(r*c for r,c in H.items())==411356
shutil.copyfile(D/'249-records.bin',D/'COHORT249-RECORDS.bin')
save('COHORT249-FRAMES.json',{});save('COHORT249-INITIAL.json',st['initial']);save('COHORT249-SELECTION.json',[])
save('IDENTITY.json',{str(i):i for i in range(st['n']+1)})
save('COHORT249-REPLAY.json',dict(status='SOURCE_BOUND_GEN5_BASELINE_PARITY_EXPORT',histogram=dict(H),delta={},new_entrance_rank=0,new_rank_mass=411356,new_records=len(es)))
