"""Direct full-angle source oracle; no one-axis tables or cached recurrence.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Authenticated interval primitives are shared mathematical dependencies.
"""
from fractions import Fraction as Q
from math import prod

def need(ok,message):
    if not ok:raise ValueError(message)

def check(radices,slopes,values,actual,precision,bound,oracle,conjugate=False):
    need(len(radices)==len(slopes)>0 and len(values)==len(actual)==prod(radices),
         'complete direct chirp source coordinates')
    modulus=2*max(radices);bits=2*precision+64;unit=1<<precision
    worst=Q(0);worst_row=None
    for index,(value,result) in enumerate(zip(values,actual)):
        quotient=index;phase=0
        for radix,slope in zip(radices,slopes):
            x=quotient%radix;quotient//=radix
            phase-=slope*x*x*(modulus//(2*radix))
        need(quotient==0,'direct chirp coordinate decomposition')
        if conjugate:phase=-phase
        phase%=modulus
        root=oracle.root_of_unity(phase,modulus,bits)
        expected=oracle.cmul(root,oracle.point(Q(value[0],unit),Q(value[1],unit),bits))
        error=sum(Q(max(abs(Q(result[c],unit)*(1<<bits)-expected[c].lo),
                        abs(Q(result[c],unit)*(1<<bits)-expected[c].hi)),1<<bits)
                  for c in (0,1))
        if error>worst:worst,worst_row=error,index
    need(worst<=bound,'actual output within direct ideal-source allowance')
    return dict(records=len(actual),maximum_enclosed_l1_error=str(worst),
                worst_row=worst_row,declared_bound=str(bound),
                direct_modulus=modulus,oracle_bits=bits)
