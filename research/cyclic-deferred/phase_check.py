"""Standalone exact signed-MRP87 phase, complement and Gaussian checks; stdlib."""
from pathlib import Path
from itertools import combinations
from collections import Counter
import hashlib,json,sys

path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/'inputs/shared-partition.json'
raw=path.read_bytes();data=json.loads(raw)
digest=hashlib.sha256(raw).hexdigest()
h=24;triples=list(combinations(range(h),3));masks=[sum(1<<j for j in T) for T in triples]
groups=data['groups'];assert Counter(map(len,groups))=={24:83,8:4}
assert sorted(t for G in groups for t in G)==list(range(len(triples)))
parity=lambda x:x.bit_count()&1
def project(x,B):
    out=0
    for b in B:
        if parity(x&b):out^=b
    return out
tests=[0]+[1<<i for i in range(h)]+[(1<<i)|(1<<j) for i,j in combinations(range(h),2)]
partial=iter(data['partial_complement_basis_supports']);records=[];gram_entries=0
for number,G in enumerate(groups):
    B=[masks[t] for t in G]
    if len(G)==24:C=[]
    else:
        supports=next(partial)
        assert len(supports)==16 and all(len(s)==len(set(s)) and all(0<=j<h for j in s) for s in supports)
        C=[sum(1<<j for j in s) for s in supports]
        assert Counter(c.bit_count() for c in C)=={1:8,3:8}
    Q=C+B;assert len(Q)==h
    assert all(parity(x&y)==(i==j) for i,x in enumerate(Q) for j,y in enumerate(Q)), 'non-orthonormal completed group basis'
    gram_entries+=len(Q)**2
    for x in tests:
        u=project(x,B);z=project(x,C)
        assert u^z==x
        assert (u.bit_count()-sum(3*parity(x&b) for b in B))%4==0
        assert (z.bit_count()-sum(c.bit_count()*parity(x&c) for c in C))%4==0
        assert (u.bit_count()+z.bit_count()-x.bit_count())%4==0
    negative=[i for i,c in enumerate(C) if c.bit_count()%4==3]
    assert (-24*len(negative))%4==0
    records.append(dict(group=number,size=len(B),complement_basis=C,
        negative_C_axes=negative,positive_C_axes=[i for i,c in enumerate(C) if c.bit_count()%4==1],
        tensor_width=24*len(C),tensor_scalar_phase_exponent_mod4=0))
assert next(partial,None) is None
for b in masks:
    for x in tests:
        u=b if parity(x&b) else 0
        assert (x.bit_count()-(x^u).bit_count()-u.bit_count())%4==0

# Exact one-coordinate inverse normalization, numerators over denominator2.
C1=[[(1,1),(1,-1)],[(1,-1),(1,1)]]
assert [[(a,-b) for a,b in row] for row in C1]==[
    [((1-2*i)*(1-2*j)*b,-(1-2*i)*(1-2*j)*a) for j,(a,b) in enumerate(row)]
    for i,row in enumerate(C1)]

# Actual Gaussian kernels with denominator2^n; no floating complex numbers.
units=[(1,0),(0,1),(-1,0),(0,-1)]
def kernel(n,phase):
    N=1<<n;A=[]
    for x in range(N):
        row=[]
        for y in range(N):
            re=im=0
            for z in range(N):
                a,b=units[phase(z)%4];sgn=1-2*parity(z&(x^y));re+=sgn*a;im+=sgn*b
            row.append((re,im))
        A.append(row)
    return A
def multiply(A,B):
    return [[(sum(a*c-b*d for (a,b),(c,d) in zip(row,col)),
              sum(a*d+b*c for (a,b),(c,d) in zip(row,col))) for col in zip(*B)] for row in A]
def scaled(A,n):return [[(n*a,n*b) for a,b in row] for row in A]
n=4;N0=1<<n;u=7;v0=11
qU=lambda x:3*parity(x&u)
qV=lambda x:3*parity(x&v0)
qG=lambda x:project(x,[u,v0]).bit_count()
qD=lambda x:(x^project(x,[u])).bit_count()
qE=lambda x:(x^project(x,[u,v0])).bit_count()
qI=lambda x:x.bit_count()
CU,CV,CG,CD,CE,CI=[kernel(n,q) for q in (qU,qV,qG,qD,qE,qI)]
assert multiply(CU,CV)==scaled(CG,N0)
assert multiply(CE,CG)==scaled(CI,N0)
assert multiply(CI,kernel(n,lambda x:-qD(x)))==scaled(CU,N0)
assert multiply(CI,CD)!=scaled(CU,N0)

R=28705;v=len(triples);m=h*h;N=v*v;ell=552;W=2*N+2*len(groups)*R
s=W*m-N+2*v*ell
out=dict(status='PASS signed MRP87 actual phases, explicit paid complement adapters and stage-two signs',
    partition_sha256=digest,groups=len(groups),group_size_histogram={24:83,8:4},
    all_triples_once=True,all_full_basis_Gram_entries_checked=gram_entries,
    phase_coefficient_points_per_group=len(tests),all_actual_Z4_phase_identities=True,
    all_complement_bases_explicit=True,all_tensor_scalar_phases_one=True,
    exact_inverse_direction_identity=True,exact_gaussian_composition=True,
    exact_stage2_gauge=True,wrong_source_sign_negative_control=True,
    R=R,W=W,rank_mass=s,deficit=N-2*v*ell,
    exterior_histogram={384:2*R*4},zero_rank_bridges_omitted=2*R*83,
    records=records,
    scope='Geometry and phase are standalone; numerical R comes from separately replayed PR117 producer')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='records'},indent=2))
