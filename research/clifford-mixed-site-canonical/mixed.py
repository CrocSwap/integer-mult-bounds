"""One-sided width-13 canonical queries for a row chart and one repeated input stabilizer."""
import argparse
from fractions import Fraction
from functools import cache, reduce
import json
from operator import xor
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/"predecessor"))
from adjoint import Q, IDENTITY, eliminate, evaluate_forms, linear_forms, solution, substitute_form, validate
from canonical import distance, point_set, quotient, unitary
from compile_row import apply, is_symplectic, span
from spherical import spherical_solution

ZERO = (4,0,(),(),0,0,0)


def geometry(basis):
    """Coordinates t in the X-projection, with a symmetric phase lift on each coset."""
    xs, zs = [], []
    pivots = {}
    for g in basis:
        x,z = divmod(g,16)
        if Q.coordinates(pivots,x) is None:
            xs.append(x)
            zs.append(z)
            pivots = Q.basis(xs)
    idx = sorted(pivots)
    cols = [pivots[i][0] for i in idx]
    zs = [reduce(xor,(zs[k] for k in Q.bits(pivots[i][1])),0) for i in idx]
    phase = {}
    for i,z in enumerate(zs):
        if (z & cols[i]).bit_count()%2:
            phase[1<<i] = 1
        for j,x in enumerate(cols[:i]):
            if (z & x).bit_count()%2:
                phase[(1<<i)|(1<<j)] = 2
    return idx,cols,phase


@cache
def vertices():
    basis,points,_ = quotient()
    return tuple((pt,geometry(b)) for b,pt in zip(basis,points,strict=True))


@cache
def inverse_kernel():
    eigen = spherical_solution()[2]
    return tuple(sum(Fraction(degree,2295)*u[j]/lam for _,degree,lam,u in eigen) for j in range(5))


def scale(chart):
    """Four-bit chart to list of (computational row, Gaussian rational) pairs."""
    _,offset,columns,terms,a,b,e = chart
    if not (a or b):
        return []
    out = []
    for t in range(1<<len(columns)):
        r = reduce(xor,(columns[i] for i in Q.bits(t)),offset)
        v = Q.multiply_i((a,b),Q.value(dict(terms),t))
        out.append((r,(Fraction(v[0],1<<e),Fraction(v[1],1<<e))))
    return out


class Producer:
    def __init__(self,chart):
        validate(chart,52)
        _,off,cols,terms,a,b,self.den = chart
        self.rank = len(cols)
        self.scalar = a,b
        self.phase = {s<<4:v for s,v in terms}
        raw = [((f>>1)<<5)|(f&1) for f in linear_forms(off,cols,52)]
        self.blocks = [raw[j:j+4] for j in range(0,52,4)]
        self.rows = [(off >> j)&15 for j in range(0,52,4)]
        self.parity = reduce(xor,self.rows)
        self.y = [2<<j for j in range(4)]

    def coordinate(self,geo):
        idx,cols,q = geo
        def t(r):
            return sum(((r>>j)&1)<<i for i,j in enumerate(idx))
        for r in self.rows:
            diff = r ^ self.parity
            if reduce(xor,(cols[i] for i in Q.bits(t(diff))),0) != diff:
                return ZERO
        angle = Q.value(q,t(self.parity))-sum(Q.value(q,t(r)) for r in self.rows)
        a,b = Q.multiply_i(self.scalar,angle+2*len(idx)+self.phase.get(0,0))
        return 4,self.parity,(),(),a,b,self.den+6*len(idx)

    def feature(self,geo):
        if self.scalar==(0,0):
            return ZERO
        if self.rank==0:
            return self.coordinate(geo)
        idx,cols,q = geo
        equations = []
        def constrain(f):
            if f:
                equations.append((f>>1,f&1))
        for j,y in enumerate(self.y):
            constrain(reduce(xor,(r[j] for r in self.blocks),y))
        phase = dict(self.phase)
        for mask,v in Q.substitute(q,[self.y[j] for j in idx]).items():
            Q.term(phase,mask,v)
        for r in self.blocks:
            coords = [r[i] for i in idx]
            for j in range(4):
                if j not in idx:
                    constrain(reduce(xor,(r[i]^self.y[i] for i,c in zip(idx,cols,strict=True)
                                          if c>>j&1),r[j]^self.y[j]))
            for mask,v in Q.substitute(q,coords).items():
                Q.term(phase,mask,-v)
        solved = solution(4+self.rank,equations)
        if solved is None:
            return ZERO
        n,forms = solved
        labels = forms[:4]
        mask = reduce(int.__or__,(f>>1 for f in labels),0)
        fixed = mask.bit_length()
        Q.need(mask == (1<<fixed)-1,"Free label bits are not a prefix")
        reduced = eliminate(n,fixed,Q.substitute(phase,forms))
        if reduced is None:
            return ZERO
        rank,pars,poly,factor = reduced
        label = [substitute_form(f,pars) for f in labels]
        offset = evaluate_forms(label,0)
        columns = tuple(evaluate_forms(label,1<<j)^offset for j in range(rank))
        a,b = Q.multiply_i(Q.multiply(self.scalar,factor),poly.pop(0,0)+2*len(idx))
        (a,b),e = Q.normalize((a,b),self.den+6*len(idx))
        return 4,offset,columns,tuple(sorted(poly.items())),a,b,e


class Decoder:
    def __init__(self,chart):
        producer = Producer(chart)
        self.features = tuple((point,scale(producer.feature(geo))) for point,geo in vertices())
        self.vectors = {}

    def vector(self,point):
        if point not in self.vectors:
            h = inverse_kernel()
            sums = [[0,0] for _ in range(16)]
            for loc,entries in self.features:
                weight = h[distance(point,loc)]
                for r,(a,b) in entries:
                    sums[r][0] += weight*a
                    sums[r][1] += weight*b
            self.vectors[point] = tuple(tuple(v) for v in sums)
        return self.vectors[point]

    def coefficient(self,target,p,right_basis=IDENTITY,column=0):
        target,right_basis = tuple(target),tuple(right_basis)
        Q.need(is_symplectic(target) and is_symplectic(right_basis),"Invalid symplectic map")
        Q.validate_integer(p,256,"Invalid Pauli label")
        Q.validate_integer(column,16,"Invalid stabilizer basis column")
        point = point_set(tuple(apply(target,v) for v in right_basis[:4]))
        d = self.vector(point)
        x,z = divmod(p,16)
        mid,l1 = unitary(target)
        right,l2 = unitary(right_basis)
        a = b = 0
        for r,(u,v) in enumerate(d):
            if not (u or v):
                continue
            m=n=0
            for j in range(16):
                s,t=Q.multiply(mid[(r^x)|(j<<4)],right[j|(column<<4)])
                m+=s
                n+=t
            sg = -1 if ((r^x)&z).bit_count()%2 else 1
            a+=sg*(m*u+n*v)
            b+=sg*(m*v-n*u)
        den = 1<<(26+l1+l2)
        return Fraction(a,den),Fraction(b,den)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request",type=Path)
    obj=json.loads(parser.parse_args().request.read_text())
    decoder=Decoder(obj["row_chart"])
    print(json.dumps([[str(v) for v in decoder.coefficient(S,p,obj.get("right_basis",IDENTITY),
                    obj.get("column",0))] for S,p in obj["queries"]]))
