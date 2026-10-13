"""Exact, import-safe balanced copied-center semantic assembly arithmetic.

The PR36 copied-center guard uses E=64*(W+m+G+1)^3, including G.
Its complex saving is 717/10^7. All balanced parameter formulas are unchanged.

Adapted from Zhihao Chen PR23/29 semantic assembly (Apache-2.0), RaD's
balanced transform / arbitrary routing / bulk resampling composition, and
jamesyc PR34's check_composition.py at 7fecbe3. PR34 source is research/reversed-two-stage/check_composition.py in that
pinned upstream commit. Original parameterized transcription by the
research workers is in rectangular-dimensions/next/assembly_parameterized.py.

This checks arithmetic, not physical corner existence, producer correctness,
or inherited all-size tape/analytic hypotheses. No imports execute producers,
parse argv, read files, change globals, or mutate the supplied finite bridge.
"""
from fractions import Fraction as Q


class InvalidAssembly(AssertionError):
    """A named exact input validation or strict inequality failed."""


def require(condition, message):
    if not condition:
        raise InvalidAssembly(message)


def rational(value):
    # Fraction(float) silently preserves binary floating error; forbid it.
    require(type(value) in (int, str, Q), 'expected integer or exact rational string/Fraction')
    return Q(value)


def integer(value):
    x = rational(value)
    require(x.denominator == 1, 'nonintegral graph constant')
    return x.numerator


def ceil(value):
    return -(-value.numerator // value.denominator)


def halving_degree(m, child):
    require(0 < child < m, 'child must strictly contract')
    degree = 1
    while m**degree <= 2 * child**degree:
        degree += 1
    return degree


def validate_bridge(finite_bridge):
    """Recompute rather than trust stored semantic and product-stock totals.

    scalar_group_upper remains a supplied, proof-certified local scalar upper
    charge. Its producer provenance is external to this arithmetic interface.
    """
    result = {}
    for name in ('bit', 'complex'):
        data = finite_bridge[name]
        m, W, child = (integer(data[k]) for k in ('m', 'W', 'maxchild'))
        require(m > 1 and W > 0, 'positive arity and role volume required')
        degree, bits = halving_degree(m, child), W.bit_length()
        require(integer(data['halving_degree']) == degree, name + ' stale halving degree')
        require(integer(data['wire_bits']) == bits, name + ' stale role logarithm')
        result[name] = dict(m=m, W=W, maxchild=child,
                            halving_degree=degree, wire_bits=bits)
    phase = finite_bridge['complex']
    s, scalar = (integer(phase[k]) for k in ('s', 'scalar_group_upper'))
    m, W, child = (result['complex'][k] for k in ('m', 'W', 'maxchild'))
    require(0 < s < m*W and scalar > 0, 'invalid complex rank/scalar bound')
    E = 64*(W+m+scalar+1)**3
    B = s+E
    literal = 2*scalar*W**2+8*s+4*W+4+32*m
    C0 = 32*m*B**2
    semantic = dict(E=E, B=B, C0=C0, C1=1, literal_charge=literal,
                    strict_literal_gap=E-literal,
                    induction_gap=2*B*(m-child)-(s+E))
    require(E > literal and semantic['induction_gap'] >= 0 and C0 > 2*B+18,
            'semantic completed-child bound failed')
    for key, value in semantic.items():
        require(rational(finite_bridge['semantic'][key]) == value,
                'stale semantic constant: '+key)
    result['complex'].update(s=s, scalar_group_upper=scalar)
    result['semantic'] = semantic
    rows = finite_bridge['rows']
    coefficient = sum(result[name]['halving_degree']*result[name]['wire_bits']
                      for name in ('bit', 'complex'))
    degree = integer(rows['degree'])
    gap = degree-Q(51,25)*coefficient
    require(degree > 0 and gap > 0, 'insufficient product row degree')
    expected = dict(coefficient=coefficient, degree=degree,
                    degree_gap=gap, suffix_slope=4*degree)
    for key, value in expected.items():
        require(rational(rows[key]) == value, 'stale product row constant: '+key)
    result['rows'] = expected
    return result


def assembly(finite_bridge, a_bit, kappa, beta=Q(1,20), h=Q(1,10**12),
             a_complex=Q(717,10**7), *, original_prefix=False,
             old_guard=False, old_exposures=False):
    """Return 47 strict slacks and seven margins, or raise InvalidAssembly.

    The three keyword switches are negative controls: they impose the old
    prefix, nonlinear guard, or old separate movement charges at these SAME
    balanced parameters. They do not silently optimize an alternative family.
    """
    f = validate_bridge(finite_bridge)
    a, b, kappa, beta, h = map(rational, (a_bit,a_complex,kappa,beta,h))
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


def cutoffs(finite_bridge, result):
    """PR34 sufficient numeric comparisons, retaining its all-interval padding.

    These are eventual arithmetic thresholds, not practical running times or
    substitutes for additional native setup / prime / recovery thresholds.
    """
    f = validate_bridge(finite_bridge)
    p = result['parameters']
    e,c,r,beta = (p[k] for k in ('epsilon','c','alpha_squared_power','beta'))
    ka,km,kb,ks = (ceil(1/x) for x in (r,e*c,1-e,e*beta))
    C0 = f['semantic']['C0']
    largest = max(f['bit']['m'],f['complex']['m'])
    cuts = dict(guard=ceil(Q((2*C0).bit_length())/(1-e)),
        normalization=ceil(7/(1-e-r)), alpha=16*ka*ka+1, compact=64*km*km+1,
        geometry=ceil(3/(1-e*(1+c))),phase_cell=ceil(9/(e-(1-r)/2)),
        period=128*kb*kb+1,stopped_leaf=ks*(4*largest).bit_length(),log_p=25,reservoir=14)
    common = max(cuts.values())
    require(common >= max(2*ka,2*km,2*kb,25), 'cutoff does not cover monotone regime')
    checkpoints=[]
    for j in range(6):
        z=common*2**j
        powers=dict(alpha=(z//ka,8*(z+ka)+64),compact=(z//km,32*(z+km)+192),
            period=(z//kb,16*(z+kb)+56),
            rows=(z//kb,f['rows']['suffix_slope']*(z+kb+8)),
            leaf=(z//ks,4*largest))
        require(all(lhs >= rhs.bit_length() for lhs,rhs in powers.values()),
                'compressed-power threshold failed')
        checkpoints.append(dict(log2_input=z,powers={name:dict(exponent=lhs,rhs=rhs,
             rhs_bits=rhs.bit_length()) for name,(lhs,rhs) in powers.items()}))
    return dict(cutoff_log2_input=cuts,common_cutoff=common,power_checkpoints=checkpoints,
        all_interval_argument='For [Z,Z+k), bound RHS at Z+k and LHS at floor(Z/k). '
          'Successive intervals double LHS; the positive affine RHS grows at most '
          'linearly, so 2^j >= j+1 proves persistence.',
        additional_eventual_conditions=['BHP prime threshold and distinct-prime packing',
          'Fixed rational basis, eligible common prime and native table setup',
          'Catalogue/descriptor domination, logarithm absorption, exact recovery'],
        practical_runtime_claim=False)
