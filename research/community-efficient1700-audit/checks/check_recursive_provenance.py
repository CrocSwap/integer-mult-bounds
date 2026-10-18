"""Authenticate the complete retained caller and proof exports against Git."""
from pathlib import Path
import hashlib,json,platform,subprocess,sys,time
P=Path('/tmp/pr-efficient1700');R=Path('/tmp/integer-mult-efficient1100-20261015');root=P/'sources/2753';pkg=root/'research/selected-bit-recursive-caller';start=time.monotonic();rows=[]
def bind(commit,path,local,rec):
 raw=subprocess.check_output(['git','show',commit+':'+path],cwd=R)
 if raw!=local.read_bytes():raise ValueError('Original bytes differ: '+path)
 if hashlib.sha256(raw).hexdigest()!=rec['sha256']:raise ValueError('SHA mismatch: '+path)
 if subprocess.check_output(['git','rev-parse',commit+':'+path],cwd=R,text=True).strip()!=rec['git_blob']:raise ValueError('Blob mismatch: '+path)
 rows.append(dict(commit=commit,path=path,local=str(local.relative_to(root)),sha256=rec['sha256']))
pred=json.loads((pkg/'PREDECESSOR.json').read_text())
for name,rec in pred['files'].items():bind(pred['head'],pred['path']+'/'+name,pkg/'predecessor'/name,rec)
for rec in json.loads((pkg/'EVIDENCE.json').read_text())['files']:bind(rec['commit'],rec['source_path'],pkg/rec['path'],rec)
src=json.loads((pkg/'SOURCES.json').read_text())
for rec in src['files']:
 if rec['usage']=='input':bind(src['base_commit'],rec['path'],root/rec['path'],rec)
if len(rows)!=65:raise ValueError('Expected50predecessor+4proof+11live')
log=P/'check-2753-supplement.log';log.write_text(json.dumps(dict(status='PASS',bindings=rows),sort_keys=True)+'\n')
d=dict(number=2753,head=json.loads((P/'2753.json').read_text())['headRefOid'],status='passed',seconds=time.monotonic()-start,commands=[dict(argv=[sys.executable,str(Path(__file__).resolve())],exit_code=0)],input_sha256={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),pkg/'PREDECESSOR.json',pkg/'EVIDENCE.json',pkg/'SOURCES.json']},log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),environment=dict(python=sys.version,platform=platform.platform()),scope='Original Git identity for all executable predecessor files, four proof/notice exports and all live inputs. Full declared replay and parametric proof review remain separate.')
(P/'check-2753-supplement.json').write_text(json.dumps(d,indent=2)+'\n');print('2753 PASS65originalGitbindings')
