import json,subprocess,tarfile,time,hashlib,os,shutil
from pathlib import Path
P=Path('/tmp/reconciliation-third100-20261013');R=Path('/tmp/integer-mult-queue-20261013');r=next(x for x in json.load(open(P/'snapshot.json'))['pull_requests']if x['number']==318);w=P/'check318';w.mkdir();head=r['headRefOid'];man=json.loads(subprocess.check_output(['git','show',head+':research/joint-dual/SOURCE.json'],cwd=R));paths=list(man['files'])+['scripts','certificates/joint-dual-kappa.json','certificates/joint-dual-validation.json','research/joint-dual/SOURCE.json'];proc=subprocess.Popen(['git','archive',head,*paths],cwd=R,stdout=subprocess.PIPE)
with tarfile.open(fileobj=proc.stdout,mode='r|') as t:t.extractall(w,filter='data')
assert proc.wait()==0
cmd=['/tmp/integer-mult-review-venv/bin/python','-B','-c',"import sys,hashlib,json; from pathlib import Path; sys.path.insert(0,'scripts/experiments'); from joint_dual_compose import check_sources,compose; check_sources(); c=compose(); assert str(c['kappa'])=='4764513337/100000000000000'; print('PASS source pins and exact 47-constraint composition'); import unittest; s=unittest.defaultTestLoader.discover('tests',pattern='test_joint_reclaim.py'); result=unittest.TextTestRunner(verbosity=2).run(s); assert result.wasSuccessful()"]
log=P/'pr318-focused.txt';start=time.monotonic()
with log.open('w')as f:ret=subprocess.run(cmd,cwd=w,stdout=f,stderr=subprocess.STDOUT).returncode
(P/'pins-execution.json').write_text(json.dumps([dict(number=318,head=head,command=cmd,exit_code=ret,seconds=time.monotonic()-start,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),scope='Changed pins, exact composition and unchanged compiler regression; no fresh full physical replay')],indent=2)+'\n');print(ret);shutil.rmtree(w)
