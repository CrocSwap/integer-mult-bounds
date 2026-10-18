import json,subprocess,time,hashlib,os,signal
from pathlib import Path
P=Path('/tmp/reconciliation92-20261013');ROOT=Path('/tmp/integer-mult-queue-20261013')
rows={r['number']:r for r in json.loads((P/'snapshot.json').read_text())['pull_requests']}
recipes={13:['source_frame_network'],14:[],15:['*'],16:['nested_source_integration'],17:['nested_stream'],19:['partial_swap_ternary'],21:['translated_partial'],22:['translated_partial'],23:['semantic_bulk'],25:['a5_semantic'],27:['semantic_bulk'],28:['rectangular_semantic'],29:['two_stage'],31:['two_stage_corners'],33:['two_stage_dimensions'],34:['two_stage_dimensions'],35:['two_stage_dimensions'],38:[],40:['copied_both_reversed'],41:[],42:['rad_fixed_reversed'],44:['optimal_matching','copied_fixed'],47:['climbed_producers']}
extra={14:['research/source-frame-corners/witness.py'],38:['research/copied-fixed-basis/verify.py'],41:['research/rad-left-producer/verify.py']}
results=[]
for n,tests in recipes.items():
 work=P/f'early{n}';head=rows[n]['headRefOid'];subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','add','--detach',str(work),head],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 commands=[['python3.12','-B','-m','unittest','discover','-s','tests','-p',f'test_{test}.py','-v'] for test in tests]+[['python3.12','-B',f] for f in extra.get(n,[])]
 for i,cmd in enumerate(commands):
  log=P/f'pr{n}-focused-{i}.txt';start=time.monotonic();print('START',n,cmd,flush=True)
  with log.open('w') as out:
   proc=subprocess.Popen(cmd,cwd=work,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
   try:code=proc.wait(timeout=900)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM);code=124
  results.append(dict(number=n,head=head,command=cmd,exit_code=code,seconds=time.monotonic()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
  (P/'early-execution.json').write_text(json.dumps(results,indent=2)+'\n');print('END',n,code,round(time.monotonic()-start),flush=True)
 drift=subprocess.check_output(['git','diff','--binary'],cwd=work)
 if drift:(P/f'pr{n}-early-drift.patch').write_bytes(drift)
 subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','remove','--force',str(work)],cwd=ROOT,check=True)
