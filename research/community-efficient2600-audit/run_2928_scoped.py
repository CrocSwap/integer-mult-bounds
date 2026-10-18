from pathlib import Path
import json,subprocess,sys,time,hashlib,importlib.util
P=Path('/tmp/pr-efficient2600');R=Path('/tmp/integer-mult-efficient1100-20261015')
spec=importlib.util.spec_from_file_location('watch','/tmp/pr-efficient1900/process_tree_watch.py');watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
rows=json.loads((P/"TOOLING-REPLAY.json").read_text())
def run(n,label,mode,expected):
 name='test_research_replay_selection.py' if n==2958 else 'test_selected_ci_inputs.py';cmd=[sys.executable,'-B']+(['-O'] if mode=='optimized' else [])+['-c',"import sys,unittest;sys.path.insert(0,'tests');import test_selected_ci_inputs as t;suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(t,n)) for n in ('ExitCodes','Records','Globs','BranchFilterCLI'));result=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(not result.wasSuccessful())"];log=P/f'{n}-{label}-{mode}.log';start=time.monotonic();peak=0;stop=None
 with log.open('w') as out:
  proc=subprocess.Popen(cmd,cwd=R,stdout=out,stderr=subprocess.STDOUT,start_new_session=True);w=watch.ProcessTreeWatch(proc.pid)
  while proc.poll() is None:
   rss,_=w.sample();peak=max(peak,rss)
   if rss>1048576 or time.monotonic()-start>150:stop='memory' if rss>1048576 else 'timeout';w.stop();break
   time.sleep(.2)
  rc=proc.wait()
 text=log.read_text();ok=(rc==0 if expected=='pass' else rc!=0) and stop is None
 if expected=='baseline_failure':ok=ok and 'FAIL: test_' in text and 'ERROR:' not in text
 result=dict(number=n,stage=label,mode=mode,command=cmd,returncode=rc,seconds=round(time.monotonic()-start,3),sampled_peak_rss_kib=peak,stop=stop,expected=expected,pass_expected_outcome=ok,log=log.name,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest());rows.append(result);(P/'TOOLING-REPLAY.json').write_text(json.dumps(rows,indent=2)+'\n');print(result,flush=True)
 if not ok:print(text[-2500:]);raise RuntimeError('Unexpected replay outcome')
for n in (2928,):
 pk=json.loads((P/'packets'/f'{n}.json').read_text());changes=[f for f in pk['files'] if f['path'].startswith(('scripts/','tests/'))];original={f['path']:git('show','HEAD:'+f['path']) for f in changes}
 try:
  for f in changes:
   if f['path'].startswith('tests/'):(R/f['path']).write_bytes(git('cat-file','blob',f['source']['oid']))
  run(n,'baseline-focused','normal','baseline_failure')
  for f in changes:(R/f['path']).write_bytes(git('cat-file','blob',f['source']['oid']))
  run(n,'candidate-focused','normal','pass');run(n,'candidate-focused','optimized','pass')
 finally:
  for path,raw in original.items():(R/path).write_bytes(raw)
print('Both targeted suites and regression controls complete; production files restored to baseline.',flush=True)
