"""Exact source binding and finite controls for a conditional Lean recurrence.

This imports no predecessor checker and performs no Lean execution.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from math import isqrt
import json
import re

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def fraction(value):
    return str(value.numerator) + "/" + str(value.denominator)


def power_bounds(data, profile):
    need(data["schema"] == "stopped-recurrence-power-bounds/1", "power-bound schema")
    den = data["denominator"]
    need(type(den) is int and den == 10**12, "rational bound grid")
    need((data["power_numerator"], data["power_denominator"], data["base_denominator"])
         == (9983, 10000, 64), "selected exponent and width")
    values = data["upper_numerators"]
    need(set(values) == {str(r) for r in profile}, "power-bound rank coverage")
    result = {}
    for rank in sorted(profile):
        n = values[str(rank)]
        need(type(n) is int and 0 < n <= den, "positive rational power bound")
        # The 10000th-power map is strictly increasing on nonnegative reals.
        # Both comparisons are integer arithmetic, without logarithms/floats.
        target = pow(rank, 9983) * pow(den, 10000)
        scale = pow(64, 9983)
        need(pow(n - 1, 10000) * scale < target <= pow(n, 10000) * scale,
             "exact fractional-power enclosure")
        result[rank] = F(n, den)
    return result


def bounded_recurrence(profile, live, bad, width, limit):
    values, prefix_maximum = [F(0)], [F(0)]
    trace = sha256()
    for n in range(1, limit + 1):
        if n < 64:
            value = F(width)
        else:
            f = n // 64
            value = sum((F(count, live) * values[rank * f] for rank, count in profile.items()), F(0))
            value += bad * prefix_maximum[f] + n + width
        # Since exponent=9983/10000 >= 1/2 and n>=1, this integer
        # envelope is no larger than the Lean theorem's power envelope.
        lower_potential = 200 * n + 10000 * width * isqrt(n)
        need(value <= lower_potential, "finite stopped-recurrence bound")
        values.append(value)
        prefix_maximum.append(max(prefix_maximum[-1], value))
        if n <= 256:
            need(prefix_maximum[n] == max(values), "fallback maximum independent scan")
        trace.update((str(n) + ":" + fraction(value) + "\n").encode())
    return {"w": width, "widths": limit + 1, "trace_sha256": trace.hexdigest(),
            "last_cost": fraction(values[-1]), "finite_bound": "200*n+10000*w*floor(sqrt(n))"}


def replay(root=HERE):
    read = lambda p: json.loads((root / p).read_text())
    expected = read("sources/selected/EXPECTED.json")
    global_record = read("sources/selected/GLOBAL.json")
    assembly = read("sources/selected/ASSEMBLY.json")
    profile = {int(k): v for k, v in expected["nine"]["profile"].items()}
    need(profile == {int(k): v for k, v in global_record["profile"].items()}, "two selected profile sources")
    m, live = global_record["m"], global_record["live"]
    need((m, live, global_record["maxchild"]) == (64, 28416, 42), "selected dimensions")
    need(assembly["bit_lower"] == expected["nine"]["bit_lower"], "selected assembly bit binding")
    need(all(type(v) is int and v > 0 and 0 < r < m for r, v in profile.items()), "positive proper children")
    formal = (root / "lean/Selected.lean").read_text()
    def vector(name):
        match = re.search(r"def " + name + r"[^\n]*:= !\[([^]]+)\]", formal)
        need(match is not None, "literal Lean vector: " + name)
        return [int(x.strip()) for x in match[1].split(",")]
    ranks, counts = vector("ranks"), vector("counts")
    need(list(zip(ranks, counts)) == sorted(profile.items()), "Lean profile matches selected sources")
    fallback = 32 * m**2 * sum(profile.values())
    need(fallback == 118606528512, "source fallback allowance")
    bad = F(fallback, 10**16 * live)
    linear = sum((F(r * count, m * live) for r, count in profile.items()), F(0)) + bad / m
    need(linear == F(2874298095721977, 2890625000000000) < F(199, 200), "linear moment binding")
    bounds = power_bounds(read("POWER-BOUNDS.json"), profile)
    upper = sum((F(count, live) * bounds[r] for r, count in profile.items()), F(0)) + bad * bounds[1]
    need(upper < F(9999, 10000), "fractional moment margin")
    need("118606528512 / (10000000000000000 * 28416)" in formal and
         "def exponent : ℝ := 9983 / 10000" in formal and "counts r / 28416" in formal,
         "Lean scalar binding")
    # These all-width countermodels are also proved in Counterexamples.lean.
    for n in range(4097):
        need(n*n <= F(1, 4) * (4*(n//2))**2 + 2*(n+1), "expanding-child recurrence")
        need(n*n <= n*(n+1), "width-dependent charge")
    witness = 20401
    need(witness**2 > 20400*witness, "expanding child defeats the source-exponent majorant")
    need(max([0, 1, 0]) > [0, 1, 0][-1], "nonmonotone fallback maximum")
    runs = [bounded_recurrence(profile, live, bad, w, 4096) for w in (1, 3, 17, 1000)]
    return {"schema": "stopped-recurrence-audit/1", "profile": {str(k): v for k, v in sorted(profile.items())},
            "live": live, "maximum_rank": max(profile), "fallback_calls": fallback,
            "bad_coefficient": fraction(bad), "linear_moment": fraction(linear),
            "fractional_moment_upper": fraction(upper), "fractional_margin": fraction(F(9999, 10000)-upper),
            "power_enclosures": len(bounds), "finite_recurrences": runs,
            "countermodel_widths": 4097,
            "expanding_child_witness": {"n": witness, "cost": witness**2,
                "potential_upper": 20400*witness, "m": 2, "rank": 4,
                "coefficient": "1/4", "C": 2, "w": 1, "exponent": "9983/10000"},
            "nonmonotone_costs": [0, 1, 0],
            "scope": "Exact source/moment binding and finite checks only. Fractional moment is an explicit Lean hypothesis; no kernel execution or full-machine uniform cost is inferred."}


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
