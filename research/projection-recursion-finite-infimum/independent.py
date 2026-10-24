"""Separate normalized Fraction recurrence and exact stationary-weight check."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

P=Path(__file__).resolve().parent
ROOT=P.parents[1]

def check(ok, message):
    if not ok:
        raise ValueError(message)

def run():
    # Deliberately does not import core.py or its integer recurrence.
    src=json.loads((P/'SOURCES.json').read_text())
    live=[v for v in src['files'] if v.get('usage')=='input']
    check(len(live)==2,'source list')
    for v in live:
        check(hashlib.sha256((ROOT/v['path']).read_bytes()).hexdigest()==v['sha256'],'source bytes')
    seed=(0,27456,48576,68320,86592)
    r=[Q(v,seed[1]) for v in seed]
    cert=[]
    for k in range(4,15):
        if k>4:
            M=2**k;den=Q(2*M*M-3*M-2,2);previous=r;r=[]
            for index in range(k+1):
                x=2**index
                coefficients=(M*M-1+M*(Q(1,x)-x),M*(Q(3,2)+Q(x,2)-Q(2,x)),M*(Q(x,2)-Q(3,2)+Q(1,x)))
                r.append(sum(c*previous[index-j]/den for j,c in enumerate(coefficients) if 0<=index-j<len(previous)))
        check(r[1]==1 and r[0]==0,'normalization')
        check(r[3]-Q(13,10)*r[2]>Q(1,32),'boundary2/3')
        check(r[4]-Q(29,26)*r[3]>Q(1,16),'boundary3/4')
        cert.append(k)
    # Independent Gaussian binomial count of stationary law at block four.
    weights=[]
    for j in range(5):
        binomial=Q(1)
        for i in range(j):
            binomial*=Q(2**(4-i)-1,2**(j-i)-1)
        weights.append(binomial*2**(j*(j+1)//2))
    check(weights==[1,30,280,960,1024] and sum(weights)==2295,'stationary counts')
    limit=Q(11,10)*sum(w*Q(a,seed[1]) for w,a in zip(weights,seed))/sum(weights)
    check(limit==Q(439277,149175),'exact limit formula')
    receipt=json.loads((P/'RESULT.json').read_text())
    check(type(receipt['infimum_attained']) is bool and receipt['infimum_attained'] is False,'typed conclusion')
    check(receipt['infimum']==str(limit),'receipt limit')
    check([v['k'] for v in receipt['boundary_certificate']]==cert,'receipt boundary coverage')
    print('PASS_INDEPENDENT_NORMALIZED_RECURRENCE_AND_LIMIT')

if __name__=='__main__':
    run()
