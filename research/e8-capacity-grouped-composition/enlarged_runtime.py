"""Exact native423 local-checker overlay with frame-baseline controls.
Only the copied runtime's local/local_admit.py changes. Original parent bytes
remain immutable and its retained native manifest is provenance only.
Prepared with OpenAI Codex assistance; inherited Apache-2.0 notices apply.
"""
from pathlib import Path
from hashlib import sha256
import json,shutil
if not __debug__:raise RuntimeError('Assertions required')
PARENT_LOCAL='55e56591261f5bb23e0badc78376ff55ca427a658859fe4bd661f46855c6cba3'
NATIVE_LOCAL='d478992ff811a3462889e1851f3b7321c98411ea32856293c44dcc9dff6c4cbb'
BANK_SOURCE='34864524dfbf7413051dd830e7ff3c083d7ff1c6a164062b9eff17e7a05be347'
BANK_ADAPTED='e0a0e7645c5a6d7be1836b6b913af85a7209617d76cc13b86c85338f0bd7aac7'
sha=lambda p:sha256(Path(p).read_bytes()).hexdigest()
def inventory(root):
 root=Path(root);assert root.is_dir()and not root.is_symlink();assert not any(p.is_symlink()for p in root.rglob('*'))
 return {p.relative_to(root).as_posix():sha(p)for p in root.rglob('*')if p.is_file()}
def check(source,derived,native):
 source,derived,native=map(Path,(source,derived,native));wanted=inventory(source)
 assert wanted['local/local_admit.py']==PARENT_LOCAL and sha(native/'local_admit.py')==NATIVE_LOCAL
 wanted['local/local_admit.py']=NATIVE_LOCAL;assert inventory(derived)==wanted
 return dict(status='PASS_EXACT_SINGLE_LOCAL_CHECKER423_OVERLAY',derived_inventory_sha256=sha256(json.dumps(wanted,sort_keys=True,separators=(',',':')).encode()).hexdigest(),changed_leaf='local/local_admit.py',changed_leaf_sha256=NATIVE_LOCAL,scope='Full derived inventory verified explicitly. The unchanged copied410 manifest is provenance, not an attestation for this derived runtime. Native423 adds actual A/B frame-reversion controls using the freshly reconstructed215 frame baseline; all compiler and phase dependency bytes remain unchanged.')
def overlay(source,native,out):
 source,native,out=map(Path,(source,native,out));assert not out.exists()and not out.resolve().is_relative_to(source.resolve());before=inventory(source);assert sha(native/'local_admit.py')==NATIVE_LOCAL
 shutil.copytree(source,out);(out/'local/local_admit.py').write_bytes((native/'local_admit.py').read_bytes());check(source,out,native);assert inventory(source)==before;return out

def prepare(source,source409,out):
 source,source409,out=map(Path,(source,source409,out));assert not out.exists();out.mkdir()
 paths=[source/'local/local_admit.py',source409.parent/'e8-response-bank64/banks.py']
 old="assert lr['raw_operator_equals_same_entrance_nonY_baseline']"
 new="assert not lr['raw_operator_equals_same_entrance_nonY_baseline'];assert lr['raw_operator_matches_protected_blocks'] and lr['actual_nongauged_dirty_response_recomputed'] and lr['helper_cleanup_subword_equal']\nassert sha(LOCALRESULT.parent/'RECOMPUTED-K.json')==lr['recomputed_response_sha256'];assert len(read(LOCALRESULT.parent/'RECOMPUTED-K.json'))==lr['recomputed_response_entries']\nassert read(LOCALRESULT.parent/'COEFFICIENT-WORDS.json')['status']=='PASS_LITERAL_COEFFICIENT_WORDS'"
 records=[];outputs=[]
 for path,want,name,pairs in zip(paths,[NATIVE_LOCAL,BANK_SOURCE],['local_admit.py','banks.py'],[[('t==124 and s==563','t==171 and s==563')],[(old,new)]]):
  raw=path.read_bytes();assert sha256(raw).hexdigest()==want;changed=raw
  for a,b in pairs:
   assert changed.count(a.encode())==1;changed=changed.replace(a.encode(),b.encode())
  got=sha256(changed).hexdigest()
  assert got==(BANK_ADAPTED if name=='banks.py'else'2be71266a647917b21e0ff742ab0451fbbe1a471686824ebb935c3e93551e200')
  output=out/name;output.write_bytes(changed);outputs.append(output)
  records.append(dict(source='pr423/local/local_admit.py'if name=='local_admit.py'else'pr409/e8-response-bank64/banks.py',source_sha256=want,output=name,output_sha256=got,replacements=pairs))
 (out/'ADAPTATIONS.json').write_text(json.dumps(records,sort_keys=True,indent=2)+'\n');return tuple(outputs)
