"""Independent dense Gaussian-integer matrix oracle against the runtime numerator circuit."""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from random import Random
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from producer import ODD,SHIFT,producer
from physical import TRACKS,loc
from readout import encode

# Literal rational spectral weights from the predecessor canonical normal equations.
PROFILE = [Fraction(279183413,16081633325721600),Fraction(52701673,32163266651443200),
           Fraction(36859,253254068121600),-Fraction(777583,64326533302886400),
           -Fraction(14688133,1029224532846182400)]


def mono_state(data,column):
    out=data['shift']
    exponent=0
    for i,row in enumerate(data['rows']):
        out ^= ((row&column).bit_count()%2)<<i
        if column>>i&1:
            exponent+=data['linear'][i]
    for k,(i,j) in enumerate(combinations(range(4),2)):
        if ((data['cross']>>k)&(column>>i)&(column>>j)&1):
            exponent+=2
    return out,(1j)**(exponent%4)


def matrix(req):
    """Expand every normalized Hadamard path on integer numerators; accumulate its phase."""
    cols=[]
    for c in range(16):
        mid,phase=mono_state(req['right'],c)
        v=[0j]*16
        v[mid]=phase
        for i in range(4):
            if (req['mask']>>i)&1:
                old=v
                v=[(1+1j)*(old[r&~(1<<i)]+(-1 if r>>i&1 else 1)*old[r|(1<<i)])
                   for r in range(16)]
        out=[0j]*16
        for base in range(16):
            before,phase=mono_state(req['left'],base)
            out[base^req['x']]=v[before]*phase.conjugate()*1j**req['phase']*(-1)**((base&req['z']).bit_count())
        cols.append(out)
    return cols


def exact(req):
    cols=matrix(req)
    j=req['mask'].bit_count()
    total=sum((1j)**t*cols[c][r].conjugate() for r,c,t in req['terms'])
    return [PROFILE[j]*Fraction(int(z),1<<j) for z in (total.real,total.imag)]


def random_mono(rng):
    rows=[1,2,4,8]
    for _ in range(12):
        i,j=rng.sample(range(4),2)
        rows[i]^=rows[j]
    return dict(rows=rows,shift=rng.randrange(16),linear=[rng.randrange(4) for _ in range(4)],
                cross=rng.randrange(64))


def request(rng,m,b=None):
    return dict(left=random_mono(rng),right=random_mono(rng),mask=rng.randrange(16) if b is None else b,
                phase=rng.randrange(4),x=rng.randrange(16),z=rng.randrange(16),
                terms=[[rng.randrange(16),rng.randrange(16),rng.randrange(4)] for _ in range(m)],
                precision=48)


def check_batch(queries):
    m=len(queries[0]['terms'])
    n,I,mags,signs=producer(m,48)
    state=[0]*n.size
    for i,req in enumerate(queries):
        bits=bytearray(TRACKS*((n.size+7)//8))
        encode(I,req,bits)
        for j in range(n.size):
            if bits[loc(j)]:
                state[j] |= 1<<i
    full=(1<<len(queries))-1
    for g in n.gates:
        ctrl=full
        for w in g[:-1]:
            ctrl &= state[w]
        state[g[-1]] ^= ctrl
    for i,req in enumerate(queries):
        got=[(-1 if state[sgn]>>i&1 else 1)*sum(((state[w]>>i)&1)<<j for j,w in enumerate(mag))
             for sgn,mag in zip(signs,mags,strict=True)]
        want=[v*(ODD<<SHIFT) for v in exact(req)]
        if got!=want:
            raise ValueError((req,got,want))
    return len(queries)


def main():
    rng=Random(7821)
    cases=0
    for b in range(16):
        base=request(rng,1,b)
        # All coordinates of this matrix, with varying record and global phases.
        queries=[dict(base,terms=[[r,c,(r+c)%4]],phase=(r-c)%4) for r in range(16) for c in range(16)]
        cases+=check_batch(queries)
    for m in (2,3,6):
        cases+=check_batch([request(rng,m) for _ in range(128)])
    print('PASS',cases,'exact complex sums against independent dense integer matrices, all 16 Hadamard masks.')


if __name__=='__main__':
    main()
