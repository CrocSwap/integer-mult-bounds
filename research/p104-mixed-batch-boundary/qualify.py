#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Qualify a contiguous 2,048-call P104 batch against two sealed #7756 batches."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys


SOURCE_HEAD = "6b0044123aad114cf71ca2bb0e98741e5a27c7b5"
PARENT_WORD = "d82aa7d2ac4974f58b8a4e9f15a8ec9286bc79e26ab5d53f9d748db9f9a04ca8"
NATIVE_GRAPH = "c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84"
PARENT_UPPER = "0.00382063778177"
PARENT_CALLS = 1024
CALLS = 2048
BIT_PIN = "0.00385248"

# These bytes are either new in #7756 or its top-level provenance/receipts.
# SOURCE-PINS.json authenticates the inherited modules and inputs.
PACKAGE_PINS = {
    "EDITS.json": "7ced0e7a5d39f1ebc1468899e1f66da84d2f7160d8c979763ee33bcd2e6e93c0",
    "PRICE.json": "8d88e2e4bdedcbe03001e4aa4ea6d69ba33b78adba16c95cfe2b20a18adb8ba2",
    "SOURCE-PINS.json": "78c1dc981a4ab6878422230a017297cd6f84540c58316854a3a13abd0bb02e7f",
    "SOURCES.json": "76818b74ee05a1a562813b1385b3609dea2bb548c260ebda1b3f8a7aeab236c9",
    "application.py": "b3eea4564d44c6f1c7a513f95e72072684f0b8a036ec43ad8a1b6e637fa3422f",
    "common.py": "8638ebe074926f5afa9ccd7edc4c9fda827261fb3c1a1b75ed703ff7089df258",
    "construction.py": "037c66277636cf5cd860e88f4f5998de46d34c726280c787fcb9f611091d634b",
    "data/CONJUGATE-CALLER.json.gz": "80009663da460229a57f09bde90e35294329a210ae7fc7ef6d1f05b61ffccbf4",
    "full_batch_probe.py": "57531420430e7f11efe5e0f9ae1296be9d79fe96e89c7fe742d0793252c4f7a2",
    "linear.py": "bc0aaa0e4ce28260907d29083e4f788e08ae60f050800257b39d1070d545e30e",
    "mixed_application.py": "e762a61f48411dff22117ce1a5154e8e530341f61d5264afeb839b398dd8345e",
    "mixed_caller.py": "4824b2aaadb592550d3a25c16ff0a453705e10b8868f5c22fe10c2874bcb9bae",
    "mixed_geometry.py": "5a7f8ed2deb6b9f8253372539b452b94ce15847200e4bf4b3721447b00362e70",
    "mixed_grid.py": "95b0526530467e84e1dd295e98fb1442d68e97a724b1b8724d04fcd2284d646b",
    "native.py": "3070ab83ed086e22340f58d5b63f3c313bc615aa9ddb4d00cb2e40c54d31febe",
    "results/application.json": "c736b04bed2be2e597cdc807dec38600008d80e8612e995f6d3a5c1df52f095d",
    "results/batch.json": "ca42f4298567752fe8b475295425271d428829d07cd3521ed8e4ed2f371dec35",
}
SCRIPT_NAMES = {"compare_recursive_invoices.py", "evaluate_recursive_power.py"}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def git_blob(raw):
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def verify_sources(source, scripts):
    for relpath, expected in PACKAGE_PINS.items():
        require(sha256((source / relpath).read_bytes()).hexdigest() == expected,
                "wrong #7756 source bytes for " + relpath)
    inherited = json.loads((source / "SOURCE-PINS.json").read_bytes())
    for pin in inherited:
        raw = (source / pin["path"]).read_bytes()
        require(sha256(raw).hexdigest() == pin["sha256"] and git_blob(raw) == pin["git_blob"],
                "wrong inherited source or blob for " + pin["path"])

    available = json.loads((source / "SOURCES.json").read_bytes())["files"]
    script_pins = {}
    for pin in available:
        path = Path(pin["path"])
        if path.parent != Path("scripts") or path.name not in SCRIPT_NAMES:
            continue
        raw = (scripts / path.name).read_bytes()
        require(sha256(raw).hexdigest() == pin["sha256"] and git_blob(raw) == pin["git_blob"],
                "wrong repository arithmetic script " + path.name)
        script_pins[path.name] = pin["sha256"]
    require(script_pins.keys() == SCRIPT_NAMES, "all repository arithmetic script pins")

    sys.path[:0] = [str(source), str(source / "vendor"), str(scripts)]
    return {
        "pr": 7756,
        "head": SOURCE_HEAD,
        "sealed_caller_sha256": PARENT_WORD,
        "package_sha256": PACKAGE_PINS,
        "inherited_files_checked": len(inherited),
        "repository_scripts_sha256": script_pins,
    }


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def normalized(value):
    return json.loads(encoded(value))


def directed(bill, point, sign):
    from evaluate_recursive_power import evaluate

    zero = dict(bill, paid={}, targets={})
    result = evaluate(zero, bill, 1 - Fraction(point), bits=256)
    require(result["classification"] == "new_cost_" + sign, "directed bill sign at " + point)
    return {"kappa": point, "sign": sign, **result["new_minus_old"]}


def price_and_compile(bill, points, physical, root):
    from interval_gate_signed import gate

    claim, probe = points["claim"], points["probe"]
    lower, upper = points["bracket"]
    signs = [directed(bill, point, sign) for point, sign in (
        (claim, "lower"), (probe, "lower"), (lower, "lower"), (upper, "higher")
    )]
    weights = {"P": bill["paid"], "T": bill["targets"]}
    compiler = gate(weights, claim, probe, lower, upper, BIT_PIN)
    outer = compiler["outer"]
    require((outer["strict_count"], outer["functional_count"]) == (54, 4)
            and Fraction(outer["minimum_margin"]) > 0
            and Fraction(compiler["BIT_margin"]) > 0, "54 strict and four functional outer predicates")
    depth = physical.check_depth_guard(root, int(compiler["H"]))
    return {**points, "directed": signs, "compiler": compiler, "depth": depth}


def check_owners(native, signed, ordinary, bill):
    bindings = signed["finite_binding"]
    calls = signed["calls"]
    require(bindings["native_main_bindings"] == 400 * calls
            and bindings["physical_port_contacts"] == 104 * calls
            and bindings["stage_helper_owners"] == (native["public"] - 400) * calls,
            "all main, physical port and stage helper bindings")
    paid, targets = sum(bill["paid"].values()), sum(bill["targets"].values())
    require(paid == ordinary["raw_paid_positions"] and targets == ordinary["raw_productive_targets"]
            and targets == bindings["stage_helper_owners"] + signed["root_owners"],
            "complete physical and recursive owner denominators")
    require(ordinary["port_view_permutations"] == ordinary["port_view_translations"] == 800 * calls
            and ordinary["port_view_routing_legs"] == 1600 * calls, "both ordinary views on every main")


def repeat_ordinary(value):
    """Sum occurrence counts and retain the per-service constants for two sealed runs."""
    fixed = {"native_numeric_homes", "scalar_step_rate", "serial_caller_real_component_arrays"}

    def double(count):
        if isinstance(count, dict):
            return {key: double(item) for key, item in count.items()}
        if isinstance(count, list):
            return [double(item) for item in count]
        require(type(count) is int, "ordinary bill counter")
        return 2 * count

    return {key: count if key in fixed else double(count) for key, count in value.items()}


def root_placements(caller, signed):
    from mixed_caller import place_roots

    sealed = place_roots(caller, PARENT_CALLS)
    contiguous = place_roots(caller, CALLS)
    ordered = [[kind, index, visits] for (kind, index), visits in contiguous.items()]
    across = Counter(kind for (kind, _), visits in contiguous.items()
                     if visits[0][0] < PARENT_CALLS <= visits[-1][0])
    delta = {kind: signed["finite_binding"]["template_roots"][kind]
             - 2 * sum(old_kind == kind for old_kind, _ in sealed)
             for kind in ("A", "B", "mixed")}
    require(delta == {"A": -56, "B": -8, "mixed": 64}, "exact exchanged root counts")
    require(across["mixed"] > 0, "actual mixed roots straddle the sealed boundary")
    return {
        "root_visits_sha256": sha256(encoded(ordered)).hexdigest(),
        "cross_seam_roots_by_type": dict(across),
        "root_delta": delta,
    }


def verify_application(points):
    from application import invoice
    from caller16 import signed_caller
    from common import physical, read
    from compare_recursive_invoices import compare_invoices
    from evaluate_recursive_power import evaluate
    from mixed_application import check_components, ordinary_for_batch, verify_caller
    from native import verify as verify_native

    parent = read("results/application.json")
    parent_batch = read("results/batch.json")
    parent_points = read("PRICE.json")
    require(parent["calls"] == parent_points["calls"] == PARENT_CALLS
            and parent["bracket"][1] == PARENT_UPPER
            and parent_batch["expansion"]["event_stream_sha256"] == PARENT_WORD,
            "pinned sealed caller baseline")
    require(Fraction(points["claim"]) > Fraction(PARENT_UPPER), "strict gain over directed upper")

    layout, authentication = verify_native()
    require(authentication["graph_sha256"] == parent["graph_sha256"] == NATIVE_GRAPH,
            "unchanged rebuilt native graph")
    native = authentication["physical"]["native"]
    for key in ("native", "scalars", "extra_prime_rejections", "partial_clear_control"):
        require(normalized(authentication["physical"][key]) == parent["physical"][key],
                "matched exact native evidence for " + key)
    require(native["retired_and_guards_restored"]
            and native["all_public_inputs_preserved_until_final_installs"]
            and native["exact_all_public_rows"] == native["same_owner_complete_fixture_outputs"] == native["public"],
            "all native output observations and guarded restoration")
    require(authentication["conditional_interfaces"] == parent["conditional_interfaces"],
            "retained conditional interfaces and selected BIT")

    caller, bases = read("data/CALLER.json.gz"), read("data/CALLER-PHASE-BASES.json")
    legacy = signed_caller(caller, layout, 2025, 9)
    components = check_components(caller, physical, authentication["physical"]["scalars"]["coefficient_bits"])
    require(components == parent["physical"]["components"], "retained scalar component service")
    contract = parent["invoice"]["contract"]

    # A full sealed replay gives the bill for the two independent identical copies.
    old, old_envelope, old_proof = verify_caller(caller, layout, PARENT_CALLS, legacy, bases)
    old_bill = invoice(native, old, contract)
    old_ordinary = ordinary_for_batch(native, old, components["coefficient_bits"])
    check_owners(native, old, old_ordinary, old_bill)
    require(normalized(old) == parent["caller"] and normalized(old_envelope) == parent["physical"]["caller_envelope"]
            and normalized(old_proof) == parent["physical"]["caller_word"]
            and old_bill == parent["invoice"] and old_ordinary == parent["physical"]["ordinary"],
            "independent sealed caller, exact bill and ordinary budget")
    comparison = dict(old_bill, **{side: {r: 2 * n for r, n in old_bill[side].items()}
                                   for side in ("paid", "targets")})
    old_root = physical.root_envelope({"candidate": native}, old_envelope)
    require(old_root == parent["physical"]["common_root"], "sealed common root envelope")
    old_price = price_and_compile(comparison, parent_points["combined"], physical, old_root)

    signed, envelope, word = verify_caller(caller, layout, CALLS, legacy, bases)
    bill = invoice(native, signed, contract)
    ordinary = ordinary_for_batch(native, signed, components["coefficient_bits"])
    check_owners(native, signed, ordinary, bill)
    require(signed["finite_binding"]["template_roots"] == {"A": 5176, "B": 8, "mixed": 8128},
            "independent chronological 2048-call roots")
    require(word["template_grids"] == old_proof["template_grids"]
            and word["template_bounds"] == old_proof["template_bounds"], "unchanged exact local substitutions")
    root = physical.root_envelope({"candidate": native}, envelope)
    require(root == old_root, "unchanged exact grid, signed width and common root bound")
    compiled = price_and_compile(bill, points, physical, root)
    differential = evaluate(comparison, bill, 1 - Fraction(points["claim"]), bits=256)
    require(differential["classification"] == "new_cost_lower", "same-call paid and productive gain at claim")
    return {
        "graph_sha256": authentication["graph_sha256"],
        "conditional_interfaces": authentication["conditional_interfaces"],
        "retained_native": authentication["physical"],
        "components": components,
        "seam": root_placements(caller, signed),
        "comparison": {
            "sealed_copies": 2,
            "calls_per_copy": PARENT_CALLS,
            "invocations": CALLS,
            "sealed_caller": old,
            "sealed_invoice": old_bill,
            "invoice": comparison,
            "ordinary": repeat_ordinary(old_ordinary),
            "price": old_price,
        },
        "candidate": {
            "calls": CALLS,
            "signed": signed,
            "envelope": envelope,
            "word_proof": word,
            "common_root": root,
            "invoice": bill,
            "ordinary": ordinary,
            "price": compiled,
        },
        "invoice_difference": compare_invoices(comparison, bill),
        "directed_difference_at_claim": differential,
        "gain_over_parent_upper": str(Fraction(points["claim"]) - Fraction(PARENT_UPPER)),
    }


def verify_batch(check):
    from common import digest, inputs, read
    from mixed_application import verify_expansion

    graph, layout, *_ = inputs()
    require(digest(graph) == NATIVE_GRAPH, "unchanged graph for every emitted occurrence")
    caller = read("data/CALLER.json.gz")
    if check == "expansion":
        result = verify_expansion(caller, layout, CALLS)
        require(result["native_calls"] == CALLS and result["op_counts"]["PORT_VIEWS"] == 2 * CALLS,
                "full native invocation and paired-view counts")
        return result

    import full_batch_probe

    # The frozen evaluator's global fixes only the finite schedule length.
    previous = full_batch_probe.CALLS
    require(previous == PARENT_CALLS, "frozen probe length")
    full_batch_probe.CALLS = CALLS
    try:
        result = full_batch_probe.verify(caller, layout, read("data/CALLER-PHASE-BASES.json"))
    finally:
        full_batch_probe.CALLS = previous
    probes = result["probes"]
    require(len(probes) == 2 and {probe["head_parity"] for probe in probes} == {0, 1}
            and all(probe["native_calls"] == CALLS and probe["native_contacts"] == 104 * CALLS
                    and probe["checked_outputs"] == 420096 for probe in probes),
            "both finite character computations reach all chronological output owners")
    return result


def read_points(path):
    points = json.loads(path.read_bytes())
    require(type(points) is dict and points.keys() == {"claim", "probe", "bracket"}
            and type(points["bracket"]) is list and len(points["bracket"]) == 2,
            "exact decimal claim, probe and two bracket endpoints")
    require(all(type(value) is str for value in (points["claim"], points["probe"], *points["bracket"])),
            "exact string points, no floating point")
    return points


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="complete frozen #7756 package")
    parser.add_argument("--scripts", type=Path, required=True, help="root repository scripts directory")
    parser.add_argument("--price", type=Path, help="JSON claim, probe and bracket")
    parser.add_argument("--check", default="application", choices=("application", "expansion", "probe", "pins"))
    parser.add_argument("--output", type=Path, help="write deterministic full receipt")
    args = parser.parse_args()
    require(sys.flags.optimize == 0, "retained compiler assertions enabled")
    if args.check == "application" and args.price is None:
        parser.error("--price is required for --check application")
    if args.check != "pins" and args.output is None:
        parser.error("--output is required for completed qualification receipts")

    source_pins = verify_sources(args.source.resolve(), args.scripts.resolve())
    if args.check == "application":
        result = verify_application(read_points(args.price))
    elif args.check in ("expansion", "probe"):
        result = verify_batch(args.check)
    else:
        result = {}
    receipt = dict(schema="p104-contiguous-caller-qualification/1", check=args.check, status="passed",
                   source=source_pins, verifier_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                   result=result)
    raw = encoded(receipt)
    if args.output is not None:
        args.output.write_bytes(raw)
    print("PASS_P104_2048", args.check, sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
