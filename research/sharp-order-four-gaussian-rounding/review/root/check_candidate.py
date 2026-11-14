"""Exact ring-domino construction; root candidate, independent of B code."""
from itertools import product
from math import isqrt
import json,random

def need(ok,why):
    if not ok:raise ValueError(why)

def rot(v,k=1):
    x,y=v
    return ((x,y),(-y,x),(-x,-y),(y,-x))[k%4]

def locate(x,y):
    r=max(abs(x),abs(y))
    need(x%2==y%2==1,'doubled half-grid')
    if y==r and x>-r:q,j=0,(r-x)//2
    elif x==-r and y>-r:q,j=1,(r-y)//2
    elif y==-r and x<r:q,j=2,(r+x)//2
    else:
        need(x==r and y<r,'last square side')
        q,j=3,(r+y)//2
    need(0<=j<r and rot((r-2*j,r),q)==(x,y),'ring coordinate')
    return r,q,j

def match(v):
    r,q,j=locate(*v)
    if ((r-1)//2)%2==0:
        if j==0:return rot((r+2,r),q)
        j+=1 if j%2 else -1
    else:
        if j==r-1:return rot((r-2,r-2),q+1)
        j+=1 if j%2==0 else -1
    return rot((r-2*j,r),q)

def n2(x):return sum(t*t for t in x)

def forward(x):
    a,b,c,d=x;s=(a+c,b+d);delta=(a-c,b-d);jd=rot(delta)
    if (s[0]-s[1])%2==0:out=jd
    else:
        v=(jd[0]+jd[1],jd[0]-jd[1]);w=match(v)
        out=((w[0]+w[1])//2,(w[0]-w[1])//2)
    need((s[0]-out[0])%2==(s[1]-out[1])%2==0,'integer pair')
    return ((s[0]+out[0])//2,(s[1]+out[1])//2,(s[0]-out[0])//2,(s[1]-out[1])//2)

def swap(x):return x[2:]+x[:2]
def phase(x):return (-x[1],x[0],-x[3],x[2])
def conjugate(x):return (x[0],-x[1],x[2],-x[3])
def inverse(x):return swap(forward(x))

def radical_interval(n,bits=128):
    a=isqrt(n<<(2*bits));return a,a+1

def below_beta(m,n):
    lo,hi=sorted((m,n))
    if (lo,hi)==(13,19):return True
    for bits in (64,128,256,512,1024,2048,4096):
        lh,uh=radical_interval(hi,bits);ll,ul=radical_interval(lo,bits)
        a,b=radical_interval(19,bits);c,d=radical_interval(13,bits)
        if uh-ll<=a-d:return True
        if lh-ul>b-c:return False
    raise ValueError('radical comparison unresolved')

def one(x):
    y=forward(x)
    need(forward(y)==swap(x),'square-to-swap')
    need(inverse(y)==x and forward(inverse(x))==x,'both inverses')
    need((y[0]+y[2],y[1]+y[3])==(x[0]+x[2],x[1]+x[3]),'exact sum')
    need(forward(phase(x))==phase(y),'global Gaussian phase')
    need(forward(swap(x))==swap(y),'wire-swap covariance')
    s=(x[0]+x[2],x[1]+x[3]);d=(x[0]-x[2],x[1]-x[3]);jd=rot(d)
    target=(s[0]+jd[0],s[1]+jd[1],s[0]-jd[0],s[1]-jd[1])
    need(sum((2*a-b)**2 for a,b in zip(y,target))==(0 if (s[0]-s[1])%2==0 else 4),'exact nearest error')
    need(below_beta(n2(x),n2(y)),'beta radial bound')

def main():
    count=0
    for t in product(range(-31,32,2),repeat=2):
        u=match(t);need(match(u)==t,'matching involution')
        need(sum(abs(a-b) for a,b in zip(t,u))==2,'one unit edge')
        need(match(rot(t))==rot(u),'quarter-turn covariance')
        count+=1
    checked=0;attainment=None;conj_failure=None
    for x in product(range(-4,5),repeat=4):
        one(x);checked+=1;y=forward(x)
        if sorted((n2(x),n2(y)))==[13,19]:attainment=(x,y)
        if conj_failure is None and conjugate(forward(conjugate(x)))!=inverse(x):conj_failure=(x,conjugate(forward(conjugate(x))),inverse(x))
    need(attainment is not None and conj_failure is not None,'attainment and interface control')
    rng=random.Random(20261113)
    for bits in (8,64,256,1024):
        for _ in range(10):one(tuple((-1 if rng.randrange(2) else 1)*rng.getrandbits(bits) for _ in range(4)))
    box=set(product(range(-5,6,2),repeat=2));edges=[]
    for u in box:
        for step in ((2,0),(-2,0),(0,2),(0,-2)):
            v=tuple(a+b for a,b in zip(u,step))
            if v not in box:edges.append((u,v))
    need(len(box)==36 and len(edges)==24,'finite obstruction boundary')
    norms=sorted(set(((n2(u)+2)//4,(n2(v)+2)//4) for u,v in edges))
    need(norms==[(7,13),(9,15),(13,19)],'boundary radial possibilities')
    print(json.dumps({'status':'PASS_ROOT_ORDER_FOUR_RING_CANDIDATE','half_grid_cases':count,'pair_cases':checked,'large_cases':40,'max_bits':1024,'seed':20261113,'sharp_beta':'sqrt(19)-sqrt(13)','attainment':attainment,'conjugation_failure':conj_failure,'obstruction_box_vertices':36,'boundary_edges':len(edges),'boundary_squared_norms':norms,'scope':'Finite exact corroboration of proposed global quarter-turn matching proof and36-vertex parity obstruction; no selected caller/tariff or kappa.'},indent=2))

if __name__=='__main__':main()
