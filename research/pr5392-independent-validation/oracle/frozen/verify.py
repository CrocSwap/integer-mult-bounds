"""Offline #5392 case check with exact unmodified published #5391 library.

No scientific engine or candidate-author code is imported/executed. Reviewer
policy is a frozen proposal requiring separate root/auditor approval for public
admission. Mutation tests alter memory only and confer no authority.
"""
from pathlib import Path
import copy
import json
import oracle as o

HERE=Path(__file__).resolve().parent
LIB_SHA='51a9d378c36ad9cb3f7f0cd9db48cae7d43d971bbd6cb028dd9bf6aa60cd8468'
POLICY_SHA='ba643471662140c171d94fdc94c51307f8992e50aa6c490bc4d68ee25b258d68'
HEAD='329b2ff35d2994b11abbb59f770d12da75c494ac'

def require(v,message):
 if not v:raise o.ContractError(message)

def basis(data):
 p,e,i,c,f,x,raw=(data[k] for k in ('physical','erratum','invoice','closure','funding','cold_correction','raw_cold'))
 require(p['head']==HEAD,'STALE_PHYSICAL_SOURCE')
 require(e['positive_universal_endpoint_gate_unchanged'] is True and e['actual_specialization_nonzero_claim_established'] is False and e['surjectivity_claim_established'] is False,'MISSING_SCOPE_CORRECTION')
 require(i['histograms']=={'paid':f['paid'],'productive':f['targets']} and i['totals']['productive']==10784,'UNEARNED_PRODUCTIVE_CREDIT')
 require(i['controller']['raw_owned_banks']==c['ordinary']['raw_local_owned_banks']==306,'STALE_274_BANK_CLOSURE')
 require(c['expanded_constants']['old_equal_N_implies_old_constants'] is False and c['tape_and_eventual_threshold']['old_C0_or_p0_reused'] is False,'OLD_PRECISION_REUSE')
 require(raw['capsule_manifest_sha256']==x['incorrect_recorded_value'] and x['correct_effective_value']==x['capsule_manifest_pre_sha256']==x['capsule_manifest_post_sha256'],'COLD_METADATA_CORRECTION_REQUIRED')

def run():
 require(o.digest((HERE/'oracle.py').read_bytes())==LIB_SHA,'LIBRARY_MODIFIED')
 folder=HERE/'case-v1';pb=(folder/'policy.json').read_bytes();require(o.digest(pb)==POLICY_SHA,'REVIEWER_POLICY_CHANGED')
 policy=o.decode(pb);candidate=o.decode((folder/'candidate.json').read_bytes())
 artifacts={p.name:p.read_bytes() for p in (folder/'artifacts').iterdir() if p.is_file()}
 # Check every byte, including offline supporting evidence not directly parsed
 # by the pure library's normalized envelope checker.
 for sha,raw in artifacts.items():require(o.digest(raw)==sha,'OFFLINE_ARTIFACT_CHANGED')
 deps=candidate['source_dependencies'];data={k:json.loads(artifacts[deps[k]]) for k in ('physical','erratum','invoice','closure','funding','cold_correction','raw_cold')}
 basis(data)
 result=o.evaluate(o.encode(candidate),artifacts,policy)
 require(result==o.decode((folder/'result.json').read_bytes()),'RESULT_CHANGED')
 require(result['label']=='FUNDED_CONDITIONAL' and result['funded_kappa']=='12109/4000000','EXPECTED_FUNDED_POINT')
 controls=[]
 def rejects(name,action):
  try:action()
  except (o.ContractError,KeyError) as exc:controls.append({'control':name,'status':'REJECTED','reason':str(exc)});return
  raise o.ContractError('CONTROL_ACCEPTED:'+name)
 for name,head in [('stale5383physical','4bd6efa51a495a7c7b7754915cf0244e7e60969e'),('stale5387physical','b1ab650d36f59e5be682a813145b7c67e219e341')]:
  d=copy.deepcopy(data);d['physical']['head']=head;rejects(name,lambda d=d:basis(d))
 d=copy.deepcopy(data);d['invoice']['histograms']['productive']['9']+=16;rejects('unearned16H9',lambda:basis(d))
 d=copy.deepcopy(data);d['closure']['ordinary']['raw_local_owned_banks']=274;rejects('old274bankclosure',lambda:basis(d))
 a=dict(artifacts);a.pop(deps['erratum']);rejects('missingmandatoryerratum',lambda:o.evaluate(o.encode(candidate),a,policy))
 d=copy.deepcopy(data);d['raw_cold']['capsule_manifest_sha256']=d['cold_correction']['correct_effective_value'];rejects('silentlyrewrittenrawcoldlabel',lambda:basis(d))
 a=dict(artifacts);a.pop(deps['cold_correction']);rejects('missingcoldcorrection',lambda:o.evaluate(o.encode(candidate),a,policy))
 c=copy.deepcopy(candidate);c['requested_label']='SELECTED';rejects('selectedpromotion',lambda:o.evaluate(o.encode(c),artifacts,policy))
 c=copy.deepcopy(candidate);c['model']['parameters']['power']=512;rejects('unsupportedcompilertuple',lambda:o.evaluate(o.encode(c),artifacts,policy))
 # Unknown-cost control deliberately rebinds in-memory test envelopes, so the
 # cost-state guard itself is exercised beyond the earlier payload hash guard.
 c=copy.deepcopy(candidate);p=copy.deepcopy(policy);a=dict(artifacts)
 c['planes']['precision_tape'][0].update(state='unknown',value_or_symbol=None)
 payload=o.digest(o.encode(o.scientific_payload(c)));p['scientific_payload_sha256']=payload
 for role in ('physical','census','closure','arithmetic'):
  r=o.decode(a[c['receipts'][role]]);r['scientific_payload_sha256']=payload
  if role=='arithmetic':r['invoice_receipt_sha256']=c['receipts']['census'];r['closure_receipt_sha256']=c['receipts']['closure']
  rb=o.encode(r);sha=o.digest(rb);a[sha]=rb;c['receipts'][role]=p['receipt_sha256'][role]=sha
 rejects('unknowncostfundedpromotion',lambda:o.evaluate(o.encode(c),a,p))
 return {'schema':'5392-oracle-case-verification/v1','label':result['label'],'funded_kappa':result['funded_kappa'],'library_sha256':LIB_SHA,'library_upstream_commit':'96f193143a7a2ff8a4e6b9d574d7f551d68a7da3','policy_sha256':POLICY_SHA,'policy_public_authority':False,'artifacts':len(artifacts),'controls':controls,'scientific_engine_execution':False}

if __name__=='__main__':print(json.dumps(run(),indent=2))
