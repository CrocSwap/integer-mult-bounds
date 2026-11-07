"""Independent rational bounds for the proposed no-idle caller envelopes.

This reviewer implementation uses atanh and Taylor bounds, and does not
import the author's verifier or any predecessor arithmetic implementation.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from math import factorial
import json
import ast
import hashlib
from pathlib import Path

H = {1:14,2:8,3:4,4:109,5:17,6:3,7:10,8:40,9:359}
PAID = {1:2234,2:454,3:489,4:110,5:152,6:7,7:9,8:1}

def atanh_bounds(z):
    if not 0 <= z <= Q(1,3): raise ValueError("atanh domain")
    n = 55
    lower = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(n)), Q(0))
    upper = lower + 2*z**(2*n+1)/(Q(2*n+1)*(1-z*z))
    return lower,upper

@lru_cache(None)
def log_bounds(r):
    k = r.bit_length()-1
    z = (Q(r,2**k)-1)/(Q(r,2**k)+1)
    l,u = atanh_bounds(z)
    l2,u2 = atanh_bounds(Q(1,3))
    return l+k*l2,u+k*u2

def exp_bounds(l,u):
    if not 0 <= l <= u <= 4: raise ValueError("exp domain")
    n=85
    low=sum((l**j/factorial(j) for j in range(n+1)),Q(0))
    high=sum((u**j/factorial(j) for j in range(n+1)),Q(0))
    high += u**(n+1)/factorial(n+1)/(1-Q(4,n+2))
    return low,high

@lru_cache(None)
def power_bounds(r,t):
    l,u=log_bounds(r)
    return exp_bounds(t*l,t*u)

def envelope(kind):
    c=Counter({r:18*(H.get(r,0)-PAID.get(r,0)) for r in set(H)|set(PAID)})
    if kind==3:
        c[25]+=104*6
        c[9]+=104*18
        c[1]-=104*9
    else:
        c[9]+=104*36
        c[1]-=104*22
    return c

def interval(c,C):
    lo=hi=Q(0)
    for r,a in c.items():
        l,u=power_bounds(r,1-C)
        if a>=0:lo+=a*l;hi+=a*u
        else:lo+=a*u;hi+=a*l
    return lo,hi

def decimal_enclosure(l,u,places=14):
    scale=10**places
    a=l.numerator*scale//l.denominator
    b=-((-u.numerator*scale)//u.denominator)
    return [str(Q(a,scale)),str(Q(b,scale))]

def authenticate(raw):
    if hashlib.sha256(raw).hexdigest() != "3c23e7112b7b822c5d4ba71b412873a8572225001986cb76aa882c6f91226582":
        raise ValueError("frozen native source SHA256")
    values = {}
    for statement in ast.parse(raw).body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in ("HELPERS", "LOCAL_PAID"):
                    if target.id in values: raise ValueError("repeated census")
                    values[target.id] = ast.literal_eval(statement.value)
    if values != {"HELPERS": H, "LOCAL_PAID": PAID}:
        raise ValueError("independently transcribed native census differs")


def main():
    raw=(Path(__file__).resolve().parent/"retained"/"pricing.py").read_bytes()
    authenticate(raw)
    try:
        authenticate(raw+b"\n")
    except ValueError:
        pass
    else:
        raise ValueError("source corruption accepted")
    C=Q('0.0033718004755')
    results={}
    for kind in [3,4]:
        c=envelope(kind)
        lo,hi=interval(c,C)
        if not hi<0:raise ValueError('envelope is not losing')
        # A different monotonicity proof from the author's normalized quotient:
        # all negative nonconstant ranks <=6 and positive ranks >=7.
        deriv_lo=Q(0)
        for r,a in c.items():
            if r==1:continue
            if (a<0 and r>6) or (a>0 and r<7):raise ValueError('rank separation')
            l,u=log_bounds(r)
            deriv_lo+=a*(l if a>=0 else u)
        if not deriv_lo>0:raise ValueError('derivative at zero not positive')
        results[str(kind)]={'C':str(C),'coefficients':dict(sorted(c.items())),
                            'margin_enclosure':decimal_enclosure(lo,hi),
                            'derivative_at_zero_certified_lower':str(deriv_lo.numerator//deriv_lo.denominator)}
    print(json.dumps(results,indent=2))
    # Omitting all eighteen negative native invoices must destroy the verdict.
    wrong = {25:104*6,9:104*18,1:-104*9}
    if interval(wrong,C)[0] <= 0:
        raise ValueError("omitted-native control failed to reverse the verdict")
    print("Negative controls: corrupted native source rejected; omitted-native invoice reverses verdict.")
    print('PASS_INDEPENDENT_NOIDLE_ENVELOPE_AUDIT')

if __name__=='__main__':main()
