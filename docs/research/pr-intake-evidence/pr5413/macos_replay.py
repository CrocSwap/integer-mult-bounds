"""Replay unchanged authenticated package with explicit Darwin AS adapter."""
from pathlib import Path
import runpy
import subprocess
import sys
import os
import tempfile

if not sys.flags.isolated or sys.platform != 'darwin':
    raise RuntimeError('This reviewed adapter is only for isolated Darwin replay')
adapter = str(Path(__file__).with_name('macos_engine.py'))
original = subprocess.run
fd, trace = tempfile.mkstemp(prefix='maintainer-darwin-rlimit-', suffix='.jsonl')
os.close(fd)
os.environ['MAINTAINER_RLIMIT_TRACE'] = trace
print('MAINTAINER DARWIN RESOURCE ADAPTER: fallback events recorded at ' + trace,
      flush=True)

def compatible_run(argv, *args, **kwargs):
    if isinstance(argv, list):
        positions = [i for i, v in enumerate(argv)
                     if isinstance(v, str) and (v.endswith('/engine_adapter.py')
                         or v.endswith('/screen/check_neutral.py'))]
        if positions:
            if len(positions) != 1:
                raise RuntimeError('Unexpected adapter command')
            argv = list(argv)
            argv.insert(positions[0], adapter)
    return original(argv, *args, **kwargs)

subprocess.run = compatible_run
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
