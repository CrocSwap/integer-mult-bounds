"""Accept timing-only phase receipt differences; reject semantic differences.
OpenAI Codex assistance; Apache-2.0. Only seconds is excluded from semantic pins.
"""
from pathlib import Path
import sys,json,copy,hashlib
from assemble import assemble
from generated_identity import phase_value,json_identity
base,audit,out=map(Path,sys.argv[1:4]);assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
digest=lambda v:hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
op=audit/'OWNERS-AND-PROFILE.json';ip=audit/'PREFIX-AND-INVOICE.json';owner=json.loads(op.read_text());invoice=json.loads(ip.read_text());baseline=assemble(owner,invoice,sha(op),sha(ip));accepted=[];rejected=[]
for pid in invoice['providers']:
 original=json.loads((base/'providers'/pid/'CLIFFORD-REVIEW.json').read_text())
 for kind in('timing_only','substantive_phase_failure'):
  phase=copy.deepcopy(original)
  if kind=='timing_only':phase['seconds']+=123.456789
  else:phase['all_child_equalities_include_global_phase']=False
  raw=(json.dumps(phase,indent=2)+'\n').encode();rawsha=hashlib.sha256(raw).hexdigest();semantic=json_identity(phase_value(base/'providers'/pid,phase))
  o,i=copy.deepcopy(owner),copy.deepcopy(invoice);name='CLIFFORD-REVIEW.json';o['source_artifacts']['providers/'+pid+'/'+name]=i['providers'][pid]['artifacts'][name]=rawsha
  o['provider_phase_semantic_sha256'][pid]=i['provider_phase_semantic_sha256'][pid]=i['providers'][pid]['semantic_artifact_sha256'][name]=semantic
  o['provider_artifact_semantic_sha256'][pid][name]=semantic
  oh=digest(o);i['owner_audit_sha256']=oh
  assert rawsha!=owner['source_artifacts']['providers/'+pid+'/'+name]
  if kind=='timing_only':
   assert semantic==invoice['provider_phase_semantic_sha256'][pid]
   r=assemble(o,i,oh,digest(i));assert r['kappa']==baseline['kappa'];accepted.append(pid)
  else:
   assert semantic!=invoice['provider_phase_semantic_sha256'][pid]
   try:assemble(o,i,oh,digest(i))
   except AssertionError:rejected.append(pid)
   else:raise AssertionError('semantic phase failure accepted')
assert len(accepted)==len(rejected)==3
out.write_text(json.dumps(dict(status='PASS_PHASE_REVIEW_TIMING_PORTABILITY_AND_SEMANTIC_REJECTION',timing_only_accepted=accepted,substantive_phase_failure_rejected=rejected,kappa=baseline['kappa'],source_owner_sha256=sha(op),source_invoice_sha256=sha(ip),scope='Actual phase receipt JSON is changed, raw artifact bindings and owner digest are consistently recomputed, and all substantive semantics are freshly hashed. Only seconds may vary; no phase correctness field is omitted from the frozen digest.'),indent=2)+'\n');print('PASS',len(accepted),len(rejected))
