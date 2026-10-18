import json
from pathlib import Path
old=json.loads(Path('/tmp/pr-efficient1700/prior-revisions/2731-original/RESULT.json').read_text())
new=json.loads(Path('research/selected-residual-live-volume/RESULT.json').read_text())
assert old['authenticated_repository_inputs']==1 and new['authenticated_repository_inputs']==0
for key in ['generation','manifest_sha256','checker_sha256','authenticated_repository_inputs']:
 old.pop(key,None);new.pop(key,None)
assert old==new
assert not Path('certificates/selected-result.json').exists()
print('PASS exact mathematical receipt unchanged, old selected record absent; only provenance/self-hashes/input count differ')
