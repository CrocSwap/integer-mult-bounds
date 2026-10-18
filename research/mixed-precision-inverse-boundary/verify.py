#!/usr/bin/env python3
"""Exact mixed-grid inverse boundary; woklerx with OpenAI Codex, Apache-2.0."""
import hashlib
import importlib.util
import itertools
import json
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def need(ok,message):
    if not ok: raise ValueError(message)
def round_grid(value,bits):
    value=value*(1<<bits)+F(1,2)
    return F(value.numerator//value.denominator,1<<bits)
def witness(a,p,w):
    q=a*(1<<(w-p))
    if q.denominator==1: return None
    d=q.denominator
    k=(pow(q.numerator,-1,d)*(d//2))%d
    return F(k,1<<p)
def run():
    for entry in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if entry['usage']=='input':
            need(hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256'],'source drift')
    spec=importlib.util.spec_from_file_location('mixed_grid_vendor',ROOT/'research/dirty-prefix-precision/vendor/pr628/dirty.py')
    vendor=importlib.util.module_from_spec(spec); spec.loader.exec_module(vendor)
    cases=aligned=counterexamples=0
    for numerator in range(-31,32):
        for denominator in range(1,32):
            a=F(numerator,denominator)
            for p in range(5):
                for w in range(p,p+5):
                    x=witness(a,p,w)
                    for v in (w+1,w+2,w+4):
                        cases+=1
                        if x is None:
                            aligned+=1
                            for k in (-3,0,5):
                                value=a*F(k,1<<p)
                                need(round_grid(value,w)==round_grid(value,v)==value,'aligned criterion')
                        else:
                            counterexamples+=1
                            lo=vendor.c.rounded((a*x,F(0)),w)[0]
                            hi=vendor.c.rounded((a*x,F(0)),v)[0]
                            need(lo!=hi,'constructive modular counterexample')
                            need(lo==round_grid(a*x,w) and hi==round_grid(a*x,v),'independent source rounding')
    # Independently enumerate each whole residue period, rather than using
    # the modular inverse witness construction, for reduced q=u/d.
    periods=0
    for d in range(1,32):
        for u in range(-31,32):
            q=F(u,d)
            for extra in (1,2,4):
                equal=all(round_grid(q*k,0)==round_grid(q*k,extra) for k in range(q.denominator))
                need(equal==(q.denominator==1),'complete residue period criterion')
                periods+=1
    # Componentwise matrix criterion: test a complete small coefficient
    # alphabet against every pair of source residues for the common period6.
    alphabet=[F(-1,3),F(0),F(1,2),F(1),F(3,2)]
    matrix_cases=0
    for a,b,c,d in itertools.product(alphabet,repeat=4):
        aligned_matrix=all((2*q).denominator==1 for q in (a,b,c,d))
        same=True
        for x,y in itertools.product(range(6),repeat=2):
            for value in (a*x+b*y,c*x+d*y):
                same &= round_grid(value,1)==round_grid(value,2)
        need(same==aligned_matrix,'matrix grid criterion')
        matrix_cases+=1
    fs=[(False,(F(1,4),F(0)),F(1))]; phases=[vendor.c.ONE]
    x=[vendor.c.ONE]; y=[vendor.c.ZERO]
    vendor.compose(x,y,fs,[],phases,F(1,2),4,1)
    forward=y.copy()
    vendor.compose(x,y,fs,[],phases,F(1,2),5,1,-1)
    need(forward==[(F(-5,16),F(0))] and y==[(F(1,32),F(0))],'actual source counterexample')
    actual_failures=actual_cases=0
    for k,fine,direction in itertools.product(range(-16,17),range(5,9),(-1,1)):
        source=[(F(k,16),F(0))]; target=[(F(5,16),F(-3,16))]
        for bits in (4,fine):
            sx=source.copy(); ty=target.copy()
            vendor.compose(sx,ty,fs,[],phases,F(1,2),bits,direction)
            vendor.compose(sx,ty,fs,[],phases,F(1,2),bits,direction,-1)
            need(sx==source and ty==target,'same-grid positive control')
        sx=source.copy();ty=target.copy()
        vendor.compose(sx,ty,fs,[],phases,F(1,2),4,direction)
        vendor.compose(sx,ty,fs,[],phases,F(1,2),fine,direction,-1)
        need(sx==source,'source restoration remains exact')
        actual_cases+=1; actual_failures+=ty!=target
    need(actual_failures>0,'precision mutation not detected')
    # A zero-only smoke input cannot establish the quantified criterion.
    need(round_grid(F(1,3)*0,1)==round_grid(F(1,3)*0,2),'zero smoke control')
    need(round_grid(F(1,3),1)!=round_grid(F(1,3),2),'nonzero control')
    return dict(status='PASS_MIXED_PRECISION_INVERSE_BOUNDARY',rational_grid_cases=cases,
                aligned_cases=aligned,constructive_counterexamples=counterexamples,
                complete_residue_period_cases=periods,matrix_alphabet_cases=matrix_cases,
                pinned_leaf=dict(coarse_bits=4,fine_inverse_bits=5,forward_target=forward,
                                 residual=[(F(1,32),F(0))]),
                pinned_leaf_grid_pairs=actual_cases,mixed_grid_nonzero_residuals=actual_failures,
                same_grid_exact_inverse_controls=2*actual_cases,
                scope='Rational rounded-linear criterion plus actual fixed-source leaf counterexample; no current caller bug')
if __name__=='__main__':
    result=json.loads(json.dumps(run(),default=str)); receipt=HERE/'EXPECTED.json'
    if receipt.exists(): need(json.loads(receipt.read_text())==result,'receipt mismatch')
    print(json.dumps(result,indent=2,sort_keys=True))
