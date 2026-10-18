from pathlib import Path
import json,subprocess,hashlib
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015')
for n in [2874,2877,2882,2888,2902,2905,2907,2912,2916]:
 d=P/'sources'/str(n);d.mkdir(parents=True,exist_ok=True);pk=json.loads((P/'packets'/f'{n}.json').read_text())
 for f in pk['files']:
  if f['source']:
   raw=subprocess.check_output(['git','cat-file','blob',f['source']['oid']],cwd=R);dst=d/f['path'];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
 packages=sorted({f['path'].split('/')[1] for f in pk['files']});print(n,packages)
 for name in packages:
  pkg=d/'research'/name
  if (pkg/'VERIFY.json').exists():print((pkg/'VERIFY.json').read_text())
