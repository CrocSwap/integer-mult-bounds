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
save('EXPORT-RECEIPT.json',dict(status='PASS_EXACT_EMITTER_PARITY_EXPORT_NOT_FULL9_REPLAY',head='739c3bb0ad0596f427e0a72a2ebeca23277217a3',frames=len(used),word='gen5',record_sha256=hashlib.sha256(p['records'].tobytes()).hexdigest(),seconds=time.monotonic()-start,scope='Pinned PR290 inherited physical emitter and parity filter. Compatibility filename249 does not assert identical word or applicability of old indices.'))
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

# Bind the original coordinates to the actual post-kernel physical context.
assert c['idx']=={r:2*st['v']+i for i,r in enumerate(st['regs'])}
assert p['context']['regs']==st['regs']==c['regs']
for stage in ('descent_transform','target_transform','kernel_transform'):
 p=load(stage).run(p)
ctx=p['context']
assert ctx['regs']==st['regs'] and ctx['idx']==c['idx']
assert (2*p['W'].v+len(ctx['regs']),p['W'].v)==(st['n'],st['v'])
final=dict(p['initial_state'])
for i in range(0,len(p['records']),6):
 op,a,b,f,rank,z=p['records'][i:i+6]
 if op==0:final[a]=f
assert {str(k):v for k,v in final.items()}==st['final']
assert p['kernel_census']['proof']['source_context_preserved']
save('SOURCE-CONTEXT.json',dict(status='PASS_FRESH_PR290_ORDERED_ROLES_INDEX_AND_KERNEL_WORD',
 ordered_helper_roles=len(st['regs']),physical_registers=st['n'],ordered_regs_and_index_equal=True,
 original_final_endpoints_equal=True,kernel_initial={str(k):v for k,v in p['initial_state'].items()},
 kernel_word_sha256=hashlib.sha256(p['records'].tobytes()).hexdigest()))
