"""Five alternating fresh-process pairs of the complete native component."""
from pathlib import Path
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def benchmark(output):
    if output.exists() or output.resolve().is_relative_to(HERE):
        raise ValueError('Use a new output outside the package')
    runs = []
    for pair in range(5):
        for engine in ('baseline','candidate'):
            start = time.perf_counter()
            call = subprocess.run([sys.executable,'-I','-W','error','-B',str(HERE/'run.py'),engine],
                                  text=True,capture_output=True,timeout=120)
            wall = time.perf_counter()-start
            if call.returncode or call.stderr:
                raise RuntimeError(f'{engine}: {call.returncode}: {call.stderr}')
            result = json.loads(call.stdout)
            if runs and result['native'] != runs[0]['native']:
                raise ValueError('Scientific output differs')
            runs.append(dict(pair=pair,engine=engine,wall_seconds=wall,**result))
            print(engine,wall,flush=True)
    medians = {e:statistics.median(r['wall_seconds'] for r in runs if r['engine']==e)
               for e in ('baseline','candidate')}
    result = {'status':'PASS_COMPLETE_NATIVE_ALTERNATING_BENCHMARK','errors':0,
              'python':sys.version,'platform':platform.platform(),'runs':runs,
              'median_wall_seconds':medians,'fraction_reduction':1-medians['candidate']/medians['baseline'],
              'source_sha256':{str(f.relative_to(HERE)):hashlib.sha256(f.read_bytes()).hexdigest()
                               for f in sorted(HERE.rglob('*.py'))},
              'scope':'Complete native component only; fresh processes, exact full receipts; no multiplier runtime claim.'}
    with output.open('x') as handle:
        handle.write(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    if len(sys.argv)!=2:
        raise ValueError('Supply one new external JSON output')
    benchmark(Path(sys.argv[1]))
