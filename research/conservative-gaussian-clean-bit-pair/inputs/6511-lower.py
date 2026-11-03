"""Bind the credited one-carry and paired SCALE circuits to selected P104.

PR3152 supplies scalar primitives; PR3159 supplies paired negation.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def need(ok,message):
    if not ok:raise ValueError(message)


def circuit(width,op,coefficient,scalar,binary,readonly):
    q = Q(coefficient)
    if op == 'ADD':return scalar.circuit(width,'add',q.numerator,q.denominator,[],binary.terms(q.numerator,q.denominator))
    if op == 'COPY':
        need(q == 1,'selected COPY coefficient')
        return [(width+i,i) for i in range(width)]
    need(op == 'SCALE' and abs(q.numerator).bit_count() == q.denominator.bit_count() == 1,'dyadic unit SCALE')
    exponent = abs(q.numerator).bit_length()-q.denominator.bit_length()
    offset = abs(exponent)
    real = tuple(range(offset,width));imag = tuple(range(width+offset,2*width));gates = []
    if q < 0:
        add = scalar.adder(imag,real,2*width)
        subtract_twice = list(reversed(scalar.adder(real[:-1],imag[1:],2*width)))
        gates = add+subtract_twice+add+subtract_twice
    fill = [('cx',('t',width-1),('t',i)) for i in range(offset)]
    rotation = readonly.rotate(width,exponent)
    raw_shift = rotation+fill if exponent >= 0 else fill+rotation
    need(all(g[0] == 'cx' and all(w[0] == 't' for w in g[1:]) for g in raw_shift),'single-component direct shift')
    shift = [tuple(w[1] for w in g[1:]) for g in raw_shift]
    shift += [tuple(i+width for i in g) for g in shift]
    gates = shift+gates if exponent >= 0 else gates+shift
    scalar.validate(width,gates)
    return gates


def apply(gates,first,second,width):
    """Execute the literal two-bank circuit with one initially zero carry."""
    state = first | (second << width)
    for gate in gates:
        control = (state >> gate[0]) & 1
        if len(gate) == 3:control &= (state >> gate[1]) & 1
        if control:state ^= 1 << gate[-1]
    need(state >> (2*width) == 0,'clean carry return')
    mask = (1 << width)-1
    return state & mask,(state >> width)&mask
