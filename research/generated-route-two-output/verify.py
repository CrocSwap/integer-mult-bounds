#!/usr/bin/env python3
"""Fresh-cache publication replay. Jerry Chen / CubeJerry, OpenAI-assisted."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent

def require(ok,message):
    if not ok:
        raise ValueError(message)

def run(mode):
    frozen=json.loads((ROOT/'PUBLICATION-FREEZE.json').read_text())
    for name,expected in frozen['files'].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,
                'frozen scientific/review file differs: '+name)
    for optimized in (False,True):
        with tempfile.TemporaryDirectory(prefix='two-output-review-') as cache:
            argv=[sys.executable,'-I','-X','pycache_prefix='+cache]
            if optimized:
                argv.append('-O')
            argv.append('-B')
            if mode=='author':
                argv.append(str(ROOT/'check.py'))
                evidence=ROOT/('EVIDENCE-OPT.json' if optimized else 'EVIDENCE.json')
            else:
                argv += [str(ROOT/'review/independent.py'),'--package',str(ROOT)]
                evidence=ROOT/'review'/('EVIDENCE-OPTIMIZED.json' if optimized else 'EVIDENCE.json')
            result=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=110,check=False)
            require(result.returncode==0,result.stdout+result.stderr)
            require(json.loads(result.stdout)==json.loads(evidence.read_text()),
                    'fresh receipt differs: '+str(evidence))
    print('PASS_TWO_OUTPUT_'+mode.upper()+'_NORMAL_OPTIMIZED_FRESH_CACHE')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',required=True,choices=('author','independent'))
    run(parser.parse_args().mode)
