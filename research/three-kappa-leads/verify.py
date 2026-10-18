#!/usr/bin/env python3
"""Bounded exact finite checks and stored-evidence authentication, no full replay."""
from pathlib import Path
import os,subprocess,sys
P=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('enabled assertions required by retained proof engines')
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
for key in ['PYTHONPATH','PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER']:env.pop(key,None)
for script in ['chronology_check.py','aggregate_controls.py','price_check.py','bridge_screen.py','consumer_screen.py','evidence_check.py','evidence_controls.py']:
 subprocess.run([sys.executable,'-B',str(P/script)],env=env,check=True)
print('PASS_THREE_LEADS_FINITE_AND_STORED_EVIDENCE_NOT_FRESH_FULL_REPLAY')
