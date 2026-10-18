"""One bounded standard-library replay of the complete scoped package."""
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
for filename in ('verify.py', 'independent.py', 'comparison.py', 'test_package.py', 'frame_replay.py'):
    command = [sys.executable, '-I', '-B']
    if filename == 'test_package.py':
        command.append('-O')
    command.append(str(here / filename))
    subprocess.run(command, check=True, timeout=120)
print('PASS_COMPLETE_K8_PHASE_LOCAL_GAUGES')
