"""Exact native Word RAM assembly ledger; Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
Arithmetic checks support the separate source-bound proof; they do not prove its identities.
"""
from fractions import Fraction as F
import json

PROVIDER=F('0.0030201656')
Q=F('0.00302016555')
STOP=F(1,10**9)
TARGET=F('0.0030201655')

def check(epsilon=1-F(1,10**8), beta=1-F(3,10**8), target=TARGET, r=F(1,10**9)):
    q=Q
    xi=epsilon*(1+q)-F(3,32)+F(1,10**10)
    savings={
      'main_transform':epsilon*q,
      'complete_address_routing':F(1),
      'fused_gaussian':1-epsilon+q*beta,
      'selected_bit_gather_restore':F(1),
      'group_scans_and_lookup':1-epsilon+beta,
      'boundary_algebra_and_couplings':F(3,32)+xi-epsilon,
      'indexed_sparse_axis_visits':F(1,2)+xi-epsilon,
      'global_precision_record_products':epsilon,
      'core_face_recovery':1-(epsilon+beta+48-128+2)}
    guards={
      'positive_saving':target,
      'source_provider_stopped_margin':PROVIDER*(1-STOP)-q,
      'below_packed_output_limit':1-target,
      'epsilon_below_one':1-epsilon,
      'beta_positive':beta,
      'beta_below_epsilon':epsilon-beta,
      'cap_above_band':xi-F(1,2),
      'cap_below_dimension':epsilon-xi,
      'global_gamma_guard':1-epsilon-r,
      'shifted_group_chirp_guard':1-(beta+2*xi-2+r),
      'group_support_and_key_guard':1-(beta+1-epsilon),
      'membership_guard':1-(beta+2*(1-epsilon)),
      'positive_spare_alpha_exponent':r,
      'strassen_integer_certificate':F(2**45-7**16)}
    guards.update({name+'_excess':value-target for name,value in savings.items()})
    if not all(v>0 for v in guards.values()):
        raise ValueError('failed strict guards: '+','.join(k for k,v in guards.items() if v<=0))
    return {'kappa':str(target),'effective_provider_saving':str(q),'source_provider_saving':str(PROVIDER),'stop':str(STOP),'epsilon':str(epsilon),'beta':str(beta),'r':str(r),'xi':str(xi),
            'nine_native_savings':{k:str(v) for k,v in savings.items()},
            'strict_guards':{k:str(v) for k,v in guards.items()},
            'minimum_excess':str(min(v-target for v in savings.values()))}

def main():
    result=check()
    controls={}
    for name,kwargs in [('epsilon_one',{'epsilon':F(1)}),('unfunded_outer_target',{'target':Q}),
                        ('key_fills_whole_word_power',{'beta':1-F(1,10**8)}),
                        ('membership_at_edge',{'beta':1-F(2,10**8)}),
                        ('normalization_at_edge',{'r':F(1,10**8)})]:
        try:check(**kwargs)
        except ValueError:controls[name]='REJECTED'
        else:raise AssertionError('control accepted: '+name)
    result.update(status='PASS',rejecting_controls=controls,
       scope='Exact native exponent/guard arithmetic only; retained algebraic/analytic identities and full implementation are separate evidence.')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
