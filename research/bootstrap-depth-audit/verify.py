#!/usr/bin/env python3
"""Exact, scoped PR387 bootstrap-depth audit. Standard library only.

Isaac Grannis (@BagMan9), with substantial OpenAI Codex assistance.
Apache-2.0. Predecessor sources are data: no predecessor code is imported.
"""

import argparse
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
HEAD = "d9fb9410b1ae6f6ada376a1e7fd12bc176e476ea"
INITIAL = F(384599, 10**10)
TARGET = F(199726931618167, 2 * 10**17)
GRID = F(1, 10**18)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(relative):
    return json.loads((ROOT / relative).read_text())


def check_source(data, record):
    require(hashlib.sha256(data).hexdigest() == record["sha256"], "source SHA256")
    blob = b"blob " + str(len(data)).encode() + b"\0" + data
    require(hashlib.sha1(blob).hexdigest() == record["git_blob"], "source Git blob")


def pins():
    source = load("SOURCE.json")
    require(source["base_commit"] == BASE, "base pin")
    require(source["audited_head"] == HEAD, "PR387 head pin")
    for name, record in source["files"].items():
        check_source((ROOT / name).read_bytes(), record)
    return source


def step(s, a):
    return s * (1 - s + a)


def chain(initial, schedule):
    result = [initial]
    for s in schedule:
        result.append(step(s, result[-1]))
    return result


def cap_integer(initial, upper, depth):
    """Unreduced integer closed form; independent of Fraction recurrence.

    Return numerator/denominator of A_depth/(1+A_depth), where
    A_depth = u - u**depth * (u-a0).
    """
    a, b = initial.numerator, initial.denominator
    p, q = upper.numerator, upper.denominator
    n = b * p * q**depth - p**depth * (b * p - a * q)
    d = b * q ** (depth + 1)
    return n, d + n


def compact_margin(a, eta):
    require(0 < eta < F(1, 2), "positive assembly slack")
    q = a * (1 - 2 * eta)
    return (1 - eta) * q / (1 + q)


def strict_grid(numerator, denominator, scale=10**18):
    """Largest scale-grid point strictly below a rational number."""
    require(denominator > 0, "positive grid denominator")
    return (scale * numerator - 1) // denominator


def separated(n, d, target):
    gap_numerator = target.numerator * d - target.denominator * n
    require(d > 0 and gap_numerator > 0, "depth ceiling does not exclude target")
    return gap_numerator


def controls(source, hi, witness, params):
    rejected = []

    def reject(name, operation, reason):
        try:
            operation()
        except ValueError as exc:
            require(str(exc) == reason, "unexpected rejection: " + name)
            rejected.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    n5, d5 = cap_integer(INITIAL, hi, 5)
    n6, d6 = cap_integer(INITIAL, hi, 6)
    reject("one_grid_lower_is_not_excluded_at_depth_five",
           lambda: separated(n5, d5, TARGET - GRID),
           "depth ceiling does not exclude target")
    reject("depth_six_is_not_excluded",
           lambda: separated(n6, d6, TARGET),
           "depth ceiling does not exclude target")
    improved_n, improved_d = cap_integer(F(3, 5000), hi, 5)
    reject("stronger_initial_supplier_escapes_five_round_ceiling",
           lambda: separated(improved_n, improved_d, TARGET),
           "depth ceiling does not exclude target")
    wrong = INITIAL
    for _ in range(5):
        wrong = hi * (1 + wrong)  # Deletes the paid s**2 term.
    reject("unpaid_square_term",
           lambda: require(wrong / (1 + wrong) == F(n5, d5), "recurrence identity"),
           "recurrence identity")
    reject("off_by_one_closed_form",
           lambda: require(F(n6, d6) == F(n5, d5), "recurrence identity"),
           "recurrence identity")
    reject("zero_assembly_slack", lambda: compact_margin(F(witness["bootstrap_chain"][-1]), F(0)),
           "positive assembly slack")
    margin = compact_margin(F(witness["bootstrap_chain"][-1]), F(params["eta"]))
    reject("next_grid_not_reached_by_witness",
           lambda: require(margin > TARGET + GRID, "witness below target"),
           "witness below target")
    # At exact equality, plain floor would wrongly admit the endpoint.
    reject("nonstrict_grid_rounding",
           lambda: require(strict_grid(3, 10, 10) == 3, "strict grid boundary"),
           "strict grid boundary")
    name, record = next(iter(source["files"].items()))
    reject("changed_source_byte",
           lambda: check_source((ROOT / name).read_bytes() + b" ", record),
           "source SHA256")
    return rejected


def verify():
    source = pins()
    precision = load("sources/pr387/EXPECTED-COARSE-PRECISION.json")
    params = load("sources/pr387/PARAMETERS.json")
    witness = load("sources/pr387/EXPECTED-WITNESS.json")
    lo, hi = F(precision["coarse_lower"]), F(precision["coarse_upper"])
    require(0 <= INITIAL < lo < hi < F(1, 32), "envelope domain")
    require(hi - lo == F(1, 10**24), "root interval width")
    # Receipt consistency only: these signs do NOT reprove the moment bracket.
    for engine in ("first", "second"):
        require(F(precision[engine + "_engine_lower_residual_upper"]) < 0,
                "inherited lower residual sign")
        require(F(precision[engine + "_engine_upper_residual_lower"]) > 0,
                "inherited upper residual sign")
    require(F(witness["complex_coarse"]) == lo, "coarse binding")
    require(F(witness["kappa"]) == TARGET, "target binding")
    require(witness["bootstrap_rounds"] == params["bootstrap_rounds"] == 6, "depth binding")
    eta, beta, backoff = (F(params[k]) for k in ("eta", "beta", "saving_backoff"))
    require(0 < beta < 1 and backoff > 0, "positive supplier slack")
    saving = (1 - beta) * lo - backoff
    require(INITIAL < saving < lo < F(witness["bit_coarse"]), "published saving domain")
    require(saving == F(witness["degraded_bit_saving"]), "saving binding")
    actual = chain(INITIAL, [saving] * 6)
    require(actual == list(map(F, witness["bootstrap_chain"])), "published recurrence chain")
    for j in range(1, 7):
        a, old = actual[j], actual[j - 1]
        require(old < a < saving < 1 - a, "completed recurrence gaps")
        require(1 - a - saving * (1 - old) > 0, "remainder gap")
    margin = compact_margin(actual[-1], eta)
    require(margin == F(witness["minimum_margin"]), "compact margin binding")
    require(margin > TARGET, "witness below target")
    require(F(witness["absorption_gap"]) == margin - TARGET, "witness gap binding")

    optimistic = chain(INITIAL, [hi] * 6)
    rows = []
    for j, ordinary in enumerate(optimistic):
        n, d = cap_integer(INITIAL, hi, j)
        require(F(n, d) == ordinary / (1 + ordinary), "independent cap identity")
        if j <= 5:
            separated(n, d, TARGET)
        rows.append({"depth": j, "largest_strict_1e18_grid_numerator": strict_grid(n, d)})
    n5, d5 = cap_integer(INITIAL, hi, 5)
    exclusion = separated(n5, d5, TARGET)
    five = F(n5, d5)
    six = F(*cap_integer(INITIAL, hi, 6))
    threshold = hi - (hi - TARGET / (1 - TARGET)) / hi**5
    require(F(586993, 10**9) < threshold < F(586994, 10**9), "base threshold enclosure")
    require(F(546434, 10**6) < (TARGET - five) / GRID < F(546435, 10**6),
            "five-round gap enclosure")
    require(F(406, 1000) < (margin - TARGET) / GRID < F(407, 1000),
            "six-round witness gap enclosure")
    rejected = controls(source, hi, witness, params)
    return {
        "status": "PASS_SCOPED_BOOTSTRAP_DEPTH_AUDIT",
        "base_commit": BASE,
        "audited_head": HEAD,
        "assignment_seed": 73,
        "initial_ordinary_saving": str(INITIAL),
        "inherited_coarse_interval": [str(lo), str(hi)],
        "target_kappa": str(TARGET),
        "optimistic_depth_grid_caps": rows,
        "five_round_outer_cap": str(five),
        "five_round_exclusion_cross_product": str(exclusion),
        "five_round_gap_in_1e18_grid_units": str((TARGET - five) / GRID),
        "six_round_optimistic_outer_cap": str(six),
        "six_round_published_margin": str(margin),
        "six_round_published_gap_in_1e18_grid_units": str((margin - TARGET) / GRID),
        "five_round_initial_saving_threshold_at_upper_endpoint": str(threshold),
        "negative_controls_rejected": rejected,
        "scope": "Ceiling for the retained recurrence accounting with independently variable per-level savings, fixed initial supplier and inherited coarse-root upper bound. Six-round compact margin replay only; no supplier replay or full assembly/multiplication proof.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", type=Path, help="Compare the full deterministic receipt")
    group.add_argument("--output", type=Path, help="Write a new receipt; never overwrite")
    args = parser.parse_args()
    result = verify()
    if args.check:
        require(result == json.loads(args.check.read_text()), "receipt mismatch")
    if args.output:
        with args.output.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print(result["status"] + "; depths 0..5 excluded; six-round margin admitted; "
          + str(len(result["negative_controls_rejected"])) + " controls rejected")


if __name__ == "__main__":
    main()
