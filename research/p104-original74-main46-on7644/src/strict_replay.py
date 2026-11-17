# SPDX-License-Identifier: Apache-2.0
"""Paired #7644 exact dirty-row and private-observation replay using its pinned engine.
Credit ToikY #7644 and authors in retained NOTICE; DreamingOfClouds #7611.
"""
import gzip,importlib.util,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('source7644_independent',D/'source7644/independent.py'); module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
a=json.loads(gzip.decompress((D/'source7644/data/word.json.gz').read_bytes()));b=json.loads(gzip.decompress((D/'candidate.json.gz').read_bytes())); n=a['public'];removed={43543,43544,45387,45388,45390,47973}; insert={43543:1,45392:2,47973:1}; j=24; aligned={}
for i,e in enumerate(a['program']):
 j+=insert.get(i,0)
 if i not in removed:
  assert b['program'][j]==e
  aligned[i]=j;j+=1
assert j==len(b['program'])
def operands(e):return e[1:3] if e[0] in ('ADD','COPY') else e[1:2]
watch={i:k for i,k in aligned.items() if max(operands(a['program'][i]))>=n or a['program'][i][0]=='COPY'}
x=module.replay(a,set(watch));y=module.replay(b,set(watch.values()))
for key in ('rows','erased','lifetime','peak','rises','owned_events','copies','targets'):
 assert x[key]==y[key],key
assert len(x['erased'])==len(y['erased'])==74
assert not x['bad_helpers'] and not y['bad_helpers']
for i,j in watch.items():assert x['readings'][i]==y['readings'][j],f'observation {i}/{j}'
result={'status':'PASS_PAIRED_EXACT_STRICT74','source_sha256':hashlib.sha256(gzip.decompress((D/'source7644/data/word.json.gz').read_bytes())).hexdigest(),'candidate_sha256':hashlib.sha256(gzip.decompress((D/'candidate.json.gz').read_bytes())).hexdigest(),'public_input_columns':n,'private_observation_events':len(watch),'ordered_clears':len(x['erased']),'copies':len(x['copies']),'paid_source':dict(x['paid']),'paid_candidate':dict(y['paid']),'grid_source':x['grid'],'grid_candidate':y['grid'],'mass_source':x['mass'],'mass_candidate':y['mass']}
(D/'STRICT-REPLAY.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result))
