#!/usr/bin/env python3
"""Standalone exact price arithmetic; no candidate/project modules imported.

Directed atanh60/Taylor32 rational engine derived from our independent #5377
review, with a separately transcribed selected #5241 outer ledger. Candidate
histograms must come from a separately authenticated independent census.
#5392 changes the paid profile; excess reserve mutation uses 1e-7 rather
than the old profile-specific 1e-8. All enclosure/ledger formulas unchanged.
Predecessors: Ali Romman (construction); Cao Yifan; Cinna Davis; zxv;
Jacob Alan Sussman; Chris R/Clear1nsight. Substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json, time
UNIT=10**55
MODEL='selected-mixed-target-p16-completion1024-v1'
ASSUMPTIONS=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']
def need(v, why):
    if not v: raise ValueError(why)
def down(x): return Q(x.numerator*UNIT//x.denominator,UNIT)
def up(x): return -down(-x)
def mul(a,b):
    p=[x*y for x in a for y in b]; return down(min(p)),up(max(p))
def divide(a,b):
    need(b[0]>0,'nonpositive denominator interval');return mul(a,(1/b[1],1/b[0]))
def difference(a,b):return a[0]-b[1],a[1]-b[0]
def logsmall(x):
    z=(x-1)/(x+1);need(0<=z<=Q(1,3),'logsmall outside [1,2]')
    term=z;s=Q(0)
    for j in range(60):s+=2*term/(2*j+1);term*=z*z
    return down(s),up(s+2*term/(121*(1-z*z)))
@lru_cache(None)
def logint(n):
    need(isinstance(n,int) and n>=1,'rank must be positive integer')
    k=n.bit_length()-1;a,b=logsmall(Q(n,2**k));c,d=logsmall(Q(2));return a+k*c,b+k*d
def exponential(x):
    if x<0:
        a,b=exponential(-x);return down(1/b),up(1/a)
    shift=0
    while x>Q(1,32):x/=2;shift+=1
    term=s=Q(1)
    for j in range(1,33):term*=x/j;s+=term
    a,b=down(s),up(s+term*x/33/(1-x/34))
    for _ in range(shift):a,b=down(a*a),up(b*b)
    return a,b
@lru_cache(None)
def power(rank,exponent):
    exponent=Q(exponent);l,h=logint(rank);l,h=sorted((l*exponent,h*exponent));return exponential(l)[0],exponential(h)[1]
def profile(p):
    for k,v in p.items():
        need((type(k) is int or type(k) is str and k.isdigit()) and type(v) is int,'rank/count must be exact integers')
    p={int(k):v for k,v in p.items()};need(all(k>0 and v>=0 for k,v in p.items()),'invalid rank/count');return {k:v for k,v in p.items() if v}
def moment(p,e):return tuple(sum((n*power(r,Q(e))[i] for r,n in p.items()),Q(0)) for i in (0,1))
def ledger(p):
    k,b,a,q,ep,be,r,st,la=(p[x] for x in ['kappa','b','a','q','epsilon','beta','r0','stop','layout'])
    si,ta=1-b,1-a;it=ta+(1-st)*max(si-ta,Q(0));lf=si+st*(1-si)
    lm=1-(q+a)/2;xi=ep*(1+q)-Q(3,32)+la;key=be+1-ep
    m=dict(main_transform=ep*q,global_coordinate_router=a,fused_gaussian=1-ep+q*be,group_bit_router=1-ep+a*be,group_scans=1-ep+be,boundary_algebraic_matrix=Q(3,32)+xi-ep,sparse_union_movement=xi+Q(1,2)-ep,polynomial_products=ep,microbox_face_corrections=1-(ep+be+48-128+2))
    c=dict(actual_bit_above_effective=p['bit_saving']-a,complex_above_effective=b-a,q_positive=q,complex_endpoint=b-q,q_below_effective=a-q,stop_positive=st,stop_below_one=1-st,leaf_saving_above_effective=(1-st)*b-a,q_below_internal=1-it-q,q_below_leaf=1-lf-q,lambda_above_tau=lm-ta,lambda_above_sigma=lm-si,lambda_above_internal=lm-it,lambda_prime_above_lambda=1-q-lm,lambda_prime_above_leaf=1-q-lf,epsilon_positive=ep,epsilon_below_one=1-ep,cap_above_band=xi-Q(1,2),cap_below_cell=ep-xi,group_positive=be,group_below_dimension=ep-be,support_router_span=1-be,group_gauge_power_slack=1-(2*xi-2)-r-be,actual_logarithmic_group_guard=1-(2*xi-2)-be,global_gamma_power_slack=1-ep-r,actual_logarithmic_gamma_guard=1-ep,alpha_logarithm_absorption=r,group_key_fits_record=1-key,membership_arithmetic_fits_record=1-be-2*(1-ep),microbox_halo_volume=128-48-be,positive_layout_slack=la,short_record_fallback=ep-a,complex_below_one_over_32=Q(1,32)-b,strassen_integer_power_gap=Q(2**45-7**16),theta_positive_polynomial_power=Q(2),cap_below_phase_cell_power=2-xi,halo_covers_generic_inverse_radius=Q(5),union_tag_work_per_visit_fits_record=1-be,union_header_fits_record=1-be,source_axis_superpolynomial=1-ep,gaussian_above_main=m['fused_gaussian']-m['main_transform'],new_complex_uniform_saving_above_b=p['complex_uniform_saving']-b,improvement_over_user_baseline=k-Q('.001730970419199163702738'),new_semantic_guard_with_C1_one=1-ep,fine_prime_halo_umbrella=Q(7,2))
    c.update({n+'_above_kappa':v-k for n,v in m.items()})
    f=dict(new_semantic_group_guard=1-be,new_BIT_row_stock_sublinear_in_active_group=be*Q(997,1000),fixed_halo_explicit_metadata_branch=128-48-ep-be-1,actual_new_BIT_stock_sublinear=be*(1-p['bit_atom']))
    return m,c,f

def enc(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):enc(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [enc(v) for v in x]
    return x

def evaluate(targets,paid,config):
    """Exact arithmetic only. Caller must bind invoice and prove source applicability.

    Supports the one fixed, source-certified tuple only. It does not promote a
    model/profile or generic precision argument to physical/funded admission.
    """
    start=time.monotonic();T,P=profile(targets),profile(paid)
    need(T and P and max(T)==145 and max(P)<=145,'OUTSIDE_PROVED_DOMAIN: ambient rank145')
    need(config['model']==MODEL,'OUTSIDE_PROVED_DOMAIN: model')
    need(config['tuple']=={'power':1024,'cutoff':20,'floor':21,'tail_offset':'1/5','theta':'63/64','logarithm_power':1000},'OUTSIDE_PROVED_DOMAIN: tuple')
    k,s=Q(config['kappa']),Q(config['tested']);lo,hi=map(Q,config['root_bracket']);reserve=Q(config['reserve']);t=1-s
    need(0<k<s<lo<hi<Q(1,20),'saving/root order')
    signs=[difference(moment(T,1-c),moment(P,1-c)) for c in (lo,hi)]
    need(signs[0][0]>0>signs[1][1],'strict root bracket fails')
    signed={r:T.get(r,0)-P.get(r,0) for r in T.keys()|P.keys()}
    der=[];away=[]
    for i in range(16):
        a,b=Q(i,320),Q(i+1,320);lower=Q(0)
        for r,n in signed.items():
            z=mul(power(r,1-b if n>0 else 1-a),logint(r));lower+=n*z[0 if n>0 else 1]
        der.append(lower)
    for i in range(128):
        a,b=Q(1,20)+Q(19*i,2560),Q(1,20)+Q(19*(i+1),2560)
        away.append(sum(n*power(r,1-a if n>0 else 1-b)[1 if n>0 else 0] for r,n in signed.items()))
    need(min(der)>0 and max(away)<0,'fixed-profile ceiling not established')
    target,payment=moment(T,t),moment(P,t)
    ratios={'alpha':divide(payment,target),'gamma':divide(moment(P,t+Q(1,5)),mul(power(20,Q(1,5)),target)),'delta':divide((Q(sum(T.values())*21),)*2,mul(power(20,s),target))}
    need(reserve>0 and ratios['alpha'][1]<1-reserve,'unfunded reserve')
    need(t+Q(1,5)>=1,'tail moment outside source domain')
    need(ratios['gamma'][1]<Q(97,100) and ratios['delta'][1]<Q(97,100),'tails not paid')
    normalized=1/(1+1024*reserve)+Q(4,2**32);eta=mul((t,t),power(145,-1024*s));theta=Q(63,64)
    capacity={'normalized_paid_upper':normalized<1,'tail_block':Q(97,100)**128<Q(1,16),'total_tails':4*Q(97,100)**1024<Q(4,2**32),'split':20**64<21**63,'shifted_exits':2*20**(1024*64)<=145**(1024*63),'eta':eta[0]>theta**1000,'initial_range':power(145,1024*s)[1]<2**1000}
    gap=(s-k)/7;need(gap.numerator==1,'non-unit grid not supported')
    step=gap.denominator
    def wins(j):return (step*j+1)**1000<2**j
    left,right=1,2
    while not wins(right):left,right=right,2*right
    while right-left>1:
        j=(left+right)//2
        if wins(j):right=j
        else:left=j
    j=right;H=step*j
    capacity.update(height_domain=H>8*1024,height_success=wins(j),preceding_grid_fails=not wins(j-1))
    need(all(capacity.values()),'compiler capacity failure')
    bit=config['ordinary_BIT'];atom,after,admitted=map(Q,(bit['atom'],bit['after_cover'],bit['admitted']))
    ordinary=(1-atom)*after+atom*Q('.0000384599')
    need(atom==Q('.004') and ordinary==Q(bit['ordinary_saving']) and atom>ordinary>admitted>s and atom<1-ordinary,'BIT conversion/stock domain fails')
    params=dict(kappa=k,tested_saving=s,complex_uniform_saving=k+6*gap,b=k+5*gap,a=k+4*gap,q=k+3*gap,bit_saving=admitted,bit_atom=atom,epsilon=1-gap,beta=1-3*gap,r0=gap/10,stop=gap,layout=gap,d=gap)
    margins,strict,functional=ledger(params)
    need(len(strict)==54 and len(functional)==4 and min(strict.values())>0 and min(functional.values())>0,'outer predicate failure')
    controls={}
    for n,patch in [('old_BIT',{'bit_saving':Q('.0027')}),('closed_uniform',{'complex_uniform_saving':params['b']}),('tested_as_final_endpoint',{'kappa':s}),('closed_epsilon',{'epsilon':Q(1)}),('missing_layout',{'layout':Q(0)}),('group_full_dimension',{'beta':params['epsilon']})]:
        _,bad,func=ledger(dict(params,**patch));controls[n]=[x for x,v in (bad|func).items() if v<=0];need(controls[n],'mutation accepted: '+n)
    controls['excess_reserve']=ratios['alpha'][0]>1-Q(1,10**7)
    controls['insufficient_reserve_completion']=1/(1+1024*Q(1,10**13))+Q(4,2**32)>1
    controls['power128_tail_envelope']=1/(1+128*reserve)+4*Q(97,100)**128>1
    controls['preceding_grid_rejected']=not wins(j-1)
    controls['raw_upper_has_negative_moment']=signs[1][1]<0
    need(all(controls.values()),'one arithmetic negative control failed')
    return enc({'status':'PASS_INDEPENDENT_EXACT_ARITHMETIC_ONLY','model':MODEL,'targets':T,'paid':P,'productive_count':sum(T.values()),'paid_count':sum(P.values()),'rank_mass_surplus':sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items()),'kappa':k,'tested':s,'root':{'bracket':[lo,hi],'width':hi-lo,'strict_signs':signs,'decreasing_domain':['0','1/20'],'derivative_upper':-min(der),'remaining_domain':['1/20','1'],'remaining_moment_upper':max(away),'scope':'necessary fixed-profile moment ceiling on 0<c<1; no circuit-wide or compiler-optimality claim'},'ratios':ratios,'reserve':reserve,'reserve_strict_slack':1-reserve-ratios['alpha'][1],'normalized_paid_upper':normalized,'completion_strict_slack':1-normalized,'eta':eta,'capacity':capacity,'gap':gap,'uniform_saving':k+6*gap,'H':H,'j':j,'N':'2^'+str(H),'ordinary_BIT':{'atom':atom,'after_cover':after,'ordinary_saving':ordinary,'admitted':admitted,'conversion_slack':ordinary-admitted,'admitted_above_tested':admitted-s,'stock_slack':1-ordinary-atom},'outer':{'parameters':params,'margins':margins,'strict_checks':strict,'functional_checks':functional,'strict_count':len(strict),'functional_count':len(functional),'minimum_strict_slack':min(strict.values()),'minimum_functional_slack':min(functional.values())},'controls':controls,'assumptions':ASSUMPTIONS,'gain_over_selected':k-Q('.0030217758'),'gain_over_independent_5377':k-Q('.00302235'),'seconds':time.monotonic()-start,'no_candidate_code_imported':True,'no_expanded_word_materialized':True,'external_gate_requirements':['independent literal physical gate','independent complete census/ordinary invoice','fresh finite-template precision/stock applicability','source provenance/capsule','registered cold replay before public admission']})
