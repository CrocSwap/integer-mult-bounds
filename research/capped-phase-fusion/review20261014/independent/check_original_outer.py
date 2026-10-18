#!/usr/bin/env python3
"""Independent controls for PR1673's ORIGINAL capped/Strassen outer.

No imports from the published verifier; no published files are written.
Exact finite controls complement ORIGINAL-OUTER-PROOF-REVIEW.md. They do not
prove the all-size assertions or regenerate the native T74 admission.
"""
from fractions import Fraction as F
from decimal import Decimal, localcontext
from itertools import product
from pathlib import Path
from math import prod, factorial
import hashlib
import json
import argparse

HERE = Path(__file__).resolve().parent
PKG = HERE.parent.parent
BASE = HERE/'source'

def enc(x):
    if isinstance(x, F):
        with localcontext() as c:
            c.prec = 65
            return {'exact': str(x), 'decimal': str(Decimal(x.numerator)/Decimal(x.denominator))}
    if isinstance(x, dict): return {str(k): enc(v) for k,v in x.items()}
    if isinstance(x, (list, tuple)): return [enc(v) for v in x]
    return x

def ledger(b, claimed, *, old_scan=False, full_cell=False, zero_guard=False,
           zero_boundary=False, equality=False, stop=F(1,10**9)):
    q = b if equality else b-F(1,10**10)
    a = (b+q)/2
    r, z, s, c = F(1,10**6), F(1,10**8), F(1,10**5), F(3,32)
    if zero_guard: z=F(0)
    if zero_boundary: s=F(0)
    # Solve main=Gaussian and boundary=main+s, not a numerical search.
    eps = (1+q+q*(c-s-r-z))/(1+q)**2
    xi = eps*(1+q)-c+s
    beta = 1-xi-r-z
    exponents = {
        'main_transform': 1-eps*q,
        'global_coordinate_routing': 1-a,
        'fused_gaussian_groups': eps-q*beta,
        'grouped_bit_routing': eps-a*beta,
        'group_scans_and_embeddings': eps-beta,
        'batched_boundary_algebra': eps-xi+F(29,32),
        'sparse_union_movement': eps+beta+F(1,2)-xi,
        'optional_full_key_union_sort': 2*beta+F(3,2)-xi,
        'packed_polynomial_products': 1-eps,
        'core_face_corrections': eps+beta-3,
    }
    if old_scan: exponents['forbidden_old_axis_scans']=eps
    slacks = {
        'bit_input': F('0.001733427039589844234749')-a,
        'strict_complex_call': b-q,
        'strict_movement_call': a-q,
        'positive_q': q,
        'stopping_leaf_above_effective_bit': (1-stop)*b-a,
        'stopping_leaf_above_q': (1-stop)*b-q,
        'positive_stop': stop,
        'stop_below_one': 1-stop,
        'epsilon_positive': eps,
        'epsilon_below_one': 1-eps,
        'cap_above_band': xi-F(1,2),
        'cap_below_original_cell': eps-xi,
        'positive_group': beta,
        'group_below_axis_count': eps-beta,
        'total_selected_support_below_full_address': 1-beta,
        'group_guard_spare': 1-beta-xi-r,
        'actual_group_log_guard_spare': 1-beta-xi,
        'global_coefficient_guard_spare': 1-eps-r,
        'actual_global_log_guard_spare': 1-eps,
        'logarithm_absorption': r,
        'membership_work_fits_record': 1-beta-2*(1-eps),
        'union_key_fits_record': 1-(beta+1-eps),
        'halo_fraction_decays': 8-3-beta,
        'positive_boundary_slack': s,
    }
    if full_cell: slacks['forbidden_full_cell_tensor_guard']=1-beta-eps-r
    slacks.update({name+'_above_claim': 1-power-claimed for name,power in exponents.items()})
    assert exponents['main_transform']==exponents['fused_gaussian_groups']
    assert 1-exponents['batched_boundary_algebra']==eps*q+s
    derived = F((eps*q*10**18).__floor__(),10**18)-F(1,10**11)
    return dict(b=b,q=q,a=a,epsilon=eps,xi=xi,beta=beta,
                derived_kappa=derived,claimed_kappa=claimed,
                exponents=exponents,slacks=slacks,
                minimum_saving=min(1-v for v in exponents.values()))

def log_unit(x, N=100):
    assert 1<=x<=2
    z=(x-1)/(x+1)
    lo=2*sum((z**(2*j+1)/F(2*j+1) for j in range(N)),F(0))
    return lo, lo+2*z**(2*N+1)/(F(2*N+1)*(1-z*z))

def log_interval(x):
    k=0
    while x>=2: x/=2; k+=1
    l,h=log_unit(x); l2,h2=log_unit(F(2))
    return l+k*l2,h+k*h2

def exp_interval(x,N=24):
    assert 0<=x<1
    lo=sum((x**j/F(factorial(j)) for j in range(N)),F(0))
    return lo,lo+x**N/F(factorial(N))/(1-x/F(N+1))

def moment_interval(b, profile):
    lo=hi=F(0)
    for r,n in profile.items():
        l,h=log_interval(F(73,r))
        elo=exp_interval(b*l)[0]; ehi=exp_interval(b*h)[1]
        weight=F(n*r,73*66304)
        lo+=weight*elo; hi+=weight*ehi
    # Outward rounding is exact; keep the portable receipt compact.
    grid=10**70
    return F((lo*grid).__floor__(),grid),F((hi*grid).__ceil__(),grid)

def eye(n): return [[F(i==j) for j in range(n)] for i in range(n)]
def mm(a,b): return [[sum((a[i][k]*b[k][j] for k in range(len(b))),F(0)) for j in range(len(b[0]))] for i in range(len(a))]
def sub(a,b): return [[x-y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def inv(a):
    n=len(a); x=[list(row)+ident for row,ident in zip(a,eye(n))]
    for k in range(n):
        p=next(i for i in range(k,n) if x[i][k])
        x[k],x[p]=x[p],x[k]
        c=x[k][k]; x[k]=[z/c for z in x[k]]
        for i in range(n):
            if i!=k:
                c=x[i][k]; x[i]=[z-c*t for z,t in zip(x[i],x[k])]
    return [row[n:] for row in x]
def block(a,b,c,d): return [x+y for x,y in zip(a,b)]+[x+y for x,y in zip(c,d)]
def zeros(n,m):return [[F(0) for _ in range(m)] for _ in range(n)]
def diagblock(a,d):return block(a,zeros(len(a),len(d)),zeros(len(d),len(a)),d)
def chain(*args):
    out=eye(len(args[0]))
    for a in args: out=mm(out,a)
    return out

def five_factor_controls():
    entries=0
    for seed in range(1,25):
        q=[[F((17+seed+i) if i==j else ((i+2*j+seed)%5-2),8) for j in range(4)] for i in range(4)]
        a=[row[:2] for row in q[:2]]; b=[row[2:] for row in q[:2]]
        c=[row[:2] for row in q[2:]]; d=[row[2:] for row in q[2:]]
        ai=inv(a); schur=sub(d,chain(c,ai,b)); si=inv(schur)
        e_b=block(eye(2),b,zeros(2,2),eye(2)); e_c=block(eye(2),zeros(2,2),c,eye(2))
        minus_b=block(eye(2),[[-v for v in r] for r in b],zeros(2,2),eye(2))
        minus_c=block(eye(2),zeros(2,2),[[-v for v in r] for r in c],eye(2))
        forward=chain(diagblock(a,eye(2)),e_c,diagblock(ai,schur),e_b,diagblock(a,eye(2)))
        backward=chain(diagblock(ai,eye(2)),minus_b,diagblock(a,si),minus_c,diagblock(ai,eye(2)))
        assert forward==q and backward==inv(q)
        # Dropping the middle dense stage is an actual rejected schedule.
        assert chain(diagblock(ai,eye(2)),minus_b,diagblock(eye(2),si),minus_c,diagblock(ai,eye(2)))!=inv(q)
        entries+=32
    return {'systems':24,'exact_matrix_entries':entries,'missing_middle_dense_rejected':True}

def q_image_controls():
    cases=addresses=0
    for power in range(2,10):
        t=2**power
        for s in range(t//2+1,t):
            image=[(2*t*j+s)//(2*s) for j in range(s)]
            assert len(set(image))==s and image==sorted(image)
            found=[]
            for k in range(t):
                # ceil(s(2k-1)/(2t)), clipped only at zero.
                j=max(0,-(-s*(2*k-1)//(2*t)))
                if j<s and 2*t*j<s*(2*k+1): found.append((k,j))
            assert found==list(zip(image,range(s)))
            cases+=1; addresses+=t
    s=[7,13,25]; t=[8,16,32]
    sources=list(product(*(range(x) for x in s)))
    images=[tuple((2*tt*j+ss)//(2*ss) for j,ss,tt in zip(x,s,t)) for x in sources]
    assert images==sorted(images) and len(set(images))==prod(s)
    return dict(one_axis_cases=cases,target_addresses=addresses,three_axis_source_records=prod(s),three_axis_target_records=prod(t))

def sparse_union_controls():
    L,g=4,3; E=[{0,1},{1,2},{2,3}]
    pts=list(product(range(L),repeat=g)); union={x for x in pts if any(x[i] in E[i] for i in range(g))}
    checks=0
    for i in range(g):
        rectangle={x for x in pts if x[i] in E[i]}
        assert len(rectangle)==len(E[i])*L**(g-1) and rectangle<=union
        for x in rectangle:
            for y in E[i]:
                out=x[:i]+(y,)+x[i+1:]
                assert out in union; checks+=1
    # Concrete dense interior stage changes coordinate 1 to 2.
    # Other axis coordinates 2 are deep, so this is a leak from U.
    E0={0,1}; before=(1,2); after=(2,2)
    assert any(t in E0 for t in before) and not any(t in E0 for t in after)
    return dict(L=L,g=g,union_records=len(union),closure_edges=checks,
                complete_rectangles=3,dense_stage_single_union_rejected=True)

def halo_controls():
    cases=0
    for N in (8,16,32):
        for A in (1,2):
            if 4*A>=N: continue
            for g in range(1,6):
                # Exact input-rectangle sum and telescoped identity, in tile units.
                rectangles=6*A*sum(N**j*(N+2*A)**(g-1-j) for j in range(g))
                assert rectangles==3*((N+2*A)**g-N**g)
                if g<=3:
                    seen=set()
                    for j in range(g):
                        for side in (0,1):
                            intervals=[range(A,N-A) if i<j else
                                       (range(0,A) if side==0 else range(N-A,N)) if i==j else
                                       range(N) for i in range(g)]
                            face=set(product(*intervals)); assert not (seen&face); seen|=face
                    actual={x for x in product(range(N),repeat=g) if any(t<A or t>=N-A for t in x)}
                    assert seen==actual and len(seen)==N**g-(N-2*A)**g
                cases+=1
    return dict(input_volume_identities=cases,first_face_partition_exact=True)

def depth_and_reservation_controls():
    def d(e):
        out=0
        while e>=73: e=48*(e//73); out+=1
        return out
    # Each two maximal-child steps at most halve width: 48^2*2<73^2.
    assert 2*48**2<73**2
    depth=[]
    for L in (10,100,1000,10000):
        actual=d(2**L); assert actual<=2*L
        depth.append([L,actual])
    # Deliberately do not infer a row-chunk constant from the one-level
    # physical invoice. Mixed and nested depths must be included. Illustrate
    # the all-size argument with an arbitrary fixed conservative stock
    # coefficient C: log2(stock)<=C ceil(log2(hG))^2. For h<=p the divided
    # row reservation is O(log p); a polynomial-log tail is sufficient.
    C=10**4
    rows=[]
    for lp in (64,128,512,4096,10**6):
        G=4*lp+6; K=128*G
        h=32*C*(lp+16)**2
        assert h<=2**lp
        lhg=(h*G).bit_length()
        row_chunks=(C*lhg**2+K-1)//K
        reserve=(2*h+127)//128+(h+127)//128+row_chunks
        assert F(reserve)<=F(h,16)
        rows.append(dict(log2p=lp,h=h,row_chunks=row_chunks,reserved=reserve))
    return dict(maxchild=48,dimension=73,two_step_halving=True,
                exact_depth_samples=depth,
                conservative_stock_family='log2(stock)<=C ceil(log2(hG))^2, C fixed',
                illustrative_fixed_C=C,polylog_tail_samples=rows,
                no_39_chunk_or_1050_threshold_assertion=True)

def source_manifest():
    relative=[
      'research/capped-phase-fusion/phase_fusion_note.tex',
      'research/capped-phase-fusion/SHALLOW-TOEPLITZ.md',
      'research/capped-phase-fusion/TENSOR-COMPILER.md',
      'research/capped-phase-fusion/SUPPLIER-SUPPORT-AUDIT.md',
      'research/capped-phase-fusion/SUPPORT-ADVERSARIAL-AUDIT.md',
      'research/capped-phase-fusion/SUPPORT-ROUTER.md',
      'research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md',
      'research/capped-phase-fusion/BILATERAL-LDU.md',
      'research/capped-phase-fusion/FORWARD-SMALL-A-AUDIT.md',
      'research/capped-phase-fusion/CAPPED-INTERIORS.md',
      'research/capped-phase-fusion/CAPPED-GAUGE-AUDIT.md',
      'research/capped-phase-fusion/PHASE-LAYOUT-AUDIT.md',
      'research/capped-phase-fusion/HALO-THEOREM.md',
      'research/capped-phase-fusion/OUTER-AUDIT.md',
      'research/capped-phase-fusion/PUBLICATION-SOURCES.json',
      'research/capped-phase-fusion/frontier_fusion/INDEPENDENT-SUBSTITUTION-REVIEW.md',
      'research/capped-phase-fusion/evidence/radical_reduction_ultra/README.md',
      'notes/endpoint-gauge-complex.tex',
      'notes/batched-complex-rows.tex',
      'notes/compact-control-layout.tex',
      'notes/compact-control-movement.tex',
      'references/semantic-bulk/rad20/reports/review-bulk-resampling.md',
      'references/semantic-bulk/rad20/reports/review-phase-cell-inverse.md',
    ]
    def resolve(p):
        prefix='research/capped-phase-fusion/'
        if p.startswith(prefix): return PKG/p[len(prefix):]
        return BASE/p
    pins=json.loads((HERE/'SOURCE-PINS.json').read_text())
    for rec in pins['files']:
        assert hashlib.sha256(resolve(rec['path']).read_bytes()).hexdigest()==rec['sha256'],rec['path']
    return {p:hashlib.sha256(resolve(p).read_bytes()).hexdigest() for p in relative}

def main():
    global PKG,BASE
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',type=Path,default=HERE.parent.parent,
                    help='capped-phase-fusion directory (installed default: ../../)')
    ap.add_argument('--repository-root',type=Path,
                    help='optional repository root for the six pinned sources; defaults to bundled source/')
    args=ap.parse_args()
    PKG=args.package.resolve()
    BASE=(args.repository_root or HERE/'source').resolve()
    if not (PKG/'phase_fusion_note.tex').is_file():
        ap.error('--package must contain phase_fusion_note.tex')
    specs={
      'original_selected_supplier':(F('0.001675462676808103522925'),F('0.001672922349588871')),
      'published_T74':(F('0.00167971337478'),F('0.001677160151714381')),
    }
    rows={}; controls={}
    for name,(b,k) in specs.items():
        row=ledger(b,k)
        assert all(x>0 for x in row['slacks'].values())
        assert row['derived_kappa']==k
        assert row['minimum_saving']==row['epsilon']*row['q']
        rows[name]=row
        controls[name]={}
        for label,args in [('old_axis_scan',dict(old_scan=True)),('full_cell_guard',dict(full_cell=True)),
                           ('zero_group_guard',dict(zero_guard=True)),('zero_boundary_slack',dict(zero_boundary=True)),
                           ('complex_endpoint_equality',dict(equality=True)),('excessive_leaf_stop',dict(stop=F(1,10**6)))]:
            bad=ledger(b,k,**args)
            failed={n:v for n,v in bad['slacks'].items() if v<=0}
            assert failed,label
            controls[name][label]=failed
    profile={1:1559766,2:337668,3:278058,4:84912,5:54612,8:5328,48:22748}
    lo,hi=moment_interval(specs['published_T74'][0],profile)
    assert hi<1
    overshoot=moment_interval(F('0.001679713374785'),profile)
    assert overshoot[0]>1
    assert 7**16<2**45
    out=dict(status='PASS_INDEPENDENT_ORIGINAL_OUTER_CONTROLS',
      scope='Original capped/Strassen PR1673 only. Conditional written proof separately reviewed. No native admission or all-size theorem is proved by these finite controls.',
      published_head='2569871ff906d2a2abfc86e97126ab9afe2e4a5a',
      head_scope='Historical reviewed head; source hashes below bind the actual current package used in this replay.',
      ledger=rows,negative_controls=controls,
      mixed_moment=dict(profile=profile,m=73,W=66304,interval=[lo,hi],strict_gap=1-hi,overshoot_lower=overshoot[0]),
      matrix_identity=five_factor_controls(),q_embedding=q_image_controls(),
      sparse_union=sparse_union_controls(),halos=halo_controls(),
      row_reservation=depth_and_reservation_controls(),source_sha256=source_manifest(),
      review_source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
          for p in [HERE/'check_original_outer.py',HERE/'ORIGINAL-OUTER-PROOF-REVIEW.md',HERE/'SOURCE-PINS.json']})
    (HERE/'ORIGINAL-OUTER-CONTROLS.json').write_text(json.dumps(enc(out),indent=2)+'\n')
    for name,row in rows.items():
        print(name,enc(row['derived_kappa'])['decimal'],len(row['slacks']),'strict checks')
    print(out['status'])

if __name__=='__main__': main()
