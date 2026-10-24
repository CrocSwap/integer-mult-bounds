"""PR197 chart inversion and bank colouring helpers (byte-identical extract of packing.py up to build()).

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from array import array
from collections import Counter
from fractions import Fraction as Q
from math import gcd
from pathlib import Path
import hashlib,json,sys

def inverse_integer(a):
    """Fraction-free Gauss-Jordan; return integral C,d with a C = d I."""
    n=len(a)
    m=[list(row)+[int(i==j) for j in range(n)] for i,row in enumerate(a)]
    previous=1
    factors=[]
    for k in range(n):
        pivot=next((i for i in range(k,n) if m[i][k]),None)
        if pivot is None:
            raise ValueError('Singular basis')
        m[k],m[pivot]=m[pivot],m[k]
        if pivot != k:factors.append(('swap',k,pivot,1,1))
        p=m[k][k]
        if p != previous:
            ratio=Q(previous,p)
            factors.append(('scale',k,k,ratio.numerator,ratio.denominator))
        for i in range(n):
            if i==k:continue
            u=m[i][k]
            if u:
                ratio=Q(-u,previous)
                factors.append(('add',i,k,ratio.numerator,ratio.denominator))
            for j in range(2*n):
                if j==k:continue
                value=p*m[i][j]-u*m[k][j]
                assert value % previous==0
                m[i][j]=value//previous
            m[i][k]=0
        previous=p
    d=m[0][0]
    assert d and all(m[i][j]==d*int(i==j) for i in range(n) for j in range(n))
    c=[row[n:] for row in m]
    common=abs(d)
    for row in c:
        for x in row:common=gcd(common,x)
    d//=common
    c=[[x//common for x in row] for row in c]
    if d<0:d=-d;c=[[-x for x in row] for row in c]
    return c,d,factors

def color_incidence(left,right,nleft,nright,colors):
    """Incremental two-color swaps; parallel edges are identified separately."""
    assert len(left)==len(right)
    full=(1<<colors)-1
    lf=[full]*nleft;rf=[full]*nright
    lc=[array('i',[-1])*colors for _ in range(nleft)]
    rc=[{} for _ in range(nright)]
    labels=array('i',[-1])*len(left)
    swaps=longest=0
    def remove(e):
        u,v,c=left[e],right[e],labels[e]
        assert lc[u][c]==e and rc[v][c]==e
        lc[u][c]=-1;del rc[v][c]
        lf[u]|=1<<c;rf[v]|=1<<c
    def add(e,c):
        u,v=left[e],right[e]
        assert lf[u]&(1<<c) and rf[v]&(1<<c)
        labels[e]=c;lc[u][c]=e;rc[v][c]=e
        lf[u]&=~(1<<c);rf[v]&=~(1<<c)
    for e,(u,v) in enumerate(zip(left,right)):
        common=lf[u]&rf[v]
        if common:
            add(e,(common&-common).bit_length()-1)
            continue
        assert lf[u] and rf[v]
        a=(lf[u]&-lf[u]).bit_length()-1
        b=(rf[v]&-rf[v]).bit_length()-1
        path=[];r=u
        while True:
            edge=lc[r][b]
            if edge<0:break
            path.append(edge);bank=right[edge]
            assert bank!=v
            edge=rc[bank].get(a,-1)
            if edge<0:break
            path.append(edge);r=left[edge]
        changes=[(edge,b if labels[edge]==a else a) for edge in path]
        for edge,_ in changes:remove(edge)
        for edge,c in changes:add(edge,c)
        add(e,b)
        swaps+=1;longest=max(longest,len(path))
    return labels,{'swaps':swaps,'longest_swapped_path':longest}

def check_coloring(left,right,labels,nleft,nright,colors,full_left=False):
    assert len(left)==len(right)==len(labels)
    lm=[0]*nleft;rm=[0]*nright
    for u,v,c in zip(left,right,labels):
        assert 0<=u<nleft and 0<=v<nright and 0<=c<colors
        bit=1<<c
        assert not lm[u]&bit and not rm[v]&bit
        lm[u]|=bit;rm[v]|=bit
    if full_left:assert all(mask==(1<<colors)-1 for mask in lm)

