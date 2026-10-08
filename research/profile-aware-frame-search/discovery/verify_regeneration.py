"""Compare independently regenerated complete literal words byte for byte."""
from pathlib import Path
import gzip,hashlib,json
from run_strategy import HERE
receipt=dict(status='PASS exact selected-word regeneration',frozen_source_pin='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',axes=[],scope='immutable saved runner plus pinned warm matching/oracle inputs; byte-identical executable words, no optimality implication')
for h in (23,25):
 selected=HERE/'profile_cost4_exchange'/f'h{h}'/'word.json.gz'
 regenerated=HERE/'profile_cost4_repro_exchange'/f'h{h}'/'word.json.gz'
 a=gzip.decompress(selected.read_bytes());b=gzip.decompress(regenerated.read_bytes())
 assert a==b,('literal word mismatch',h)
 assert selected.read_bytes()==regenerated.read_bytes(),('deterministic gzip mismatch',h)
 old=json.loads(selected.with_name('compiled.json').read_text());new=json.loads(regenerated.with_name('compiled.json').read_text())
 assert old['word_sha256']==new['word_sha256']==hashlib.sha256(a).hexdigest()
 assert old['experiment_runner_sha256']==new['experiment_runner_sha256']=='2d545544e429a83aea08c1d6b344dff149b1bfc75fcd9685c148bb01934f61f5'
 assert old['local_profile_oracle_sha256']==new['local_profile_oracle_sha256']
 receipt['axes'].append(dict(h=h,literal_word_sha256=hashlib.sha256(a).hexdigest(),gzip_sha256=hashlib.sha256(selected.read_bytes()).hexdigest(),selected=str(selected.relative_to(HERE)),regenerated=str(regenerated.relative_to(HERE)),runner_sha256=new['experiment_runner_sha256'],oracle_sha256=new['local_profile_oracle_sha256']))
(HERE/'selected4-regeneration-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
