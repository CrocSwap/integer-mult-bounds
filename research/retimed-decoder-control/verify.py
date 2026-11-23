#!/usr/bin/env python3
"""Fresh-cache immutable receipt replay; CubeJerry, OpenAI-assisted, Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent

def require(ok,message):
    if not ok:raise ValueError(message)

def run(mode):
    frozen=json.loads((ROOT/'PUBLICATION-FREEZE.json').read_text())
    for name,digest in frozen['files'].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,
                'frozen scientific/source/review file differs: '+name)
    for optimized in (False,True):
        with tempfile.TemporaryDirectory(prefix='decoder-control-replay-') as folder:
            scratch=Path(folder);output=scratch/'actual.json'
            argv=[sys.executable,'-X','pycache_prefix='+str(scratch/'bytecode')]
            if optimized:argv.append('-O')
            argv.append('-B')
            if mode=='author':
                argv += [str(ROOT/'check.py'),'--output',str(output)]
                evidence=ROOT/'evidence'/('OPTIMIZED.json' if optimized else 'RESULT.json')
            else:
                argv += [str(ROOT/'review/review.py'),'--package',str(ROOT),'--output',str(output)]
                evidence=ROOT/'review'/('RESULT-OPT.json' if optimized else 'RESULT.json')
            result=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=285,check=False)
            require(result.returncode==0,result.stdout+result.stderr)
            require(output.is_file(),'fresh child receipt missing')
            require(json.loads(output.read_text())==json.loads(evidence.read_text()),
                    'fresh receipt differs: '+str(evidence))
    print('PASS_DECODER_CONTROL_'+mode.upper()+'_NORMAL_OPTIMIZED_FRESH_CACHE')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',required=True,choices=('author','independent'))
    run(parser.parse_args().mode)
