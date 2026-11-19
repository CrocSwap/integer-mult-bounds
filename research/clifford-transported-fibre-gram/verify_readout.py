"""Compare transported chart readouts to literal Bell contractions and tensor columns."""
from collections import defaultdict
from hashlib import sha256
import json
from fractions import Fraction
from functools import cache
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from readout import (BatchReadout, HERE, IDENTITY, Q, ZERO, base_reads, iter_reads,
                     label_sum, pack, target_axes, translated_reads)
from bell_reads import transvection
from compile_row import apply
from raw_row import split_address


def require(ok, message):
    if not ok:
        raise ValueError(message)


def plus(left, right):
    return left[0]+right[0], left[1]+right[1]


def conjugate(value):
    return value[0], -value[1]


def power(value, exponent):
    a = (1,0)
    for _ in range(exponent):
        a = Q.multiply(a,value)
    return a


def symplectic(axes):
    mat = IDENTITY
    for axis in axes:
        mat = tuple(transvection(axis,v) for v in mat)
    return mat


TARGETS = (IDENTITY, symplectic([1,18,2]), symplectic([33,64,19,129,79]), IDENTITY[4:]+IDENTITY[:4])


@cache
def lift(target):
    """Build lift columns by left action of (1+i)(I+iP)/2 on literal basis states."""
    matrix = [[(int(r==c),0) for c in range(16)] for r in range(16)]
    axes = target_axes(target)
    for axis in axes:
        x,z = divmod(axis,16)
        exponent = ((x&z).bit_count()%2)+1
        v = []
        for r in range(16):
            phase = exponent + 2*((z&(r^x)).bit_count()%2)
            v.append([Q.multiply((1,1), plus(matrix[r][c],Q.multiply_i(matrix[r^x][c],phase)))
                      for c in range(16)])
        matrix = v
    return matrix,len(axes)


def translated_lift(target, p):
    mat, den = lift(target)
    x,z = divmod(p,16)
    return [[Q.multiply_i(a,2*((z&(r^x)).bit_count()%2)) for a in mat[r^x]] for r in range(16)],den


def literal_trace(target, p, other, b):
    a,d = translated_lift(target,p)
    v,e = translated_lift(other,b)
    total = ZERO
    for row, col in zip(a,v,strict=True):
        for x,y in zip(row,col,strict=True):
            total = plus(total,Q.multiply(conjugate(x),y))
    return tuple(Fraction(n,1<<(d+e)) for n in total)


def literal_dense(chart,target):
    _,offset,columns,terms,a,b,den = chart
    buckets = defaultdict(list)
    for read in iter_reads(target):
        out,inp = label_sum(read.output_labels),label_sum(read.input_labels)
        all_labels=read.output_labels+read.input_labels
        buckets[tuple(v>>4 for v in all_labels)].append(
            (pack([v&15 for v in all_labels]),out,inp,read.numerator,read.correction_i))
    singleton = [[ZERO for _ in range(16)] for _ in range(16)]
    for i in range(1<<len(columns)):
        raw = offset ^ apply(columns,i)
        r,c=map(split_address,divmod(raw,1<<52))
        nibbles = r[:-1]+c[:-1]
        key = tuple(u^v for u,v in zip(nibbles[::2],nibbles[1::2],strict=True))
        free=pack(nibbles[1::2])
        y=Q.multiply_i((a,b),Q.value(dict(terms),i))
        for w,l,t,n,phase in buckets.get(key,()):
            signs=(free&w).bit_count()+(l&r[-1]).bit_count()+(t&c[-1]).bit_count()
            rr=r[-1]^(l>>4)
            cc=c[-1]^(t>>4)
            atom=Q.multiply_i((n*y[0],n*y[1]), phase+2*signs)
            singleton[rr][cc]=plus(singleton[rr][cc],atom)
    result=[]
    for p in range(256):
        matrix,e=translated_lift(target,p)
        val=ZERO
        for row,block in zip(matrix,singleton):
            for u,v in zip(row,block):
                val=plus(val,Q.multiply(conjugate(u),v))
        result.append(tuple(Fraction(n,4096<<(den+e)) for n in val))
    return result


def one_column(target,p,phase):
    """Recover the eight-bit Choi chart by querying all literal matrix entries, then tensor."""
    mat,d=translated_lift(target,p)
    vals={16*r+c:v for r,row in enumerate(mat) for c,v in enumerate(row) if v!=ZERO}
    o=min(vals); basis=[]; span={0}
    for v in vals:
        w=v^o
        if w not in span:
            basis.append(w)
            span.update([s^w for s in span])
    require(len(vals)==len(span),"Choi support")
    unit=vals[o]; phases={}
    for i in range(1<<len(basis)):
        y=vals[o^apply(basis,i)]
        phases[i]=next(e for e in range(4) if Q.multiply_i(unit,e)==y)
    phase_terms={}
    for i in range(len(basis)):
        phase_terms[1<<i]=phases[1<<i]
        for j in range(i):
            idx=(1<<i)|(1<<j)
            val=(phases[idx]-phases[1<<i]-phases[1<<j])%4
            require(val in (0,2),"Choi quadratic phase")
            phase_terms[idx]=val
    require(all(Q.value(phase_terms,i)==v for i,v in phases.items()),"Choi amplitudes")
    def place(v,j):
        return ((v>>4)<<(52+4*j)) | ((v&15)<<(4*j))
    offset=sum(place(o,j) for j in range(13))
    dirs=tuple(place(v,j) for j in range(13) for v in basis)
    polys=tuple((t<<(len(basis)*j),v) for j in range(13) for t,v in phase_terms.items() if v)
    coef=Q.multiply_i(power(unit,13),phase)
    return (104,offset,dirs,polys,*coef,26+13*d)


def off_image():
    charts=[]
    rng=Random(7800)
    for target in TARGETS:
        read=next(r for r in iter_reads(target) if r.numerator)
        row=0;col=0
        for j in range(6):
            v,w=rng.randrange(16),rng.randrange(16)
            row=(row<<8)|(((read.output_labels[j]>>4)^v)<<4)|v
            col=(col<<8)|(((read.input_labels[j]>>4)^w)<<4)|w
        o=((row<<4|3)<<52)|(col<<4|5)
        charts.append((104,o,(1,2,1<<53,1<<17,1<<52),((1,1),(3,2),(20,2)),3,-5,3))
    affected=0
    for chart in charts:
        batch=BatchReadout(chart)
        for target in TARGETS:
            v,_=batch.evaluate(target)
            require(v==literal_dense(chart,target),"Off-image literal Bell/Pauli trace")
            affected+=any(z!=ZERO for z in v)
    require(affected>=3,"Control failed to exercise nonzero off-image contractions")
    return affected


def main():
    for pin in json.loads((HERE / "SOURCE-PINS.json").read_text()):
        require(sha256((HERE / pin["local"]).read_bytes()).hexdigest() == pin["sha256"],
                "Retained source digest: " + pin["local"])
    for t in TARGETS:
        require(list(translated_reads(t))==list(iter_reads(t)),"Transport cocycle differs from original list")
    for n,t in enumerate(TARGETS):
        p=(49*n+23)%256
        batch=BatchReadout(one_column(t,p,n))
        for target in (t,TARGETS[(n+1)%len(TARGETS)]):
            out,_=batch.evaluate(target)
            expected=[ZERO]*256
            if t==target:
                expected[p]=Q.multiply_i((1,0),n)
            require(out==expected,"Complex Pauli coefficient on a literal dense-lift tensor")
    print("PASS",len(TARGETS)*len(base_reads()),"literal transported read records;",
          "8 phase-sensitive tensor readouts; 16 off-image/all-Pauli comparisons with", off_image(),"nonzero.")


if __name__=="__main__":
    main()
