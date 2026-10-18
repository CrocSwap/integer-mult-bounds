"""Exact bounded-domain equality of rounded scalar increments. Apache-2.0."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def floor_sum(n, modulus, a, b):
    """Sum floor((a*i+b)/modulus), i=0..n-1; signed a,b allowed."""
    require(n >= 0 and modulus > 0, "floor sum domain")
    answer = 0
    while True:
        qa, a = divmod(a, modulus)
        qb, b = divmod(b, modulus)
        answer += qa * n * (n - 1) // 2 + qb * n
        height = a * n + b
        if height < modulus:
            return answer
        n, b = divmod(height, modulus)
        modulus, a = a, modulus


def residues_below(a, d, lower, upper, cutoff):
    n = upper - lower + 1
    require(n >= 0 and 0 <= cutoff <= d, "residue interval")
    b = a * lower
    return n - (floor_sum(n, d, a, b + d - cutoff) - floor_sum(n, d, a, b))


def equal_count(q, gap, lower, upper):
    """q is coefficient in coarse-grid units; integer inputs [lower,upper]."""
    require(isinstance(q, Fraction) and type(gap) is int and gap >= 1,
            "rational coefficient and positive precision gap required")
    require(type(lower) is int and type(upper) is int and lower <= upper,
            "nonempty integer interval required")
    a, d = q.numerator, q.denominator
    twice_g = 2 << gap
    low_end = (d - 1) // twice_g + 1
    high_start = (d * (twice_g - 1) + twice_g - 1) // twice_g
    return (residues_below(a, d, lower, upper, low_end)
            + upper - lower + 1 - residues_below(a, d, lower, upper, high_start))


def first_failure(q, gap, lower, upper):
    if equal_count(q, gap, lower, upper) == upper - lower + 1:
        return None
    left, right = lower, upper
    while left < right:
        middle = (left + right) // 2
        if equal_count(q, gap, lower, middle) == middle - lower + 1:
            left = middle + 1
        else:
            right = middle
    return left


def round_at(value, bits):
    scaled = value * (1 << bits) + Fraction(1, 2)
    return Fraction(scaled.numerator // scaled.denominator, 1 << bits)


def direct(q, gap, k):
    return round_at(q * k, 0) == round_at(q * k, gap)


def run():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        if row["usage"] == "input":
            require(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "source pin " + row["path"])
    floor_cases = 0
    for n in range(13):
        for d in range(1, 14):
            for a in range(-15, 16):
                for b in (-29, -1, 0, 1, 23):
                    require(floor_sum(n, d, a, b) == sum((a * i + b) // d for i in range(n)),
                            "independent floor sum")
                    floor_cases += 1
    intervals = dirty_inputs = 0
    for a in range(-12, 13):
        for d in range(1, 20):
            q = Fraction(a, d)
            for gap in (1, 2, 4):
                for lo, hi in ((-31, -1), (-17, 19), (0, 0), (0, 37), (11, 43)):
                    flags = [direct(q, gap, k) for k in range(lo, hi + 1)]
                    require(equal_count(q, gap, lo, hi) == sum(flags), "rounded count")
                    expected = next((k for k in range(lo, hi + 1) if not flags[k - lo]), None)
                    require(first_failure(q, gap, lo, hi) == expected, "least counterexample")
                    intervals += 1
                    dirty_inputs += len(flags)
    d = (1 << 100) + 1
    q, gap, hi = Fraction(1, d), 3, 1 << 200
    periods, tail = divmod(hi + 1, d)
    low = (d - 1) // 16 + 1
    high = (15 * d + 15) // 16
    expected = periods * (low + d - high) + min(tail, low) + max(0, tail - high)
    huge_count = equal_count(q, gap, 0, hi)
    huge_first = first_failure(q, gap, 0, hi)
    require(huge_count == expected and huge_first == low, "huge exact period oracle")
    require(equal_count(Fraction(1, 1000), 2, -100, 100) == 201, "bounded safe nonintegral")
    require(direct(Fraction(1, 8), 2, -1) and not direct(Fraction(1, 8), 2, 1), "asymmetric ties")
    require(first_failure(Fraction(1, 1000), 2, -100, 125) == 125, "reachable boundary")
    inverse_cases = 0
    for k in range(-17, 18):
        for y in (Fraction(-7, 3), Fraction(0), Fraction(11, 5)):
            q = Fraction(7, 19)
            restored = y + round_at(q * k, 0) - round_at(q * k, 2)
            require((restored == y) == direct(q, 2, k), "dirty inverse criterion")
            inverse_cases += 1
    controls = []
    for name, call in (("zero_gap", lambda: equal_count(Fraction(1, 3), 0, 0, 1)),
                       ("empty_domain", lambda: equal_count(Fraction(1, 3), 1, 2, 1)),
                       ("floating_coefficient", lambda: equal_count(0.5, 1, 0, 1))):
        try:
            call()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("accepted invalid input: " + name)
    return {"status": "PASS_BOUNDED_GRID_ROUNDING_COUNT", "floor_sum_cases": floor_cases,
            "independent_intervals": intervals, "dirty_inputs": dirty_inputs,
            "dirty_inverse_cases": inverse_cases, "huge_interval": [0, hi],
            "huge_denominator": d, "huge_equal_count": huge_count,
            "huge_first_failure": huge_first, "bounded_safe_nonintegral": 201,
            "tie_countercontrol": {"negative_safe": -1, "positive_unsafe": 1},
            "rejected_controls": controls, "new_kappa": False}


if __name__ == "__main__":
    result = run()
    if "--write" in sys.argv:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text(encoding="utf-8")), "receipt mismatch")
    print(result["status"], "intervals=" + str(result["independent_intervals"]),
          "huge_first_failure=" + str(result["huge_first_failure"]))
