"""Bind four freshly rebuilt, proof-content-pinned providers to a literal plan.
Prepared with OpenAI Codex assistance; Apache-2.0. No choices are optimized here.
"""
from pathlib import Path
import argparse,copy,hashlib,json,shutil
from collections import Counter
from generated_identity import artifact_identities
assert __debug__, 'Assertions required'
P=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser(description=__doc__)
for name in ('parent','four','prefix','out'):ap.add_argument('--'+name,type=Path,required=True)
a=ap.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
contracts=read(P/'CONTRACTS.json');expected=read(P/'EXPECTED.json')
assert sha(P/'CONTRACTS.json')==expected['contracts_sha256']
assert read(a.parent/'RECEIPT.json')['source_manifest_sha256']==expected['parent_manifest_sha256']
assert read(a.parent/'RESULT.json')['kappa_decimal']=='0.001600535778621932'
plan=read(P/'data/PLAN.json')
assert Counter(c['provider']for c in plan['provider_calls'])==expected['provider_counts']
dirs={'plain_four':a.four,'plain_eight':a.parent/'baseline568/eight-cold-local',
      'width7_eight':a.parent/'width7-local','prefix_width7_eight':a.prefix}
assert set(dirs)==set(plan['provider_registry'])==set(contracts)
base=a.out/'base';shutil.copytree(a.parent/'baseline568/baseline558/complex-global/base',base)
bound={}
for pid,directory in dirs.items():
 target=base/'providers'/pid;shutil.copytree(directory,target)
 identities=artifact_identities(target)
 assert identities==contracts[pid]['semantic_artifact_sha256']
 d=plan['provider_registry'][pid]
 assert d['widths']==contracts[pid]['widths'] and d['actual_paid_profile']==contracts[pid]['paid_profile']
 assert d['orientation_program_sha256']==contracts[pid]['program_hashes']
 d['directory']='providers/'+pid;d['artifact_sha256']={n:sha(target/n)for n in identities};d['artifact_semantic_sha256']=identities
 bound[pid]=dict(raw=d['artifact_sha256'],semantic=identities)
plan['runtime_source_plan_sha256']=sha(P/'data/PLAN.json')
(a.out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
receipt=dict(status='PASS_FROZEN_FOUR_PROVIDER_FRESH_BINDING',source_plan_sha256=plan['runtime_source_plan_sha256'],runtime_plan_sha256=sha(a.out/'PLAN.json'),contracts_sha256=sha(P/'CONTRACTS.json'),parent_receipt_sha256=sha(a.parent/'RECEIPT.json'),providers=bound,scope='Every proof-relevant generated identity and every literal artifact reference is checked before binding. No owner, width, dispatch or scalar choice changes.')
(a.out/'BINDING.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
