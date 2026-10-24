"""Declared-resource source-array grant; not a measured high-water estimate.
JoyboyBrian with substantial OpenAI assistance. Apache-2.0.
"""

def positive(value):
    return type(value) is int and value > 0


def bound(*, volume, highs, old_prefixes, depth, code_bits, residue_bits,
          index_bits, residue_capacity, index_capacity, input_backings,
          q, dimension=64, families=28416, roles=661):
    values=(volume,highs,old_prefixes,code_bits,residue_bits,index_bits,
            residue_capacity,index_capacity,q,dimension,families,roles)
    if not all(map(positive,values)) or type(depth) is not int or depth<0:
        raise ValueError('positive declared resource domain')
    if residue_bits<2 or index_bits<2 or q<2:
        raise ValueError('word and radix domain')
    if len(input_backings)!=9 or not all(map(positive,input_backings)):
        raise ValueError('nine named input backing lengths')
    key=dimension**2*(residue_bits+1)
    field=code_bits+2+key
    directory=1+old_prefixes*highs*(depth+1)*field
    program=2*index_bits+residue_bits+6+(depth+1)*(code_bits+2*index_bits+90)
    a,b=2*index_bits+4,residue_bits+3;t=max(a,b)
    stacks=2*((depth+2)*t+(depth+1)*b)+t+b+2
    digits=max(1,volume.bit_length(),index_bits,residue_bits)
    extent=max(volume+highs*key+1,directory,program,stacks)
    numeric=(residue_capacity+1)*(residue_bits+2)+(index_capacity+1)*(index_bits+2)
    counts=200*(digits+3)
    roots=families+roles+1+q*q+128
    inputs=sum(input_backings)
    total=inputs+numeric+counts+roots*extent
    return dict(total=total,named_inputs=inputs,numeric_capacity=numeric,
                count_backing=counts,noncount_roots=roots,noncount_extent=extent,
                directory=directory,extended_program=program,continuation=stacks,
                route_key=key,count_digits=digits)
