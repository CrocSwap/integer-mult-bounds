"""Portable full native and fixed17-stage caller replay; no network writes."""
from pathlib import Path
import subprocess,sys,time
HERE=Path(__file__).resolve().parent
assert __debug__,'Run Python without -O'
for script in ('reroute/build.py','validation_native/owned_contract.py','validation_native/run.py','validation_signed/run.py','finalise.py'):
 print('RUN',script,flush=True);started=time.time()
 subprocess.run([sys.executable,str(HERE/script)],cwd=HERE.parent,check=True)
 print('PASS',script,'seconds',time.time()-started,flush=True)
print('PASS_COMPLETE_CHANGED_PRODUCER_APPLICATION',flush=True)
