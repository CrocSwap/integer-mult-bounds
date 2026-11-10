#!/usr/bin/env python3
"""Cold construction from the two frozen predecessor words; standard library."""
from pathlib import Path
import gzip,hashlib,json,subprocess,sys,shutil,tempfile
HERE=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Run without -O; assertions are proof checks.')
sources=json.loads((HERE/'NATIVE-INPUTS.json').read_text())
for item in sources['sources']:
 assert hashlib.sha256((HERE/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
commands=[['compose.py'],['build_wire.py'],['split_build.py','build/extra_wire_0.json.gz','42531','660','759','split759'],['split_build.py','build/split759.json.gz','37192','595','450','split759_450']]
with tempfile.TemporaryDirectory(prefix='shared-wire-reconstruction-') as temporary:
 work=Path(temporary)
 shutil.copytree(HERE/'data',work/'data')
 (work/'build').mkdir()
 for name in ('compose.py','build_wire.py','split_build.py'):
  shutil.copyfile(HERE/name,work/name)
 for command in commands:
  subprocess.run([sys.executable,'-B',str(work/command[0]),*command[1:]],cwd=work,check=True)
 actual=json.load(gzip.open(work/'build/split759_450.json.gz'))
 for name in ('split759.proof.json','split759_450.proof.json'):
  assert json.loads((work/'build'/name).read_text())==json.loads((HERE/'data'/name).read_text())
 review=HERE/'independent_construction.py'
 subprocess.run([sys.executable,'-I','-B',str(review),'--package-root',str(HERE),'--build-dir',str(work/'build')],check=True)
expected=json.load(gzip.open(HERE/'data/final.json.gz'))
assert actual==expected
canonical=hashlib.sha256(json.dumps(actual,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert canonical==sources['final_canonical_json_sha256']
print('PASS_RECONSTRUCTION',canonical)
