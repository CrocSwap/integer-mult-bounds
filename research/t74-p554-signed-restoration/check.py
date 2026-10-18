#!/usr/bin/env python3
"""Local construction and arithmetic checks; full physical replay is separate."""
import os,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None)
for n in ['verify.py','price.py']:
    subprocess.run([sys.executable,'-I','-B',str(P/n)],check=True,env=env)
print('PASS_P554_CONSTRUCTION_AND_PRICE kappa=0.001676938111022438')
