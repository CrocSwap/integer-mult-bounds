#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent positive-binomial and 1024-bit endpoint-to-kappa audit of the selected PR #942 (T37) record.

Prepared for steph4n-gh with substantial Google Gemini assistance (Track 75-84, Seed 78).
Uses only the Python 3 standard library. No production logarithm, exponential,
moment, outer-assembly, supplier, or owner module is imported or executed.
"""
import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = 1 << 240
TAIL_LIMIT = 1 << 70  # At most 2^-170 per power factor.

WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
CAPACITIES = {8: (672, 2), 16: (448, 4), 32: (448, 8), 48: (448, -13)}
INVENTORY = {4: 80, 5: 32, 7: 54, 8: 122, 9: 216}
U8_LOCAL_PROFILE = {1: 2548, 2: 338, 3: 446, 4: 162, 5: 72, 8: 8}
T21_IDLE = {48: 6292, 3: 1, 1: 3}
T16_IDLE = {48: 4793, 44: 1, 2: 1, 1: 2}
EDITED_HELPER_WIDTHS = {5: 4, 186: 4, 193: 4, 266: 9, 414: 4}
INITIAL_AFFECTED_REMAINDERS = {
    (29, 8, 0): 44,
    (28, 8, 79): 0,
    (20, 14, 111): 3,
    (27, 15, 0): 2,
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(n, d):
    return -(-n // d)


def ceil_q(x):
    return -(-x.numerator // x.denominator)


def dec70(x):
    with localcontext() as ctx:
        ctx.prec = 70
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def git_blob_sha1(data):
    header = b'blob ' + str(len(data)).encode('ascii') + b'\0'
    return hashlib.sha1(header + data).hexdigest()


def intervals_overlap(a_lo, a_hi, b_lo, b_hi):
    return max(a_lo, b_lo) <= min(a_hi, b_hi)


def power_interval(r, m, a):
    """Enclose (m/r)^a for 0 <= a <= 1 via positive generalized-binomial series.

    Put x = 1 - r/m in [0, 1). Then
      (m/r)^a = (1 - x)^(-a) = sum_{k>=0} t_k,
    where t_0 = 1 and t_{k+1} = t_k * ((a + k) / (k + 1)) * x.
    Since 0 <= a <= 1, (a + k)/(k + 1) <= 1, so t_{k+m} <= t_{k+1} * x^{m-1}
    for all m >= 1, bounding the infinite tail after t_k by t_{k+1} / (1 - x)
    = t_{k+1} * (m / r). Every recurrence step rounds outward on denominator D.
    """
    require(type(r) is int and type(m) is int and 0 < r <= m, 'Invalid rank or arity')
    require(isinstance(a, Q) and 0 <= a <= 1, 'Saving must be a rational in [0,1]')
    if a == 0 or r == m:
        return Q(1), Q(1), 0
    p, q = a.numerator, a.denominator
    tl = tu = sl = su = D
    for k in range(20000):
        numerator = (p + k * q) * (m - r)
        denominator = q * (k + 1) * m
        nl = tl * numerator // denominator
        nu = ceil_div(tu * numerator, denominator)
        tail = ceil_div(nu * m, r)
        if tail <= TAIL_LIMIT:
            return Q(sl, D), Q(su + tail, D), k + 1
        tl, tu = nl, nu
        sl, su = sl + tl, su + tu
    raise ValueError('Series did not reach the prescribed tail bound')


def moment(profile, m, live, a, surcharge=False):
    require(type(live) is int and live > 0, 'Invalid live stock')
    require(type(m) is int and m > 1 and bool(profile), 'Invalid arity or empty profile')
    lower = upper = Q(0)
    terms = {}
    for r, count in sorted(profile.items()):
        require(type(r) is int and type(count) is int and 0 < r < m and count > 0,
                'Invalid child rank or multiplicity')
        l, u, steps = power_interval(r, m, a)
        weight = Q(r * count, m * live)
        lower += weight * l
        upper += weight * u
        terms[str(r)] = steps
    if surcharge:
        l, u, steps = power_interval(1, m, a)
        weight = Q(32 * m * sum(profile.values()), 10**16 * live)
        lower += weight * l
        upper += weight * u
        terms['fallback'] = steps
    return lower, upper, terms


def bracket_and_compare(profile, m, live, endpoint, surcharge, recorded_rows):
    step = Q(1, 10**24)
    lower = moment(profile, m, live, endpoint, surcharge)
    upper = moment(profile, m, live, endpoint + step, surcharge)
    require(lower[1] < 1, 'Claimed lower endpoint does not have a strict acceptance certificate')
    require(upper[0] > 1, 'Claimed successor does not have a strict rejection certificate')
    require(len(recorded_rows) == 2, 'Expected two recorded moment rows')
    for row, (lo, hi, _), expected_z, expected_accept in (
        (recorded_rows[0], lower, endpoint, True),
        (recorded_rows[1], upper, endpoint + step, False),
    ):
        require(Q(row['endpoint']) == expected_z and row['accept'] is expected_accept
                and row['surcharge'] is surcharge, 'Recorded moment row metadata mismatch')
        res_lo, res_hi = lo - 1, hi - 1
        for engine_key in ('mercator', 'base_two'):
            rec_lo, rec_hi = map(Q, row[engine_key])
            require(intervals_overlap(res_lo, res_hi, rec_lo, rec_hi),
                    'Binomial interval disagrees with recorded ' + engine_key)
    return {
        'endpoint': str(endpoint),
        'successor': str(endpoint + step),
        'lower_residual_interval': [str(lower[0] - 1), str(lower[1] - 1)],
        'successor_residual_interval': [str(upper[0] - 1), str(upper[1] - 1)],
        'terms': lower[2],
        'overlaps_recorded_mercator_and_base_two': True,
    }


def verify_edits_and_accounting(claim, assembly, edits_doc):
    replicas, m = 37, 73
    calls, roles, live = 9 * replicas, 9 * replicas * 504, 8 * 112 * replicas
    physical = live + 504 + 8 + 2
    for key, expected in (
        ('replicas', replicas),
        ('calls', calls),
        ('roles', roles),
        ('live', live),
        ('physical', physical),
        ('rank_mass', 2408256),
        ('deficit', 11840),
        ('prefix_bits', 779),
        ('charged_prefix_bits', 1024),
        ('physical_row_coefficient', 17495),
    ):
        require(type(claim[key]) is int and claim[key] == expected,
                'Construction claim accounting changed: ' + key)
    require(assembly['provider_counts'] == {'gauge44': calls}, 'Assembly call count mismatch')

    # Verify the 8-role remainder trade in EDITS.json converts {44:1, 3:1, 2:1} -> {48:1, 1:1}.
    require(edits_doc['delay'] == 0 and len(edits_doc['edits']) == 8, 'Expected 8 delay-0 edits')
    seen_roles = set()
    delta_used = Counter()
    for entry in edits_doc['edits']:
        role = tuple(entry['role'])
        require(len(role) == 3 and role not in seen_roles, 'Duplicate or malformed edit role')
        seen_roles.add(role)
        helper = role[2]
        require(helper in EDITED_HELPER_WIDTHS, 'Unexpected edited helper index')
        w = EDITED_HELPER_WIDTHS[helper]
        b_bin = (entry['before']['owner_replica'], entry['before']['child'], entry['before']['port'])
        a_bin = (entry['after']['owner_replica'], entry['after']['child'], entry['after']['port'])
        require(b_bin in INITIAL_AFFECTED_REMAINDERS and a_bin in INITIAL_AFFECTED_REMAINDERS,
                'Edit touches unexpected owner bin')
        delta_used[b_bin] -= w
        delta_used[a_bin] += w
    before_rem = Counter(r for r in INITIAL_AFFECTED_REMAINDERS.values() if r > 0)
    after_rem = Counter()
    for bin_key, init_r in INITIAL_AFFECTED_REMAINDERS.items():
        final_r = init_r - delta_used[bin_key]
        require(0 <= final_r <= 48, 'Invalid post-edit remainder')
        if final_r > 0:
            after_rem[final_r] += 1
    require(dict(before_rem) == {44: 1, 3: 1, 2: 1} and dict(after_rem) == {48: 1, 1: 1},
            'Remainder trade does not realize 44+3+2 -> 48+1')

    untraded_idle = Counter(T21_IDLE) + Counter(T16_IDLE)
    require(dict(untraded_idle) == {48: 11085, 44: 1, 3: 1, 2: 1, 1: 5},
            'Untraded T21+T16 idle sum mismatch')
    traded_idle = Counter(untraded_idle)
    traded_idle.subtract(before_rem)
    traded_idle.update(after_rem)
    traded_idle = +traded_idle
    idle = {48: 11086, 1: 6}
    require(dict(traded_idle) == idle and {int(r): c for r, c in claim['idle'].items()} == idle,
            'Traded idle profile mismatch')

    derived = Counter({r: c * calls for r, c in U8_LOCAL_PROFILE.items()})
    derived.update(idle)
    profile = {int(r): c for r, c in assembly['complex_profile'].items()}
    require(dict(derived) == profile and {int(r): c for r, c in claim['profile'].items()} == profile,
            'Local + idle profile does not match committed assembly')
    require(sum(profile.values()) == 1201234, 'Complex child count mismatch')
    require(sum(r * c for r, c in profile.items()) == 2408256, 'Complex rank mass mismatch')
    require(m * live - 2408256 == 11840 == replicas * 320, 'Complex deficit mismatch')

    # Finite reserve, symplectic group stock, C0 precision, and row-coefficient checks.
    local_prefix_bits = 72
    prefix_bits = local_prefix_bits + replicas + calls + calls + 4
    require(prefix_bits == 779 < 1024 and prefix_bits >= 512,
            'Global prefix bit reserve check failed')
    group = 1 << (36 * 36)
    for j in range(1, 37):
        group *= (1 << (2 * j)) - 1
    stock = group * physical
    streamed_mass = group * 2408256
    total_mass = streamed_mass + (1 << 100000)
    stock_bits = stock.bit_length()
    c0_bits = (32 * 73 * total_mass * total_mass).bit_length()
    row_coeff = 2 * stock_bits + 9909 + 252 + 2 * 1024
    require(stock_bits == 2643 and c0_bits == 200012 < 210000 and total_mass < (1 << 100001),
            'Symplectic stock or C0 bit bound mismatch')
    require(row_coeff == 17495 < 20161, 'Physical row coefficient mismatch')
    # Admissible integer payload reserve window P: 779 < P and 15447 + 2*P < 20161 => 780 <= P <= 2356.
    for payload, expected_ok in ((512, False), (779, False), (780, True),
                                 (1024, True), (2356, True), (2357, False)):
        ok = (prefix_bits < payload) and (2 * stock_bits + 9909 + 252 + 2 * payload < 20161)
        require(ok is expected_ok, 'Payload reserve boundary check failed at ' + str(payload))
    return profile, {
        'replicas': replicas,
        'calls': calls,
        'roles': roles,
        'live_stock': live,
        'physical_stock': physical,
        'child_count': 1201234,
        'rank_mass': 2408256,
        'deficit': 11840,
        'local_prefix_bits': local_prefix_bits,
        'global_prefix_bits': prefix_bits,
        'charged_prefix_bits': 1024,
        'historical_512_prefix_rejected': prefix_bits >= 512,
        'admissible_payload_interval': [780, 2356],
        'physical_stock_bits': stock_bits,
        'required_C0_bits': c0_bits,
        'C0_exponent_cap': 210000,
        'physical_row_coefficient': row_coeff,
        'retained_row_coefficient_cap': 20161,
        'remainder_trade': {
            'edits_count': 8,
            'before_remainders': {'2': 1, '3': 1, '44': 1},
            'after_remainders': {'1': 1, '48': 1},
            'untraded_idle': {str(k): v for k, v in sorted(untraded_idle.items())},
            'traded_idle': {str(k): v for k, v in sorted(idle.items())},
        },
    }


def verify_all_t_binomial_and_bridge(profile, b_lower, repository=None):
    """Certify the 42 strict rank inequalities of the all-T supporting lemma via positive binomial series."""
    upper, count = {}, 0
    for cap, (_, bonus) in CAPACITIES.items():
        for vec in itertools.product(*(range(cap // w + 1) for w in WIDTHS)):
            used = sum(w * n for w, n in zip(WIDTHS, vec))
            if used <= cap:
                count += 1
                r = cap - used
                val = bonus + sum(p * n for p, n in zip(PRICES, vec))
                upper[r] = max(upper.get(r, -10**6), val)
    dp = {}
    for cap, (_, bonus) in CAPACITIES.items():
        scores = [None] * (cap + 1)
        scores[0] = 0
        for fill in range(cap + 1):
            if scores[fill] is None:
                continue
            for width, price in zip(WIDTHS, PRICES):
                nxt = fill + width
                if nxt <= cap and (scores[nxt] is None or scores[fill] + price > scores[nxt]):
                    scores[nxt] = scores[fill] + price
        for fill, val in enumerate(scores):
            if val is not None:
                dp[cap - fill] = max(dp.get(cap - fill, -10**6), val + bonus)
    require(upper == dp and count == 1163 and len(upper) == 45,
            'Independent Cartesian and DP dual tables disagree')

    mass_per_rep = sum(c * n for c, (n, _) in CAPACITIES.items()) - 9 * sum(
        r * n for r, n in INVENTORY.items()
    )
    signed_per_rep = sum(n * p for n, p in CAPACITIES.values()) + 9 * sum(
        INVENTORY[r] * p for r, p in zip(WIDTHS, PRICES)
    )
    credit_per_rep = 48 * signed_per_rep + 13 * mass_per_rep
    require((mass_per_rep, signed_per_rep, credit_per_rep, upper[0], upper[48])
            == (14382, -3892, 150, 0, -13), 'All-T per-replica constants mismatch')

    z_upper = b_lower + Q(1, 10**24)
    phi = {}
    for r in sorted(upper):
        if r > 0:
            l, u, steps = power_interval(r, 73, z_upper)
            phi[r] = (r * l, r * u, steps)
    cost = {
        r: (48 * phi[r][0] - r * phi[48][1], 48 * phi[r][1] - r * phi[48][0])
        for r in phi if r < 48
    }
    credit = {r: 48 * upper[r] + 13 * r for r in cost}
    require(credit[1] == 925 and all(lo > 0 for lo, _ in cost.values()),
            'Positive non-48 cost or rank-1 credit failed')
    lam_lo, lam_hi = cost[1][0] / 925, cost[1][1] / 925

    margins = {}
    for r in sorted(cost):
        if r == 1:
            continue
        v = credit[r]
        lo, hi = cost[r]
        rhs_hi = v * lam_hi if v >= 0 else v * lam_lo
        rhs_lo = v * lam_lo if v >= 0 else v * lam_hi
        m_lo, m_hi = lo - rhs_hi, hi - rhs_lo
        require(m_lo > 0, 'Supporting rank inequality failed at r=' + str(r))
        margins[r] = (m_lo, m_hi)
    require(len(margins) == 42, 'Expected 42 strict rank inequalities')
    min_rank = min(margins, key=lambda r: margins[r][0])

    # Exact symbolic and numerical bridge connecting T21, T16, T37, and the 44+3+2 -> 48+1 trade:
    # 1. Both T21 ({48:6292, 3:1, 1:3}) and T16 ({48:4793, 44:1, 2:1, 1:2}) are signed-dual tight:
    require(sum(r * n for r, n in T21_IDLE.items()) == 21 * mass_per_rep
            and sum((48 * upper[r] + 13 * r) * n for r, n in T21_IDLE.items() if r < 48) == 21 * credit_per_rep,
            'T21 signed-dual tightness failed')
    require(sum(r * n for r, n in T16_IDLE.items()) == 16 * mass_per_rep
            and sum((48 * upper[r] + 13 * r) * n for r, n in T16_IDLE.items() if r < 48) == 16 * credit_per_rep,
            'T16 signed-dual tightness failed')
    require(credit[44] + credit[3] + credit[2] == -100 + 375 + 650 == 925 == credit[1],
            'Remainder-trade dual credit conservation failed')

    # 2. Verify exact symbolic coefficient identities in the Phi(r, z) basis:
    #    M_21(z) - M_37(z) == margin(3, z) / (48 * 73 * 18816)
    #    M_16(z) - M_37(z) == (margin(44, z) + margin(2, z)) / (48 * 73 * 14336)
    #    M_untraded(z) - M_37(z) == (margin(44, z) + margin(3, z) + margin(2, z)) / (48 * 73 * 33152)
    idle37_norm = {48: Q(11086, 37), 1: Q(6, 37)}
    idle21_norm = {r: Q(n, 21) for r, n in T21_IDLE.items()}
    idle16_norm = {r: Q(n, 16) for r, n in T16_IDLE.items()}
    require(idle21_norm[3] == Q(1, 21)
            and idle21_norm[1] - idle37_norm[1] == -Q(credit[3], 925 * 21)
            and idle21_norm[48] - idle37_norm[48] == -Q(3 - Q(credit[3], 925), 48 * 21),
            'Symbolic T21 minus T37 margin identity failed')
    require(idle16_norm[44] == Q(1, 16) and idle16_norm[2] == Q(1, 16)
            and idle16_norm[1] - idle37_norm[1] == -Q(credit[44] + credit[2], 925 * 16)
            and idle16_norm[48] - idle37_norm[48] == -Q(44 + 2 - Q(credit[44] + credit[2], 925), 48 * 16),
            'Symbolic T16 minus T37 margin identity failed')

    # 3. Numerical interval verification at z_upper:
    untraded_profile = dict(profile)
    untraded_profile[48] -= 1
    untraded_profile[1] -= 1
    untraded_profile[44] = 1
    untraded_profile[3] += 1
    untraded_profile[2] += 1
    m37_up = moment(profile, 73, 33152, z_upper, False)
    mun_up = moment(untraded_profile, 73, 33152, z_upper, False)
    diff_direct = (mun_up[0] - m37_up[1], mun_up[1] - m37_up[0])
    denom37 = 48 * 73 * 33152
    diff_margin = (
        (margins[44][0] + margins[3][0] + margins[2][0]) / denom37,
        (margins[44][1] + margins[3][1] + margins[2][1]) / denom37,
    )
    require(intervals_overlap(diff_direct[0], diff_direct[1], diff_margin[0], diff_margin[1])
            and diff_margin[0] > Q(1, 10**8),
            'Remainder-trade moment reduction disagrees with supporting-margin sum')

    if repository is not None:
        all_t_doc = json.loads(
            (repository.resolve() / 'research/community-frontier942-audit/ALL-T-BOUND.json').read_text()
        )
        require(all_t_doc['dual_bin_vectors'] == 1163, 'ALL-T-BOUND vector count mismatch')
        require({int(k): v for k, v in all_t_doc['upper'].items()} == upper,
                'ALL-T-BOUND upper table mismatch')
        for engine_key in ('mercator', 'atanh'):
            rec = all_t_doc['supporting_inequalities'][engine_key]
            require({int(k): v for k, v in rec['credit'].items()} == credit,
                    'ALL-T-BOUND credit mismatch for ' + engine_key)
            rec_lam_lo, rec_lam_hi = map(Q, rec['multiplier_interval'])
            require(intervals_overlap(lam_lo, lam_hi, rec_lam_lo, rec_lam_hi),
                    'Binomial multiplier interval disagrees with ' + engine_key)
            tol = Q(1, 10**47) if engine_key == 'mercator' else Q(1, 10**29)
            for r, (m_lo, m_hi) in margins.items():
                rec_m_lo = Q(rec['strict_margin_by_rank'][str(r)])
                require(abs(m_lo - rec_m_lo) < tol and abs(m_hi - rec_m_lo) < tol,
                        'Binomial rank margin disagrees with ' + engine_key + ' at r=' + str(r))

    return {
        'dual_bin_vectors': count,
        'realized_remainders': len(upper),
        'mass_per_replica': mass_per_rep,
        'signed_price_per_replica': signed_per_rep,
        'credit_per_replica': credit_per_rep,
        'equality_ratio': '6/37',
        'certified_exponent': str(z_upper),
        'strict_rank_inequalities_certified': len(margins),
        'multiplier_interval': [str(lam_lo), str(lam_hi)],
        'minimum_strict_margin_rank': min_rank,
        'minimum_strict_margin_interval': [str(margins[min_rank][0]), str(margins[min_rank][1])],
        'remainder_trade_bridge': {
            't21_dual_tight': True,
            't16_dual_tight': True,
            'traded_ranks': [2, 3, 44],
            'traded_rank_credits': {'2': credit[2], '3': credit[3], '44': credit[44], 'sum': 925},
            'trade_moment_reduction_interval': [str(diff_margin[0]), str(diff_margin[1])],
            'trade_moment_reduction_decimal': dec70(diff_margin[0]),
        },
    }


def outer47(bit_saving, complex_saving, degree_gap, kappa, eta=Q(1, 10**24), beta=Q(1, 10**24)):
    """Independent implementation of the 47 strict outer assembly inequalities."""
    require(0 < eta < Q(1, 8) and 0 < beta < 1, 'Invalid outer backoff parameters')
    a, b = bit_saving, complex_saving
    tau, sigma = 1 - a, 1 - b
    q = a * (1 - 2 * eta)
    lp = 1 - q
    lam = (tau + lp) / 2
    c = q + eta / 4
    eps = (1 - eta) / (1 + q)
    minimum = eps * q
    r = (minimum + 1 - eps) / 2
    delta = eta / 8
    internal = tau + (1 - beta) * max(sigma - tau, Q(0))
    leaf = sigma + beta * (1 - sigma)
    margins = {
        'balanced_prefix': 1 - eps,
        'coordinate_movement': a,
        'compact_phase_layer': minimum,
        'bulk_exposure': a,
        'Gaussian_arithmetic': min(1 - eps - delta, r - delta),
        'scalar_work': 1 - eps - delta,
        'dimension': eps,
    }
    slacks = {
        'bit_positive': a,
        'complex_above_bit': b - a,
        'complex_below_one_over32': Q(1, 32) - b,
        'beta_positive': beta,
        'beta_below_one': 1 - beta,
        'leaf_saving_above_bit': (1 - beta) * b - a,
        'q_positive': q,
        'q_below_internal': 1 - internal - q,
        'q_below_leaf': 1 - leaf - q,
        'c_positive': c,
        'c_below_one': 1 - c,
        'q_below_reservations': c - q,
        'lambda_above_tau': lam - tau,
        'lambda_above_sigma': lam - sigma,
        'lambda_above_internal': lam - internal,
        'lambda_prime_above_lambda': lp - lam,
        'compact_leaf': lp - leaf,
        'compact_reservations': lp - (1 - c),
        'lambda_prime_below_one': q,
        'epsilon_positive': eps,
        'epsilon_below_one': 1 - eps,
        'guard_width': 1 - eps,
        'K_geometry': 1 - eps * (1 + c),
        'K_dominates_log': eps * c,
        'record_suffix': 1 - eps,
        'phase_local': 1 - eps - delta,
        'phase_boundary': r - delta,
        'gamma_sublinear': 1 - eps - r,
        'cell_above_band': eps - (1 - r) / 2,
        'prime_interval_packing': 1 - eps,
        'alpha_positive': r,
        'alpha_below_one': 1 - r,
        'alpha_below_one_fourth': Q(1, 4) - r,
        'delta_positive': delta,
        'delta_below_one_eighth': Q(1, 8) - delta,
        'short_record_fallback': eps - a,
        'small_field_exposure': 1 - eps - minimum,
        'artificial_boundary': 8 - eps + r - delta - minimum,
        'literal_scalar_guard': Q(1),
        'row_product_gap': degree_gap,
    }
    slacks.update({name + '_above_kappa': val - kappa for name, val in margins.items()})
    require(len(slacks) == 47 and all(v > 0 for v in slacks.values()), 'Outer strict constraint failed')
    require(min(margins.values()) == minimum, 'Compact phase layer is not the minimum margin')
    require(margins['balanced_prefix'] - minimum == eta and 1 - eps - r == eta / 2,
            'Balanced prefix identity failed')
    require(1 - eps * (1 + c) == eta - eps * eta / 4, 'K_geometry identity failed')
    return slacks, minimum


def reduce_endpoint_to_kappa(c_bit, b_complex, recorded_cuts, recorded_outer, recorded_controls):
    eta = beta = Q(1, 10**24)
    s = min(c_bit, (1 - beta) * b_complex) - Q(1, 10**27)
    require(0 < s < c_bit and s < (1 - beta) * b_complex, 'Invalid bootstrap step saving s')
    chain = [Q(384599, 10**10)]
    cuts = []
    min_1024_dominance_margin = None
    for idx in range(7):
        old = chain[-1]
        a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
        require(old < a < s < 1 - a and gap > 0, 'Bootstrap chain monotonicity failed')
        quad_cut = ceil_q(Q(36) / (gap * gap))
        lin_1024 = ceil_q(Q(2 * (4 + 1024)) / gap)
        lin_512 = ceil_q(Q(2 * (4 + 512)) / gap)
        cut = max(quad_cut, lin_1024)
        require(cut == quad_cut and quad_cut > lin_1024 > lin_512,
                'Quadratic cutoff did not strictly dominate 1024-bit linear cutoff')
        dom_margin = quad_cut - lin_1024
        if min_1024_dominance_margin is None or dom_margin < min_1024_dominance_margin:
            min_1024_dominance_margin = dom_margin
        step_dict = {'exponent': str(a), 'gap': str(gap), 'cutoff_log2': str(cut)}
        require(step_dict == recorded_cuts[idx], 'Bootstrap step mismatch at index ' + str(idx))
        cuts.append(step_dict)
        chain.append(a)

    q = chain[-1] * (1 - 2 * eta)
    margin = (1 - eta) * q / (1 + q)
    ticks = margin * 10**18
    k = Q((ticks.numerator - 1) // ticks.denominator, 10**18)
    degree_gap = Q(10**6) - Q(51 * 20161, 25)
    require(degree_gap == Q(23971789, 25), 'Degree gap formula mismatch')
    slacks, minimum = outer47(chain[-1], b_complex, degree_gap, k, eta=eta, beta=beta)
    require({name: str(val) for name, val in slacks.items()} == recorded_outer,
            'Outer 47 strict slack dictionary mismatch')

    rejected = []
    for name, kk, ee, be in (
        ('next_grid', k + Q(1, 10**18), eta, beta),
        ('zero_eta', k, Q(0), beta),
        ('zero_beta', k, eta, Q(0)),
        ('unit_beta', k, eta, Q(1)),
    ):
        try:
            outer47(chain[-1], b_complex, degree_gap, kk, eta=ee, beta=be)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('Outer control unexpectedly passed: ' + name)
    require(rejected == recorded_controls, 'Outer control list mismatch')
    return k, minimum, min_1024_dominance_margin, rejected


def run_controls(complex_profile, bit_profile, b_native, b_cons, c_bit):
    alg_count = 0
    for m in (2, 3, 5, 7, 64, 73):
        for r in range(1, m + 1):
            for a in (Q(0), Q(1, 3), Q(1, 2), Q(2, 3), Q(1)):
                l, u, _ = power_interval(r, m, a)
                exact = Q(m, r) ** a.numerator
                require(l ** a.denominator <= exact <= u ** a.denominator,
                        'Algebraic enclosure failed')
                alg_count += 1

    # 8 mathematical model controls:
    # 1. Zero-saving mass identities (complex and bit)
    require(moment(complex_profile, 73, 33152, Q(0))[:2]
            == (Q(2408256, 73 * 33152), Q(2408256, 73 * 33152))
            and moment(bit_profile, 64, 28416, Q(0))[:2]
            == (Q(1808352, 64 * 28416), Q(1808352, 64 * 28416)),
            'Zero-saving mass identity failed')
    # 2. Omitted rank-48 complex child wrongly admits b_native + 10^-24
    omitted = dict(complex_profile)
    omitted[48] -= 1
    require(moment(omitted, 73, 33152, b_native + Q(1, 10**24))[1] < 1,
            'Omitted child control failed')
    # 3. Dropped conservative complex surcharge wrongly admits b_cons + 10^-24
    require(moment(complex_profile, 73, 33152, b_cons + Q(1, 10**24), False)[1] < 1,
            'Dropped conservative complex surcharge control failed')
    # 4. Dropped bit surcharge wrongly admits c_bit + 10^-24 (and native complex rejected with old surcharge)
    require(moment(bit_profile, 64, 28416, c_bit + Q(1, 10**24), False)[1] < 1
            and moment(complex_profile, 73, 33152, b_native, True)[0] > 1,
            'Cross-model surcharge control failed')
    # 5. Physical-stock vs live-stock normalization wrongly admits b_native + 10^-24
    require(moment(complex_profile, 73, 33666, b_native + Q(1, 10**24))[1] < 1,
            'Physical-stock normalization control failed')
    # 6. Mass-and-count-preserving concavity redistribution: 2*48 -> 47 + 49 strictly lowers moment
    redistributed = dict(complex_profile)
    redistributed[48] -= 2
    redistributed[47] = redistributed[49] = 1
    require(sum(redistributed.values()) == sum(complex_profile.values())
            and sum(r * n for r, n in redistributed.items()) == 2408256,
            'Redistribution mass/count changed')
    orig_m = moment(complex_profile, 73, 33152, b_native)
    red_m = moment(redistributed, 73, 33152, b_native)
    require(red_m[1] < orig_m[0], 'Mass-preserving concavity redistribution not distinguished')
    # 7. Untraded T21+T16 remainder {48:11085, 44:1, 3:1, 2:1, 1:5} has identical rank mass 2408256
    #    and signed-dual credit 5550, but is strictly rejected at the accepted T37 endpoint b_native!
    untraded = dict(complex_profile)
    untraded[48] -= 1
    untraded[1] -= 1
    untraded[44] = 1
    untraded[3] += 1
    untraded[2] += 1
    require(sum(r * n for r, n in untraded.items()) == 2408256, 'Untraded control mass changed')
    untraded_m = moment(untraded, 73, 33152, b_native)
    require(untraded_m[0] > 1, 'Untraded T21+T16 remainder control failed to reject at b_native')
    # 8. Supporting-lemma perturbation control: inflating u(2) from 13 to 19 violates c(2) > lambda * v(2)
    z_up = b_native + Q(1, 10**24)
    l1, u1, _ = power_interval(1, 73, z_up)
    l2, u2, _ = power_interval(2, 73, z_up)
    l48, u48, _ = power_interval(48, 73, z_up)
    c1_lo = 48 * l1 - u48
    c2_hi = 48 * 2 * u2 - 2 * 48 * l48
    perturbed_v2 = 48 * 19 + 13 * 2
    require(c2_hi - perturbed_v2 * (c1_lo / 925) < 0,
            'Perturbed dual supporting-lemma control failed')

    rejection_count = 0
    for bad_args in (
        (0, 73, Q(1, 2)),
        (74, 73, Q(1, 2)),
        (1, 0, Q(1, 2)),
        (1, 73, Q(-1, 2)),
        (1, 73, Q(3, 2)),
        (True, 73, Q(1, 2)),
        (1, True, Q(1, 2)),
        (1, 73, 0.5),
    ):
        try:
            power_interval(*bad_args)
        except ValueError:
            rejection_count += 1
        else:
            raise ValueError('Invalid power_interval input accepted')
    for bad_profile in ({1: 0}, {73: 1}, {1: True}, {1: -1}, {}, {0: 5}):
        try:
            moment(bad_profile, 73, 33152, b_native)
        except ValueError:
            rejection_count += 1
        else:
            raise ValueError('Invalid profile accepted')

    return {
        'algebraic_comparisons': alg_count,
        'mathematical_controls': 8,
        'rejected_inputs': rejection_count,
        'redistributed_minus_original_interval': [
            str(red_m[0] - orig_m[1]),
            str(red_m[1] - orig_m[0]),
        ],
        'untraded_residual_at_native_endpoint_interval': [
            str(untraded_m[0] - 1),
            str(untraded_m[1] - 1),
        ],
    }


def repository_bindings(root, pins):
    """Compare all pinned and reference source bytes without importing supplier code."""
    root = root.resolve()
    sources = {remote: pins['files'][local] for local, remote in pins['provenance'].items()}
    sources.update(pins['references'])
    for relative, expected in sorted(sources.items()):
        path = (root / relative).resolve()
        require(path.is_relative_to(root) and path.is_file(),
                'Missing repository source: ' + relative)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected,
                'Repository source changed: ' + relative)
    return len(sources)


def audit(repository=None):
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    required_inputs = {
        'inputs/ASSEMBLY.json',
        'inputs/CLAIM.json',
        'inputs/EDITS.json',
        'inputs/PR589-EXPECTED.json',
        'inputs/selected-result.json',
    }
    require(set(pins['files']) == set(pins['provenance']) == required_inputs,
            'Incomplete pinned source inventory')
    for name, expected in sorted(pins['files'].items()):
        raw = (HERE / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected, 'Pinned input changed: ' + name)
    bit_bytes = (HERE / 'inputs/PR589-EXPECTED.json').read_bytes()
    require(git_blob_sha1(bit_bytes) == pins['git_blob_sha1']['inputs/PR589-EXPECTED.json'],
            'Pinned bit supplier git blob SHA1 mismatch')

    if repository is not None:
        checked = repository_bindings(repository, pins)
        print('PASS_T37_REPOSITORY_BINDINGS files=' + str(checked))

    assembly = json.loads((HERE / 'inputs/ASSEMBLY.json').read_text())
    selected = json.loads((HERE / 'inputs/selected-result.json').read_text())
    claim = json.loads((HERE / 'inputs/CLAIM.json').read_text())
    edits_doc = json.loads((HERE / 'inputs/EDITS.json').read_text())
    bit_doc = json.loads(bit_bytes)

    require(selected['source_prs'][0] == pins['audited_pr'] == 942
            and selected['audited_source_head'] == pins['audited_source_head'],
            'Selected PR or source head changed')
    require(pins['files']['inputs/ASSEMBLY.json'] == selected['certificate_sha256'],
            'Selected certificate binding changed')
    for supp_path in ('research/complex-t37-owners/PROOF.md',
                      'research/complex-t37-owners/ALL-T-PROOF.md'):
        require(pins['references'][supp_path] == selected['proof_supplements'][supp_path],
                'Selected proof supplement binding changed: ' + supp_path)
    require(Q(selected['kappa']) == Q(assembly['kappa']) == Q(claim['kappa']),
            'Selection, claim, and assembly kappa disagree')
    require(Q(claim['complex_lower']) == Q(assembly['complex_lower'])
            and Q(claim['bit_lower']) == Q(assembly['bit_lower']),
            'Claim and assembly supplier endpoints disagree')
    require(assembly['input_sha256']['package:inputs/PR589-EXPECTED.json']
            == pins['files']['inputs/PR589-EXPECTED.json'],
            'Assembly bit supplier SHA256 binding changed')
    for engine in ('moment.py', 'base_two_moment.py', 'outer.py'):
        ref_key = 'research/complex-k492-owner-repair/vendor/multicold/engines/' + engine
        require(pins['references'][ref_key] == assembly['input_sha256']['engines/' + engine],
                'Assembly arithmetic engine binding changed: ' + engine)

    complex_profile, accounting = verify_edits_and_accounting(claim, assembly, edits_doc)

    # Verify PR589 bit supplier parameters, derived deficit, and profile.
    word = bit_doc['word']
    bit_nine = bit_doc['nine']
    v_port, cst, copy_ranks = word['v'], word['decoder_constant'], word['copy_ranks']
    require(v_port == 111 and cst == 63 and len(copy_ranks) == 9 and sum(copy_ranks) == cst,
            'Bit supplier word parameters changed')
    bit_live = bit_nine['bit']['live']
    bit_deficit = 32 * (2 * 4 * v_port - 9 * cst)
    bit_profile = {int(r): c for r, c in bit_nine['profile'].items()}
    bit_mass = sum(r * c for r, c in bit_profile.items())
    require(bit_live == 28416 and bit_deficit == 10272 and bit_mass == 1808352
            and 64 * bit_live - bit_mass == bit_deficit
            and sum(bit_profile.values()) == 904896,
            'Bit supplier profile or derived deficit mismatch')

    b_native = Q(assembly['complex_lower'])
    b_cons = Q(assembly['conservative_complex_lower'])
    c_bit = Q(assembly['bit_lower'])

    bit_rows = [r for r in assembly['moments'] if r['side'] == 'bit']
    native_rows = [r for r in assembly['moments'] if r['side'] == 'complex']
    cons_rows = assembly['conservative_moments']

    ctrl_summary = run_controls(complex_profile, bit_profile, b_native, b_cons, c_bit)

    native_bracket = bracket_and_compare(complex_profile, 73, 33152, b_native, False, native_rows)
    cons_bracket = bracket_and_compare(complex_profile, 73, 33152, b_cons, True, cons_rows)
    bit_bracket = bracket_and_compare(bit_profile, 64, 28416, c_bit, True, bit_rows)

    all_t_summary = verify_all_t_binomial_and_bridge(complex_profile, b_native, repository)

    k_acc, min_margin_acc, dom_acc, ctrl_acc = reduce_endpoint_to_kappa(
        c_bit, b_native, assembly['bootstrap'], assembly['outer'], assembly['controls']
    )
    k_cons, min_margin_cons, dom_cons, ctrl_cons = reduce_endpoint_to_kappa(
        c_bit, b_cons, assembly['conservative_bootstrap'],
        assembly['conservative_outer'], assembly['conservative_controls']
    )
    require(k_acc == Q(assembly['kappa']) and k_cons == Q(assembly['conservative_kappa']),
            'Reduced kappa or conservative_kappa disagrees with assembly')
    surcharge_gain = k_acc - k_cons
    require(dec70(surcharge_gain) == assembly['native_correction_gain']
            and surcharge_gain == Q(2882367, 10**18),
            'Native correction gain mismatch')
    pr890_k = Q(claim['baseline_pr890_kappa'])
    gain_over_t21 = k_acc - pr890_k
    require(gain_over_t21 == Q(claim['delta']) == Q(2773066918, 10**18),
            'Gain over PR890 (T21) mismatch')

    return {
        'status': 'PASS_T37_BINOMIAL_AND_ENDPOINT_AUDIT',
        'base_commit': pins['base_commit'],
        'assignment_seed': 78,
        'audited_pr': 942,
        'audited_source_head': pins['audited_source_head'],
        'source_files_sha256': pins['files'],
        'selected_kappa_unchanged': assembly['kappa'],
        'selected_kappa_decimal': assembly['kappa_decimal'],
        'conservative_kappa': assembly['conservative_kappa'],
        'conservative_kappa_decimal': assembly['conservative_kappa_decimal'],
        'native_correction_gain': assembly['native_correction_gain'],
        'native_correction_gain_grid_ticks': int(surcharge_gain * 10**18),
        'gain_over_pr890_t21_decimal': claim['delta'],
        'gain_over_pr890_t21_grid_ticks': int(gain_over_t21 * 10**18),
        't37_accounting': accounting,
        'bit_supplier_accounting': {
            'git_blob_sha1': pins['git_blob_sha1']['inputs/PR589-EXPECTED.json'],
            'arity': 64,
            'live_stock': bit_live,
            'child_count': 904896,
            'rank_mass': bit_mass,
            'derived_deficit': bit_deficit,
        },
        'moment_brackets': {
            'complex_native': native_bracket,
            'complex_conservative': cons_bracket,
            'bit_surcharged': bit_bracket,
        },
        'all_t_supporting_lemma_binomial': all_t_summary,
        'outer_reduction_1024': {
            'accepted_bootstrap_steps': 7,
            'conservative_bootstrap_steps': 7,
            'accepted_outer_strict_constraints': 47,
            'conservative_outer_strict_constraints': 47,
            'min_quadratic_over_1024_linear_cutoff_margin_accepted': dom_acc,
            'min_quadratic_over_1024_linear_cutoff_margin_conservative': dom_cons,
            'accepted_absorption_gap': str(min_margin_acc - k_acc),
            'conservative_absorption_gap': str(min_margin_cons - k_cons),
            'accepted_outer_controls': ctrl_acc,
            'conservative_outer_controls': ctrl_cons,
        },
        'controls': ctrl_summary,
        'scope': (
            'Independent standard-library verification of the selected PR #942 (T37) '
            'native complex, conservative complex, and PR589 bit moment brackets plus '
            'all 42 strict rank inequalities of the all-T signed-dual supporting lemma '
            'using positive generalized-binomial enclosures on 2^-240, together with '
            'the 8-role 44+3+2 -> 48+1 remainder trade, 1024-bit reserve/bootstrap '
            'cutoffs, 94 strict outer slacks, and surcharge stakes. Physical circuit '
            'replay, owner window sweep, and inherited all-size/compiler/H1-H5 '
            'assumptions remain separate.'
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true')
    parser.add_argument('--repository', type=Path,
                        help='Also compare all 14 pinned and reference sources with this checkout')
    args = parser.parse_args()
    result = audit(args.repository)
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    path = HERE / 'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(text)
    else:
        require(path.is_file() and path.read_text() == text,
                'Recorded certificate differs from fresh independent computation')
    print(
        result['status'],
        '6 moment decisions; 42 all-T binomial rank inequalities; '
        '14 bootstrap steps; 94 outer slacks;',
        str(result['controls']['algebraic_comparisons']), 'algebraic comparisons;',
        str(result['controls']['mathematical_controls']), 'mathematical controls;',
        str(result['controls']['rejected_inputs']), 'rejected inputs.',
    )


if __name__ == '__main__':
    main()
