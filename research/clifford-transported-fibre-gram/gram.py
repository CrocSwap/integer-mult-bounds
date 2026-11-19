"""Apply the width-13 Gram, canonical inverse Gram, or either exact decoder schedule on named fibres."""
import argparse
from fractions import Fraction
from functools import cache
import json
from math import lcm, prod
from pathlib import Path

from class_algebra import GROUP_ORDER, class_index, data
from readout import HERE, ZERO, decode_paulis, rotate_right, synthesize_paulis
from compile_row import compose, inverse

GRAM_DEN = 16**12


def fixed_dimension(left, right):
    pivots = {}
    for a, b in zip(left, right, strict=True):
        v = a ^ b
        while v and v.bit_length() in pivots:
            v ^= pivots[v.bit_length()]
        if v:
            pivots[v.bit_length()] = v
    return 8-len(pivots)


def steps(which):
    src = json.loads((HERE / 'retained' / 'SCHEDULE.json').read_text())
    if which == 'schedule52':
        return [Fraction(n,1<<e) for n,e in src['dyadic_steps_numerator_and_fraction_bits']]
    if which == 'schedule51':
        bits = src['norm_optimal_dyadic_fraction_bits']
        return [Fraction(n,1<<bits) for n in src['norm_optimal_dyadic_numerators']] + [
            Fraction(*src['norm_optimal_final_reciprocal'])]
    raise ValueError('Unknown schedule')


@cache
def spectral_packets():
    classes = data()['classes']
    packets = []
    for row in data()['characters']:
        norm = sum(c['size']*v*v for c,v in zip(classes,row,strict=True)) // GROUP_ORDER
        degree = row[0] // norm
        eigen = Fraction(sum(c['size']*v*(-64)**c['fixed'] for c,v in zip(classes,row,strict=True)),
                         row[0]*GRAM_DEN)
        packets.append((row,degree,eigen))
    return packets


def inverse_transform(values):
    # Lift the weights to one denominator before the 80 integer dot products.
    packets = spectral_packets()
    denominator = lcm(*(v.denominator for v in values))
    scaled = [value.numerator*(denominator//value.denominator)*degree
              for value,(_,degree,_) in zip(values, packets, strict=True)]
    return tuple(Fraction(sum(a*row[j] for a,(row,_,_) in zip(scaled,packets,strict=True)),
                          denominator*GROUP_ORDER) for j in range(len(data()['classes'])))


@cache
def kernels(action):
    eigen = [e for _,_,e in spectral_packets()]
    if action == 'canonical':
        return (inverse_transform([1/e for e in eigen]),)
    schedule = steps(action)
    residual = [prod(1-h*x for h in schedule) for x in eigen]
    correction = [(1-p)/x for p,x in zip(residual,eigen,strict=True)]
    return inverse_transform(residual), inverse_transform(correction)


def rescale(matrix, shift):
    return [(Fraction(a,1<<shift),Fraction(b,1<<shift)) for a,b in matrix]


def synthesize(target, coefficients):
    matrix,power = rotate_right(synthesize_paulis(coefficients),target,False)
    return rescale(matrix,power)


def extract(target, matrix):
    matrix,power = rotate_right(matrix,target,True)
    return rescale(decode_paulis(matrix),power+4)


def apply_blocks(action, inputs, targets):
    """Inputs is a sequence of fibre dictionaries. Schedules take (d0,t); other actions take (c,)."""
    filters = () if action == 'gram' else kernels(action)
    if len(inputs) != (len(filters) if filters else 1):
        raise ValueError('Gram/canonical require one input and schedules require two')
    matrices = [{tuple(t):synthesize(t,c) for t,c in source.items()} for source in inputs]
    sources = set().union(*matrices)
    outputs = {}
    for target in targets:
        target = tuple(target)
        accum = [ZERO]*256
        for source in sources:
            if action == 'gram':
                weights = (Fraction((-64)**fixed_dimension(target,source),GRAM_DEN),)
            else:
                rel = class_index(compose(inverse(target),source))
                weights = tuple(f[rel] for f in filters)
            for mats,weight in zip(matrices,weights,strict=True):
                if weight and source in mats:
                    for j,(a,b) in enumerate(mats[source]):
                        u,v = accum[j]
                        accum[j] = u+weight*a, v+weight*b
        outputs[target] = extract(target,accum)
    return outputs


def parse_blocks(items):
    blocks = {}
    for item in items:
        t = tuple(item['target'])
        if t in blocks:
            raise ValueError('Repeated input fibre')
        coeffs = [ZERO]*256
        for key,pair in item['coefficients'].items():
            j = int(key)
            if str(j)!=key or not 0<=j<256 or len(pair)!=2:
                raise ValueError('Expected an index 0..255 and rational real/imaginary values')
            coeffs[j] = tuple(map(Fraction,pair))
        blocks[t] = coeffs
    return blocks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path,help='JSON with action, inputs (one or two block lists), targets')
    request = json.loads(parser.parse_args().input.read_bytes())
    result = apply_blocks(request['action'],[parse_blocks(x) for x in request['inputs']],request['targets'])
    print(json.dumps([{'target':t,'coefficients':[[str(a),str(b)] for a,b in values]}
                      for t,values in result.items()]))
