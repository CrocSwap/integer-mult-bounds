"""Measure serial complete price replays in fresh Python processes."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--output',required=True)
args = parser.parse_args()
output = Path(args.output)
if output.exists():
    raise ValueError('Use a new benchmark output path')
runs = []
expected = None
for pair in range(3):
    for engine in (['baseline','certificate'] if pair%2 == 0 else ['certificate','baseline']):
        start = time.monotonic()
        process = subprocess.run([sys.executable,'-B',str(HERE/'run.py'),engine],
                                 text=True,capture_output=True,timeout=180)
        if process.returncode:
            raise RuntimeError(process.stderr)
        data = json.loads(process.stdout)
        receipt = data.pop('result')
        if expected is None:
            expected = receipt
        elif receipt != expected:
            raise ValueError('Complete price receipts differ')
        data.update(pair=pair,engine=engine,wall_seconds=time.monotonic()-start,
                    receipt_sha256=hashlib.sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest())
        runs.append(data)
        print(engine,data['seconds'],flush=True)
median = {k:statistics.median(r['wall_seconds'] for r in runs if r['engine'] == k)
          for k in ('baseline','certificate')}
result = {'status':'PASS_COMPLETE_PRICE_BENCHMARK','python':sys.version,'platform':platform.platform(),
          'runs':runs,'median_wall_seconds':median,'speedup':median['baseline']/median['certificate'],
          'source_sha256':{str(f.relative_to(HERE)):hashlib.sha256(f.read_bytes()).hexdigest()
                           for f in sorted(HERE.rglob('*')) if f.is_file() and
                           (f.suffix == '.py' or 'inputs' in f.relative_to(HERE).parts or f.name in ('BRACKET.json','SOURCES.json'))},
          'scope':'Complete source price/compiler/outer module with pinned native/caller inputs; no native replay or new kappa.'}
output.write_text(json.dumps(result,indent=2)+'\n')
