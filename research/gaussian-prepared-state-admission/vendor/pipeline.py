"""Gaussian transforms -> pointwise product -> opposite transform -> exact bits.

There is no direct DFT, convolution, or multiplication oracle in this caller.
Python indices expose complete small boxes; no tape-time bound is claimed.
"""
from fractions import Fraction as F
from itertools import product
from math import gcd, prod

from intervals import (need, ceildiv, in_disk, grid_point, cmul,
                       inward_quantize)


class RecoveryFailure(ValueError):
    pass


def tensor_transform(values, lines, opposite=False, mutation=None):
    shape=tuple(line.s for line in lines)
    coordinates=list(product(*(range(s) for s in shape)))
    need(len(values)==prod(shape),"complete CRT rectangle")
    state=dict(zip(coordinates,values))
    error=F(0)
    executions=0
    for axis,line in enumerate(lines):
        other=shape[:axis]+shape[axis+1:]
        axis_error=F(0)
        for fixed in product(*(range(s) for s in other)):
            addresses=[fixed[:axis]+(j,)+fixed[axis:] for j in range(line.s)]
            result,local=line.transform([state[a] for a in addresses],opposite,mutation)
            for a,z in zip(addresses,result):state[a]=z
            axis_error=max(axis_error,local)
            executions+=1
        # The ideal source-axis RF is a contraction, regardless of its
        # amplified internal Gaussian factorization. Existing error is not
        # multiplied by that internal amplification again.
        error+=axis_error
    return [state[c] for c in coordinates],error,executions


def uniform_certificate(lines,digit_bits):
    need(lines and digit_bits>0,"nonempty finite multiplier configuration")
    p,bits=lines[0].p,lines[0].bits
    need(all(line.p==p and line.bits==bits for line in lines),"common grid")
    for line in lines:
        if line.operator_error is None:line.certify_operator()
    shape=[line.s for line in lines]
    need(all(gcd(a,b)==1 for i,a in enumerate(shape) for b in shape[:i]),"coprime source lengths")
    size=prod(shape)
    transform_error=sum(line.uniform_error for line in lines)
    # Each source-axis RF is a contraction. A quarter-disk input stays
    # below .26, so pointwise products and the opposite call are admissible.
    need(transform_error<F(1,100),"uniform source-transform disk margin")
    product_error=F(2,1<<p)+F(8,1<<bits)
    scale=size*size*(1<<(2*digit_bits+4))
    radius=(3*transform_error+product_error)*scale
    need(digit_bits+2<=p and radius<F(1,2),"uniform exact-recovery precision")
    return {"source_shape":shape,"target_shape":[line.t for line in lines],
            "precision":p,"working_interval_bits":bits,"digit_bits":digit_bits,
            "max_input_digits":(size+1)//2,"max_input_bits":digit_bits*((size+1)//2),
            "error_radius":[radius.numerator,radius.denominator],
            "operator_error_bounds":[[line.operator_error.numerator,line.operator_error.denominator]
                                     for line in lines]}


def multiply(left,right,lines,digit_bits=4,mutation=None,input_bits=None):
    need(left>=0 and right>=0 and lines,"nonnegative binary inputs")
    p=lines[0].p;bits=lines[0].bits
    need(all(line.p==p and line.bits==bits for line in lines),"common root precision")
    shape=tuple(line.s for line in lines)
    need(all(gcd(a,b)==1 for i,a in enumerate(shape) for b in shape[:i]),
         "pairwise coprime CRT axes")
    size=prod(shape);radix=1<<digit_bits
    digits=max(1,ceildiv(max(left.bit_length(),right.bit_length()),digit_bits))
    if input_bits is None:input_bits=max(1,left.bit_length(),right.bit_length())
    need(input_bits>=max(1,left.bit_length(),right.bit_length()),"declared binary input width")
    need(2*digits-1<=size and digit_bits+2<=p,"no cyclic wrap and exact input grid")
    coordinates=list(product(*(range(s) for s in shape)))
    positions={c:i for i,c in enumerate(coordinates)}
    index=[positions[tuple(j%s for s in shape)] for j in range(size)]
    need(len(set(index))==size,"CRT address bijection")
    u=[(0,0)]*size;v=[(0,0)]*size
    for j in range(digits):
        u[index[j]]=(((left>>(j*digit_bits))%(radix))<<(p-digit_bits-2),0)
        v[index[j]]=(((right>>(j*digit_bits))%(radix))<<(p-digit_bits-2),0)
    fu,eu,cu=tensor_transform(u,lines,mutation=mutation)
    fv,ev,cv=tensor_transform(v,lines,mutation=mutation)
    paired=[];ep=F(0)
    for a,b in zip(fu,fv):
        z=cmul(grid_point(a,p,bits),grid_point(b,p,bits))
        rounded,local=inward_quantize(z,p)
        need(in_disk(rounded,p),"pointwise product disk")
        paired.append(rounded);ep=max(ep,local)
    result,eo,co=tensor_transform(paired,lines,opposite=True,mutation=mutation)
    # Ideal Fourier outputs and computed outputs lie in the unit disk:
    # |ab-AB| <= |a| |b-B| + |B| |a-A| <= eu+ev.
    error=eu+ev+ep+eo
    scale=size*size*(1<<(2*digit_bits+4))
    if mutation=="missing_source_factor":scale//=size
    radius=error*scale
    if radius>=F(1,2):
        raise RecoveryFailure("precision certificate does not separate integer coefficients")
    coefficients=[]
    for position in index:
        a,b=result[position]
        center=F(a*scale,1<<p)
        lo,hi=center-radius,center+radius
        smallest=ceildiv(lo.numerator,lo.denominator)
        largest=hi.numerator//hi.denominator
        imaginary=F(b*scale,1<<p)
        if smallest!=largest or smallest<0 or abs(imaginary)>radius:
            raise RecoveryFailure("recovery enclosure has no unique admissible integer coefficient")
        coefficients.append(smallest)
    # Ordinary convolution degree < size, so its nonnegative coefficients
    # can be recovered by a carry scan in the original (inverse CRT) order.
    carry=0;output=[]
    for coefficient in coefficients:
        carry,digit=divmod(coefficient+carry,radix)
        output.append(digit)
    while carry:
        carry,digit=divmod(carry,radix);output.append(digit)
    recovered=sum(value<<(j*digit_bits) for j,value in enumerate(output))
    need(recovered.bit_length()<=2*input_bits,"exact output width")
    return recovered,{
        "source_shape":list(shape),"target_shape":[line.t for line in lines],
        "precision":p,"working_interval_bits":bits,"digit_bits":digit_bits,
        "input_digits":digits,"coefficients":coefficients,
        "source_scale":scale,"error_radius":[radius.numerator,radius.denominator],
        "gaussian_line_executions":cu+cv+co,
        "pointwise_products":size,
        "output_bits":format(recovered,'0'+str(2*input_bits)+'b'),
    }
