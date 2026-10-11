"""Exact native PR422 replica64 configuration over a copied PR409 runtime.
The source program is unchanged. All five restored PR409 trees stay immutable.
Prepared with OpenAI Codex assistance; inherited Apache-2.0 notices apply.
"""
from pathlib import Path
from hashlib import sha256
import json,shutil
if not __debug__:raise RuntimeError('Assertions required')
sha=lambda p:sha256(Path(p).read_bytes()).hexdigest()
def inventory(root):
 root=Path(root);assert root.is_dir()and not root.is_symlink();assert not any(p.is_symlink()for p in root.rglob('*'))
 return {p.relative_to(root).as_posix():sha(p)for p in root.rglob('*')if p.is_file()}
def check(source,derived,config422):
 source,derived,config422=map(Path,(source,derived,config422));wanted=inventory(source);original=source/'e8-sequential-gauges/CONFIG.json';assert sha(original)=='5d75d1c5bb382a7bf2db9a0800871838913e50d7985206de1e44f3257ae1edab'
 raw=original.read_bytes();new=config422.read_bytes();assert sha256(new).hexdigest()=='f69efcfda73a331c7924da50da3ca0b1cc011a3a092cb214e0b148f1c303a80c';wanted['e8-sequential-gauges/CONFIG.json']=sha256(new).hexdigest()
 assert inventory(derived)==wanted
 a=json.loads(raw);b=json.loads(new);assert a['replicas']==32 and b['replicas']==64 and a['deficit_per_replica']==b['deficit_per_replica']==312
 assert {k for k in a if a[k]!=b[k]}=={'replicas','expected_kappa','benchmark_kappa'}
 return dict(status='PASS_EXACT_REPLICA64_CONFIGURATION_ONLY_COPY',original_configuration_sha256=sha256(raw).hexdigest(),derived_configuration_sha256=sha256(new).hexdigest(),derived_inventory_sha256=sha256(json.dumps(wanted,sort_keys=True,separators=(',',':')).encode()).hexdigest(),changed_data_fields={k:[a[k],b[k]]for k in a if a[k]!=b[k]},all_native_program_bytes_unchanged=True,scope='Only replicas and deficit_per_replica feed the retained expansion/bank/audit/bridge code. Native PR422 expected/benchmark score fields remain original source provenance and are not a claim for this candidate. The final profile is freshly repriced.')
def prepare(source,out,config422):
 source,out,config422=map(Path,(source,out,config422));assert not out.exists()and not out.resolve().is_relative_to(source.resolve());before=inventory(source);shutil.copytree(source,out);p=out/'e8-sequential-gauges/CONFIG.json';p.write_bytes(config422.read_bytes());receipt=check(source,out,config422);assert inventory(source)==before;return out/'e8-sequential-gauges',receipt
