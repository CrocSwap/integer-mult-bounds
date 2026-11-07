#!/usr/bin/env python3
"""All-aligned arm rank checks. @CubeJerry/OpenAI, Apache-2.0."""
import argparse
from fractions import Fraction as F
import itertools
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def rank(rows):
    a=[[F(x) for x in row] for row in rows]
    if not a:return 0
    r=0
    for j in range(len(a[0])):
        p=next((i for i in range(r,len(a)) if a[i][j]),None)
        if p is None:continue
        a[r],a[p]=a[p],a[r];z=a[r][j];a[r]=[x/z for x in a[r]]
        for i in range(r+1,len(a)):
            z=a[i][j]
            if z:a[i]=[x-z*y for x,y in zip(a[i],a[r])]
        r+=1
        if r==len(a):break
    return r

def identity(n):return [[int(i==j) for j in range(n)] for i in range(n)]

def multiply(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]

def transpose(a):return list(map(list,zip(*a)))

def gram(xs,ys):return [[sum(x*y for x,y in zip(row,col)) for col in xs] for row in ys]

def product(xs,ys):
    n=len(xs[0]);q=identity(n)
    for x,y in zip(xs,ys):
        row=[sum(y[i]*q[i][j] for i in range(n)) for j in range(n)]
        q=[[q[i][j]-2*x[i]*row[j] for j in range(n)] for i in range(n)]
    return q

def displacement(g):
    return [[int(i==j)+((i>j)-(i<j))*g[i][j] if i!=j else 1-g[i][j]
             for j in range(len(g))] for i in range(len(g))]

def block(signs):
    need(all(s in (-1,1) for s in signs),'sign alphabet')
    k=len(signs)
    return [[1 if i==j else ((i>j)-(i<j))*signs[i] for j in range(k)] for i in range(k)]

def transitions(signs):
    return sum(signs[i]==1 and signs[(i+1)%len(signs)]==-1 for i in range(len(signs)))

def check_block(signs):
    k=len(signs);b=block(signs);c=[[signs[i]*x for x in row] for i,row in enumerate(b)]
    need(all(c[i][j]+c[j][i]==(2*signs[i] if i==j else 0) for i in range(k) for j in range(k)),
         'symmetric part is invertible diagonal')
    value=rank(b)
    need(value==k-transitions(signs),'exact cyclic-sign rank')
    need(value>=(k+1)//2,'half-rank lower bound')
    return value

def check_root(xs,ys):
    n=len(xs[0]);N=len(xs)
    need(product(xs,ys)==[[-int(i==j) for j in range(n)] for i in range(n)],'scalar endpoint -I')
    g=gram(xs,ys)
    need(rank(displacement(g))==N-n,'universal displacement rank')
    return {'dimension':n,'queries':N,'displacement_rank':N-n}

def canonical_root(n):
    need(n%2==0 and n>=2,'even root dimension')
    xs=identity(n)+[[(-1)**(i+1) for i in range(n)]]
    ys=[[(i>j)-(i<j) for j in range(n)] for i in range(n+1)]
    need(all(sum(a*b for a,b in zip(x,y))==0 for x,y in zip(xs,ys)),'native nilpotence')
    return xs,ys

def reject(action,reason,label,controls):
    try:action()
    except ValueError as error:
        need(reason in str(error),'wrong rejection reason');controls.append(label)
    else:raise ValueError('accepted invalid control: '+label)

def run():
    patterns=0;by_length={}
    for k in range(3,11):
        hist={}
        for signs in itertools.product((-1,1),repeat=k):
            r=check_block(signs);hist[str(r)]=hist.get(str(r),0)+1;patterns+=1
        need(sum(hist.values())==2**k,'all sign words covered')
        by_length[str(k)]=hist
    need(patterns==2040,'fixed exhaustive sign domain')
    extremal=[]
    for k in (11,12,31,32):
        signs=tuple((-1)**i for i in range(k));r=check_block(signs)
        need(r==(k+1)//2,'alternating rank is sharp')
        need(check_block((1,)*k)==k,'constant signs have full rank')
        extremal.append({'arms':k,'alternating_rank':r,'constant_rank':k})
    # Independently reconstruct hub/private vectors and their actual Gram block.
    signs=(1,-1,1,-1,1);alphas=(F(2),F(-3),F(5,2),F(-7,3),F(4));k=len(signs);n=k+2
    xs=[];ys=[]
    for i,(s,a) in enumerate(zip(signs,alphas)):
        x=[F(0)]*n;y=[F(0)]*n;x[0]=a;x[i+2]=1;y[0]=s/a;y[i+2]=-s
        need(sum(v*w for v,w in zip(x,y))==0,'literal selected query nilpotence')
        xs.append(x);ys.append(y)
    g=gram(xs,ys)
    normalized=[[alphas[i]*g[i][j]/alphas[j] for j in range(k)] for i in range(k)]
    expected=[[0 if i==j else signs[i] for j in range(k)] for i in range(k)]
    need(normalized==expected,'row-sign Gram normalization')
    b=displacement(g)
    need([[alphas[i]*b[i][j]/alphas[j] for j in range(k)] for i in range(k)]==block(signs),
         'displacement diagonal similarity orientation')
    # The coarse half-rank bound also permits arbitrary nonzero coupling scalars.
    sigmas=(F(2),F(-3),F(5,2),F(-7))
    general=[[1 if i==j else ((i>j)-(i<j))*sigmas[i] for j in range(4)] for i in range(4)]
    c=[[x/sigmas[i] for x in row] for i,row in enumerate(general)]
    need(all(c[i][j]+c[j][i]==(2/sigmas[i] if i==j else 0) for i in range(4) for j in range(4)),
         'nonzero-scalar symmetric-part extension')
    need(rank(general)>=2,'nonzero-scalar half-rank bound')
    roots=[]
    for n in (2,4,6,8):
        xx,yy=canonical_root(n);roots.append(check_root(xx,yy))
    xx,yy=canonical_root(2)
    splitx=[[F(v,2) for v in xx[0]]]*2+xx[1:];splity=[yy[0]]*2+yy[1:]
    roots.append(check_root(splitx,splity))
    roots.append(check_root(xx+[[1,0],[1,0]],yy+[[1,0],[1,0]]))
    controls=[]
    reject(lambda:block((1,0,-1)),'sign alphabet','zero coupling sign',controls)
    wrong=[[0 if i==j else signs[j] for j in range(k)] for i in range(k)]
    reject(lambda:need(normalized==wrong,'row-sign orientation'),'row-sign orientation','column-sign substitution',controls)
    alternating=(1,-1,1,-1,1,-1)
    reject(lambda:need(check_block(alternating)>=4,'false stronger lower bound'),
           'false stronger lower bound','false ceil-half plus one claim',controls)
    cyclic=(-1,1,1)
    linear=sum(cyclic[i]==1 and cyclic[i+1]==-1 for i in range(2))
    reject(lambda:need(check_block(cyclic)==3-linear,'missing cyclic edge'),
           'missing cyclic edge','linear transition count omits closing edge',controls)
    changed=[list(x) for x in xx];changed[0]=[2*v for v in changed[0]]
    reject(lambda:check_root(changed,yy),'scalar endpoint','uncompensated query change',controls)
    # The original unaligned four-arm coupling block has displacement rank one.
    us=((1,0),(0,1),(0,1),(-1,0));vs=((1,-1),(1,-1),(1,1),(1,1));ss=(1,-1,1,-1)
    active=[[[F(u[i]*v[j],s) for j in range(2)] for i in range(2)] for u,v,s in zip(us,vs,ss)]
    reject(lambda:need(all(p==active[0] for p in active),'all common alignment'),
           'all common alignment','unaligned native four-arm block',controls)
    unaligned=[[0 if i==j else sum(a*b for a,b in zip(vs[i],us[j])) for j in range(4)] for i in range(4)]
    need(rank(displacement(unaligned))==1,'unaligned block really violates half-rank conclusion')
    return {'claim':'Exact all-aligned cyclic-sign displacement rank and thin-query lower bound; no new kappa',
        'sign_domain':{'lengths':[3,10],'words':patterns,'seed':None,'stop_rule':'exhaust every sign word'},
        'rank_histograms':by_length,'extremal_checks':extremal,'literal_normalization_arms':k,
        'universal_rank_identity_roots':roots,'negative_controls':controls,
        'net_thin_bound':'2+k-r; r is cyclic plus-to-minus transitions; at least 2+ceil(k/2)',
        'scope':'All actual pure hub-idle projectors aligned; disjoint private arms; full scalar endpoint.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true')
    args=parser.parse_args();result=run();path=HERE/'RESULT.json'
    if args.write:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(json.loads(path.read_text())==result,'frozen result')
    print('PASS_ALL_ALIGNED_ARM_RANK '+json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
