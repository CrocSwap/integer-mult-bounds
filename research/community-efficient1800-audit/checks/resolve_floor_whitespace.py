from pathlib import Path
import ast,hashlib,json,shutil,subprocess,tempfile,time
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');rel=Path('research/two-sided-ten-term-floor');base=P/'sources/2854'/rel
sha=lambda b:hashlib.sha256(b).hexdigest()
start=time.monotonic();old=(base/'checks/diag9.py').read_bytes();new=b'\n'.join(line.rstrip(b' \t') for line in old.split(b'\n'))
assert old!=new and old.replace(b'J): \n',b'J):\n')==new
assert ast.dump(ast.parse(old),include_attributes=False)==ast.dump(ast.parse(new),include_attributes=False)
oldmanifest=(base/'MANIFEST.sha256').read_bytes();newmanifest=oldmanifest.replace((sha(old)+'  checks/diag9.py').encode(),(sha(new)+'  checks/diag9.py').encode());assert newmanifest!=oldmanifest
logs=[]
with tempfile.TemporaryDirectory(prefix='floor-cosmetic-') as td:
 root=Path(td)/'floor';shutil.copytree(base,root,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 (root/'checks/diag9.py').write_bytes(new);(root/'MANIFEST.sha256').write_bytes(newmanifest)
 for script in ['manifest_check.py','diag9.py']:
  work=Path(td)/'work';work.mkdir(exist_ok=True)
  for src in (root/'checks').glob('*.py'):shutil.copy2(src,work/src.name)
  shutil.copy2(root/'data/data.json',work/'data.json')
  entry=root/'checks'/script if script=='manifest_check.py' else work/script
  cmd=['/tmp/pr-efficient1800/floor-venv/bin/python','-B',str(entry)]
  r=subprocess.run(cmd,cwd=root,capture_output=True,timeout=30);assert r.returncode==0,(script,r.stdout,r.stderr)
  if script=='diag9.py':assert r.stdout==(P/'sources/2854/maintainer-logs/d9.log').read_bytes()
  logs.append(dict(script=script,exit_code=r.returncode,stdout=r.stdout.decode(),stderr=r.stderr.decode()))
archive=P/'prior-revisions/2854-prewhitespace';archive.mkdir(parents=True,exist_ok=True)
shutil.copy2(P/'resolution-plan.json',archive/'resolution-plan.json');(archive/'MANIFEST.sha256').write_bytes(oldmanifest);(archive/'diag9.py').write_bytes(old)
plan=json.loads((P/'resolution-plan.json').read_text())
for path,data in [('checks/diag9.py',new),('MANIFEST.sha256',newmanifest)]:
 full=str(rel/path);entry=next((e for e in plan if e['number']==2854 and e['path']==full),None)
 if entry is None:
  entry=dict(number=2854,path=full,original_sha256=sha(old),resolved_mode='100644',reason='Remove one trailing space; identical Python AST and exact output against the retained complete census. Original full-run sources remain immutable.');plan.append(entry)
 else:entry['reason']+=' Subsequent one-space cosmetic cleanup has identical AST and diag9 output; manifest-only hashes rebound with a separate receipt.'
 entry['resolved_sha256']=sha(data)
 for dst in [P/'resolutions/2854'/full,R/full]:dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 subprocess.run(['git','add','--sparse','--',full],cwd=R,check=True)
(P/'resolution-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
report=dict(number=2854,head='7c0569975c3f331b8737e06f5aecfc2c7193c500',status='passed',seconds=time.monotonic()-start,scope='One trailing space removed. Full mathematical replay retained unchanged; AST equality plus exact diag9 output and complete manifest validation at the integrated bytes.',original_diag_sha256=sha(old),resolved_diag_sha256=sha(new),prior_manifest_sha256=sha(oldmanifest),resolved_manifest_sha256=sha(newmanifest),checks=logs)
log=json.dumps(report,indent=2)+'\n';(P/'check-2854-cosmetic.log').write_text(log);report['log_sha256']=sha(log.encode());(P/'check-2854-cosmetic.json').write_text(json.dumps(report,indent=2)+'\n');print(log)
