"""Authenticate PR2872 references/provenance against original Git objects."""
import pathlib,json,subprocess,hashlib
P=pathlib.Path('/tmp/pr-efficient1800');R='/tmp/integer-mult-efficient1100-20261015';D=P/'sources/2872/research/encoded-phase-bank';rows=[]
for ref in json.loads((D/'REFERENCES.json').read_text()):
 raw=subprocess.check_output(['git','show',ref['commit']+':'+ref['source_path']],cwd=R)
 assert raw==(D/ref['local_path']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==ref['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==ref['git_blob']
 rows.append(ref)
s=json.loads((D/'SOURCES.json').read_text())
for ref in s['files']:
 raw=subprocess.check_output(['git','show',s['base_commit']+':'+ref['path']],cwd=R)
 assert hashlib.sha256(raw).hexdigest()==ref['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==ref['git_blob']
 rows.append(dict(ref,commit=s['base_commit']))
(P/'provenance-2872.json').write_text(json.dumps(dict(bindings=rows,scope='Two original reference README files and two provenance-only base files authenticated. No predecessor code executed or broader predecessor theorem admitted.'),indent=2)+'\n')
print('PASS_ENCODED_PROVENANCE original_git_bindings=4')
