"""Exact width-13 Hilbert adjoint on a supplied affine-quadratic observation."""
import argparse
from functools import cache, reduce
import json
from operator import xor
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE / 'source' / sub) for sub in ('engine', 'row')]
from contractions import Q, conjugate, power, solution
from bell_reads import decompose
from compile_row import IDENTITY, is_symplectic


def evaluate_form(form, argument):
    return (form & 1) ^ ((form >> 1) & argument).bit_count() % 2


def linear_forms(offset, columns, width):
    return [((offset >> i) & 1) | sum(((c >> i) & 1) << (j+1)
                                       for j,c in enumerate(columns)) for i in range(width)]


def evaluate_forms(forms, argument):
    return sum(evaluate_form(f,argument) << j for j,f in enumerate(forms))


def substitute_form(f, forms):
    return reduce(xor, (forms[j] for j in Q.bits(f >> 1)), f & 1)


def validate(chart, n):
    width, offset, cols, terms, a, b, e = chart
    Q.need(width == n and all(type(x) is int for x in (width,a,b,e)) and e >= 0,
           "Invalid chart width or scalar")
    Q.validate_integer(offset,1 << n,"Invalid chart offset")
    for col in cols:
        Q.validate_integer(col,1 << n,"Invalid support column")
    Q.basis(cols)
    phase = dict(terms)
    Q.need(len(phase)==len(terms),"Repeated phase monomial")
    for m,v in phase.items():
        Q.validate_integer(m,1 << len(cols),"Invalid phase monomial")
        Q.need(type(v) is int and 1 <= v <= 3 and
               (m.bit_count() <= 1 or (m.bit_count() == 2 and v == 2)),"Invalid quadratic phase")


def table(target):
    """Normalized Choi numerators at local address r+16c; common denominator 2**e."""
    Q.need(is_symplectic(target) and all(type(v) is int for v in target), "Invalid symplectic map")
    axes = decompose(target)
    values = [(int((j & 15) == (j >> 4)),0) for j in range(256)]
    for axis in axes:
        x,z = divmod(axis,16)
        updated = []
        for j,(a,b) in enumerate(values):
            e = 1 + ((x & z).bit_count() & 1) + 2*((z & (j ^ x)).bit_count() & 1)
            u,v = Q.multiply_i(values[j ^ x],e)
            updated.append(Q.multiply((1,1),(a+u,b+v)))
        values = updated
    return values, len(axes)+2


@cache
def site(target):
    vals, den = table(target)
    active = [j for j,x in enumerate(vals) if x != (0,0)]
    origin = min(active)
    independent = []
    pivots = {}
    for j in active:
        u = j ^ origin
        if Q.coordinates(pivots, u) is None:
            independent.append(u)
            pivots = Q.basis(independent)
    positions = sorted(pivots)
    columns = [pivots[j][0] for j in positions]
    rotations = [Q.multiply_i(vals[origin],k) for k in range(4)]
    phase = {1 << i: rotations.index(vals[origin ^ c]) for i,c in enumerate(columns)}
    for i,c in enumerate(columns):
        for h,d in enumerate(columns[:i]):
            value = (rotations.index(vals[origin ^ c ^ d]) - phase[1<<i] - phase[1<<h]) % 4
            Q.need(value in (0,2),"Nonquadratic Choi phase")
            if value:
                phase[(1<<i)|(1<<h)] = value
    phase = {k:v for k,v in phase.items() if v}
    for j,value in enumerate(vals):
        coords = sum((((j ^ origin) >> i) & 1) << h for h,i in enumerate(positions))
        reconstructed = reduce(xor,(columns[h] for h in Q.bits(coords)),origin)
        expected = rotations[Q.value(phase,coords)] if reconstructed == j else (0,0)
        Q.need(value==expected,"Single-site affine phase reconstruction")
    return origin, positions, columns, phase, vals[origin], den


def eliminate(n, fixed, phase):
    """Sum n-fixed Boolean variables, retaining the affine conditions on the fixed ones."""
    scalar = (1,0)
    constraints = []
    while n > fixed:
        n -= 1
        last = 1 << n
        a = phase.pop(last,0)
        neighbours = 0
        for mask in tuple(phase):
            if mask & last:
                neighbours ^= mask ^ last
                del phase[mask]
        if a & 1:
            scalar = Q.multiply(scalar,(1,1 if a == 1 else -1))
            Q.affine(phase,neighbours << 1,-a)
            continue
        scalar = (2*scalar[0],2*scalar[1])
        if neighbours >> fixed:
            # Solve a second *summed* variable. No factor accompanies fixing this bit.
            _,forms = solution(n,[(neighbours,a//2)])
            phase = Q.substitute(phase,forms)
            n -= 1
        else:
            constraints.append((neighbours,a//2))
    resolved = solution(fixed,constraints)
    if resolved is None:
        return None
    rank, forms = resolved
    return rank, forms, Q.substitute(phase,forms), scalar


class Observation:
    def __init__(self, chart):
        validate(chart,104)
        _,offset,columns,terms,a,b,self.denominator = chart
        self.rank = len(columns)
        self.scalar = (a,b)
        self.phase = dict(terms)
        # The high half of each address is the physical row, the low half its column.
        raw = linear_forms(offset,columns,104)
        raw = [((f >> 1) << 9) | (f & 1) for f in raw]
        self.blocks = []
        for t in range(13):
            rows = [raw[52+4*t+j] ^ (1 << (5+j)) for j in range(4)]
            self.blocks.append(rows + raw[4*t:4*t+4])

    def fibre(self,target):
        origin,pivots,cols,local,anchor,den = site(tuple(target))
        equations = []
        phase = {k << 8:v for k,v in self.phase.items()}
        for block in self.blocks:
            displaced = [f ^ ((origin >> j) & 1) for j,f in enumerate(block)]
            coords = [displaced[j] for j in pivots]
            for j in range(8):
                if j not in pivots:
                    eq = reduce(xor,(coord for col,coord in zip(cols,coords,strict=True) if col >> j & 1),
                                displaced[j])
                    equations.append((eq >> 1,eq & 1))
            for k,v in Q.substitute(local,coords).items():
                Q.term(phase,k,-v)
            for j in range(4):
                Q.product(phase,1 << (1+j),block[j])
        zero = (8,0,(),(),0,0,0)
        resolved = solution(8+self.rank,equations)
        if resolved is None or self.scalar == (0,0):
            return zero
        n,forms = resolved
        labels = forms[:8]
        # Highest-pivot elimination leaves a prefix of free label variables before observations.
        label_mask = reduce(int.__or__,(f >> 1 for f in labels),0)
        fixed = label_mask.bit_length()
        Q.need(label_mask == (1 << fixed)-1,"Noncontiguous free labels")
        summed = eliminate(n,fixed,Q.substitute(phase,forms))
        if summed is None:
            return zero
        rank, pars, q, scale = summed
        label = [substitute_form(f,pars) for f in labels]
        offset = evaluate_forms(label,0)
        columns = tuple(evaluate_forms(label,1 << j) ^ offset for j in range(rank))
        scalar = Q.multiply(Q.multiply(self.scalar,power(conjugate(anchor),13)),scale)
        scalar = Q.multiply_i(scalar,q.pop(0,0))
        (a,b),e = Q.normalize(scalar,self.denominator+13*den)
        return 8,offset,columns,tuple(sorted(q.items())),a,b,e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    request = json.loads(parser.parse_args().input.read_text())
    if ('chart' in request) == ('circuit' in request):
        parser.error("Supply exactly one of chart or circuit")
    chart = request['chart'] if 'chart' in request else Q.signature(104,request['circuit'],request.get('initial',0))
    observation = Observation(chart)
    print(json.dumps([observation.fibre(target) for target in request['targets']]))
