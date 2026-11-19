"""Literal tensor entries, parameter sums and sharp support-rank witnesses."""
from random import Random
from pathlib import Path
import json
from hashlib import sha256
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from adjoint import (HERE, IDENTITY, Observation, Q, conjugate, decompose, eliminate,
                     evaluate_forms, power)
from bell_reads import transvection


def target(axes):
    out = IDENTITY
    for axis in axes:
        out = tuple(transvection(axis,j) for j in out)
    return out


def add(v,w):
    return v[0]+w[0],v[1]+w[1]


def entry(chart,p):
    pair,e = Q.amplitude(chart,p)
    return pair[0],pair[1],1 << e


def same(x,y):
    return x[0]*y[2]==y[0]*x[2] and x[1]*y[2]==y[1]*x[2]


def literal(t):
    # Right multiplication in reversed word order, on columns. The consumer acts on rows.
    rows = [[(int(r==c),0) for c in range(16)] for r in range(16)]
    axes = decompose(t)
    for a in reversed(axes):
        x,z = divmod(a,16)
        new = []
        for row in rows:
            new.append([Q.multiply((1,1),add(v,Q.multiply_i(row[c ^ x],
                  1 + ((x & z).bit_count() & 1) + 2*(z & c).bit_count()))) for c,v in enumerate(row)])
        rows = new
    return rows,len(axes)+2


def literal_contractions(chart,t):
    _,offset,columns,phase,a,b,e = chart
    vals,d = literal(t)
    sums = [(0,0)]*256
    for u in range(1 << len(columns)):
        address = offset
        for j in Q.bits(u):
            address ^= columns[j]
        r,c = divmod(address,1<<52)
        sample = Q.multiply_i((a,b),Q.value(dict(phase),u))
        for x in range(16):
            prod = sample
            parity_input = 0
            for j in range(13):
                before = ((r >> (4*j)) & 15) ^ x
                parity_input ^= before
                prod = Q.multiply(prod,conjugate(vals[before][(c >> (4*j)) & 15]))
                if prod == (0,0):
                    break
            if prod!=(0,0):
                for z in range(16):
                    p=16*x+z
                    sums[p]=add(sums[p],Q.multiply_i(prod,2*(z & parity_input).bit_count()))
    return [(*v,1 << (e+13*d)) for v in sums]


def parametric_checks(rng):
    checked = 0
    for n in range(9):
        for fixed in range(n+1):
            for _ in range(5):
                q = {0:rng.randrange(4)}
                for i in range(n):
                    Q.term(q,1 << i,rng.randrange(4))
                    for j in range(i):
                        Q.term(q,(1<<i)|(1<<j),2*rng.randrange(2))
                compact = eliminate(n,fixed,dict(q))
                pred = [(0,0)] * (1 << fixed)
                if compact is not None:
                    rank,forms,r,base = compact
                    for v in range(1<<rank):
                        pred[evaluate_forms(forms,v)] = Q.multiply_i(base,Q.value(r,v))
                ref = [(0,0)] * len(pred)
                for v in range(1<<n):
                    i = v & ((1<<fixed)-1)
                    ref[i] = add(ref[i],Q.multiply_i((1,0),Q.value(q,v)))
                Q.need(pred==ref,"Literal parameterized Gauss sum")
                checked += len(ref)
    return checked


def encoded(d):
    # E_I f, from a direct Fourier sum over the four z bits at fixed x.
    dz,dx=min(d,4),max(0,d-4)
    columns=[(1<<j)|(1<<(52+j)) for j in range(52)]
    horizontal=[sum(1<<(52+4*t+j) for t in range(13)) for j in range(dx)]
    q={}
    for j in range(dx):
        Q.term(q,1<<(52+j),1)
    for j in range(dz):
        mask = sum(1<<(4*t+j) for t in range(13))
        if j==0 and dx:
            mask ^= 1<<52
        Q.affine(q,mask << 1,-1)
    return 104,0,columns+horizontal,list(q.items()),*power((1,1),dz),26


def check():
    rng = Random(620791)
    tested=parametric_checks(rng)
    full = target([17,34,68,136])  # all four local Fourier-type basis changes
    maps = [IDENTITY, target([16,1,32]), target([49,82,9,164,55]), full]
    one = (1 << 52) | 1
    pair = (1 << 16) | (1 << 73)
    charts = [Q.signature(104,[]), Q.signature(104,[('C',one,1),('C',pair,-1),('phase',-1)]),
              (104,(1<<104)-1,[rng.getrandbits(104) for _ in range(5)],[(1,1),(6,2),(8,3)],3,-2,4)]
    for chart in charts:
        for m in maps:
            out=Observation(chart).fibre(m)
            ref=literal_contractions(chart,m)
            Q.need(all(same(entry(out,p),ref[p]) for p in range(256)),"Literal 13-site adjoint with full phases")
    for d in range(9):
        out=Observation(encoded(d)).fibre(IDENTITY)
        Q.need(len(out[2])==d,"Encoded rank")
        dx,dz=max(0,d-4),min(d,4)
        for p in range(256):
            x,z=divmod(p,16)
            ok=x < (1<<dx) and z < (1<<dz)
            exponent=x.bit_count()+z.bit_count()+2*(x & z & 1)
            want=Q.multiply_i((int(ok),0),exponent)
            Q.need(same(entry(out,p),(*want,1)),"Encoded diagonal Pauli-label chart")
    # Swap two distinct local basis labels. The original vector is nonzero but cancels in A*.
    a,b = 1,1<<4
    anti=(104,a,[a^b],[(1,2)],1,1,1)
    for m in maps:
        Q.need(Observation(anti).fibre(m)[4:6]==(0,0),"Antisymmetric rejection")
    print(f"PASS {tested} literal parameter sums; 3,072 literal tensor adjoint values; "
          "2,304 encoded amplitudes across all nine support ranks; antisymmetric zero.")


if __name__ == '__main__':
    for record in json.loads((HERE/'SOURCE-PINS.json').read_text()):
        Q.need(sha256((HERE/record['local']).read_bytes()).hexdigest()==record['sha256'],"Frozen file digest")
    check()
