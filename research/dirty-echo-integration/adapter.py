"""All-role adapters for the PR673 echo; mathematical prototypes, not tape code.

Prepared for @androolloyd with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('integration_echo', HERE.parent/'cyclic-dirty-commutator-audit/echo.py')
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)
ZERO=(F(0),F(0)); ONE=(F(1),F(0)); I=(F(0),F(1))
A=(F(1,2),F(1,2)); B=(F(1,2),F(-1,2))


def need(ok,message):
    if not ok:
        raise ValueError(message)


def add(x,y): return x[0]+y[0],x[1]+y[1]
def neg(x): return -x[0],-x[1]
def scale(x,q): return x[0]*q,x[1]*q
def mul(x,y): return x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]
def ipow(n): return (ONE,I,neg(ONE),neg(I))[n%4]


def role_count(factors,fanout):
    depth,_=E.resources(factors,fanout)
    return 2*((depth+3)//2)


def echo_shear(arrays,source,target,factors,leaf,plus,times_sign,fanout=8,sign=1,mutant=None):
    """Translate one target by a composed linear map; restore all other roles.

    A leaf streams its output from a distinct, unchanged source array. The
    prototype uses indexed reads; their tape routing is not silently free.
    """
    need(source!=target and len({id(x) for x in arrays})==len(arrays),'distinct arrays')
    depth,N=E.resources(len(factors),fanout)
    scratch=[i for i in range(len(arrays)) if i not in (source,target)][:depth]
    need(len(scratch)==depth,'insufficient borrowed roles')
    local=[source,target]+scratch
    calls=0
    for s,t,index,q in E.instructions(0,len(factors),0,1,2,fanout,sign):
        if mutant=='omit_negative_leaf' and q==-1:
            continue
        values=leaf(arrays[local[s]],factors[index])
        dst=arrays[local[t]]
        seen=0
        for j,value in enumerate(values):
            need(j<len(dst),'leaf shape')
            dst[j]=plus(dst[j],times_sign(value,q))
            seen+=1
        need(seen==len(dst),'leaf shape')
        calls+=1
    if mutant is None:
        need(calls==N,'echo leaf accounting')
    return calls


def complex_layer(arrays,selected_bits,record_width,fanout=8,mutant=None):
    """Apply C tensor selected bits to EVERY role, including borrowed roles."""
    need(len({id(row) for row in arrays})==len(arrays),'distinct arrays')
    selected_bits=tuple(selected_bits)
    need(selected_bits and len(set(selected_bits))==len(selected_bits),'distinct selected bits')
    need(len(arrays)%2==0 and len(arrays)>=role_count(len(selected_bits),fanout),'even sufficient roles')
    masks=[1<<bit for bit in selected_bits]
    n=len(arrays[0]);need(n%record_width==0,'record shape')
    need(all(len(row)==n for row in arrays) and max(masks)<n//record_width,'layer extent')
    factors=[(mask,False) for mask in masks]
    inverse=[(mask,True) for mask in reversed(masks)]
    def parity(index): return sum(bool((index//record_width)&mask) for mask in masks)%2
    def leaf(row,factor):
        mask,inv=factor;a,b=(B,A) if inv else (A,B)
        return (add(mul(a,row[j]),mul(b,row[((j//record_width)^mask)*record_width+j%record_width])) for j in range(n))
    calls=0
    pairs=range(0,len(arrays),2) if mutant!='skip_borrowed_outputs' else (0,)
    for x in pairs:
        y=x+1
        # A^-1 = gamma Z A Z, gamma=(-i)^D. Pre-Z on the second role
        # and gamma^-1 Z after the block rotation turn both outputs into A.
        for j,v in enumerate(arrays[y]):
            arrays[y][j]=scale(v,-1 if parity(j) else 1)
        calls+=echo_shear(arrays,x,y,factors,leaf,add,scale,fanout,mutant=mutant)
        calls+=echo_shear(arrays,y,x,inverse,leaf,add,scale,fanout,-1,mutant)
        calls+=echo_shear(arrays,x,y,factors,leaf,add,scale,fanout,mutant=mutant)
        if mutant!='omit_role_exchange':
            for j in range(n):
                old=arrays[x][j];arrays[x][j]=arrays[y][j];arrays[y][j]=neg(old)
        gamma_inverse=ipow(len(masks)) if mutant!='omit_inverse_phase' else ONE
        for j,v in enumerate(arrays[y]):
            arrays[y][j]=mul(gamma_inverse,scale(v,-1 if parity(j) else 1))
    return dict(roles=len(arrays),factors=len(masks),leaf_calls=calls,optimistic_child_calls=calls)


def boolean_layer(arrays,permutations,fanout=8,mutant=None):
    """Apply an involutive address permutation product to every bit-data role.

    The given factors must commute and square to identity, as disjoint swaps do.
    Bit data are Python integers interpreted as independent F2 basis coefficients.
    """
    need(len({id(row) for row in arrays})==len(arrays),'distinct arrays')
    need(len(arrays)%2==0 and len(arrays)>=role_count(len(permutations),fanout),'even sufficient roles')
    n=len(arrays[0]);need(all(len(row)==n for row in arrays),'bit shape')
    for p in permutations:
        need(len(p)==n and sorted(p)==list(range(n)),'permutation')
        need(all(p[p[j]]==j for j in range(n)),'involutive factor')
    for p in permutations:
        for q in permutations:
            need(all(p[q[j]]==q[p[j]] for j in range(n)),'commuting factors')
    leaf=lambda row,p:(row[p[j]] for j in range(n))
    plus=lambda a,b:a^b
    times_sign=lambda value,sign:value
    calls=0
    pairs=range(0,len(arrays),2) if mutant!='skip_borrowed_outputs' else (0,)
    for x in pairs:
        y=x+1
        calls+=echo_shear(arrays,x,y,permutations,leaf,plus,times_sign,fanout,mutant=mutant)
        calls+=echo_shear(arrays,y,x,permutations,leaf,plus,times_sign,fanout,-1,mutant)
        calls+=echo_shear(arrays,x,y,permutations,leaf,plus,times_sign,fanout,mutant=mutant)
        if mutant!='omit_role_exchange':
            for j in range(n):
                arrays[x][j],arrays[y][j]=arrays[y][j],arrays[x][j]
    return dict(roles=len(arrays),factors=len(permutations),leaf_calls=calls,optimistic_child_calls=calls)
