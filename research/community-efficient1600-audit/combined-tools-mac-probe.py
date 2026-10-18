from pathlib import Path
import importlib.util, subprocess, sys, unittest
n=int(sys.argv[1]);name='isolated_test_cancellation' if n==2625 else 'script_cancellation'
path=Path(__file__).parent/'combined-tool-fixture'/'tests'/f'test_{name}.py'
spec=importlib.util.spec_from_file_location('native_cancellation_probe',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
# Only replace the platform-specific /proc observer; run submitted tests and
# runner code unchanged on macOS's native POSIX process groups.
def alive(self):
 result=subprocess.run(['ps','-o','state=','-p',str(self.pid)],capture_output=True,text=True,timeout=3)
 if result.returncode==1:return False
 if result.returncode:raise RuntimeError('process observation failed: '+result.stderr)
 state=result.stdout.strip()
 return bool(state) and state[0] not in ('Z','X')
m.ProcessObserver.alive=alive
m.CancellationTests.__unittest_skip__=False
suite=unittest.defaultTestLoader.loadTestsFromModule(m)
result=unittest.TextTestRunner(verbosity=2).run(suite)
if result.skipped:raise RuntimeError('unexpected skipped native probe tests')
raise SystemExit(0 if result.wasSuccessful() else 1)
