"""Check the source spectra, all central kernels and literal absolute-phase tensor Gram entries."""
from collections import Counter
from fractions import Fraction
from math import gcd, lcm
from random import Random

from class_algebra import GROUP_ORDER, class_index, data, gram_class_matrix
from gram import (GRAM_DEN, HERE, apply_blocks, extract, fixed_dimension, inverse_transform, kernels,
                  spectral_packets, steps, synthesize)
from compile_row import compose, inverse
from readout import ZERO
from verify_readout import Q, TARGETS, literal_trace, plus, power, require, symplectic
import json


def recurrence(schedule, matrix):
    # Replay each factor by integral multiplication in the *class* basis, exact common scaling.
    p = [1]+[0]*79
    den = 1
    for h in schedule:
        a,b = h.as_integer_ratio()
        scale = b*GRAM_DEN
        p = [scale*old-a*sum(x*y for x,y in zip(row,p,strict=True)) for row,old in zip(matrix,p,strict=True)]
        den *= scale
        common = gcd(den,*p)
        p = [x//common for x in p]
        den //= common
    return tuple(Fraction(x,den) for x in p)


def moment_checks():
    src = json.loads((HERE/'retained'/'width13-spectrum.json').read_text())['rows']
    known = Counter()
    for row in src:
        known[Fraction(*row['eigenvalue'])] += row['quotient_degree']**2
    actual = Counter()
    for row,d,eigen in spectral_packets():
        actual[eigen] += row[0]*d
    require(actual==known and sum(actual.values())==GROUP_ORDER and len(known)==52,'Independent spectrum')
    classes = data()['classes']
    matrix = gram_class_matrix()
    shell = [Fraction((-64)**c['fixed'],GRAM_DEN) for c in classes]
    eigen = [e for _,_,e in spectral_packets()]
    require(inverse_transform(eigen)==tuple(shell),'Inverse transform Gram')
    ident = [1]+[0]*79
    for name in ['canonical','schedule51','schedule52']:
        filters = kernels(name)
        p,q = (ident,filters[0]) if name=='canonical' else filters
        if name!='canonical':
            require(recurrence(steps(name),matrix)==p,'Independent class convolution schedule')
        scale = lcm(*(v.denominator for v in q))
        nums = [v.numerator*(scale//v.denominator) for v in q]
        kq = [Fraction(sum(x*y for x,y in zip(row,nums,strict=True)),scale*GRAM_DEN) for row in matrix]
        require(all(a==(i if name=='canonical' else i-h) for a,i,h in zip(kq,ident,p,strict=True)), 'Inverse/affine kernel')
        kernel_den = lcm(*(v.denominator for f in filters for v in f))
        coeff_bits = max((abs(v.numerator)*(kernel_den//v.denominator)).bit_length() for f in filters for v in f)
        print(name,'common coefficient denominator bits',kernel_den.bit_length(),'largest signed-magnitude numerator bits',coeff_bits)


def direct_tests():
    rng = Random(7813)
    targets = TARGETS+(symplectic([rng.randrange(1,256) for _ in range(14)]),)
    entries = {}
    for k,t in enumerate(targets[:3]):
        blocks = [ZERO]*256
        for j in range(3):
            blocks[(k*81+j*75)%256]=(Fraction(2*j-k,3),Fraction(5*k-j,7))
        entries[t] = blocks
        require(extract(t,synthesize(t,blocks))==blocks,'Change of basis')
    outputs = apply_blocks('gram',(entries,),targets)
    stats = Counter()
    for t in targets:
        for p in (0,75,81,150,156,162,237,255,7,28,48,97):
            want = ZERO
            for u,block in entries.items():
                for b,c in enumerate(block):
                    if c==ZERO:
                        continue
                    tau=literal_trace(t,p,u,b)
                    k=fixed_dimension(t,u)
                    stats['nonzero' if tau!=ZERO else 'zero']+=1
                    stats['imag']+=tau[1]!=0
                    stats['odd_fix']+=(k%2==1 and tau!=ZERO)
                    term=power(tuple(v/16 for v in tau),13)
                    want=plus(want,Q.multiply(term,c))
            require(outputs[t][p]==want,'Direct tensor Gram mismatch')
    require(all(stats[key]>0 for key in ('nonzero','zero','imag','odd_fix')), 'Degenerate tensor tests')
    # Delta d0 and t on two different source fibres. Literal traces convert the already independently
    # checked scalar class weights back to the original coefficient coordinates at selected outputs.
    t,u=targets[:2]
    d0=[ZERO]*256; d0[0]=(1,-2)
    rhs=[ZERO]*256; rhs[17]=(3,1)
    for name in ('schedule51','schedule52','canonical'):
        fs=kernels(name)
        inputs=({t:d0},{u:rhs}) if len(fs)==2 else ({u:rhs},)
        got=apply_blocks(name,inputs,targets[2:3])
        v=targets[2]
        scales=[f[class_index(compose(inverse(v),s))]/16 for f,s in zip(fs,(t,u) if len(fs)==2 else (u,),strict=True)]
        for p in range(0,256,9):
            terms=[Q.multiply(d0[0],literal_trace(v,p,t,0)), Q.multiply(rhs[17],literal_trace(v,p,u,17))]
            if len(fs)==1:
                terms=terms[1:]
            expected=tuple(sum(c*w[j] for c,w in zip(scales,terms,strict=True)) for j in range(2))
            require(got[v][p]==expected,'Affine schedule exact complex coefficient')
    print('PASS literal Gram pairings',dict(stats),'and 87 filtered output pairs.')


if __name__=='__main__':
    moment_checks()
    direct_tests()
