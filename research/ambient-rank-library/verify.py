"""Bounded exact replay, separate occurrence oracle, and semantic controls.

Default operation is read-only and compares the computed receipt. Apache-2.0.
Prepared for CubeJerry with substantial OpenAI assistance.
"""
import argparse
from bisect import bisect_right
import hashlib
import importlib.util
import json
from math import gcd, lcm
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticated_sources():
    sources = json.loads((ROOT / "SOURCES.json").read_text())
    checked = []
    for row in sources["files"]:
        if "local" not in row:
            continue
        raw = (ROOT / row["local"]).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(digest == row["sha256"] and blob == row["git_blob"], "source drift " + row["local"])
        checked.append({"local": row["local"], "sha256": digest, "bytes": len(raw)})
    require(len(checked) >= 6, "frozen source inventory incomplete")
    return checked


def row_tuple(row):
    return row.replication, row.width, row.leaves, row.units


def compare(subject, oracle, case, digest):
    ambient, targets, paid, maximum = case
    rule = subject.Rule(ambient, targets, paid)
    library = subject.compile_library(rule, maximum)
    literal = oracle.explicit_library(ambient, targets, paid, maximum)
    work = subject.Work()
    g = subject.height(rule, maximum)
    targets_table = subject.product_tables(targets, g, subject.Limits(), work)
    paid_table = subject.product_tables(paid, g + 1, subject.Limits(), work)
    for rank in range(1, maximum + 1):
        actual = row_tuple(library.rows[rank])
        require(actual == literal["rows"][rank], "independent row mismatch")
        digest.update(json.dumps([case, rank, actual], separators=(",", ":")).encode())
        if rank < ambient:
            continue
        flow = subject.census(rule, rank, targets_table, paid_table, subject.Limits(), work)
        other = literal["flows"][rank]
        require((flow.height, flow.units, flow.sources, flow.exits) ==
                (other["height"], other["units"], other["sources"], other["exits"]),
                "independent occurrence census mismatch")
    envelope = subject.envelope(rule, maximum)
    generators = {r for alphabet in (targets, paid) for r, _ in alphabet if r >= 2}
    gamma = oracle.semigroup(generators, maximum // ambient)
    require(len(gamma) <= envelope["plateau_count_bound"], "semigroup box failure")
    divisor = 1
    for location in gamma:
        source_count = sum(c for _, c in literal["flows"][ambient * location]["sources"])
        divisor *= source_count ** envelope["plateau_visit_bound"]
    require(divisor <= 1 << envelope["width_log_bound"], "divisor envelope failure")
    depth, runs, labels = [0] * (maximum + 1), [0] * (maximum + 1), [None] * (maximum + 1)
    for rank, row in enumerate(library.rows[1:], 1):
        require(divisor % row.width == 0, "all-prime divisor failure")
        require(sum(row_tuple(row)[1:]).bit_length() <= envelope["combined_output_bits"],
                "expanded output bit envelope failure")
        require(max(abs(x).bit_length() for x in row_tuple(row)) <= envelope["Z"], "record bit cap")
        if rank < ambient:
            continue
        flow = literal["flows"][rank]
        label = gamma[bisect_right(gamma, rank // ambient) - 1]
        labels[rank] = label
        reference = literal["flows"][ambient * label]
        require(flow == reference, "full literal plateau signature changed")
        children = [rank - s for s, _ in flow["sources"] if s < rank]
        children += [e for _, e in flow["cuts"]]
        require(all(0 < e < rank and ambient * e <= (ambient - 1) * rank for e in children),
                "contracting child failure")
        depth[rank] = 1 + max(depth[e] for e in children)
        runs[rank] = 1 + max(runs[e] if labels[e] == label else 0 for e in children)
        require(depth[rank] <= envelope["D"] and runs[rank] <= envelope["plateau_visit_bound"],
                "chain depth or plateau visit failure")
    return {"ambient": ambient, "targets": targets, "paid": paid, "maximum": maximum,
            "ranks": maximum, "literal_units": literal["units"], "literal_cuts": literal["cuts"],
            "constraints": literal["constraints"], "plateaus": len(gamma),
            "divisor_bits": divisor.bit_length(), "max_depth": max(depth),
            "max_plateau_visits": max(runs),
            "max_width_bits": max(row.width.bit_length() for row in library.rows[1:])}


def rejects(label, action):
    try:
        action()
    except (ValueError, IndexError):
        return label
    raise ValueError("negative control escaped: " + label)


def mutant(label, old, new):
    source = (ROOT / "ambient_library.py").read_text()
    require(source.count(old) == 1, "mutation anchor not unique: " + label)
    module = types.ModuleType("mutant_" + label)
    sys.modules[module.__name__] = module
    exec(compile(source.replace(old, new), "mutant_" + label, "exec"), module.__dict__)
    return module


def lower_bounds(subject):
    totals = []
    for ambient in tuple(range(4, 81)) + (127, 128, 255, 256):
        maximum = 2 * ambient - 1
        rule = subject.Rule(ambient, ((2, 1), (3, 1)), ((1, 1),))
        library = subject.compile_library(rule, maximum)
        bits = 0
        for rank in range(ambient, maximum + 1):
            exponent = (rank - ambient) // 2 + 1
            require(library.rows[rank].width == 1 << exponent, "ambient lower-bound formula")
            bits += library.rows[rank].width.bit_length()
        expected = ((ambient - 1) ** 2) // 4 + 2 * ambient
        require(bits == expected, "ambient aggregate bit formula")
        totals.append({"ambient": ambient, "maximum": maximum, "written_width_bits": bits})
    return totals


def controls(subject, oracle):
    rule = subject.Rule(4, ((3, 2),), ((2, 2),))
    library = subject.compile_library(rule, 12)
    work = subject.Work()
    target = subject.product_tables(rule.targets, 1, subject.Limits(), work)
    paid = subject.product_tables(rule.paid, 2, subject.Limits(), work)
    flow = subject.census(rule, 12, target, paid, subject.Limits(), work)
    factors = [library.rows[12 - s].width // gcd(library.rows[12 - s].width, c)
               for s, c in flow.sources if s < 12]
    factors += [library.rows[e].width // gcd(library.rows[e].width, c) for e, c in flow.exits]
    pooled = lcm(*factors)
    require((flow.sources, flow.exits, library.rows[4].width, library.rows[12].replication, pooled) ==
            (((9, 4),), ((4, 4),), 2, 2, 1), "ambient pooling witness changed")
    result = [rejects("pooled-distinct-exits", lambda: subject.finish_row(flow, library.rows, pooled, subject.Limits()))]
    invalid = [
        ("ambient-below-target", lambda: subject.Rule(2, ((3, 1),), ((1, 1),))),
        ("unseparated", lambda: subject.Rule(3, ((3, 1),), ((3, 1),))),
        ("zero-rank", lambda: subject.compile_library(rule, 0)),
        ("rank-capacity", lambda: subject.compile_library(rule, 5000)),
        ("ambient-bit-capacity", lambda: subject.compile_library(subject.Rule(1 << 100, ((2, 1),), ((1, 1),)), 1,
                                                                  subject.Limits(max_bits=32))),
        ("rank-zero-child", lambda: subject.child(library.rows, 12, 0)),
        ("base-envelope", lambda: subject.envelope(rule, 3)),
    ]
    result += [rejects(label, action) for label, action in invalid]
    changes = [
        ("lost-ambient-height", "threshold = rule.ambient", "threshold = rule.m"),
        ("lost-ambient-fit", "rule.ambient * size", "rule.m * size"),
        ("wrong-base", "if rank < rule.ambient:\n            row", "if rank < rule.m:\n            row"),
        ("pooled-exit-code", "factor = child(rows, flow.rank, exit_rank).width",
         "factor = child(rows, flow.rank, exit_rank).width // gcd(child(rows, flow.rank, exit_rank).width, multiplicity)"),
        ("lost-cut-multiplicity", "copies = limits.integer(multiplicity * per_cut)", "copies = per_cut"),
        ("lost-complement-gcd", "factor = width // gcd(width, count)", "factor = width"),
    ]
    case = (4, ((3, 2),), ((2, 2),), 12)
    for label, old, new in changes:
        changed = mutant(label, old, new)
        fixture = ((8, ((3, 1), (5, 1)), ((1, 1), (2, 1)), 40)
                   if label == "lost-ambient-fit" else case)
        result.append(rejects(label, lambda mod=changed, test=fixture: compare(mod, oracle, test, hashlib.sha256())))
    changed = mutant("default-visit-constant", "visits = rule.ambient *", "visits = rule.m *")
    bad_rule = changed.Rule(64, ((2, 1), (3, 1)), ((1, 1),))
    bad_bound = changed.envelope(bad_rule, 127)["width_log_bound"]
    actual = subject.compile_library(subject.Rule(64, bad_rule.targets, bad_rule.paid), 127).rows[127].width
    result.append(rejects("default-visit-constant", lambda: require(actual <= 1 << bad_bound, "false default envelope")))
    require(actual == 1 << 32 and (1 << 3) % actual != 0, "exact failed default divisor")
    return {"rejected": result, "pooling": {"ambient": 4, "rank": 12, "exit_rank": 4,
            "distinct_cuts": 4, "child_width": 2, "valid_replication": 2, "pooled_replication": 1},
            "false_default_divisor": {"ambient": 64, "rank": 127, "default_Q": 8,
                                       "actual_width": actual, "wrong_beta": bad_bound}}


def run():
    sources = authenticated_sources()
    subject = load_module("ambient_subject", ROOT / "ambient_library.py")
    oracle = load_module("ambient_literal_oracle", ROOT / "literal_oracle.py")
    default = load_module("frozen_default_library", ROOT / "inputs/default_library.py")
    cases = [
        (2, ((2, 1),), ((1, 2),), 32),
        (2, ((2, 1),), ((1, 4),), 40),
        (5, ((3, 1), (5, 1)), ((1, 1), (2, 2)), 50),
        (8, ((3, 1), (5, 1)), ((1, 1), (2, 2)), 96),
        (13, ((2, 2), (3, 1)), ((1, 3),), 104),
        (7, ((3, 1), (5, 1)), ((2, 1),), 70),
        (11, ((3, 1), (4, 1)), ((2, 2),), 400),
        (9, ((3, 1), (4, 2)), ((2, 3),), 300),
        (4, ((3, 2),), ((2, 2),), 40),
        (32, ((2, 1), (3, 1)), ((1, 1),), 63),
        (6, ((2, 1), (4, 1)), ((1, 1),), 48),
        (3, ((2, 1), (3, 1)), ((1, 1),), 24),
    ]
    trace = hashlib.sha256()
    results = [compare(subject, oracle, case, trace) for case in cases]
    default_ranks = 0
    for ambient, targets, paid, maximum in cases:
        if ambient != targets[-1][0]:
            continue
        current = subject.compile_library(subject.Rule(ambient, targets, paid), maximum)
        previous = default.compile_library(default.Rule(targets, paid), maximum)
        require(tuple(map(row_tuple, current.rows[1:])) == tuple(map(row_tuple, previous.rows[1:])),
                "default specialization regression")
        default_ranks += maximum
    base = subject.compile_library(subject.Rule(1000, ((3, 1),), ((2, 1),)), 20)
    require(tuple(map(row_tuple, base.rows[1:])) == tuple((1, 1, n, 0) for n in range(1, 21)),
            "all-base initialization")
    lower = lower_bounds(subject)
    negative = controls(subject, oracle)
    ambient = 153 ** 1920
    huge_rule = subject.Rule(ambient, ((2, 1), (3, 1)), ((1, 1),))
    bounds = subject.envelope(huge_rule, 2 * ambient - 1)
    require(bounds["height"] == 0 and bounds["D"] == ambient and
            bounds["width_log_bound"] == 8 * ambient, "symbolic huge ambient envelope")
    endpoint_length = (ambient + 1) // 2 + 1
    huge = {"ambient_expression": "153**1920", "ambient_bits": ambient.bit_length(),
            "ambient_sha256": hashlib.sha256(ambient.to_bytes((ambient.bit_length() + 7) // 8, "big")).hexdigest(),
            "maximum_expression": "2*A-1", "maximum_bits": (2 * ambient - 1).bit_length(),
            "bound_value_bits": bounds["width_log_bound"].bit_length(),
            "endpoint_width_length_encoding_bits": endpoint_length.bit_length(),
            "materialized_rows": 0, "scope": "toy histogram bounds only, not selected library"}
    science = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
               for name in ("ambient_library.py", "literal_oracle.py", "verify.py", "PROOF.md")}
    return {"status": "PASS_AMBIENT_RANK_LIBRARY", "base": "e54523517d0f03e58352e647c403a5af3e525a57",
            "selected_kappa": "0.00363005817", "no_new_kappa": True,
            "cases": results, "independent_ranks": sum(x["ranks"] for x in results),
            "independent_units": sum(x["literal_units"] for x in results),
            "independent_cuts": sum(x["literal_cuts"] for x in results),
            "independent_constraints": sum(x["constraints"] for x in results),
            "default_regression_ranks": default_ranks, "all_base_rows": 20,
            "lower_bound_fixtures": lower, "negative_controls": negative,
            "large_ambient_bound_only": huge, "trace_sha256": trace.hexdigest(),
            "frozen_sources": sources, "scientific_sha256": science}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, help="write a new external receipt; refuse existing paths")
    args = parser.parse_args()
    result = json.loads(json.dumps(run(), sort_keys=True))
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        destination = args.receipt.resolve()
        require(not destination.is_relative_to(ROOT), "receipt must be external to the package")
        with destination.open("x", encoding="utf-8") as output:
            output.write(encoded)
    else:
        expected = json.loads((ROOT / "VALIDATION.json").read_text())
        require(result == expected, "computed receipt differs from committed VALIDATION.json")
    print(json.dumps({"status": result["status"], "independent_ranks": result["independent_ranks"],
                      "independent_cuts": result["independent_cuts"],
                      "negative_controls": len(result["negative_controls"]["rejected"]),
                      "trace_sha256": result["trace_sha256"], "no_new_kappa": True}, sort_keys=True))


if __name__ == "__main__":
    main()
