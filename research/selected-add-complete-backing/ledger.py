"""Explicit source-cell upper bound; inherited components are cited in PROOF."""


def continuation(h, index_bits, residue_bits):
    a, b = 2*index_bits+4, residue_bits+3
    t = max(a,b)
    # Conservative PR2758 per-array bound, including all four LEFT markers.
    return 2*((h+1)*t+h*b)+t+b+2


def bound(extents, modulus, h, code_bits, program_backing, histories, lives, bits, child=False):
    u,g,s = extents
    r,i = bits
    hr,hi = histories
    lr,li = lives
    lengths = [x.bit_length() for x in extents]
    e = sum(x+2 for x in lengths)+max(i+2,3*max(lengths)+9)
    returned = sum(x+3 for x in lengths)
    p,m,z = [x+3 for x in lengths]
    c = p+r+2+m+max(m,r+2+(2*z if s>1 else 0))
    jr = 20494 if child else 37672
    prep = (max(hr,lr+6)-hr)*(r+2)+(max(hi,li+4)-hi)*(i+2)
    all_numeric = (max(hr,lr+max(jr,6))-hr)*(r+2)+(max(hi,li+22)-hi)*(i+2)
    records = continuation(h,i,r)
    if child:
        records = 4+continuation(h+1,i,r)+program_backing+84+code_bits+2*i
    f = u*modulus*g*modulus*s
    callback = all_numeric+returned+f+3+records
    traversal = all_numeric+returned+2*f+3+c
    preparation = prep+e
    return {'extra':max(preparation,callback,traversal), 'preparation':preparation,
            'callback':callback,'traversal':traversal,'numerical_extra':all_numeric,
            'extended_program_bound':program_backing+84+code_bits+2*i if child else 0,
            'record_allowance':records,'count_preparation':e,'count_returned':returned,
            'count_traversal':c,'fibre_bits':f}
