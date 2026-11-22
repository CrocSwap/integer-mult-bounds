#!/usr/bin/env python3
"""Exact ledger for fine-prime padding (PR1786, chafreaky / Chafik Boukhalfa, with Tim Trudgian's prime theorem) at the free point epsilon = 1 - (1025/1024)*10^-(DIG+80), explicit Strassen boundary, retuned to the fixed-grid maximum kappa = C - 1/FLOOR - BACKOFF.

Adapted from PR1786's ledger, itself adapted from PR1731's cost ledger, credited to Jeremy Kothe et al. and
Vlado Vojdanovski (PR1673); uses PR1758's gauge-free chirp and per-visit tag
accounting. New source-prime, coefficient-setup and halo lemmas are in
FINE-PRIME-PADDING.md. Finite arithmetic does not prove the all-size theorem.
"""
from fractions import Fraction as Q
from decimal import Decimal, localcontext
from pathlib import Path
from math import factorial
import hashlib, json, sys
sys.set_int_max_str_digits(0)

if not __debug__: raise RuntimeError('Assertions must be enabled')
HERE=Path(__file__).resolve().parent
WORK=HERE.parent
SPEC=WORK/'new/SPEC.json'
CLAIM=WORK/'CLAIM.json'
BJ=json.loads((HERE/'B.json').read_text())
spec=json.loads(SPEC.read_text())
# Free strict slacks of the PR1673 proof (retuned in this package, see RETUNED-SLACKS.md); every one only needs to be > 0.
DIG=spec['outer_refinement']['endpoint_digits']   # the supplier endpoint is certified to 10^-DIG (accept at the endpoint, reject at endpoint + 10^-DIG); every slack sits 10 digits below
# Fixed-grid maximum (PR2180 / PR2161, dataisfire; proof PROOF-GRID-MAX.md): the free gaps shrink together to R0 = 10^-(DIG+80); grid, backoff and certified endpoint are unchanged.
R0=Q(1,10**(DIG+80)); ZETA=R0/100; SLACK=R0; GAP=R0; STOP=R0/10**6
FLOOR=10**(DIG+46); BACKOFF=Q(1,10**(DIG+22)); B_GAP=R0
# Fine prime padding: theta is between 1/(4p^2) and 1/(2p^2-1).
# Online chirp guard beta+2*xi-2<1; coefficient setup uses O(p^2 log p) bits.
# epsilon = 1 - DELTA_E is a FREE parameter (outer/FINE-PADDING-COMPOSITION.md sec. 2): every row is strictly satisfied for every DELTA_E > r0 = 10^-(DIG+80); beta = 1 - 3 DELTA_E lies in the admissible window
# [1 - DELTA_E (1 + 1/q), 1 - 2 DELTA_E). DELTA_E = (1025/1024) r0 keeps the gamma spare power 1-eps-r0 = r0/1024 > 0 and puts C - eps*q below 1/FLOOR (PROOF-GRID-MAX.md).
DELTA_E=Q(1025,1024)*R0
EPS=1-DELTA_E
BETA=1-3*DELTA_E
THETA_POWER=Q(2)
HALO_POWER=48
CORE_POWER=128
STRASSEN_TAU=Q(45,16)
KAPPA_1828=Q('0.0016797549561255445213356709939207025769983114385025802954603275201627999999999999999999999999979966404900867489109573286580121585')  # exact kappa of rohanarun's PR1828 (slack refinement of PR1800 at 1e-96), from its body
KAPPA_1839=Q('0.0016797549561255445213356709939207025769983114385025802954603275201628645482603256388263049999999997996640490086748910957328658012158594')  # exact kappa of PR1839 (previous package: 1e-90 endpoint)
KAPPA_1875=Q('0.0016797549561255445213356709939207025769983114385025802954603275201628645482603256388263056561328446322744513169085862209720704481201654121427713006366929567157349625273906229277148454180995537563371124755588139767841405530386745578819565618798006892541712197674874836946756930569827889227573192555649999999997996640490086748910957328658012158594')  # exact kappa of rohanarun's PR1875 (1e-300 endpoint), from its body
KAPPA_1876=Q('0.001679754956125544521335670993920702576998311438502580295460327520162864548260325638826305656132844632274451316908586220972070448120165412142771300636692956715734962527390622927714845418099553756337112475558813976784140553038674557881956561879800689254171219767487483694675693056982788922757319255565606685566411725238449650999339827075715283714270157705762309226038611771955655377501414652136546310799999999999999999997996640490086748910957328658012158594846')  # exact kappa of rohanarun's PR1876 (1e-400 endpoint), from its body
KAPPA_1897=Q('0.001679754956125544521335670993920702576998311438502580295460327520162864548260325638826305656132844632274451316908586220972070448120165412142771300636692956715734962527390622927714845418099553756337112475558813976784140553038674557881956561879800689254171219767487483694675693056982788922757319255565606685566411725238449650999339827075715283714270157705762309226038611771955655377501414652136546310881185746917580802513640545967852810801680966856133978576162943792322682482152988532923811998938861379689883167389728443314312230815059559906903773756886872476136837071871203030423643505345473735135533')  # exact kappa of M6LI's PR1897 (1e-500 grid), from its body
KAPPA_1786=Q('0.0016797547881500489087805478664999999999999999999999999999999998000000199999')  # exact kappa of chafreaky's PR1786 ledger (EXPECTED-BALANCE.json), headline 0.001679754788150048
KAPPA_PKG5=Q('0.001677992607205282520732088774830808372222877897034109604209719298829805473412451530867883424937597')  # previous package (rectangular k=2, tau_eff=2.2500351)
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

GB=int((DIG+130)*3.3220)+16   # enclosure grid 2^-GB, about 50 digits below the slacks
ONE=1<<GB
try:
    from gmpy2 import mpz   # optional accelerator, identical integer results
except ImportError:
    mpz=int
def _cd(a,b):return -((-a)//b)
def down(x):return Q((x*ONE).__floor__(),ONE)
def up(x):return Q(_cd(x.numerator*ONE,x.denominator),ONE)
LN=GB//3+12   # atanh terms: z<=1/3, so the tail is below 9^-LN < 2^-GB
EN=GB//6+12   # exponential terms: x<0.01, so x^EN/EN! < 2^-GB
def unit_log(y):
    # 2*atanh((y-1)/(y+1)) in directed-rounding integer fixed point: floor every term for the lower sum, ceil every term for the upper sum, geometric tail
    z=(y-1)/(y+1);p,q=mpz(z.numerator),mpz(z.denominator);p2,q2=p*p,q*q
    pl=ONE*p//q;ph=_cd(ONE*p,q);sl=sh=mpz(0)
    for j in range(LN):
        sl+=pl//(2*j+1);sh+=_cd(ph,2*j+1);pl=pl*p2//q2;ph=_cd(ph*p2,q2)
    tail=_cd(2*ph*q2,(2*LN+1)*(q2-p2))
    return Q(int(2*sl),ONE),Q(int(2*sh+tail),ONE)
ln2=unit_log(Q(2))
def log(x):
    k=0
    while x>=2:x/=2;k+=1
    lo,hi=unit_log(x)
    return down(lo+k*ln2[0]),up(hi+k*ln2[1])
def exp(x):
    assert 0<=x<Q(1,100)
    xl=mpz(x.numerator)*ONE//x.denominator;xu=_cd(mpz(x.numerator)*ONE,x.denominator)
    tl=th=sl=sh=mpz(ONE)
    for j in range(1,EN):
        tl=((tl*xl)>>GB)//j;th=_cd(-((-th*xu)>>GB),j);sl+=tl;sh+=th
    tn=_cd(-((-th*xu)>>GB),EN)    # x^EN/EN! (rounded up); the tail is at most twice this
    return Q(int(sl),ONE),Q(int(sh+2*tn+2),ONE)
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
           old_scan=False, full_gauge=False, full_key=False, old_union=False, old_theta=False, old_linear=False, old_tag=False,
           eps_=EPS, beta_=BETA, tau_eff=STRASSEN_TAU, halo_power=HALO_POWER, core_power=CORE_POWER):
    r=R0; stop=STOP
    # Existing explicit Strassen format, 7^16<2^45; c=3/32.
    # Union: radix-distributed schedule (outer/UNION-SCHEDULE.md, new in this package): row exponent eps+1/2-xi. The boundary row binds with main; the Gaussian row has slack at this explicit point.
    c=(3-tau_eff)/2
    eps=eps_; beta=beta_
    xi=eps*(1+q_)-c+slack
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
        'microbox_face_corrections':1-(eps+beta+halo_power-core_power+2),
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
        'group_gauge_power_slack':1-(2*xi-THETA_POWER)-r-beta,
        'actual_logarithmic_group_guard':1-(2*xi-THETA_POWER)-beta,
        'global_gamma_power_slack':1-eps-r,
        'actual_logarithmic_gamma_guard':1-eps,
        'alpha_logarithm_absorption':r,
        'group_key_fits_record':1-key,
        'membership_arithmetic_fits_record':1-beta-2*(1-eps),
        'microbox_halo_volume':core_power-halo_power-beta,
        'positive_layout_slack':slack,
        'short_record_fallback':eps-a,
        'improvement_over_online_final':kappa-online,
        'improvement_over_previous_local_final':kappa-old,
        'complex_below_one_over_32':Q(1,32)-b,
    }
    checks['strassen_integer_power_gap']=Q(2**tau_eff.numerator-7**tau_eff.denominator)
    checks['theta_positive_polynomial_power']=THETA_POWER
    checks['cap_below_phase_cell_power']=THETA_POWER-xi
    checks['halo_covers_generic_inverse_radius']=Q(halo_power-43)
    checks['union_tag_work_per_visit_fits_record']=1-beta
    checks['union_header_fits_record']=1-beta
    checks['source_axis_superpolynomial']=1-eps
    checks['improvement_over_pr1786']=kappa-KAPPA_1786
    checks['improvement_over_pr1828']=kappa-KAPPA_1828
    checks['improvement_over_pr1839']=kappa-KAPPA_1839
    checks['improvement_over_pr1875']=kappa-KAPPA_1875
    checks['improvement_over_pr1876']=kappa-KAPPA_1876
    checks['improvement_over_pr1897']=kappa-KAPPA_1897
    checks['improvement_over_pr1758']=kappa-Q('0.001679745508802299051546533685199973672313473419790800679752457380932784242972585600630181672224983')
    checks['improvement_over_pr1699']=kappa-KAPPA_1699
    checks['improvement_over_pr1712']=kappa-KAPPA_1712
    checks['improvement_over_previous_package']=kappa-KAPPA_PKG4
    checks['improvement_over_pkg_k2']=kappa-KAPPA_PKG5
    if full_gauge:checks['unrecentered_group_gauge']=1-THETA_POWER-r-beta
    if old_theta:checks['old_theta_chirp_guard']=1-(2*xi-eps)-r-beta
    if old_linear:checks['old_linear_guard']=1-xi-r-beta
    if old_tag:checks['old_union_tag_2beta']=1-2*beta
    # Main-binding family invariant (PR2180): the Gaussian saving stays above the main saving. The fixed kappa grid (FLOOR) is coarser than the free gaps,
    # so the *_above_kappa rows alone would no longer exclude a beta outside the main-binding window; this row is delta*(1-2q) > 0.
    checks['gaussian_above_main']=margins['fused_gaussian']-saving
    checks.update({n+'_above_kappa':v-kappa for n,v in margins.items()})
    assert margins['boundary_algebraic_matrix']==saving+slack
    assert margins['sparse_union_movement']==saving+slack+(tau_eff-2)/2
    return {'kind':kind,'kappa':kappa,'epsilon':eps,'xi':xi,'beta':beta,
            'q':q_,'a':a,'r0':r,'zeta':zeta,'slack':slack,
            'margins':margins,'strict_checks':checks}

def encode(x):
    if isinstance(x,Q):
        with localcontext() as c:
            c.prec=DIG+200
            return {'rational':str(x),'decimal':str(Decimal(x.numerator)/Decimal(x.denominator))}
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

rows={};controls={}
for kind in ['struct_boundary_radix_union']:
    row=ledger(kind)
    assert all(v>0 for v in row['strict_checks'].values())
    assert min(row['margins'].values())==row['margins']['main_transform']
    # fixed-grid maximum: C*FLOOR is an integer and 0 < C - eps*q < 1/FLOOR, so floor(FLOOR*eps*q)/FLOOR = C - 1/FLOOR exactly and kappa attains the grid/backoff ceiling
    assert (certified_complex*FLOOR).denominator==1 and 0<certified_complex-EPS*q<Q(1,FLOOR)
    assert row['kappa']==certified_complex-Q(1,FLOOR)-BACKOFF
    assert len(row['strict_checks'])==63
    rows[kind]=row
    variants=[('endpoint_equality',{'q_':b}),('zero_layout_slack',{'slack':Q(0)}),
              ('old_per_axis_scan',{'old_scan':True}),('full_cell_gauge',{'full_gauge':True}),
              ('full_key_sort',{'full_key':True}),('old_g_factor_union_row',{'old_union':True}),
              ('old_theta_chirp_guard',{'old_theta':True}),('old_linear_guard',{'old_linear':True}),
              ('old_union_tag_2beta',{'old_tag':True}),('matrix_below_strassen',{'tau_eff':Q(14,5)}),
              ('halo_too_short',{'halo_power':40}),('core_too_small',{'core_power':48}),
              ('group_equals_dimension',{'beta_':EPS}),('epsilon_equals_one',{'eps_':Q(1)}),('epsilon_not_above_r0_slack',{'eps_':1-R0}),('beta_below_gaussian_window',{'beta_':1-700*DELTA_E}),('beta_above_membership_window',{'beta_':1-2*DELTA_E})]
    controls[kind]={}
    for name,kwargs in variants:
        bad=ledger(kind,**kwargs)
        failed={n:v for n,v in bad['strict_checks'].items() if v<=0}
        assert failed,(kind,name)
        controls[kind][name]=failed
    assert 'old_g_factor_union_row_above_kappa' in controls[kind]['old_g_factor_union_row'] and 'unnecessary_full_key_sort_above_kappa' in controls[kind]['full_key_sort']
# PR1786 p^10 umbrella (vendor/pr1786/FINE-PRIME-PADDING.md, "a conservative common eventual bound p^10", and check_fine_padding.py norm_power = 10) tied to THETA_POWER:
# the inverse-norm bound ||K^-1|| = O(alpha^5 rho^2 theta^-2 exp(a rho/3)) has theta^-2 <= 16 p^(2*THETA_POWER) (theta >= 1/(4 p^THETA_POWER)), an exponential factor <= p^2 eventually,
# alpha^5 polylogarithmic; a further half power is allowed for the polylogarithmic and bounded-constant factors of the augmented matrices. The umbrella must exceed that budget.
UMBRELLA_POWER=10
def umbrella_margin(theta_power):return UMBRELLA_POWER-(2*theta_power+2+Q(1,2))
assert umbrella_margin(THETA_POWER)>0 and umbrella_margin(Q(15,4))<=0   # control: the umbrella would fail silently for THETA_POWER >= 3.75
HALO_UMBRELLA={'umbrella_power':UMBRELLA_POWER,'theta_power':THETA_POWER,'exponent_budget':2*THETA_POWER+2+Q(1,2),'margin':umbrella_margin(THETA_POWER),'fails_from_theta_power':Q(15,4)}
out={'status':'PASS_FINE_PRIME_PADDING_EXACT_ARITHMETIC',
     'scope':'Conditional fine-prime padding composition. Fresh native admission is required by verify.py. The cited prime theorem, written gauge-free theorem and inherited all-size interfaces are not proved by this arithmetic. No independent human review is claimed.',
     'geometry_changes':{'theta_power':THETA_POWER,'halo_power':HALO_POWER,'core_power':CORE_POWER,'matrix_exponent':STRASSEN_TAU},
     'halo_umbrella':HALO_UMBRELLA,'complex_lower_short':b,'complex_lower_pinned':certified_complex,
     'native_moment':native,'profile':profile,'m':m,'W':W,
     'online_final_kappa':online,'rows':rows,'rejecting_controls':controls,
     'pr1673_kappa':Q('0.001677160151714381'),'improvement_over_pr1673':rows['struct_boundary_radix_union']['kappa']-Q('0.001677160151714381'),
     'source_sha256':{p.relative_to(WORK).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [SPEC,CLAIM]}}
(HERE/'LEDGER.json').write_text(json.dumps(encode(out),indent=2)+'\n')
print(out['status'])
for name,row in rows.items():
    print(name,'FINAL KAPPA',encode(row['kappa'])['decimal'],
          'positive checks',len(row['strict_checks']),
          'gain over online',encode(row['kappa']-online)['decimal'])
