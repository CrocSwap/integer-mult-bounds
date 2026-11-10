#!/usr/bin/env python3
"""Independent rational atanh-log / Taylor-exp review, without author imports.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys

UNIT = 1 << 160
MINIMUM, CEILING = F('0.00330720'), F('0.0033072446849')

def require(ok, why):
    if not ok:
        raise ValueError(why)

def down(x): return x.numerator // x.denominator

def up(x): return -((-x.numerator) // x.denominator)

def log_atanh(z):
    require(F(0) <= z <= F(1, 3), 'atanh reduction domain')
    square, power, total = z*z, z, F(0)
    for j in range(64):
        total += power / (2*j+1)
        power *= square
    tail = power / (129*(1-square))
    return 2*total, 2*(total+tail)

LOG2 = log_atanh(F(1, 3))

@lru_cache(None)
def power(rank, kappa):
    exponent = rank.bit_length()-1
    dyadic = 1 << exponent
    residual = log_atanh(F(rank-dyadic, rank+dyadic))
    logs = tuple(exponent*x+y for x,y in zip(LOG2,residual))
    lo = F(down(kappa*logs[0]*UNIT), UNIT)
    hi = F(up(kappa*logs[1]*UNIT), UNIT)
    require(0 <= lo <= hi < 1, 'small exponential argument')
    def taylor(value):
        term = total = F(1)
        for degree in range(1,25):
            term = term*value/degree
            total += term
        tail = (term*value/25)/(1-value/26)
        return total, total+tail
    lower_exp = taylor(lo)[0]
    upper_exp = taylor(hi)[1]
    return down(rank*UNIT/upper_exp), up(rank*UNIT/lower_exp)

def plus(*intervals):
    return sum(x for x,_ in intervals), sum(y for _,y in intervals)

def times(interval, multiplier):
    q=F(multiplier)
    ends=interval if q>=0 else tuple(reversed(interval))
    return down(ends[0]*q), up(ends[1]*q)

def point(value): return times((UNIT,UNIT),value)

def increment(n,k):
    return plus(power(8*n+1,k),times(power(8*n,k),-1))

def envelope(intervals):
    values=list(intervals)
    return max(x for x,_ in values),max(y for _,y in values)

def display(interval):
    values=[]
    for value,mode in zip(interval,(ROUND_FLOOR,ROUND_CEILING)):
        with localcontext() as ctx:
            ctx.prec=45
            ctx.rounding=mode
            values.append(str(Decimal(value)/Decimal(UNIT)))
    return values

def main():
    package=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
    root_raw=(package/'frozen'/'ROOT6726.json').read_bytes()
    require(hashlib.sha256(root_raw).hexdigest()=='b31151c36e39c9267bcc81ec3e13d9d29df9d0c0b404830a9cfb01e21a5b8fc2','literal root source pin')
    root=json.loads(root_raw)
    require(root['fields']==8 and len(root['full_sites'])==6 and len(root['queries'])==9,'symbolic root shape')
    supports=[[stage for stage,mask in enumerate(root['masks']) if mask>>field&1] for field in range(8)]
    require(supports==[[0,1,2,3,4,5],[0,1,2],[3,4,5],[],[3,4],[3,4],[1,2],[1,2]],'symbolic root body supports')
    require(1-(len(root['queries'])-len(root['full_sites']))==-2,'root target minus thin-query constant')
    raw=(package/'frozen'/'economics-pricing6726.py').read_bytes()
    require(hashlib.sha256(raw).hexdigest()=='cbd2b98722461ec6d91879154e837ba9a7dfaeeb03ae249165cda688b24233c2',
            'frozen native inventory pin')
    constants={}
    for node in ast.parse(raw).body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            if node.targets[0].id in ('HELPERS','LOCAL_PAID'):
                constants[node.targets[0].id]=ast.literal_eval(node.value)
    helper,paid=constants['HELPERS'],constants['LOCAL_PAID']
    native={r:helper.get(r,0)-paid.get(r,0) for r in set(helper)|set(paid)}
    def ell(k):
        return times(plus(*(times(power(r,k),c) for r,c in native.items())),F(1,104))
    require(393*4**250<5**250,'small-tree bound')
    require(9*32**250<33**250,'native power lower bound')
    slope=sum((-c*r*(r-1).bit_length() if c<0 else
               -F(32,33)*c*r*(r.bit_length()-1)) for r,c in native.items())/104
    require(slope==-F(24273,572),'native derivative rational certificate')
    k=MINIMUM
    internal=plus(times(increment(2,k),2),point(-1))
    tail=plus(times(ell(k),50),times(internal,44),times(increment(1,k),4),
              power(401,k),times(power(201,k),2),point(-2))
    tangent=plus(ell(k),internal,times(power(401,k),8*(1-k)/401),
                 times(power(201,k),8*(1-k)/201))
    require(tail[1]<0 and tangent[1]<0,'independent large-tree exclusion')
    # Include both new-node orientations, unlike the author's all-old DP.
    k=CEILING
    tree={1:(0,0)}
    local_comparisons=0
    for n in range(2,50):
        options=[]
        for left in range(1,n):
            base=plus(tree[left],tree[n-left])
            old=plus(times(increment(n,k),2),point(-1))
            for selected in (left,n-left):
                new=plus(times(increment(selected,k),2),point(-2))
                require(new[1]<old[0],'strict old/new interval separation')
                options.append(plus(base,new))
                local_comparisons+=1
            options.append(plus(base,old))
        tree[n]=envelope(options)
    half={}
    triple_count=0
    for total in range(3,47):
        options=[]
        for a in range(1,total-1):
            for b in range(1,total-a):
                c=total-a-b
                options.append(plus(tree[a],tree[b],tree[c],increment(b+c,k),increment(c,k)))
                triple_count+=1
        half[total]=envelope(options)
    margins={}
    for total in range(6,50):
        options=[plus(half[a],half[total-a],power(8*a+1,k),power(8*(total-a)+1,k))
                 for a in range(3,total-2)]
        margins[total]=plus(times(ell(k),total),power(8*total+1,k),point(-2),envelope(options))
    require(all(upper<0 for _,upper in margins.values()),'all finite totals negative')
    best=max(margins,key=lambda n:margins[n][1])
    require(best==18,'finite optimum size')
    omitted=plus(times(increment(1,k),2),point(-1))
    old_two=plus(times(increment(2,k),2),point(-1))
    require(omitted[0]>old_two[1],'omitting the extra query must reverse local comparison')
    report={'status':'PASS_INDEPENDENT_ATANH_TREE_REVIEW',
            'mechanism':'64-term rational atanh log bounds and degree24 Taylor exp bounds; directed160-bit output; no author power-engine import.',
            'tail':display(tail),'tail_derivative':display(tangent),
            'native_derivative_over_log2_upper':str(slope),
            'finite_sizes':len(margins),'best_size':best,'best_gap':display(margins[best]),
            'explicit_new_orientation_comparisons':local_comparisons,'ordered_triples':triple_count,
            'symbolic_root_supports':supports,'omitted_query_reversal_detected':True,
            'reviewed_sha256':{name:hashlib.sha256((package/name).read_bytes()).hexdigest()
                                for name in ('ECONOMICS.md','verify_economics.py')}}
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
