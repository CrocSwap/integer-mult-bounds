from pathlib import Path
import json, subprocess, hashlib
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015')
def blob(commit,path):
 v=subprocess.run(['git','show',commit+':'+path],cwd=R,capture_output=True)
 return v.stdout if v.returncode==0 else None
def record(n,result):(P/f'provenance-{n}-references.json').write_text(json.dumps(result,indent=2)+'\n')
# An author replay receipt is retained as author evidence, not a maintainer execution.
d=P/'sources/2880/research/encoded-bank-criterion-audit';s=json.loads((d/'SOURCE-REPLAY.json').read_text());rows=[]
for path,sha in s['files'].items():
 raw=blob(s['audited_commit'],'research/encoded-phase-bank/'+path)
 assert raw is not None and hashlib.sha256(raw).hexdigest()==sha,path
 oid=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert oid==s['git_blobs'][path]
 rows.append(dict(path=path,sha256=sha,git_blob=oid))
record(2880,dict(status='PASS',commit=s['audited_commit'],files=rows,scope='All thirteen source-replay inventory files match the original Git objects. Parent execution receipt is author evidence, not a new maintainer replay. New audit suite executed separately.'))
# Exact vendored predecessor receipt, not merely agreement with author-provided hash.
d=P/'sources/2909/research/p104-endpoint-saturation';s=json.loads((d/'SOURCES.json').read_text())['predecessor'];raw=blob(s['commit'],s['path']);assert raw==(d/s['snapshot']).read_bytes() and hashlib.sha256(raw).hexdigest()==s['sha256'];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==s['git_blob'];record(2909,dict(status='PASS',source=s,scope='Vendored predecessor RESULT exactly matches original commit/path/blob/SHA. New geometry independently reconstructed in candidate.'))
# Source claim under discussion; do not execute that source.
d=P/'sources/2881/research/scale-dependent-seed-moment-audit';records=json.loads((d/'SOURCES.json').read_text())['external_reviewed_sources'];checks=[]
for s in records:
 raw=blob(s['commit'],s['path'])
 if raw is None:
  raw=subprocess.check_output(['gh','api','-H','Accept: application/vnd.github.raw+json',f"repos/{s['repository']}/contents/{s['path']}?ref={s['commit']}"])
 assert hashlib.sha256(raw).hexdigest()==s['sha256'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==s['git_blob']
 out=P/'reference-2881'/Path(s['path']).name;out.parent.mkdir(exist_ok=True);out.write_bytes(raw);checks.append(s)
record(2881,dict(status='PASS',sources=checks,scope='Reference claim text authenticated to exact original Git bytes, without executing it. New counterexample replay separate.'))
print('PASS original reference source bindings for2880,2881,2909')
