"""Separate exact circuit and closed-convolution column calculations.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The canonical chart and native recipe definitions retain their source credit.
"""
from functools import lru_cache
from common import need


def rotate(z,q):
    a,b = z
    return ((a,b),(-b,a),(-a,-b),(b,-a))[q % 4]


def normalize(values,den):
    values = {i:z for i,z in values.items() if z != (0,0)}
    while den and all((a | b) & 1 == 0 for a,b in values.values()):
        values = {i:(a//2,b//2) for i,(a,b) in values.items()};den -= 1
    return values,den


def circuit_column(circuit,basis):
    values = {basis:(1,0)};den = 0
    for gate in circuit:
        out = {};tag = gate[0]
        for x,z in values.items():
            if tag == 'C':
                a,b = z;s = gate[2]
                terms = ((x,(a-s*b,b+s*a)),(x ^ gate[1],(a+s*b,b-s*a)))
            else:
                target = x
                if tag == 'P': target = sum(((row & x).bit_count() % 2) << i for i,row in enumerate(gate[1]))
                elif tag == 'X': target ^= gate[1]
                elif tag == 'phase': z = rotate(z,gate[1])
                elif tag == 'D':
                    q = sum(v for i,v in enumerate(gate[2]) if x >> i & 1)
                    q += 2*sum(((row >> (i+1)) & (x >> (i+1))).bit_count() for i,row in enumerate(gate[1]) if x >> i & 1)
                    z = rotate(z,q)
                else: raise ValueError('Unknown native gate')
                terms = ((target,z),)
            for target,(a,b) in terms:
                c,d = out.get(target,(0,0));out[target] = a+c,b+d
        values = out
        if tag == 'C': den += 1
    return normalize(values,den)


def adjoint(circuit):
    out = []
    for gate in reversed(circuit):
        tag = gate[0]
        if tag == 'P':
            perm = [sum(((row & x).bit_count() % 2) << i for i,row in enumerate(gate[1])) for x in range(512)]
            back = [0]*512
            for i,j in enumerate(perm): back[j] = i
            rows = [sum(((back[1 << j] >> i) & 1) << j for j in range(9)) for i in range(9)]
            out.append(['P',rows])
        elif tag == 'D': out.append(['D',gate[1],[-v % 4 for v in gate[2]]])
        elif tag == 'C': out.append(['C',gate[1],-gate[2]])
        elif tag == 'phase': out.append(['phase',-gate[1]])
        else:
            need(tag == 'X','Adjoint gate');out.append(gate)
    return out


@lru_cache(None)
def chart(vectors):
    if len(vectors) == 9: return tuple(range(512)),(0,)*512
    span = {0};columns = []
    for value in (*vectors,*(1 << j for j in range(9))):
        if value not in span:
            columns.append(value);span |= {v ^ value for v in tuple(span)}
    need(len(columns) == 9,'Independent chart completion')
    permutation = []
    for x in range(512):
        y = 0
        for i,v in enumerate(columns):
            if x >> i & 1: y ^= v
        permutation.append(y)
    inverse = [0]*512
    for x,y in enumerate(permutation): inverse[y] = x
    gi = [inverse[1 << i] for i in range(9)]
    quadratic = [[int(i == j) ^ ((gi[i] & gi[j]).bit_count() % 2) for j in range(9)] for i in range(9)]
    phases = []
    for x in range(512):
        bits = [i for i in range(9) if x >> i & 1]
        phases.append((sum(quadratic[i][i] for i in bits)+2*sum(quadratic[i][j] for i in bits for j in bits if i<j)) % 4)
    return tuple(permutation),tuple(phases)


@lru_cache(None)
def core(rank,sign):
    out = []
    for mask in range(1 << rank):
        a,b = 1,0
        for bit in range(rank):
            s = -sign if mask >> bit & 1 else sign
            a,b = a-s*b,b+s*a
        out.append((a,b))
    return tuple(out)


@lru_cache(None)
def frame_column(vectors,basis,sign):
    perm,phases = chart(vectors);rank = len(vectors)
    original = perm.index(basis)
    return {perm[original ^ mask]:rotate(z,phases[perm[original ^ mask]]-phases[basis])
            for mask,z in enumerate(core(rank,sign))},rank


def closed_column(old,new,basis):
    first,d1 = frame_column(tuple(old),basis,-1)
    out = {}
    for middle,(a,b) in first.items():
        second,d2 = frame_column(tuple(new),middle,1)
        for target,(c,d) in second.items():
            u,v = out.get(target,(0,0));out[target] = u+a*c-b*d,v+a*d+b*c
    return normalize(out,d1+d2)
