"""Run each scientific scope against the installed candidate and record its actual exit."""
from datetime import datetime,timezone
from pathlib import Path
from subprocess import run
from hashlib import sha256
import json
import sys
import time
from shutil import copyfile

root=Path(__file__).resolve().parent
candidate=root/'successor'
runtime=candidate/'runtime'
peer=candidate/'peer/research/frequency-weighted-native-multiplier'
log=candidate/'logs';log.mkdir(exist_ok=True)
scopes={
    'invoice':[str(peer/'receipt.py'),str(runtime)],
    'independent_price':[str(root/'check_six_price.py'),str(runtime)],
    'placement':[str(peer/'check_placement.py'),str(runtime)],
    'calendar':[str(peer/'check_calendar.py'),str(runtime)],
    'ownership':[str(peer/'check_ownership.py'),str(runtime)],
    'exterior':[str(peer/'check_exterior.py'),str(runtime)],
    'nested':[str(peer/'check_nested.py'),str(runtime)],
    'raw':[str(peer/'check_raw.py'),str(runtime)],
    'product':[str(root/'check_successor_tiers.py'),str(runtime),'product'],
    'stages':[str(root/'check_successor_tiers.py'),str(runtime),'stages'],
    'cutoff':[str(root/'check_successor_cutoff.py'),str(runtime)],
    'corrupted_owner':[str(root/'check_corrupt_owner.py'),str(runtime)],
    'ordinary_floor':[str(root/'check_six_ordinary.py'),str(runtime)],
    'setup':[str(peer.parent/'tiered-native-multiplier/check_serial_setup.py')]}
stamp=lambda:datetime.now(timezone.utc).isoformat(timespec="microseconds")
failures=[]
for mode in sys.argv[1:] or list(scopes):
    if (log/f'{mode}.json').exists():
        previous=json.loads((log/f'{mode}.json').read_bytes())
        attempt=log/'attempts'/previous['started_at'].replace(':','-')
        attempt.mkdir(parents=True,exist_ok=True)
        for ext in ('json','err','out'):copyfile(log/f'{mode}.{ext}',attempt/f'{mode}.{ext}')
    start=stamp();tick=time.monotonic()
    with (log/f'{mode}.out').open('wb') as stdout,(log/f'{mode}.err').open('wb') as stderr:
        result=run([sys.executable,'-IB',*scopes[mode]],stdout=stdout,stderr=stderr)
    end=stamp(); elapsed=time.monotonic()-tick
    status=dict(mode=mode,code=result.returncode,started_at=start,finished_at=end,elapsed=elapsed,
                output_sha256=sha256((log/f'{mode}.out').read_bytes()).hexdigest())
    (log/f'{mode}.json').write_text(json.dumps(status,indent=2)+'\n')
    print(mode,result.returncode,round(elapsed,2),flush=True)
    if result.returncode:failures.append(mode)
if failures:raise SystemExit("Failed scopes: "+", ".join(failures))
