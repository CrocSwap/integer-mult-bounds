"""Measure the complete source command in alternating fresh processes."""
from hashlib import sha256
from pathlib import Path
import json
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
rows = []
for pair in range(3):
    for mode in (('baseline','integrated') if pair%2 == 0 else ('integrated','baseline')):
        start = time.monotonic()
        result = subprocess.run([sys.executable,'-I','-B',str(HERE/'run.py'),mode],capture_output=True,check=True)
        seconds = time.monotonic()-start
        row = dict(pair=pair,mode=mode,wall_seconds=seconds,sha256=sha256(result.stdout).hexdigest())
        if rows and row['sha256'] != rows[0]['sha256']:
            raise ValueError('Complete output mismatch')
        rows.append(row)
        print(json.dumps(row),file=sys.stderr,flush=True)
medians = {mode:statistics.median(r['wall_seconds'] for r in rows if r['mode']==mode) for mode in ('baseline','integrated')}
print(json.dumps(dict(python=platform.python_version(),platform=platform.platform(),samples=rows,medians=medians,
                     ratio=medians['baseline']/medians['integrated'],scope='Complete PR6453 regeneration and all scientific checks.'),indent=2,sort_keys=True))
