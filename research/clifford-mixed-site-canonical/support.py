"""Canonical support of a row coordinate, via its binary quadratic defect."""
from functools import reduce
from operator import xor


def slot(i,j):
    if i>j:
        i,j=j,i
    return j*(j+1)//2+i


def evaluation_bits(v):
    return sum(((v>>i)&(v>>j)&1)<<slot(i,j) for j in range(4) for i in range(j+1))


def form_value(form,v):
    return (form&evaluation_bits(v)).bit_count()%2


def defect(rows):
    if len(rows)!=13 or any(type(r) is not int or not 0<=r<16 for r in rows):
        raise ValueError("Expected thirteen four-bit rows")
    t=reduce(xor,rows)
    shifts=[r^t for r in rows]
    def value(v):
        count=sum((u&v).bit_count()%2 for u in shifts)
        if count%2:
            raise ValueError("Parity must vanish about XOR")
        return (count//2)%2
    return sum((value(1<<i) if i==j else value((1<<i)^(1<<j))^value(1<<i)^value(1<<j))<<slot(i,j)
               for j in range(4) for i in range(j+1))


def carrier(form):
    null=[v for v in range(16) if form_value(form,v)==0 and
          all(form_value(form,v^y)==form_value(form,y) for y in (1,2,4,8))]
    return frozenset(x for x in range(16) if all((x&v).bit_count()%2==0 for v in null))


def support_counts(rows):
    e=len(carrier(defect(rows))).bit_length()-1
    def combinations(n,k):
        num=den=1
        for j in range(k):
            num*=2**n-2**j
            den*=2**k-2**j
        return num//den
    shells=[(h,combinations(4-e,h-e) * 2**(h*(h+1)//2) * 20643840) for h in range(e,5)]
    return sum(n for _,n in shells),sum((16<<h)*n for h,n in shells)
