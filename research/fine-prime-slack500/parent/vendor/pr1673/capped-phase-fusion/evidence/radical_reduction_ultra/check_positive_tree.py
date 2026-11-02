#!/usr/bin/env python3
"""Exact controls for the positive interpolation tree and two global tails."""
from fractions import Fraction as F
from math import prod
from pathlib import Path
import json

def mul(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]+=x*y
    return c

def add(a,b):
    c=[F(0)]*max(len(a),len(b))
    for i,x in enumerate(a): c[i]+=x
    for i,x in enumerate(b): c[i]+=x
    return c

def factor(xs):
    p=[F(1)]
    for x in xs: p=mul(p,[F(1),x])
    return p

def test(s,H,r):
    t=s+H
    qi=[(2*t*i+s)//(2*s) for i in range(s)]
    xs=[F(r)**q for q in qi]
    es=factor(xs)
    ws=[]
    for i in range(s):
        den=prod(xs[i]-xs[j] for j in range(s) if j!=i)
        ws.append(F((i*7+3)%11-5,den))
    whole=[F(0)]*s
    abswhole=[F(0)]*s
    for i in range(s):
        e=factor(xs[:i]+xs[i+1:])
        whole=add(whole,[ws[i]*v for v in e])
        abswhole=add(abswhole,[abs(ws[i])*v for v in e])
    # Arbitrary positive target coefficient weights suffice for the exact
    # completion inequality; these reproduce a Gaussian-shaped gauge.
    ds=[F(1,r**(j*j)) for j in range(s)]
    B=max(abswhole[s-1-j]/ds[j] for j in range(s))
    checked=0
    def tree(l,u):
        nonlocal checked
        if u-l==1:
            fi=[F(1),xs[l]]; ri=[ws[l]]; ai=[abs(ws[l])]
        else:
            m=(l+u)//2
            fl,rl,al=tree(l,m); fr,rr,ar=tree(m,u)
            fi=mul(fl,fr)
            ri=add(mul(fr,rl),mul(fl,rr))
            ai=add(mul(fr,al),mul(fl,ar))
        Mh=prod(xs[u:])
        for k in range(u-l):
            target=s-u+k
            assert abs(ri[k])<=ai[k]
            assert Mh*ai[k]<=abswhole[target]
            assert ai[k]<=B*ds[u-1-k]/Mh
            checked+=1
        return fi,ri,ai
    ff,rr,aa=tree(0,s)
    assert ff==es and rr==whole and aa==abswhole
    left=factor(xs[:s//2])
    broken=[F(0)]*s
    for i in range(s//2):
        wrong=factor(xs[:i]+xs[i+1:s//2])
        broken=add(broken,[ws[i]*v for v in wrong])
    for i in range(s//2,s):
        right=factor(xs[s//2:i]+xs[i+1:])
        broken=add(broken,[ws[i]*v for v in mul(left,right)])
    assert broken != whole
    tails=0
    for j in range(s):
        k=s-1-j
        for i in range(s):
            e=factor(xs[:i]+xs[i+1:])[k]
            if i<j:
                m=j-i
                app=es[k]
                assert app>=e
                assert (app-e)*r**(m+1)<=4*app
                tails+=1
            if i>j:
                m=i-j
                app=es[k+1]/xs[i]
                assert app>=e
                assert (app-e)*r**(m+1)<=4*app
                tails+=1
    return checked,tails

n=nodes=tails=0
for s in range(3,15):
    for H in range(1,min(s,5)):
        for r in (4,8):
            c,d=test(s,H,r)
            n+=1; nodes+=c; tails+=d
out={"status":"pass", "arithmetic":"exact rational", "instances":n,
     "tree_coefficient_completion_inequalities":nodes,
     "far_field_relative_error_inequalities":tails,
     "negative_controls":["Omitting the upper-child factor changes the root polynomial.",
                          "The omitted upper-child factor is detected in every instance."],
     "claims_excluded":["Fast normalized convolution implementation", "Tensor fusion", "New final exponent"]}
Path(__file__).with_name('POSITIVE-TREE-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
