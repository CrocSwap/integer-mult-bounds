#!/usr/bin/env python3
"""Integer strictness gap for the historical U8/T37 dual. Apache-2.0; woklerx/Codex."""
from fractions import Fraction as Q
from hashlib import sha256, sha1
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
if hasattr(sys,'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def log_unit(x, n=48):
    """Atanh enclosure for1<=x<=2; positive omitted tail bounded geometrically."""
    need(1 <= x <= 2, 'log range')
    t=(x-1)/(x+1); p=t; total=Q(0)
    for k in range(n):
        total += 2*p/(2*k+1); p *= t*t
    return total, total + 2*p/((2*n+1)*(1-t*t))


def log_bounds(x):
    need(x>=1,'positive log range')
    k=0
    while x>=2:
        x/=2; k+=1
    a,b=log_unit(x); c,d=log_unit(Q(2))
    return a+k*c,b+k*d


def exp_bounds(lo,hi,n=24):
    need(0<=lo<=hi<1,'small exp range')
    sums=[]
    for x in (lo,hi):
        p=total=Q(1)
        for k in range(1,n+1):
            p=p*x/k; total+=p
        sums.append((total,p*x/(n+1)/(1-x/(n+2))))
    return sums[0][0],sums[1][0]+sums[1][1]


def phi(r,z):
    lo,hi=log_bounds(Q(73,r));lo,hi=exp_bounds(z*lo,z*hi)
    return r*lo,r*hi


def bin_credits():
    # Exact unbounded fill DP, independently implemented from the frozen
    # Cartesian enumeration. No predecessor module is imported.
    out={}
    for capacity,bonus in ((8,2),(16,4),(32,8),(48,-13)):
        fill=[None]*(capacity+1);fill[0]=0
        for used in range(1,capacity+1):
            candidates=[fill[used-w]+p for w,p in ((4,-1),(5,-20),(7,-8),(8,-2),(9,4))
                        if used>=w and fill[used-w] is not None]
            if candidates:fill[used]=max(candidates)
        for used,score in enumerate(fill):
            if score is not None:
                r=capacity-used
                out[r]=max(out.get(r,-10**9),bonus+score)
    return out


def pure_profile(t):
    # n1 congruent14382T=30T (mod48), and925n1>=150T.
    residue=(30*t)%48
    k=max(0,(6*t-37*residue+37*48-1)//(37*48))
    n1=residue+48*k
    need((14382*t-n1)%48==0,'rank integrality')
    n48=(14382*t-n1)//48
    need(n48>=0 and 925*n1>=150*t,'pure profile feasibility')
    return n1,n48,925*n1-150*t


def verify():
    for row in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
        if row['usage']!='input':continue
        data=(ROOT/row['path']).read_bytes()
        blob=sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        need(sha256(data).hexdigest()==row['sha256'] and blob==row['git_blob'],'source drift')
    predecessor=json.loads((ROOT/'research/complex-t37-owners/evidence/ALL-T-BOUND.json').read_bytes())
    upper=bin_credits()
    need(upper=={int(r):v for r,v in predecessor['upper'].items()},'full attainable-rank credit table')
    need((predecessor['mass_per_replica'],predecessor['credit_per_replica'])==(14382,150),'family constants')
    z=Q('0.001664727258740678855773')
    values={r:phi(r,z) for r in upper if r}
    cost={r:(48*a-r*values[48][1],48*b-r*values[48][0]) for r,(a,b) in values.items() if r<48}
    lam=tuple(x/925 for x in cost[1])
    need(lam[0]>Q(1,3000),'rational lambda floor')
    margins={}
    for r,(a,b) in cost.items():
        if r==1:continue
        v=48*upper[r]+13*r
        margin=a-v*lam[1 if v>=0 else 0]
        need(margin>Q(29,100),'rational nonextremal margin floor')
        margins[r]=margin
    residues=[]
    for t in range(1,38):
        n1,n48,gap=pure_profile(t)
        # Exhaust the small feasible n1 prefix to independently check the
        # closed form. The next congruent choice is exactly48larger.
        brute=next(n for n in range(n1+1) if 925*n>=150*t and (14382*t-n)%48==0)
        need(brute==n1,'closed formula minimality')
        need(gap==1200*((23*t)%37) and ((gap==0)==(t%37==0)),'exact integer credit lattice')
        nxt=pure_profile(t+37)
        need(nxt[0]==n1+6 and nxt[2]==gap,'period37')
        residues.append({'residue':t%37,'n1':n1,'n48':n48,'credit_slack':gap,
                         'certified_G_floor':str(min(Q(29,100),Q(gap,3000)))})
    positive=[r['credit_slack'] for r in residues if r['credit_slack']]
    need(min(positive)==1200,'sharp lattice slack minimum')
    # Assumption-removal controls: fractional counts attain zero for T=1;
    # T=37 has an integer zero-gap profile; removing the credit constraint
    # admits n1=0 and cannot establish the proposed positive bound.
    need(925*Q(6,37)-150==0,'fractional equality control')
    need(Q(6,37)+48*Q(11086,37)==14382,'fractional mass control')
    need(pure_profile(37)==(6,11086,0),'multiple37 equality control')
    need(925*0<150,'omitted-credit control')
    need(925*1-150*6==25 and (14382*6-1)%48!=0,'omitted-mass-congruence control')
    bad=dict(upper);bad[1]+=1
    need(48*bad[1]+13!=925,'wrong-credit-table control')
    return {'status':'PASS_T37_INTEGER_SLACK_AUDIT','endpoint':str(z),
            'attainable_ranks':len(upper),'strict_margin_ranks':len(margins),
            'lambda_floor':'1/3000','nonextremal_G_floor':'29/100',
            'period':37,'minimum_positive_credit_slack':1200,'nonmultiple37_G_floor':'29/100',
            'normalized_moment_gap_for_nonmultiple37':'strictly greater than29/(313958400*T)',
            'assumption_controls':5,'residues':residues,
            'scope':'Integer residual histograms in the historical U8 family only; no new supplier, selected improvement, sharp optimum, or outer kappa claim.'}


if __name__=='__main__':
    result=verify()
    expected=HERE/'RESULT.json'
    if expected.exists():need(result==json.loads(expected.read_bytes()),'receipt mismatch')
    print(json.dumps(result,indent=2))
