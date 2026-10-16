from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Independently verify remaining emitted boundaries and freeze the audit."""
import gzip,hashlib,json,struct
from pathlib import Path
from collections import Counter
import numpy as np
if not __debug__:raise RuntimeError('Assertions must be enabled')
HERE=support.AUDIT;L=support.LOWER;A=support.ADM;C=support.FRAME/"SOURCE-GEOMETRY-CORRECTION.json"
def read(p):return json.loads(Path(p).read_bytes())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
result=read(L/'RESULT.json');phases=read(L/'extended-phases.json');receipts=read(HERE/'EXPECTED-OPERAND-HASHES.json');emitted={x['phase_index']:x['expanded_operand_sha256']for x in receipts}
manifest=read(L/'MANIFEST.json')
for name,value in manifest.items():assert digest(L/name)==value
boundary=np.frombuffer(gzip.decompress((L/'boundary-records.i32.gz').read_bytes()),dtype='<i4').reshape(-1,8)
assert len(boundary)==921600
cursor=0;chain=hashlib.sha256();counts=Counter();ranks=Counter()
for p in phases:
 chain.update(canon(p)+b'\n');kind=p['kind'];idx=p['phase_index']
 if kind=='helper':chain.update(bytes.fromhex(emitted[idx]));continue
 if kind=='paid_bank_completion':chain.update(canon(p['operations'])+b'\n');ranks[p['rank']]+=1;continue
 t=p['replica'];rows=[]
 def family(b,port):return (4*t+b)*960+port
 if kind=='idle':
  patterns={0:[(2,38,0),(3,38,1)],1:[(2,19,2),(3,19,3)],2:[(0,42,4),(1,42,5),(2,4,6),(3,4,7)]}[p['which']]
  for bank,rank,pid in patterns:
   for port in range(960):rows.append([idx,4,family(bank,port),-1,0,rank,pid,port])
 elif kind=='bridge':
  patterns={0:[(0,2,1),(3,1,-1)],1:[(3,1,1),(0,2,-1)],2:[(1,3,-1),(2,0,1)]}[p['which']]
  for dst,src,sign in patterns:
   for port in range(960):rows.append([idx,5,family(dst,port),family(src,port),sign,0,p['which'],port])
 else:
  assert kind=='terminal_exchange'
  for dst,src in [(0,1),(2,3)]:
   for port in range(960):rows.append([idx,7,family(dst,port),family(src,port),-1,0,0,port])
 exp=np.asarray(rows,dtype='<i4');actual=boundary[cursor:cursor+len(rows)];assert np.array_equal(actual,exp)
 cursor+=len(rows);chain.update(actual.tobytes())
 for row in rows:
  counts[row[1]]+=1
  if row[1]==4:ranks[row[5]]+=1
assert cursor==len(boundary) and dict(counts)=={4:460800,5:345600,7:115200}
assert chain.hexdigest()==result['operand_binding']['extended_compositional_program_sha256']
assert ranks=={38:115200,19:115200,42:115200,4:115200,49:5,11:5}
paid=read(support.BANK/"split_49_11/RESULT.json")
assert result['invoice']['terms']==paid['finite_invoice']['terms']
assert result['source_admission_sha256']==digest(A/'ADMISSION-RESULT.json')
assert not result['whole_final_raw_frame_program_regenerated'] and not result['unconditional_all_size_theorem']
support.verify_correction()
base=read(HERE/'AUDIT-RESULT.json');lower=read(HERE/'LOWERING-AUDIT-RESULT.json')
assert base['checker_sha256']==digest(support.HERE/'audit/audit_contract.py')
assert lower['checker_sha256']==digest(support.HERE/'audit/audit_lowering.py')
assert lower['emitter_operand_receipts_matched'] and lower['source_chronology_correction_sha256']==digest(C)
final={'status':'PASS_NEW_PAID_COMPLETION_COMPOSITIONAL_OBLIGATION','candidate_sha256':result['candidate_sha256'],'split':[49,11],'new_gate_closed':True,'source_correction_bound':True,'raw_regular_frame_regeneration_claimed':False,'all_size_unconditional_claimed':False,'emitted_boundary_records_checked':len(boundary),'all_expanded_scalar_records_checked':100887900,'compositional_program_sha256':chain.hexdigest(),'kappa':base['kappa'],'bindings':{'incremental_result':digest(L/'RESULT.json'),'incremental_manifest':digest(L/'MANIFEST.json'),'source_admission':digest(A/'ADMISSION-RESULT.json'),'source_chronology_correction':digest(C),'contract_audit':digest(HERE/'AUDIT-RESULT.json'),'lowering_audit':digest(HERE/'LOWERING-AUDIT-RESULT.json')},'retained_interfaces':result['inherited_interfaces'],'normalizer_direction_ambiguity':'Resolved by explicit pi/inverse chronological lists and independent actual-basis-image tests.','scope':'The exact NEW paid-complement composition is verified. The unchanged regular final-frame/reorder, arbitrary-dirty endpoint and generic compiler interfaces remain named inherited premises; no zero/clean bank initialization, new dense primitive, fractional physical index, omitted child fee or relaxed rank guard is introduced.','checker_sha256':digest(__file__)}
(HERE/'FINAL-AUDIT.json').write_text(json.dumps(final,indent=2)+'\n')
print(json.dumps(final,indent=2))
