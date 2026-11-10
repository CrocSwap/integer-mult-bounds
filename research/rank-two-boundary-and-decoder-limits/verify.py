"""Replay the frozen-boundary calculation and reprice the saved rank profiles."""
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path

from boundary import boundary_rows

EVIDENCE = Path(__file__).resolve().parent / "evidence"
SCALE = 10**30

def load(name):
    data = (EVIDENCE / name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith(".gz") else data)

def enclosure(rank, saving):
    exponent = 1 - saving
    target = rank**exponent.numerator * SCALE**exponent.denominator
    lower, upper = 0, (rank + 1) * SCALE
    while upper - lower > 1:
        mid = (lower + upper) // 2
        if mid**exponent.denominator <= target:
            lower = mid
        else:
            upper = mid
    return lower, upper

def signed_histograms(*terms):
    result = [0] * 23
    for sign, histogram in terms:
        for rank, count in histogram.items():
            result[int(rank)] += sign * count
    return result

def moment_bounds(coefficients, powers):
    lower = upper = 0
    for rank, coefficient in enumerate(coefficients):
        if rank == 0 or coefficient == 0:
            continue
        lo, hi = powers[rank]
        if coefficient < 0:
            lo, hi = hi, lo
        lower += coefficient * lo
        upper += coefficient * hi
    return Fraction(lower, SCALE), Fraction(upper, SCALE)

def overlap(first, second):
    return max(first[0], second[0]) <= min(first[1], second[1])

def published_interval(entry):
    return tuple(map(Fraction, entry["rational"]))

def best_bound(rows):
    return max(lo for lo, _ in rows), max(hi for _, hi in rows)

def main():
    assert __debug__, "Run without optimization"
    provenance = load("provenance.json")
    for name, expected in provenance["published_evidence_sha256"].items():
        assert sha256((EVIDENCE / name).read_bytes()).hexdigest() == expected, name

    rows = boundary_rows()
    assert rows == load("boundary.json")["cases"]
    assert len(rows) == 111
    for row in rows:
        assert row["initial_plane_extension_dimension"] == 0
        assert row["final_complement_shrink_dimension"] == 0
    print("PASS: zero frozen-neighbor endpoint extensions on 111 ports")

    data = load("profiles.json.gz")
    single_audit = load("single-invoice-audit.json")["rows"]
    paired_audit = load("paired-invoice.json")["summaries"]
    caller = load("45-port-caller.json")
    baseline = data["baseline"]

    for historical in single_audit:
        saving = Fraction(historical["kappa"])
        powers = {rank: enclosure(rank, saving) for rank in range(1, 23)}
        for name, expected in (("single", 6993), ("paired", 8040)):
            bounds = []
            retained = []
            for row in data[name]:
                coeff = signed_histograms((1, row["helper"]), (-1, row["paid"]),
                                          (-1, baseline["helper_targets"]), (1, baseline["paid"]))
                interval = moment_bounds(coeff, powers)
                assert interval[1] < 0
                bounds.append(interval)
                if row.get("retained_rank2_seeds"):
                    retained.append(interval)
            assert len(bounds) == expected
            best = best_bound(bounds)
            if name == "paired":
                published = paired_audit[str(saving)]
                assert overlap(best, published_interval(published["best_delta"]))
                assert overlap(best_bound(retained), published_interval(published["best_retaining_any_rank2_plane_delta"]))
            else:
                assert historical["negative_cases"] == expected
                assert abs(best[1] - Fraction(historical["best_upper_bound"])) < Fraction(1, 10**22)
            print(f"PASS: {name}, kappa={saving}, {expected} negative profiles, best upper bound {float(best[1]):.9f}")

        factors = caller["factor_rank_bounds"]
        assert factors["protected_C"] + 3 * factors["each_native_d"] == factors["main_factored_path_C_d3_d2_d1_rank_at_most"] == 20
        coefficient = signed_histograms((1, caller["UNCONSTRUCTED_target_with90_rank20_main_rows"]),
                                        (-1, caller["three_native_paid_plus_inherited_early_queries"]))
        margin = moment_bounds(coefficient, powers)
        assert margin[1] < 0
        assert overlap(margin, published_interval(caller["optimistic_margins_before_decoder"][str(saving)]))
        print(f"PASS: fixed 45-port caller tariff at kappa={saving}, upper margin {float(margin[1]):.9f}")

if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Run without Python optimization")
    main()
