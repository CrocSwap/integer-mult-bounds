#!/usr/bin/env python3
"""Portable exact physical and moment certificate for the selected fused word."""
from fractions import Fraction as Q
from pathlib import Path
import gzip
import json
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent;PACKAGE=HERE.parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(PACKAGE/'arithmetic'));sys.dont_write_bytecode=True
from interval_moment import saving_grid


def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [js(v) for v in x]
    return x


def main():
    assert not sys.flags.optimize
    candidate=PACKAGE/'selected/complex'
    with tempfile.TemporaryDirectory(prefix='paired-cube-exact-') as tmp:
        out=Path(tmp)/'physical.json'
        run=subprocess.run([sys.executable,'-B',str(HERE/'physical.py'),'--candidate',str(candidate),'--source',str(ROOT),'--out',str(out)],text=True,capture_output=True)
        if run.returncode:raise ValueError(run.stdout+run.stderr)
        physical=json.loads(out.read_text())
    physical.pop('seconds',None);physical.pop('maxrss',None)
    physical['source_sha256']={str(Path(k).resolve().relative_to(ROOT)):v for k,v in physical['source_sha256'].items()}
    raw=json.loads(gzip.decompress((candidate/'profile-before.json.gz').read_bytes()))
    paid=physical['physical']
    row={k:raw[k] for k in ('h','v','c','q','matched','total_M_operations','loss')}
    row.update({k:paid[k] for k in ('m','W_per_vertex','rank_per_vertex','deficit_per_vertex','child_histogram')})
    row.update(R=paid['physical_R'],scalar_role_reserve=raw['R'],reuse_pairs=paid['pairs'],maxchild=max(map(int,paid['child_histogram'])))
    p=dict(m=row['m'],W=row['W_per_vertex'],N=row['deficit_per_vertex'],L=0,total_rank=row['rank_per_vertex'],maxchild=row['maxchild'],child_multiplicities=row['child_histogram'])
    moment=saving_grid(p,10**18)
    assert moment['accepted']['saving']==Q(297370240363723,5*10**17)
    moment['complex_saving']=moment['accepted']['saving']
    moment['scope']='Strict contraction and adjacent point exclusion for this fixed complete complex profile.'
    print(json.dumps(js(dict(status='PASS',profile=row,physical=physical,moment=moment)),sort_keys=True))


if __name__=='__main__':main()
