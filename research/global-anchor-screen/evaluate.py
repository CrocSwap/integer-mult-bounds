#!/usr/bin/env python3
"""Exact finite moment and inherited assembly for alternate clearing words.

Consumes regenerated fixed-I+J profile arrays; unchanged PR62 geometry and
PR48/PR57 arithmetic retained with their existing provenance and assumptions.
Prepared with substantial OpenAI Codex assistance. No independent theorem.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import importlib.util
import json
import math

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('pair_verify',ROOT/'research/pair-assembly/frame/frame_verify.py')
verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)

def evaluate(paths,prefix):
    axes=[json.loads(Path(path).read_text()) for path in paths]
    words=json.loads((ROOT/'research/pair-assembly/frame/frame-compiler.json').read_text())
    p=verify.profile(axes,words)
    rows=p['child_multiplicities'];m=p['m'];W=p['W']
    lo,hi=0.,0.001
    for _ in range(60):
        mid=(lo+hi)/2
        if sum(n*(t/m)**(1-mid)/W for t,n in rows.items())<1:
            lo=mid
        else:
            hi=mid
    candidate=math.floor(lo*10**11)
    while verify.arithmetic.moment(m,W,rows,Q(candidate,10**11))['strict_gap']<=0:
        candidate-=1
    AB=Q(candidate,10**11)
    moment=verify.arithmetic.moment(m,W,rows,AB)
    excluded=verify.arithmetic.moment(m,W,rows,AB+Q(1,10**11))
    bridge=json.loads((verify.OLD/'certificate.json').read_text())['finite_bridge']
    bridge['bit']['W']=W
    k=candidate
    while True:
        try:
            assembled=verify.balanced.assembly(bridge,AB,Q(k,10**11),a_complex=Q(717,10**7))
            break
        except AssertionError:
            k-=1
    KAPPA=Q(k,10**11)
    try:
        verify.balanced.assembly(bridge,AB,KAPPA+Q(1,10**11),a_complex=Q(717,10**7))
        next_kappa_grid_fails=False
    except AssertionError:
        next_kappa_grid_fails=True
    assert next_kappa_grid_fails
    assert moment['strict_gap'] > 0 and excluded['lower'] > 1
    record=dict(scope='Conditional finite changed-word result; inherited theorem and transfer assumptions retained.',
                bit_saving=AB,kappa=KAPPA,exact_moment=moment,
                next_bit_grid_lower=excluded['lower'],next_kappa_grid_fails=next_kappa_grid_fails,profile=p,assembly=assembled,
                profile_files=[f'{prefix}profiles-{h}.json' for h in (23,25)])
    target=HERE/f'{prefix}arithmetic.json'
    target.write_text(json.dumps(verify.arithmetic.js(record),indent=2)+'\n')
    for h,axis in zip((23,25),axes):
        (HERE/f'{prefix}profiles-{h}.json').write_text(json.dumps(axis,indent=2)+'\n')
    print(json.dumps(dict(numerical_root=lo,bit_saving=str(AB),kappa=str(KAPPA),
                         strict_gap=float(moment['strict_gap']),next_bit_lower_excess=float(excluded['lower']-1),
                         constraints=len(assembled['constraints']),margins=len(assembled['margins'])),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('h23');p.add_argument('h25');p.add_argument('--prefix',default='')
    a=p.parse_args();evaluate((a.h23,a.h25),a.prefix)
