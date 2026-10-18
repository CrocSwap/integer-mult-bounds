"""Rebuild only the PR548 complex supplier used for an R420 composition.
No PR548 bit result is used. Unchanged source auditors retain their notices.
Prepared for Rohan Arun with OpenAI Codex assistance.
"""
from pathlib import Path
import json,hashlib,subprocess,os,sys,time
R=Path(__file__).resolve().parent;P=R/'source548-review';O=R/'pr548-complex314';assert not O.exists();manifest=json.loads((P/'MANIFEST.json').read_text());present={f.relative_to(P).as_posix()for f in P.rglob('*')if f.is_file()and '__pycache__'not in f.parts};assert present==set(manifest['files'])|{'MANIFEST.json'}
for rel,item in manifest['files'].items():
 raw=(P/rel).read_bytes();raw=raw.replace(b'\r\n',b'\n')if item['mode']=='lf-text'else raw;assert hashlib.sha256(raw).hexdigest()==item['sha256'],rel
O.mkdir();(O/'tmp').mkdir();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(O/'tmp'));steps=[];start=time.monotonic()
for name,script,args in [('local',P/'complex-local/run_local.py',['--out',O/'complex-local','--vendor',P/'complex-global/vendor531']),('global',P/'complex-global/replay.py',['--local',O/'complex-local/local','--out',O/'complex-global'])]:
 t=time.monotonic()
 with(O/(name+'.log')).open('w')as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],env=env,cwd=O,stdout=f,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,exit=r.returncode,seconds=time.monotonic()-t));(O/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
 if r.returncode:print((O/(name+'.log')).read_text()[-5000:]);raise SystemExit(name+' failed')
 print('PASS',name,flush=True)
def read(path):return json.loads(path.read_text())
e=read(P/'EXPECTED.json');A=O/'complex-global/audit';owner=read(A/'OWNERS-AND-PROFILE.json');inv=read(A/'PREFIX-AND-INVOICE.json');host=read(O/'complex-global/hosted/HOSTED.json');assert owner['template_sha256']==inv['template_sha256']==host['template_sha256']==e['complex_template_sha256'];assert inv['canonical_word_sha256']==e['complex_canonical_word_sha256'];assert owner['paid_profile']==e['complex_global_profile'];assert inv['global_prefix_bits']==e['complex_prefix_bits'];assert all(inv['strict_checks'].values());assert inv['finite']['physical_row_coefficient']<20161
r=dict(status='PASS_FRESH_PR548_COMPLEX_COMPONENT_ADMISSION',source_head='66dbc2bffc1bfa8d50b3f9a2ac7ccba8fd9f6f36',steps=steps,profile=owner['paid_profile'],template_sha256=owner['template_sha256'],canonical_word_sha256=inv['canonical_word_sha256'],prefix_bits=inv['global_prefix_bits'],live=owner['live'],physical=owner['physical'],deficit=owner['deficit'],seconds=time.monotonic()-start,artifacts={f.relative_to(O).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in [A/'OWNERS-AND-PROFILE.json',A/'PREFIX-AND-INVOICE.json',A/'ASYNC-AUDIT.json',O/'complex-local/local/CLIFFORD-REVIEW.json',O/'complex-local/local/INDEPENDENT-LOCAL-REPLAY.json']},scope='Fresh PR548 complex construction, frames, changed local phase edges, residual wrappers, whole-owner controller, mutations and finite invoice. Pinned unchanged phase/data dependencies retained. PR548 bit supplier not rebuilt or used; intended bit supplier is previously independently verified PR543. All-size assumptions remain conditional.')
(O/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['seconds'],flush=True)
