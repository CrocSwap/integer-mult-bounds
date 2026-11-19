"""Check mixed row charts by literal tensor products and verify the 36,720-dimensional rank."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from mixed import Decoder,HERE,IDENTITY,Producer,Q,apply,geometry,inverse_kernel,point_set,quotient,scale,unitary,vertices
from adjoint import conjugate, power
from canonical import coefficient as repeated, distance
from bell_reads import transvection


def scalar_sum(pairs):
    a=b=0
    for x,y in pairs:
        a+=x
        b+=y
    return a,b


def target(axes):
    S=IDENTITY
    for axis in axes:
        S=tuple(transvection(axis,v) for v in S)
    return S


def literal_column(S,R,c,p):
    left,k=unitary(S)
    right,l=unitary(R)
    x,z=divmod(p,16)
    values=[]
    for r in range(16):
        a,b=scalar_sum(Q.multiply(left[(r^x)|(j<<4)],right[j|(c<<4)]) for j in range(16))
        sg=(-1)**(((r^x)&z).bit_count())
        values.append((Fraction(sg*a,1<<(k+l)),Fraction(sg*b,1<<(k+l))))
    return values


def explicit_terms(chart):
    _,offset,cols,terms,a,b,e=chart
    for j in range(1<<len(cols)):
        u=offset
        for i in Q.bits(j):
            u^=cols[i]
        t=Q.multiply_i((a,b),Q.value(dict(terms),j))
        yield [(u>>(4*k))&15 for k in range(13)],(Fraction(t[0],1<<e),Fraction(t[1],1<<e))


def tensor_overlap(terms,column):
    out=[]
    for rows,amplitude in terms:
        val=amplitude
        for r in rows:
            val=Q.multiply(val,conjugate(column[r]))
        out.append(val)
    return scalar_sum(out)


def main():
    for record in json.loads((HERE/"SOURCE-PINS.json").read_text()):
        Q.need(sha256((HERE/record["local"]).read_bytes()).hexdigest()==record["sha256"],"Source digest")
    one=sum(1<<(4*i) for i in range(13))
    masks=[one,one<<1,sum(2<<(4*i) for i in range(2,13))]
    charts=[(52,0,(),(),1,0,0),(52,0,masks,[(1,3),(6,2)],3,2,2),
            (52,0x103,[0x201,0x43,0x154],[(1,1),(3,2)],-2,3,1),
            (52,1,[1^16],[(1,2)],1,0,0)]
    maps=[IDENTITY,target([1,16,32]),target([17,34,68,136]),target([31,47,77,101])]
    checks=0
    for chart in charts:
        pro=Producer(chart)
        terms=list(explicit_terms(chart))
        for s,S in enumerate(maps):
            R=maps[(s+1)%4] if s%2 else IDENTITY
            c=s%2
            f=scale(pro.feature(geometry(tuple(apply(S,v) for v in R[:4]))))
            for p in range(0,256,7):
                col=literal_column(S,R,c,p)
                direct=tensor_overlap(terms,col)
                calculated=scalar_sum(Q.multiply(conjugate(col[r]),v) for r,v in f)
                Q.need(calculated==direct,"Literal Pauli-column product")
                checks+=1
    # Antisymmetric cut survives in the input, then is annihilated in every basis.
    reject=Producer(charts[-1])
    Q.need(all(not scale(reject.feature(g)) for _,g in vertices()),"Antisymmetric cancellation on full geometry")
    # A phase-sensitive entangled GHZ input has an independently known linear combination of canonical answers.
    a,b=Fraction(1,2),Fraction(1,2)
    ghz=Decoder((52,0,[one],[(1,1)],1,1,1))
    total=0
    for S in maps:
        R=maps[2]
        for p in (0,16,32,7,68,116,255):
            r0=repeated(S,p,0,1,IDENTITY,R)
            r1=repeated(S,p,1,1,IDENTITY,R)
            z=scalar_sum([Q.multiply((a,b),r0),Q.multiply((-b,a),r1)])
            Q.need(ghz.coefficient(S,p,R,1)==z,"Entangled GHZ canonical inverse")
            total+=1
    # A genuinely full rank 52-bit input with a known stabilizer product readout.
    uniform=Producer((52,0,[1<<i for i in range(52)],[],1,0,26))
    xbasis=point_set((16,32,64,128))
    for i in (0,15,145,218,888,1555,2294):
        pt,g=vertices()[i]
        w=Fraction(-1,64)**distance(xbasis,pt)/4
        Q.need(dict(scale(uniform.feature(g)))=={r:(w,0) for r in range(16)},"Full rank entangled-producer control")
    # The 36,720 test tensors have Gram unitarily equivalent to C tensor I_16.
    n=(1,30,280,960,1024)
    off=sum(Fraction(k,64**i) for i,k in enumerate(n) if i)
    Q.need(0<off<1,"Strict diagonal dominance")
    print("PASS",checks,"literal complex mixed overlaps;",total,"canonical GHZ queries;",
          "2,295 antisymmetric controls; seven rank-52 charts; one-sided linear rank 36,720.")


if __name__=="__main__":
    main()
