"""Reachable prefix-cell discovery, exact integer arithmetic; no imported ports."""
import json
from fractions import Fraction

def execute(k, q, p, g):
    # x = a / 2**s, preserving incoming precision even when t decreases.
    a, s = 5, 3
    targets = [(1, 6)]
    m = 1
    while m < p:
        m = min(2*m, p)
        targets.append((m,m+g))
    trace = []
    for m,t in targets:
        C = k >> (q-t)
        U = (C*a) >> s
        X = (a*((2<<t)-U)) >> s
        a,s = X,t
        trace.append([m,t,C,U,X])
    return a,s,trace

def search(g, limit):
    covered=[]
    for p in range(1,limit+1):
        q=max(6,p+g)
        for k in range(1<<q,2<<q):
            a,s,tr=execute(k,q,p,g)
            # One fixed trace on [k/2**q,(k+1)/2**q).
            # Find a midpoint with a strict residual violation; also inspect left endpoint.
            for num,den in ((k,1<<q),(2*k+1,2<<q)):
                diff=abs((den<<s)-num*a)
                if (diff<<(p+1)) >= (den<<s):
                    return dict(guards=g,p=p,c=str(Fraction(num,den)),x=str(Fraction(a,1<<s)),residual=str(1-Fraction(num*a,den<<s)),cell=[k,q],trace=tr,completed_precisions=covered,first_failing_k=k)
        covered.append(p)
    return dict(guards=g,completed_precisions=covered,no_failure=True)

if __name__=='__main__':
    for g in (2,1,0):print(json.dumps(search(g,16)),flush=True)
