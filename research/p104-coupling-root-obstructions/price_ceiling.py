#!/usr/bin/env python3
"""All-length four-arm price obstruction. @CubeJerry/OpenAI, Apache-2.0.

Independent exact arithmetic: integer 310th-root inequalities, with no
predecessor pricing or logarithm/exponential implementation imported.
"""
from collections import Counter
from functools import lru_cache
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
SCALE = 1 << 40
DENOMINATOR = 310
SOURCE_SHA256 = "da448ecb925b2c7c7f23167ae6ab082d482dc38ccf7a59cc462338094d0e1eaa"
NATIVE = {1:-2220,2:-446,3:-485,4:-1,5:-135,6:-4,7:1,8:39,9:359}


def need(condition,message):
    if not condition:
        raise ValueError(message)


@lru_cache(None)
def power(rank):
    """Enclose rank^(309/310) by exact integer comparisons."""
    need(type(rank) is int and 1<=rank<=10000,"rank domain")
    target = rank**(DENOMINATOR-1) * SCALE**DENOMINATOR
    lo,hi = SCALE,rank*SCALE+1
    while hi-lo>1:
        middle = (lo+hi)//2
        if middle**DENOMINATOR<=target:
            lo=middle
        else:
            hi=middle
    need(lo**DENOMINATOR<=target<(lo+1)**DENOMINATOR,"integer root enclosure")
    return lo,lo if lo**DENOMINATOR==target else lo+1


def add(a,b):
    return a[0]+b[0],a[1]+b[1]


def scale(a,n):
    return (n*a[0],n*a[1]) if n>=0 else (n*a[1],n*a[0])


def moment(profile):
    result=(0,0)
    for rank,count in profile.items():
        need(type(count) is int,"integral invoice multiplicity")
        result=add(result,scale(power(rank),count))
    return result


def difference(a,b):
    return {k:a.get(k,0)-b.get(k,0) for k in set(a)|set(b)}


def envelope(total,thin_charge=4):
    need(type(total) is int and total>=4,"four positive arm lengths")
    signed=Counter({k:total*v for k,v in NATIVE.items()})
    signed[8*total+1]+=208
    signed[8*total]-=104
    signed[1]-=104*thin_charge
    q,r=divmod(total,4)
    for length,multiplicity in ((q,4-r),(q+1,r)):
        for j in range(1,length+1):signed[8*j+1]+=104*multiplicity
        for j in range(1,length):signed[8*j]-=104*multiplicity
    return dict(signed)


def delta(rank):
    return add(power(8*rank+1),scale(power(8*rank),-1))


def binary_envelope(total):
    need(type(total) is int and total>=4,"four positive arm lengths")
    value=moment({k:total*v for k,v in NATIVE.items()})
    outer=add(scale(power(8*total+1),2),scale(power(8*total),-1))
    outer=add(outer,(-4*SCALE,-4*SCALE))
    cap=add(scale(delta(2),2),(-SCALE,-SCALE))
    q,r=divmod(total,4)
    for length,multiplicity in ((q,4-r),(q+1,r)):
        side=power(8*length+1)
        for j in range(1,length):
            d=delta(j)
            side=add(side,(max(d[0],cap[0]),max(d[1],cap[1])))
        outer=add(outer,scale(side,multiplicity))
    return add(value,scale(outer,104))


def certificate(optimum=38,thin_charge=4):
    before=moment(difference(envelope(optimum,thin_charge),envelope(optimum-1,thin_charge)))
    after=moment(difference(envelope(optimum+1,thin_charge),envelope(optimum,thin_charge)))
    maximum=moment(envelope(optimum,thin_charge))
    gap=add(add(delta(9),scale(delta(2),-2)),(SCALE,SCALE))
    need(before[0]>0,"envelope rises before maximum")
    need(after[1]<0,"envelope falls after maximum")
    need(maximum[1]<0,"global envelope is negative")
    need(gap[0]>0,"binary-child envelope matches near maximum")
    need(Fraction(33,32)**2<2,"strict concavity ratio bound")
    derivative=Fraction(2220*8,81)-Fraction(2,7)-Fraction(39,8)
    need(derivative>0,"native normalized derivative")
    return dict(before=before,after=after,maximum=maximum,binary_gap=gap,
                native_derivative_lower=str(derivative))


def reject(action,label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError("accepted negative control: "+label)


def authenticate(raw):
    need(sha256(raw).hexdigest()==SOURCE_SHA256,"retained native profile source")
    source=json.loads(raw)
    helpers={int(k):v for k,v in source['local']['helpers'].items()}
    paid={int(k):v for k,v in source['local']['paid'].items()}
    need(difference(helpers,paid)==NATIVE,"complete frozen native signed profile")


def display(pair):
    def decimal(n):
        sign='-' if n<0 else ''
        whole,part=divmod(abs(n),10**12)
        return sign+str(whole)+'.'+str(part).zfill(12)
    return [decimal(pair[0]*10**12//SCALE),
            decimal(-((-pair[1]*10**12)//SCALE))]


def run():
    raw=(HERE/'retained/CHAIN-RESULT.json').read_bytes()
    authenticate(raw)
    cert=certificate()
    maximum=cert['maximum']
    for total in range(4,97):
        result=binary_envelope(total)
        need(result[1]<0,"finite total-length corroboration")
        if total!=38:need(result[1]<maximum[0],"finite unique envelope maximum")
        profile=envelope(total)
        need(sum(k*v for k,v in profile.items())==48*total-208,"complete rank-mass identity")
    negative=[reject(lambda:certificate(thin_charge=3),"omit mandatory fourth thin query"),
              reject(lambda:certificate(optimum=37),"false optimum37"),
              reject(lambda:certificate(optimum=39),"false optimum39"),
              reject(lambda:envelope(3),"fewer than four positive arms"),
              reject(lambda:power(True),"noninteger rank"),
              reject(lambda:authenticate(raw+b'\n'),"retained source mutation")]
    need(moment(envelope(38,3))[0]>0,"optimistic three-thin invoice is favorable")
    need(power(1)==(SCALE,SCALE),"exact rank-one power")
    return {'status':'PASS_FOUR_ARM_PRICE_CEILING','saving':'1/310','power':'309/310',
            'scale':SCALE,'source_sha256':SOURCE_SHA256,'maximum_total':38,
            'certificate':{k:display(v) if isinstance(v,tuple) else v for k,v in cert.items()},
            'finite_corroboration':{'totals':[4,96],'count':93,'seed':None,'stop_rule':'exhaust stated totals'},
            'negative_controls':negative,'new_kappa':False,
            'scope':'Declared four-arm bill with at least four net thin charges; all hub idles optimistically fused. Analytical proof covers all lengths and binary children.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args();result=run();path=HERE/'PRICE-RESULT.json'
    if args.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==result,'deterministic price receipt')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
