"""Offline source-pinned composition; every complete local invocation stays atomic."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,gzip,hashlib,subprocess,os,sys,time
assert __debug__
P=Path(__file__).resolve().parent;S=P.parent/'complex-stage4-gauge-mix'
a=argparse.ArgumentParser();a.add_argument('out',type=Path);a.add_argument('--reuse-local',type=Path);args=a.parse_args();O=args.out.resolve()
assert not O.exists() and not O.is_relative_to(P)
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in read(P/'MANIFEST.json').items():assert sha(P/n)==h,n
for n,h in read(P/'SIBLING-PINS.json').items():assert sha(S/n)==h,n
O.mkdir();A=O/'audit';A.mkdir();steps=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
def run(name,script,*argv):
 t=time.monotonic();log=O/(name+'.log')
 with log.open('w')as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,argv)],stdout=f,stderr=subprocess.STDOUT,env=env)
 steps.append(dict(name=name,returncode=r.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));(O/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
 assert r.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
try:
 if args.reuse_local:
  L=args.reuse_local.resolve()
  for n,h in read(S/'REUSE-LOCAL-INPUTS.json').items():assert sha(L/n)==h,n
  assert read(L/'RECEIPT.json')['status']=='PASS_BOTH_LOCAL_WORDS_NO_MIXED_GLOBAL_ADMISSION'
 else:
  run('fresh-source-provider-and-local',S/'verify.py',O/'dependency');L=O/'dependency/local'
 V=L/'baseline';assert read(V/'split-centres/FULL-WORD.json.gz')==read(S/'data/BASE-WORD.json.gz')
 t=read(V/'split-centres/GLOBAL-TEMPLATE.json.gz');checks=read(V/'split-centres/LOCAL-CHECKS.json');roles=read(P/'inputs/ASYNC-OWNERS.json.gz');used=defaultdict(set);paid=Counter()
 for z in roles:
  k=(z['child'],z['owner_replica'],z['port']);cells=set(range(z['offset'],z['offset']+z['width']));assert not used[k]&cells;used[k]|=cells
 for c in t['calls']:paid.update({int(k):v for k,v in checks[c['orientation']]['paid_profile'].items()})
 for idle in t['idle_children']:
  for rep in range(8):
   u=used[idle['child'],rep,idle['port']];assert u==set(range(len(u)));left=idle['rank']-len(u);assert left>=0
   if left:paid[left]+=1
 plan=read(P/'inputs/ASYNC-3.json');plan['profile']={str(k):v for k,v in sorted(paid.items())};assert plan==read(P/'inputs/RETIMED-PLAN.json');planfile=O/'PLAN.json';planfile.write_text(json.dumps(plan,indent=2)+'\n')
 H=O/'hosted';G=S/'vendor/complex/e8-complex-gauge-kernel'
 run('emit-async',P/'code/emit_async.py',G,V,P/'inputs/ASYNC-OWNERS.json.gz',planfile,H)
 run('independent-async',P/'code/audit_async.py',V,H,A/'ASYNC-AUDIT.json')
 run('finite-invoice',P/'code/audit_async_invoice.py',A,V,H)
 run('exact-assembly',P/'code/assemble.py',A,V,H,P/'inputs/PR493-EXPECTED.json')
 x=read(A/'EXACT-ASSEMBLY.json');expected=read(P/'EXPECTED.json')
 for k,v in expected.items():assert x[k]==v,k
 receipt=dict(status='PASS_CONDITIONAL_RETIMED_ASYNC_COMPLEX_COMPOSITION',**expected,local_mode='published-byte-pinned-completed-replay-reuse'if args.reuse_local else'fresh',bit_mode='PR493 operator cited; profile repriced in two exact engines',steps=steps,artifacts={f.relative_to(O).as_posix():sha(f)for f in sorted(A.glob('*.json'))},scope='Finite conditional witness. All-size compiler, common-label/mutable-basis, Lemma A realization, restored-row, precision/tape and analytic-transfer contracts remain assumptions.')
 (O/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],x['kappa_decimal'],flush=True)
except BaseException as e:
 (O/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
