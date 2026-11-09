"""Exact source scale and common-grid admission, not a numerical Core service."""
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def power2(exponent):
    need(type(exponent) is int, 'integer dyadic exponent')
    return Q(1 << exponent) if exponent >= 0 else Q(1, 1 << -exponent)


def ceil_log2(value):
    value = Q(value)
    need(value > 0, 'positive logarithm input')
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    return exponent + int(power2(exponent) < value)


def scale_policy(normalizer_bits, caller_bits, gamma, policy):
    need(normalizer_bits and len(normalizer_bits) == len(caller_bits), 'matched nonempty groups')
    need(all(type(x) is int and x >= 0 for x in (*normalizer_bits, *caller_bits, gamma)),
         'nonnegative exact scale exponents')
    need(policy in ('spend_existing', 'add_new'), 'named scale policy')
    if policy == 'spend_existing':
        need(all(k >= u for k, u in zip(caller_bits, normalizer_bits)),
             'existing normalizer cannot be overspent')
        remaining = [k-u for k, u in zip(caller_bits, normalizer_bits)]
        restore = gamma
    else:
        remaining = list(caller_bits)
        restore = gamma + sum(normalizer_bits)
    return {'remaining_bits': remaining, 'restoration_bits': restore,
            'target_exponent': restore-sum(remaining)-sum(normalizer_bits),
            'declared_target_exponent': gamma-sum(caller_bits)}


def diagonal_gate(normalizer_bits, caller_bits, diagonal_bits, policy='spend_existing'):
    need(len(normalizer_bits) == len(diagonal_bits), 'one diagonal bound per group')
    need(all(type(v) is int and v >= 0 for v in diagonal_bits), 'dyadic diagonal norm bounds')
    scales = scale_policy(normalizer_bits, caller_bits, 0, policy)
    gains = [power2(v-r) for v, r in zip(diagonal_bits, scales['remaining_bits'])]
    need(all(c <= 1 for c in gains), 'remaining diagonal must contract arbitrary errors')
    return gains


def common_budget(groups, radius, tau, restoration_bits):
    """Groups contain authenticated bridge Axis objects with actual source J."""
    need(groups and all(group for group in groups), 'nonempty groups and axes')
    need(type(radius) is int and radius >= 1 and type(tau) is int and tau >= 1,
         'positive integer actual radius and target')
    need(type(restoration_bits) is int and restoration_bits >= 0, 'funded final restoration')
    r_bridge, r_wrapper = 2*radius, 3*radius
    height = ceil_log2(len(groups))
    z = tau+restoration_bits+height+1
    eta = power2(-z)
    row_costs = [sum((Q((2*a.bandwidth+1)*r_bridge+2)/Q(a.gap) for a in group), Q())
                 for group in groups]
    q = max(max(a.normalizer_bits for group in groups for a in group),
            z+ceil_log2(max(Q(8), 2*max(row_costs))))
    targets = [max(1, z+2-sum(a.normalizer_bits for a in group)) for group in groups]
    tails = [sum((a.tail for a in group), Q()) for group in groups]
    need(all(tail <= eta/(4*r_bridge) for tail in tails), 'complete source tails are underfunded')
    return {'grid_bits': q, 'core_targets': targets, 'bridge_radius': r_bridge,
            'wrapper_radius': r_wrapper, 'local_bridge_allowance': eta,
            'local_wrapper_allowance': eta, 'final_restoration_bits': restoration_bits,
            'normalized_total_allowance': 2*len(groups)*eta,
            'restored_total_allowance': power2(restoration_bits)*2*len(groups)*eta,
            'row_costs': row_costs, 'tails': tails, 'z': z}


def trunc_grid(value, q):
    value = Q(value)
    need(type(q) is int and q >= 0, 'nonnegative component grid')
    numerator = abs(value.numerator)*(1 << q)//value.denominator
    return Q(-numerator if value < 0 else numerator, 1 << q)


def hole_schedule(value, normalizer_bits, caller_bits, gamma, policy, q):
    """Exact identity-hole reference action and stated q-grid truncations only."""
    scale = scale_policy(normalizer_bits, caller_bits, gamma, policy)
    stages = []
    state = Q(value)
    for u, r in zip(normalizer_bits, scale['remaining_bits']):
        returned = trunc_grid(state*power2(-u), q)
        state = trunc_grid(returned*power2(-r), q)
        stages.append((returned, state))
    return state*power2(scale['restoration_bits']), stages
