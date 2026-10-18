"""Run PR2377's complete POSIX fixture with a macOS liveness observer.
Only /proc-based observation and Linux-only skip are adapted; production runner,
process-group/session checks, scenarios and leader-only negative controls remain.
For an already-exited leader Darwin may reject getpgid/getsid; that leader
records both identifiers before exiting. Live descendants are queried directly.
This is native macOS evidence, NOT a Linux run.
"""
import importlib.util,pathlib,subprocess,unittest,sys
root=pathlib.Path(sys.argv[1]);real_popen=subprocess.Popen
import types
path=root/'tests/test_research_process_tree.py'
source=path.read_text()
needle='(root / f"{depth}.pid").write_text(str(os.getpid()))'
source=source.replace(needle,needle+'\n(root / f"{depth}.pgid").write_text(str(os.getpgid(0)))\n(root / f"{depth}.sid").write_text(str(os.getsid(0)))')
source=source.replace('self.assertEqual(os.getpgid(pid), process.pid)', 'self.assertEqual(observed_id(pid, root, pids, "pgid"), process.pid)')
source=source.replace('self.assertEqual(os.getsid(pid), process.pid)', 'self.assertEqual(observed_id(pid, root, pids, "sid"), process.pid)')
m=types.ModuleType('process_fixture2377');m.__file__=str(path)
exec(compile(source,str(path),'exec'),m.__dict__)
def observed_id(pid, directory, pids, kind):
 import os
 try:return (os.getpgid if kind=='pgid' else os.getsid)(pid)
 except ProcessLookupError:
  if pid!=pids[2]:raise
  if alive(pid):raise RuntimeError('Missing identifier for a live leader')
  return int((directory/('2.'+kind)).read_text())
m.observed_id=observed_id
def alive(pid):
 p=real_popen(['/bin/ps','-p',str(pid),'-o','stat='],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 out,err=p.communicate(timeout=5)
 if p.returncode==1 and not out.strip():return False
 if p.returncode!=0:raise RuntimeError('ps failed: '+err)
 return bool(out.strip()) and out.strip()[0] not in ('Z','X')
m.alive=alive;m.ProcessTreeTests.__unittest_skip__=False
baseline='--baseline' in sys.argv
if baseline:
 original=subprocess.check_output(['git','show','0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2:scripts/research_package.py'],cwd=root)
 prior=types.ModuleType('baseline_research_package');prior.__file__=str(root/'scripts/research_package.py')
 exec(compile(original,prior.__file__,'exec'),prior.__dict__)
 m.package.run_command=prior.run_command
suite=unittest.defaultTestLoader.loadTestsFromTestCase(m.ProcessTreeTests)
r=unittest.TextTestRunner(verbosity=2).run(suite)
if baseline:
 expected={'test_successful_leader_exit_terminates_descendants','test_failed_leader_exit_terminates_descendants','test_interruption_terminates_descendants'}
 if r.errors or r.skipped or {t._testMethodName for t,_ in r.failures}!=expected:raise SystemExit(1)
 print('PASS_BASELINE_CONTROL_EXPECTED_3_LIFETIME_FAILURES')
 raise SystemExit(0)
if r.skipped or r.testsRun!=7 or not r.wasSuccessful():raise SystemExit(1)
print('PASS_NATIVE_MACOS_PROCESS_GROUP_ALL_7 no_skips original_PID_PGID_SID_assertions_and_negative_controls')
