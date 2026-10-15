#!/usr/bin/env python3
"""Recombine THIS PACKAGE's T74 supplier (PR1661's pivot-566 stack plus the pivot-554 kernel) with the reviewed phase-fusion outer proof (PR1673).

Adapted from PR1673 research/capped-phase-fusion/frontier_fusion/check_frontier_fusion.py (Vlado Vojdanovski): the ledger formulas, constants
and all strict inequalities are unchanged except the matrix-boundary constant c=3/10 (tau=12/5, Le Gall's published omega<2.3728639, as specialised by PR1699, Chafik Boukhalfa); the free strict slacks (r0, zeta, layout slack, q=b-GAP, stop, the decimal floor, the backoff) and b = certified endpoint - 1e-64 are retuned, see RETUNED-SLACKS.md and the constants at the top.
Only the supplier inputs change: the complex saving b, the native profile/W/m and the supplier SPEC/CLAIM are this package's own.
This checks arithmetic and provenance; the supplier's native admission is the package's verify.py.
"""
from fractions import Fraction as Q
from decimal import Decimal, localcontext
from pathlib import Path
from math import factorial
import hashlib, json

HERE=Path(__file__).resolve().parent
WORK=HERE.parent
SPEC=WORK/'new/SPEC.json'
CLAIM=WORK/'CLAIM.json'
BJ=json.loads((HERE/'B.json').read_text())
spec=json.loads(SPEC.read_text())
# Free strict slacks of the PR1673 proof (retuned in this package, see RETUNED-SLACKS.md); every one only needs to be > 0.
R0=Q(1,10**64); ZETA=Q(1,10**66); SLACK=Q(1,10**64); GAP=Q(1,10**64); STOP=Q(1,10**70)
FLOOR=10**100; BACKOFF=Q(1,10**76); B_GAP=Q(1,10**64)
# Rectangular boundary batching (new in this package, outer/RECT-BOUNDARY.md): W^k right-hand-side columns per factor page, k=2. The boundary cost per RHS column is
# W^(omega(1,1,k)-k), so the effective square-equivalent exponent is tau_eff = omega(1,1,k) - k + 1. The published bound omega(1,1,2) = omega(1,2,1) < 3.250035
# is ADVWXXZ 2024 ('More Asymmetry Yields Faster Matrix Multiplication', Table 1, k = 2.00); the fixed format exponent sigma is chosen strictly above it.
K_BATCH=2
SIGMA_PUB=Q('3.250035')
SIGMA=Q('3.2500351')
TAU_EFF=SIGMA-(K_BATCH-1)
KAPPA_PKG4=Q('0.0016778199023144364336310551358776001013829401215770658599799349282716974076737897457922714197448847')  # previous package (radix union schedule, square boundary tau=2.372864)
KAPPA_1712=Q('0.0016776417313433545642517275958639984231708545722735432722117400060454625429077941422798526440584702')  # pkg of PR1712 (Le Gall tau=12/5, old union row)
KAPPA_1699=Q('0.001677641731343354564251058287063644749065568493')  # exact kappa of PR1699's ledger (Chafik Boukhalfa), same supplier profile
certified_complex=Q(spec['expected']['complex_lower'])
bit=Q('0.001733427039589844234749')
# Keep short independently checkable decimals strictly inside both endpoints.
b=certified_complex-B_GAP   # strictly inside the certified supplier endpoint; B.json carries the same exact value
assert b==Q(BJ['b'])
q=b-GAP
a=(q+b)/2
online=Q(spec['expected']['kappa'])
old=Q('0.001673360105405778')
assert b<certified_complex<bit
profile={int(r):int(n) for r,n in spec['expected']['global_profile'].items()}
m=spec['geometry']['dimension']; W=spec['expected']['live']
assert (m,W)==(73,66304)
EXPECTED_PROFILE={int(k):v for k,v in BJ['profile'].items()}
assert profile==EXPECTED_PROFILE

GRID=10**110
def down(x):return Q((x*GRID).__floor__(),GRID)
def up(x):return Q((x*GRID).__ceil__(),GRID)
def unit_log(y):
    z=(y-1)/(y+1); N=130
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
    N=45
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
b_up=Q(BJ['b_above_endpoint'])
assert b_up>certified_complex and moment(b_up)[0]>1   # a larger test endpoint is rejected

def ledger(kind, *, q_=q, zeta=ZETA, slack=SLACK,
           old_scan=False, full_gauge=False, full_key=False, old_union=False, sig=SIGMA):
    r=R0; stop=STOP
    # Boundary: Le Gall's published omega<2.3728639 at the fixed target tau=2.372864 (PR1699's specialisation, Chafik Boukhalfa); c=(3-tau)/2.
    # Union: radix-distributed schedule (outer/UNION-SCHEDULE.md, new in this package): row exponent eps+1/2-xi. The boundary row now binds with main = fused Gaussian.
    tau_eff=sig-(K_BATCH-1)
    c=(3-tau_eff)/2
    eps=(1+q_+q_*(c-slack-r-zeta))/(1+q_)**2
    xi=eps*(1+q_)-c+slack
    beta=1-xi-r-zeta
    saving=eps*q_
    # Deliberate strict gap (BACKOFF) after decimal truncation to the FLOOR grid.
    kappa=Q((saving*FLOOR).__floor__(),FLOOR)-BACKOFF
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
        'sparse_union_movement':xi+Q(1,2)-eps,
        'polynomial_products':eps,
        'microbox_face_corrections':1-(eps+beta+3-8+2),
    }
    if old_union:margins['old_g_factor_union_row']=1-eps-beta-Q(1,2)+xi
    if old_scan:margins['old_per_axis_scan']=1-eps
    if full_key:margins['unnecessary_full_key_sort']=margins['sparse_union_movement']-key
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
    checks['rect_exponent_above_published_bound']=sig-SIGMA_PUB          # fixed format <n,n,n^2;R>, R<n^sigma, needs sigma > published omega(1,1,2)
    checks['rect_leaf_domination']=sig-3                                  # additions O(W^3) per level are dominated by the leaves (geometric ratio n^3/R<1)
    checks['rect_effective_exponent_below_five_halves']=Q(5,2)-tau_eff
    checks['rect_effective_exponent_above_two']=tau_eff-2                   # output size W^(k+1) = trivial lower bound
    checks['union_tag_work_fits_record']=1-2*beta   # worst case: a record with |F|=g visits g rounds of O(g) tag work
    checks['union_header_fits_record']=1-beta
    checks['improvement_over_pr1699']=kappa-KAPPA_1699
    checks['improvement_over_pr1712']=kappa-KAPPA_1712
    checks['improvement_over_previous_package']=kappa-KAPPA_PKG4
    if full_gauge:checks['unrecentered_group_gauge']=1-eps-r-beta
    checks.update({n+'_above_kappa':v-kappa for n,v in margins.items()})
    assert margins['main_transform']==margins['fused_gaussian']
    assert margins['boundary_algebraic_matrix']==saving+slack
    assert margins['sparse_union_movement']>saving+slack
    return {'kind':kind,'kappa':kappa,'epsilon':eps,'xi':xi,'beta':beta,
            'q':q_,'a':a,'r0':r,'zeta':zeta,'slack':slack,
            'margins':margins,'strict_checks':checks}

def encode(x):
    if isinstance(x,Q):
        with localcontext() as c:
            c.prec=140
            return {'rational':str(x),'decimal':str(Decimal(x.numerator)/Decimal(x.denominator))}
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

rows={};controls={}
for kind in ['rect_batch_k2_radix_union']:
    row=ledger(kind)
    assert all(v>0 for v in row['strict_checks'].values())
    assert min(row['margins'].values())==row['margins']['main_transform']
    rows[kind]=row
    variants=[('endpoint_equality',{'q_':b}),('zero_group_guard',{'zeta':Q(0)}),
              ('zero_layout_slack',{'slack':Q(0)}),('old_per_axis_scan',{'old_scan':True}),
              ('full_cell_gauge',{'full_gauge':True})]
    variants+=[('full_key_sort',{'full_key':True}),('old_g_factor_union_row',{'old_union':True}),('sigma_below_published_bound',{'sig':Q('3.2500349')}),('sigma_equal_published_bound',{'sig':SIGMA_PUB})]
    controls[kind]={}
    for name,kwargs in variants:
        bad=ledger(kind,**kwargs)
        failed={n:v for n,v in bad['strict_checks'].items() if v<=0}
        assert failed,(kind,name)
        controls[kind][name]=failed
    assert 'rect_exponent_above_published_bound' in controls[kind]['sigma_below_published_bound'] and 'rect_exponent_above_published_bound' in controls[kind]['sigma_equal_published_bound']
    assert 'old_g_factor_union_row_above_kappa' in controls[kind]['old_g_factor_union_row'] and 'unnecessary_full_key_sort_above_kappa' in controls[kind]['full_key_sort']
out={'status':'PASS_EXACT_T74_PHASE_FUSION_ARITHMETIC',
     'scope':'Conditional recomposition of pinned supplier and already-reviewed outer proofs. Full fresh native replay is a separately tracked requirement; inherited all-size assumptions remain.',
     'complex_lower_short':b,'complex_lower_pinned':certified_complex,
     'native_moment':native,'profile':profile,'m':m,'W':W,
     'online_final_kappa':online,'rows':rows,'rejecting_controls':controls,
     'pr1673_kappa':Q('0.001677160151714381'),'improvement_over_pr1673':rows['rect_batch_k2_radix_union']['kappa']-Q('0.001677160151714381'),
     'source_sha256':{p.relative_to(WORK).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [SPEC,CLAIM]}}
(HERE/'LEDGER.json').write_text(json.dumps(encode(out),indent=2)+'\n')
print(out['status'])
for name,row in rows.items():
    print(name,'FINAL KAPPA',encode(row['kappa'])['decimal'],
          'positive checks',len(row['strict_checks']),
          'gain over online',encode(row['kappa']-online)['decimal'])
