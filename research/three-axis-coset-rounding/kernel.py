"""An eight-point Gaussian coset map with an exact inverse.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from bisect import bisect_left
import importlib.util
from pathlib import Path
import struct

P = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def retained(name):
    spec = importlib.util.spec_from_file_location('retained_'+name, P/'inputs'/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


two = retained('two/kernel')
baseline = retained('baseline')


def matrix():
    rows = [[0]*16 for _ in range(16)]
    phases = ((-1,1),(1,1),(1,-1),(-1,-1))
    for j in range(8):
        for k in range(8):
            a,b = phases[(j ^ k).bit_count() % 4]
            rows[2*j][2*k],rows[2*j][2*k+1] = a,-b
            rows[2*j+1][2*k],rows[2*j+1][2*k+1] = b,a
    return rows


def multiply(rows, x):
    return tuple(sum(a*b for a,b in zip(row,x)) for row in rows)


def reversed_pairs(x):
    return tuple(v for i in range(7,-1,-1) for v in x[2*i:2*i+2])


class Table:
    def __init__(self, data):
        need(len(data) == 64*48, 'Exact coset table size')
        self.rows = [struct.unpack('16B32b',data[i:i+48]) for i in range(0,len(data),48)]
        self.keys = [row[:16] for row in self.rows]
        need(self.keys == sorted(set(self.keys)), 'Distinct sorted coset keys')

    def offset(self, key, sign):
        i = bisect_left(self.keys, key)
        need(i < len(self.keys) and self.keys[i] == key, 'Known lattice coset')
        return self.rows[i][16:32] if sign == 1 else self.rows[i][32:48]


def block(values, width, table, sign=1, trace=None):
    need(type(width) is int and width >= 2 and type(sign) is int and sign in (-1,1), 'Block format')
    need(len(values) == 8 and all(len(z) == 2 for z in values), 'Eight Gaussian words')
    trace = trace if trace is not None else {}
    def word(v):
        need(type(v) is int and -(1 << (width-1)) <= v < (1 << (width-1)), 'Signed word overflow')
        trace['checked_values'] = trace.get('checked_values',0)+1
        trace['peak_integer'] = max(trace.get('peak_integer',0),abs(v))
        return v
    def rotate(z,q):
        a,b = z
        q %= 4
        if q == 0: return a,b
        if q == 1: return -b,a
        if q == 2: return -a,-b
        return b,-a
    x = [tuple(map(word,z)) for z in values]
    x = [tuple(map(word,rotate(z,-sign*i.bit_count()))) for i,z in enumerate(x)]
    for bit in range(3):
        step = 1 << bit
        for base in range(0,8,2*step):
            for low in range(step):
                i,j = base+low,base+low+step
                a,b = x[i];c,d = x[j]
                x[i] = word(a+c),word(b+d)
                x[j] = word(a-c),word(b-d)
    x = [tuple(map(word,rotate(z,-sign*i.bit_count()))) for i,z in enumerate(x)]
    nums = tuple(v for a,b in x for v in ((word(-a-b),word(a-b)) if sign == 1
                                         else (word(b-a),word(-a-b))))
    key = tuple(v % 4 for v in (nums if sign == 1 else reversed_pairs(nums)))
    offset = table.offset(key,sign)
    out = []
    for a,b in zip(nums,offset):
        n = word(a+b)
        need(n % 4 == 0, 'Exact quarter shift')
        out.append(word(n >> 2))
    for key,count in dict(three_blocks=1,data_additions=80,data_quarter_shifts=16,
                          residue_reads=16,table_offset_reads=16,checked_divisibilities=16,
                          data_negations=28,component_swaps=8).items():
        trace[key] = trace.get(key,0)+count
    return tuple(zip(out[::2],out[1::2]))


def plan(f):
    need(type(f) is int and f >= 1, 'Positive axis count')
    if f == 1:
        return [1]
    q,r = divmod(f,3)
    if r == 1:
        return [3]*(q-1)+[2,2]
    return [3]*q+([2] if r == 2 else [])


def make_call(table):
    def call(values,f,axis,width,adjoint=False,trace=None):
        need(type(axis) is int and axis in (0,2) and len(values) == 8**f
             and type(adjoint) is bool, 'Literal Gaussian call dimensions')
        groups = [];start = 0
        for size in plan(f):
            groups.append(tuple(3*j+axis for j in range(start,start+size)))
            start += size
        if adjoint:
            groups.reverse()
        sign = -1 if adjoint else 1
        for bits in groups:
            if len(bits) == 1:
                baseline.layer(values,bits[0],width,sign,trace)
            elif len(bits) == 2:
                two.group(values,*bits,width,sign,trace)
            else:
                mask = sum(1 << bit for bit in bits)
                for base in range(len(values)):
                    if base & mask == 0:
                        indices = [base | sum(((k >> j) & 1) << bit for j,bit in enumerate(bits)) for k in range(8)]
                        out = block([values[k] for k in indices],width,table,sign,trace)
                        for k,z in zip(indices,out):
                            values[k] = z
        return values
    return call
