"""Portable read-only exact replay entry point. Apache-2.0; Codex assistance."""
from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
P=Path(__file__).resolve().parent
for name,digest in json.loads((P/'INTEGRITY.json').read_bytes()).items():
    if sha256((P/name).read_bytes()).hexdigest()!=digest:raise ValueError('Changed input: '+name)
flags=['-I','-B']+(['-O']if sys.flags.optimize else[])
for script in ['backward.py','caller.py','phase_backward.py']:
    subprocess.run([sys.executable,*flags,str(P/script)],check=True,timeout=110)
print('PASS_NATIVE_INVOLUTIVE_DUAL_AND_DYADIC_CALLER_NO_NEW_KAPPA')
