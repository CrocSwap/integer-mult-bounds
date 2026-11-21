from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
commands = [['verify_relaxation.py'], ['verify_chart_paths.py'], ['verify_membership.py'], ['verify_balanced_planes.py']]
for args in commands:
    subprocess.run([sys.executable, "-B", *args], cwd=root, check=True)
