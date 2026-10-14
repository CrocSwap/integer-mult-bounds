"""Exact free-epsilon refinement of PR2044; no supplier or theorem change.

The ledger formulas below are retained from PR2044 / Jeremy Kothe's package,
PR1786 (Chafik Boukhalfa), PR1673 (Vlado Vojdanovski), and PR1758 lineage.
Only DELTA_E changes. Parent native/moment admission is a separate required gate.
Prepared under dataisfire with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
import json,sys
sys.set_int_max_str_digits(0)
if not __debug__: raise RuntimeError('Assertions must be enabled')
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'capped-fusion-t74-k554'
spec=json.loads((PARENT/'new/SPEC.json').read_text())
BJ=json.loads((PARENT/'outer/B.json').read_text())
DIG=spec['outer_refinement']['endpoint_digits']
R0=Q(1,10**(DIG+10)); ZETA=Q(1,10**(DIG+12)); SLACK=R0; GAP=R0; STOP=Q(1,10**(DIG+16))
FLOOR=10**(DIG+46); BACKOFF=Q(1,10**(DIG+22)); B_GAP=R0
DELTA_E=Q(1025,1024)*R0
EPS=1-DELTA_E; BETA=1-3*DELTA_E
THETA_POWER=Q(2); HALO_POWER=48; CORE_POWER=128; STRASSEN_TAU=Q(45,16)
certified_complex=Q(spec['expected']['complex_lower'])
bit=Q('0.001733427039589844234749')
b=certified_complex-B_GAP
assert b==Q(BJ['b'])
q=b-GAP; a=(q+b)/2
online=Q(spec['expected']['kappa']); old=Q('0.001673360105405778')
assert 0<q<a<b<certified_complex<bit
profile={int(r):int(n) for r,n in spec['expected']['global_profile'].items()}
m=spec['geometry']['dimension']; W=spec['expected']['live']
assert (m,W)==(73,66304)
assert profile=={int(k):v for k,v in BJ['profile'].items()}
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
    checks.update({n+'_above_kappa':v-kappa for n,v in margins.items()})
    assert margins['boundary_algebraic_matrix']==saving+slack
    assert margins['sparse_union_movement']==saving+slack+(tau_eff-2)/2
    return {'kind':kind,'kappa':kappa,'epsilon':eps,'xi':xi,'beta':beta,
            'q':q_,'a':a,'r0':r,'zeta':zeta,'slack':slack,
            'margins':margins,'strict_checks':checks}
