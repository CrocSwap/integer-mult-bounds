#!/usr/bin/env python3
"""Separately reviewed actual PR5392 oracle case; no mathematical engine replay.

Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
The exact published library and original producer proposal remain unchanged.
"""
from pathlib import Path
import argparse,json,tempfile,time
import verify as core
HERE=Path(__file__).resolve().parent;O=HERE/'oracle'
ORACLE_SHA256='19d82ea7e1b6ab6d5c420a8a2579487c0c90b842139b588547657958481ea921'
def inventory():
 core.need(core.sha(O/'ORACLE-PACKET.json')==ORACLE_SHA256,'immutable oracle subpacket')
 m=core.read(O/'ORACLE-PACKET.json');names=set()
 for row in m['files']:
  p=core.safe(O,row['path']);b=p.read_bytes();names.add(row['path']);core.need(len(b)==row['bytes'] and core.sha(p)==row['sha256'],'oracle source/artifact byte guard '+row['path'])
 core.need(names=={p.relative_to(O).as_posix() for p in O.rglob('*') if p.is_file() and p.name!='ORACLE-PACKET.json'},'complete oracle subpacket inventory')
 return len(names)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--integrity-only',action='store_true');args=ap.parse_args();start=time.monotonic();count=inventory()
 review=core.read(O/'ORACLE-POLICY-ACCEPTANCE.json');root=core.read(O/'ROOT-POLICY-REVIEW.json');case=O/'frozen/case-v1'
 core.need(review['decision']=='ACCEPT_EXACT_SOURCE_BOUND_CONDITIONAL_CASE' and root['decision']=='ACCEPT_EXACT_CONDITIONAL_CASE_FOR_REVIEW_PACKAGE','separate exact-case review authority')
 core.need(root['candidate_head']==review['candidate_head']==core.HEAD and root['independent_audit_receipt_sha256']==core.sha(O/'ORACLE-POLICY-ACCEPTANCE.json'),'root-independent review identity')
 core.need(root['policy_sha256']==review['policy_sha256']==core.sha(case/'policy.json') and review['candidate_sha256']==core.sha(case/'candidate.json') and review['result_sha256']==core.sha(case/'result.json'),'reviewed exact policy/candidate/result')
 core.need(root['library_sha256']==review['library_sha256']==core.sha(O/'frozen/oracle.py'),'exact unmodified library')
 core.need(not root['general_policy_authority_granted'] and not root['selected_transition_authorized'] and not review['public_review_authority_granted'],'no general/public/selected authority')
 core.need(review['artifact_hashes']==sorted(p.name for p in (case/'artifacts').iterdir() if p.is_file()),'reviewed39 artifact inventory')
 core.need(root['scope_erratum_required']==core.sha(core.D/'01-physical/SCOPE-ERRATUM-RECEIPT.json') and root['cold_metadata_correction_required']==core.sha(core.C/'BOUNDED-REGISTERED-RUN-CORRECTION.json'),'reviewed mandatory core corrections')
 proof=core.read(O/'LIBRARY-PROOF.json');core.raw_path(core.raw_objects(proof),proof['row'],O/'frozen/oracle.py')
 result=dict(status='PASS_REVIEWED_PR5392_ORACLE_INTEGRITY',oracle_packet_files=count,policy_sha256=root['policy_sha256'],library_sha256=root['library_sha256'],candidate_head=core.HEAD,conditional_framework_assumptions=5,review_decision=root['decision'],independent_review_receipt_sha256=core.sha(O/'ORACLE-POLICY-ACCEPTANCE.json'),root_review_receipt_sha256=core.sha(O/'ROOT-POLICY-REVIEW.json'),original_proposal_preserved=True,public_or_selected_authority=False,scientific_engine_execution=False)
 if not args.integrity_only:
  commands=[]
  with tempfile.TemporaryDirectory(prefix='pr5392-oracle-') as td:
   observed=json.loads(core.launch([HERE/'exec_frozen.py',O/'frozen/verify.py'],Path(td),commands,10))
  core.need(observed==core.read(O/'frozen/VERIFY-NORMAL.json')==core.read(O/'frozen/VERIFY-OPTIMIZED.json'),'complete actual-case result/control equality')
  core.need(observed['label']=='FUNDED_CONDITIONAL' and observed['funded_kappa']=='12109/4000000' and len(observed['controls'])==10,'reviewed actual case and all controls')
  result.update(status='PASS_REVIEWED_PR5392_ORACLE_CASE',actual_case=observed,commands=commands)
 inventory();result['seconds']=round(time.monotonic()-start,6);print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
