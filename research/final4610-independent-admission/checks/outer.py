#!/usr/bin/env python3
"""Independent Fraction evaluation of retained PR4359 outer formulas.

Formula source: zxv PR4359 endpoint, Jacob Alan Sussman mixed-target flow,
Cinna Davis 4470 and intqwq 4610 instantiation. No repository engine imported.
"""
from fractions import Fraction as F

def parameters(kappa,tested):
    kappa,tested=F(kappa),F(tested);g=(tested-kappa)/7
    assert g>0
    return dict(kappa=kappa,tested_saving=tested,complex_uniform_saving=kappa+6*g,b=kappa+5*g,a=kappa+4*g,q=kappa+3*g,bit_saving=F(17,5000),epsilon=1-g,beta=1-3*g,r0=g/10,stop=g,layout=g,d=g)
def evaluate(p):
    k,b,a,q,e,B,r,s,l=[p[x] for x in ['kappa','b','a','q','epsilon','beta','r0','stop','layout']]
    sig,tau=1-b,1-a;inside=tau+(1-s)*max(sig-tau,0);leaf=sig+s*(1-sig)
    lam=1-(q+a)/2;xi=e*(1+q)-F(3,32)+l;key=B+1-e
    margins=dict(main_transform=e*q,global_coordinate_router=a,fused_gaussian=1-e+q*B,group_bit_router=1-e+a*B,group_scans=1-e+B,boundary_algebraic_matrix=F(3,32)+xi-e,sparse_union_movement=xi+F(1,2)-e,polynomial_products=e,microbox_face_corrections=1-(e+B+48-128+2))
    checks={
      'actual_bit_above_effective':p['bit_saving']-a,
      'complex_above_effective':b-a,'q_positive':q,'complex_endpoint':b-q,'q_below_effective':a-q,
      'stop_positive':s,'stop_below_one':1-s,'leaf_saving_above_effective':(1-s)*b-a,
      'q_below_internal':1-inside-q,'q_below_leaf':1-leaf-q,'lambda_above_tau':lam-tau,
      'lambda_above_sigma':lam-sig,'lambda_above_internal':lam-inside,
      'lambda_prime_above_lambda':1-q-lam,'lambda_prime_above_leaf':1-q-leaf,
      'epsilon_positive':e,'epsilon_below_one':1-e,'cap_above_band':xi-F(1,2),
      'cap_below_cell':e-xi,'group_positive':B,'group_below_dimension':e-B,'support_router_span':1-B,
      'group_gauge_power_slack':1-(2*xi-2)-r-B,'actual_logarithmic_group_guard':1-(2*xi-2)-B,
      'global_gamma_power_slack':1-e-r,'actual_logarithmic_gamma_guard':1-e,'alpha_logarithm_absorption':r,
      'group_key_fits_record':1-key,'membership_arithmetic_fits_record':1-B-2*(1-e),
      'microbox_halo_volume':128-48-B,'positive_layout_slack':l,'short_record_fallback':e-a,
      'complex_below_one_over_32':F(1,32)-b,'strassen_integer_power_gap':F(2**45-7**16),
      'theta_positive_polynomial_power':F(2),'cap_below_phase_cell_power':2-xi,
      'halo_covers_generic_inverse_radius':F(48-43),'union_tag_work_per_visit_fits_record':1-B,
      'union_header_fits_record':1-B,'source_axis_superpolynomial':1-e,
      'gaussian_above_main':margins['fused_gaussian']-margins['main_transform'],
      'new_complex_uniform_saving_above_b':p['complex_uniform_saving']-b,
      'improvement_over_user_baseline':k-F('.001730970419199163702738'),
      'new_semantic_guard_with_C1_one':1-e,'fine_prime_halo_umbrella':10-(2*2+2+F(1,2))}
    checks.update({n+'_above_kappa':v-k for n,v in margins.items()})
    functional=dict(new_semantic_group_guard=1-B,new_BIT_row_stock_sublinear_in_active_group=B*(1-F(3,1000)),fixed_halo_explicit_metadata_branch=128-48-e-B-1,actual_new_BIT_stock_sublinear=B*(1-F(1,250)))
    assert len(checks)==54 and len(functional)==4
    return dict(parameters=p,margins=margins,strict_checks=checks,functional_checks=functional,all_positive=all(x>0 for g in [checks,functional] for x in g.values()))
def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    if isinstance(x,list):return [encode(v) for v in x]
    return x
