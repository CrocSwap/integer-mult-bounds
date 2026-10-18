from pathlib import Path
import json,subprocess,hashlib,io,tarfile,importlib.metadata
p=Path('research/t74-native-fast');r=Path('/tmp/integer-mult-efficient1100-20261015');prov=json.loads((p/'SOURCE-PROVENANCE.json').read_text());cache={}
assert importlib.metadata.version('numpy')=='2.2.6'
for entry in prov['files']:
 o=entry['origin'];key=o['commit']+':'+o['path']
 if key not in cache:cache[key]=subprocess.check_output(['git','show',key],cwd=r)
 b=cache[key]
 if 'member' in o:
  assert hashlib.sha256(b).hexdigest()==o['archive_sha256']
  with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz') as t:b=t.extractfile(o['member']).read()
 assert b==(p/entry['local']).read_bytes(),entry['local']
ref=prov['reference_receipts'];b=subprocess.check_output(['git','show',ref['commit']+':'+ref['path']],cwd=r);assert hashlib.sha256(b).hexdigest()==ref['sha256']
ref=json.loads(b);expected=json.loads((p/'EXPECTED.json').read_text());pins=json.loads((p/'PINS.json').read_text())
for provider,e in expected.items():
 for name,sha in e['reference_files'].items():assert ref['cache_files'][pins[f'fixtures/WORD-{provider}.json.gz']+'/local/'+name]==sha,name
print('PASS20 original source/fixture copies; all22 reference artifact hashes match original PR2751 reuse pins; numpy==2.2.6')
