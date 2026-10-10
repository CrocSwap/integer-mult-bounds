"""Portable pure functions extracted from the reviewed complex checks; no historical receipt readers."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
Q=Fraction
from hashlib import sha256
from pathlib import Path
from math import prod
import gzip,json,sys

def need(b, why):
    if not b: raise ValueError(why)

def gl_count_test():
    # Exhaustively test a literal binary Gaussian-elimination implementation
    # through m=4. Row swaps cost three selected-bit additions.
    out=[]
    for m in range(1,5):
        good=mx=0
        for word in range(1<<(m*m)):
            rows=[(word>>(m*i))&((1<<m)-1) for i in range(m)]
            ops=0
            for k in range(m):
                p=next((i for i in range(k,m) if rows[i]>>k&1),None)
                if p is None: break
                if p!=k: rows[p],rows[k]=rows[k],rows[p];ops+=3
                for i in range(m):
                    if i!=k and rows[i]>>k&1: rows[i]^=rows[k];ops+=1
            else:
                need(rows==[1<<i for i in range(m)],'basis reduction endpoint')
                need(ops<=m*(m-1)+3*m,'row-addition count')
                good+=1;mx=max(mx,ops)
        need(good==prod((1<<m)-(1<<i) for i in range(m)),'GL coverage')
        out.append(dict(m=m,invertible_matrices=good,maximum_selected_bit_additions=mx))
    return out
