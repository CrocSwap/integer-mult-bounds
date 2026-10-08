#!/usr/bin/env python3
"""Search-only exact profile screening; full source/dirty replay is omitted.

An accepted final candidate must subsequently run verify_words.py with its
actual words. This screen checks the literal frame-event correspondence and
exact fixed profiles, then ranks equal-role axes at one exact saving.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as Q
import json
from pathlib import Path
import subprocess
import sys
from verify_words import check_source,load_module


def run_one(job):
    name,h,word,out,profiler,upstream=job
    sys.dont_write_bytecode=True
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    prepare=load_module('screen_prepare',Path(upstream)/'scripts/experiments/binary_frame_profile_prepare.py').prepare
    transitions=output/'transitions.bin'
    prepared=prepare(Path(word),transitions)
    subprocess.run([profiler,str(transitions)],check=True,capture_output=True)
    profile=json.loads(Path(str(transitions)+'.profiles.json').read_text())
    assert profile['h']==h and profile['crt_disagreements']==0
    assert profile['rank_sum']==h*profile['R']+h*(h-1)
    receipt=dict(status='PROFILE SCREEN ONLY; full source/target/dirty replay not performed',
                 prepared=prepared,profile=profile,word=str(word))
    (output/'screened-axis.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return name,h,str(output/'screened-axis.json'),receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--upstream',type=Path,required=True);p.add_argument('--base',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--profiler',type=Path,required=True)
    p.add_argument('--saving',type=Q,required=True);p.add_argument('--workers',type=int,default=3)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    check_source(a.upstream.resolve())
    math=load_module('screen_math',a.upstream.resolve()/'scripts/experiments/binary_frame_math.py')
    jobs=[]
    for directory in sorted(a.base.iterdir()):
        for h in (23,25):
            word=directory/f'h{h}'/'word.json.gz'
            if word.exists():jobs.append((directory.name,h,str(word.resolve()),str((a.output/directory.name/f'h{h}').resolve()),str(a.profiler.resolve()),str(a.upstream.resolve())))
    rows=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        futures=[pool.submit(run_one,j) for j in jobs]
        for f in as_completed(futures):
            name,h,path,receipt=f.result();price=Q()
            for t,n in enumerate(receipt['profile']['blocks']):
                if t and n:
                    v=a.saving*math.logs(Q(575,t))[1]
                    price+=n*t*(1+v+v*v/(2*(1-v/3)))
            rows.append(dict(name=name,h=h,receipt=path,R=receipt['profile']['R'],
                             word=receipt['word'],fixed_saving=str(a.saving),exact_internal_upper_price=str(price)))
            ordered=sorted(rows,key=lambda r:(r['h'],Q(r['exact_internal_upper_price'])))
            (a.output/'ranking.json').write_text(json.dumps(ordered,indent=2)+'\n')
            print('SCREEN',name,h,float(price),flush=True)
    print('PASS profile-only screens',len(rows),'full final replay remains required',flush=True)


if __name__=='__main__':main()
