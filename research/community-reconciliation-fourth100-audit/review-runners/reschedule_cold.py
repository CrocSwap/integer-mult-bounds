import json,subprocess,time,os,signal,datetime
from pathlib import Path
P=Path('/tmp/reconciliation-fourth100-20261013');parent=75306
while True:
 data=json.load(open(P/'cold-retry-execution.json'))
 done={r['number'] for r in data}
 if {641,643}<=done:break
 time.sleep(5)
rows=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines();tree={}
for row in rows:
 fields=row.strip().split(None,2)
 if len(fields)==3:tree[int(fields[0])]=(int(fields[1]),fields[2])
assert parent in tree and 'cold_retry.py' in tree[parent][1]
os.kill(parent,signal.SIGSTOP)
# The parent is paused only while identifying and stopping its task-owned children.
rows=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True).splitlines();tree={}
for row in rows:
 f=row.strip().split(None,2)
 if len(f)==3:tree[int(f[0])]=(int(f[1]),f[2])
children=[];layer=[parent]
while layer:
 nxt=[p for p,(pp,c) in tree.items() if pp in layer];children+=nxt;layer=nxt
for p in reversed(children):
 try:os.kill(p,signal.SIGTERM)
 except ProcessLookupError:pass
os.kill(parent,signal.SIGTERM);os.kill(parent,signal.SIGCONT)
remaining=[n for n in [646,636,638,639,640,642,644] if n not in done]
record=dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),completed_before_rescheduling=sorted(done),cancelled_driver=parent,terminated_task_children=children,remaining_fresh_replays=remaining,reason='After the current pair completes, reschedule the remaining isolated full replays from two to four concurrent jobs as the other replay queues finish. No partial result is accepted or reused; all remaining runs start in new directories.',commands={str(p):tree[p][1] for p in children})
(P/'scheduling.json').write_text(json.dumps(record,indent=2)+'\n');print('RESCHEDULE',remaining,flush=True)
with (P/'cold-parallel-runner.log').open('w') as f:
 rc=subprocess.call(['python3','-B',str(P/'cold_parallel.py'),*map(str,remaining)],stdout=f,stderr=subprocess.STDOUT,cwd=P)
print('DONE PARALLEL',rc,flush=True)
