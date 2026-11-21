from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
commands = [['check_invoice.py'], ['check_incidence.py']]
for args in commands:
    subprocess.run([sys.executable, "-B", *args], cwd=root, check=True)
