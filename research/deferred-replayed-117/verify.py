"""Verify frozen source pins, exact accounting, controls and optional full replay."""
import sys
assert not sys.flags.optimize, 'Assertions must remain enabled'
sys.dont_write_bytecode = True
import argparse, hashlib, json, os, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--full',action='store_true');args=ap.parse_args()
    manifest=json.loads((HERE/'SOURCE.json').read_text())
    for base,key in ((HERE,'package_files'),(ROOT,'repository_files')):
        for name,expected in manifest[key].items():
            assert hashlib.sha256((base/name).read_bytes()).hexdigest()==expected, name
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('CX_PRODUCER',None)
    run=lambda cmd:subprocess.run([sys.executable,*cmd],cwd=ROOT,env=env,check=True)
    frozen={n:json.loads((HERE/n).read_text()) for n in ('complex-profile.json','bit-profile.json','certificate.json')}
    run([str(HERE/'certificate.py')]);run([str(HERE/'test_unit_readouts.py')])
    if args.full:
        run([str(HERE/'complex_deferred.py')]);run([str(HERE/'bit_round7.py'),str(ROOT/'research/cube-deferred/inputs')])
        run([str(HERE/'certificate.py')]);run([str(HERE/'audit.py'),'--source',str(HERE/'complex_deferred.py'),'--check',str(HERE/'audit-result.json')])
    for name,data in frozen.items():assert json.loads((HERE/name).read_text())==data, name
    print('PASS deferred PR117 source pins, exact unit-shear accounting and controls'+(' with full physical/reflected replay' if args.full else ''))
if __name__=='__main__':main()
