from pathlib import Path
import json,subprocess,hashlib
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015')
for n in [2878, 2879, 2880, 2881, 2885, 2889, 2891, 2896, 2897, 2900, 2907, 2909, 2910, 2913, 2920]:
 d=P/'sources'/str(n);d.mkdir(parents=True,exist_ok=True);pk=json.loads((P/'packets'/f'{n}.json').read_text())
 for f in pk['files']:
  if f['source']:
   raw=subprocess.check_output(['git','cat-file','blob',f['source']['oid']],cwd=R);dst=d/f['path'];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
 packages=sorted({f['path'].split('/')[1] for f in pk['files']});print(n,packages)
 for name in packages:
  pkg=d/'research'/name
  if (pkg/'VERIFY.json').exists():print((pkg/'VERIFY.json').read_text())
