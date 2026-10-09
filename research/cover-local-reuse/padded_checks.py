#!/usr/bin/env python3
"""Exact padded66D cover, sequential triple sharing and paid data endings."""
import argparse,json,sys
from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
HERE=Path(__file__).resolve().parent
def basis(rows):
    p={}
    for x in rows:
        for j in sorted(p,reverse=True):
            if x>>j&1:x^=p[j]
        if x:
            j=x.bit_length()-1
            for k in p:
                if p[k]>>j&1:p[k]^=x
            p[j]=x
    return tuple(p[j]for j in sorted(p,reverse=True))
def app(C,x):
    y=0
    while x:
        z=x&-x;x-=z;y^=C[z.bit_length()-1]
    return y
def mul(A,B):return tuple(app(A,b)for b in B)
def inverse(C):
    n=len(C);rows=[sum(((C[j]>>i)&1)<<j for j in range(n))|(1<<(n+i))for i in range(n)]
    for i in range(n):
        j=next(j for j in range(i,n)if rows[j]>>i&1);rows[i],rows[j]=rows[j],rows[i]
        for j in range(n):
            if j!=i and rows[j]>>i&1:rows[j]^=rows[i]
    assert all(rows[i]&((1<<n)-1)==1<<i for i in range(n))
    return tuple(sum(((rows[i]>>(n+j))&1)<<i for i in range(n))for j in range(n))
def trans(C):return tuple(sum(((C[i]>>j)&1)<<i for i in range(len(C)))for j in range(len(C)))
def sympair(x,y,h):
    mask=(1<<h)-1
    return (((x&mask)&(y>>h)).bit_count()+((y&mask)&(x>>h)).bit_count())&1

def representative(U,h):
    """Construct K_G C_E K_G^-1, including degenerate U."""
    U=basis(U);cols=list(U)
    for i in range(h):
        if len(basis(tuple(cols)+(1<<i,)))>len(cols):cols.append(1<<i)
    assert len(cols)==h
    G=tuple(cols);GiT=trans(inverse(G))
    K=tuple(G[i]|((G[i]^GiT[i])<<h)for i in range(h))+tuple(c<<h for c in GiT)
    assert all(sympair(K[i],K[j],h)==int(abs(i-j)==h)for i in range(2*h)for j in range(2*h))
    CE=tuple(1<<i for i in range(h))+tuple((1<<(h+i))|((1<<i)if i<len(U)else 0)for i in range(h))
    return mul(mul(K,CE),inverse(K))
def fourier(h,active=None):
    active=set(range(h))if active is None else set(active)
    return tuple(1<<i for i in range(h))+tuple((1<<(h+i))|((1<<i)if i in active else 0)for i in range(h))
def embed(T,h,m,offset):
    def lift(x):return ((x&((1<<h)-1))<<offset)|((x>>h)<<(m+offset))
    C=[1<<i for i in range(2*m)]
    for i in range(h):C[offset+i]=lift(T[i]);C[m+offset+i]=lift(T[h+i])
    return tuple(C)
def rank(C,h):return len(basis(c&((1<<h)-1)for c in C[h:]))
def nd(U):return len(basis(sum(((x&y).bit_count()&1)<<j for j,y in enumerate(U))for x in U))==len(U)


def profile(local):
    h,v,R=(local[k]for k in ('h','v','R'));m=3*h;old_m=3*h-2
    assert (h,v)==(22,comb(22,3))
    inv=local['physical_auxiliary_source_frames'];assert sum(row['count']for row in inv)==R
    H=Counter({int(r):n for r,n in local['child_multiplicities'].items()})
    removed=Counter({(h-1)**2:2*v*v,1:v*v})
    for row in inv:removed[h*h-h+len(row['basis'])]+=2*v*row['count']
    H.subtract(removed);assert all(n>=0 and n%(2*v)==0 for n in H.values())
    H=Counter({r:n//(2*v)for r,n in H.items()if n})
    children=Counter({r:9*n for r,n in H.items()});exteriors=Counter()
    zero_tails=0
    for row in inv:
        d=len(row['basis']);c=row['count']
        if d:exteriors[3*d]+=3*c
        else:zero_tails+=3*c
    data=Counter({m-old_m:6*v});children.update(exteriors);children.update(data)
    w=6*v+3*R;s=sum(r*n for r,n in children.items())
    assert w*m-s==3*(2*v-3*h*(h-1))==5082
    assert all(0<r<m and n>0 for r,n in children.items())
    return dict(h=h,m=m,v=v,R=R,vertices_per_cell=3,stages=3,roles_per_cell=w,rank_per_cell=s,
      deficit_per_cell=w*m-s,maxchild=max(children),local_copies_per_cell=9,
      local_child_multiplicities=dict(sorted(H.items())),
      local_cell_child_multiplicities={r:9*n for r,n in sorted(H.items())},
      exterior_cell_child_multiplicities=dict(sorted(exteriors.items())),
      data_finish_cell_child_multiplicities=dict(data),zero_width_exteriors_omitted=zero_tails,
      child_multiplicities=dict(sorted(children.items())))

def image(C,U):return basis(app(C,x)for x in U)
def contains(U,V):return len(basis(U+V))==len(V)
def dot(x,y):return (x&y).bit_count()&1

def port_geometry(h,m):
    A=tuple(1<<i for i in range(h));B=tuple(1<<i for i in range(h,2*h-1))
    C=tuple(1<<i for i in range(2*h-1,3*h-2));D=tuple(1<<i for i in range(3*h-2,m))
    E0=basis(A+B+C);E=basis(E0+D);checks=0
    assert len(D)==2 and len(E0)==m-2
    for triple in combinations(range(h),3):
        q=sum(1<<i for i in triple);d=next(i for i in range(h)if i not in triple);w=q^(1<<d)
        Aq=tuple((1<<i)^(w if w>>i&1 else 0)for i in range(h)if i!=d)
        assert all(dot(x,y)==int(i==j)for i,x in enumerate(Aq)for j,y in enumerate(Aq))
        assert all(not dot(x,q)for x in Aq)
        def swap(other):
            cols=[(q if q>>j&1 else 0)^sum((other[i]if u>>j&1 else 0)for i,u in enumerate(Aq))for j in range(h)]
            for axis in (B,C):cols.extend(Aq if axis==other else axis)
            cols.extend(D);R=tuple(cols)
            assert mul(R,R)==tuple(1<<i for i in range(m))
            assert all(dot(x,y)==int(i==j)for i,x in enumerate(R)for j,y in enumerate(R))
            assert image(R,D)==basis(D)and app(R,q)==q
            return R
        R12,R23=swap(B),swap(C)
        assert image(R12,A)==basis(B+(q,))and image(R23,A)==basis(C+(q,))
        assert image(R23,B+C)==basis(B+Aq)
        stages=[((q,),basis(B+(q,)),(),basis(B)),
                (basis(B+(q,)),basis(A+B),basis(B),basis(Aq+B)),
                (basis(A+B),E0,basis(Aq+B),basis(Aq+B+C))]
        for xs,xe,ys,ye in stages:assert contains(xs,xe)and contains(ys,ye)
        xlast,ylast=stages[-1][1],stages[-1][3]
        yfinal=basis(ylast+D)
        assert contains(xlast,E)and len(E)-len(xlast)==2
        assert contains(ylast,yfinal)and len(yfinal)-len(ylast)==2
        assert len(yfinal)==m-1 and all(not dot(x,q)for x in yfinal)
        # X finish is E0 -> E, Y finish is (E0 intersect q-perp)
        # -> q-perp. Both are nested exact transitions of Fourier rank2.
        checks+=1
    return checks

def check(local):
    p=profile(local);h,m=p['h'],p['m'];F=fourier(m);I=tuple(1<<i for i in range(2*m))
    tau=tuple(1<<((i+h)%m)for i in range(m))
    assert mul(mul(tau,tau),tau)==tuple(1<<i for i in range(m))
    assert tau!=tuple(1<<i for i in range(m)) and mul(tau,tau)!=tuple(1<<i for i in range(m))
    assert all(dot(x,y)==int(i==j)for i,x in enumerate(tau)for j,y in enumerate(tau))
    blocks=[tuple(range(j*h,(j+1)*h))for j in range(3)]
    assert len(set().union(*map(set,blocks)))==m
    FF=[fourier(m,b)for b in blocks]
    O={}
    for stage in (1,2,3):
        axes=range(0)if stage==1 else range(h,2*h-1)if stage==2 else range(h,3*h-2)
        O[stage]=[fourier(m,((i+j*h)%m for i in axes))for j in range(3)]
    count=Counter();types=0;degenerate=0;controls=set()
    for row in local['physical_auxiliary_source_frames']:
        U=tuple(row['basis']);d=len(U);assert U==basis(U)
        T=representative(U,h);Ts=[embed(T,h,m,j*h)for j in range(3)]
        for stage in (1,2,3):
            residuals=[]
            for j,(Tj,Fj,Oj)in enumerate(zip(Ts,FF,O[stage])):
                assert mul(Oj,Tj)==mul(Tj,Oj)and mul(Oj,Fj)==mul(Fj,Oj)
                Pj=mul(Fj,inverse(Tj))
                if stage==2:
                    entry=Oj;last=mul(mul(Oj,Tj),inverse(Fj));expected=inverse(Pj)
                else:entry=mul(Oj,Tj);last=mul(Oj,Fj);expected=Pj
                residual=mul(last,inverse(entry));assert residual==expected
                residuals.append(residual)
            product=mul(residuals[2],mul(residuals[1],residuals[0]));tail=mul(F,inverse(product))
            assert mul(tail,product)==F and rank(tail,m)==3*d
            if d==0:
                assert rank(tail,m)==0
                assert mul(tail,mul(residuals[1],residuals[0]))!=F
                controls.add('omitted-third-residual-rejected')
            if d:
                assert product!=F
                controls.add('omitted-nonzero-gauge-tail-rejected')
            count[stage]+=1
        types+=1;degenerate+=not nd(U)
    ports=port_geometry(h,m)
    unpaid=p['rank_per_cell']-sum(r*n for r,n in p['data_finish_cell_child_multiplicities'].items())
    assert p['roles_per_cell']*m-unpaid!=p['deficit_per_cell']
    controls.add('omitted-data-finishes-rejected')
    return dict(status='PASS exact66D padded ports and sequential triple-bank geometry',profile=p,
      source_frame_types_checked=types,degenerate_source_frame_types=degenerate,
      stage_source_frame_checks=dict(sorted(count.items())),actual_ports_checked=ports,
      order_three_orthogonal_permutation=True,right_cosets_have_three_vertices=True,
      stages_shared=[1,2,3],completed_offsets_cancel=True,reversed_residual_is_forward_inverse=True,
      all_three_active_spaces_disjoint=True,all_stage_tail_ranks_three_times_source_dimension=True,
      zero_rank_exteriors_are_rank_zero_adapters=True,all_local_histograms_retained_nine_times=True,
      both_data_bank_finishes_paid=True,data_finish_rank_per_bank=2,data_finish_ports_per_cell=6*p['v'],
      data_before_finish_dimension=3*h-2,ambient_dimension=3*h,negative_controls=sorted(controls),
      exact_tail_definition='E_stage = F_total (R3 R2 R1)^-1; forward Rj=F_active,j T_sigma,j^-1; reverse Rj=R_forward,j^-1',
      exact_data_finish='Choose completed64D endpoints (F_E0, F_E0 T_q^-1); apply F_total F_E0^-1 on each data bank. Its rank is2 on both endpoint frames and the original Pauli input correction and bank exchange still give two copies of F_total.',
      scope='Checks every actual h22 port and every physical source frame, including degenerate gauges. Exact phases cancel by the displayed inverse definitions. Retains inherited scalar transparency, general Clifford adapters, common generic basis, finite routing and all-size/tape/analytic hypotheses.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=HERE.parents[1]);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    root=args.root.resolve();local=root/'research/cyclic-deferred';src=local/'complex-profile.json'
    data=json.loads(src.read_text());audit=json.loads((local/'reflection-audit.json').read_text())
    assert audit['child_multiplicities']==data['child_multiplicities']
    assert audit['physical_auxiliary_source_frames']==data['physical_auxiliary_source_frames']
    for k in ('exact_arbitrary_dirty_cancellation_by_dependency_cut','physical_aliased_numeric_replay','literal_frame_incidences_both_directions','completed_core_pre_exterior_frames_full'):
        assert audit[k]is True,k
    out=check(data)
    files=[src,local/'reflection-audit.json',root/'notes/general-clifford-frames.tex',root/'notes/three-stage-cover-complex.tex']
    out['source_sha256']={str(f.relative_to(root)):sha256(f.read_bytes()).hexdigest()for f in files}
    out['checker_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    path=HERE/'padded-geometry.json';text=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if args.write:path.write_text(text)
    else:assert path.read_text()==text,'Padded geometry receipt mismatch'
    print(out['status'],out['source_frame_types_checked'],'sourceframes',out['actual_ports_checked'],'ports',flush=True)
if __name__=='__main__':main()
