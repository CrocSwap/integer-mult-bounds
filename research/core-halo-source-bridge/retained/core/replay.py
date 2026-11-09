"""Bounded registered replay, including one complete actual physical word.

Each child uses a fresh bytecode namespace and the requested optimization mode.
The extended eight-context physical word is an explicit separate command.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,message):
    if not ok:raise ValueError(message)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--reviews-only',action='store_true')
    args=ap.parse_args();started=time.monotonic();records=[]
    for manifest in ('INDEPENDENT-SOURCES.json','EXECUTION-SOURCES.json'):
        for row in json.loads((HERE/manifest).read_text())['files']:
            raw=(HERE/row['path']).read_bytes()
            need(len(raw)==row['bytes'] and sha256(raw).hexdigest()==row['sha256'],
                 'unchanged execution/checker source '+row['path'])
    with tempfile.TemporaryDirectory(prefix='complete-core-check-') as scratch:
        scratch=Path(scratch)
        def run(name,*arguments):
            cache=scratch/('pycache-'+str(len(records)))
            argv=[sys.executable,'-B','-X','pycache_prefix='+str(cache)]
            if sys.flags.optimize:argv+=['-O' if sys.flags.optimize==1 else '-OO']
            argv += [str(HERE/name),*(str(x) for x in arguments)]
            before=time.monotonic()
            result=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True,check=False)
            if result.returncode:
                sys.stderr.write(result.stdout+result.stderr)
                raise ValueError('failed complete-Core check: '+name)
            records.append(dict(check=name,seconds=time.monotonic()-before,
                                stdout_sha256=sha256(result.stdout.encode()).hexdigest()))
            print('PASS '+name,flush=True)
            return result.stdout
        run('check_source_compatibility.py')
        run('check_budget.py')
        run('check_allocation.py','--source-package',HERE)
        run('check_source_join.py','--source-package',HERE)
        run('review/independent_core_transport.py',HERE/'physical_join.py')
        run('review/independent_original_route.py','--package',HERE,
            '--output',scratch/'original-route.json')
        physical=scratch/'physical.json'
        if args.reviews_only:
            physical=HERE/'PHYSICAL-OPTIMIZED-RESULT.json'
        else:
            run('verify.py','--output',physical)
            observed=json.loads(physical.read_text())
            retained=json.loads((HERE/'PHYSICAL-OPTIMIZED-RESULT.json').read_text())
            ignored={'seconds','online_seconds'}
            need({k:v for k,v in observed.items() if k not in ignored}==
                 {k:v for k,v in retained.items() if k not in ignored},
                 'complete replay matches all retained scientific and machine-operation fields')
        run('check_physical_result.py','--source-package',HERE,'--receipt',physical)
        print(json.dumps(dict(status='PASS_COMPLETE_CORE_PACKAGE',
            actual_physical_replayed=not args.reviews_only,
            optimization=sys.flags.optimize,checks=records,
            seconds=time.monotonic()-started,
            extended_original_physical_replayed=False,no_new_kappa=True),indent=2,sort_keys=True))

if __name__=='__main__':main()
