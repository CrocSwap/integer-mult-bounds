#!/usr/bin/env python3
"""Rebuild the credited bit word and selected complex graph in scratch."""
import sys
if not __debug__:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import argparse,os,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
    work=a.work.resolve();work.mkdir(parents=True,exist_ok=True)
    parent=ROOT/'research/stopped-pairtree'
    jobs=[(parent/'reproduce.py',['--work',work/'complex']),
          (parent/'physical_check.py',['--work',work/'complex']),
          (parent/'literal_check.py',['--work',work/'complex']),
          (parent/'interface_check.py',[]),
          (ROOT/'research/merged-span-frames/producer.py',['--h','25','--output',work/'bit'])]
    for script,args in jobs:
        subprocess.run([sys.executable,str(script),*map(str,args)],cwd=ROOT,check=True,
                       env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    print('PASS freshly rebuilt complex producer/matching and h25 physical bit word')

if __name__=='__main__':main()
