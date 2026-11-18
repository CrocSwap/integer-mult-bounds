#!/usr/bin/env python3
"""Source-free control: a hook-owned process group contains its child."""
import os
from pathlib import Path
import importlib.util
import json
import shutil
import signal
import subprocess
import sys
import tempfile
import time


def main():
    with tempfile.TemporaryDirectory(prefix='p104-timeout-control-') as directory:
        package = Path(__file__).resolve().parent
        spec = importlib.util.spec_from_file_location('p104_replay_control', package / 'verify.py')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        verifier.POINTER = Path(directory) / 'pointer.json'
        scratch = verifier.create_workspace()
        try:
            if verifier.workspace() != scratch:
                raise RuntimeError('workspace binding mismatch')
            try:
                verifier.create_workspace()
            except FileExistsError:
                pass
            else:
                raise RuntimeError('concurrent pointer was accepted')
            marker_file = scratch / '.replay-owner.json'
            marker = json.loads(marker_file.read_text())
            marker['token'] = 'incorrect-token'
            marker_file.write_text(json.dumps(marker))
            try:
                verifier.workspace()
            except ValueError:
                pass
            else:
                raise RuntimeError('mismatched owner marker was accepted')
        finally:
            shutil.rmtree(scratch)
            verifier.POINTER.unlink()
        marker = Path(directory) / 'child.pid'
        parent_code = """\
import subprocess
import sys
import time
from pathlib import Path

child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
marker = Path(sys.argv[1])
pending = marker.with_suffix(".tmp")
pending.write_text(str(child.pid), encoding="ascii")
pending.replace(marker)
time.sleep(60)
"""
        parent = subprocess.Popen([sys.executable, '-I', '-B', '-c', parent_code, str(marker)],
                                  start_new_session=True)
        try:
            deadline = time.monotonic() + 10
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            if not marker.exists():
                raise RuntimeError('timeout control child did not start')
            child_pid = int(marker.read_text())
            if os.getpgid(child_pid) != parent.pid:
                raise RuntimeError('child escaped hook-owned group')
            os.killpg(parent.pid, signal.SIGTERM)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                status = Path('/proc') / str(child_pid) / 'stat'
                try:
                    state = status.read_text().split()[2]
                except FileNotFoundError:
                    state = None
                leader_exit = os.waitid(os.P_PID, parent.pid,
                                        os.WEXITED | os.WNOHANG | os.WNOWAIT)
                if leader_exit is not None and state in (None, 'Z'):
                    break
                time.sleep(0.02)
            else:
                raise RuntimeError('group termination left a live parent or child')
        finally:
            # Keep the group leader unreaped until the final cleanup. Its PID
            # cannot be reused even if it exits before publishing the marker.
            try:
                os.killpg(parent.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            parent.wait(timeout=5)
    print('PASS_SOURCE_FREE_PROCESS_GROUP_CONTROL')


if __name__ == '__main__':
    main()
