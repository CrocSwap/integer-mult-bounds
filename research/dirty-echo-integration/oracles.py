"""Direct definitions used independently of the echo and transform schedules."""
from fractions import Fraction as Q
from itertools import product
from math import prod

ZERO=(Q(0),Q(0));ONE=(Q(1),Q(0))
def add(x,y):return x[0]+y[0],x[1]+y[1]
def mul(x,y):return x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]
def scale(x,q):return x[0]*q,x[1]*q


def rotate(values,exponent):
    r=len(values);result=[ZERO]*r
    for j,value in enumerate(values):
        quotient,index=divmod(j+exponent,r)
        result[index]=scale(value,(-1)**quotient)
    return result


def polynomial_product(x,y):
    r=len(x);out=[ZERO]*r
    for i,a in enumerate(x):
        for j,b in enumerate(y):
            q,k=divmod(i+j,r)
            out[k]=add(out[k],scale(mul(a,b),(-1)**q))
    return out


def coordinates(axes):return list(product(*(range(t) for t in axes)))


def fourier(row,axes,r,sign):
    coords=coordinates(axes);size=prod(axes);result=[]
    for target in coords:
        output=[ZERO]*r
        for i,source in enumerate(coords):
            exponent=sign*sum((2*r//t)*a*b for t,a,b in zip(axes,target,source))
            values=rotate(row[i*r:(i+1)*r],exponent)
            output=[add(a,b) for a,b in zip(output,values)]
        result.extend(scale(z,Q(1,size)) for z in output)
    return result


def bit_reverse_records(row,axes,r):
    coords=coordinates(axes);index={value:i for i,value in enumerate(coords)};out=[ZERO]*len(row)
    for i,coord in enumerate(coords):
        reverse=tuple(int(format(a,'0%db'%(t.bit_length()-1))[::-1],2) for t,a in zip(axes,coord))
        j=index[reverse];out[j*r:(j+1)*r]=row[i*r:(i+1)*r]
    return out


def convolution(x,y,axes,r):
    coords=coordinates(axes);index={value:i for i,value in enumerate(coords)};out=[ZERO]*len(x)
    for i,a in enumerate(coords):
        for j,b in enumerate(coords):
            destination=tuple((aa+bb)%t for aa,bb,t in zip(a,b,axes));k=index[destination]
            contribution=polynomial_product(x[i*r:(i+1)*r],y[j*r:(j+1)*r])
            out[k*r:(k+1)*r]=[add(c,d) for c,d in zip(out[k*r:(k+1)*r],contribution)]
    return out


def c_tensor(row,bits):
    a=(Q(1,2),Q(1,2));b=(Q(1,2),Q(-1,2));mask=sum(1<<j for j in bits)
    out=[]
    for i in range(len(row)):
        value=ZERO
        for j,input_value in enumerate(row):
            if (i^j)&~mask:
                continue
            coefficient=ONE
            for bit in bits:
                coefficient=mul(coefficient,b if (i^j)&(1<<bit) else a)
            value=add(value,mul(coefficient,input_value))
        out.append(value)
    return out


def address_swap_permutations(q,groups):
    coords=coordinates([q]*(2*groups));index={c:i for i,c in enumerate(coords)};result=[]
    for i in range(groups):
        permutation=[]
        for coord in coords:
            c=list(coord);c[i],c[groups+i]=c[groups+i],c[i]
            permutation.append(index[tuple(c)])
        result.append(permutation)
    # Whole-chunk interchange directly, without composing the factor maps.
    whole=[index[c[groups:]+c[:groups]] for c in coords]
    return result,whole
