#!/usr/bin/env python3
"""Verify the PR1154 aggregate-profile packing relaxation. Apache-2.0."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "research/adaptive-kernel-demotion"
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
import ceiling as C  # noqa: E402

M, FAMILIES, STAGES, CENTRE = 73, 896, 9, 64
GRID = Q(1, 10**15)
SELECTED_RECORD_SHA256 = "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129"
CEILING_SHA256 = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
SOURCE_HEAD = "342b67f23dfa8f41a520a0d58978b2875e9eb0dd"
MANIFEST_INPUTS = (
    "expected/OWNER-AUDIT.json",
    "expected/EXACT-PRICE.json",
    "data/SOURCE-BINDING.json",
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def json_file(path):
    return json.loads(path.read_text())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def derive_local(full, idle, calls, live):
    R = C.max_idle_rank(M)
    require(calls > 0 and live > 0, "positive calls and live stock")
    require(all(r > 0 and n >= 0 for r, n in full.items()), "complete profile domain")
    require(all(r > 0 and n >= 0 for r, n in idle.items()), "idle profile domain")
    require(all(r <= R for r in idle), "idle rank exceeds halving guard")
    require(all(idle.get(r, 0) <= n for r, n in full.items()), "idle profile not contained in complete profile")
    require(all(r in full for r in idle), "idle rank absent from complete profile")
    expected_mass = (M - 1) * live + CENTRE * calls
    observed_mass = sum(r * n for r, n in full.items())
    require(observed_mass == expected_mass, "complete profile violates coverage identity")
    local_counts = {r: n - idle.get(r, 0) for r, n in full.items()}
    require(sum(r * n for r, n in local_counts.items()) + sum(r * n for r, n in idle.items()) == expected_mass,
            "local and idle rank mass do not reconstruct complete profile")
    return {r: Q(n, calls) for r, n in local_counts.items() if n}


def expect_reject(fn, label):
    try:
        fn()
    except ValueError:
        return "rejected"
    raise ValueError("failure control accepted: " + label)


def decimal(q, digits=18):
    q = Q(q)
    scale = 10**digits
    n = (abs(q.numerator) * scale) // q.denominator
    sign = "-" if q < 0 else ""
    return f"{sign}{n // scale}.{n % scale:0{digits}d}"


def main():
    selected_raw = (ROOT / "certificates/selected-result.json").read_bytes()
    record = json.loads(selected_raw)
    require(sha256(selected_raw).hexdigest() == SELECTED_RECORD_SHA256, "selected record pin changed")
    certificate_path = ROOT / record["certificate"]
    require(digest(certificate_path) == record["certificate_sha256"], "selected certificate hash changed")
    selected_certificate = json_file(certificate_path)
    bit_saving = Q(selected_certificate["bit_lower"])

    require(digest(ROOT / "research/complex-local-word-ceiling/ceiling.py") == CEILING_SHA256,
            "ceiling module pin changed")
    manifest = json_file(SOURCE / "MANIFEST.json")
    for rel in MANIFEST_INPUTS:
        require(rel in manifest and digest(SOURCE / rel) == manifest[rel],
                "PR1154 manifest mismatch: " + rel)
    binding = json_file(SOURCE / "data/SOURCE-BINDING.json")
    require(binding["source_head"] == SOURCE_HEAD, "PR1154 source head changed")
    for rel, expected in binding["files"].items():
        require(digest(SOURCE / "data" / rel) == expected, "PR1154 source binding mismatch: " + rel)

    owner = json_file(SOURCE / "expected/OWNER-AUDIT.json")
    price = json_file(SOURCE / "expected/EXACT-PRICE.json")
    full = {int(r): int(n) for r, n in owner["profile"].items()}
    priced_full = {int(r): int(n) for r, n in price["profile"].items()}
    idle = {int(r): int(n) for r, n in owner["idle_profile"].items()}
    require(full == priced_full, "owner audit and exact-price profiles differ")
    calls = int(owner["calls"])
    live_fraction = Q(FAMILIES * calls, STAGES)
    require(live_fraction.denominator == 1, "source call count gives nonintegral live stock")
    live = live_fraction.numerator
    require(live == 14336, "unexpected PR1154 live stock")
    require(int(owner["idle_remainders"]) == sum(idle.values()) == 6034,
            "idle remainder count mismatch")
    require(sum(r * n for r, n in full.items()) == int(owner["rank_mass"]),
            "owner-audit rank mass mismatch")
    require(int(owner["deficit"]) == M * live - sum(r * n for r, n in full.items()),
            "recorded deficit mismatch")

    local = derive_local(full, idle, calls, live)
    q = C.model(local, M, FAMILIES, STAGES, CENTRE)
    require(q["R"] == 51, "unexpected halving-guard rank cap")
    lo, hi = C.ceiling(local, M, FAMILIES, STAGES, CENTRE, grid=GRID)
    lower_value = C.relax(local, M, FAMILIES, STAGES, CENTRE, lo)[1]
    upper_value = C.relax(local, M, FAMILIES, STAGES, CENTRE, hi)[0]
    require(lower_value < 1 < upper_value, "exact root bracket does not straddle one")

    candidate_a = Q(price["complex_lower"])
    candidate_kappa = Q(price["kappa"])
    kappa_cap = hi / (1 + hi)
    required_a = candidate_kappa / (1 - candidate_kappa)
    require(candidate_a < lo, "candidate complex saving not below relaxation root")
    require(candidate_kappa <= candidate_a / (1 + candidate_a),
            "candidate kappa is not covered by its complex saving")
    require(bit_saving > required_a, "bit-side saving does not clear candidate kappa")
    require(candidate_kappa < kappa_cap, "candidate kappa exceeds packing cap")

    bad_full = dict(full)
    bad_full[1] += 1
    controls = {
        "one_rank_unit_added_to_complete_profile": expect_reject(
            lambda: derive_local(bad_full, idle, calls, live), "coverage mass"),
        "idle_rank_52": expect_reject(
            lambda: derive_local(full, {**idle, 52: 1}, calls, live), "halving guard"),
        "local_profile_mass_over_coverage": expect_reject(
            lambda: C.model({1: Q(10000)}, M, FAMILIES, STAGES, CENTRE), "local mass"),
    }

    result = {
        "status": "PASS_PR1154_AGGREGATE_PACKING_RELAXATION",
        "source": {
            "task_base": "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
            "pr": 1154,
            "pr_head": "390de2866a03758e7f4ddbb2846e5b2ee4e72154",
            "merge_commit": "998a33b0df8af40aa672c72585c61ad7e1bbe701",
            "supplier_source_head": SOURCE_HEAD,
            "selected_record_sha256": SELECTED_RECORD_SHA256,
            "selected_kappa": record["kappa"],
        },
        "model": {
            "m": M, "families": FAMILIES, "stages": STAGES, "centre": CENTRE,
            "calls": calls, "live_stock": live, "idle_rank_cap": q["R"],
            "coverage_identity": "rank_mass = 72*live_stock + 64*calls",
            "rank_mass": str(sum(r * n for r, n in full.items())),
            "deficit": int(owner["deficit"]),
        },
        "profiles": {
            "complete": {str(r): full[r] for r in sorted(full)},
            "idle": {str(r): idle[r] for r in sorted(idle)},
            "local_per_call": {str(r): str(local[r]) for r in sorted(local)},
            "local_mass_per_call": str(q["local_mass"]),
            "idle_mass_per_call": str(q["idle_mass"]),
        },
        "packing_cap": {
            "a_lower": str(lo), "a_upper": str(hi),
            "a_upper_decimal": decimal(hi),
            "kappa_upper": str(kappa_cap),
            "kappa_upper_decimal": decimal(kappa_cap),
            "a_root_lower_relaxation": [str(x) for x in C.relax(local, M, FAMILIES, STAGES, CENTRE, lo)],
            "a_root_upper_relaxation": [str(x) for x in C.relax(local, M, FAMILIES, STAGES, CENTRE, hi)],
            "candidate_a_fraction_realized": str(candidate_a / hi),
            "candidate_a_fraction_realized_decimal": decimal(candidate_a / hi),
            "candidate_kappa_fraction_of_cap": str(candidate_kappa / kappa_cap),
            "candidate_kappa_fraction_of_cap_decimal": decimal(candidate_kappa / kappa_cap),
        },
        "supplier_comparison": {
            "candidate_complex_a_lower": str(candidate_a),
            "candidate_kappa": str(candidate_kappa),
            "candidate_kappa_decimal": price["kappa_decimal"],
            "candidate_required_a": str(required_a),
            "selected_bit_a_lower": str(bit_saving),
            "selected_bit_margin_over_candidate_required_a": str(bit_saving - required_a),
            "complex_side_binds_for_this_comparison": True,
        },
        "controls": controls,
        "scope": "Upper bound for all repackings of PR1154's fixed aggregate local profile under the 73-rank, 896-family, nine-stage, centre-64 coverage model and rank-51 halving guard. Fractional idle placement is allowed. Not an attained optimum, supplier admission, or bound for changed words or models.",
        "limits": [
            "The hash-pinned PR1154 owner-audit and exact-price receipts are inputs; their underlying owner/native replay was not independently reproduced.",
            "PR1154 remains partially reviewed and is not a selected supplier.",
            "The selected bit value is source-bound by the selected certificate; the full bit circuit was not replayed in this session.",
        ],
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    out = HERE / "RESULT.json"
    if sys.argv[1:] == ["--write"]:
        out.write_text(encoded)
    else:
        require(out.is_file() and out.read_text() == encoded, "RESULT.json differs; run with --write")
    print(result["status"], "kappa_cap", result["packing_cap"]["kappa_upper_decimal"],
          "fraction_realized", result["packing_cap"]["candidate_kappa_fraction_of_cap_decimal"])


if __name__ == "__main__":
    try:
        main()
    except (KeyError, OSError, TypeError, ValueError) as exc:
        print("FAIL:", exc)
        sys.exit(1)
