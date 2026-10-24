"""Real POSIX descendants must not outlive a shared Git blob read.

Builds on the retained source-reader deadline and compatibility contracts.
JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
# Run the reader in a separate process so the unfixed regression is bounded by
# the test, without releasing its blocked read before we record the failure.
WORKER = r'''
import importlib.util,json,os,subprocess,sys,time
from pathlib import Path
from unittest.mock import patch
root, directory, mode, mutant = sys.argv[1:]
directory=Path(directory)
spec=importlib.util.spec_from_file_location('blob_reader',Path(root)/'scripts/research_package.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
p.GIT_BLOB_RESPONSE_TIMEOUT=.8
real_popen=subprocess.Popen
calls=[]
leader = r"""
import os,subprocess,sys,time
from pathlib import Path
directory=Path(sys.argv[1]);mode=sys.argv[2]
child=subprocess.Popen([sys.executable,'-c',
 'import os,time;from pathlib import Path;Path('+repr(str(directory/'child-ready'))+').write_text(str(os.getpid()));time.sleep(60)'])
while not (directory/'child-ready').exists(): time.sleep(.005)
if mode=='write': sys.exit(0)
while sys.stdin.buffer.read(1) not in (b'\0',b'\n',b''): pass
reply=b'a'*40+b' blob 4\n'+b'\0\xff\r\n'+b'\n'
if mode=='header': sys.exit(0)
if mode=='payload': sys.stdout.buffer.write(reply[:50]);sys.stdout.buffer.flush();sys.exit(0)
if mode=='terminator': sys.stdout.buffer.write(reply[:-1]);sys.stdout.buffer.flush();sys.exit(0)
if mode=='malformed': sys.stdout.buffer.write(b'bad\n');sys.stdout.buffer.flush();sys.exit(0)
sys.stdout.buffer.write(reply);sys.stdout.buffer.flush()
if mode=='suspended':
 while sys.stdin.buffer.read(1) not in (b'\0',b'\n',b''): pass
 sys.stdout.buffer.write(reply);sys.stdout.buffer.flush()
if mode=='early': time.sleep(60)
"""
def start(argv,**kwargs):
 calls.append(argv)
 if mode=='fallback' and len(calls)==1:
  child=real_popen([sys.executable,'-I','-B','-c','import sys;sys.exit(129)'],**kwargs)
 else:
  child=real_popen([sys.executable,'-I','-B','-c',leader,str(directory),mode],**kwargs)
 (directory/('leader-'+str(len(calls)))).write_text(str(child.pid))
 return child
if mutant=='direct':
 def direct(process):
  try: process.kill()
  except ProcessLookupError: pass
 p._stop_git_blob_process=direct
result={}
try:
 with patch.object(p.subprocess,'Popen',side_effect=start):
  rows=p.git_blobs(directory,['x'*2_000_000] if mode=='write' else ['HEAD:first','HEAD:second'] if mode=='suspended' else ['HEAD:first'])
  if mode in ('early','suspended'):
   result['first']=next(rows)==('a'*40,b'\0\xff\r\n')
   if mode=='suspended':
    time.sleep(1.1)
    os.kill(int((directory/'child-ready').read_text()),0)
    result['second']=next(rows)==('a'*40,b'\0\xff\r\n')
    result['exhausted']=list(rows)==[]
   rows.close()
  else: result['values']=list(rows)==[('a'*40,b'\0\xff\r\n')]
except Exception as error:
 import traceback;traceback.print_exc()
 result['error']=type(error).__name__
result['calls']=len(calls)
print(json.dumps(result),flush=True)
'''


def running(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    # An adopted zombie is stopped, even before the system reaps its PID.
    state = subprocess.run(['ps', '-o', 'stat=', '-p', str(pid)],
                           capture_output=True, text=True, timeout=2).stdout.strip()
    return bool(state) and not state.startswith('Z')


@unittest.skipUnless(os.name == 'posix', 'POSIX owned process-group contract')
class GitBlobDescendantTests(unittest.TestCase):
    def exercise(self, mode, mutant=False):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            argv = [sys.executable, '-I', '-B']
            if sys.flags.optimize:
                argv.append('-O')
            argv += ['-c', WORKER, str(ROOT), temporary, mode, 'direct' if mutant else 'none']
            process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, start_new_session=True)
            try:
                try:
                    stdout, stderr = process.communicate(timeout=4)
                    expired = False
                except subprocess.TimeoutExpired:
                    expired = True
                    process.kill()
                    stdout, stderr = process.communicate(timeout=2)
                # Readiness and process state are inspected BEFORE fallback cleanup.
                self.assertTrue((directory / 'child-ready').exists(), stderr)
                child = int((directory / 'child-ready').read_text())
                if mutant:
                    self.assertTrue(expired, stdout + stderr)
                    self.assertTrue(running(child))
                    return
                self.assertFalse(expired, 'reader exceeded its deadline: ' + stderr)
                self.assertEqual(process.returncode, 0, stderr)
                if 'PermissionError' in stderr: self.fail(stderr)
                end = time.monotonic() + 1
                while running(child) and time.monotonic() < end:
                    time.sleep(.01)
                self.assertFalse(running(child), 'descendant survived reader completion')
                return json.loads(stdout)
            finally:
                # This is failure containment, never evidence of successful cleanup.
                for path in directory.glob('leader-*'):
                    try:
                        os.killpg(int(path.read_text()), signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=2)
                for stream in (process.stdout, process.stderr):
                    stream.close()

    def test_exited_leader_header_payload_terminator_and_write_stalls(self):
        for mode in ('header', 'payload', 'terminator', 'write'):
            with self.subTest(mode=mode):
                result = self.exercise(mode)
                self.assertEqual(result, {'error': 'TimeoutExpired', 'calls': 1})

    def test_success_and_malformed_reply_stop_ready_descendant(self):
        self.assertEqual(self.exercise('success'), {'values': True, 'calls': 1})
        self.assertEqual(self.exercise('malformed'), {'error': 'ValueError', 'calls': 1})

    def test_early_close_stops_live_leader_and_descendant(self):
        self.assertEqual(self.exercise('early'), {'first': True, 'calls': 1})

    def test_consumer_suspension_does_not_expire_the_next_response(self):
        self.assertEqual(self.exercise('suspended'),
                         {'first': True, 'second': True, 'exhausted': True, 'calls': 1})

    def test_legacy_fallback_retains_exact_reply_and_owns_descendant(self):
        self.assertEqual(self.exercise('fallback'), {'values': True, 'calls': 2})

    def test_direct_child_only_mutant_still_hangs_with_ready_descendant(self):
        self.exercise('header', mutant=True)


if __name__ == '__main__':
    unittest.main()
