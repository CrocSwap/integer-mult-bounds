"""Independent transcription of the inherited 47 rational assembly slacks.

The positive bridge gaps remain explicit inputs. No finite bridge or all-size
claim follows from these formulas. See NOTICE.md for the inherited lineage.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as F
import re
CAP_NAME='b_below_one_over32'
def rational(value):
    if type(value) is int or type(value) is F:
        return F(value)
    if type(value) is str and re.fullmatch(r'-?[0-9]+(?:/[1-9][0-9]*)?', value):
        return F(value)
    raise ValueError('Expected an exact integer or rational fraction; floats/bools rejected')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def direct_slacks(a, b, beta, h, kappa, scalar_gap=1, row_gap=1):
    """Independent transcription of the displayed equations, using exact fractions.

    Return violations rather than suppressing the production cap. The caller
    explicitly chooses a diagnostic evaluation mode in verdict().
    """
    a,b,beta,h,kappa,scalar_gap,row_gap = map(rational,
        (a,b,beta,h,kappa,scalar_gap,row_gap))
    q = a*(1-2*h)
    require(1+q != 0, 'Undefined epsilon')
    eps = (1-h)/(1+q)
    G = eps*q
    tau, sigma = 1-a, 1-b
    lp, c = 1-q, q+h/4
    lam = (tau+lp)/2
    r, delta = (G+1-eps)/2, h/8
    internal = tau+(1-beta)*max(sigma-tau, F(0))
    leaf = sigma+beta*(1-sigma)
    margins = {'g1':1-eps, 'g2':a, 'g3':G, 'g4':a,
               'g5':min(1-eps-delta,r-delta), 'g6':1-eps-delta,'g7':eps}
    slacks = {
        'a_positive':a, 'a_below_b':b-a, CAP_NAME:F(1,32)-b,
        'beta_positive':beta, 'beta_below_one':1-beta,
        'phase_leaf_above_bit':(1-beta)*b-a,
        'q_positive':q, 'q_below_internal':1-internal-q,
        'q_below_leaf':1-leaf-q, 'c_positive':c,'c_below_one':1-c,
        'q_below_reservations':c-q, 'lambda_above_tau':lam-tau,
        'lambda_above_sigma':lam-sigma, 'lambda_above_internal':lam-internal,
        'lambda_prime_above_lambda':lp-lam, 'compact_leaf':lp-leaf,
        'compact_reservations':lp-(1-c),'lambda_prime_below_one':q,
        'epsilon_positive':eps,'epsilon_below_one':1-eps,'guard_width':1-eps,
        'K_geometry':1-eps*(1+c),'K_dominates_log':eps*c,
        'record_suffix':1-eps, 'phase_local':1-eps-delta,
        'phase_boundary':r-delta, 'gamma_sublinear':1-eps-r,
        'cell_above_band':eps-(1-r)/2,'prime_interval_packing':1-eps,
        'alpha_positive':r,'alpha_below_one':1-r,
        'alpha_below_one_fourth':F(1,4)-r,'delta_positive':delta,
        'delta_below_one_eighth':F(1,8)-delta,'short_record_fallback':eps-a,
        'small_field_exposure':1-eps-G,
        'artificial_boundary':8-eps+r-delta-G,
        'literal_scalar_guard':scalar_gap,'row_product_gap':row_gap}
    slacks.update({name+'_above_kappa':value-kappa for name,value in margins.items()})
    preconditions = {'positive_backoff':h>0, 'backoff_below_half':h<F(1,2),
                     'positive_kappa':kappa>0}
    return dict(slacks=slacks, margins=margins, preconditions=preconditions,
                parameters=dict(a=a,b=b,beta=beta,h=h,kappa=kappa,q=q,
                                epsilon=eps,G=G,r=r,delta=delta,c=c))


def factored_slacks(a,b,beta,h,kappa,scalar_gap=1,row_gap=1):
    """Second evaluation, from the proof's factorizations for a < b."""
    a,b,beta,h,kappa,scalar_gap,row_gap = map(rational,
        (a,b,beta,h,kappa,scalar_gap,row_gap))
    require(a<b, 'Factorization assumes a < b')
    require(h>=0, 'Minimum-margin factorization assumes h >= 0')
    q=a*(1-2*h); eps=(1-h)/(1+q); G=eps*q; L=(1-beta)*b-a
    r=G+h/2; c=q+h/4
    result={
        'a_positive':a,'a_below_b':b-a,CAP_NAME:F(1,32)-b,
        'beta_positive':beta,'beta_below_one':1-beta,'phase_leaf_above_bit':L,
        'q_positive':q,'q_below_internal':2*a*h,'q_below_leaf':L+2*a*h,
        'c_positive':c,'c_below_one':1-c,'q_below_reservations':h/4,
        'lambda_above_tau':a*h,'lambda_above_sigma':b-a+a*h,
        'lambda_above_internal':a*h,'lambda_prime_above_lambda':a*h,
        'compact_leaf':L+2*a*h,'compact_reservations':h/4,
        'lambda_prime_below_one':q,'epsilon_positive':eps,
        'epsilon_below_one':G+h,'guard_width':G+h,
        'K_geometry':h*(1-eps/4),'K_dominates_log':eps*c,
        'record_suffix':G+h,'phase_local':G+7*h/8,'phase_boundary':G+3*h/8,
        'gamma_sublinear':h/2,'cell_above_band':eps-(1-r)/2,
        'prime_interval_packing':G+h,'alpha_positive':r,'alpha_below_one':1-r,
        'alpha_below_one_fourth':F(1,4)-r,'delta_positive':h/8,
        'delta_below_one_eighth':(1-h)/8,'short_record_fallback':eps-a,
        'small_field_exposure':h,'artificial_boundary':8-eps+3*h/8,
        'literal_scalar_guard':scalar_gap,'row_product_gap':row_gap}
    margins={'g1':G+h,'g2':a,'g3':G,'g4':a,'g5':G+3*h/8,'g6':G+7*h/8,'g7':eps}
    result.update({name+'_above_kappa':value-kappa for name,value in margins.items()})
    return result


def serial(value):
    if type(value) is F: return str(value)
    if isinstance(value,dict): return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [serial(v) for v in value]
    return value

