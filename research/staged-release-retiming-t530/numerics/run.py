#!/usr/bin/env python3
"""Offline exact moment and transfer check; Python standard library only."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, tempfile
D=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args()
for name,digest in json.loads((D/'INPUT-SHA256.json').read_text()).items():
 if hashlib.sha256((D/name).read_bytes()).hexdigest()!=digest:raise ValueError('changed capsule input '+name)
out=a.out.resolve() if a.out else Path(tempfile.mkdtemp(prefix='retimed-numerics-'))
if out==D or D in out.parents:raise ValueError('output must be outside package')
if a.out and out.exists():raise ValueError('choose a fresh output directory')
out.mkdir(parents=True,exist_ok=True)
if (out/'MOMENT.json').exists() or (out/'outer').exists():raise ValueError('choose a fresh output directory')
subprocess.run([sys.executable,'-B',str(D/'verify_moment.py'),'--repo',str(D/'vendor-repo'),'--t530',str(D/'t530'),'--words',str(D/'words'),'--out',str(out/'MOMENT.json')],check=True)
subprocess.run([sys.executable,'-B',str(D/'verify_outer.py'),'--repo',str(D/'vendor-repo'),'--t530',str(D/'t530'),'--moment',str(out/'MOMENT.json'),'--out',str(out/'outer')],check=True)
print('Fresh exact arithmetic evidence:',out)
