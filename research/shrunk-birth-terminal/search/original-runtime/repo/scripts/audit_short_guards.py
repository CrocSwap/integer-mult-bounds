#!/usr/bin/env python3
"""Short working guards and an explicit, still-unproved gathering target.

The packed gadget and address permutation are checked exactly. No fast tape
implementation of gathering is claimed; independent window moves are linear
in the number of windows and do not achieve the required saving.
"""
from fractions import Fraction as Q
from pathlib import Path
import json

from certify import require, verify_sources
from prepare_layers import serializable, scenarios

ROOT=Path(__file__).resolve().parents[1]
ROTATIONS=(('y',-1,0),('z',-1,0),('y',1,0),('z',1,0),
           ('z',1,1),('y',1,1),('z',-1,1),('y',-1,1))


def guard_width(p):
    require(isinstance(p,int) and p>=2,'Integer p>=2 required')
    return 4*(p-1).bit_length()+6


def gather_order(f,K,rho,g):
    """Input bit indices in output low-to-high order for one slot.

    Gather the first f-1 windows into the most significant contiguous field.
    Keep the remaining coordinates in relative order in a spectator field.
    The highest selected bit is omitted and handled separately after undo.
    """
    require(f>=1 and K>=1 and 0<=rho<K and 1<=g<=K,'Invalid window shape')
    active=[rho+j*K+t for j in range(f-1) for t in range(g)]
    require(len(set(active))==len(active) and all(i<f*K for i in active),
            'Overlapping or overflowing windows')
    selected=set(active)
    guards=[i for i in range(f*K) if i not in selected]
    return guards+active


def gather(value,order):
    return sum(((value>>source)&1)<<target for target,source in enumerate(order))


def ungather(value,order):
    return sum(((value>>target)&1)<<source for target,source in enumerate(order))


def active_mask(value,n,g):
    return sum(((value>>(j*g))&1)<<(j*g) for j in range(n))


def rotate_gadget(x,y,z,n,g,*,inverse=False):
    """Eight modular rotations on compact n*g-bit slots, omitting the top bit."""
    require(n>=1 and g>=1,'Nonempty compact slots required')
    modulus=1<<(n*g)
    state={'y':y,'z':z}
    operations=reversed(ROTATIONS) if inverse else ROTATIONS
    for target,sign,test in operations:
        other=state['z' if target=='y' else 'y']
        offset=sum(1<<(j*g) for j in range(n-1)
                   if x>>(j*g)&1 and (other>>(j*g)&1)==test)
        state[target]=(state[target]+(-sign if inverse else sign)*offset)%modulus
    return x,state['y'],state['z']


def exceptional(y,z,n,g):
    mask=(1<<g)-1
    maximum=(1<<(g-1))-11
    return any(not 10<=((slot>>(j*g))&mask)//2<=maximum
               for slot in (y,z) for j in range(n-1))


def compact_add(x,y,z,n,g):
    """Exact address map, including the existing exceptional-set correction.

    This simulates addresses, not a tape implementation or its running time.
    For g<6 every guard may be exceptional; those cases are finite controls.
    """
    out=rotate_gadget(x,y,z,n,g)
    if exceptional(out[1],out[2],n,g):
        original=rotate_gadget(*out,n,g,inverse=True)
        out=(original[0],original[1]^active_mask(original[0],n-1,g),original[2])
    # Supply the most significant selected bit omitted by the rotations.
    top=(n-1)*g
    return out[0],out[1]^(((out[0]>>top)&1)<<top),out[2]


def gathered_add(x,y,z,f,K,rho,g):
    """Gather three slots, use compact gadget, undo, then add omitted top bit."""
    order=gather_order(f,K,rho,g)
    require(all(0<=v<1<<(f*K) for v in (x,y,z)),'Slot outside complete range')
    if f==1:
        return x,y^(((x>>rho)&1)<<rho),z
    n=f-1
    spectator_width=f*K-n*g
    spectator_mask=(1<<spectator_width)-1
    packed=[gather(v,order) for v in (x,y,z)]
    data=[v>>spectator_width for v in packed]
    updated=compact_add(*data,n,g)
    result=[ungather((new<<spectator_width)|(old&spectator_mask),order)
            for old,new in zip(packed,updated)]
    top=rho+(f-1)*K
    result[1]^=((result[0]>>top)&1)<<top
    return tuple(result)


def repair_budget(p,f):
    require(1<=f<=p,'Use the retained f<=p hypothesis')
    g=guard_width(p)
    require(1<<g >= 64*p**4,'Short guard inequality failed')
    # Before inserting A<=C*p and R superpolynomial, the bad fraction is
    # bounded by 80*f*2^-g <= (5/4)*p^-3. This deliberately overcounts.
    fraction=Q(80*f,1<<g)
    require(fraction<=Q(5,4*p**3),'Repair density failed')
    return dict(p=p,f=f,g=g,bad_fraction_upper=fraction,
                normalized_repair_at_A_equal_p_R_at_least_p=2*p*fraction)


def reduction_exponents(tau,sigma,beta,c,r,theta):
    """Implication of a MISSING gather bound O(V f^r K^theta polylog(p))."""
    require(0<tau<1 and 0<=sigma<1 and 0<beta<1 and c>0 and
            0<r<1 and theta>=0,'Invalid exponent hypothesis')
    gathering=r+theta*c+(1-beta)*max(sigma-r,Q(0))
    compact=tau+(1-beta)*max(sigma-tau,Q(0))
    leaf=sigma+beta*(1-sigma)
    return dict(gathering=gathering,compact_gadget=compact,leaf=leaf,
                layer=max(gathering,compact,leaf),
                status='IMPLICATION OF AN UNPROVED GATHERING BOUND')


def monotone_lengths(permutation):
    """Small exact LIS/LDS control; no inference about unrestricted tape time."""
    inc=[1]*len(permutation);dec=[1]*len(permutation)
    for i,x in enumerate(permutation):
        for j in range(i):
            if permutation[j]<x:inc[i]=max(inc[i],inc[j]+1)
            if permutation[j]>x:dec[i]=max(dec[i],dec[j]+1)
    return max(inc,default=0),max(dec,default=0)


def monotone_stream_obstruction(guard_bits,active_bits):
    """A restricted transpose inside an extreme-field gathering permutation.

    For A guard values and B active values, any global monotone output stream
    contains at most A+B-1 of the AB selected records. This only rules out a
    bounded number of one-shot global monotone streams; nested local reversals
    and coded tape algorithms are outside this model.
    """
    require(guard_bits>=1 and active_bits>=1,'Need two nonempty variable fields')
    A,B=1<<guard_bits,1<<active_bits
    lower=(A*B+A+B-2)//(A+B-1)
    return dict(guard_bits=guard_bits,active_bits=active_bits,
                records=A*B,max_per_monotone_stream=A+B-1,
                required_global_monotone_streams_at_least=lower,
                scope='One-shot uncoded global monotone split/merge only; not all linear-time tape routines.')


def certificate():
    cases=[repair_budget(p,p) for p in (2,7,16,100,1024,10**6)]
    targets={}
    for name,row in scenarios().items():
        if not row['recurrence']['hypothetical']:continue
        p=row['parameters']
        result=reduction_exponents(p['tau'],p['sigma'],p['beta'],p['c'],
                                   p['tau'],1-p['tau'])
        require(result['layer']<p['lamp'],'Gather target does not fit the layer margin')
        targets[name]=dict(target=p['kappa'],exponents=result,
                           missing_hypothesis='Uniform gather and inverse in O(V f^tau K^(1-tau) polylog(p)), with complete descriptor, padding and cleanup costs.')
    return dict(status='SHORT-GUARD REDUCTION; NO FAST GATHERER AND NO NEW KAPPA',
                upstream_commit=verify_sources(),guard_formula='4*ceil(log2(p))+6',
                repair_controls=cases,conditional_targets=targets,
                reduction_cost='O(G_gather + G_inverse + V*(f*log(p))^tau + V), with a fixed number of gather/inverse calls',
                naive_cost='Separate window moves or binary-key sorting give only a linear-in-f certified bound, insufficient for a sublinear layer.',
                stream_control=monotone_stream_obstruction(8,12),
                next_step='Search a gatherer or an operation on strided windows directly; gathering is the remaining theorem, not a free preprocessing step.')


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/short-guard-audit.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS short-guard arithmetic and reduction targets; fast gathering remains unproved.')
