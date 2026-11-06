#!/usr/bin/env python3
"""Independent square replay: dense Walsh sums and a different coset section.

Closed two-step orbit formulas replace the author's iterative decoder.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
No author module is imported.
"""
import json
from hashlib import sha256
from pathlib import Path
import sys

def need(ok,message):
    if not ok:raise ValueError(message)

ROWS=(0x21,0x906,0x6fde,0x103,0xa8ec,0x29e)
HIGH=tuple(i for i in range(16)if i.bit_count()>1)
SIGNS=tuple(1 if i.bit_count()%2==0 else -1 for i in range(16))
W=tuple(tuple(1 if (r&s).bit_count()%2==0 else -1 for s in range(16))for r in range(16))

def neg(z):return tuple(-x for x in z)
def add(x,y):return tuple(a+b for a,b in zip(x,y))
def sw(z):return tuple(s*sum(a*b for a,b in zip(row,z))for s,row in zip(SIGNS,W))
def quarter(z):
    need(all(x%4==0 for x in z),'Noninteger quarter')
    return tuple(x//4 for x in z)
def b(z):return quarter(sw(z))
def k(z):return tuple(SIGNS[i]*z[15-i]for i in range(16))
def coords(z):
    total=sum(z);sums=[sum(z[i]for i in range(16)if i&(1<<j))for j in range(4)]
    need(total%4==0 and all(x%2==0 for x in sums),'Not in L')
    return(total//4,*(x//2 for x in sums),*(z[i]for i in HIGH))
def synd(c):
    return sum((sum(c[j]for j in range(16)if row&(1<<j))%2)<<i for i,row in enumerate(ROWS))
def base(q):
    a=q%4;bits=q//4;z=[0]*16
    for j in range(4):z[1<<j]=(bits>>j)&1
    z[0]=a-sum(z)
    return tuple(z)
def label(z):
    q=sum(z)%4+4*sum((sum(z[i]for i in range(16)if i&(1<<j))%2)<<j for j in range(4))
    return 64*q+synd(coords(add(z,neg(base(q)))))
def basis():
    ans=[]
    for j in range(16):
        z=[0]*16
        if j==0:z[0]=4
        elif j<5:z[0]=-2;z[1<<(j-1)]=2
        else:
            h=HIGH[j-5];z[h]=1;z[0]=h.bit_count()-1
            for i in range(4):
                if h&(1<<i):z[1<<i]=-1
        ans.append(tuple(z))
    return ans

def replay(path):
    raw=path.read_bytes();data=json.loads(raw)
    need(data['schema_version']==1 and data['period_rows']==list(ROWS),'Schema or period')
    bs=basis();sections={}
    # Last binary coefficient vector per fiber, instead of the author's first
    # independent columns. These are different representatives of every coset.
    for mask in range(1<<16):
        c=tuple((mask>>j)&1 for j in range(16));sections[synd(c)]=c
    need(len(sections)==64,'Surjective syndrome')
    lifts=[tuple(sum(a*v[i]for a,v in zip(sections[s],bs))for i in range(16))for s in range(64)]
    reps=[add(base(q),lifts[s])for q in range(64)for s in range(64)]
    need([label(z)for z in reps]==list(range(4096)),'Independent representatives')
    for i in range(16):
        z=tuple(8*(j==i)for j in range(16));need(label(z)==0,'Low-three-bit period')
    table={}
    for source,values in data['cycles']:
        c=tuple(values);need(len(c)==16 and all(type(x)is int for x in c),'Correction vector')
        z=reps[source];y=quarter(add(sw(z),c));d=neg(b(c))
        for u,e in ((z,c),(y,d),(k(z),k(c)),(k(y),k(d))):
            for v,f in ((u,e),(neg(u),neg(e))):
                j=label(v);need(j not in table or table[j]==f,'Conflicting orbit assignments')
                table[j]=f
    need(len(table)==4096,'Complete correction coverage')
    transform=lambda z:quarter(add(sw(z),table[label(z)]))
    image=[];energy=0;coordinate=0
    re=(1,0,-1,0);im=(0,-1,0,1)
    for j,z in enumerate(reps):
        c=table[j];y=transform(z);image.append(label(y))
        need(table[label(y)]==neg(b(c)),'Square transition')
        need(transform(y)==k(z),'Exact square on alternative representative')
        need(table[label(neg(z))]==neg(c),'Odd correction')
        need(table[label(k(z))]==k(c),'K covariance')
        need(sum(re[i.bit_count()%4]*c[i]for i in range(16))==0,'Real weighted sum')
        need(sum(im[i.bit_count()%4]*c[i]for i in range(16))==0,'Imaginary weighted sum')
        e=sum(x*x for x in c);need(e<=64,'Sharp radius');energy=max(energy,e)
        coordinate=max(coordinate,max(map(abs,c)))
    need(len(set(image))==4096,'Quotient bijection')
    need(energy==64 and coordinate==5,'Sharp and coordinate maxima')
    bad=dict(table);bad[0]=tuple(x+4*(i==0)for i,x in enumerate(bad[0]))
    bad_t=lambda z:quarter(add(sw(z),bad[label(z)]))
    need(any(bad_t(bad_t(z))!=k(z)for z in reps),'Changed correction negative control')
    packed=json.dumps([list(table[j])for j in range(4096)],separators=(',',':')).encode()
    return{'status':'PASS_INDEPENDENT_SQUARE_TRANSITIONS','certificate_sha256':sha256(raw).hexdigest(),
           'table_sha256':sha256(packed).hexdigest(),'classes':4096,'max_energy':energy,
           'max_coordinate':coordinate,'section':'largest binary L-coordinate representative',
           'changed_correction_rejected':True}

if __name__=='__main__':
    p=Path(sys.argv[1])if len(sys.argv)>1 else Path(__file__).with_name('CERTIFICATE.json')
    print(json.dumps(replay(p),indent=2,sort_keys=True))
