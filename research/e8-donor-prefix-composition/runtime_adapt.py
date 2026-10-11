"""Two exact byte adapters: target-specific omission control and actual-response bank contract.
All other native source bytes, including the bank source CRLF, are preserved.
Prepared with OpenAI Codex assistance; inherited Apache-2.0 notices apply.
"""
from pathlib import Path
from hashlib import sha256
import json
if not __debug__:raise RuntimeError('Assertions required')
ADAPTERS=[{'output': 'local_admit.py', 'output_sha256': '8b6808b58c4041bc7701d79ec99eed6fc9d6d8c83f5f62bbbdc8f45f53eff4f9', 'replacements': [['t==124 and s==563', 't==171 and s==563']], 'source': 'pr416/local/local_admit.py', 'source_sha256': '55e56591261f5bb23e0badc78376ff55ca427a658859fe4bd661f46855c6cba3'}, {'output': 'banks.py', 'output_sha256': 'e0a0e7645c5a6d7be1836b6b913af85a7209617d76cc13b86c85338f0bd7aac7', 'replacements': [["assert lr['raw_operator_equals_same_entrance_nonY_baseline']", "assert not lr['raw_operator_equals_same_entrance_nonY_baseline'];assert lr['raw_operator_matches_protected_blocks'] and lr['actual_nongauged_dirty_response_recomputed'] and lr['helper_cleanup_subword_equal']\nassert sha(LOCALRESULT.parent/'RECOMPUTED-K.json')==lr['recomputed_response_sha256'];assert len(read(LOCALRESULT.parent/'RECOMPUTED-K.json'))==lr['recomputed_response_entries']\nassert read(LOCALRESULT.parent/'COEFFICIENT-WORDS.json')['status']=='PASS_LITERAL_COEFFICIENT_WORDS'"]], 'source': 'pr409/e8-response-bank64/banks.py', 'source_sha256': '34864524dfbf7413051dd830e7ff3c083d7ff1c6a164062b9eff17e7a05be347'}]
def prepare(source411,source409,out):
 source411,source409,out=map(Path,(source411,source409,out));assert not out.exists();out.mkdir()
 paths=[source411/'local/local_admit.py',source409.parent/'e8-response-bank64/banks.py'];results=[]
 for row,path in zip(ADAPTERS,paths):
  raw=path.read_bytes();assert sha256(raw).hexdigest()==row['source_sha256'];result=raw
  for old,new in row['replacements']:
   old,new=old.encode(),new.encode();assert result.count(old)==1;result=result.replace(old,new)
  assert sha256(result).hexdigest()==row['output_sha256'];p=out/row['output'];p.write_bytes(result);results.append(p)
 (out/'ADAPTATIONS.json').write_text(json.dumps(ADAPTERS,sort_keys=True,indent=2)+'\n')
 return tuple(results)

def check(base,derived,native):
 import prefix_source
 base,derived,native=map(Path,(base,derived,native));wanted=prefix_source.inventory(base);raw=(native/'local_admit.py').read_bytes();assert sha256(raw).hexdigest()==ADAPTERS[0]['source_sha256'];wanted['local/local_admit.py']=sha256(raw).hexdigest()
 assert prefix_source.inventory(derived)==wanted
 return dict(status='PASS_EXACT_SINGLE_LOCAL_CHECKER416_OVERLAY',derived_inventory_sha256=sha256(json.dumps(wanted,sort_keys=True,separators=(',',':')).encode()).hexdigest(),changed_leaf='local/local_admit.py',changed_leaf_sha256=sha256(raw).hexdigest())
def overlay(base,native,out):
 import shutil,prefix_source
 base,native,out=map(Path,(base,native,out));assert not out.exists()and not out.resolve().is_relative_to(base.resolve());before=prefix_source.inventory(base);shutil.copytree(base,out);(out/'local/local_admit.py').write_bytes((native/'local_admit.py').read_bytes());check(base,out,native);assert prefix_source.inventory(base)==before;return out
