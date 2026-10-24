#!/usr/bin/env python3
"""Check the finite root, quadratic and rank-seven inputs for private rank 64."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys
import time

if not __debug__:
    raise SystemExit('Run with assertions enabled.')
root,out=map(lambda s:Path(s).resolve(),sys.argv[1:3])
source=root/'baseline535/source531/research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'
data=json.loads(source.read_text());R,P=data['root_lines'],data['binary_ports'];assert len(R)==len(P)==120
lane=root.parent/'p518-next/complex/paired-five'
chamber_path=lane/'E8-ALL-GATHER.json';chamber=json.loads(chamber_path.read_text())
started=time.monotonic()
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
def basis(rows):
    pivots={}
    for x in rows:
        while x:
            k=x.bit_length()-1
            if k in pivots:x^=pivots[k]
            else:pivots[k]=x;break
    return list(pivots.values())
def inverse(rows):
    n=len(rows);a=[list(map(Q,row))+[Q(i==j)for j in range(n)]for i,row in enumerate(rows)]
    for j in range(n):
        k=next(i for i in range(j,n)if a[i][j]);a[k],a[j]=a[j],a[k]
        v=a[j][j];a[j]=[x/v for x in a[j]]
        for i in range(n):
            if i!=j:
                v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[j])]
    return [row[n:]for row in a]
assert len(set(P))==120 and all(p.bit_count()%2 for p in P)
assert all(dot(r,r)==4 for r in R)
assert all(dot(R[i],R[j])==0 for i in range(8)for j in range(i))
assert all((P[i]&P[j]).bit_count()%2==(1+dot(R[i],R[j])//2)%2 for i in range(120)for j in range(120))

# Derive chamber coefficients from the simple matrix, rather than use saved
# coefficient lists. The finite reflection argument is in the written audit.
simple=chamber['simple_roots'];inv=inverse(simple)
coefficients=[[sum(Q(row[k])*inv[k][j]for k in range(8))for j in range(8)]for row in R]
assert all(all(x.denominator==1 for x in row)and(all(x>=0 for x in row)or all(x<=0 for x in row))for row in coefficients)
signed={tuple(s*x for x in r)for r in R for s in(-1,1)}
assert len(signed)==240 and len(basis(P[8:]))==9
assert all(tuple(a)in signed and dot(a,a)==4 for a in simple)
assert all(sum(r[i]*r[j]for r in R[8:])==56*int(i==j)for i in range(8)for j in range(8))
attaining=[len(basis([p for p,r in zip(P[8:],R[8:])if r[j]]))for j in range(8)]
assert attaining==[8]*8
for a in simple:
    for r in signed:
        g=dot(a,r);assert g%2==0 and tuple(x-g//2*y for x,y in zip(r,a))in signed
weights=[[inv[i][j]for i in range(8)]for j in range(8)]
counts=[sum(dot(r,w)!=0 for r in R)for w in weights]
assert sorted(counts)[0]==57 and sorted(counts)[1]>=78
short=weights[counts.index(57)]
assert tuple(2*x for x in short)in signed
zeros=[0]*9
for mask in range(256):
    z=sum(all(not row[j]or mask>>j&1 for j in range(8))for row in coefficients)
    zeros[mask.bit_count()]=max(zeros[mask.bit_count()],z)
assert zeros==[0,1,3,6,12,20,36,63,120]
generalized=[53]+[112-zeros[8-d]for d in range(2,9)]
assert generalized==[53,76,92,100,106,109,111,112]
root_supports=[sum(1<<i for i,r in enumerate(R[8:])if dot(a,r))for a in R]
assert Counter(s.bit_count()for s in root_supports)=={56:8,53:112}

# Recover the exact quadratic function on the affine odd-label space.
label=lambda x:x|((1^(x.bit_count()%2))<<8)
points=set(P);truth=[int(label(x)in points)for x in range(256)]
anf=list(truth)
for bit in range(8):
    for x in range(256):
        if x>>bit&1:anf[x]^=anf[x^(1<<bit)]
assert not anf[0]and all(x.bit_count()<=2 for x,v in enumerate(anf)if v)
q=lambda x:truth[x]
polar=lambda x,y:q(x)^q(y)^q(x^y)^q(0)
assert len(basis([sum(polar(1<<i,1<<j)<<j for j in range(8))for i in range(8)]))==8
assert sum(1-2*v for v in truth)==16
remaining=[1<<i for i in range(8)];pairs=[]
while remaining:
    a=remaining.pop();k=next(i for i,b in enumerate(remaining)if polar(a,b));b=remaining.pop(k)
    pairs.append((a,b));remaining=[x^(a if polar(x,b)else 0)^(b if polar(x,a)else 0)for x in remaining]
assert len(pairs)==4 and sum(q(a)*q(b)for a,b in pairs)%2==0
for mask in range(256):
    x=value=0
    for j,(a,b)in enumerate(pairs):
        u,v=(mask>>(2*j))&1,(mask>>(2*j+1))&1
        if u:x^=a
        if v:x^=b
        value^=u*v^u*q(a)^v*q(b)
    assert q(x)==value
# The sign hypothesis is needed. Its opposite permits a constant-one
# affine four-space and cannot support the rank-five capacity of twelve.
origin=0
for a,b in pairs:
    if q(a):origin^=b
constant_coset=[]
for mask in range(16):
    x=origin
    for j,(a,b)in enumerate(pairs):
        if mask>>j&1:x^=a
    constant_coset.append(x)
assert len(set(constant_coset))==16 and all(q(x)==0 for x in constant_coset)
assert sum(q(x)^1 for x in constant_coset)==16>12
root_hyperplane_checks=[]
for p in P:
    H=[x for x in range(256)if not(p&label(x)).bit_count()%2];a=H[0]
    directions=basis([x^a for x in H]);assert len(H)==128 and len(directions)==7
    polar_rows=[sum(polar(u,v)<<j for j,v in enumerate(directions))for u in directions]
    assert len(basis(polar_rows))==6
    radical=[x for x in range(256)if all(not polar(x,v)for v in directions)and all((p&label(a^x)).bit_count()%2==0 for _ in(0,))]
    assert len(radical)==2
    rad=next(x for x in radical if x)
    assert all(q(x^rad)==q(x)for x in H)
    assert sum(1-2*q(x)for x in H)==16 and sum(q(x)for x in H)==56
    root_hyperplane_checks.append(p)

# Use projective two-plane sets, not an RREF frame enumeration.
planes={frozenset((a,b,a^b))for a in range(1,512)for b in range(a+1,512)}
assert len(planes)==43435
zero=[sum(1<<i for i,p in enumerate(P[8:])if not(p&x).bit_count()%2)for x in range(512)]
frames=[]
for plane in planes:
    a,b=sorted(plane)[:2];frames.append(zero[a]&zero[b])
hist=Counter(x.bit_count()for x in frames)
assert max(hist)==36 and all(k%2==0 for k in hist)
maximum_root_intersection=max((s&t).bit_count()for s in frames for t in root_supports)
assert maximum_root_intersection==32
self_max=max((s&root_supports[j]).bit_count()for s in frames for j in range(8,120)if s>>(j-8)&1)
assert self_max<=21
largest=[x for x in frames if x.bit_count()==36];large=[x for x in frames if x.bit_count()>=34]
assert len(largest)==448 and len(large)==4032
large_union=max((s|t).bit_count()for s in largest for t in large)
assert large_union==66
assert max(large_union,34+34,36+32)==68
assert max(z.bit_count()for z in zero[1:])==64

# Check all full-root planes and the binary regular-simplex label model.
nonorthogonal=orthogonal=0
for a,b in combinations(R,2):
    g=dot(a,b);assert g in(-2,0,2)
    solutions=[(A,B)for A,B in product((-2,0,2),repeat=2)if 4*(A*A+B*B)-2*g*A*B==4*(16-g*g)]
    if not g:assert not solutions;orthogonal+=1
    else:
        assert len(solutions)==2
        assert tuple(x-g//2*y for x,y in zip(a,b))in signed;nonorthogonal+=1
edges=list(combinations(range(9),2));edge_labels={e:511^(1<<e[0])^(1<<e[1])for e in edges}
for j in range(9):
    star=[p for e,p in edge_labels.items()if j in e]
    assert len(basis(star))==8 and all(not p>>j&1 for p in star)
    assert all(p>>j&1 for e,p in edge_labels.items()if j not in e)
    for a,b in edges:
        values=[2*int(i==a)-2*int(i==b)for i in range(9)]
        for endpoint in(a,b):
            shifted=[v-values[endpoint]for v in values]
            assert shifted[endpoint]==0 and all(v!=0 for i,v in enumerate(shifted)if i!=endpoint)
report=dict(status='PASS_INDEPENDENT_PRIVATE64_GEOMETRIC_INPUTS',generalized_support_bounds=generalized,
    zero_root_maxima=zeros,fundamental_support_counts=counts,quadratic_ones=sum(truth),quadratic_gauss_sum=16,
    symplectic_pairs=pairs,arf_invariant=0,analytic_source_capacities=[0,1,2,4,8,12,20,36,64,112],
    attaining_private_coordinate_frame_ranks=attaining,
    negative_control='Complementing the quadratic sign produces an affine four-space with sixteen ones; the positive-Gauss hypothesis is necessary.',
    root_nonself_hyperplanes_checked=len(root_hyperplane_checks),rank7_planes=len(planes),rank7_histogram=dict(hist),
    maximum_root_intersection_rank7=maximum_root_intersection,maximum_rank7_intersection_when_self_port_present=self_max,maximum_rank7_pair_union=68,
    large_pair_checks=len(largest)*len(large),nonorthogonal_root_planes=nonorthogonal,orthogonal_root_planes=orthogonal,
    analytic_rank5_rank6_bounds_require_written_coisotropic_argument=True,
    source_sha256={str(p):sha256(p.read_bytes()).hexdigest()for p in(source,chamber_path)},seconds=time.monotonic()-started,
    scope='Exact chamber, quadratic, complete rank7 and simplex-model prerequisites. Uniform affine rank5/rank6 capacities and both algebraic query closures are supplied by the independent written audit. No scalar-private theorem is inferred solely from this finite receipt.')
out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['seconds'])
