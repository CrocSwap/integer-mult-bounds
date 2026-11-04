#!/usr/bin/env python3
"""Rational outward tables and a Jensen tail for all binary root patterns."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,importlib.util,hashlib,argparse
H=Path(__file__).resolve().parent
ROOT=H.parents[2]
ENGINE=H/'inputs'/'interval_engine.py'
spec=importlib.util.spec_from_file_location('root_bound_intervals',ENGINE);E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
K=Q('.00424927762');N=80;GRID=10**12

def floor(x):return x.numerator//x.denominator
def ceil(x):return -floor(-x)

def main():
    global K,N
    ap=argparse.ArgumentParser();ap.add_argument('--kappa',default=str(K));ap.add_argument('--max-leaves',type=int,default=N);ap.add_argument('--prefix',default='PATTERN');args=ap.parse_args()
    K=Q(args.kappa);N=args.max_leaves;assert all(c.isalnum()or c in '_-'for c in args.prefix)
    src=H/'inputs/BIT-NATIVE-WORD.json.gz';w=json.loads(gzip.decompress(src.read_bytes()));ff=w['frames']
    P=Counter(abs(ff[str(e[2])]['dim']-ff[str(e[3])]['dim'])for e in w['program']if e[0]=='MOVE')
    T=Counter(abs(ff[str(w['final'][i])]['dim']-ff[str(w['start'][i])]['dim'])for i in range(222,w['public']))
    lo=(E.moment(P,1-K)[0]-E.moment(T,1-K)[1])/111;Li=floor(lo*GRID)
    head=[GRID]+[ceil(E.power(1+7*n,1-K)[1]*GRID)for n in range(1,N+1)]
    body=[0]+[floor(E.power(7*n,1-K)[0]*GRID)for n in range(1,N+1)]
    C=[0]*(N+1)
    for n in range(2,N+1):C[n]=min(C[a]+C[n-a]for a in range(1,n))+2*body[n]+GRID-2*head[n]
    patterns=json.loads((H/'ALL-SITE-PATTERNS.json').read_text())['patterns']
    lines=[f'{N} {len(patterns)} {GRID} {Li}']+[' '.join(map(str,(head[n],body[n],C[n])))for n in range(N+1)]+[' '.join(map(str,p['masks']))for p in patterns]
    (H/(args.prefix+'-BOUND-TABLES.txt')).write_text('\n'.join(lines)+'\n')
    # Delete each charged extra stage placement from an arbitrary output.
    # Concavity says this only increases the margin. The remaining six
    # outputs have total body mass14f, so Jensen gives the displayed tail.
    x=E.divide(E.power(3+7*N,1-K),E.power(3,1-K))
    tail=6*x[1]-N*(lo-1)-7
    xp=E.divide(E.power(3+7*N,-K),E.power(3,-K))
    derivative=14*(1-K)*xp[1]-(lo-1)
    assert tail<0 and derivative<0
    out=dict(status='PASS_RATIONAL_ROOT_FAMILY_TAIL',kappa=str(K),tail_starts_at=N,integer_grid=GRID,native_deficit_lower=str(lo),tail_margin_upper=str(tail),tail_derivative_upper=str(derivative),tail_margin_display=E.display((tail,tail)),tail_derivative_display=E.display((derivative,derivative)),formula='B(f)=6(1+7f/3)^(1-kappa)-f(L-1)-7',proof='Every binary node costs at least -1. Removing a charged extra stage placement can only increase productive-minus-paid moment by concavity. Six remaining outputs have total body rank14f; Jensen bounds their moment. B is concave, so B(N)<0 and Bprime(N)<0 exclude every realf>=N.',interval_engine_sha256=hashlib.sha256(ENGINE.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),scope='All six-field seven-query roots with four full sites, common bodyrank7, rank2/3 stage projectors, independent binary children, no additional helper exchange or refund.')
    (H/(args.prefix+'-TAIL-BOUND.json')).write_text(json.dumps(out,indent=2)+'\n');print(out['tail_margin_display'],out['tail_derivative_display'])

if __name__=='__main__':main()
