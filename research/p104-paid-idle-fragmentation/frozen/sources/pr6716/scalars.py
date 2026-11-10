"""Fresh ordinary scalar-work and coefficient-height envelope."""
from collections import Counter
from fractions import Fraction as Q

def verify(word):
    total=height=maximum=0;counts=Counter()
    for e in word['events']:
        op=e[0];counts[op]+=1
        if op in('ADD','SCALE'):
            c=Q(e[-1]);n,d=abs(c.numerator),c.denominator
            if not n or d&(d-1):raise ValueError('Nonzero dyadic scalar required')
            maximum=max(maximum,abs(c))
            if op=='ADD':
                # Binary Horner: form n*x, divide by 2^log2(d), sign, add dst.
                component=(n.bit_length()-1)+(n.bit_count()-1)+(d.bit_length()-1)+int(c<0)+1
                work=2*component
            else:
                if n&(n-1):raise ValueError('Scale must be a dyadic unit')
                component=abs((n.bit_length()-1)-(d.bit_length()-1))+int(c<0)
                work=2*component
            increment=(n+d).bit_length()+(d.bit_length()-1)+1
        elif op=='LAMBDA':
            # The retained four-operation two-address-pair implementation.
            work,increment=16,8
        elif op=='SWAP':work,increment=8,4
        else:work,increment=0,0
        if work>32 or increment>32:raise ValueError('Fresh 32-unit ordinary envelope fails')
        total+=work;height+=increment
    return {'real_scalar_units_per_port':total,'coefficient_height_units':height,
            'max_scalar':str(maximum),'per_instruction_envelope':32,'event_census':dict(counts),
            'ordinary_lambdas':counts['LAMBDA'],'uncharged_gaussian_jobs':0}
