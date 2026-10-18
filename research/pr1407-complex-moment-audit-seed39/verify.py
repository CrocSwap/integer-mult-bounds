#!/usr/bin/env python3
"""Code-disjoint exact interval check of PR1407's complex moment receipts."""
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
REFERENCE_SHA256 = "3e1657810dc9ceff2e36fc0cd030c2a03f7457e55ba9bad3cd7d49fb58e6ca5c"
M, W = 73, 14336
LOG_TERMS, EXP_TERMS = 48, 32
PRINT_SCALE = 10**32


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def atanh_log(z):
    """Enclose 2*atanh(z) with a positive rational tail bound."""
    require(0 <= z <= F(1, 3), "range-reduced atanh input")
    total = F(0)
    for j in range(LOG_TERMS):
        total += 2 * z ** (2*j + 1) / (2*j + 1)
    tail = 2 * z ** (2*LOG_TERMS + 1) / ((2*LOG_TERMS + 1) * (1-z*z))
    return total, total + tail


def ln_integer(n):
    """Exact interval for ln(n); binary reduction keeps the series ratio <=1/9."""
    require(type(n) is int and n >= 1, "positive integer logarithm input")
    if n == 1:
        return F(0), F(0)
    k = n.bit_length() - 1
    reduced = F(n, 1 << k)
    z = (reduced - 1) / (reduced + 1)
    ln2 = atanh_log(F(1, 3))
    ln_reduced = atanh_log(z)
    return k*ln2[0] + ln_reduced[0], k*ln2[1] + ln_reduced[1]


def ln_ratio(n, d):
    """Exact interval for ln(n/d), from independently enclosed integer logs."""
    nl, nu = ln_integer(n)
    dl, du = ln_integer(d)
    return nl-du, nu-dl


def exp_positive(xl, xu):
    """Exact interval for exp(x), 0<=xl<=xu<1/10, with a geometric tail."""
    require(0 <= xl <= xu < F(1, 10), "small positive exponential domain")

    def partial_and_tail(x):
        s = t = F(1)
        for j in range(1, EXP_TERMS):
            t *= x / j
            s += t
        next_term = t * x / EXP_TERMS
        tail = next_term / (1 - x/(EXP_TERMS+1))
        return s, s + tail

    return partial_and_tail(xl)[0], partial_and_tail(xu)[1]


def moment_interval(profile, alpha, surcharge):
    """Enclose the pinned complex moment, with the inherited optional envelope."""
    require(0 < alpha < F(1, 50), "complex exponent interval")
    lower = upper = F(0)
    for r, count in profile.items():
        require(type(r) is int and 0 < r < M and type(count) is int and count > 0,
                "positive paid profile with ranks below width")
        ll, lu = ln_ratio(M, r)
        pl, pu = exp_positive(alpha*ll, alpha*lu)
        scale = F(count*r, M*W)
        lower += scale*pl
        upper += scale*pu
    if surcharge:
        ml, mu = exp_positive(alpha*ln_integer(M)[0], alpha*ln_integer(M)[1])
        factor = F(32*M*sum(profile.values()), 10**16*W)
        lower += factor*ml
        upper += factor*mu
    return lower, upper


def parse_bracket(rows, surcharge):
    rows = [x for x in rows if x["surcharge"] is surcharge]
    require(len(rows) == 2, "published lower and upper endpoint rows")
    return [(F(x["endpoint"]), x["accept"]) for x in rows]


def verify_bracket(profile, rows, surcharge, label):
    result = []
    for endpoint, accepts in parse_bracket(rows, surcharge):
        lo, hi = moment_interval(profile, endpoint, surcharge)
        if accepts:
            require(hi < 1, f"{label}: accepted endpoint has strict upper moment < 1")
        else:
            require(lo > 1, f"{label}: rejected endpoint has strict lower moment > 1")
        result.append({"endpoint": str(endpoint), "accept": accepts,
                       "moment_minus_one_interval_scaled_1e32": scaled_interval(lo-1, hi-1)})
    require(F(result[0]["endpoint"]) < F(result[1]["endpoint"]), f"{label}: ordered root bracket")
    return result


def scaled_interval(lo, hi):
    lower = (lo.numerator*PRINT_SCALE)//lo.denominator
    upper = -((-hi.numerator*PRINT_SCALE)//hi.denominator)
    return [str(lower), str(upper)]


def floor_grid(x, scale):
    return F((x.numerator*scale)//x.denominator, scale)


def must_reject(fn, label):
    try:
        fn()
    except AssertionError:
        return label
    raise AssertionError("failure control unexpectedly passed: " + label)


def main():
    ref_path = PKG / "REFERENCE.json"
    ref_raw = ref_path.read_bytes()
    require(hashlib.sha256(ref_raw).hexdigest() == REFERENCE_SHA256,
            "immutable reference snapshot hash")
    ref = json.loads(ref_raw)
    require(ref["source"]["pr"] == 1407 and
            ref["source"]["head"] == "d8640f5b7ae99b43f5d56146cb94ca62b8b3835d",
            "external PR head pin")
    require(ref["surcharge_model"] == {"complex": False, "bit": True},
            "candidate surcharge convention")

    selected_record = json.loads((ROOT / "certificates/selected-result.json").read_text())
    selected = json.loads((ROOT / "research/community-frontier1094-audit/ASSEMBLY.json").read_text())
    replay = json.loads((ROOT / "research/community-frontier1094-audit/REPLAY.json").read_text())
    require(selected_record["kappa"] == selected["kappa"] == replay["kappa"],
            "selected record, assembly and replay agree")
    require(replay["complex_profile"] == selected["complex_profile"],
            "selected replay profile matches its assembly")
    check_path = ROOT / "research/community-batch1099-audit/check_frontier1094.py"
    if check_path.exists():
        require("live=14336" in check_path.read_text(), "selected live width provenance")
    base = {int(r): int(n) for r, n in selected["complex_profile"].items()}
    candidate = {int(r): int(n) for r, n in ref["candidate_profile"].items()}
    advertised = {int(r): int(n) for r, n in ref["result"]["profile"].items()}
    require(candidate == advertised, "reference profile equals published result profile")
    delta = Counter(candidate)
    delta.subtract(base)
    delta = Counter({r: n for r, n in delta.items() if n})
    require(delta == Counter({1: 1, 7: -7, 16: 3}), "exact advertised profile delta")
    require(sum(r*n for r, n in delta.items()) == 0, "rank mass conserved")
    require(sum(delta.values()) == -3, "three zero-rank child calls removed")
    require(sum(r*n for r, n in candidate.items()) == 1041408, "candidate rank mass")
    require(M*W - sum(r*n for r, n in candidate.items()) == 5120, "candidate deficit")
    require(ref["result"]["live"] == W and ref["result"]["rank_mass"] == 1041408 and
            ref["result"]["deficit"] == 5120, "published capacity receipt")

    base_primary_rows = [x for x in selected["moments"] if x["side"] == "complex"]
    candidate_primary_rows = [x for x in ref["complex_moments"]]
    base_primary = verify_bracket(base, base_primary_rows, False, "base complex")
    candidate_primary = verify_bracket(candidate, candidate_primary_rows, False, "candidate complex")
    base_conservative_rows = [x for x in selected["conservative_moments"]
                              if x["side"] == "conservative_complex"]
    candidate_conservative_rows = ref["conservative_complex_moments"]
    base_conservative = verify_bracket(base, base_conservative_rows, True, "base conservative complex")
    candidate_conservative = verify_bracket(candidate, candidate_conservative_rows, True,
                                            "candidate conservative complex")

    # Both endpoint intervals move strictly upward, including the reserved envelope.
    require(F(candidate_primary[0]["endpoint"]) > F(base_primary[1]["endpoint"]),
            "candidate primary lower root exceeds base upper root")
    require(F(candidate_conservative[0]["endpoint"]) > F(base_conservative[1]["endpoint"]),
            "candidate conservative lower root exceeds base upper root")

    result = ref["result"]
    require(result["complex_lower"] == candidate_primary[0]["endpoint"], "primary endpoint receipt")
    require(result["conservative_complex_lower"] == candidate_conservative[0]["endpoint"],
            "conservative endpoint receipt")
    bit = F(result["bit_lower"])
    candidate_a = F(result["complex_lower"])
    conservative_a = F(result["conservative_complex_lower"])
    require(result["bit_lower"] == selected["bit_lower"], "candidate retains selected bit endpoint")
    require(bit == F(selected["bit_lower"]), "unchanged selected bit supplier value")
    require(F(candidate_primary[1]["endpoint"]) < bit, "complex bracket is below unchanged bit endpoint")
    require(F(candidate_conservative[1]["endpoint"]) < bit,
            "conservative complex bracket is below unchanged bit endpoint")

    k_primary = floor_grid(candidate_a/(1+candidate_a), 10**18)
    k_conservative = floor_grid(conservative_a/(1+conservative_a), 10**18)
    base_k = F(selected["kappa"])
    require(k_primary == F(result["kappa"]), "primary complex-to-kappa grid")
    require(k_conservative == F(result["conservative_kappa"]), "conservative complex-to-kappa grid")
    require(F(result["baseline_kappa"]) == base_k, "published baseline kappa")
    require(F(result["delta"]) == k_primary-base_k, "published exact kappa delta")

    controls = []
    wrong = Counter(candidate)
    wrong[16] += 1
    controls.append(must_reject(lambda: require(wrong == advertised,
                                                "reference profile equality"),
                                "added rank-16 child"))
    wrong_labels = [dict(row) for row in candidate_primary_rows]
    for row in wrong_labels:
        row["accept"] = not row["accept"]
    controls.append(must_reject(lambda: verify_bracket(candidate, wrong_labels,
                                                       False, "mutated endpoint labels"),
                                "swap accepted/rejected endpoint labels"))
    controls.append(must_reject(lambda: require(floor_grid(candidate_a/(1+candidate_a), 10**18)
                                                == k_primary+F(1,10**18), "bad kappa grid"),
                                "one-grid-unit kappa mutation"))
    controls.append(must_reject(lambda: require(moment_interval(candidate,
                        F(candidate_conservative[1]["endpoint"]), False)[0] > 1,
                        "missing inherited envelope"), "omit conservative surcharge"))

    output = {
        "status": "PASS_PR1407_COMPLEX_PROFILE_ARITHMETIC_INDEPENDENT_AUDIT",
        "base_commit": "bce54fb3f895cbe5cd4c0eb477c3afeed100190f",
        "external_head": ref["source"]["head"],
        "external_source_sha256": {x["name"]: x["sha256"] for x in ref["source"]["files"]},
        "profile_delta": dict(sorted(delta.items())),
        "rank_mass_delta": 0,
        "call_delta": -3,
        "base_primary_bracket": base_primary,
        "candidate_primary_bracket": candidate_primary,
        "base_conservative_bracket": base_conservative,
        "candidate_conservative_bracket": candidate_conservative,
        "bit_endpoint_unchanged": str(bit),
        "primary_kappa_grid": str(k_primary),
        "conservative_kappa_grid": str(k_conservative),
        "exact_kappa_gain": str(k_primary-base_k),
        "interval_method": f"standard-library Fraction; {LOG_TERMS}-term binary-reduced atanh logarithm bounds and {EXP_TERMS}-term positive Taylor exponential with geometric tail",
        "failure_controls": controls,
        "construction_scope": "Arithmetic only; no owner/window/path, native compiler, controller, all-47-outer-constraint or full ancestry replay."
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
