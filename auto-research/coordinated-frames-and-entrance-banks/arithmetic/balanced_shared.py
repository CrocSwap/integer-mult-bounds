"""Paid balanced assembly with an explicit uniform-bit/shared-complex bridge.

The complete 47-constraint arithmetic body is PR141 balanced_stopped.py,
with only bridge plumbing and an actual-bit-supplier bound added. Original
PR34/RaD/PR23, icekylinx and PR100/103 attribution is retained in the pinned
source. It does not assert a finite old coarse profile for the uniform bit
supplier. General cutoff/analytic/word contracts remain external.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from fractions import Fraction as Q
from shared_bridge import rational, require, validate_shared_bridge

def assembly(finite_bridge, complex_row, a_bit, kappa, beta=Q(1,20), h=Q(1,10**12),
             a_complex=Q(717,10**7), *, original_prefix=False,
             old_guard=False, old_exposures=False):
    """Return 47 strict slacks and seven margins, or raise InvalidAssembly.

    The three keyword switches are negative controls: they impose the old
    prefix, nonlinear guard, or old separate movement charges at these SAME
    balanced parameters. They do not silently optimize an alternative family.
    """
    f = validate_shared_bridge(finite_bridge, complex_row)
    a, b, kappa, beta, h = map(rational, (a_bit,a_complex,kappa,beta,h))
    require(a <= f['bit_uniform']['ordinary_saving'], 'transfer saving exceeds actual uniform bit supplier')
    require(0 < h < Q(1,2) and kappa > 0, 'positive backoff and saving required')
    tau, sigma = 1-a, 1-b
    q = a*(1-2*h)
    require(1+q != 0, 'undefined balanced epsilon')
    lp, c, eps = 1-q, q+h/4, (1-h)/(1+q)
    lam = (tau+lp)/2
    G = eps*q
    r, delta = (G+1-eps)/2, h/8
    C1 = Q(19991,10000) if old_guard else Q(1)
    margins = dict(g1=1-eps, g2=a, g3=G, g4=a,
                   g5=min(1-eps-delta,r-delta), g6=1-eps-delta, g7=eps)
    if original_prefix:
        margins['g1'] = 1-eps*(1+c)
    if old_exposures:
        margins.update(g2=eps*c*a, g4=a*(1-eps))
    internal = tau+(1-beta)*max(sigma-tau,Q(0))
    leaf = sigma+beta*(1-sigma)
    slacks = dict(a_positive=a, a_below_b=b-a, b_below_one_over32=Q(1,32)-b,
        beta_positive=beta, beta_below_one=1-beta, phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q, q_below_internal=1-internal-q, q_below_leaf=1-leaf-q,
        c_positive=c, c_below_one=1-c, q_below_reservations=c-q,
        lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal, lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf, compact_reservations=lp-(1-c), lambda_prime_below_one=q,
        epsilon_positive=eps, epsilon_below_one=1-eps, guard_width=1-eps*C1,
        K_geometry=1-eps*(1+c), K_dominates_log=eps*c,
        record_suffix=1-eps, phase_local=1-eps-delta, phase_boundary=r-delta,
        gamma_sublinear=1-eps-r, cell_above_band=eps-(1-r)/2,
        prime_interval_packing=1-eps, alpha_positive=r, alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r, delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta, short_record_fallback=eps-a,
        small_field_exposure=1-eps-G, artificial_boundary=8-eps+r-delta-G,
        literal_scalar_guard=Q(f['semantic']['strict_literal_gap']),
        row_product_gap=f['rows']['degree_gap'])
    slacks.update({name+'_above_kappa': value-kappa for name,value in margins.items()})
    require(len(slacks) == 47 and len(margins) == 7, 'constraint list incomplete')
    failed = {name:str(value) for name,value in slacks.items() if value <= 0}
    require(not failed, str(failed))
    require(min(margins.values()) == G, 'unexpected controlling margin')
    require(1-eps-G == h and 1-eps-r == h/2, 'balanced identities failed')
    require(1-eps*(1+c) == h-eps*h/4, 'geometric identity failed')
    parameters = dict(a_bit=a, a_complex=b, tau=tau, sigma=sigma, beta=beta,h=h,
        q=q,c=c,epsilon=eps,lambda_=lam,lambda_prime=lp,alpha_squared_power=r,
        delta=delta,C0=f['semantic']['C0'],C1=C1,kappa=kappa)
    return dict(parameters=parameters,constraints=slacks,margins=margins,
        minimum_margin=G,absorption_gap=G-kappa,scoped_limit=a/(1+a),
        recurrence=dict(internal=internal,leaf=leaf,reservations=1-c),finite_bridge=f)
