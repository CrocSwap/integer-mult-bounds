#!/usr/bin/env python3
"""Optional candidate generation, never an admission proof and never default replay.
Produces a new exact-normalizer catalogue through the pinned retained compiler;
verify.py independently verifies it. Apache-2.0; source/compiler credit retained.
"""
from pathlib import Path
import argparse,atexit,json,sys,tempfile,time
HERE=Path(__file__).resolve().parent
_cache=tempfile.TemporaryDirectory(prefix='4610-generation-bytecode-');atexit.register(_cache.cleanup)
sys.pycache_prefix=_cache.name;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
from checks import source

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=HERE.parents[1]);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--limit-pairs',type=int);a=ap.parse_args()
    source.need(__debug__,'optimized generation unsupported');source.bootstrap(a.repo,HERE/'SOURCES.json')
    from checks import paid
    check,C,c,pairs,counts=paid.setup();a.catalog=a.output
    out=paid.generate(a,check,C,c,pairs,counts)
    print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()
