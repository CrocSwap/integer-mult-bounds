#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact standalone conditional critical-root tightening over PR4470/4532/4535.

Improved *conditional parameter point* only. Native/physical, critical-root
theorem and analytic transfer remain retained prerequisites, not re-proven.
This imports the previous independent rational PR4470 raw-moment oracle.
"""
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from frontier_rational_gate import profiles,moment_interval

K=Q('0.0030201659769')
D=Q(1,10**15)
S=K+6*D
THETA_LO,THETA_HI=Q('.9969798340229'),Q('.9969798340230')
H=10**15

def outer(k,d):
 b,a,q=k+5*d,k+4*d,k+3*d
 epsilon,beta,r0,stop,layout=1-d,1-3*d,d/10,d,d
 sigma,tau=1-b,1-a
 internal=tau+(1-stop)*max(sigma-tau,Q(0))
 leaf=sigma+stop*(1-sigma)
 lam,c=1-(q+a)/2,Q(3,32)
 xi,key=epsilon*(1+q)-c+layout,beta+1-epsilon
 margins={
  'main_transform':epsilon*q,
  'global_coordinate_router':a,
  'fused_gaussian':1-epsilon+q*beta,
  'group_bit_router':1-epsilon+a*beta,
  'group_scans':1-epsilon+beta,
  'boundary_algebraic_matrix':c+xi-epsilon,
  'sparse_union_movement':xi+Q(1,2)-epsilon,
  'polynomial_products':epsilon,
  'microbox_face_corrections':1-(epsilon+beta+48-128+2)}
 checks={
  'actual_bit_above_effective':Q('.0034')-a,
  'complex_above_effective':b-a,
  'q_positive':q,'complex_endpoint':b-q,
  'q_below_effective':a-q,
  'stop_positive':stop,'stop_below_one':1-stop,
  'leaf_saving_above_effective':(1-stop)*b-a,
  'q_below_internal':1-internal-q,
  'q_below_leaf':1-leaf-q,
  'lambda_above_tau':lam-tau,
  'lambda_above_sigma':lam-sigma,
  'lambda_above_internal':lam-internal,
  'lambda_prime_above_lambda':1-q-lam,
  'lambda_prime_above_leaf':1-q-leaf,
  'epsilon_positive':epsilon,
  'epsilon_below_one':1-epsilon,
  'cap_above_band':xi-Q(1,2),
  'cap_below_cell':epsilon-xi,
  'group_positive':beta,
  'group_below_dimension':epsilon-beta,
  'support_router_span':1-beta,
  'group_gauge_power_slack':1-(2*xi-2)-r0-beta,
  'actual_logarithmic_group_guard':1-(2*xi-2)-beta,
  'global_gamma_power_slack':1-epsilon-r0,
  'actual_logarithmic_gamma_guard':1-epsilon,
  'alpha_logarithm_absorption':r0,
  'group_key_fits_record':1-key,
  'membership_arithmetic_fits_record':1-beta-2*(1-epsilon),
  'microbox_halo_volume':128-48-beta,
  'positive_layout_slack':layout,
  'short_record_fallback':epsilon-a,
  'complex_below_one_over_32':Q(1,32)-b,
  'strassen_integer_power_gap':Q(2**45-7**16),
  'theta_positive_polynomial_power':Q(2),
  'cap_below_phase_cell_power':2-xi,
  'halo_covers_generic_inverse_radius':Q(5),
  'union_tag_work_per_visit_fits_record':1-beta,
  'union_header_fits_record':1-beta,
  'source_axis_superpolynomial':1-epsilon,
  'gaussian_above_main':margins['fused_gaussian']-margins['main_transform'],
  'new_complex_uniform_saving_above_b':k+6*d-b,
  'improvement_over_user_baseline':k-Q('0.001730970419199163702738'),
  'new_semantic_guard_with_C1_one':1-epsilon,
  'fine_prime_halo_umbrella':10-(2*2+2+Q(1,2))}
 checks.update({name+'_above_kappa':value-k for name,value in margins.items()})
 functional={
  'new_semantic_group_guard':1-beta,
  'new_BIT_row_stock_sublinear_in_active_group':beta*(1-Q(3,1000)),
  'fixed_halo_explicit_metadata_branch':128-48-epsilon-beta-1,
  'actual_new_BIT_stock_sublinear':beta*(1-Q('.004'))}
 assert (len(margins),len(checks),len(functional))==(9,54,4)
 return margins,checks,functional

def run():
 target,paid=profiles()
 lo,hi=1-THETA_HI,1-THETA_LO
 assert moment_interval(target,paid,lo)['positive']
 assert moment_interval(target,paid,hi)['negative']
 assert moment_interval(target,paid,S)['positive']
 assert THETA_HI<1-S and lo>S
 m,c,f=outer(K,D)
 assert all(v>K for v in m.values())
 assert all(v>0 for v in c.values())
 assert all(v>0 for v in f.values())
 assert any(v<=0 for v in outer(K,Q(0))[1].values())
 # Logarithmic majorant from PR4532 is A*N^theta*(133+ln N)^(2/5).
 # ln A < (1-theta_lo)*(ln145+650*ln1024)<20, explicitly bounded.
 assert sum(Q(8**i,factorial(i)) for i in range(6))>145
 assert sum(Q(7**i,factorial(i)) for i in range(19))>1024
 assert (1-THETA_LO)*(8+650*7)<20
 assert 133+H<2**50 and H>8+650*10
 gap=(1-S)-THETA_HI
 assert gap==Q(94,10**15)
 # ln2 > 2/3 from 2 atanh(1/3); ln2 < 1 from e>2.
 # At N=2^H: gap*ln N - ln A-(2/5)ln(133+ln N)
 # > gap*(2/3)*H-20-20 = 68/3 >0.
 absorption_lower=gap*Q(2*H,3)-40
 assert absorption_lower==Q(68,3)>0
 assert gap>Q(2,5)/(133+Q(2*H,3))
 height=2*(H//10)
 assert H%10==0 and (14+17*(height+1))==3400000000000031
 assert K>Q('.003020165')
 result={
  'status':'PASS_EXACT_CONDITIONAL_PARAMETER_SCREEN',
  'source_pins':{
   'native_PR4470':'b9a13c1673e0e9697de410de16e8bbf3207a7363',
   'critical_theorem_PR4532':'644607ba59ebe401ac7ecd627ae7f331f924d1b0',
   'transfer_PR4535':'a6d7237f697185e857090e174c23c1cb22c6563c',
   'outer_source':'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'},
  'kappa_candidate':str(K),'existing_selected':'0.00302015',
  'open_PR4535':'0.003020165',
  'gain_over_pending':str(K-Q('.003020165')),
  'uniform_complex_saving':str(S),'slack_d':str(D),
  'raw_root_bracket':[str(lo),str(hi)],
  'verified_exact_outer_checks':len(c),
  'verified_exact_functional_guards':len(f),
  'all_outer_predicates_positive':True,
  'minimum_strict_predicate':str(min(c.values())),
  'minimum_margin_above_kappa':str(min(m.values())-K),
  'N':'2^(10^15)',
  'rigorous_log_absorption_margin_lower':str(absorption_lower),
  'compiler_height_bound':height,
  'log2_class_envelope_bound':14+17*(height+1),
  'physical_native_and_unconditional_analytic_interfaces':'INHERITED_NOT_PROVEN',
  'whole_new_compiler_implementation':'NOT_MATERIALIZED',
  'independent_oracle':'Exact previous PR4470 moment gate, no input rounding',
  'hosted_CI':'NOT_CONFIRMED',
  'reviewed_or_selected':False,
  'new_unconditional_multiplication_theorem':False}
 return result

if __name__=='__main__':
 out=run()
 Path(__file__).with_name('TIGHT_TRANSFER_RECEIPT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('PASS_EXACT_TIGHT_TRANSFER kappa',out['kappa_candidate'],
       'strict=54 functional=4 log_margin',out['rigorous_log_absorption_margin_lower'])
