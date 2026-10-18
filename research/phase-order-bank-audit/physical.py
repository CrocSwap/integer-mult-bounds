"""Separate exact rational physical-array check; no symbolic checker imports.
Dennis / antunishdPursuit with OpenAI Codex. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256


def need(ok,message):
    if not ok:
        raise ValueError(message)


def transform(data,axis,inverse=False,omit_scale=False):
    bit = 1 << axis
    out = data[:]
    divisor = 1 if inverse or omit_scale else 2
    for a in range(len(data)):
        if not a & bit:
            b = a | bit
            out[a] = (data[a]+data[b])/divisor
            out[b] = (data[a]-data[b])/divisor
    return out


def translate(data,source,target):
    out = [Fraction(0)]*len(data)
    for address,value in enumerate(data):
        out[address ^ (((address >> source)&1) << target)] = value
    return out


def program(f,order,colors,column,omit_scale=False,omit_last=False):
    b = max(colors)+1
    data = [Fraction(0)]*(1 << (2*f+b))
    data[column] = Fraction(1)
    sequence = [*range(f),*order]
    if omit_last:
        sequence.pop()
    for j in sequence:
        c = 2*f+colors[j]
        data = translate(data,c,j)
        data = transform(data,c,omit_scale=omit_scale)
        data = translate(data,c,f+j)
        data = transform(data,c,inverse=True)
    return data


def kernel(f,b,column):
    mask = (1 << f)-1
    result = []
    for row in range(1 << (2*f+b)):
        if row >> (2*f) != column >> (2*f):
            result.append(Fraction(0))
        else:
            delta = row ^ column
            parity = ((delta & mask) & ((delta >> f)&mask)).bit_count()%2
            result.append(Fraction(-1 if parity else 1,1 << f))
    return result


def run_checks():
    fixtures = [(1,(0,),(0,)),(2,(1,0),(0,0)),(2,(0,1),(0,1)),
                (3,(2,1,0),(0,0,0)),(3,(2,0,1),(0,1,0))]
    digest, columns = sha256(),0
    summary = []
    for f,order,colors in fixtures:
        b = max(colors)+1
        count = 1 << (2*f+b)
        for column in range(count):
            values = program(f,order,colors,column)
            need(values == kernel(f,b,column),'complete physical column differs')
            for value in values:
                digest.update(f'{value.numerator}/{value.denominator};'.encode())
            columns += 1
        summary.append({'f':f,'consumer_order':list(order),'bank_assignment':list(colors),
                        'bank_bits':b,'complete_columns':count})
    mutations = [('same-order shared bank',2,(0,1),(0,0),{}),
                 ('missing Hadamard scale',1,(0,),(0,),{'omit_scale':True}),
                 ('omitted final consumer',2,(1,0),(0,0),{'omit_last':True})]
    witnesses = []
    for name,f,order,colors,options in mutations:
        b = max(colors)+1
        for col in range(1 << (2*f+b)):
            actual,expected = program(f,order,colors,col,**options),kernel(f,b,col)
            if actual != expected:
                row = next(i for i,(a,e) in enumerate(zip(actual,expected)) if a != e)
                witnesses.append({'mutation':name,'column':col,'row':row,
                                  'actual':str(actual[row]),'expected':str(expected[row])})
                break
        else:
            raise ValueError('physical mutant escaped: '+name)
    return {'fixtures':summary,'complete_columns':columns,
            'exact_matrix_sha256':digest.hexdigest(),'rejected_controls':len(witnesses),
            'failure_witnesses':witnesses,
            'arithmetic':'Fraction rational physical H0/H0-inverse and controlled XOR; no C/native invoice replay'}
