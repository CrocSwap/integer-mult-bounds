"""Independent complementary-minor certificate; no other checker imports."""
from itertools import combinations,permutations
from math import factorial
import json

ZERO = (0,)*6
ONE = {ZERO:1}
ORDER = (0,1,2,4,6,5,3,7)


def add(a,b,sign=1):
    out=dict(a)
    for m,c in b.items():
        out[m]=out.get(m,0)+sign*c
        if not out[m]:
            del out[m]
    return out


def mul(a,b):
    out={}
    for m,c in a.items():
        for n,d in b.items():
            key=tuple(x+y for x,y in zip(m,n))
            out[key]=out.get(key,0)+c*d
    return {m:c for m,c in out.items() if c}


def variable(k):
    return {tuple(int(i==k) for i in range(6)):1}


def entry(i,j):
    exponents=[0]*6
    for axis in range(3):
        left,right=(i>>(2-axis))&1,(j>>(2-axis))&1
        if left!=right:
            exponents[2*axis+left]=1
    return {tuple(exponents):1}


def det(a):
    total={}
    for p in permutations(range(len(a))):
        value=ONE
        for i,j in enumerate(p):
            value=mul(value,a[i][j])
            if not value:
                break
        sign=(-1)**sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p)))
        total=add(total,value,sign)
    return total


def require(ok,message):
    if not ok:
        raise RuntimeError(message)


def run():
    matrix=[[add(entry(ORDER[i],ORDER[j]),entry(ORDER[i-1],ORDER[j-1]),-1)
             if i*j else entry(ORDER[i],ORDER[j]) for j in range(8)] for i in range(8)]
    layers=[[[{m:c for m,c in cell.items() if sum(m[k] for k in (1,3,5))==d}
              for cell in row] for row in matrix] for d in (0,1)]
    a,b=layers
    u,v,x,y,r,z=(variable(k) for k in range(6))
    require(all(not cell for cell in a[7]),"upper-only last row")
    require(all(mul(u,a[5][j])==mul(x,a[6][j]) for j in range(8)),"upper-only row dependence")
    result={}; nonzero=0
    for rows in ((5,7),(6,7)):
        remain_rows=[i for i in range(8) if i not in rows]
        for cols in combinations(range(8),2):
            remain_cols=[i for i in range(8) if i not in cols]
            minor=det([[a[i][j] for j in remain_cols] for i in remain_rows])
            if not minor:
                continue
            nonzero+=1
            small=det([[b[i][j] for j in cols] for i in rows])
            result=add(result,mul(minor,small),(-1)**(sum(rows)+sum(cols)))
    expected=mul(mul(add(u,r,-1),add(mul(u,r),mul(x,x))),
                 mul(add(mul(x,y),mul(u,v),-1),add(mul(x,y),mul(r,z),-1)))
    require(result==expected and len(result)==16,"leading factorization")
    crude=factorial(8)*16**8
    require(crude<2**48,"universal weighted remainder budget")
    require(4096**2*32**3>=2**32,"source smallness endpoint")
    return {"status":"PASS_COMPLEMENTARY_MINOR_REVIEW","row_pairs":2,"column_pairs":28,
            "nonzero_upper_minors":nonzero,"leading_terms":len(result),
            "raw_weighted_mass_bound":crude,"bound_exponent":48,
            "source_guard":"p>=4096 and a>=32 imply p^2 a^3>=2^32",
            "proof_scope":"Leading coefficient plus independent coarse remainder bound; no transcendence sampling."}


if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))
