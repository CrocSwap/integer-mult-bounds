"""Independent exact-integer regression of root's DIV-free reciprocal formulas.

This checks arithmetic, not a compiler lowering or a complexity theorem.
"""
from random import Random
import json

def need(ok,msg):
    if not ok:raise ValueError(msg)

def prepare(w,d):
    need(w>=2 and 0<d<1<<w,'domain')
    s=w-d.bit_length(); dp=d<<s
    B=1<<(4*w); A=dp<<(3*w); X=B
    k=(4*w-1).bit_length()
    for j in range(1,k+1):
        N=2*B*B*X-A*X*X
        need(N>=0,'nonnegative Newton numerator')
        X=N>>(8*w)
        need(B<=X and A*X<=B*B,'reciprocal invariant')
        # e_j <= 2^(-2^j)+j/B, checked by integer cross products.
        denom=1<<(1<<j)
        need((B*B-A*X)*denom<=B*B+j*B*denom,'Lipschitz error bound')
    need((B*B-A*X)*(1<<(2*w))<=B*B,'terminal reciprocal error')
    return s,X

def quotient(w,n,d,s,X):
    t=(n*(1<<s)*X)>>(5*w)
    need(0<=n-t*d<2*d,'one-correction interval')
    ans=t+int(n-t*d>=d)
    need(ans==n//d,'exact quotient')
    return ans

def main():
    exhaustive=random=0
    for w in range(2,9):
        for d in range(1,1<<w):
            s,X=prepare(w,d)
            for n in range(1<<w):
                quotient(w,n,d,s,X);exhaustive+=1
    rng=Random(20261022)
    for w in (16,32,64,128,256,1024):
        for j in range(90):
            d=rng.randrange(1,1<<w);s,X=prepare(w,d)
            for n in (0,1,(1<<w)-1,rng.randrange(1<<w)):
                quotient(w,n,d,s,X);random+=1
    print(json.dumps({'status':'PASS_INDEPENDENT_NEWTON_ARITHMETIC',
                     'exhaustive_small_word_quotients':exhaustive,
                     'large_word_quotients':random,
                     'largest_width':1024,
                     'scope':'Arithmetic identities and invariants only; primitive shifts/full products still require their stated native lowering.'},indent=2))

if __name__=='__main__':main()
