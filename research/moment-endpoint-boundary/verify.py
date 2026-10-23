#!/usr/bin/env python3
"""Exact rational audit of the PR3576 moment acceptance boundary."""

from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re


P = Path(__file__).resolve().parent
ROOT = P.parents[1]
SCALE = 10**30
HEAD = "1630afea0fc1083717b5b2799b8de7a819a6ea02"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def floor_scaled(value, scale):
    return value.numerator * scale // value.denominator


def ceil_scaled(value, scale):
    return -((-value.numerator * scale) // value.denominator)


def below_one(interval):
    return interval[1] < 1


def above_one(interval):
    return interval[0] > 1


def main():
    ext = json.loads((P / "EXTERNAL-SOURCES.json").read_bytes())
    need(ext["pull_request"] == 3576 and ext["head_commit"] == HEAD
         and ext["base_commit"] == "20ecf2891d80b5acf18f980b2164fb44ea7faa90",
         "pinned PR3576 head")
    rows = {
        row["source_path"]: {key: row[key] for key in ("local_path", "git_blob", "sha256")}
        for row in ext["files"]
    }
    expected_sources = {
        "research/t74-retuned-ordinary-layer/PROOF.md": {
            "local_path": "inputs/PR3576-PROOF.md",
            "git_blob": "055c093ffd09b38eebb78e50e179909f007e25f4",
            "sha256": "e393df9aaf1a2a1027377cf30e27ea16255d4d2fbefffeef0857f31a64ba7378",
        },
        "research/t74-retuned-ordinary-layer/rate.py": {
            "local_path": "inputs/PR3576-rate.py",
            "git_blob": "99983e724d5faa0828d6508bba18b43f3774881c",
            "sha256": "a66e97da03752c72ffabe57048eab80b0fbe00b0d4c4b5a0c7debca845b81d53",
        },
    }
    need(rows == expected_sources, "exact PR3576 source paths and content pins")
    inputs = {}
    for source_path, row in rows.items():
        data = (P / row["local_path"]).read_bytes()
        need(sha256(data) == row["sha256"], "source SHA256: " + source_path)
        need(git_blob(data) == row["git_blob"], "source Git blob: " + source_path)
        inputs[source_path] = data

    proof = inputs["research/t74-retuned-ordinary-layer/PROOF.md"].decode("utf-8")
    rate = inputs["research/t74-retuned-ordinary-layer/rate.py"].decode("utf-8")
    profile_path = "research/rank7-joint-endframes/allocation/PROFILE.json"
    order_path = "research/rank7-joint-endframes/allocation/ORDER.json"
    profile_hash = sha256((ROOT / profile_path).read_bytes())
    order_hash = sha256((ROOT / order_path).read_bytes())
    need(profile_hash == "94a819747f3ced41f1544ada0036c983fc0c92847b9644380f877a06cd7931cf",
         "#2979 paid profile source pin")
    need(order_hash == "519d1d5dbb997a219fcfcad34c0b03e7838bef24199784d7e964fa10090f66e1",
         "#2979 T74 call order source pin")
    for source_path, digest in ((profile_path, profile_hash), (order_path, order_hash)):
        need(source_path in rate and digest in rate, "PR3576 rate.py authenticates " + source_path)

    source_contract = (
        'need(all(upper < 1 for _lower, upper in moments), "complete T74 moment passes")',
        'need(all(lower > 1 for lower, _upper in naive),',
        'need(all(lower > 1 for lower, _upper in extra),',
        "lower=lower.numerator * scale // lower.denominator",
        "upper=-((-upper.numerator * scale) // upper.denominator)",
    )
    need(all(fragment in rate for fragment in source_contract),
         "pinned source uses strict endpoint directions and outward rounding")

    numerators = re.findall(r"\[(\d+)\s*,\s*(\d+)\]\s*/\s*10\^30", proof)
    expected = [
        ("999999903535664027556833879161", "999999903535664027556833879162"),
        ("1000003022093731739239177793276", "1000003022093731739239177793277"),
        ("1000000111677363244276477808366", "1000000111677363244276477808367"),
    ]
    need(numerators == expected, "three exact 30-place intervals from pinned proof")
    intervals = [tuple(F(int(endpoint), SCALE) for endpoint in pair) for pair in numerators]
    sigma, tau, extra = intervals
    need(all(lo <= hi and hi - lo == F(1, SCALE) for lo, hi in intervals),
         "adjacent, ordered rational endpoints")

    need(below_one(sigma), "sigma moment upper endpoint is strictly below one")
    sigma_gap = 1 - sigma[1]
    promised_gap = F(9, 10**8)
    need(sigma_gap > promised_gap, "sigma interval clears the strict 9e-8 gap")
    need(above_one(tau), "ordinary-exponent lower endpoint is strictly above one")
    need(above_one(extra), "extra-rank-one lower endpoint is strictly above one")

    # Equality and straddling canaries catch non-strict and wrong-endpoint tests.
    equality = (F(1), F(1))
    straddling = (F(SCALE - 1, SCALE), F(SCALE + 1, SCALE))
    need(not below_one(equality) and not above_one(equality), "strict equality boundary rejects")
    need(not below_one(straddling) and not above_one(straddling),
         "correct endpoint tests reject an interval straddling one")
    need(straddling[0] < 1 and straddling[1] > 1,
         "wrong-endpoint mutants would accept the straddling canary")
    need(not below_one((sigma[0], F(1))), "sigma upper corruption to equality rejects")
    need(not above_one((F(1), tau[1])), "tau lower corruption to equality rejects")
    need(not above_one((F(1), extra[1])), "extra rank-one lower corruption to equality rejects")

    # Exercise outward floor/ceiling one third of a decimal ulp from one.
    near_below = 1 - F(1, 3 * SCALE)
    near_above = 1 + F(1, 3 * SCALE)
    low_below, high_below = floor_scaled(near_below, SCALE), ceil_scaled(near_below, SCALE)
    low_above, high_above = floor_scaled(near_above, SCALE), ceil_scaled(near_above, SCALE)
    need((low_below, high_below) == (SCALE - 1, SCALE), "outward rounding below one")
    need((low_above, high_above) == (SCALE, SCALE + 1), "outward rounding above one")
    need(F(low_below, SCALE) <= near_below <= F(high_below, SCALE),
         "lower/upper rounding encloses below-one rational")
    need(F(low_above, SCALE) <= near_above <= F(high_above, SCALE),
         "lower/upper rounding encloses above-one rational")
    need(F(ceil_scaled(near_below, SCALE), SCALE) > near_below,
         "upward-rounded lower-end mutant is inward")
    need(F(floor_scaled(near_above, SCALE), SCALE) < near_above,
         "downward-rounded upper-end mutant is inward")

    result = {
        "status": "PASS_EXACT_MOMENT_ENDPOINT_ACCEPTANCE",
        "source_head": HEAD,
        "intervals_over_1e30": [list(pair) for pair in numerators],
        "sigma_gap": str(sigma_gap),
        "sigma_excess_over_9e-8": str(sigma_gap - promised_gap),
        "tau_lower_excess_over_one": str(tau[0] - 1),
        "extra_rank1_lower_excess_over_one": str(extra[0] - 1),
        "controls": {
            "strict_equality_rejected": True,
            "wrong_endpoint_direction_canary": True,
            "sigma_upper_corruption_to_one_rejected": True,
            "tau_lower_corruption_to_one_rejected": True,
            "extra_lower_corruption_to_one_rejected": True,
            "outward_rounding_ulp_canaries": True,
            "inward_rounding_mutants_detected": True,
        },
        "scope": "Checks exact consumption and outward rounding of the published intervals; does not rederive either moment enclosure.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
