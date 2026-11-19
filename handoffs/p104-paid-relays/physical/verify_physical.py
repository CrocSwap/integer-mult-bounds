#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay native physical routes, ordinary resources, and the P104 outer gate."""

import argparse
from copy import deepcopy
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


BASE = "e54523517d0f03e58352e647c403a5af3e525a57"
PARENT_HEAD = "d5219594c9b0e80c002a75e79b85766256496b07"
PARENT_GRAPH = "c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84"
APPLICANT_GRAPH = "eb8a9cbf477308f8baa949a780a5a3b6d998ff9a64934591839a4b5690186702"
CALLER = "3b326189234984d7797566fa4732d4e2698db778f117cd09bb5654ea740c5563"
TARGET = "0.00383069832566"
CALLS = 2048
PARENT_PINS = {
    "qualify.py": "4b6e6a199c4d1a926e3cba8d30273ea15704811ba3e3db61f6ded116b46399ac",
    "PRICE.json": "01322abb90aa91f7844ec91f66b61e68aa08a8ddd18f5eb5613f7f4c2f2d2014",
    "evidence/application.json": "e6c64909c6dbc68bb041a3c9b80610375f2dbc0357652c1204bd2ffc42d039fa",
    "evidence/expansion.json": "70f2ab97769bdd39e8b31605a693407973124c6e39e81a602be5703296e2b155",
    "evidence/native-source-replay.json": "5dbd74f941ae174144535cdb362828e70ae4a47b4777fcf9fef25a9901d26999",
    "evidence/price.json": "9d7cb0ebcf4a83b9ffa2596c4a1c178b79c9fa91a6a54b195be3083b411726f6",
    "PR7756-SOURCES.json": "ade91c7697192df63fd68ee50f5dd3132f59b7413139090807a94151d50cf53d",
}
BASE_PATHS = (
    "scripts/compare_recursive_invoices.py",
    "scripts/evaluate_recursive_power.py",
    "research/shared-wire-split-composition/frozen/clifford_exact.py",
    "research/shared-wire-split-composition/frozen/native_verify.py",
)


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(raw):
    return sha256(raw).hexdigest()


def stage_base(repo, work, native_source, qualify):
    manifest = json.loads((native_source / "SOURCES.json").read_bytes())
    need(manifest["base_commit"] == BASE, "unexpected canonical source base")
    pins = {row["path"]: row for row in manifest["files"] if row["usage"] == "input"}
    git_env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_NO_REPLACE_OBJECTS="1")
    for name in BASE_PATHS:
        raw = subprocess.check_output(["git", "-C", str(repo), "show", f"{BASE}:{name}"],
                                      env=git_env, timeout=30)
        pin = pins[name]
        need(sha(raw) == pin["sha256"] and qualify.git_blob(raw) == pin["git_blob"],
             "wrong canonical source bytes for " + name)
        path = work / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    sys.path.insert(0, str(work / Path(BASE_PATHS[-1]).parent))
    return {name: pins[name] for name in BASE_PATHS}


def load_sources(package, repository, work):
    for name, digest in PARENT_PINS.items():
        need(sha((package / name).read_bytes()) == digest, "wrong #7761 bytes for " + name)
    sys.path.insert(0, str(package))
    import qualify

    source = package / "pr7756"
    # Authenticate the source manifest before it can select any imports.
    need(sha((source / "SOURCES.json").read_bytes()) == qualify.PACKAGE_PINS["SOURCES.json"],
         "wrong #7756 source manifest")
    pinned_base = stage_base(repository, work, source, qualify)
    provenance = qualify.verify_sources(source, work / "scripts")
    return qualify, provenance, pinned_base


def changed_routes(parent, applicant, digest):
    import clifford_exact as producer
    import native_verify as checker

    old = {k: (a, b) for k, a, b in parent["moves"]}
    routes = sorted({(a, b) for k, a, b in applicant["moves"] if old.get(k) != (a, b)})
    frames = applicant["frames"]

    @cache
    def source_frame(i):
        return producer.canonical_frame(9, tuple(frames[i]))

    @cache
    def independent_frame(i):
        return checker.frame(frames[i], 9)

    reports = []
    for a, b in routes:
        recipe, _ = producer.lower_child(source_frame(a).adjoint().then(source_frame(b)))
        need(recipe["rank"] == abs(len(frames[a]) - len(frames[b])) > 0, "changed physical transfer rank")
        actual = checker.recipe(recipe)
        expected = checker.adjoint(independent_frame(a)) + independent_frame(b)
        checker.equal(actual, expected, "signed Pauli action and absolute phase")
        for op, reference in ((actual, expected), (checker.adjoint(actual), checker.adjoint(expected))):
            need(all(checker.state(op, col) == checker.state(reference, col) for col in range(512)),
                 "exact forward and adjoint Gaussian columns")
        wrong = deepcopy(recipe)
        wrong["left"]["phase"] = (wrong["left"]["phase"] + 1) % 4
        try:
            checker.equal(checker.recipe(wrong), expected, "phase fault")
        except ValueError:
            pass
        else:
            raise ValueError("changed global phase accepted")
        reports.append(dict(pair=[a, b], rank=recipe["rank"], forward_and_adjoint_columns=1024,
                            incorrect_phase_rejected=True, recipe_sha256=digest(recipe)))
    return reports


def point_price(bill, point):
    from evaluate_recursive_power import evaluate

    zero = dict(bill, paid={}, targets={})
    return evaluate(zero, bill, 1 - Fraction(point), bits=152)


def points_for(bill, bit_pin):
    denominator = 10**14
    left, right = 0, 690_000_000_000
    mass = sum(int(r) * n for r, n in bill["targets"].items()) - sum(int(r) * n for r, n in bill["paid"].items())
    need(mass > 0 and point_price(bill, Fraction(right, denominator))["classification"] == "new_cost_higher",
         "finite signed price bracket")
    while right - left > 1:
        mid = (left + right) // 2
        sign = point_price(bill, Fraction(mid, denominator))["classification"]
        need(sign in {"new_cost_lower", "new_cost_higher"}, "unresolved exact price sign")
        if sign == "new_cost_lower":
            left = mid
        else:
            right = mid
    claim = min(left - 8, int(Fraction(bit_pin) * denominator) - 8)

    def decimal(n):
        return f"{n // denominator}.{n % denominator:014d}"

    return dict(claim=decimal(claim), probe=decimal(claim + 7), bracket=[decimal(left), decimal(right)])


def ordinary_delta(old, new):
    result = {}
    need(old.keys() == new.keys(), "ordinary resource key mismatch")
    for name, value in new.items():
        if isinstance(value, dict):
            delta = ordinary_delta(old[name], value)
        elif isinstance(value, list):
            numbers = [a - b for a, b in zip(value, old[name], strict=True)]
            delta = numbers if any(numbers) else []
        else:
            delta = value - old[name]
        if delta:
            result[name] = delta
    return result


def physical_replay(package, candidate, graph_pin, qualify):
    from application import invoice
    from caller16 import signed_caller
    from common import digest, inputs, jobs, physical, read
    from compare_recursive_invoices import compare_invoices
    from evaluate_recursive_power import evaluate
    from mixed_application import check_components, ordinary_for_batch, verify_caller
    from native import selected_interfaces

    baseline, layout, old_moves, _, interface = inputs()
    need(digest(baseline) == PARENT_GRAPH and digest(candidate) == graph_pin, "bound parent and applicant native graphs")
    need(candidate.keys() == baseline.keys() and all(candidate[k] == baseline[k]
         for k in ("initial", "final", "frames", "first_output")), "fixed native public charts and owner order")
    expansion = json.loads((package / "evidence/expansion.json").read_bytes())["result"]
    baseline_price = json.loads((package / "evidence/price.json").read_bytes())["contiguous_2048"]
    baseline_app = json.loads((package / "evidence/application.json").read_bytes())["result"]
    baseline_points = qualify.read_points(package / "PRICE.json")
    need(expansion["event_stream_sha256"] == CALLER and expansion["native_calls"] == CALLS
         and baseline_app["graph_sha256"] == PARENT_GRAPH
         and baseline_price["raw_bracket"] == baseline_points["bracket"], "public #7761 baseline binding")
    baseline_native = baseline_app["retained_native"]["native"]
    previous_paid, previous_targets, previous_pairs = jobs(baseline, interface[0], old_moves)
    normalized = qualify.normalized
    need(normalized(previous_paid) == baseline_native["paid_native_ranks"]
         and normalized(previous_targets) == baseline_native["positive_helper_ranks"], "rebuilt baseline native counts")
    catalogue = json.loads((package / "evidence/native-source-replay.json").read_bytes())
    old_physics = catalogue["exact_results"]
    partitions = old_physics["phased_partitions"]
    need(catalogue["status"] == "passed" and catalogue["public_head"] == qualify.SOURCE_HEAD
         and catalogue["native_bindings"]["graph_sha256"] == PARENT_GRAPH
         and old_physics["native_physical"] == baseline_native
         and old_physics["total_chart_pairs"] == len(previous_pairs)
         and [row["shard"] for row in partitions] == [0, 1, 2]
         and all(row["checked_pairs"] == len(range(i, len(previous_pairs), 3))
                 and row["total_pairs"] == len(previous_pairs) for i, row in enumerate(partitions)),
         "inherited source-pinned catalogue and native physical replay")

    moves = {key: (a, b) for key, a, b in candidate["moves"]}
    rows = {key: [(donor, Fraction(q)) for donor, q in row] for key, row in candidate["forms"]}
    terminals = set(range(candidate["first_output"], candidate["first_output"] + layout["public"]))
    need(len(moves) == len(candidate["moves"]) and len(rows) == len(candidate["forms"]) == len(candidate["schedule"])
         and rows.keys() == moves.keys() | terminals == set(candidate["schedule"])
         and all([donor for donor, _ in row] == sorted({donor for donor, _ in row}) for row in rows.values()),
         "complete unique applicant bank graph")
    native = physical.graph_bounds(candidate, moves, rows, interface[0])
    paid, productive, applicant_pairs = jobs(candidate, interface[0], moves)
    need(paid == native["paid_native_ranks"] and productive == native["positive_helper_ranks"],
         "independent paid and productive native counts")
    charts = changed_routes(baseline, candidate, digest)
    need(applicant_pairs - previous_pairs <= {tuple(row["pair"]) for row in charts},
         "coverage of all new route pairs")
    print("PHYSICAL ROUTES", len(charts), flush=True)

    grid = native["path_grid"]
    expected = physical.expected_rows(layout["public"], layout, interface, grid)
    native.update(physical.exact_basis_grid(candidate, moves, rows, grid, expected))
    native.update(physical.held_schedule(candidate, moves, rows, grid, expected, control=True))
    clear = physical.partial_clear_control()
    need(native["retired_and_guards_restored"] and native["all_public_inputs_preserved_until_final_installs"]
         and native["exact_all_public_rows"] == native["same_owner_complete_fixture_outputs"] == layout["public"]
         and clear["dirty_unaddressed_last_cell_rejected"] and clear["neighbor_unchanged"],
         "exact public rows, guarded CLEAR, and protected independent inputs")

    caller, phase_bases = read("data/CALLER.json.gz"), read("data/CALLER-PHASE-BASES.json")
    scalars = physical.scalar_cases([rows], caller, (2025, native["path_grid_odd"]))
    components = check_components(caller, physical, scalars["coefficient_bits"])
    inherited = signed_caller(caller, layout, 2025, 9)
    signed, envelope, caller_proof = verify_caller(caller, layout, CALLS, inherited, phase_bases)
    previous = baseline_app["candidate"]
    assumptions = selected_interfaces()
    need(normalized(signed) == previous["signed"] and signed["finite_binding"] == baseline_price["binding"]
         and normalized(envelope) == previous["envelope"] and normalized(caller_proof) == previous["word_proof"]
         and assumptions == baseline_app["conditional_interfaces"], "exact inherited ownership and physical caller phases")

    contract = baseline_price["invoice"]["contract"]
    old_bill = invoice(baseline_native, signed, contract)
    old_ordinary = ordinary_for_batch(baseline_native, signed, baseline_app["components"]["coefficient_bits"])
    old_root = physical.root_envelope({"candidate": baseline_native}, envelope)
    qualify.check_owners(baseline_native, signed, old_ordinary, old_bill)
    need(old_bill == previous["invoice"] == baseline_price["invoice"]
         and normalized(old_ordinary) == previous["ordinary"] == baseline_price["ordinary"]
         and normalized(old_root) == previous["common_root"], "complete #7761 ordinary, invoice and root binding")
    old_compiler = qualify.price_and_compile(old_bill, baseline_points, physical, old_root)
    need(normalized(old_compiler) == previous["price"], "parent outer replay")

    new_bill = invoice(native, signed, contract)
    ordinary = ordinary_for_batch(native, signed, components["coefficient_bits"])
    qualify.check_owners(native, signed, ordinary, new_bill)
    comparison = compare_invoices(old_bill, new_bill)
    need(comparison["delta_targets"] == {}, "fixed productive target invoice")
    root = physical.root_envelope({"prior": baseline_native, "revised": native}, envelope)
    points = points_for(new_bill, qualify.BIT_PIN)
    compiled = qualify.price_and_compile(new_bill, points, physical, root)
    gain = Fraction(points["claim"]) - Fraction(baseline_points["bracket"][1])
    at_target = point_price(new_bill, TARGET)
    difference = evaluate(old_bill, new_bill, 1 - Fraction(points["claim"]), bits=256)
    return dict(
        public_condition_names=assumptions, native=native, chart_qualifications=charts,
        native_scalar_cases=scalars, clear_control=clear, components=components, signed_caller=signed,
        route_coverage=dict(baseline_catalogue_pairs=len(previous_pairs), applicant_pairs=len(applicant_pairs),
                            inherited_pairs=len(applicant_pairs & previous_pairs), new_pairs=len(applicant_pairs - previous_pairs)),
        caller_proof=caller_proof, common_root=root, ordinary=ordinary,
        ordinary_delta=ordinary_delta(old_ordinary, ordinary), candidate_invoice=new_bill,
        baseline=dict(invoice=old_bill, ordinary=old_ordinary, compiler=old_compiler),
        invoice_comparison=comparison, compiler=compiled, difference_at_claim=difference,
        target=TARGET, cost_at_target=at_target["new_minus_old"], cost_at_target_sign=at_target["classification"],
        gain_over_parent_upper=str(gain), meets_target=Fraction(points["claim"]) >= Fraction(TARGET),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-package", type=Path, required=True, help="pinned #7761 research package")
    parser.add_argument("--repository", type=Path, required=True, help="Git repository with complete pinned canonical base")
    parser.add_argument("--graph", type=Path, required=True, help="reconstructed JSON or JSON.gz graph")
    parser.add_argument("--expected-graph-sha256", default=APPLICANT_GRAPH, help="explicit alternative canonical graph pin")
    parser.add_argument("--output", type=Path, required=True, help="deterministic replay receipt")
    args = parser.parse_args()
    need(sys.flags.optimize == 0, "retain physical and interval assertions")
    raw = args.graph.read_bytes()
    candidate = json.loads(gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw)
    with TemporaryDirectory(prefix="p104-physical-") as directory:
        package = args.parent_package.resolve()
        qualify, provenance, canonical = load_sources(package, args.repository.resolve(), Path(directory))
        result = physical_replay(package, candidate, args.expected_graph_sha256, qualify)
    source = dict(parent_head=PARENT_HEAD, parent_graph_sha256=PARENT_GRAPH, caller_word_sha256=CALLER,
                  applicant_graph_sha256=args.expected_graph_sha256, applicant_bytes_sha256=sha(raw),
                  base_commit=BASE, parent_file_sha256=PARENT_PINS, canonical_inputs=canonical, pr7756=provenance)
    receipt = dict(schema="p104-fixed-boundary-physical-replay/1", status="passed", source=source, result=result)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("PASS P104 PHYSICAL", result["compiler"]["claim"], "target", result["meets_target"], flush=True)


if __name__ == "__main__":
    main()
