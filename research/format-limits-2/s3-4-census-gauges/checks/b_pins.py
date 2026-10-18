"""Cross-pins of bundle B: the rebuilt (derived) words against the hashes their PRs publish.  (The vendored files themselves are checked
by scripts/provenance.py, step 0 of verify.sh.)"""
import json, os
from common import *
S = json.load(open(os.path.join(ROOT, '..', 'SOURCES.json')))
PFX = os.path.basename(ROOT) + '/'
D = {e['file'][len(PFX):]: e for e in S['derived'] if e['file'].startswith(PFX)}
plan = load_json('pr656', 'PLAN.json.gz'); g = plan['provider_registry']['gauge44']
d = D['inputs/derived/g44-CANONICAL-WORD.json.gz']
check('B.0 pin: #656 PLAN.json gauge44 CANONICAL-WORD bytes', g['artifact_sha256']['CANONICAL-WORD.json.gz'] == d['sha256'])
check('B.0 pin: #656 PLAN.json gauge44 CANONICAL-WORD content', g['artifact_semantic_sha256']['CANONICAL-WORD.json.gz'] == d['content_sha256'])
gi = load_json('pr626', 'GENERATED-IDENTITY-CONTROLS.json')['source_providers']['ck']
d = D['inputs/derived/ck-CANONICAL-WORD.json.gz']
check('B.0 pin: #626 identity controls ck CANONICAL-WORD bytes', gi['raw']['CANONICAL-WORD.json.gz'] == d['sha256'])
check('B.0 pin: #626 identity controls ck CANONICAL-WORD content', gi['semantic']['CANONICAL-WORD.json.gz'] == d['content_sha256'])
finish()
