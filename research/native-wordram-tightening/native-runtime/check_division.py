"""Exact finite checks for the informal division-elimination theorem; Apache-2.0.
Dugongue with substantial OpenAI Codex assistance. Python integers verify the
identities; they are not a unit-cost arbitrary-precision machine model.
"""
import random,json

def need(ok,why):
    if not ok:raise ValueError(why)

def divide(n,d,w,correct=True):
    need(w>=2 and 0<=n<(1<<w) and 0<d<(1<<w),'input bound')
    # Binary search the most significant bit, using only shifts/comparisons.
    lo,hi=0,w
    while lo+1<hi:
        mid=(lo+hi)>>1
        if d>>mid:lo=mid
        else:hi=mid
    s=w-1-lo;dn=d<<s;q=4*w;B=1<<q;A=dn<<(q-w);X=B
    k=0;power=1
    while power<4*w:power<<=1;k+=1
    for _ in range(k):
        numerator=(2*B*B*X-A*X*X)
        need(numerator>=0,'Newton numerator')
        X=numerator>>(2*q)
        need(B<=X and A*X<=B*B,'reciprocal interval')
    err_num=B*(1<<w)-dn*X
    need(err_num>=0 and (err_num<<(2*w))<=B*(1<<w),'error bound')
    t=(n*(1<<s)*X)>>(w+q)
    need(t*d<=n<(t+2)*d,'one-correction bound')
    if correct and n-t*d>=d:t+=1
    return t,n-t*d

def main():
    checks=0;corrections=0
    for w in range(2,9):
        for d in range(1,1<<w):
            for n in range(1<<w):
                v=divide(n,d,w);need(v==divmod(n,d),'exhaustive result');checks+=1
                if divide(n,d,w,False)!=v:corrections+=1
    rng=random.Random(20261022)
    for w in [16,31,32,63,64,127,128,255,256,512]:
        edge=[1,2,3,(1<<(w-1))-1,1<<(w-1),(1<<w)-1]
        for i in range(2000):
            d=edge[i%len(edge)] if i<60 else rng.randrange(1,1<<w)
            n=edge[(i//len(edge))%len(edge)] if i<60 else rng.randrange(1<<w)
            need(divide(n,d,w)==divmod(n,d),'wide result');checks+=1
    need(corrections>0,'omitted-correction mutant must fail')
    rejected=0
    for n,d,w in [(0,0,32),(-1,1,32),(1<<32,1,32),(1,1<<32,32),(1,1,1)]:
        try:divide(n,d,w)
        except ValueError:rejected+=1
    need(rejected==5,'input controls')
    print(json.dumps({'status':'PASS_FINITE_DIVISION_IDENTITY_CHECKS','exact_pairs':checks,'omitted_correction_failures':corrections,'invalid_inputs_rejected':rejected,'scope':'finite identities plus separate universal proof; not a complete multiplier implementation'},indent=2))
if __name__=='__main__':main()
