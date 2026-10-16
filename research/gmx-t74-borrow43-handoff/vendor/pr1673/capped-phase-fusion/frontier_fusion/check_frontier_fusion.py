#!/usr/bin/env python3
"""Recombine the pinned T74 supplier with the reviewed phase-fusion proof.

This checks arithmetic and provenance, not the independent native replay.
The latter's completion is recorded separately; no all-size premise is waived.
"""
from fractions import Fraction as Q
from decimal import Decimal, localcontext
from pathlib import Path
from math import factorial
import hashlib, json

HERE=Path(__file__).resolve().parent
WORK=HERE.parent
SPEC=WORK/'target002_upstream/pr1661/research/gmx-t74-p566-ep400/new/SPEC.json'
CLAIM=WORK/'target002_upstream/pr1661/research/gmx-t74-p566-ep400/CLAIM.json'
spec=json.loads(SPEC.read_text())
certified_complex=Q(spec['expected']['complex_lower'])
bit=Q('0.001733427039589844234749')
# Keep short independently checkable decimals strictly inside both endpoints.
b=Q('0.00167971337478')
q=b-Q(1,10**10)
a=(q+b)/2
online=Q(spec['expected']['kappa'])
old=Q('0.001673360105405778')
assert b<certified_complex<bit
profile={int(r):int(n) for r,n in spec['expected']['global_profile'].items()}
m=spec['geometry']['dimension']; W=spec['expected']['live']
assert (m,W)==(73,66304)
assert profile=={1:1559766,2:337668,3:278058,4:84912,5:54612,8:5328,48:22748}

GRID=10**45
def down(x):return Q((x*GRID).__floor__(),GRID)
def up(x):return Q((x*GRID).__ceil__(),GRID)
def unit_log(y):
    z=(y-1)/(y+1); N=50
    lo=2*sum((z**(2*j+1)/(2*j+1) for j in range(N)),Q(0))
    return lo,lo+2*z**(2*N+1)/((2*N+1)*(1-z*z))
ln2=unit_log(Q(2))
def log(x):
    k=0
    while x>=2:x/=2;k+=1
    lo,hi=unit_log(x)
    return down(lo+k*ln2[0]),up(hi+k*ln2[1])
def exp(x):
    assert 0<=x<1
    N=12
    lo=sum((x**j/factorial(j) for j in range(N)),Q(0))
    hi=lo+x**N/factorial(N)/(1-x/(N+1))
    return down(lo),up(hi)
def moment(endpoint):
    lo=hi=Q(0)
    for r,n in profile.items():
        l,h=log(Q(m,r)); weight=Q(n*r,m*W)
        lo+=weight*exp(endpoint*l)[0]
        hi+=weight*exp(endpoint*h)[1]
    return down(lo),up(hi)

native=moment(b)
assert native[1]<1
assert moment(Q('0.001679713374785'))[0]>1

def ledger(kind, *, q_=q, zeta=Q(1,10**8), slack=Q(1,10**5),
           old_scan=False, full_gauge=False, full_key=False):
    r=Q(1,10**6); stop=Q(1,10**9)
    if kind=='strassen':
        c=Q(3,32)
        eps=(1+q_+q_*(c-slack-r-zeta))/(1+q_)**2
        xi=eps*(1+q_)-c+slack
    else:
        c=Q(5,16)
        xi=(Q(3,2)+q_-(1+q_)*(r+zeta)+slack)/(2+q_)
        eps=(1+q_*(1-xi-r-zeta))/(1+q_)
    beta=1-xi-r-zeta
    saving=eps*q_
    # Deliberate strict 1e-11 gap after decimal truncation.
    kappa=Q((saving*10**18).__floor__(),10**18)-Q(1,10**11)
    # kappa is derived, not silently asserted to equal an expected decimal.
    tau=1-a; sigma=1-b
    internal=tau+(1-stop)*max(sigma-tau,Q(0))
    leaf=sigma+stop*(1-sigma)
    lam=1-(q_+a)/2
    key=beta+1-eps
    margins={
        'main_transform':saving,
        'global_coordinate_router':a,
        'fused_gaussian':1-eps+q_*beta,
        'group_bit_router':1-eps+a*beta,
        'group_scans':1-eps+beta,
        'boundary_algebraic_matrix':c+xi-eps,
        'sparse_union_movement':1-eps-beta-Q(1,2)+xi,
        'polynomial_products':eps,
        'microbox_face_corrections':1-(eps+beta+3-8+2),
    }
    if kind=='strassen':margins['sparse_union_full_key']=margins['sparse_union_movement']-key
    if old_scan:margins['old_per_axis_scan']=1-eps
    if full_key and kind!='strassen':margins['unnecessary_full_key_sort']=margins['sparse_union_movement']-key
    checks={
        'actual_bit_above_effective':bit-a,
        'complex_above_effective':b-a,
        'q_positive':q_, 'complex_endpoint':b-q_,
        'q_below_effective':a-q_, 'stop_positive':stop,
        'stop_below_one':1-stop,
        'leaf_saving_above_effective':(1-stop)*b-a,
        'q_below_internal':1-internal-q_, 'q_below_leaf':1-leaf-q_,
        'lambda_above_tau':lam-tau, 'lambda_above_sigma':lam-sigma,
        'lambda_above_internal':lam-internal,
        'lambda_prime_above_lambda':1-q_-lam,
        'lambda_prime_above_leaf':1-q_-leaf,
        'epsilon_positive':eps,'epsilon_below_one':1-eps,
        'cap_above_band':xi-Q(1,2),'cap_below_cell':eps-xi,
        'group_positive':beta,'group_below_dimension':eps-beta,
        'support_router_span':1-beta,
        'group_gauge_power_slack':1-xi-r-beta,
        'actual_logarithmic_group_guard':1-xi-beta,
        'global_gamma_power_slack':1-eps-r,
        'actual_logarithmic_gamma_guard':1-eps,
        'alpha_logarithm_absorption':r,
        'group_key_fits_record':1-key,
        'membership_arithmetic_fits_record':1-beta-2*(1-eps),
        'microbox_halo_volume':8-3-beta,
        'positive_layout_slack':slack,
        'short_record_fallback':eps-a,
        'improvement_over_online_final':kappa-online,
        'improvement_over_previous_local_final':kappa-old,
        'complex_below_one_over_32':Q(1,32)-b,
    }
    if kind!='strassen':
        checks['sparse_union_fraction_decays']=xi-beta-Q(1,2)
        checks['matrix_exponent_above_supplied_bound']=Q(19,8)-Q(9,4)
        checks['matrix_exponent_below_five_halves']=Q(5,2)-Q(19,8)
    if full_gauge:checks['unrecentered_group_gauge']=1-eps-r-beta
    checks.update({n+'_above_kappa':v-kappa for n,v in margins.items()})
    assert margins['main_transform']==margins['fused_gaussian']
    if kind=='strassen':assert margins['boundary_algebraic_matrix']==saving+slack
    else:assert margins['sparse_union_movement']==saving+slack
    return {'kind':kind,'kappa':kappa,'epsilon':eps,'xi':xi,'beta':beta,
            'q':q_,'a':a,'r0':r,'zeta':zeta,'slack':slack,
            'margins':margins,'strict_checks':checks}

def encode(x):
    if isinstance(x,Q):
        with localcontext() as c:
            c.prec=60
            return {'rational':str(x),'decimal':str(Decimal(x.numerator)/Decimal(x.denominator))}
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

rows={};controls={}
for kind in ['strassen','matrix_9_4']:
    row=ledger(kind)
    assert all(v>0 for v in row['strict_checks'].values())
    assert min(row['margins'].values())==row['margins']['main_transform']
    rows[kind]=row
    variants=[('endpoint_equality',{'q_':b}),('zero_group_guard',{'zeta':Q(0)}),
              ('zero_layout_slack',{'slack':Q(0)}),('old_per_axis_scan',{'old_scan':True}),
              ('full_cell_gauge',{'full_gauge':True})]
    if kind!='strassen':variants.append(('full_key_sort',{'full_key':True}))
    controls[kind]={}
    for name,kwargs in variants:
        bad=ledger(kind,**kwargs)
        failed={n:v for n,v in bad['strict_checks'].items() if v<=0}
        assert failed,(kind,name)
        controls[kind][name]=failed
out={'status':'PASS_EXACT_T74_PHASE_FUSION_ARITHMETIC',
     'scope':'Conditional recomposition of pinned supplier and already-reviewed outer proofs. Full fresh native replay is a separately tracked requirement; inherited all-size assumptions remain.',
     'complex_lower_short':b,'complex_lower_pinned':certified_complex,
     'native_moment':native,'profile':profile,'m':m,'W':W,
     'online_final_kappa':online,'rows':rows,'rejecting_controls':controls,
     'source_sha256':{str(p.relative_to(WORK)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [SPEC,CLAIM]}}
(HERE/'FRONTIER-FUSION-ARITHMETIC.json').write_text(json.dumps(encode(out),indent=2)+'\n')
print(out['status'])
for name,row in rows.items():
    print(name,'FINAL KAPPA',encode(row['kappa'])['decimal'],
          'positive checks',len(row['strict_checks']),
          'gain over online',encode(row['kappa']-online)['decimal'])
