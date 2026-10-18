from pathlib import Path
import subprocess,shutil
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-2906';D.mkdir(exist_ok=True)
paths=['scripts/run_isolated_tests.py','scripts/replay_historical_check.py','tests/test_isolated_test_runner.py','tests/test_isolated_historical_completion.py','tests/test_isolated_test_cancellation.py']
for rel in paths:
 f=D/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(subprocess.check_output(['git','show','HEAD:'+rel],cwd=R))
runner=D/paths[0];(P/'baseline-runner2906.py').write_bytes(runner.read_bytes());s=runner.read_text();needle='''            if finished:
                with lock:
                    active.discard(process)''';insert='''            if finished:
                # Pipe EOF and leader exit do not imply solver completion: a
                # descendant may have closed its inherited capture streams.
                # Keep ownership until POSIX group cleanup succeeds, including
                # ordinary success/failure. Windows exited leaders need a Job
                # Object; the existing taskkill cancellation contract is unchanged.
                if os.name != 'nt':
                    stop_module(process)
                with lock:
                    active.discard(process)''';assert s.count(needle)==1;runner.write_text(s.replace(needle,insert))
for rel in ['tests/test_isolated_test_exit_cleanup.py','docs/research/isolated-test-exit-cleanup.md']:
 f=D/rel;f.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/'sources/2906'/rel,f)
# Port only the observer to native retained kqueue process-exit events. The
# production fixture, readiness handshake and all six assertions are unchanged.
helper='''
class ProcessHandle:
    def __init__(self, pid):
        self.queue = select.kqueue()
        self.exited = False
        try:
            self.queue.control([select.kevent(pid, filter=select.KQ_FILTER_PROC,
                flags=select.KQ_EV_ADD | select.KQ_EV_ENABLE | select.KQ_EV_ONESHOT,
                fflags=select.KQ_NOTE_EXIT)], 0, 0)
        except BaseException:
            self.queue.close()
            raise
    def ready(self):
        self.exited = self.exited or bool(self.queue.control([], 1, 0))
        return self.exited
    def close(self):
        self.queue.close()
def open_process(pid):
    return ProcessHandle(pid)
def process_select(handles, write, error, timeout):
    import time
    deadline = time.monotonic() + timeout
    while True:
        ready = [h for h in handles if h.ready()]
        if ready or time.monotonic() >= deadline:
            return ready, [], []
        time.sleep(.005)
'''
s=(D/'tests/test_isolated_test_exit_cleanup.py').read_text();s=s.replace('os.pidfd_open(pid)','open_process(pid)').replace('os.close(handle)','handle.close()').replace('select.select(', 'process_select(').replace('sys.platform == "linux" and hasattr(os, "pidfd_open")','sys.platform == "darwin" and hasattr(select, "kqueue")').replace('Linux retained process descriptors required','macOS retained kqueue process-exit events required');s=s.replace('ROOT = Path(__file__)',helper+'\nROOT = Path(__file__)');s=s.replace('from pathlib import Path\nclass T(unittest.TestCase):','from pathlib import Path\n'+helper+'\nclass T(unittest.TestCase):')
(D/'tests/test_exit_cleanup_macos.py').write_text(s)
print('Prepared current-runner candidate and native macOS observer for all six author controls')
