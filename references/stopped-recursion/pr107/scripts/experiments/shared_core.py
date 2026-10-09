"""First/third-stage reuse for two-field bit cores with an orthogonal matching.

No automorphism of the central factor is needed: the matching acts on the
fixed invocation coordinates, while local auxiliary indices remain fixed.
"""
from fractions import Fraction as Q

from audit_joint_frames import eye, zero, product, sub
from certify import require
from experiments.rank_product_core import _compile, counts, tensor
from search_network import log_integer_bounds


def shared_counts(n, r, d, side_roles):
    out = counts(n, r, d, side_roles)
    removed = n*n*(side_roles+r)
    out.update(unshared_W=out['W'], removed_roles=removed,
               W=out['W']-removed, s=out['s']-removed*out['m'])
    out['relative_deficit'] = Q(out['deficit'], out['W']*out['m'])
    if out['positive']:
        lo, hi = log_integer_bounds(out['m']); eta = out['relative_deficit']
        out.update(saving_lower=eta/hi, saving_upper=eta/((1-eta)*lo))
    return out


def check_matching(core, permutation):
    n, d, P = core['n'], core['d'], core['projections']
    require(len(permutation) == n and all(type(i) is int for i in permutation)
            and sorted(permutation) == list(range(n)), 'Need an actual label permutation')
    Z = zero(d)
    require(all(product(P[i], P[j]) == Z and product(P[j], P[i]) == Z
                for i, j in enumerate(permutation)), 'Matching must mutually annihilate')


def compile_shared(core, permutation, maximum_roles=1000):
    """Expand a complete shared network; budget includes the unshared expansion.

    Widen the first J gate of each stage-three target from B tensor P_t to
    B tensor I. This preserves its monotone rank ledger and is needed before
    the auxiliary roles can be joined. Merely identifying the old roles is
    not a valid loss-preserving construction.
    """
    check_matching(core, permutation)
    candidate, _ = _compile(core, maximum_roles)
    n, r, d = core['n'], core['r'], core['d']
    N = n**3; bank = len(core['side_edges'])+r
    expected = shared_counts(n, r, d, len(core['side_edges']))
    invocation_gates = 4*n+4
    require(len(candidate['gates']) == 3*n*n*invocation_gates,
            'The underlying compiler schedule has changed')
    P = core['projections']
    remap = list(range(candidate['W']))
    for a in range(n):
        for b in range(n):
            first = 2*N+(a*n+b)*bank
            third_invocation = b*n+permutation[a]
            third = 2*N+(2*n*n+third_invocation)*bank
            remap[third:third+bank] = range(first, first+bank)
    for u in range(n):
        for v in range(n):
            first_gate = (2*n*n+u*n+v)*invocation_gates
            low = tensor([sub(eye(d*d), tensor([P[u], P[v]])), eye(d)])
            for gate in candidate['gates'][first_gate:first_gate+n]:
                gate['frame'] = low
    for gate in candidate['gates']:
        gate['roles'] = [remap[i] for i in gate['roles']]
        gate['xors'] = [[remap[t], remap[s]] for t, s in gate['xors']]
    W = expected['W']
    candidate.update(W=W, rho=candidate['rho'][:W],
                     source_frames=candidate['source_frames'][:W],
                     sink_frames=candidate['sink_frames'][:W])
    return candidate, expected


def target_budget(n, r, d, target):
    """Hypothetical loss-preserving side role budget, assuming valid matching."""
    require(isinstance(target, Q) and target > 0, 'Use an exact positive target')
    f = 1-Q(6*r*d, n); m = d**3
    require(f > 0, 'No positive numerator')
    lo, hi = log_integer_bounds(m)
    sufficient = Q(n, 2)*(f/(m*target*hi)-2)-r
    t = target*lo
    necessary = Q(n, 2)*(f*(1+t)/(m*t)-2)-r
    return dict(target_bit_saving=target, sufficient_side_roles=sufficient,
                necessary_side_roles=necessary, sufficient_ratio=sufficient/n,
                necessary_ratio=necessary/n,
                loss_preserving_side_construction_required=True)
