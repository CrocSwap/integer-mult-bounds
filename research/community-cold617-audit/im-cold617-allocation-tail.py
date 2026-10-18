import subprocess,pathlib,json,time,sys,hashlib
root=pathlib.Path('/tmp/integer-mult-family588');runs=pathlib.Path('/tmp/im-cold617-replay');pkgs={int(k):pathlib.Path(v)for k,v in json.load(open('/tmp/im-cold617-packages.json')).items()}; sources=root/'research';records=[]
args=[]
for k,p in {'multicold':'complex-multicold','larger_gain':'promoted-kernel-coalescing/vendor/larger_gain','structural_gain':'structural-gain','joint_prefix':'complex-joint-prefix','frame_coalescing':'kernel-frame-coalescing'}.items():args+=['--source',k+'='+str(sources/p)]
def wait(n):
 deadline=time.time()+3600
 while not (runs/f'pr{n}/RECEIPT.json').exists():
  if time.time()>deadline:raise RuntimeError('Timed out waiting for '+str(n))
  time.sleep(3)
wait(614)
for n,b,localroot,basepkg in [(616,604,runs/'pr604',pkgs[604])]:
 if b==604:wait(604)
 pkg=pkgs[n];spec=json.load(open(pkg/'data/SPEC.json'));cmd=['/tmp/integer-mult-review-venv/bin/python','-B',str(pkg/'verify.py'),'--work',str(runs/f'pr{n}'),'--jobs','2',*args,'--reuse-baseline',str(runs/'pr601/baseline558')]
 evidence={}
 if b:
  for rel in ['verify.py',*[str(p.relative_to(basepkg))for p in sorted((basepkg/'code').glob('*.py'))]]:
   assert (basepkg/rel).read_bytes()==(pkg/rel).read_bytes(),(n,rel)
  basespec=json.load(open(basepkg/'data/SPEC.json'))
  for pid,d in spec['build']['providers'].items():
   assert d['word_content_sha256']==basespec['build']['providers'][pid]['word_content_sha256']
   lp=localroot/(pid+'-local');assert (lp/'CANONICAL-WORD.json.gz').exists()
   cmd+=['--reuse-local',pid+'='+str(lp)]
   evidence[pid]={str(p.relative_to(lp)):hashlib.sha256(p.read_bytes()).hexdigest()for p in lp.iterdir()if p.is_file()}
 t=time.time();print('RUN',n,flush=True)
 with open(f'/tmp/im-cold617-pr{n}.log','w')as f:proc=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 records.append({'pr':n,'reused_provider_pr':b,'local_artifacts':evidence,'command':cmd,'exit_code':proc.returncode,'seconds':time.time()-t});(runs/'ALLOCATIONS-TAIL.json').write_text(json.dumps(records,indent=2)+'\n')
 if proc.returncode:raise SystemExit(f'PR{n} failed')
 print('PASS',n,json.load(open(runs/f'pr{n}/RESULT.json'))['kappa_decimal'],flush=True)
