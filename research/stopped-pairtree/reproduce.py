#!/usr/bin/env python3
"""Fresh parent producers and selected integer-weighted pair tree, all in scratch."""
import sys
if not __debug__:
    raise RuntimeError('Assertions required')
sys.dont_write_bytecode = True
import argparse, json, os
from pathlib import Path
import shutil, subprocess
import producer

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT/'references/stopped-recursion/pr107'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    parent = work/'parent'
    shutil.copytree(ARCHIVE, parent, ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo'))
    for name in ('verify.py','test_controls.py'):
        subprocess.run([sys.executable, str(parent/'research/reversed-rational-centers'/name)],
                       cwd=parent, check=True, env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    receipt = producer.regenerate(work)
    assert receipt == json.loads((HERE/'producer-check.json').read_text()), 'Selected producer receipt differs'
    assert json.loads((work/'constructor.json').read_text()) == json.loads((HERE/'constructor.json').read_text())
    print('PASS parent PR104/107 reproduction and selected integer-weighted tree')

if __name__ == '__main__':
    main()
