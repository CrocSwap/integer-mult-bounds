"""Reprice the literal candidate and #7781 using their common 48-call supplier."""
import argparse
from decimal import Decimal
from fractions import Fraction
import json
from pathlib import Path
import sys


def run(args):
    cache = args.cache.resolve()
    parent = cache / "parent"
    sys.path.insert(0, str(parent))
    import qualify_complex as inherited

    base = inherited.json_file(parent / "evidence/application.json")
    parent_claim = inherited.json_file(parent / "CLAIM.json")
    graph = inherited.json_file(args.word)
    layout = inherited.json_file(args.layout)
    inherited.need(inherited.digest(graph) == args.word_sha, "candidate word differs from declared pin")
    inherited.need(inherited.digest(layout) == args.layout_sha, "candidate layout differs from declared pin")
    inherited.need(base["native_sha256"] == parent_claim["complex_word"] and
                   base["layout_sha256"] == parent_claim["layout"], "parent application pins")
    constants = (parent_claim["complex_raw_bracket"][1], "0.00387981257853")
    inherited.need(constants[0] == "0.00386981257853", "fixed compatible comparator")
    source = cache / "source"
    supplier_dir = source / "research/p104-dual-supplier-lift"
    reference = inherited.historical_checker(cache / "peer")
    sys.path.insert(0, str(supplier_dir / "complex"))
    import supplier
    import supplier_gate
    from closed_application import apply, main_boundary, verify_caller

    main_boundary(graph, layout)
    role_sets = inherited.owners(layout)
    caller = supplier.read(supplier.SOURCE / "data/CALLER.json.gz")
    moves, rows = reference.graph_inputs(graph)
    if args.shard is not None:
        sys.path.insert(0, str(source / "research/shared-wire-split-composition/frozen"))
        import catalogue
        from network import Network
        net = Network(graph["first_output"], graph["initial"], graph["final"], moves,
                      {i: dict(row) for i, row in rows.items()})
        catalogue.build = lambda: (graph, layout, net)
        return {"native_sha256": args.word_sha, "shard": args.shard, "charts": catalogue.verify(args.shard)}

    bits = inherited.json_file(args.binary_finite)
    inherited.need(bits["word_sha256"] == args.binary_sha, "qualified binary word pin")
    cap = Fraction(bits["ordinary_admitted"])
    inherited.need(Fraction(constants[0]) < cap < Fraction("0.0069"), "qualified ordinary service domain")
    native = supplier.physical.graph_bounds(graph, moves, rows, role_sets[0])
    fixed = reference.count_caller(caller)
    weights = reference.invoice(native, fixed)
    parent_native = dict(base["native"])
    for key in ("positive_helper_ranks", "paid_native_ranks"):
        parent_native[key] = inherited.histogram(parent_native[key])
    base_weights = reference.invoice(parent_native, fixed)
    archived = {side: inherited.histogram(hist) for side, hist in base["application"]["invoice"].items()}
    inherited.need(archived == {"paid": base_weights["P"], "targets": base_weights["T"]},
                   "parent signed bill and common caller")
    root_cap = Fraction("0.0069")
    _, _, old_lo, old_hi = inherited.price(reference, base_weights, root_cap)
    inherited.need([old_lo, old_hi] == parent_claim["complex_raw_bracket"], "directed parent price")
    claim, tested, lo, hi = inherited.price(reference, weights, cap)
    inherited.need(Fraction(claim) > Fraction(old_hi), "strict gain over compatible comparator")
    signed, guard, proof, coefficients = verify_caller(caller, graph, layout,
                                                        supplier.read(supplier.SOURCE / "data/CALLER-PHASE-BASES.json"))
    inherited.need(inherited.histogram(signed["fixed_root_targets"]) == dict(fixed[0]) and
                   inherited.histogram(signed["fixed_caller_paid"]) == dict(fixed[1]) and signed["calls"] == 48,
                   "independent complete fixed caller prices")
    conversion = reference.native_replay(supplier, graph, layout, role_sets, moves, rows, native, caller)
    original_cap = supplier_gate.BIT_PIN
    try:
        supplier_gate.BIT_PIN = str(cap)
        application = apply(native, signed, guard, coefficients, conversion, supplier.physical,
                            claim, tested, lo, hi, cap)
    finally:
        supplier_gate.BIT_PIN = original_cap
    inherited.need(application["invoice"] == {"paid": weights["P"], "targets": weights["T"]},
                   "physical signed invoice")
    common = supplier.physical.root_envelope({"candidate": native, "comparator": base["native"]}, guard)
    guard_proofs = {name: supplier.physical.check_depth_guard(common, int(app["compiler"]["H"]))
                    for name, app in (("candidate", application), ("comparator", base["application"]))}
    return {"schema": "p104-iterated-returns-application/v1", "native_sha256": args.word_sha,
            "layout_sha256": args.layout_sha, "binary_word_sha256": args.binary_sha,
            "ordinary_binary": bits["ordinary_admitted"], "complex_raw": [lo, hi], "finite_lower": claim,
            "comparator_complex": base["native_sha256"], "comparator_raw": [old_lo, old_hi],
            "comparator_finite": base["finite_lower"], "target": constants[1],
            "gain_above_upper": str(Decimal(claim) - Decimal(old_hi)),
            "remaining_to_target": str(max(Decimal(0), Decimal(constants[1]) - Decimal(claim))),
            "native": native, "conversion": conversion, "caller": signed, "caller_proof": proof,
            "caller_guard": guard, "common_root": common, "joint_depth_guards": guard_proofs,
            "application": application}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("cache", "word", "layout", "binary-finite", "out"):
        p.add_argument("--" + key, required=True, type=Path)
    for key in ("word-sha", "layout-sha", "binary-sha"):
        p.add_argument("--" + key, required=True)
    p.add_argument("--shard", type=int, choices=(0, 1, 2))
    opts = p.parse_args()
    out = run(opts)
    opts.out.parent.mkdir(parents=True, exist_ok=True)
    opts.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("PASS", out.get("finite_lower", f"physical chart shard {opts.shard}"))
