"""Exact 13-receiver nonlinear obstruction and explicit nine-bit relaxed index code."""
from fractions import Fraction
from hashlib import sha256
import gzip
import itertools
import json
from pathlib import Path
import sys

C=(0,14,15,30,31,60,69,70)
E={78:(0,14),77:(0,15),93:(0,30),61:(14,15),110:(14,30)}
GZIP_SHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
RAW_SHA='b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69'


def product(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def projector(spec):
    A=list(map(list,zip(*(spec['B']+spec['A']))));n=len(A);d=spec['dim'];assert n==8 and len(spec['B'])==d
    aug=[[Fraction(t) for t in r]+[Fraction(i==j) for j in range(n)] for i,r in enumerate(A)]
    for i in range(n):
        k=next(k for k in range(i,n) if aug[k][i]);aug[k],aug[i]=aug[i],aug[k];q=aug[i][i];aug[i]=[x/q for x in aug[i]]
        for j in range(n):
            if i!=j and aug[j][i]:q=aug[j][i];aug[j]=[u-q*v for u,v in zip(aug[j],aug[i])]
    inv=[row[n:] for row in aug];assert all(v.denominator%3 for row in inv for v in row)
    P=product([r[:d] for r in A],inv[:d]) if d else [[Fraction(0)]*n for _ in range(n)]
    assert product(P,P)==P
    return P,[row[0] for row in A],inv[0]


def xor_forms(g):
    # All helpers and y are zero, with all 111 x_i as independent input variables.
    n=g['public'];values={i:(1<<i) if i<111 else 0 for i in range(n)};out=[]
    for op,d,*args in g['program']:
        if op=='INIT':values[d]=0
        elif op=='ADD':values[d]^=values[args[0]]
        elif op=='SWAP':j=args[0];values[d],values[j]=values[j],values[d]
        elif op=='CLEAR':del values[d]
        elif op=='MOVE':
            if args[1]==0:out.append(values[d])
        else:raise ValueError(op)
    assert len(out)==9
    return out


def bounded_rectangles():
    # For one edge, each endpoint has at most two private binary nuisances.
    # Only its two possible sets of endpoint responses are relevant. Enumerate
    # every nonempty response subset, including genuine dependence on nuisance.
    subsets=(frozenset([0]),frozenset([1]),frozenset([0,1]));total=works=0
    for a0,a1,b0,b1 in itertools.product(subsets,repeat=4):
        z=set(itertools.product(a0,b0));o=set(itertools.product(a1,b1));recover=z.isdisjoint(o)
        assert recover==(a0.isdisjoint(a1) or b0.isdisjoint(b1));total+=1;works+=recover
    return {'rectangle_patterns':total,'separable_patterns':works}


def bitids(x):return [i for i in range(x.bit_length()) if x>>i&1]


def check(path):
    blob=Path(path).read_bytes();assert sha256(blob).hexdigest()==GZIP_SHA;raw=gzip.decompress(blob);assert sha256(raw).hexdigest()==RAW_SHA;g=json.loads(raw)
    P=111;n=g['public'];assert n==630 and g['final'][:P]==[1]*P and g['start'][P:2*P]==[0]*P
    axes=[]
    for i in range(P):
        head=g['frames'][str(g['start'][i])];body=g['frames'][str(g['final'][P+i])];assert (head['dim'],body['dim'])==(1,7)
        h,u,v=projector(head);b,_,_=projector(body)
        assert all(h[j][k]+b[j][k]==int(j==k) for j in range(8) for k in range(8))
        axes.append((u,v))
    # H_j<=B_i iff H_j H_i and H_i H_j are zero, using B_i=I-H_i.
    # For H_k=u_k v_k^t the two scalar contractions decide this exactly.
    ortho=[sum(1<<j for j,(uj,vj) in enumerate(axes) if not sum(x*y for x,y in zip(vi,uj)) and not sum(x*y for x,y in zip(vj,ui))) for ui,vi in axes]
    assert all(not(ortho[i]>>i&1) for i in range(P));assert all((ortho[i]>>j&1)==(ortho[j]>>i&1) for i in range(P) for j in range(P))
    assert len(C)==8 and len(E)==5;vertices=set(v for pair in E.values() for v in pair);assert len(vertices)==4
    assert all(not(ortho[i]>>j&1) for i in C for j in C)
    for edge,ends in E.items():
        assert {c for c in C if ortho[edge]>>c &1}==set(ends)
        for other,extra in E.items():
            if other!=edge and set(ends)&set(extra):assert not(ortho[edge]>>other&1)
    available={e:sorted(f for f in E if ortho[e]>>f&1) for e in E}
    sums=[0];words=xor_forms(g)
    for w in words:sums+= [w^u for u in sums]
    assert len(set(sums))==512
    dec=[]
    for i in range(P):
        m=next(k for k,v in enumerate(sums) if ((v^(1<<i))&~ortho[i])==0)
        u=sums[m]^(1<<i);assert u&~ortho[i]==0 and u^sums[m]==1<<i
        dec.append({'port':i,'broadcast_mask':m,'side_info_ports':bitids(u)})
    wrong=[w for w in words];wrong[0]=0;test=[0]
    for w in wrong:test+=[w^u for u in test]
    missed=[i for i in range(P) if all((v^(1<<i))&~ortho[i] for v in test)];assert missed
    return {'graph_compressed_sha256':GZIP_SHA,'graph_expanded_sha256':RAW_SHA,'main_ports':P,'public_inputs':n,'geometry_pairs_tested':P*P,'lower_bound':9,'upper_bound_nine_linear_broadcasts':len(words),'clique':C,'four_vertices':sorted(vertices),'five_outsiders_endpoints':E,'actual_side_info_between_outsiders':available,'rectangle_control':bounded_rectangles(),'eight_signal_control_failed_receivers':missed,'linear_broadcast_forms':[bitids(w) for w in words],'111_decoders':dec}

if __name__=='__main__':print(json.dumps(check(sys.argv[1]),sort_keys=True,indent=2))
