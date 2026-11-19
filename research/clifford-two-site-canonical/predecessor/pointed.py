"""Canonical 12+1 readout via pointed Lagrangians. All coefficient pairs are Gaussian rational."""
import argparse
from collections import Counter
from fractions import Fraction
from functools import cache
import json
from math import lcm
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'predecessor'))
from canonical import IDENTITY, ORDER, conjugate, distance, point_set, quotient, transition
from adjoint import Q
from compile_row import apply, compose, inverse, is_symplectic, pairing, span

BASE = (1 << 16)-1
NFLAGS = 34425


def require(ok, message):
    if not ok:
        raise ValueError(message)


def relation(L, v, X, w):
    """Ordered orbit of (L,v),(X,w); marks must be nonzero members."""
    return (distance(L,X), int(v==w), (X>>v)&1, (L>>w)&1, pairing(v,w))


@cache
def geometry():
    bases,spaces,rings = quotient()
    elems = [span(B) for B in bases]
    flags = [(L,v) for L,vs in zip(spaces,elems,strict=True) for v in vs if v]
    counts = Counter(relation(BASE,1,L,v) for L,v in flags)
    reps = {relation(BASE,1,L,v):(L,v) for L,v in flags}
    require(len(flags)==NFLAGS and list(counts.values()).count(0)==0,"flag inventory")
    return spaces,elems,counts,reps


def class_inverse(data):
    classes = data['classes']
    rows = data['characters']
    coeffs = []
    for chi in rows:
        n,rem = divmod(sum(c['size']*a*a for c,a in zip(classes,chi,strict=True)),ORDER)
        require(not rem and chi[0]%n==0,"ordinary packet size")
        degree = chi[0]//n
        eig = Fraction(sum(c['size']*a*(-64)**c['fixed'] for c,a in zip(classes,chi,strict=True)),
                       chi[0]*16**12)
        coeffs.append(degree/eig)
    den = lcm(*(x.denominator for x in coeffs))
    nums = [(x*den).numerator for x in coeffs]
    return [Fraction(sum(v*c for v,c in zip(col,nums,strict=True)),den*ORDER)
            for col in zip(*rows,strict=True)]


@cache
def orbital_kernels():
    data = json.loads((HERE/'predecessor'/'source'/'CLASS-ALGEBRA.json').read_text())
    spaces,elems,counts,_ = geometry()
    gram,recip = Counter(),Counter()
    for c,reciprocal in zip(data['classes'],class_inverse(data),strict=True):
        old = None
        for S in c['representatives']:
            action = [apply(S,v) for v in range(256)]
            obs = Counter()
            for L,vs in zip(spaces,elems,strict=True):
                ws = [action[v] for v in vs]
                X = sum(1<<w for w in ws)
                j = distance(L,X)
                for v,w in zip(vs[1:],ws[1:],strict=True):
                    obs[(j,int(v==w),(X>>v)&1,(L>>w)&1,pairing(v,w))] += 1
            if old is not None:
                require(old==obs,"rationally fused classes have unequal displacement census")
            old=obs
        for key,n in old.items():
            mass=c['size']*n
            gram[key]+=mass*(-64)**c['fixed']
            recip[key]+=mass*reciprocal
    G = {k:Fraction(gram[k],NFLAGS*m*16**12) for k,m in counts.items()}
    I = {k:recip[k]/(NFLAGS*m) for k,m in counts.items()}
    return G,I


def rhs(j):
    return Fraction(1,4**13)*Fraction(-1,64)**j/(1<<(4-j))


@cache
def weights():
    """Scalar weights for the unmarked summand and every ordered pointed pair."""
    spaces,_,_,reps = geometry()
    _,kernel = orbital_kernels()
    # Recover the unmarked kernel by summing inverse transition weights over
    # all marked target points at a fixed Lagrangian, starting at one marked flag.
    by_shell = {}
    bases,_,rings = quotient()
    for B,L,j in zip(bases,spaces,rings,strict=True):
        if j not in by_shell:
            by_shell[j]=sum(kernel[relation(BASE,1,L,v)] for v in span(B) if v)
    unmarked=[]
    candidates = {j:L for j,L in zip(rings,spaces,strict=True)}
    for j in range(5):
        X=candidates[j]
        unmarked.append(sum(by_shell[distance(X,Y)]*rhs(i) for Y,i in zip(spaces,rings,strict=True)))
    restricted = [(Y,rhs(i)) for Y,i in zip(spaces,rings,strict=True) if (Y>>1)&1]
    pointed = {k:sum(kernel[relation(X,x,Y,1)]*b for Y,b in restricted)
               for k,(X,x) in reps.items()}
    return tuple(unmarked),pointed


def transformed_inputs(target,left_basis,right_basis):
    for S in (target,left_basis,right_basis):
        require(is_symplectic(S),"four-qubit symplectic map required")
    return compose(inverse(tuple(left_basis)),compose(tuple(target),tuple(right_basis)))


def site_weights(relative,r,c,unmarked,pointed):
    """Walsh factors indexed in the repeated site's left and right bases."""
    require(type(r) is int and type(c) is int and 0<=r<16 and 0<=c<16,"invalid repeated-site labels")
    X=point_set(relative[:4])
    raw=[Fraction(0)]*256
    raw[0]=unmarked[distance(BASE,X)]
    for v in range(1,16):
        w=apply(relative,v)
        for u in range(1,16):
            raw[u | (v<<4)]=pointed[relation(BASE,u,X,w)]
    for bit in range(8):
        shift=1<<bit
        for k in range(256):
            if not k & shift:
                a,b=raw[k],raw[k^shift]
                raw[k],raw[k^shift]=a+b,a-b
    return [raw[k^(r | (c<<4))] for k in range(256)]


def coefficient(target,p,r,c,C,left_basis=IDENTITY,right_basis=IDENTITY):
    """C is an iterable of (i,j,(re,im)) in the indicated stabilizer bases."""
    relative=transformed_inputs(target,left_basis,right_basis)
    factors=site_weights(relative,r,c,*weights())
    real=imag=Fraction(0)
    for i,j,g in C:
        require(type(i) is int and type(j) is int and 0<=i<16 and 0<=j<16,"invalid singleton coordinate")
        value=conjugate(transition(tuple(target),p,i,j,tuple(left_basis),tuple(right_basis)))
        term=Q.multiply(value,g)
        h=factors[i | (j<<4)]
        real+=term[0]*h
        imag+=term[1]*h
    return real,imag


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('request',type=Path)
    req=json.loads(ap.parse_args().request.read_text())
    terms=[(i,j,tuple(map(Fraction,g))) for i,j,g in req['singleton']]
    outs=[coefficient(S,p,req['row'],req['column'],terms,req.get('left_basis',IDENTITY),
                      req.get('right_basis',IDENTITY)) for S,p in req['queries']]
    print(json.dumps([[str(a),str(b)] for a,b in outs]))
