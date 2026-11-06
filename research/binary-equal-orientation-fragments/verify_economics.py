#!/usr/bin/env python3
"""Independent complete-tree pricing using directed integer square roots.

Jerry Chen / @CubeJerry with substantial OpenAI assistance. Apache-2.0.
The frozen invoice and root accounting are credited to #6726 and its lineage.
No predecessor numerical engine is imported.
"""
import ast
from collections import Counter
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
SCALE=1<<256
EXPONENT_BITS=192
KMIN,KCEIL,KCAP=Q('0.00330720'),Q('0.0033072446849'),Q(1,250)
ZERO=(0,0)
PINS={
 'economics-pricing6726.py':'cbd2b98722461ec6d91879154e837ba9a7dfaeeb03ae249165cda688b24233c2',
 'economics-result6726.json':'e1df91e78b3b1aeafcea9c88bc8badef8a294e88e166df458e41860ae9f9b25a',
 'ROOT6726.json':'b31151c36e39c9267bcc81ec3e13d9d29df9d0c0b404830a9cfb01e21a5b8fc2',
}

def need(ok,message):
    if not ok:raise ValueError(message)

def ceildiv(a,b):return -((-a)//b)

def ceilroot(a):
    b=isqrt(a)
    return b+(b*b!=a)

@lru_cache(None)
def h(n,k):
    """Enclose n**(1-k) in units 2**-256 by binary exponent brackets."""
    need(isinstance(n,int)and n>=1 and 0<=k<1,'Power domain')
    a,remainder=divmod(k.numerator<<EXPONENT_BITS,k.denominator)
    lo=hi=n*SCALE;pl=ph=SCALE
    for j in range(1,EXPONENT_BITS+1):
        lo=isqrt(lo*SCALE);hi=ceilroot(hi*SCALE)
        if (a>>(EXPONENT_BITS-j))&1:
            pl=pl*lo//SCALE;ph=ceildiv(ph*hi,SCALE)
    if remainder:ph=ceildiv(ph*hi,SCALE)
    return n*SCALE*SCALE//ph,ceildiv(n*SCALE*SCALE,pl)

def add(*terms):return sum(x[0]for x in terms),sum(x[1]for x in terms)

def mul(x,c):
    c=Q(c);lo,hi=x if c>=0 else(x[1],x[0])
    return lo*c.numerator//c.denominator,ceildiv(hi*c.numerator,c.denominator)

def fixed(q):return mul((SCALE,SCALE),q)

def inc(n,k):return add(h(8*n+1,k),mul(h(8*n,k),-1))

def maximum(terms):
    terms=list(terms);need(bool(terms),'Empty optimization domain')
    return max(x[0]for x in terms),max(x[1]for x in terms)

def show(x):
    with localcontext()as ctx:
        ctx.prec=42
        ctx.rounding=ROUND_FLOOR;lo=str(Decimal(x[0])/Decimal(SCALE))
        ctx.rounding=ROUND_CEILING;hi=str(Decimal(x[1])/Decimal(SCALE))
        return[lo,hi]

def find_invoice(value):
    if isinstance(value,dict):
        if value.get('status')=='PASS_TWO_PAID_FRAGMENTS_COMPLETE_PRICE':return value
        for child in value.values():
            found=find_invoice(child)
            if found is not None:return found
    return None

def inputs():
    data={}
    for name,digest in PINS.items():
        raw=(HERE/'frozen'/name).read_bytes()
        need(sha256(raw).hexdigest()==digest,'Changed frozen input: '+name);data[name]=raw
    constants={}
    for node in ast.parse(data['economics-pricing6726.py']).body:
        if isinstance(node,ast.Assign)and len(node.targets)==1:
            name=node.targets[0]
            if isinstance(name,ast.Name)and name.id in('HELPERS','LOCAL_PAID'):
                constants[name.id]=ast.literal_eval(node.value)
    need(set(constants)=={'HELPERS','LOCAL_PAID'},'Literal native inventories')
    receipt=find_invoice(json.loads(data['economics-result6726.json']))
    need(receipt is not None,'Complete original invoice absent')
    root=json.loads(data['ROOT6726.json'])
    need(root['fields']==8 and root['full_sites']==[0,1,2,6,7,8],
         'Six-full-site root contract')
    need(len(root['queries'])==9 and root['stage_ranks']==[2,4,4,4,4,2],
         'Root query and idle invoice')
    masks=root['masks']
    need(masks==[3,195,195,53,53,5],'Root body masks')
    supports=[''.join('ABCDEF'[j] for j,m in enumerate(masks) if (m>>i)&1)
              for i in range(8)]
    need(supports==['ABCDEF','ABC','DEF','','DE','DE','BC','BC'],
         'Symbolic root body supports')
    return constants['HELPERS'],constants['LOCAL_PAID'],receipt

def moment(histogram,k):return add(*(mul(h(r,k),c)for r,c in histogram.items()))

def signed_formula(helpers,paid):
    out=Counter()
    for r in set(helpers)|set(paid):out[r]+=18*(helpers.get(r,0)-paid.get(r,0))
    for size,count in ((2,8),(4,4)):
        out[8*size+1]+=208*count;out[8*size]-=208*count;out[1]-=104*count
    for rank,count in ((145,104),(73,208),(41,208),(40,-208),(9,208),(8,-208),(1,-208)):
        out[rank]+=count
    return {r:c for r,c in out.items()if c}

def all_sizes(helpers,paid):
    native={r:helpers.get(r,0)-paid.get(r,0)for r in set(helpers)|set(paid)}
    need(393*4**250<5**250,'Small-tree elementary power bound')
    need(9*32**250<33**250,'Native monotonicity elementary power bound')
    # Bound ell'(k)/log(2) from above using integer floor/ceiling log2.
    slope=Q(0)
    for r,c in native.items():
        floor=r.bit_length()-1;ceiling=(r-1).bit_length()
        slope+=(-c*r*ceiling if c<0 else -Q(32,33)*c*r*floor)
    slope/=104
    need(slope<0,'Native margin monotonicity')
    k=KMIN;t=1-k
    ell=mul(moment(native,k),Q(1,104));A=add(mul(inc(2,k),2),fixed(-1))
    need(A[0]>0,'Uniform internal-node envelope positive')
    tail=add(mul(ell,50),mul(A,44),mul(inc(1,k),4),h(401,k),mul(h(201,k),2),fixed(-2))
    derivative=add(ell,A,mul(h(401,k),8*t/Q(401)),mul(h(201,k),8*t/Q(201)))
    need(tail[1]<0 and derivative[1]<0,'All-size concave tail')
    k=KCEIL;ell=mul(moment(native,k),Q(1,104));dp={1:ZERO}
    comparisons=0
    for n in range(2,50):
        dp[n]=add(maximum(add(dp[a],dp[n-a])for a in range(1,n)),mul(inc(n,k),2),fixed(-1))
        comparisons+=n-1
    triple={}
    for n in range(3,47):
        triple[n]=maximum(add(dp[a],dp[b],dp[n-a-b],inc(n-a,k),inc(n-a-b,k))
                          for a in range(1,n-1)for b in range(1,n-a))
    gaps={}
    for n in range(6,50):
        gaps[n]=add(mul(ell,n),h(8*n+1,k),fixed(-2),
            maximum(add(triple[a],triple[n-a],h(8*a+1,k),h(8*(n-a)+1,k))for a in range(3,n-2)))
    need(all(v[1]<0 for v in gaps.values()),'Finite original-tree ceiling')
    best=max(gaps,key=lambda n:gaps[n][1]);need(best==18,'Expected optimum size')
    return {'tail_at_50':show(tail),'tail_derivative_at_50':show(derivative),
            'native_derivative_over_log2_upper':str(slope),'finite_sizes':len(gaps),
            'binary_split_comparisons':comparisons,'best_size':best,'best_gap_at_ceiling':show(gaps[best])}

def controls(formula,receipt):
    fixtures=[(4,Q(1,2),2),(16,Q(1,4),8),(32,Q(2,5),8),
              (81,Q(1,2),9),(16,Q(3,4),2),(7,Q(0),7)]
    for n,k,want in fixtures:
        lo,hi=h(n,k);need(lo<=want*SCALE<=hi,'Exact rational-power fixture')
        need(hi-lo<SCALE//10**40,'Power enclosure unexpectedly wide')
    literal={int(r):c for r,c in receipt['targets'].items()}
    for r,c in receipt['paid'].items():literal[int(r)]=literal.get(int(r),0)-c
    literal={r:c for r,c in literal.items()if c}
    need(literal==formula,'Reconstructed root and child invoice differs')
    mutant=dict(literal);mutant[1]+=104
    need(mutant!=formula,'Missing-query negative control was not rejected')
    admitted=moment(literal,KMIN);ceiling=moment(literal,KCEIL)
    need(admitted[0]>0 and ceiling[1]<0,'Known complete invoice sign controls')
    unpaid=add(mul(inc(1,KMIN),2),mul(inc(2,KMIN),-2))
    need(unpaid[0]>0,'Unpaid-query mutant should change the conclusion locally')
    big=(8<<80)+8;k=Q(1,8)
    local=add(mul(add(h(9,k),mul(h(8,k),-1)),2),
              mul(add(h(big+1,k),mul(h(big,k),-1)),-2),fixed(-1))
    need(local[0]>0,'Extreme-asymmetry local positive control')
    return {'power_fixtures':len(fixtures),'known_admitted_margin':show(admitted),
            'known_ceiling_margin':show(ceiling),'omitted_query_rejected':True,
            'unpaid_query_false_local_gain':show(unpaid),'true_asymmetric_local_gain':show(local)}

def main():
    helpers,paid,receipt=inputs();formula=signed_formula(helpers,paid)
    result={'status':'PASS_EQUAL_ORIENTATION_COMPLETE_TREE_CEILING',
            'scope':'Fixed #6726 two-fragment root; exact old/new binary-node invoices; no new kappa.',
            'kappa_interval':[str(KMIN),str(KCAP)],'raw_ceiling':str(KCEIL),
            'arithmetic':'Directed integer square roots; 256 fractional bits, 192 exponent bits.',
            'controls':controls(formula,receipt),'all_sizes':all_sizes(helpers,paid)}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
