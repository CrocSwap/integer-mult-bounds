import json,gzip,hashlib,shutil,subprocess,os,time
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');PY='/tmp/integer-mult-review-venv/bin/python';rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']};receipts=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n in [455,505]:
 old=P/('local-455-out'if n==455 else'repaired-505-out');out=P/f'serialized-{n}-out';shutil.copytree(old,out);src=P/('local-455'if n==455 else'repaired-505');pkg=next((src/'research').iterdir());logs=[];repairs=[]
 files=['local0/nine/GEOMETRY.json','local2/nine/GEOMETRY.json']if n==455 else['base/split-centres/RESIDUAL-ADAPTERS.json']
 # Every retained source file must still satisfy the frozen manifest (505 metadata-only repair).
 mf=json.load(open(pkg/'MANIFEST.json'));mf=mf.get('files',mf)
 for p,h in mf.items():assert sha(pkg/p)==h,p
 for name in files:
  f=out/name;raw=f.read_bytes();assert b'\r'not in raw;fixed=raw.replace(b'\n',b'\r\n');assert fixed.replace(b'\r\n',b'\n')==raw and json.loads(fixed)==json.loads(raw);f.write_bytes(fixed);repairs.append(dict(path=name,original_sha256=hashlib.sha256(raw).hexdigest(),crlf_sha256=sha(f)))
 if n==455:
  stages=json.load(open(old/'FAILURE.json'))['completed'];assert len(stages)>=30
  for stage in stages:assert sha(old/(stage['name']+'.log'))==stage['log_sha256']
  commands=[]
  for v in [0,2]:
   local=out/f'local{v}';commands.append(['v'+str(v)+'-global',pkg/'vendor/runtime/global_k.py','--word',local/'word.json','--local-check',local,'--out',local/'nine','--isometries',pkg/'inputs/residual-isometries.json','--stages','11','--replicas','8','--no-banks'])
  commands += [['whole-bit',pkg/'code/emit_whole.py',out/'local0/nine',out/'local0',pkg/'inputs/bit-selection.json',out/'bit',out/'local2'],['whole-bit-independent',pkg/'code/audit_whole.py',out/'local0',out/'bit',out/'bit/AUDIT.json',out/'local2'],['exact-assembly',pkg/'code/assemble.py',out/'local0',out/'bit',out/'bit/AUDIT.json',out/'RESULT.json','--complex',out/'complex','--engines',pkg/'engines','--inherited',pkg/'inherited','--route-extra','3','--label','PR451','--variant-globals',out/'local2/nine/GLOBAL.json']]
  cwd=src
 else:
  stages=json.load(open(old/'STEPS.json'));assert len(stages)==11 and all(s['exit']==0 for s in stages)
  V=out/'base';G=pkg/'vendor/complex/e8-complex-gauge-kernel';H=out/'hosted';A=out/'audit';commands=[['parent-integration',G/'code/integrate_gk.py'],['parent-replay',G/'code/replay_gk.py'],['emit-async',pkg/'code/emit_async.py',G,V,pkg/'inputs/ASYNC-OWNERS.json.gz',pkg/'inputs/ASYNC-3.json',H],['independent-async',pkg/'code/audit_async.py',V,H,A/'ASYNC-AUDIT.json'],['invoice',pkg/'code/audit_async_invoice.py',A,V,H],['two-moments-assembly',pkg/'code/assemble.py',A,V,H,pkg/'inputs/PR493-EXPECTED.json']];cwd=V
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONINTMAXSTRDIGITS='0');start=time.time();log=P/f'pr{n}-serialization.txt';print('START',n,flush=True)
 try:
  with log.open('w')as stream:
   for name,*args in commands:
    
    if name in ('whole-bit','emit-async'):shutil.rmtree(out/('bit' if n==455 else 'hosted'))
    cmd=[PY,'-B',*map(str,args)];stream.write('COMMAND '+json.dumps(cmd)+'\n');stream.flush();z=subprocess.run(cmd,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT);logs.append(dict(name=name,command=cmd,exit_code=z.returncode));assert z.returncode==0,name
   expected=json.load(open(pkg/'EXPECTED.json'))
   if n==455:
    actual=json.load(open(out/'RESULT.json'))
    for k in ['kappa','bit_lower','complex_lower','bit_profile','bit_template_sha256','complex_template_sha256','emitted_program_sha256']:assert actual[k]==expected[k],(k,actual[k],expected[k])
    assert len(json.load(open(out/'bit/AUDIT.json'))['mutations_rejected'])>=19;assert len(json.load(open(out/'complex/AUDIT.json'))['mutations_rejected'])==10
   else:
    x=json.load(open(out/'audit/EXACT-ASSEMBLY.json'));actual={**x,'template_sha256':x['complex_template_sha256']}
    for k in ['kappa','complex_lower','bit_lower','template_sha256']:assert actual[k]==expected[k],(k,actual[k],expected[k])
   stream.write('PASS every original expected endpoint, full template digest and downstream audit after lossless JSON newline serialization. Original scientific sources unchanged.\n')
  status=0
 except Exception as e:
  with log.open('a')as f:f.write(repr(e)+'\n')
  status=1
 evidence=dict(number=n,head=rows[n]['headRefOid'],serialization_repairs=repairs,prior_stages=stages,downstream=logs,scope='Original full scientific stages reused from this round; exact JSON value preserving LF-to-CRLF serialization, followed by fresh unchanged dependent emitters/audits/assembly. Every original final expected hash is required.');(P/f'serialization-{n}.json').write_text(json.dumps(evidence,indent=2)+'\n')
 receipts.append(dict(number=n,head=rows[n]['headRefOid'],commands=[x['command']for x in logs],exit_code=status,seconds=time.time()-start,log=log.name,sha256=sha(log),scope=evidence['scope']));(P/'serialization-execution.json').write_text(json.dumps(receipts,indent=2)+'\n');print('DONE',n,status,flush=True)
 keep=P/f'pr{n}-outputs'/'serialization';keep.mkdir(exist_ok=True)
 for f in out.rglob('*'):
  if f.is_file()and f.name in['RESULT.json','EXACT-ASSEMBLY.json','AUDIT.json','ASYNC-AUDIT.json','HOSTED.json']:
   dest=keep/f.relative_to(out);dest=dest.with_name(dest.name+'.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(gzip.compress(f.read_bytes(),mtime=0))
 if status==0:shutil.rmtree(out)
