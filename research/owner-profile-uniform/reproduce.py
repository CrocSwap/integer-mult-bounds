"""Run both proofs and mutation controls from any working directory."""
from pathlib import Path
import subprocess
import sys

p=Path(__file__).resolve().parent
for name in ('verify.py','independent.py','controls.py'):
    subprocess.run([sys.executable,'-B',p/name],check=True)
print('PASS_UNIFORM_OWNER_PACKAGE')
