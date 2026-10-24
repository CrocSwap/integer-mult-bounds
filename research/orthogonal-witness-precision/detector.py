"""Detect a selected rational Cayley endpoint with a proved dyadic precision.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The retained source and classical determinant bounds are credited in PROOF.md.
"""
from fractions import Fraction as Q
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent/'vendor/orthogonal'))
from literal import parameters, action
from syntax import validate


def need(value, message):
    if not value:
        raise ValueError(message)


def trunc(n, d=1):
    return n//d if n >= 0 else -((-n)//d)


def budget(program, dimension, parameter):
    need(validate(program).characteristic == 0, 'rational grammar required')
    parameter = Q(parameter)
    need(type(dimension) is int and dimension >= 1 and 0 < parameter <= Q(1,4), 'Cayley domain')
    denominator, gain, largest = 1, Q(1), Q(0)
    calls = steps = 0
    for side in ('left','right'):
        for ins in program[side]:
            steps += 1
            if ins['op'] == 'linear':
                coefficients = [Q(c) for _,c in ins['terms']]
                beta, gamma = max(Q(1),sum(map(abs,coefficients),Q(0))), Q(0)
            elif ins['op'] == 'apply':
                coefficients = []
                beta, gamma = Q(dimension), Q(dimension)
                calls += 1
            else:
                coefficients = [Q(ins['coefficient'])]
                gamma = abs(coefficients[0])*dimension
                beta = 1+gamma
                calls += 1
            for c in coefficients:
                denominator *= c.denominator
            gain *= beta
            largest = max(largest,gamma)
    separation_denominator = denominator * (3*parameter.denominator)**(dimension*calls)
    separation = Q(1,separation_denominator)
    error_multiplier = steps*gain*(largest*gain+1)
    required = 4*max(Q(1),error_multiplier)*separation_denominator
    bits = max(0,required.numerator.bit_length()-required.denominator.bit_length())
    while 1 << bits < required:
        bits += 1
    return dict(bits=bits, separation=separation, error=error_multiplier/(1 << bits),
                gain=gain, scalar_denominator=denominator, calls=calls, steps=steps,
                coefficient_denominator_bits=separation_denominator.bit_length())


def dyadic_matrices(program, word, parameter, bits):
    d, scale = len(word)+1, 1 << bits
    matrices = {}
    for label, band in parameters(program,word,parameter).items():
        columns = [action(band,[Q(i==j) for i in range(d)],1) for j in range(d)]
        rows = [[trunc(x.numerator*scale,x.denominator) for x in row] for row in zip(*columns)]
        matrices[label,1] = rows
        matrices[label,-1] = list(map(list,zip(*rows)))
    return matrices


def detect(program, word, parameter, input_index, output_index):
    need(type(word) in (list,tuple) and all(type(a) is str and a in program['operators'] for a in word),
         'valid path word required')
    roles, d = program['roles'], len(word)+1
    need(type(input_index) is int and type(output_index) is int and
         0 <= input_index < len(roles) and 0 <= output_index < len(roles), 'invalid role')
    parameter = Q(parameter)
    plan = budget(program,d,parameter)
    bits, scale = plan['bits'], 1 << plan['bits']
    matrices = dyadic_matrices(program,word,parameter,bits)
    endpoints = []
    products = roundings = scalar_products = 0
    for side in ('left','right'):
        values = {role:[scale*int(i==input_index and j==d-1) for j in range(d)]
                  for i,role in enumerate(roles)}
        for ins in program[side]:
            dst = ins['dst']
            if ins['op'] == 'linear':
                rational = [sum((Q(c)*values[src][j] for src,c in ins['terms']),Q(0)) for j in range(d)]
                result = [trunc(x.numerator,x.denominator) for x in rational]
                scalar_products += d*len(ins['terms'])
            else:
                src = dst if ins['op'] == 'apply' else ins['src']
                matrix = matrices[ins['operator'],ins['direction']]
                dot = [sum(a*b for a,b in zip(row,values[src])) for row in matrix]
                products += d*d
                if ins['op'] == 'apply':
                    result = [trunc(x,scale) for x in dot]
                else:
                    c = Q(ins['coefficient'])
                    result = [trunc(old*scale*c.denominator+c.numerator*x,scale*c.denominator)
                              for old,x in zip(values[dst],dot)]
                    scalar_products += d
            roundings += d
            values[dst] = result
        endpoints.append([values[role] for role in roles])
    difference = [[a-b for a,b in zip(left,right)] for left,right in zip(*endpoints)]
    value = Q(difference[output_index][0],scale)
    need(plan['error'] <= plan['separation']/4, 'unfunded numerical detector')
    return dict(nonzero=abs(value)>plan['separation']/2, value=value, endpoint_integers=difference,
                plan=plan, matrix_products=products, scalar_products=scalar_products,
                data_roundings=roundings, stored_matrix_entries=2*len(program['operators'])*d*d)
