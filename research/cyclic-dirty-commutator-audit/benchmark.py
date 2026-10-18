#!/usr/bin/env python3
"""Same-input Fraction prototype timing; no fast-arithmetic performance claim."""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import statistics
import subprocess
import tempfile
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def need(ok,message):
    if not ok:
        raise ValueError(message)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    E=load('benchmark_echo',HERE/'echo.py')
    source=json.loads((HERE/'SOURCE.json').read_text())
    nf=16;length=8;bits=1024;beta=F(1,2);repetitions=3
    factors=[(i%2==0,(F(1,4),F((-1)**i,8)),F(3 if i==0 else 1)) for i in range(nf)]
    phases=[(F(1),F(0)),(F(0),F(1)),(F(3,5),F(4,5))]
    phases=[phases[i%3] for i in range(length)]
    before=[[(F(7+2*i+j,4),F(7-3*i-j,8)) for i in range(length)] for j in range(nf+1)]
    rows=[]
    with tempfile.TemporaryDirectory(prefix='echo-benchmark-') as temp:
        root=Path(temp)
        for name,digest in source['files'].items():
            result=subprocess.run(['git','show',source['commit']+':'+source['package']+'/'+name],cwd=ROOT,capture_output=True)
            need(result.returncode==0 and hashlib.sha256(result.stdout).hexdigest()==digest,'pinned source '+name)
            (root/name).write_bytes(result.stdout)
        D=load('benchmark_binary',root/'dirty.py')
        expected=D.exact_operator(before[0],factors,phases,1)
        for label,fanout in (('pinned binary',2),('echo fanout 8',8),('flat echo',nf)):
            depth,N=E.resources(nf,fanout)
            seconds=[]
            for _ in range(repetitions):
                arrays=copy.deepcopy(before[:depth+2]);saved=copy.deepcopy(arrays)
                start=time.perf_counter()
                if fanout==2:
                    stats=dict(leaves=0,scalar_steps=0)
                    D.compose(*arrays[:2],factors,arrays[2:],phases,beta,bits,1,stats=stats)
                else:
                    stats=E.compose(D,*arrays[:2],factors,arrays[2:],phases,beta,bits,1,fanout=fanout)
                seconds.append(time.perf_counter()-start)
                need(stats['leaves']==N,'benchmark count')
                need(arrays[0]==saved[0] and arrays[2:]==saved[2:],'benchmark restoration')
                need(all(D.c.norm2(D.c.sub(D.c.sub(y,y0),z))<=F(1,1<<64) for y,y0,z in zip(arrays[1],saved[1],expected)),'benchmark 32-bit accuracy')
            rows.append(dict(method=label,borrowed_arrays=depth,leaf_calls=N,seconds=seconds,median_seconds=statistics.median(seconds)))
    args.out.write_text(json.dumps(dict(python=platform.python_version(),platform=platform.platform(),factors=nf,length=length,bits=bits,repetitions=repetitions,results=rows,scope='Same source, target, phases, factors, precision and prefix of a common scratch pool. Unequal scratch counts are explicit. Fraction prototype timing only; no practical multiplication speedup claim.'),indent=2)+'\n')
    for row in rows:
        print(row['method'],row['leaf_calls'],'calls',row['borrowed_arrays'],'arrays',round(row['median_seconds'],4),'median seconds')


if __name__=='__main__':
    main()
