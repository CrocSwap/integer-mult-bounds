"""Bind unchanged exact phase evidence, or regenerate all selected phase pairs."""
import gzip,hashlib,json,os,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent.parent;O=Path('split-centres')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.load(gzip.open(O/'CANONICAL-WORD.json.gz'))
r=json.loads((P/'inputs/complex-phase-receipt.json').read_text())
raw=gzip.decompress((P/'inputs/complex-phase-recipes.json.gz').read_bytes());recipes=json.loads(raw)
# Bind the canonical payload to the original frozen envelope. Python 3.11/3.12
# and 3.14 emit different gzip OS bytes for identical contents.
reference=P/'inputs/complex-canonical-reference.json.gz'
assert sha(reference)==r['canonical_word_sha256']
assert gzip.decompress((O/'CANONICAL-WORD.json.gz').read_bytes())==gzip.decompress(reference.read_bytes())
r['frozen_canonical_envelope_sha256']=r['canonical_word_sha256']
r['canonical_word_sha256']=sha(O/'CANONICAL-WORD.json.gz')
r['canonical_payload_sha256']=hashlib.sha256(gzip.decompress(reference.read_bytes())).hexdigest()
assert hashlib.sha256(raw).hexdigest()==r['recipe_sha256']
edges=set(map(tuple,c['edges']))|{(a,b) for f in c['center_frames'] for a,b in ((f,0),(0,f))}
assert {(z['old'],z['new']) for z in recipes['children']}==edges
assert len(recipes['children'])==len(edges) and len(recipes['endpoint_adapters'])==240
for z in recipes['children']:assert z['rank']==abs(len(c['frames'][z['old']])-len(c['frames'][z['new']]))
if os.environ.get('E8_REPLAY_PHASES')=='1':
 subprocess.run([sys.executable,'-B',str(P/'code/complex_phases_full.py')],check=True)
 assert (O/'CLIFFORD-RECIPES.json').read_bytes()==raw
else:
 (O/'CLIFFORD-RECIPES.json').write_bytes(raw)
 r['validation_mode']='Reuse exact phase evidence bound to the unchanged canonical word and recipe hashes'
 (O/'CLIFFORD-REVIEW.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS source-bound phase recipes',len(edges))
