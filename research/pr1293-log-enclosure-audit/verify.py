#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound soundness audit of PR1293's logarithm cross-check.

AI-generated contribution by an OpenAI assistant and review subagents.
The pinned subject is Navinor's code; only the oracle/proof checks are ours.
No repository moment engine is imported. See README.md for the analytic scope.
"""
import argparse
import difflib
import hashlib
import json
from fractions import Fraction as Q
from functools import lru_cache
from math import factorial
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORDER, STEPS, ORACLE_TERMS, ORACLE_BITS = 48, 72, 128, 384
OLD = "        else:\n            lo = hi = mid\n            break\n"
UNRESOLVED = "ln_exp_bisection unresolved at current Taylor order"
NEW = ("        else:\n"
       "            # Overlap is not equality; do not report a completed cross-check.\n"
       "            raise ValueError('" + UNRESOLVED + "')\n")
SUBJECT_PATH = "research/selected-suppliers-de-diagnostic/verify.py"
SUBJECT_ID = {
    "repository": "https://github.com/CrocSwap/integer-mult-bounds",
    "pull_request": 1293,
    "head": "85a361233431befe4b11cf878f7b1b77a244d473",
    "path": SUBJECT_PATH,
    "vendored_path": "vendor/pr1293_verify.py",
    "git_blob": "f9a9d5e5103b6ccbadb3f50fea34e25ccfce7ff1",
    "sha256": "e69fc72f0534a8eb9ea8e6c0f83deb1ae6537d2f6bf8e511bca23026b68a270f",
}
SUBJECT_ID["source_url"] = (SUBJECT_ID["repository"] + "/blob/" +
                            SUBJECT_ID["head"] + "/" + SUBJECT_PATH)
INPUT_PINS = {
    "research/community-frontier1094-audit/ASSEMBLY.json":
        "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    "research/community-frontier1094-audit/INDEPENDENT1094.json":
        "301fb8a0e4ab7e3c383ff974c54c08178283b2a3453c5282757f692a3c7a4bfd",
    "research/e8-bit-p111-tuned/tune/EXPECTED.json":
        "b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_json(data):
    def unique_keys(pairs):
        keys = [key for key, _ in pairs]
        require(len(keys) == len(set(keys)), "duplicate JSON key")
        return dict(pairs)
    return json.loads(data, object_pairs_hook=unique_keys)


def validate_subject_bytes(data, metadata):
    require(sha256(data) == metadata["sha256"], "subject SHA256 drift")
    blob = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
    require(blob == metadata["git_blob"], "subject Git blob drift")


def subject_source():
    metadata = load_json((HERE / "SUBJECT.json").read_bytes())
    identity = {key: metadata.get(key) for key in SUBJECT_ID}
    require(canonical(identity) == canonical(SUBJECT_ID), "subject identity drift")
    path = HERE / metadata["vendored_path"]
    require(path.is_file() and not path.is_symlink() and not path.parent.is_symlink()
            and path.resolve().is_relative_to(HERE.resolve()), "subject must be an internal ordinary file")
    data = path.read_bytes()
    validate_subject_bytes(data, metadata)
    source = data.decode("utf-8")
    require(source.count(OLD) == 1, "repair anchor must be unique")
    return source, metadata


def repaired_source(source):
    require(source.count(OLD) == 1, "repair anchor must be unique")
    return source.replace(OLD, NEW, 1)


def repair_diff(source):
    return "".join(difflib.unified_diff(
        source.splitlines(keepends=True),
        repaired_source(source).splitlines(keepends=True),
        fromfile="a/" + SUBJECT_PATH, tofile="b/" + SUBJECT_PATH, n=1))


def load_subject(repaired=False):
    source, _ = subject_source()
    if repaired:
        source = repaired_source(source)
    # Do not call main here. The separate full replay relocates its output and
    # input paths; this audit only calls the original arithmetic functions.
    namespace = {"__name__": "pr1293_audit_subject",
                 "__file__": str(HERE / "vendor/pr1293_verify.py")}
    exec(compile(source, namespace["__file__"], "exec"), namespace)
    require((namespace["CROSS_ORDER"], namespace["CROSS_BITS"]) == (ORDER, STEPS),
            "subject default precision changed")
    return namespace


def check_live_inputs():
    sources = load_json((HERE / "SOURCES.json").read_bytes())
    rows = sources["files"]
    paths = [row["path"] for row in rows]
    require(len(paths) == len(set(paths)), "duplicate source row")
    live = {row["path"]: row for row in rows if row["usage"] == "input"}
    require(set(live) == set(INPUT_PINS), "required live-input inventory mismatch")
    documents = {}
    for name, expected in INPUT_PINS.items():
        require(live[name]["sha256"] == expected, "live input pin drift: " + name)
        data = (ROOT / name).read_bytes()
        require(sha256(data) == expected, "live input drift: " + name)
        documents[name] = load_json(data)  # Parse precisely the checked bytes.
    return dict(INPUT_PINS), documents


def polynomial(point, order):
    """Independent closed finite sum, not the subject's recurrence."""
    require(point >= 0 and type(order) is int and order >= 0, "polynomial domain")
    return sum((point ** j / factorial(j) for j in range(order + 1)), Q(0))


def exponential_upper(point, order):
    """Independent strict Taylor majorant for point > 0, point < order+2."""
    require(point > 0 and point < order + 2, "majorant domain")
    first = point ** (order + 1) / factorial(order + 1)
    return polynomial(point, order) + first / (1 - point / (order + 2))


def counterexample_specs():
    specs = []
    for point in (Q(1, 4), Q(1, 2), Q(3, 4), Q(3, 2), Q(5, 2), Q(7, 2), Q(11, 2)):
        specs.append(("lower-endpoint", point, polynomial(point, ORDER), "below"))
    point = Q(1, 2)
    lower = polynomial(point, ORDER)
    first = point ** (ORDER + 1) / factorial(ORDER + 1)
    upper = exponential_upper(point, ORDER)
    upper_next = exponential_upper(point, ORDER + 1)
    specs += [("interior-below", point, lower + first / 2, "below"),
              ("upper-endpoint", point, upper, "above"),
              ("interior-above", point, (upper + upper_next) / 2, "above")]
    return specs


def atanh_log_bounds(value, terms):
    """Exact ln(value) bounds for 1 <= value <= 2; see README proof."""
    require(1 <= value <= 2 and type(terms) is int and terms >= 1, "oracle domain")
    z = (value - 1) / (value + 1)
    power, total = z, Q(0)
    for j in range(terms):
        total += 2 * power / (2 * j + 1)
        power *= z * z
    tail = 2 * power / ((2 * terms + 1) * (1 - z * z))
    return total, total + tail


def outward_dyadic(lower, upper):
    scale = 1 << ORACLE_BITS
    lo = (lower.numerator * scale) // lower.denominator
    hi = -((-upper.numerator * scale) // upper.denominator)
    return Q(lo, scale), Q(hi, scale)


@lru_cache(maxsize=None)
def log_oracle(value):
    """Independent range-reduced positive atanh series, no subject functions."""
    value = Q(value)
    require(value >= 1, "oracle logarithm domain")
    reduced, power = value, 0
    while reduced >= 2:
        reduced /= 2
        power += 1
    lower, upper = atanh_log_bounds(reduced, ORACLE_TERMS)
    if power:
        lo2, hi2 = atanh_log_bounds(Q(2), ORACLE_TERMS)
        lower += power * lo2
        upper += power * hi2
    return outward_dyadic(lower, upper)


def encloses(outer, inner):
    return outer[0] <= inner[0] <= inner[1] <= outer[1]


def traced_call(namespace, value, repaired=False):
    """Observe actual exp calls, then check their chronological decisions.

    This is a subject trace, NOT the independent mathematical oracle.
    The original ln function and constants are executed without replacement.
    """
    observed = []
    original_exp = namespace["exp_taylor"]

    def observe(point, order):
        bounds = original_exp(point, order)
        observed.append((point, order, *bounds))
        return bounds

    namespace["exp_taylor"] = observe
    caught_unresolved = False
    try:
        try:
            result = namespace["ln_exp_bisection"](value)
        except ValueError as error:
            if not repaired or str(error) != UNRESOLVED:
                raise
            caught_unresolved = True
            result = None
    finally:
        namespace["exp_taylor"] = original_exp
    if value == 1:
        require(not observed and not caught_unresolved and result == (Q(0), Q(0)),
                "unit special case")
        return result, {"bracket_calls": 0, "bisection_steps": 0, "overlap": None}

    lo, hi, index = Q(0), Q(1), 0
    while True:
        point, order, elo, ehi = observed[index]
        index += 1
        require(point == hi and order == ORDER and elo <= ehi, "bracketing trace")
        if elo >= value:
            break
        hi *= 2
    bracket_calls, overlap = index, None
    for step, (point, order, elo, ehi) in enumerate(observed[index:], 1):
        mid = (lo + hi) / 2
        require(point == mid and order == ORDER and elo <= ehi, "bisection trace")
        if ehi < value:
            lo = mid
        elif elo > value:
            hi = mid
        else:
            overlap = {"step": step, "mid": str(mid),
                       "bracket_before": [str(lo), str(hi)],
                       "exp_bounds": [str(elo), str(ehi)]}
            if not repaired:
                lo = hi = mid
            require(step == len(observed) - index, "calls after overlap stop")
            break
    require(len(observed) - index <= STEPS, "too many bisection steps")
    require(caught_unresolved == (repaired and overlap is not None),
            "unresolved outcome must raise, not return None")
    expected_return = None if caught_unresolved else (lo, hi)
    require(result == expected_return, "trace disagrees with actual subject outcome")
    return result, {"bracket_calls": bracket_calls,
                    "bisection_steps": len(observed) - index, "overlap": overlap}


def fraction_pair(bounds):
    return [str(x) for x in bounds]


def selected_arguments(documents):
    assembly = documents["research/community-frontier1094-audit/ASSEMBLY.json"]
    expected = documents["research/e8-bit-p111-tuned/tune/EXPECTED.json"]
    return {
        "selected_complex": sorted({Q(73, int(r)) for r in assembly["complex_profile"]}),
        "selected_bit": sorted({Q(64, int(r)) for r in expected["nine"]["profile"]}),
    }


def make_receipt():
    pins, documents = check_live_inputs()
    source, metadata = subject_source()
    require((HERE / "repair.patch").read_text() == repair_diff(source), "repair patch drift")
    original, repaired = load_subject(), load_subject(repaired=True)
    fixtures = []
    # Include both endpoint equalities and strict interior overlaps, on both
    # sides of the true exponential. Additional midpoints exercise four brackets.
    for kind, point, value, relation in counterexample_specs():
        positive_tail = point ** (ORDER + 1) / factorial(ORDER + 1)
        if relation == "below":
            witness = polynomial(point, ORDER + 1)
            require(positive_tail > 0 and value < witness,
                    "strict positive-tail witness")
            proof = "input < T_49(point) < exp(point)"
        else:
            witness = exponential_upper(point, ORDER + 1)
            require(witness < value <= exponential_upper(point, ORDER),
                    "strict geometric-tail witness")
            proof = "exp(point) < U_49(point) < input <= U_48(point)"
        bad, before = traced_call(original, value)
        safe, after = traced_call(repaired, value, repaired=True)
        reference = log_oracle(value)
        require(before["overlap"] is not None and before == after, "expected overlap trace")
        require(bad == (point, point), "counterexample must return the midpoint")
        require(reference[1] < point if relation == "below" else reference[0] > point,
                "independent oracle must strictly refute singleton")
        require(safe is None, "repair must fail closed on unresolved comparison")
        fixtures.append({"kind": kind, "point": str(point), "input": str(value),
                         "proof": proof, "strict_rational_witness": str(witness),
                         "positive_first_omitted_term": str(positive_tail),
                         "original_return": fraction_pair(bad),
                         "repaired_outcome": "ValueError: " + UNRESOLVED,
                         "independent_log_enclosure": fraction_pair(reference),
                         "trace": before})

    # A compact integer input found by a bounded search, independently proved
    # by a finite positive Taylor sum. No minimal-integer claim is needed.
    integer_input = Q(1681)
    bad, integer_trace = traced_call(original, integer_input)
    safe, safe_trace = traced_call(repaired, integer_input, repaired=True)
    point = Q(4384212064881345387879, 590295810358705651712)
    gap = polynomial(point, ORDER + 1) - integer_input
    integer_reference = log_oracle(integer_input)
    require(bad == (point, point) and integer_trace == safe_trace,
            "integer counterexample trace")
    require(integer_trace["overlap"] is not None and integer_trace["bisection_steps"] == 72,
            "integer counterexample must reach final-step overlap")
    elo, ehi = (Q(x) for x in integer_trace["overlap"]["exp_bounds"])
    require(elo < integer_input < ehi and gap > 0,
            "strict interior overlap and positive finite Taylor witness")
    require(integer_reference[1] < point and safe is None,
            "integer oracle refutation and fail-closed repair")
    integer_fixture = {"input": "1681", "original_return": fraction_pair(bad),
                       "proof": "input < T_49(returned midpoint) < exp(returned midpoint)",
                       "positive_rational_gap": str(gap), "proof_order": 49,
                       "independent_log_enclosure": fraction_pair(integer_reference),
                       "repaired_outcome": "ValueError: " + UNRESOLVED,
                       "trace": integer_trace}

    selected = {}
    groups = selected_arguments(documents)
    require(all(len(arguments) == 8 for arguments in groups.values())
            and len(set(sum(groups.values(), []))) == 16, "selected argument inventory changed")
    for group, arguments in groups.items():
        rows = []
        for value in arguments:
            before, trace = traced_call(original, value)
            after, after_trace = traced_call(repaired, value, repaired=True)
            reference = log_oracle(value)
            require(trace["overlap"] is None and trace["bisection_steps"] == STEPS,
                    "selected argument reaches unresolved branch")
            require(before == after and trace == after_trace, "selected output changed")
            require(encloses(before, reference), "selected bracket excludes independent oracle")
            rows.append({"input": str(value), "return": fraction_pair(before),
                         "independent_log_enclosure": fraction_pair(reference),
                         "bracket_calls": trace["bracket_calls"],
                         "bisection_steps": trace["bisection_steps"], "overlap_hits": 0})
        selected[group] = rows
    require(original["ln_exp_bisection"](Q(1)) == repaired["ln_exp_bisection"](Q(1)) == (0, 0),
            "exact positive fixture ln(1)")
    return {"status": "PASS_PR1293_LOG_ENCLOSURE_AUDIT",
            "subject_identity": dict(SUBJECT_ID),
            "subject_head": metadata["head"], "subject_sha256": metadata["sha256"],
            "repaired_source_sha256": sha256(repaired_source(source).encode()),
            "default_order": ORDER, "default_bisection_steps": STEPS,
            "oracle": {"method": "range-reduced positive atanh series, outward dyadic rounding",
                       "terms": ORACLE_TERMS, "bits": ORACLE_BITS},
            "live_inputs": pins, "counterexamples": fixtures,
            "integer_counterexample": integer_fixture,
            "selected_arguments": selected,
            "positive_control": "ln(1) is exactly [0,0] in both versions",
            "scope": "A false general enclosure in a pending cross-check, not a failed selected moment. The selected 16 rank-log arguments avoid the branch; no word rebuild or multiplication theorem is claimed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path, help="explicitly write regenerated evidence")
    args = parser.parse_args()
    receipt = make_receipt()
    if args.write_receipt:
        args.write_receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        expected = load_json((HERE / "RESULT.json").read_bytes())
        require(canonical(receipt) == canonical(expected), "receipt drift")
    print(receipt["status"])
    print("11 exact counterexamples; 16 selected rank-log arguments enclosed; zero selected overlap hits")


if __name__ == "__main__":
    main()
