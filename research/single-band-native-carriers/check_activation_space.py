"""Evaluate the all-size stripe bound and the exact entrance geometry of a native profile."""

from fractions import Fraction

from linear_geometry import ceil_log2, connected_exponent, entrance_geometry


def receipt(
    rank_logs,
    complex_log,
    final_width_log,
    program_log,
    raw_power,
    raw_ports_log=20,
    context_guard=872,
    *,
    complex_power=None,
):
    exponent = connected_exponent(final_width_log, complex_log)
    s = exponent + 1
    # Each raw rule has fewer than 2**raw_ports_log targets and paid occurrences separately.
    # The ambient dimension is at most 153. Keep every bound on raw visits and live copies.
    nodes_log = 64 + ceil_log2(raw_power + 1) + (raw_ports_log + 10) * raw_power
    local_log = 4 * nodes_log + 8 * ceil_log2(1 + max(complex_log, *rank_logs)) + 512
    q = 1 << ceil_log2(local_log + 1)
    numerical_power = raw_power if complex_power is None else complex_power
    assert 0 < numerical_power <= raw_power
    context_cost_bits = (context_guard * numerical_power * (complex_log + 1) ** 2).bit_length()
    assert context_cost_bits <= complex_log
    # Reserve 32 non-native outer levels at 1024 bits of local logarithmic slack per level.
    ranks = (complex_log, *rank_logs)
    quotients = [(s + h - 1) // h for h in ranks]
    depth = 2 + quotients[0] + sum(3 + c for c in quotients[1:])
    payload_excess = (2 * depth + 4) * q + 64 * 1024 + 48 + 2 * (s + 128).bit_length()
    slope = 2 * q * sum(Fraction(1, h) for h in ranks)
    intercept = (10 + 8 * len(rank_logs)) * q + 64 * 1024 + 48
    per_step = Fraction(1, 2) - slope - Fraction(1, 32)
    assert per_step > 0 and per_step * s - intercept - 3 > 1024
    assert s // 2 - 2 - payload_excess > 1024
    geometry = entrance_geometry(exponent)
    legacy = entrance_geometry(exponent, quadratic=True)
    # Linear sums divided by (s+1)^8 decrease on this tail. Every private and hardware
    # counter has a separate allowance with no multiplicative factor on an actual field.
    table_max = (1 << 21) * (s + 1)
    assert 64 + 8 * (program_log + 1) + 64 * s + 8 * (table_max + 1) < (s + 1) ** 8
    assert 33**9 < 2 * 32**9
    assert (12 * (128 * (s + 130) * (s + 1) ** 8 + 64)).bit_length() <= s - 2
    assert (1200 * (64 * (128 * s**2 + s) + 2 * s + 128)).bit_length() <= s - 2
    return {
        "log2_sufficient_public_precision": exponent,
        "initial_s": s,
        "raw_structural_nodes_log2_upper": nodes_log,
        "native_volume_log2_upper": q,
        "positive_context_cost_bitlength_upper": context_cost_bits,
        "native_depth_bound_at_entrance": depth,
        "stripe_excess_log_at_entrance": payload_excess,
        "stripe_margin_at_entrance": s // 2 - 2 - payload_excess,
        "uniform_payload_slope": str(slope),
        "all_size_margin_lower_at_entrance": int(per_step * s - intercept - 3),
        "linear_geometry": geometry,
        "prior_geometry_at_same_n": legacy,
    }
