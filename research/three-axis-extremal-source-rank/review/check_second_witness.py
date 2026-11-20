"""Root-authored complete finite certificate at a different integer point.

No primary or first-review imports. Exact source exponents are checked
directly from the literal nearest-target expression with Fraction.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations
from math import isqrt, prod
import json

P = 2147483647
POINT = ((17,19),(23,29),(31,37))


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def determinant(a):
    b = [list(row) for row in a]
    result = 1
    for k in range(len(b)):
        pivot = next((i for i in range(k,len(b)) if b[i][k]%P),None)
        if pivot is None:
            return 0
        if pivot != k:
            b[k],b[pivot] = b[pivot],b[k]
            result = -result
        value = b[k][k]%P
        result = result*value%P
        inv = pow(value,-1,P)
        for i in range(k+1,len(b)):
            factor = b[i][k]*inv%P
            for j in range(k+1,len(b)):
                b[i][j] = (b[i][j]-factor*b[k][j])%P
    return result%P


def tensor_entry(i,j,point):
    return prod(1 if ((i>>a)&1)==((j>>a)&1) else point[2-a][(i>>a)&1]
                for a in range(3))


def displacement(order,point):
    return [[tensor_entry(order[i],order[j],point)
             - (tensor_entry(order[i-1],order[j-1],point) if i*j else 0)
             for j in range(8)] for i in range(8)]


def run():
    require(all(P%d for d in range(2,isqrt(P)+1)), "prime modulus")
    digest,count = sha256(),0
    for order in permutations(range(8)):
        value = determinant(displacement(order,POINT))
        require(value!=0,"vanishing independent witness")
        digest.update((str(value)+'\n').encode())
        count += 1
    require(count==40320,"incomplete permutation domain")
    require(determinant(displacement((0,1,2,4,6,5,3,7),((17,19),)*3))==0,
            "equal-factor negative control")
    t = 18446744073709551616
    primes = (18446743751587004417,18446743674277593089,18446743605558116353)
    for s in primes:
        i = (pow(t-s,-1,s)*(-(s-1)//2))%s
        def target(j):
            x=F(t*j,s)+F(1,2)
            return x.numerator//x.denominator
        def exponent(j,k):
            return (F(t*k,s)-target(j))**2-(F(t*k,s)-target(k))**2
        require(0<=i<s-1,"legal extremal index")
        require(exponent(i,i+1)==F(2*(t-s)+1,s),"literal upper exponent")
        require(exponent(i+1,i)==F(2*s-1,s),"literal lower exponent")
    return {"status":"PASS_SECOND_COMPLETE_WITNESS","orders":count,
            "modulus":P,"point":POINT,"residue_sha256":digest.hexdigest(),
            "literal_source_exponent_cases":len(primes),"equal_factor_control_rejected":True}


if __name__ == '__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))
