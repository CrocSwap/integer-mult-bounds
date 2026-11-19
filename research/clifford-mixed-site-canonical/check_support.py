"""Exact Fourier support on every shear orbit, including the worst cancellations."""
from fractions import Fraction
from itertools import product
from math import lcm
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from mixed import Decoder, Producer, Q, distance, inverse_kernel, point_set, scale, span, vertices
from support import carrier, defect, form_value, slot, support_counts


def transvection(w,d,i,j):
    axes=[1<<k for k in range(d)]
    axes[j]^=1<<i
    def value(v):
        return form_value(w,v)
    return sum((value(axes[a]) if a==b else value(axes[a]^axes[b])^value(axes[a])^value(axes[b]))
               <<slot(a,b) for b in range(d) for a in range(b+1))


def representatives(d):
    remaining=set(range(1<<(d*(d+1)//2)))
    while remaining:
        w=min(remaining)
        orbit=[w]
        remaining.remove(w)
        for v in orbit:
            for i,j in product(range(d),repeat=2):
                if i!=j:
                    a=transvection(v,d,i,j)
                    if a in remaining:
                        remaining.remove(a)
                        orbit.append(a)
        yield w


def graph_mask(geo):
    idx,cols,q=geo
    def coord(r):
        return sum(((r>>j)&1)<<i for i,j in enumerate(idx))
    def polar(i,j):
        x,y=coord(1<<i),coord(1<<j)
        return ((Q.value(q,x^y)-Q.value(q,x)-Q.value(q,y))%4)//2
    return sum(polar(i,j)<<slot(i,j) for j in range(4) for i in range(j+1))


def main():
    points=[]
    for point,geo in vertices():
        idx,cols,_=geo
        points.append((point,len(idx),frozenset(span(cols)),graph_mask(geo)))
    split=[r for r in points if r[-1]==0]
    Q.need(len(split)==67,"Expected one zero graph above every subspace")
    weights=inverse_kernel()
    denominator=lcm(*(v.denominator for v in weights))
    integers=[int(v*denominator) for v in weights]
    convolution=[[integers[distance(p,x)] for x,*_ in points] for p,*_ in split]
    counts=[]
    for d in range(5):
        D=set(range(1<<d))
        reps=list(representatives(d))
        counts.append(len(reps))
        for w in reps:
            e=carrier(w)
            rhs=[(-1)**(h+(w&T).bit_count()) * (1<<(24-6*h)) if D<=H else 0
                 for _,h,H,T in points]
            for (_,_,H,_),row in zip(split,convolution,strict=True):
                coefficient=sum(x*y for x,y in zip(row,rhs,strict=True))
                Q.need(bool(coefficient)==(e<=H),"Noncancellation fails on a marked Fourier orbit")
    Q.need(counts==[1,2,4,5,7],"Incomplete quadratic defect census")
    # Independent check against actual coordinate phase charts, including an affine translation.
    vectors=[list(range(13)),[0]*11+[1,2],[0]*12+[1],[3,7,9,13,10,8,4,12,5,1,1,0,9]]
    for rows in vectors:
        u=0
        for x in rows:
            u^=x
        shifts={x^u for x in rows}
        w=defect(rows)
        p=Producer((52,sum(x<<(4*i) for i,x in enumerate(rows)),[],[],1,0,0))
        for (_,geo),(_,h,H,T) in zip(vertices(),points,strict=True):
            want=Fraction((-1)**(h+(w&T).bit_count()),1<<(6*h)) if shifts<=H else 0
            got=scale(p.feature(geo))
            Q.need(got==([(u,(want,0))] if want else []),"Literal chart versus defect")
    for e in range(5):
        # Two copies of each independent axis realize a linear defect; four directions
        # can require a genuine quadratic defect. Exhibit actual rows with the target carrier.
        examples=[
            [0]*13,[1,1]+[0]*11,[1,2,3]+[0]*10,[1,2,3,4,4]+[0]*8,
            [1,2,3,4,8,12]+[0]*7]
        rows=examples[e]
        Q.need(len(carrier(defect(rows)))==1<<e,"Missing attainable support rank")
        claimed=(8338459852800,6670767882240,5929571450880,5580773130240,5411658792960)[e]
        Q.need(support_counts(rows)[1]==claimed,"Exact support sizes")
    example=[0]*12+[1]
    p=Producer((52,1,[],[],1,0,0))
    vals=[(scale(p.feature(g)) or [(1,(0,0))])[0][1][0] for _,g in vertices()]
    # Directly compare the globally compressed solution and its projection norm for the example.
    groups={}
    for i,(_,h,H,_) in enumerate(points):
        groups.setdefault((h,1 in H),[]).append(i)
    mass=0
    Q.need(len(groups)==8,"Eight mixed shells")
    for ids in groups.values():
        i=ids[0]
        sol=sum(weights[distance(points[i][0],pt)]*v for (pt,*_),v in zip(points,vals,strict=True))
        mass+=len(ids)*sol*vals[i]
    mass*=Fraction(16*20643840,4**26)
    Q.need(mass==Fraction(34240796149757,767064758258815834521600),"Mixed projection mass")
    ident=(1,2,4,8,16,32,64,128)
    q=Decoder((52,1,[],[],1,0,0)).coefficient(ident,16)
    Q.need(q==(Fraction(-1965636949,32404491151329024000),0),"New nonzero off the adjoint support")
    print("PASS 19 quadratic form orbits, 1,273 exact noncancellation decisions, all five attainable support sizes.")
    print("PASS mixed projection mass",mass,"and a new canonical coefficient",q[0])


if __name__=="__main__":
    main()
