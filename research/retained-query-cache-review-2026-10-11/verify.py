"""Byte-bound scoped collaboration witnesses; no global supplier claim."""
from pathlib import Path
from hashlib import sha256
import json, shutil, subprocess, sys
P=Path(__file__).resolve().parent
if not __debug__:raise SystemExit('Assertions required')
manifest=json.loads((P/'SOURCE-MANIFEST.json').read_text())
for name,h in manifest['files'].items():assert sha256((P/name).read_bytes()).hexdigest()==h,name
review=json.loads((P/'FACTUAL-REVIEW.json').read_text())
assert review['status']=='PASS_INDEPENDENT_SOURCE_BOUND_SCOPED_CASCADE_COLLABORATION_REVIEW'
assert sha256((P/'sources/MANIFEST.json').read_bytes()).hexdigest()==review['manifest_sha256']
D=P/'derived'
if D.exists():shutil.rmtree(D)
shutil.copytree(P/'sources',D)
subprocess.run([sys.executable,'-B',str(D/'verify.py')],check=True)
result={'status':'PASS_SOURCE_CLOSED_SCOPED_RETAINED_QUERY_CACHE_REVIEW','bound_files':len(manifest['files']),'scope':'Public-source integrity and tiny dirty query/cache algebra only; no global admission or improved score.'}
(D/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps(result))
