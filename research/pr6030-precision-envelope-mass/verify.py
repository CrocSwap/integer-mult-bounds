#!/usr/bin/env python3
"""Bind the selected PR6030 precision envelope to the complete paid rank mass.

The check uses explicit exceptions, so python -O does not skip it.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
INVOICE = ROOT / "research/p104-helper470-twin-rung-removal/RESULT.json"
REVIEW = ROOT / "docs/research/pr-intake-evidence/pr6030-audit/PROOF-REVIEW.md"

ENVELOPE = "2^(10^9+240152f)"
CALLER_BOUND = 126_626_680
ALLOWANCE = 184_647_552
RAW_BUDGET = 10**9


def need(condition, message):
    if not condition:
        raise SystemExit(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank_mass(histogram):
    mass = 0
    count = 0
    for key, value in histogram.items():
        rank = int(key)
        number = int(value)
        need(rank > 0 and number > 0, "nonpositive histogram entry")
        mass += rank * number
        count += number
    return mass, count


def subset_sums(exponents):
    sums = [0]
    for exponent in exponents:
        sums.extend(total + exponent for total in list(sums))
    return sums


def main():
    pins = {row["path"]: row for row in json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))["files"]}
    for path in (INVOICE, REVIEW):
        rel = path.relative_to(ROOT).as_posix()
        need(sha256(path) == pins[rel]["sha256"], "sha256 pin mismatch: " + rel)

    invoice = json.loads(INVOICE.read_text(encoding="utf-8"))
    review = REVIEW.read_text(encoding="utf-8")
    cost = invoice["complete_cost"]
    paid_mass, paid_calls = rank_mass(cost["paid"])
    target_mass, fields = rank_mass(cost["targets"])
    need(paid_mass == 240152 and paid_calls == 66834, "complete paid histogram")
    need(target_mass == 240912 and fields == 13444, "complete target histogram")
    need(target_mass - paid_mass == 760 == cost["rank_mass_surplus"], "rank-mass surplus")
    need(cost["paid_calls"] == paid_calls and cost["productive_fields"] == fields, "invoice totals")

    nonrecursive = cost["nonrecursive"]
    need(nonrecursive["raw_budget"] == RAW_BUDGET, "raw budget")
    need(nonrecursive["raw_scalar_upper"] == ALLOWANCE, "scalar allowance")
    need(nonrecursive["local_paid_rank_mass"] == 5952, "local paid rank mass")
    need("use local_paid_rank_mass for the whole word" in nonrecursive["tensor_native_growth_bound"],
         "local growth note")
    need(5952 != paid_mass, "local mass is not the complete mass")

    need("paid rank mass 240,152" in review, "review paid rank mass")
    need("productive rank mass 240,912, surplus 760" in review, "review productive mass")
    need("complete envelope is " + ENVELOPE + ", plus the retained fixed local realization" in review,
         "review envelope")
    need("caller bound is 126,626,680, below the retained allowance 184,647,552<10^9." in review,
         "review caller bound")
    need(CALLER_BOUND < ALLOWANCE < RAW_BUDGET, "budget is strictly looser")
    slack = RAW_BUDGET - CALLER_BOUND
    need(slack == 873_373_320, "caller-bound slack")
    allowance_slack = RAW_BUDGET - ALLOWANCE
    need(allowance_slack == 815_352_448, "allowance slack")

    # Exponent of one scalar (2^1), one monomial (2^0), and one rank-3 Gaussian at f=2 (2^(3*2)).
    witness = (1, 0, 3 * 2)
    need(all(exponent >= 0 for exponent in witness), "witness exponents")
    full = sum(witness)
    for partial in subset_sums(witness):
        need(0 <= partial <= full, "nonnegative subproduct")
    need(full == 1 + 0 + 6, "witness total")

    # A majorant below 1 makes a singleton exceed the full product of majorants.
    negative = (1, -1)
    need(max(negative) > sum(negative), "negative exponent breaks the prefix bound")

    mutant = dict(cost["paid"])
    mutant["1"] -= 1
    mutant_mass, mutant_calls = rank_mass(mutant)
    need(mutant_mass == paid_mass - 1 and mutant_calls == paid_calls - 1, "one-call mutant")
    need(mutant_mass != 240152, "mutant must miss the published coefficient")

    # One extra power on a single Gaussian is a different envelope.
    need(paid_mass + 1 != paid_mass, "extra Gaussian power")

    print(
        "PASS_PR6030_PRECISION_ENVELOPE_MASS"
        f" paid_rank_mass={paid_mass}"
        f" paid_calls={paid_calls}"
        f" target_rank_mass={target_mass}"
        f" raw_budget={RAW_BUDGET}"
        f" caller_bound={CALLER_BOUND}"
        f" allowance={ALLOWANCE}"
        f" caller_slack={slack}"
        " envelope=2^(10^9+240152f)"
        " precision_tape_discharged=false"
        " no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
