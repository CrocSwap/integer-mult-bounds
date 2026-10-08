#!/usr/bin/env python3
"""Freshly verify independent word axes and rank exact fixed-saving costs."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
from verify_words import axis, check_source, load_module


def run_one(job):
    name,h,word,out,profiler,upstream=job
    sys.dont_write_bytecode=True
    receipt=axis(Path(word),Path(out),Path(profiler),Path(upstream))
    return name,h,str(Path(out)/'verified-axis.json'),receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--upstream',type=Path,required=True)
    p.add_argument('--base',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--profiler',type=Path,required=True)
    p.add_argument('--saving',type=Q,required=True)
    p.add_argument('--workers',type=int,default=3)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    check_source(a.upstream.resolve())
    math=load_module('batch_exact_math',a.upstream.resolve()/'scripts/experiments/binary_frame_math.py')
    jobs=[]
    for directory in sorted(a.base.iterdir()):
        for h in (23,25):
            word=directory/f'h{h}'/'word.json.gz'
            if word.exists():
                jobs.append((directory.name,h,str(word.resolve()),str((a.output/directory.name/f'h{h}').resolve()),
                             str(a.profiler.resolve()),str(a.upstream.resolve())))
    rows=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        future={pool.submit(run_one,j):j for j in jobs}
        for f in as_completed(future):
            name,h,path,receipt=f.result()
            price=Q()
            for t,n in enumerate(receipt['profile']['blocks']):
                if t and n:
                    v=a.saving*math.logs(Q(575,t))[1]
                    price+=n*t*(1+v+v*v/(2*(1-v/3)))
            rows.append(dict(name=name,h=h,receipt=path,R=receipt['profile']['R'],
                             scalar_xors=receipt['replay']['elementary_xors'],fixed_saving=str(a.saving),
                             exact_internal_upper_price=str(price)))
            print('RANK',name,h,'price',float(price),flush=True)
            ordered=sorted(rows,key=lambda r:(r['h'],Q(r['exact_internal_upper_price'])))
            (a.output/'ranking.json').write_text(json.dumps(ordered,indent=2)+'\n')
    print('PASS verified axes',len(rows),flush=True)


if __name__=='__main__':
    main()
