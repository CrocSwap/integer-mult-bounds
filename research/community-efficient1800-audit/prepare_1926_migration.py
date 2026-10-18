from pathlib import Path
import json,hashlib,subprocess,shutil
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-1926';assert not D.exists();D.mkdir();pkg='research/unittest-receipt-comparison';H=D/pkg;H.mkdir(parents=True);pk=json.loads((P/'packets/1926.json').read_text());original={}
for row in pk['files']:
 rel=row['path'];raw=subprocess.check_output(['git','cat-file','blob',row['source']['oid']],cwd=R);f=D/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw);original[Path(rel).name]=hashlib.sha256(raw).hexdigest()
(H/'historical').mkdir()
for name in ['README.md','SOURCES.json','VERIFY.json']:shutil.copy2(H/name,H/'historical'/name)
s=json.loads((H/'SOURCES.json').read_text());archive='scripts/historical-ci-inputs/ledger-batch932-run_isolated_tests.py';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();inputs={}
for row in s['files']:
 if row['usage']!='input':continue
 rel=row['path'];physical=archive if rel=='scripts/run_isolated_tests.py' else rel;raw=subprocess.check_output(['git','show',head+':'+physical],cwd=R);assert hashlib.sha256(raw).hexdigest()==row['sha256'];target=D/physical;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);inputs[rel]={'physical':physical,'sha256':row['sha256']}
 if physical!=rel:
  row['path']=physical;row['pin']='head:'+head+':'+physical;row['git_blob']=subprocess.check_output(['git','rev-parse',head+':'+physical],cwd=R,text=True).strip()
(H/'SOURCES.json').write_text(json.dumps(s,indent=2)+'\n');v=json.loads((H/'VERIFY.json').read_text());v['inputs']=[archive if x=='scripts/run_isolated_tests.py' else x for x in v['inputs']]
for i,cmd in enumerate(v['commands']):
 cmd['argv']=['{python}','-B',*( ['-O'] if i else []),'{package}/historical_replay.py',*(['--optimized'] if i else [])];cmd['timeout_seconds']=150;cmd['checks']='Authenticate original package and all three historical runtime inputs; run unchanged full 20-test receipt under '+('optimized' if i else 'normal')+' Python in a private immutable context; current runner untouched.'
v['commands'].append(dict(argv=['{python}','-I','-O','-B','{package}/test_historical_replay.py'],timeout_seconds=60,checks='Every original-file/input mutation rejects, missing input rejects, failed or silent-zero-exit child rejects, and post-replay mutation rejects.'))
(H/'VERIFY.json').write_text(json.dumps(v,indent=2)+'\n');(P/'1926-original-pins.json').write_text(json.dumps(original,indent=2)+'\n');(P/'1926-input-map.json').write_text(json.dumps(inputs,indent=2)+'\n')
print('Prepared original package and exact archived runner context')
