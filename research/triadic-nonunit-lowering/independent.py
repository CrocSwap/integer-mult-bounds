"""Independent integer matrices and exhaustive triangular double cosets.

Does not import model.py, verify.py, or execute the predecessor compiler.
"""
import hashlib
import json
from math import gcd
from pathlib import Path

P=Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def pins():
    for file,root,key in [('SOURCES.json',P.parents[1],'path'),('VENDOR.json',P,'local_path')]:
        for item in json.loads((P/file).read_text(encoding='utf-8'))['files']:
            if file == 'SOURCES.json' and item.get('usage') != 'input':
                continue
            raw=(root/item[key]).read_bytes()
            require(hashlib.sha256(raw).hexdigest()==item['sha256'],'source SHA256')
            require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob'],'source Git blob')


def identity(n):
    return [[int(i==j) for j in range(n)] for i in range(n)]


def multiply(a,b,m):
    return [[sum(x*y for x,y in zip(row,col))%m for col in zip(*b)] for row in a]


def elementary(t, diagonal, cs, m):
    a=identity(6)
    a[t]=[0]*6
    a[t][t]=diagonal%m
    for i,v in cs:
        a[t][i]=v%m
    return a


def literal_unit(u,m):
    # Rebuild the retained seven events as six by six integer matrices.
    c=u*pow(4,-1,m)%m
    d=pow(c,-1,m)
    swap=identity(6); swap[0],swap[5]=swap[5],swap[0]
    events=[elementary(2,1,[(0,-1)],m),elementary(3,1,[(0,1)],m),
            elementary(5,c,[(0,1+c),(2,-c),(3,-c)],m),swap,
            elementary(2,1,[(0,1)],m),elementary(3,1,[(0,-1)],m),
            elementary(5,-d,[(0,d-1),(2,1),(3,1)],m)]
    out=identity(6)
    for e in events:
        out=multiply(e,out,m)
    return out


def expected(k,m):
    s=[1,0,1,-1,0,-1];r=[1,0,-1,-1,0,1]
    return [[(int(i==j)+k*pow(4,-1,m)*s[i]*r[j])%m for j in range(6)] for i in range(6)]


def run():
    pins()
    cases=0
    for m in [3,5,9,15,21,25,27,35,45,81]:
        for k in range(-2*m,2*m+1):
            if k%m==0:
                got=identity(6)
            elif gcd(k,m)==1:
                got=literal_unit(k,m)
            else:
                # Choose a different unit than the primary first-positive search.
                u=next(x for x in range(m-1,0,-1) if gcd(x,m)==gcd(k-x,m)==1)
                got=multiply(literal_unit(k-u,m),literal_unit(u,m),m)
            require(got==expected(k,m),'complete independent operator')
            require(multiply(expected(-k,m),got,m)==identity(6),'complete inverse')
            cases+=1
    # Exhaust all lower triangular invertible 2x2 factors, with the sole
    # swap between them. Their top-right entries must be exactly the units.
    products=0
    entries={}
    for m in (3,5,9):
        units=[i for i in range(m) if gcd(i,m)==1]
        factors=[(a,b,d) for a in units for b in range(m) for d in units]
        observed=set()
        for a,b,d in factors:
            for e,f,h in factors:
                # [[a,0],[b,d]] C [[e,0],[f,h]]
                got=(a*f%m,a*h%m,(b*f+d*e)%m,b*h%m)
                require(gcd(got[1],m)==1,'one-child unit corner')
                observed.add(got[1]);products+=1
        require(observed==set(units),'full unit corner range')
        entries[str(m)]=sorted(observed)
    # Nonunit is the decisive condition, not merely a nonzero corner.
    require(expected(3,9)[0][5]==3,'nonzero nonunit witness')
    require(expected(3,3)==identity(6),'zero boundary')
    require(expected(3,5)[0][5]==2,'unit boundary')
    # A forbidden reverse-ordered elementary shear can have nonunit corner
    # with zero children, showing why the free-map restriction is needed.
    reverse=identity(6);reverse[0][5]=3
    inv=identity(6);inv[0][5]=-3
    require(multiply(reverse,inv,9)==identity(6),'forbidden shear invertible')
    require(gcd(reverse[0][5],9)==3,'forbidden shear escapes invariant')
    print('PASS_INDEPENDENT_NONUNIT_LOWERING matrices='+str(cases)+' double_coset_pairs='+str(products))
    return {'matrices':cases,'double_coset_pairs':products,'unit_corners':entries}


if __name__=='__main__':
    run()
