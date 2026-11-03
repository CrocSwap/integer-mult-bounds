"""Compile coupled G20 carry states to explicit finite tables.

The carry identity is from PR6474 and the retained fused G20 construction.
Partition refinement is classical. Ali Romman with OpenAI Codex assistance.
Apache-2.0.
"""
from fractions import Fraction as Q
from math import lcm


def require(ok,message):
    if not ok:raise ValueError(message)


def columns(source):
    for basis in ('ports','scale_free_ports'):
        require([r['port'] for r in source[basis]] == list(range(111)), 'all released ports')
        for record in source[basis]:
            for direction in ('forward','inverse'):
                rows = [[Q(i == j) for j in range(8)] for i in range(8)]
                for e in record[direction]:
                    for row in rows:
                        if e[0] == 'ADD':row[e[2]] += Q(e[-1])*row[e[1]]
                        else:
                            require(e[0] == 'SCALE','source operation')
                            row[e[1]] *= Q(e[-1])
                for j,col in enumerate(zip(*rows)):
                    yield [basis,record['port'],direction,j],col


def plan(column):
    d = lcm(*(v.denominator for v in column))
    require(d in (1,4),'released denominator')
    a = tuple(int(d*v) for v in column)
    lo = sum(min(v,0) for v in a);positive = sum(max(v,0) for v in a)
    hi = max(0,positive-1)
    sums = {0}
    for v in a:sums |= {s+v for s in tuple(sums)}
    return a,d,(lo,hi,tuple(sorted(sums)))


def classify(keys):
    indices = {};result = []
    for key in keys:
        if key not in indices:indices[key] = len(indices)
        result.append(indices[key])
    return result


def compile_model(model):
    lo,hi,digits = model;thresholds = tuple(range(lo+1,hi+1))
    alphabet = [(s,b) for s in digits for b in (0,1)]
    zero = (0,)*len(thresholds);states = [zero];index = {zero:0};edges = []
    for state in states:
        row = []
        for digit,bit in alphabet:
            nxt = tuple((v+digit-j*bit)//2 for v,j in zip(state,thresholds))
            if nxt not in index:
                require(len(states) < 20000,'bounded reachable-state search')
                index[nxt] = len(states);states.append(nxt)
            row.append(index[nxt])
        edges.append(row)
    output = [lo+sum(v >= 0 for v in state) for state in states]
    groups = classify(output);levels = [groups];rounds = 0
    while True:
        nxt = classify((output[i],tuple(groups[j] for j in edges[i])) for i in range(len(states)))
        rounds += 1
        if nxt == groups:break
        groups = nxt
        levels.append(groups)
    representatives = [groups.index(i) for i in range(max(groups)+1)]
    return dict(model=[lo,hi,list(digits)],alphabet=[list(a) for a in alphabet],
                states=[list(s) for s in states],edges=edges,output=output,groups=groups,
                levels=levels,
                compact_edges=[[groups[j] for j in edges[i]] for i in representatives],
                compact_output=[output[i] for i in representatives],start=groups[0],refinement_rounds=rounds)


def read_bits(data,offset,width):
    value = 0
    for i in range(width):value |= ((data[(offset+i)//8] >> ((offset+i)%8)) & 1) << i
    return value


def pack(tables):
    data = bytearray();position = 0;descriptors = []
    def append(value,width):
        nonlocal position
        require(0 <= value < (1 << width),'packed value range')
        for i in range(width):
            if position//8 == len(data):data.append(0)
            data[position//8] |= ((value >> i) & 1) << (position%8)
            position += 1
    for c in tables:
        count = len(c['compact_output']);width = (count-1).bit_length()
        d = dict(model=c['model'],states=count,index_bits=width,start=c['start'],
                 output_offset=position)
        for v in c['compact_output']:append(v+16,5)
        d['edge_offset'] = position
        for row in c['compact_edges']:
            for v in row:append(v,width)
        descriptors.append(d)
    return descriptors,bytes(data),position


def produce(column,machine,data,rows):
    coefficients,denominator,model = plan(column)
    require(machine['model'] == [model[0],model[1],list(model[2])], 'column model binding')
    alphabet = {(s,b):i for i,(s,b) in enumerate((s,b) for s in model[2] for b in (0,1))}
    state = machine['start'];compare = [0]*8;residue = radix_high = phase = 0
    last = 0
    for row in rows:
        require(type(row) in (list,tuple) and len(row) == 9 and all(type(v) is int and v in (0,1) for v in row),'nine binary symbols')
        bits,bit = row[:8],row[8]
        if phase == 0:require(bit == 1,'odd radix')
        last = bit
        digit = sum(a*b for a,b in zip(coefficients,bits))
        offset = machine['edge_offset']+(state*len(alphabet)+alphabet[digit,bit])*machine['index_bits']
        state = read_bits(data,offset,machine['index_bits'])
        compare = [(a+b-bit)//2 for a,b in zip(compare,bits)]
        if phase < 2:
            residue = (residue+(digit << phase)) % denominator
            if phase == 1:radix_high = bit
            phase += 1
    require(phase > 0 and last == 1,'canonical radix ending')
    require(all(v == -1 for v in compare),'canonical low inputs')
    u = read_bits(data,machine['output_offset']+5*state,5)-16
    c = u-(u-residue*(1+2*radix_high)) % denominator
    k = c*(4//denominator)
    require(-16 <= k <= 12,'packet envelope')
    return tuple(((k+16) >> bit) & 1 for bit in range(5))
