from pathlib import Path
import json,hashlib,subprocess,time,platform,ast
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'sources/1518';py='/tmp/pr-efficient200-venv/bin/python'
sha=lambda b:hashlib.sha256(b).hexdigest()
def blob(path):return subprocess.check_output(['git','show','HEAD:'+path],cwd=R)
prior='research/community-efficient600-audit/checks/check-1518'
raw=blob(prior+'.json');old=json.loads(raw);log=blob(prior+'.log')
assert old['status']=='passed' and old['exit_codes']==[0] and old['head']=='0c6a58aaf22e0fc1b34497f8f6f80db6212b4621'
assert sha(log)==old['log_sha256'] and b'PASS_ATOMIC_TRIO_CONNECTOR' in log
code='research/atomic-trio-connector/verify.py';data=(D/code).read_bytes()
assert sha(data)==old['input_sha256'][code]
tree=ast.parse(data)
assert all(n.module in ('collections','itertools') for n in ast.walk(tree) if isinstance(n,ast.ImportFrom))
assert not any(isinstance(n,ast.Import) for n in ast.walk(tree))
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('open','eval','exec','__import__') for n in ast.walk(tree))
packet=json.loads((P/'packets/1518.json').read_text())
for f in packet['files']:
 b=subprocess.check_output(['git','cat-file','blob',f['source']['oid']],cwd=R)
 assert sha(b)==old['input_sha256'][f['path']],f['path']
start=time.monotonic();commands=[]
inputs={f.relative_to(D).as_posix():sha(f.read_bytes()) for f in (D/'research/atomic-trio-connector').iterdir() if f.is_file()}
with (P/'check-1518.log').open('wb') as out:
 out.write(('REUSED_SOURCE_BOUND_CENSUS '+prior+' receipt_sha256='+sha(raw)+' log_sha256='+sha(log)+'\n').encode());out.flush()
 for flags in [[],['-O']]:
  cmd=[py,*flags,'-B','research/atomic-trio-connector/parity.py'];t=time.monotonic()
  proc=subprocess.run(cmd,cwd=D,stdout=out,stderr=subprocess.STDOUT,timeout=60)
  commands.append(dict(argv=cmd,exit_code=proc.returncode,seconds=time.monotonic()-t))
  assert proc.returncode==0
 assert all(sha((D/f).read_bytes())==h for f,h in inputs.items())
r=dict(number=1518,head=old['head'],status='passed',seconds=time.monotonic()-start,commands=commands,input_sha256=inputs,changed_files_after={},log_sha256=sha((P/'check-1518.log').read_bytes()),environment=dict(python=subprocess.check_output([py,'--version'],text=True).strip(),platform=platform.platform()),reused=dict(receipt=prior+'.json',receipt_sha256=sha(raw),log=prior+'.log',log_sha256=sha(log),original_seconds=old['seconds'],scope='Unchanged standalone standard-library verifier, all original author package blobs match original receipt. Original complete census reused; no fresh census claim.'),scope='Complete affine-orbit parity certificate, normal and optimized, plus exact-head authenticated original 6048000-word census. Written parity reduction and tariff argument reviewed separately. No new kappa.')
(P/'check-1518.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['seconds'])
