import subprocess,pathlib,json,time,sys,os
root=pathlib.Path('/tmp/integer-mult-family588'); out=pathlib.Path('/tmp/im-cold617-replay'); sources=root/'research'
args=[]
for k,p in {'multicold':'complex-multicold','larger_gain':'promoted-kernel-coalescing/vendor/larger_gain','structural_gain':'structural-gain','joint_prefix':'complex-joint-prefix','frame_coalescing':'kernel-frame-coalescing'}.items():args+=['--source',k+'='+str(sources/p)]
while not (out/'pr601/RECEIPT.json').exists():
 try:os.kill(1213,0)
 except ProcessLookupError:raise SystemExit('PR601 exited without receipt; stop chain')
 time.sleep(2)
assert json.load(open(out/'pr601/RESULT.json'))['kappa_decimal']=='0.001614202339036103'
steps=[]
for n,name in [(604,'complex-571-cold14'),(615,'complex-571-cold14-e1'),(617,'complex-571-cold14-b3')]:
 package=pathlib.Path(f'/tmp/im-cold617-sources/pr{n}/research')/name
 cmd=['/tmp/integer-mult-review-venv/bin/python','-B',str(package/'verify.py'),'--work',str(out/f'pr{n}'),'--jobs','2',*args]
 if n!=617:cmd+=['--reuse-baseline',str(out/'pr601/baseline558')]
 t=time.time();print('RUN',n,flush=True)
 with open(f'/tmp/im-cold617-pr{n}.log','w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 steps.append({'pr':n,'exit_code':p.returncode,'seconds':time.time()-t,'cmd':cmd});(out/'CHAIN.json').write_text(json.dumps(steps,indent=2)+'\n')
 if p.returncode:raise SystemExit(f'PR{n} failed')
 print('PASS',n,json.load(open(out/f'pr{n}/RESULT.json'))['kappa_decimal'],flush=True)
