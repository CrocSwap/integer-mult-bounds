"""Time alternating complete price commands in fresh processes."""
from pathlib import Path
from hashlib import sha256
import json
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
rows = []
for pair in range(3):
    for mode in (('exact','bounded') if pair%2 == 0 else ('bounded','exact')):
        start = time.monotonic()
        result = subprocess.run([sys.executable,'-I','-B',str(HERE/'run.py'),mode],capture_output=True,check=True)
        elapsed = time.monotonic()-start
        receipt = json.loads(result.stdout)
        rows.append(dict(pair=pair,mode=mode,wall_seconds=elapsed,sha256=sha256(result.stdout).hexdigest()))
        if rows[-1]['sha256'] != rows[0]['sha256']:
            raise ValueError('Complete output mismatch')
medians = {mode:statistics.median(r['wall_seconds'] for r in rows if r['mode']==mode) for mode in ('exact','bounded')}
print(json.dumps(dict(python=platform.python_version(),platform=platform.platform(),samples=rows,medians=medians,
                     ratio=medians['exact']/medians['bounded'],scope='Complete source price/compiler/outer; native/caller inputs pinned.'),indent=2,sort_keys=True))
