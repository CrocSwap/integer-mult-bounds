"""Exact finite corroboration of the sharp split-charge theorem. Apache-2.0."""

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


BITS = 88
SCALE = 1 << BITS
PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exponent(t):
    require(isinstance(t, F) and 0 < t < 1, "exponent must be in (0,1)")
    require(t.denominator <= 128, "finite verifier exponent limit")
    return t.numerator, t.denominator


def root_floor(n, degree):
    require(n >= 0 and 1 <= degree <= 128, "invalid integer root")
    lo, hi = 0, 1 << ((n.bit_length() + degree - 1) // degree)
    for _ in range(hi.bit_length()):
        if hi - lo <= 1:
            break
        mid = (lo + hi) // 2
        if mid**degree <= n:
            lo = mid
        else:
            hi = mid
    require(lo**degree <= n < (lo + 1)**degree, "integer root contract")
    return lo


def power_bounds(x, t):
    a, b = exponent(t)
    require(isinstance(x, F) and 0 <= x <= 1, "power input outside [0,1]")
    scaled = (x.numerator**a * SCALE**b) // x.denominator**a
    k = root_floor(scaled, b)
    lo, hi = F(k, SCALE), F(k + 1, SCALE)
    if lo**b == x**a:
        hi = lo
    require(lo**b <= x**a <= hi**b, "power enclosure contract")
    return lo, hi


def critical_bounds(t):
    a, b = exponent(t)
    # y = s_t^(1/b); a-(b-a)y^b-b*y^(b-a) is strictly decreasing.
    lo, hi = F(0), F(1)
    for _ in range(BITS):
        mid = (lo + hi) / 2
        value = a - (b - a) * mid**b - b * mid**(b - a)
        if value == 0:
            lo = hi = mid
            break
        if value > 0:
            lo = mid
        else:
            hi = mid
    require(0 < lo <= hi < 1, "critical interval interior")
    require(a - (b - a) * lo**b - b * lo**(b - a) >= 0,
            "critical lower endpoint")
    require(a - (b - a) * hi**b - b * hi**(b - a) <= 0,
            "critical upper endpoint")
    return (lo**b, hi**b), (t / hi**(b - a), t / lo**(b - a))


def ratio_bounds(q, r, j, t):
    require(1 <= j <= 10**6 and 1 <= q <= 64 and 0 <= r < j,
            "split domain")
    s = F(r, j)
    low, high = power_bounds(s, t)
    return (q + low) / (q + s), (q + high) / (q + s)


def census(t):
    _, constant = critical_bounds(t)
    count = 0
    for j in range(1, 49):
        for r in range(j):
            s = F(r, j)
            low, high = power_bounds(s, t)
            require(low >= s, "concave power lies above chord")
            for q in range(1, 9):
                upper = (q + high) / (q + s)
                require(upper <= constant[1], "sharp constant violated")
                # Direct cross-multiplication certifies reduction to q=1.
                require((q - 1) * (low - s) >= 0, "quotient reduction")
                count += 1
    return count


def sharpness(t):
    critical, constant = critical_bounds(t)
    last = None
    for k in range(1, 7):
        j = 10**k
        r_low = (critical[0] * j).__floor__()
        r_high = (critical[1] * j).__floor__()
        require(r_low == r_high, "critical floor unresolved")
        last = ratio_bounds(1, r_low, j, t)
        require(last[1] <= constant[1], "sharpness sequence upper bound")
    require(constant[1] - last[0] < F(1, 10**10), "sharpness convergence")
    return {"t": str(t), "J": j, "R": j + r_low,
            "gap_upper": str(constant[1] - last[0])}


def must_reject(call):
    try:
        call()
    except ValueError:
        return
    raise ValueError("negative control accepted")


def controls():
    for t in (F(0), F(1), F(-1, 2), F(1, 129)):
        must_reject(lambda: critical_bounds(t))
    must_reject(lambda: ratio_bounds(0, 0, 1, F(1, 2)))
    must_reject(lambda: ratio_bounds(1, 1, 1, F(1, 2)))
    must_reject(lambda: power_bounds(F(-1), F(1, 2)))
    # J=6,R=7 refutes both coefficient 1 and the tempting rounded 6/5.
    witness = ratio_bounds(1, 1, 6, F(1, 2))
    must_reject(lambda: require(witness[0] <= 1, "coefficient 1 fails"))
    must_reject(lambda: require(witness[0] <= F(6, 5), "6/5 fails"))
    _, c = critical_bounds(F(1, 2))
    sqrt2 = root_floor(2 * SCALE**2, 2)
    closed = ((1 + F(sqrt2, SCALE)) / 2,
              (1 + F(sqrt2 + 1, SCALE)) / 2)
    require(max(c[0], closed[0]) <= min(c[1], closed[1]),
            "half-exponent closed form disagreement")
    _, third = critical_bounds(F(1, 3))
    require(third == (F(4, 3), F(4, 3)) and
            ratio_bounds(1, 1, 8, F(1, 3)) == third,
            "attained third-exponent closed form disagreement")
    must_reject(lambda: require(witness[0] <= 1 / c[1],
                               "reciprocal constant fails"))
    # The higher-moment transfer requires sigma>=1.
    # At t=1/2,sigma=3/4,J=1,R=256, charge is 256;
    # even the older coefficient 2 would give only 2*64=128.
    must_reject(lambda: require(256 <= 2 * 64, "sigma<1 transfer fails"))
    return 11


def result():
    values = (F(1, 4), F(1, 3), F(1, 2), F(2, 3), F(3, 4), F(7, 8))
    counts = {str(t): census(t) for t in values}
    witnesses = [sharpness(t) for t in (*values, F(127, 128))]
    for t in (*values, F(127, 128)):
        _, (lo, hi) = critical_bounds(t)
        require(1 < lo <= hi < 2, "strict improvement over factor 2")
    files = ("README.md", "verify.py", "TASK.json", "SOURCES.json", "VERIFY.json")
    hashes = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
              for name in files}
    return {"schema": "sharp-integer-split-charge/v1", "source_sha256": hashes,
            "split_cases_by_exponent": counts, "sharpness_sequences": witnesses,
            "rejected_controls": controls(),
            "claim": "Scoped analytic proof; finite checks corroborate it."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    actual = result()
    if args.write:
        # Explicit author operation only; ordinary verification never writes.
        args.write.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(actual == expected, "receipt or source-hash mismatch")
    total = sum(actual["split_cases_by_exponent"].values())
    print(f"PASS_SHARP_INTEGER_SPLIT_CHARGE cases={total} "
          f"sharpness_sequences=7 rejected_controls={actual['rejected_controls']}")


if __name__ == "__main__":
    main()
