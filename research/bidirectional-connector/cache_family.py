#!/usr/bin/env python3
"""Paid star transfers and arbitrary dirty parent caches, no clean storage.

Apache-2.0. conorholds with substantial OpenAI Codex assistance.
"""
from fractions import Fraction
import families as f


def counts(n):
    f.require(type(n) is int and n>0, 'positive source count required')
    m=(1<<n)-1
    return {'sources':n,'source_calls':2*n,'readout_calls':2*m,
            'transfers':2*m+1+int(n%2==0)+5*n,'dirty_root_rows':n+1}


def path(coordinates,a,b):
    """Hamiltonian cube path between opposite-parity vertices, by induction."""
    coordinates=tuple(coordinates)
    f.require(coordinates and all(type(j) is int and j>=0 for j in coordinates)
              and len(set(coordinates))==len(coordinates), 'invalid cube coordinates')
    f.require(type(a) is int and type(b) is int and a>=0 and b>=0, 'invalid path vertices')
    mask=sum(1<<j for j in coordinates)
    f.require(a&~mask==b&~mask and ((a^b).bit_count()&1)==1, 'invalid path endpoints')
    if len(coordinates)==1:
        return [a,b]
    split=next(j for j in coordinates if (a^b)&(1<<j))
    other=next(j for j in coordinates if j!=split)
    c=a^(1<<other)
    rest=tuple(j for j in coordinates if j!=split)
    return path(rest,a,c)+path(rest,c^(1<<split),b)


def construct(n):
    """All operator queries use physical z0; caches are declared parent rows."""
    invoice=counts(n)
    f.require(n<=18, 'explicit emission bounded to n<=18; counts are unrestricted')
    full=(1<<n)-1
    endpoint=full if n&1 else full^1
    word=[]
    def move(old,new):
        bit=(old^new).bit_length()-1
        word.append(['T',0,bit+1,1 if new&(1<<bit) else -1])
    old=0
    for new in path(range(n),0,endpoint)[1:]:
        move(old,new);word.append(['A',new,0,-1]);old=new
    if old!=full:
        move(old,full)  # Full mask was already read; this is only positioning.
    def update_cache(j,sign):
        word.extend([['T',j+1,0,-1],['B',j,0,sign],['T',j+1,0,1]])
    for j in range(n):update_cache(j,1)
    mask=full
    word.append(['A',mask,0,1])
    for step,j in enumerate(f.cycle(list(range(n))),1):
        new=mask^(1<<j);move(mask,new);mask=new
        if step<(1<<n) and mask:word.append(['A',mask,0,1])
    f.require(mask==full, 'new-cache tour did not close')
    for j in range(n):update_cache(j,-1)
    word.extend(['T',0,j+1,-1] for j in range(n))
    for kind,key in (('A','readout_calls'),('B','source_calls'),('T','transfers')):
        f.require(sum(op[0]==kind for op in word)==invoice[key], 'cache invoice mismatch')
    return word


def screen(n,b,a,t):
    invoice=counts(n)
    b,a,t=map(Fraction,(b,a,t))
    f.require(b>0 and a>0 and t>=0, 'invalid fixed call tariff')
    floor=2*n*b+2*((1<<n)-1)*a
    total=floor+invoice['transfers']*t
    one=f.locality_lower_bound(n,b,a,1)
    two=f.locality_lower_bound(n,b,a,2)
    return {**invoice,'b':str(b),'a':str(a),'t':str(t),'query_cost':str(total),
            'any_root_operator_floor':str(floor),'relative_gap_to_any_root_lower_bound':str((total-floor)/floor),
            'one_root_lower_bound':str(one),'two_root_lower_bound':str(two),
            'guaranteed_one_root_saving':str(1-total/one),
            'guaranteed_two_root_saving':str(1-total/two)}
