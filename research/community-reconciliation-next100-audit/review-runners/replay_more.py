from pathlib import Path
import subprocess,json,time,hashlib,os
R=Path('/tmp/integer-mult-queue-20261013');P=Path('/tmp/reconciliation-next100-20261013');rows={r['number']:r for r in json.load(open(P/'snapshot.json'))['pull_requests']};G=['git','-c','maintenance.auto=false','-c','gc.auto=0'];PY='/tmp/integer-mult-review-venv/bin/python';env={**os.environ,'PATH':str(Path(PY).parent)+':'+os.environ['PATH'],'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'};out=[]
recipes={160:[[PY,'-B','scripts/paired_cube_bit.py']],241:[['python3.12','-B','research/complex-bank-run3/importer66.py','--contract','research/complex-bank-run3/export-contract-bit.json','--exports','research/complex-bank-run3/exports-bit','--partial']],255:[[PY,'-B','research/fixed-prime-pr254/verify.py']],256:[[PY,'-B','research/gcert-program-233/verify.py']],264:[[PY,'-B','scripts/verify_selected_result.py'],['make','entrance-bank-verify']]}
out=json.load(open(P/'more-execution.json'))
for n,cmds in recipes.items():
 if n<255:continue
 w=P/f'more-{n}';h=rows[n]['headRefOid']
 if not w.exists():subprocess.run(G+['worktree','add','--detach',str(w),h],cwd=R,check=True,stdout=subprocess.DEVNULL)
 for i,cmd in enumerate(cmds):
  log=P/f'pr{n}-more-{i}.txt';start=time.monotonic();print('START',n,cmd,flush=True)
  with log.open('w')as f:
   try:ret=subprocess.run(cmd,cwd=w,stdout=f,stderr=subprocess.STDOUT,timeout=1200,env=env).returncode
   except subprocess.TimeoutExpired:ret=124
  d=subprocess.check_output(G+['diff','--binary'],cwd=w)
  if d:(P/f'pr{n}-more-{i}.patch').write_bytes(d)
  out.append(dict(number=n,head=h,command=cmd,exit_code=ret,seconds=time.monotonic()-start,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),tracked_drift=bool(d)))
  (P/'more-execution.json').write_text(json.dumps(out,indent=2)+'\n');print('END',n,ret,round(time.monotonic()-start),flush=True)
 subprocess.run(G+['worktree','remove','--force',str(w)],cwd=R,check=True)
