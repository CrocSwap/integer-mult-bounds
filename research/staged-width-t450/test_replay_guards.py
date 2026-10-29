# SPDX-License-Identifier: Apache-2.0
"""Optimization must fail before creating output or reading missing inputs."""
from pathlib import Path
import subprocess,sys,tempfile
P=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory()as td:
 out=Path(td)/'must-not-exist'
 for name,args in [('replay.py',['--work',str(out),'--materialize-only']),('source_builder.py',['--out',str(out),'--source','missing','--local-package','missing','--driver-dir','missing','--retained-cache','missing','--retained-receipt','missing'])]:
  r=subprocess.run([sys.executable,'-O',str(P/name),*args],capture_output=True,text=True)
  if r.returncode==0 or 'Assertions must be enabled'not in r.stderr or out.exists():raise AssertionError((name,r.returncode,r.stderr))
print('PASS_TWO_OPTIMIZED_REPLAY_REFUSAL_CONTROLS')
