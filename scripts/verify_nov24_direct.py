"""Check pinned sources and the exact parameters of a multiplication corollary.

This checks source integrity and necessary scalar inequalities. It does not
generate the finite templates, execute a multiplier, or check the Lean proof.
"""
import argparse
from fractions import Fraction
from hashlib import sha1, sha256
import json
from math import isqrt
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/nov24-direct-multiplication"
COMMIT = "92b516ef8e2abf66c3db7aa31438d3010bc7956f"
THEOREM = "OAI.Computability.NearSquareRoot.uniformIntegerMultiplication"
LIMIT = Fraction(1, 2)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def specialize(kappa):
    if not 0 < kappa < LIMIT:
        raise ValueError("A fixed positive saving strictly below 1/2 is required")
    gap = LIMIT - kappa
    eventual = LIMIT + gap / 2
    target = 1 - kappa
    require(eventual < target, "The excess exponent needs positive slack")
    return {"kappa": str(kappa), "eventual_log_exponent": str(eventual),
            "target_log_exponent": str(target)}


def check_construction(parameters, kappa):
    """Check the explicit outer choices, not the ungenerated finite templates."""
    require(parameters["schema"] == "nov24-explicit-outer-parameters/1",
            "Wrong construction-parameter schema")
    index = parameters["scheduler_index"]
    prime = parameters["interchange_label_prime"]
    require(type(index) is int and index >= 1, "Positive integer scheduler index")
    require(type(prime) is int and prime > 2 and prime % 2 == 1 and
            all(prime % divisor for divisor in range(3, isqrt(prime) + 1, 2)),
            "Odd interchange label prime required")
    theta = Fraction(parameters["candidate_log_exponent"])
    rho = Fraction(parameters["fourier_log_exponent"])
    gamma = Fraction(parameters["interchange_intermediate_exponent"])
    require(theta == LIMIT + Fraction(1, index + 2), "Scheduler exponent")
    require(LIMIT < gamma < rho < min(Fraction(1), theta) and theta < 1 - kappa,
            "Strict construction exponent ordering")
    margin = gamma - LIMIT - Fraction(3 * prime - 1, prime * prime)
    require(margin > 0 and
            margin == Fraction(parameters["interchange_label_margin"]),
            "Interchange label exponent margin")
    require(parameters["finite_templates_materialized"] is False and
            parameters["multiplier_executed"] is False,
            "Scalar checks do not materialize or execute the construction")
    return parameters


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kappa", type=Fraction, help="also check a fixed rational witness")
    args = parser.parse_args()
    record = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
    check = run_path(str(ROOT / "scripts/verify_selected_result.py"))["check"]
    selected = check(record, ROOT)
    claim = json.loads((ROOT / record["certificate"]).read_bytes())
    upstream = json.loads((PACKAGE / "UPSTREAM.json").read_bytes())
    require(upstream["commit"] == record["audited_source_head"] == COMMIT, "Source revision")
    require(sha256((PACKAGE / "UPSTREAM.json").read_bytes()).hexdigest() ==
            "385a07bd42952d5452cb057da2acbf0e4952a8cd74b8f6ebf0d1197c4605226e", "Release inventory differs from the checked revision")
    for name, pin in upstream["files"].items():
        raw = (PACKAGE / "source" / name).read_bytes()
        oid = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(sha256(raw).hexdigest() == pin["sha256"] and oid == pin["git_blob"],
                f"Upstream file changed: {name}")
    comparator = json.loads((PACKAGE / "source/NearSquareRootMultiplication.json").read_bytes())
    require(THEOREM in comparator["theorem_names"] and
            comparator["solution_module"] == "OAI.Computability.NearSquareRoot.Main",
            "Wrong upstream comparator binding")
    require(claim["upstream_theorem"] == THEOREM and claim["schema"] == "direct-multiplier-corollary/1",
            "Wrong selected theorem")
    require(claim["supported_savings"] == {"lower_exclusive": "0", "upper_exclusive": "1/2"} and
            record["supported_savings"] == claim["supported_savings"], "Strict family endpoint")
    require(claim["uniform_in_input_length"] is True and record["assumptions"] == [],
            "The cited upper theorem uses one machine without a complexity hypothesis")
    require(selected == Fraction(4999, 10000) and claim["witness"] == specialize(selected),
            "Selected specialization")
    check_construction(claim["construction"], selected)
    for excluded in (LIMIT, LIMIT + Fraction(1, 10000)):
        try:
            specialize(excluded)
        except ValueError:
            continue
        raise ValueError("Accepted a witness outside the upper theorem")
    if args.kappa is not None:
        try:
            other = specialize(args.kappa)
        except ValueError as exc:
            parser.error(str(exc))
    print("PASS_NOV24_DIRECT_COROLLARY", json.dumps(specialize(selected), sort_keys=True))
    print("PASS_NOV24_CONSTRUCTION_PARAMETERS", json.dumps(claim["construction"], sort_keys=True))
    print("One multiplier for every fixed 0 < kappa < 1/2. Endpoint attainment open.")
    if args.kappa is not None:
        print(json.dumps(other, sort_keys=True))


if __name__ == "__main__":
    main()
