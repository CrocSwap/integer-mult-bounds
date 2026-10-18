import json,subprocess,time,hashlib
from pathlib import Path
P=Path('/tmp/reconciliation92-20261013');ROOT=Path('/tmp/integer-mult-queue-20261013');D={r['number']:r for r in json.loads((P/'snapshot.json').read_text())['pull_requests']}
rows=[]
for n,folder,up,target in [(70,'profile-aware-frame-search','ad0f25ff7b23cff7f08ad237c2254e6ecf74257e','Frozen62Research'),(75,'current-record-circuits','1bef94fd40a746452548c84a4a8f8834670a3113','CurrentRecordMath')]:
 work=P/f'ext{n}';base=P/f'base{n}';head=D[n]['headRefOid']
 for path,sha in [(work,head),(base,up)]:subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','add','--detach',str(path),sha],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 p=work/'research'/folder;prof=P/f'profiler{n}'
 commands=[(['c++','-O3','-std=c++17','-I',str(base/'references/frame-compiler/pr48/scripts/partial_swap'),str(base/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(prof)],work),(['python3.12','-B',str(p/'verification/verify_words.py'),'--upstream',str(base),'--profiler',str(prof),'--word23',str(p/'words/word-23.json.gz'),'--word25',str(p/'words/word-25.json.gz'),'--output',str(work/'build/reconciliation-replay')],work),(['lake','build',target],p/'math')]
 for i,(cmd,cwd) in enumerate(commands):
  print('START',n,i,flush=True);log=P/f'pr{n}-external-{i}.txt';start=time.monotonic()
  with log.open('w') as out:r=subprocess.run(cmd,cwd=cwd,stdout=out,stderr=subprocess.STDOUT)
  rows.append(dict(number=n,head=head,command=cmd,cwd=str(cwd.relative_to(work)),exit_code=r.returncode,seconds=time.monotonic()-start,log=log.name,sha256=hashlib.sha256(log.read_bytes()).hexdigest()));(P/'external-execution.json').write_text(json.dumps(rows,indent=2)+'\n');print('END',n,i,r.returncode,flush=True)
 for path in [work,base]:subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','worktree','remove','--force',str(path)],cwd=ROOT,check=True)
 if prof.exists():prof.unlink()
