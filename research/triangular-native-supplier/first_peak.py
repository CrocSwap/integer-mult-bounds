"""Check the integer comparisons for the first connected occupied-tape bound."""

from staged_carriers import RANK_LOGS, strong_precision_log


def receipt():
    a = strong_precision_log()
    s = a + 1
    old_guard = 2_881_869_654_258_596
    old_matrix_log = 2 * 240_000_000_000_000
    # A is even.  The first multiple of six at least 2**A is 2**A + 2.
    assert a > 2 and a % 2 == 0 and pow(2, a, 6) == 4
    # This expresses bounds on logarithms. Never allocate the input or its width p.
    log_j = max(RANK_LOGS) * 20_000
    log_private = (1 << 20) * (s + 1) ** 2
    log_k = (s + 1) ** 8
    local_constant_log = 64 + 8 * (log_j + 1) + 64 * s + 8 * (log_private + 1)
    assert local_constant_log < log_k
    # The largest logical core bound is (T+1) times K**(8*(s+130)).
    log_scratch_factor = 8 * (s + 130) * log_k
    # L <= p/6 + 3; this suffices for log2(core) < p/5.
    margin = 30 * (log_scratch_factor + 4)
    assert margin.bit_length() <= a
    # Peak with all observer counters is <= 32*core**4.
    assert a > 8
    assert old_guard > a + 4 and old_matrix_log > a + 3
    return {
        "precision_exponent_A": a,
        "size_parameter_s": s,
        "log2_largest_fixed_compiler_bound": log_j,
        "log2_private_clock_and_cell_bound": log_private,
        "local_factor_check_bits": local_constant_log.bit_length(),
        "log2_K_bit_length": log_k.bit_length(),
        "required_margin_bit_length": margin.bit_length(),
        "old_guard_minus_A_minus_4": old_guard - a - 4,
        "old_matrix_exponent_minus_A_minus_2": old_matrix_log - a - 2,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(receipt(), indent=2))
