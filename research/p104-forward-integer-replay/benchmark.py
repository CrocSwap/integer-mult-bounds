"""Measure complete fresh-process scalar replays in alternating order."""
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent
samples=[];receipt=None
for cycle in range(5):
    order=('fraction','sparse','packed') if cycle%2==0 else ('packed','sparse','fraction')
    for engine in order:
        start=time.perf_counter()
        process=subprocess.run([sys.executable,'-I','-B',str(HERE/'run.py'),engine],check=True,text=True,capture_output=True)
        elapsed=time.perf_counter()-start
        value=json.loads(process.stdout)
        result=json.dumps(value['result'],sort_keys=True,separators=(',',':'))
        if receipt is not None and result!=receipt:
            raise ValueError('Scientific receipts differ')
        receipt=result
        samples.append(dict(cycle=cycle,engine=engine,process_seconds=elapsed,replay_seconds=value['seconds']))
medians={engine:{key:statistics.median(x[key] for x in samples if x['engine']==engine)
                  for key in ('process_seconds','replay_seconds')} for engine in ('fraction','sparse','packed')}
result=dict(environment=dict(python=sys.version,platform=platform.platform()),samples=samples,medians=medians,
            receipt_sha256=sha256(receipt.encode()).hexdigest(),
            sources={name:sha256((HERE/name).read_bytes()).hexdigest() for name in ('driver.py','rows.py','run.py','pins.py','benchmark.py')})
print(json.dumps(result,indent=2,sort_keys=True))
