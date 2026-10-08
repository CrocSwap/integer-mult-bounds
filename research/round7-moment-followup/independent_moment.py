#!/usr/bin/env python3
"""Independent rational moment enclosures for the frozen kappa7 histogram.

Uses log scaling by3/2 and48 atanh terms, followed by degree12 exponential
Taylor bounds. No upstream arithmetic implementation or floating evaluation is
imported. This verifies an analytic inequality conditional on the input histogram.
"""
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse,json,subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]/'research/deferred-signed/swapnil-round7'
PIN='741e7aa078392553815df7926ee17ac5e25a8c38'
LOG_SCALE=10**64
SUM_SCALE=10**64

def down(x,scale):return Q(x.numerator*scale//x.denominator,scale)
def up(x,scale):return Q(-((-x.numerator*scale)//x.denominator),scale)

def atanh_twice(z):
    assert 0<=z<=Q(1,5)
    term=z;partial=Q(0)
    for j in range(48):
        partial+=term/Q(2*j+1);term*=z*z
    # term=z^97; every later denominator is at least97.
    return 2*partial,2*partial+2*term/(97*(1-z*z))

@lru_cache(None)
def logarithm(x):
    x=Q(x);assert x>=1
    count=0;y=x
    while y>=Q(3,2):y*=Q(2,3);count+=1
    assert 1<=y<Q(3,2)
    L,U=atanh_twice(Q(1,5));l,u=atanh_twice((y-1)/(y+1))
    lo=count*L+l;hi=count*U+u
    return down(lo,LOG_SCALE),up(hi,LOG_SCALE),dict(scale_count=count,reduced_argument=str(y))

def exponential(xlo,xhi):
    assert 0<=xlo<=xhi<1
    lo=hi=Q(1);tl=tu=Q(1)
    for j in range(1,13):
        tl*=xlo/j;tu*=xhi/j;lo+=tl;hi+=tu
    # Tail begins at degree13; all successive ratios are at most xhi/14.
    tail=(tu*xhi/13)/(1-xhi/14)
    return lo,hi+tail

def moment(c,a,kind):
    a=Q(a);assert 0<=a<1 and kind in ('exponential','reciprocal')
    lower=upper=Q(0);terms=[]
    for t,count in c['hist']:
        assert type(t)is int and type(count)is int and 0<t<c['m'] and count>0
        l,u,meta=logarithm(Q(c['m'],t));xlo,xhi=a*l,a*u
        if kind=='exponential':lo,hi=exponential(xlo,xhi)
        else:
            assert xhi<1
            lo,hi=1/(1-xlo),1/(1-xhi)
        weight=Q(count*t,c['m']*c['W'])
        termlo=down(weight*lo,SUM_SCALE);termhi=up(weight*hi,SUM_SCALE)
        lower+=termlo;upper+=termhi
        terms.append(dict(width=t,multiplicity=count,weight=str(weight),log_lower=str(l),log_upper=str(u),
            log_scaling=meta,term_lower=str(termlo),term_upper=str(termhi)))
    return dict(kind=kind,a=str(a),lower=str(lower),upper=str(upper),
        below_one=upper<1,above_one=lower>1,terms=terms)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',action='append',required=True,help='LABEL=KIND:CLAIM:SAVING; KIND exp/recip, CLAIM accept/reject/report')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    from check_sources import check_sources
    check_sources()
    source=ROOT/'lean/round7-histograms.json'
    data=json.loads(source.read_text());c=data['bit']
    assert (c['m'],c['W'],c['s'])==(529,108516254,57403754177)
    assert sum(t*n for t,n in c['hist'])==c['s']<c['m']*c['W']
    assert len({t for t,n in c['hist']})==len(c['hist'])
    # Exact controls independent of the candidate thresholds.
    assert logarithm(Q(1))[:2]==(0,0)
    assert exponential(Q(0),Q(0))==(1,1)
    zero=moment(c,Q(0),'exponential')
    assert Q(zero['lower'])<=Q(c['s'],c['m']*c['W'])<=Q(zero['upper'])<1
    results={}
    for case in args.case:
        label,spec=case.split('=',1);kind,claim,saving=spec.split(':',2)
        assert label not in results and kind in ('exp','recip') and claim in ('accept','reject','report')
        result=moment(c,Q(saving),'exponential' if kind=='exp' else 'reciprocal')
        if claim=='accept':assert result['below_one'],label
        if claim=='reject':assert result['above_one'],label
        result['requested_claim']=claim;results[label]=result
        print(label,claim,'PASS','1-upper='+str(1-Q(result['upper'])),'lower-1='+str(Q(result['lower'])-1),flush=True)
    output=dict(status='PASS independent directed rational moment checks',pin=PIN,
        histogram_path=str(source.relative_to(HERE.parents[1])),histogram_sha256=sha256(source.read_bytes()).hexdigest(),
        checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        m=c['m'],W=c['W'],rank_mass=c['s'],rank_deficit=c['m']*c['W']-c['s'],
        method=dict(log_scale='3/2',atanh_terms=48,exponential_degree=12,directed_denominator=10**64),
        controls=dict(log_one=True,exp_zero=True,moment_zero_equals_normalized_rank=True),cases=results,
        scope='Analytic moment inequality for a fixed finite histogram only; neither physical construction nor all-size multiplication theorem is proved here.')
    assert not args.output.exists(),'Preserve prior exact audit receipts'
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':main()
