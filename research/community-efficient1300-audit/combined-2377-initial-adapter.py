"""Run PR2377's complete POSIX fixture with a macOS liveness observer.
Only /proc-based observation and Linux-only skip are adapted; production runner,
process-group/session checks, scenarios and leader-only negative controls remain.
This is native macOS evidence, NOT a Linux run.
"""
import importlib.util,pathlib,subprocess,unittest,sys
root=pathlib.Path(sys.argv[1]);real_popen=subprocess.Popen
spec=importlib.util.spec_from_file_location('process_fixture2377',root/'tests/test_research_process_tree.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def alive(pid):
 p=real_popen(['/bin/ps','-p',str(pid),'-o','stat='],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 out,err=p.communicate(timeout=5)
 if p.returncode==1 and not out.strip():return False
 if p.returncode!=0:raise RuntimeError('ps failed: '+err)
 return bool(out.strip()) and out.strip()[0] not in ('Z','X')
m.alive=alive;m.ProcessTreeTests.__unittest_skip__=False
suite=unittest.defaultTestLoader.loadTestsFromTestCase(m.ProcessTreeTests)
r=unittest.TextTestRunner(verbosity=2).run(suite)
if r.skipped or r.testsRun!=7 or not r.wasSuccessful():raise SystemExit(1)
print('PASS_NATIVE_MACOS_PROCESS_GROUP_ALL_7 no_skips original_PID_PGID_SID_assertions_and_negative_controls')
