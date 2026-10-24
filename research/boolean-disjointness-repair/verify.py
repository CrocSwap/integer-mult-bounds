"""Replay rank elimination and the separate exhaustive kernel checks."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
for name, expected in json.loads((HERE/'SOURCE-HASHES.json').read_text()).items():
    if hashlib.sha256((HERE/name).read_bytes()).hexdigest() != expected:
        raise ValueError('Source hash mismatch: '+name)
with tempfile.TemporaryDirectory(prefix='boolean-disjointness-repair-') as temp:
    work = Path(temp)/'package'
    shutil.copytree(HERE, work, ignore=shutil.ignore_patterns('__pycache__'))
    for script, result in [('check_zeta_corrector.py','ZETA-CORRECTOR-CHECK.json'),
                           ('independent/verify.py','independent/RESULT.json')]:
        run = subprocess.run([sys.executable,'-I','-B',str(work/script)],cwd=work,
                             capture_output=True,text=True,timeout=120)
        if run.returncode:
            raise ValueError(script+'\n'+run.stderr)
        if json.loads((work/result).read_text()) != json.loads((HERE/result).read_text()):
            raise ValueError('Receipt mismatch: '+result)
        print('PASS '+script)
print('PASS_BOOLEAN_DISJOINTNESS_REPAIR h=2..11 independent_kernels=2..4 no_new_kappa')
