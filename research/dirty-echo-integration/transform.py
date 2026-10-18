"""Complete normalized synthetic transforms using the all-role echo adapter.

Matches the stored-order contract of upstream/06-transforms.tex. Exact Fraction
prototype with indexed address reads; this does not implement a fixed-tape bound.
"""
import importlib.util
from math import gcd,prod
from pathlib import Path

spec=importlib.util.spec_from_file_location('synthetic_echo_adapter',Path(__file__).with_name('adapter.py'))
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)


def axis_data(axes):
    widths=[]
    for n in axes:
        A.need(n>=2 and n&(n-1)==0,'power-of-two axis')
        widths.append(n.bit_length()-1)
    return widths,[sum(widths[i+1:]) for i in range(len(widths))]


def rounds(axes,record_width):
    widths,offsets=axis_data(axes)
    A.need(record_width>=2 and record_width&(record_width-1)==0,'power-of-two record')
    A.need(all((2*record_width)%t==0 for t in axes),'synthetic root order')
    result=[]
    for s in range(max(widths)):
        active=[(i,width-s-1) for i,width in enumerate(widths) if width>s]
        bits=[offsets[i]+bit for i,bit in active]
        exponents=[]
        for address in range(prod(axes)):
            exponent=0
            for i,bit in active:
                coord=(address>>offsets[i])&(axes[i]-1)
                exponent-=(2*record_width//(1<<(bit+1)))*((coord>>bit)&1)*(coord&((1<<bit)-1))
            exponents.append(exponent%(2*record_width))
        result.append((bits,exponents))
    return result


def rotate_record_in_place(row,start,r,exponent):
    """Multiply one polynomial by y^exponent mod y^r+1 with one held scalar."""
    exponent%=2*r
    for begin in range(gcd(r,exponent)):
        position=begin;held=row[start+position]
        while True:
            quotient,destination=divmod(position+exponent,r)
            old=row[start+destination]
            row[start+destination]=A.scale(held,(-1)**quotient)
            held=old;position=destination
            if position==begin:
                break


def normalized_layer(arrays,bits,r,fanout,mutant=None):
    multiplier=A.ONE
    for _ in bits:
        multiplier=A.mul(multiplier,A.B)
    for row in arrays:
        for j,v in enumerate(row):
            row[j]=A.mul(A.ipow(sum(((j//r)>>bit)&1 for bit in bits)),v)
    receipt=A.complex_layer(arrays,bits,r,fanout,mutant)
    for row in arrays:
        for j,v in enumerate(row):
            factor=A.ipow(sum(((j//r)>>bit)&1 for bit in bits))
            if mutant!='omit_normalization':
                factor=A.mul(factor,multiplier)
            row[j]=A.mul(factor,v)
    return receipt


def transform(arrays,axes,r,opposite=False,fanout=8,mutant=None):
    """Forward B F-minus; opposite F-plus B^-1. Both normalized by 1/M."""
    A.need(len({id(row) for row in arrays})==len(arrays),'distinct arrays')
    schedule=rounds(axes,r)
    A.need(len(arrays)%2==0 and len(arrays)>=A.role_count(len(axes),fanout),'even sufficient roles')
    A.need(all(len(row)==prod(axes)*r for row in arrays),'array extent')
    leaves=0;twiddle_writes=0;layer_records=[]
    for bits,exponents in reversed(schedule) if opposite else schedule:
        if opposite:
            for row in arrays:
                for address,exponent in enumerate(exponents):
                    rotate_record_in_place(row,address*r,r,-exponent)
                    twiddle_writes+=r
        receipt=normalized_layer(arrays,bits,r,fanout,mutant)
        leaves+=receipt['leaf_calls'];layer_records.append(receipt)
        if not opposite:
            for row in arrays:
                for address,exponent in enumerate(exponents):
                    rotate_record_in_place(row,address*r,r,exponent if mutant!='reverse_twiddle_sign' else -exponent)
                    twiddle_writes+=r
    size=len(arrays[0]);W=len(arrays)
    return dict(axes=list(axes),record_width=r,opposite=opposite,rounds=len(schedule),
                all_role_layer_records=layer_records,echo_leaves=leaves,
                source_component_reads=2*size*leaves,target_component_reads=size*leaves,
                leaf_component_writes=size*leaves,adapter_and_butterfly_component_writes=4*W*size*len(schedule),
                twiddle_component_writes=twiddle_writes,
                tape_scope='Indexed-read reference only. Routing, coefficient bit lengths and a fixed-tape implementation are not discharged.')
