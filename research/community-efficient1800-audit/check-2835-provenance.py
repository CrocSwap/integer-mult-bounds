"""Authenticate every exported runtime/oracle/proof file against original Git."""
from pathlib import Path
import hashlib,json,subprocess,sys
pkg,repo=map(Path,sys.argv[1:])
entries=json.loads((pkg/'INPUTS.json').read_text())['files']
for f in entries:
 spec=f['source_head']+':'+f['source_path']
 raw=subprocess.check_output(['git','show',spec],cwd=repo)
 if raw!=(pkg/f['path']).read_bytes() or hashlib.sha256(raw).hexdigest()!=f['sha256']:
  raise ValueError('Original source byte mismatch: '+spec)
 if subprocess.check_output(['git','rev-parse',spec],cwd=repo,text=True).strip()!=f['git_blob']:
  raise ValueError('Original Git blob mismatch: '+spec)
print(json.dumps(dict(status='PASS',exports=len(entries),scope='Byte-exact original runtime, oracle and proof sources; no mathematical claim from hashes alone.')))
