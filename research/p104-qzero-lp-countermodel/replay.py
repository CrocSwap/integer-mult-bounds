from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
commands = [['verify_independent.py'], ['witness_event_frame.py']]
for args in commands:
    subprocess.run([sys.executable, "-B", *args], cwd=root, check=True)
