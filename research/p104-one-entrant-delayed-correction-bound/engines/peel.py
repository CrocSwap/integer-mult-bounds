"""Exact quotient by chart-bank singleton rows before triangular elimination."""
from fractions import Fraction as Q


def add(a,b,c):
    for j,v in b.items():
        x=a.get(j,0)+c*v
        if x:
            a[j]=x
        else:
            a.pop(j,None)


def test(target,bank):
    single={next(iter(v)) for v in bank.values() if len(v)==1}
    piv={}
    for row in sorted(bank.values(),key=len):
        if len(row)<=1:
            continue
        v={j:x for j,x in row.items() if j not in single}
        while v:
            j=min(v)
            if j not in piv:
                c=v[j]
                piv[j]={i:x/c for i,x in v.items()}
                break
            add(v,piv[j],-v[j])
    v={j:x for j,x in target.items() if j not in single}
    for j,row in sorted(piv.items()):
        if j in v:
            add(v,row,-v[j])
    rank=len(single)+len(piv)
    if not v:
        return rank,len(single),None
    j=min(v)
    x={j:Q(1)}
    for j,row in sorted(piv.items(),reverse=True):
        a=-sum(v*x.get(i,0) for i,v in row.items() if i!=j)
        if a:
            x[j]=a
    def dot(r):
        return sum(r.get(j,0)*v for j,v in x.items())
    assert all(not dot(row) for row in bank.values())
    value=dot(target)
    assert value
    return rank,len(single),{"input":x,"source_value":value}
