"""Independent stdlib finite compiler audit. No project code is imported.

Exact atanh logarithm and Taylor exponential with rational remainder bounds;
all acceptance comparisons are rational/integer. Authored for the swarm audit,
retaining Cao Yifan/zxv/Cinna Davis/Jacob Alan Sussman predecessor credit.
"""
from fractions import Fraction as F
from collections import Counter
from functools import lru_cache
from pathlib import Path
from hashlib import sha256
import argparse, json, time, platform, re
from . import source

UNIT=2**240
def down(x): return F(x.numerator*UNIT//x.denominator,UNIT)
def up(x): return -down(-x)
def add(x,y): return x[0]+y[0],x[1]+y[1]
def mul(x,y):
    v=[a*b for a in x for b in y];return down(min(v)),up(max(v))
def divide(x,y):
    assert y[0]>0
    return mul(x,(1/y[1],1/y[0]))
def logbase(x):
    z=(x-1)/(x+1);term=z;s=F(0)
    for j in range(100):s+=term/F(2*j+1);term*=z*z
    rem=2*abs(term)/(201*(1-z*z))
    return down(2*s-rem),up(2*s+rem)
@lru_cache(None)
def logint(n):
    b=n.bit_length()-1
    a=logbase(F(n,2**b));l2=logbase(F(2))
    return a[0]+b*l2[0],a[1]+b*l2[1]
def exp_point(x):
    if x<0:
        l,u=exp_point(-x);return down(1/u),up(1/l)
    shifts=0
    while x>F(1,16):x/=2;shifts+=1
    term=s=F(1)
    for j in range(1,51):term=term*x/j;s+=term
    nxt=term*x/51
    # Ratios in the remaining positive Taylor series are <= x/52.
    l,u=down(s),up(s+nxt/(1-x/52))
    for _ in range(shifts):l,u=down(l*l),up(u*u)
    return l,u
def power(n,e):
    l,u=logint(n);l,u=(e*l,e*u) if e>=0 else (e*u,e*l)
    return exp_point(l)[0],exp_point(u)[1]
def moment(p,e):
    l=u=F(0)
    for n,c in p.items():a,b=power(n,e);l+=c*a;u+=c*b
    return l,u
def ledger(p):
    # Manually transcribed from the exact source; no AST/source execution.
    k,b,a,q,ep,be,r,st,la=(p[x] for x in ['kappa','b','a','q','epsilon','beta','r0','stop','layout'])
    si,ta=1-b,1-a;it=ta+(1-st)*max(si-ta,F(0));lf=si+st*(1-si)
    lm=1-(q+a)/2;xi=ep*(1+q)-F(3,32)+la;key=be+1-ep
    m=dict(main_transform=ep*q,global_coordinate_router=a,fused_gaussian=1-ep+q*be,group_bit_router=1-ep+a*be,group_scans=1-ep+be,boundary_algebraic_matrix=F(3,32)+xi-ep,sparse_union_movement=xi+F(1,2)-ep,polynomial_products=ep,microbox_face_corrections=1-(ep+be+48-128+2))
    c=dict(actual_bit_above_effective=p['bit_saving']-a,complex_above_effective=b-a,q_positive=q,complex_endpoint=b-q,q_below_effective=a-q,stop_positive=st,stop_below_one=1-st,leaf_saving_above_effective=(1-st)*b-a,q_below_internal=1-it-q,q_below_leaf=1-lf-q,lambda_above_tau=lm-ta,lambda_above_sigma=lm-si,lambda_above_internal=lm-it,lambda_prime_above_lambda=1-q-lm,lambda_prime_above_leaf=1-q-lf,epsilon_positive=ep,epsilon_below_one=1-ep,cap_above_band=xi-F(1,2),cap_below_cell=ep-xi,group_positive=be,group_below_dimension=ep-be,support_router_span=1-be,group_gauge_power_slack=1-(2*xi-2)-r-be,actual_logarithmic_group_guard=1-(2*xi-2)-be,global_gamma_power_slack=1-ep-r,actual_logarithmic_gamma_guard=1-ep,alpha_logarithm_absorption=r,group_key_fits_record=1-key,membership_arithmetic_fits_record=1-be-2*(1-ep),microbox_halo_volume=128-48-be,positive_layout_slack=la,short_record_fallback=ep-a,complex_below_one_over_32=F(1,32)-b,strassen_integer_power_gap=F(2**45-7**16),theta_positive_polynomial_power=F(2),cap_below_phase_cell_power=2-xi,halo_covers_generic_inverse_radius=F(5),union_tag_work_per_visit_fits_record=1-be,union_header_fits_record=1-be,source_axis_superpolynomial=1-ep,gaussian_above_main=m['fused_gaussian']-m['main_transform'],new_complex_uniform_saving_above_b=p['complex_uniform_saving']-b,improvement_over_user_baseline=k-F('.001730970419199163702738'),new_semantic_guard_with_C1_one=1-ep,fine_prime_halo_umbrella=F(7,2))
    c.update({n+'_above_kappa':v-k for n,v in m.items()})
    f=dict(new_semantic_group_guard=1-be,new_BIT_row_stock_sublinear_in_active_group=be*F(997,1000),fixed_halo_explicit_metadata_branch=128-48-ep-be-1,actual_new_BIT_stock_sublinear=be*F(996,1000))
    return m,c,f
def enc(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):enc(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [enc(y) for y in x]
    return x
def run(root,invoice):
    start=time.monotonic();pkg='research/kappa-round6-compiler-tightening-20261022/'
    a=source.js(pkg+'ARITHMETIC.json');controller=source.js('research/joint-helper-lattice/CONTROLLER.json')
    assert source.digest(source.raw('research/joint-helper-lattice/CONTROLLER.json'))==a['source_sha256']['research/joint-helper-lattice/CONTROLLER.json']
    assert source.digest(source.raw('research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'))==a['source_sha256']['research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py']
    H={4:28,7:7,8:47,9:326};P0={1:2201,2:412,3:510,4:127,5:40,8:8};T,P=Counter(),Counter()
    for e in controller['physical_events']:
        if e[0]=='LOCAL':T.update(H);P.update(P0)
        elif e[0]=='QUERY_SHEAR':P[1]+=112
        elif e[0]=='IDLE':P[8*len(e[2])]+=224
        elif e[0] in {'ADD','SIGNED_SWAP'}:pass # Scalar operations, priced below.
        else:raise AssertionError(e[0])
    for e in controller['diagonal']:T[1+8*sum(e[1:])]+=112
    assert dict(T)=={int(k):v for k,v in invoice['targets'].items()} and dict(P)=={int(k):v for k,v in invoice['paid'].items()}
    assert dict(T)=={int(k):v for k,v in a['targets'].items()} and dict(P)=={int(k):v for k,v in a['paid'].items()}
    assert H=={int(k):v for k,v in a['local_helpers'].items()} and P0=={int(k):v for k,v in a['local_paid'].items()}
    assert sum(T.values())==10928 and sum(P.values())==64404
    assert sum(n*c for n,c in T.items())-sum(n*c for n,c in P.items())==752
    k=F('.0030217758');s=F('.00302177581');g=(s-k)/7;t=1-s;reserve=F(1,10**11)
    assert F(a['kappa'])==k and F(a['strictification']['tested'])==s
    tt,pp=moment(T,t),moment(P,t)
    rootlow,roothigh=map(F,a['raw_root_interval'])
    ml=moment(T,1-rootlow)[0]-moment(P,1-rootlow)[1]
    mh=moment(T,1-roothigh)[1]-moment(P,1-roothigh)[0]
    assert ml>0>mh and s<rootlow
    ratios=dict(alpha=divide(pp,tt),gamma=divide(moment(P,t+F(1,5)),mul(power(20,F(1,5)),tt)),delta=divide((F(sum(T.values())*21),)*2,mul(power(20,s),tt)))
    for n,x in ratios.items():assert F(a['strictification'][n]['lower'])<=x[0]<=x[1]<=F(a['strictification'][n]['upper'])
    assert ratios['alpha'][1]<1-reserve and ratios['alpha'][0]>1-F(1,10**9)
    assert ratios['gamma'][1]<F(97,100) and ratios['delta'][1]<F(97,100)
    assert F(97,100)**128<F(1,16)
    normalized=1/(1+1024*reserve)+F(4,2**32)
    assert normalized==F(a['strictification']['normalized_paid_upper'])<1
    # 1024=8*128; both tails contribute <=2/2^32, total <=4/2^32.
    assert 2*F(97,100)**1024+2*F(97,100)**1024<F(4,2**32)
    assert t+F(1,5)>=1 and 20**64<21**63
    theta=F(63,64);assert 2*(20**1024)**64<=(145**1024)**63
    # Ambient m=145^1024; compiler eta=t*m^(t-1).
    assert 1024*s<F(25,8) and 145<2**8
    assert 2*145**3==6097250 and theta**1000<t/F(6097250)
    assert 6097250<2**1000
    eta=mul((t,t),power(145,-1024*s));assert eta[0]>theta**1000
    j=55099;step=g.denominator;h=step*j
    assert g==F(1,700000000000) and h==a['compiler']['H']==38569300000000000 and j==a['compiler']['integer_test_exponent']
    assert (h+1)**1000<2**j and (step*(j-1)+1)**1000>=2**(j-1)
    assert h>8*1024
    # Strict convex log ratio has one positive crossing; previous-grid failure
    # plus success establishes minimality on this grid (not among programs).
    uniform=k+6*g;assert s-uniform==g and uniform==F(a['compiler']['uniform_saving'])
    p=dict(kappa=k,tested_saving=s,complex_uniform_saving=uniform,b=k+5*g,a=k+4*g,q=k+3*g,bit_saving=F(17,5000),epsilon=1-g,beta=1-3*g,r0=g/10,stop=g,layout=g,d=g)
    for n,v in p.items():assert F(a['outer']['parameters'][n])==v
    m,c,f=ledger(p)
    for n,tab in [('margins',m),('strict_checks',c),('functional_checks',f)]:assert tab=={x:F(y) for x,y in a['outer'][n].items()}
    assert len(c)==54 and len(f)==4 and min(c.values())>0 and min(f.values())>0
    assert 0<f['actual_new_BIT_stock_sublinear']<1 and 0<f['new_BIT_row_stock_sublinear_in_active_group']<1
    controls={}
    for n,patch in [('old_BIT',dict(bit_saving=F('.0027'))),('closed_uniform',dict(complex_uniform_saving=p['b'])),('unfunded_endpoint',dict(kappa=s)),('closed_epsilon',dict(epsilon=F(1))),('missing_layout',dict(layout=F(0))),('group_full_dimension',dict(beta=p['epsilon']))]:
        _,bad,_=ledger(dict(p,**patch));failed=[x for x,v in bad.items() if v<=0];assert failed;controls[n]=failed
    # Explicit parameter mutations fail charged compiler inequalities.
    controls['old_reserve_rejected']=ratios['alpha'][0]>1-F(1,10**9)
    controls['power128_does_not_fit_rounded_tail_envelope']=1/(1+128*reserve)+4*F(97,100)**128>1
    controls['preceding_grid_rejected']=(step*(j-1)+1)**1000>=2**(j-1)
    assert all(controls[x] for x in controls)
    scalar=158168;routes=(sum(P0.values())+2*408+688)*1000
    raw=18*10**7+15*1792+32*112*(len(controller['physical_events'])+sum(len(controller['boundaries'][x+'_program']) for x in ['left','right']))
    assert routes==4802000 and scalar+routes<10**7 and raw==181098496<10**9
    assert a['nonrecursive']=={'local_scalar':scalar,'local_routes':routes,'raw_scalar_upper':raw}
    bit=a['ordinary_BIT'];ordinary=(1-F(bit['atom']))*F(bit['after_cover'])+F(bit['atom'])*F('.0000384599')
    assert ordinary==F(bit['ordinary_saving']) and F(bit['atom'])>ordinary>F(bit['admitted'])>s
    assert F(bit['atom'])<1-ordinary
    result=dict(status='PASS_INDEPENDENT_EXACT_FINITE_COMPILER_AND_58_OUTER',command='final4610-independent-admission compiler stage',python=platform.python_version(),seconds=time.monotonic()-start,repository_pin='ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c',arithmetic_sha256=source.digest(source.raw(pkg+'ARITHMETIC.json')),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),targets=dict(T),paid=dict(P),kappa=k,tested=s,ratios=ratios,eta=eta,normalized_paid_upper=normalized,completion_slack=1-normalized,uniform_saving=uniform,gap=g,H=h,j=j,root_signs=[ml,mh],nonrecursive=dict(scalar=scalar,routes=routes,raw_controller_scalar=raw),outer_strict_count=len(c),functional_count=len(f),minimum_outer_strict_slack=min(c.values()),outer_strict_slacks=c,functional_slacks=f,controls=controls,fresh_author_recorded_modules=[],reused_author_recorded_modules=[],objects_checked=False,Lean_run=False,scope='Fresh independent exact arithmetic from the independently derived invoice; no Lean/log acceptance inherited and no end-to-end multiplication theorem.')
    return enc(result)
