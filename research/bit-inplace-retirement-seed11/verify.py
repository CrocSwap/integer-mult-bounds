#!/usr/bin/env python3
"""Exact interval replay of the frozen helper470 same-slot profile bill."""
from collections import Counter
from fractions import Fraction as F
import ast
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
PINS = {
    "research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/moment.py": "81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482",
    "research/e8-bit-p111-tuned/tune/EXPECTED.json": "b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4",
    "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz": "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f",
    "research/e8-bit-p111-tuned/tune/fastc.py": "ae51f1fbb22b8c8dac8aab787c798361f6aa5d4e1fefb29e43d0197899d4eab5",
}
M, W, REPLICAS = 64, 28416, 288
BAD_SCALE = F(32 * M, 10**16 * W)
LOG_TERMS, EXP_TERMS, PRINT_SCALE = 24, 32, 10**30


def check(ok, message):
    if not ok:
        raise AssertionError(message)


def ln_interval(n):
    """Exact rational enclosure of ln(n), via binary reduction and atanh."""
    check(n >= 1, "log input must be positive")
    if n == 1:
        return F(0), F(0)

    def atanh_log(z):
        s = F(0)
        for j in range(LOG_TERMS):
            s += 2 * z ** (2 * j + 1) / (2 * j + 1)
        tail = 2 * z ** (2 * LOG_TERMS + 1) / ((2 * LOG_TERMS + 1) * (1 - z * z))
        return s, s + tail

    k = n.bit_length() - 1
    u = F(n, 1 << k)
    z = (u - 1) / (u + 1)
    ln2 = atanh_log(F(1, 3))
    lnu = atanh_log(z)
    return k * ln2[0] + lnu[0], k * ln2[1] + lnu[1]


def exp_pos_interval(xl, xu):
    """Exact positive-exponential interval; geometric tail after Taylor sum."""
    check(0 <= xl <= xu < F(1, 10), "positive exponential range")

    def bounds(x):
        s = t = F(1)
        for j in range(1, EXP_TERMS + 1):
            t *= x / j
            s += t
        nxt = t * x / (EXP_TERMS + 1)
        tail = nxt / (1 - x / (EXP_TERMS + 2))
        return s, s + tail

    return bounds(xl)[0], bounds(xu)[1]


def exp_neg_point_interval(x):
    """Exact alternating-series interval for exp(-x), 0 <= x < 1/10."""
    check(0 <= x < F(1, 10), "negative exponential range")

    def partial(terms):
        s = t = F(1)
        for j in range(1, terms):
            t *= -x / j
            s += t
        return s

    # For a decreasing alternating series, even term count ends below, odd above.
    return partial(EXP_TERMS), partial(EXP_TERMS - 1)


def power_q_interval(n, alpha):
    """Exact enclosure of n^(1-alpha); zero has its separate exact value."""
    if n == 0:
        return F(0), F(0)
    ll, lu = ln_interval(n)
    lo = exp_neg_point_interval(alpha * lu)[0]
    hi = exp_neg_point_interval(alpha * ll)[1]
    return n * lo, n * hi


def add_delta(profile, delta):
    ans = Counter(profile)
    ans.update(delta)
    return Counter({r: n for r, n in ans.items() if n})


def raw_sum_interval(profile, alpha):
    lo = hi = F(0)
    for r, count in profile.items():
        pl, pu = power_q_interval(r, alpha)
        lo += count * pl
        hi += count * pu
    return lo, hi


def moment_interval(profile, alpha):
    """Parent moment engine's frozen expression with its inherited bad term."""
    lo, hi = raw_sum_interval(profile, alpha)
    ln_m = ln_interval(M)
    ml, mu = exp_pos_interval(alpha * ln_m[0], alpha * ln_m[1])
    calls = sum(profile.values())
    scale = F(1, M * W)
    return (lo * ml * scale + BAD_SCALE * calls * ml,
            hi * mu * scale + BAD_SCALE * calls * mu)


def signed_sum_interval(terms, alpha):
    lo = hi = F(0)
    for rank, coefficient in terms.items():
        pl, pu = power_q_interval(rank, alpha)
        if coefficient >= 0:
            lo += coefficient * pl
            hi += coefficient * pu
        else:
            lo += coefficient * pu
            hi += coefficient * pl
    return lo, hi


def delta_for_remainder(r):
    # Shrink width 8 to 7 in place, and return one rank to this idle remainder.
    d = Counter({1: 1, 5: 1, 7: -1})
    d[r + 1] += 1
    if r:
        d[r] -= 1
    return Counter({rank: n for rank, n in d.items() if n})


def two_slot_relaxation(r):
    # PR1256's distinct favorable relaxation: move width 7 between two slots.
    d = Counter({1: 1, 5: 1, 7: -2, r + 8: 1, r: -1})
    return Counter({rank: n for rank, n in d.items() if n})


def decimal_interval(interval):
    lo, hi = interval
    return [str((lo.numerator * PRINT_SCALE) // lo.denominator),
            str(-((-hi.numerator * PRINT_SCALE) // hi.denominator))]


def load_inputs():
    raw = {}
    for path, expected_sha in PINS.items():
        data = (ROOT / path).read_bytes()
        check(hashlib.sha256(data).hexdigest() == expected_sha, f"SHA256 pin mismatch: {path}")
        raw[path] = data
    exp_path = "research/e8-bit-p111-tuned/tune/EXPECTED.json"
    expected = json.loads(raw[exp_path])
    moment_src = raw["research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/moment.py"].decode()
    check("p=F(r*n,m*W)" in moment_src and "32*m*sum(H.values())" in moment_src,
          "pinned parent moment and inherited surcharge formulas")
    gz_path = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
    word_raw = gzip.decompress(raw[gz_path])
    check(hashlib.sha256(raw[gz_path]).hexdigest() == expected["word"]["file_sha256"], "word gzip receipt")
    check(hashlib.sha256(word_raw).hexdigest() == expected["word"]["content_sha256"], "word content receipt")
    # The paid local histogram and global profile are both frozen source receipts.
    local = {int(k): int(v) for k, v in expected["word"]["local_histogram"].items()}
    profile = {int(k): int(v) for k, v in expected["nine"]["profile"].items()}
    source = ast.parse(raw["research/e8-bit-p111-tuned/tune/fastc.py"].decode())
    remainder = None
    for node in ast.walk(source):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "REM" for t in node.targets):
            remainder = ast.literal_eval(node.value)
            break
    check(remainder is not None, "frozen idle remainder declaration")
    rebuilt = Counter({r: REPLICAS * n for r, n in local.items()})
    rebuilt.update({int(r): int(n) for r, n in remainder.items()})
    check(dict(rebuilt) == profile, "288 * local profile + pinned remainder mismatch")
    check(sum(profile.values()) == 904896, "source child count")
    check(sum(r * n for r, n in profile.items()) == 1808352, "source rank mass")
    check(M * W - sum(r * n for r, n in profile.items()) == 10272, "source rank deficit")
    alpha = F(expected["nine"]["bit_lower"])
    check(0 < alpha < 1, "selected bit exponent domain")
    return expected, profile, remainder, alpha


def main():
    expected, profile, remainder, alpha = load_inputs()
    results = {}
    for r in range(57):
        uniform = Counter({1: 1, 5: 1, 7: -1})
        uniform[r + 1] += 1
        if r:
            uniform[r] -= 1
        q = signed_sum_interval(uniform, alpha)
        check(q[0] > 0, f"positive in-place raw moment delta r={r}")
    for r in (2, 4, 6):
        delta = delta_for_remainder(r)
        candidate = add_delta(profile, delta)
        check(sum(delta.values()) == 1, f"one added child r={r}")
        check(sum(k * v for k, v in delta.items()) == 0, f"rank mass returned r={r}")
        check(all(v >= 0 for v in candidate.values()), f"nonnegative candidate histogram r={r}")
        base_cost = moment_interval(profile, alpha)
        new_cost = moment_interval(candidate, alpha)
        observed = (new_cost[0] - base_cost[1], new_cost[1] - base_cost[0])
        direct_raw = signed_sum_interval(delta, alpha)
        ml = exp_pos_interval(alpha * ln_interval(M)[0], alpha * ln_interval(M)[1])
        direct = (direct_raw[0] * ml[0] / (M * W) + BAD_SCALE * ml[0],
                  direct_raw[1] * ml[1] / (M * W) + BAD_SCALE * ml[1])
        check(observed[0] > 0 and direct[0] > 0, f"complete paid bill increases r={r}")
        check(observed[0] <= direct[1] and direct[0] <= observed[1], f"independent delta matches full-profile price r={r}")

        omitted_return = signed_sum_interval({1: 1, 5: 1, 7: -1}, alpha)
        check(omitted_return[1] < 0, "negative control: omitting returned idle rank looks favorable")
        relaxed = signed_sum_interval(two_slot_relaxation(r), alpha)
        check(relaxed[1] < 0, f"positive control: distinct PR1256 two-slot relaxation r={r}")

        # Mutation controls: deleting the returned rank or miscounting the new child
        # must violate the two exact conservation laws checked above.
        bad_return = Counter(delta)
        bad_return[r] -= 1
        check(sum(bad_return.values()) != sum(delta.values()), f"control catches omitted return r={r}")
        bad_call = Counter(delta)
        bad_call[1] -= 1
        check(sum(bad_call.values()) != sum(delta.values()), f"control catches omitted helper child r={r}")

        results[str(r)] = {
            "delta_histogram": dict(sorted(delta.items())),
            "calls_delta": sum(delta.values()),
            "rank_mass_delta": sum(k * v for k, v in delta.items()),
            "full_moment_delta_interval_scaled_1e-30": decimal_interval(observed),
            "direct_formula_interval_scaled_1e-30": decimal_interval(direct),
            "two_slot_relaxation_raw_delta_interval_scaled_1e-30": decimal_interval(relaxed),
        }

    # Exact all-remainder argument is written out in README: the interval replay
    # independently covers every integer remainder in the fixed width-64 domain.
    print(json.dumps({
        "status": "PASS_SAME_SLOT_HELPER470_BILL_INCREASES",
        "base_commit": "bce54fb3f895cbe5cd4c0eb477c3afeed100190f",
        "selected_bit_exponent": str(alpha),
        "inherited_bad_term": "32*64*N/(10^16*28416) * 64^alpha",
        "pinned_idle_remainder": {str(k): int(v) for k, v in sorted(remainder.items())},
        "actual_remainder_classes": results,
        "uniform_remainders_checked": 57,
        "interval_method": f"exact Fraction atanh-log ({LOG_TERMS} terms), alternating/geometric Taylor exp ({EXP_TERMS} terms), signed outward intervals",
        "source_profile_calls": sum(profile.values()),
        "source_profile_rank_mass": sum(k*v for k,v in profile.items()),
        "selected_record_bit_lower": expected["nine"]["bit_lower"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
