from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
commands = [['rare_tag_check.py']]
for args in commands:
    subprocess.run([sys.executable, "-B", *args], cwd=root, check=True)
