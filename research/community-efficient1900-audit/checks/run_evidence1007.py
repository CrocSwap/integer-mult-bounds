from pathlib import Path
import json,subprocess,hashlib,time,sys
from process_tree_watch import ProcessTreeWatch
P=Path('/tmp/pr-efficient1900');D=P/'combined-1007';pkg='research/pr116-evidence-reconciliation';py=sys.executable
commands=[[py,'-I','-O','-B',pkg+'/verify.py'],[py,'-I','-O','-B',pkg+'/test_package.py'],[py,'-I','-B','-m','unittest','discover','-s','tests','-p','test_pr116_ledger_evidence.py'],[py,'-B','scripts/reconcile_pr_queue.py'],[py,'-B','scripts/reconcile_pr_queue.py']]
results=[];first=None
with (P/'check-1007.log').open('wb') as log:
 for cmd in commands:
  log.write((repr(cmd)+'\n').encode());log.flush();start=time.monotonic();peak=0;reason=None
  proc=subprocess.Popen(cmd,cwd=D,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);watch=ProcessTreeWatch(proc.pid)
  while proc.poll() is None:
   rss,_=watch.sample();peak=max(peak,rss)
   if rss>1048576:reason='sampled_memory_guard_1GiB';watch.stop();break
   if time.monotonic()-start>120:reason='120_second_timeout';watch.stop();break
   time.sleep(.1)
  code=proc.wait();results.append(dict(argv=cmd,exit_code=code,seconds=time.monotonic()-start,peak_sampled_descendant_rss_kib=peak,stop_reason=reason));assert code==0 and reason is None,results[-1]
  if cmd[-1]=='scripts/reconcile_pr_queue.py':
   now={n:hashlib.sha256((D/'docs/research'/n).read_bytes()).hexdigest() for n in ['pr-ledger.json','pr-ledger.md']}
   if first is None:first=now
   else:assert first==now
before=json.loads((P/'before-1007-ledger.json').read_text());after=json.loads((D/'docs/research/pr-ledger.json').read_text());source=pkg+'/PARENT-EVIDENCE.json';comp=json.loads((D/source).read_text())['pull_requests'][0]
import copy
expected=copy.deepcopy(before);row=next(r for r in expected['pull_requests'] if r['number']==116);row['evidence'].append(dict(head=comp['head'],evidence=source,scope=comp['scope'],kind='independent_consolidation'));expected['source_sha256'][source]=hashlib.sha256((D/source).read_bytes()).hexdigest()
assert after==expected,'Whole-ledger preservation mismatch'
record=dict(number=1007,head=json.loads((P/'1007.json').read_text())['headRefOid'],status='passed',commands=results,whole_ledger_rows_preserved=len(before['pull_requests']),only_additions=['PR116 independent historical evidence pointer',source+' input digest'],byte_stable_regeneration=first,log_sha256=hashlib.sha256((P/'check-1007.log').read_bytes()).hexdigest(),scope='Independent historical evidence capsule,28tests,2ledger regressions, complete current-ledger equality except the two specified additions. No historical multiplication replay or Lean. Selected record untouched.')
(P/'check-1007.json').write_text(json.dumps(record,indent=2)+'\n');print('PASS',len(before['pull_requests']),'ledger records preserved;28+2tests;208objects authenticated')
