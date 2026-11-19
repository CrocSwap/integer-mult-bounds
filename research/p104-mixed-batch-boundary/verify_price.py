#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the signed P104 price of 2,048 contiguous calls against two 1,024-call copies."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path
import sys


SOURCE_HEAD = "6b0044123aad114cf71ca2bb0e98741e5a27c7b5"
GRAPH_SHA256 = "c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84"
SOURCE_WORD = "d82aa7d2ac4974f58b8a4e9f15a8ec9286bc79e26ab5d53f9d748db9f9a04ca8"
COMPARATOR_BRACKET = ("0.00382063778176", "0.00382063778177")
TARGET = "0.00382065"
BIT_PIN = "0.00385248"
BRACKET_DIGITS = 14
POWER_BITS = 256
FILENAMES = {
    "EDITS.json": "7ced0e7a5d39f1ebc1468899e1f66da84d2f7160d8c979763ee33bcd2e6e93c0",
    "SOURCE-PINS.json": "78c1dc981a4ab6878422230a017297cd6f84540c58316854a3a13abd0bb02e7f",
    "SOURCES.json": "76818b74ee05a1a562813b1385b3609dea2bb548c260ebda1b3f8a7aeab236c9",
    "common.py": "8638ebe074926f5afa9ccd7edc4c9fda827261fb3c1a1b75ed703ff7089df258",
    "construction.py": "037c66277636cf5cd860e88f4f5998de46d34c726280c787fcb9f611091d634b",
    "data/CONJUGATE-CALLER.json.gz": "80009663da460229a57f09bde90e35294329a210ae7fc7ef6d1f05b61ffccbf4",
    "linear.py": "bc0aaa0e4ce28260907d29083e4f788e08ae60f050800257b39d1070d545e30e",
    "mixed_application.py": "e762a61f48411dff22117ce1a5154e8e530341f61d5264afeb839b398dd8345e",
    "mixed_caller.py": "4824b2aaadb592550d3a25c16ff0a453705e10b8868f5c22fe10c2874bcb9bae",
    "mixed_geometry.py": "5a7f8ed2deb6b9f8253372539b452b94ce15847200e4bf4b3721447b00362e70",
    "mixed_grid.py": "95b0526530467e84e1dd295e98fb1442d68e97a724b1b8724d04fcd2284d646b",
    "native.py": "3070ab83ed086e22340f58d5b63f3c313bc615aa9ddb4d00cb2e40c54d31febe",
    "results/application.json": "c736b04bed2be2e597cdc807dec38600008d80e8612e995f6d3a5c1df52f095d",
    "results/batch.json": "ca42f4298567752fe8b475295425271d428829d07cd3521ed8e4ed2f371dec35",
    "results/witness.json": "2709d9f3f8af7b1f5111ab86f6bb9b70be80ab1f37c0b36ae8a3b557f1d40a87",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def bind_source(source, scripts):
    """Check the public-head file bytes before importing any reused source."""
    def check(path, digest, blob=None):
        raw = path.read_bytes()
        require(sha256(raw).hexdigest() == digest, f"SHA-256 mismatch for {path.name}")
        if blob:
            git_data = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
            require(sha1(git_data).hexdigest() == blob, f"Git blob mismatch for {path.name}")

    for path, digest in FILENAMES.items():
        check(source / path, digest)
    vendor_pins = read_json(source / "SOURCE-PINS.json")
    for entry in vendor_pins:
        check(source / entry["path"], entry["sha256"], entry["git_blob"])

    external = read_json(source / "SOURCES.json")["files"]
    script_pins = [entry for entry in external if entry["path"].startswith("scripts/")]
    require({Path(entry["path"]).name for entry in script_pins} == {
        "compare_recursive_invoices.py", "evaluate_recursive_power.py"
    }, "comparison script inventory")
    for entry in script_pins:
        check(scripts / Path(entry["path"]).name, entry["sha256"], entry["git_blob"])
    return {
        "head": SOURCE_HEAD,
        "unchanged_native_graph_sha256": GRAPH_SHA256,
        "deposited_1024_event_stream_sha256": SOURCE_WORD,
        "package_sha256": FILENAMES,
        "retained_file_count": len(vendor_pins),
        "canonical_script_pins": script_pins,
    }


def template_profiles(source, caller):
    """Read paid operations and signed terminals directly from the two caller files."""
    def local_profile(events, endpoints, color_base):
        paid, targets, ordinary_uses = Counter(), Counter(), Counter()
        gaussian_uses = negative_targets = 0
        valid_colors = set(range(color_base, 16 + color_base))
        for phase, mask in endpoints:
            require(phase in (-1, 1) and set(mask) <= valid_colors and
                    0 < len(mask) == len(set(mask)), "terminal phase or body mask")
            targets[1 + 8 * len(mask)] += 1
            negative_targets += phase < 0
        for op, _, *args in events:
            ordinary_uses[op] += 1
            if op == "QUERY":
                require(len(args) == 2 and args[1] in (-1, 1), "QUERY head")
                paid[1] += 1
            elif op in ("IDLE_ONE", "IDLE_ODD"):
                mask, *sign = args
                require(0 < len(mask) == len(set(mask)) and set(mask) <= valid_colors,
                        "IDLE body mask")
                odd = op == "IDLE_ODD"
                require(sign in ([-1], [1]) if odd else not sign, "IDLE head")
                paid[8 * len(mask) + odd] += 1
            elif op in ("ADD", "SCALE"):
                coeff = args[-1]
                if isinstance(coeff, list):
                    gaussian_uses += Fraction(coeff[1]) != 0
            else:
                require(op in ("SWAP", "LAMBDA"), f"unknown caller operation {op}")
        return {
            "paid": paid,
            "targets": targets,
            "uses": ordinary_uses,
            "negative_targets": negative_targets,
            "gaussian_uses": gaussian_uses,
        }

    profiles = {}
    require(caller["types"].keys() == {"A", "B"}, "legacy caller types")
    for kind, spec in caller["types"].items():
        endpoints = []
        for phase, scalar, *bits in spec["diagonal"]:
            require(scalar == 0 and len(bits) == 16 and set(bits) <= {0, 1}, "terminal support")
            endpoints.append((phase, [color for color, bit in enumerate(bits, 1) if bit]))
        require(len(endpoints) == spec["roles"], "legacy caller owner count")
        profiles[kind] = local_profile(
            (e[1:] for e in caller["events"] if e[0] == kind), endpoints, 1
        )
    mixed = read_json(source / "data/CONJUGATE-CALLER.json.gz")
    hosts = [(e[0], e[1]) for e in mixed["events"] if e[0].startswith("HOST_")]
    sequence = ["HOST_A"] * 7 + ["HOST_B"] * 2 + ["HOST_A"] * 7
    require(hosts == list(zip(sequence, range(16))) and mixed["roles"] == len(mixed["diagonal"]),
            "mixed template visits and owners")
    profiles["mixed"] = local_profile(
        (e for e in mixed["events"] if not e[0].startswith("HOST_")), mixed["diagonal"], 0
    )
    return profiles


def weighted_profiles(profiles, counts, field):
    aggregate = Counter()
    for kind, count in counts.items():
        aggregate.update({r: multiplicity * count for r, multiplicity in profiles[kind][field].items()})
    return +aggregate


def construct_invoice(contract, native, profiles, calls, roots):
    invoice = {"schema": "integer-mult-recursive-invoice/v1", "contract": contract}
    for side in ("paid", "targets"):
        histogram = Counter({r: n * calls for r, n in native[side].items()})
        histogram.update(weighted_profiles(profiles, roots, side))
        invoice[side] = {str(r): histogram[r] for r in sorted(histogram)}
    return invoice


def difference(new, old):
    return {
        r: new.get(r, 0) - old.get(r, 0)
        for r in new.keys() | old.keys()
        if new.get(r, 0) != old.get(r, 0)
    }


def scaled_decimal(n, decimals):
    whole, fraction = divmod(abs(n), 10**decimals)
    return f"{'-' if n < 0 else ''}{whole}.{fraction:0{decimals}d}"


def enclosure(interval, decimals=24):
    low, high = interval
    scale = 10**decimals
    return {
        "lower": str(low),
        "upper": str(high),
        "decimal_bounds": [
            scaled_decimal(low * scale // 1, decimals),
            scaled_decimal(-(-high * scale // 1), decimals),
        ],
    }


def weight(histogram, point, power_bounds):
    lower = upper = Fraction(0)
    exponent = 1 - Fraction(point)
    for rank, count in histogram.items():
        lo, hi = power_bounds(int(rank), exponent, POWER_BITS)
        lower += count * (lo if count > 0 else hi)
        upper += count * (hi if count > 0 else lo)
    return lower, upper


def opposite(interval):
    return -interval[1], -interval[0]


def bracket(margin):
    scale = 10**BRACKET_DIGITS
    lo, hi = (int(Fraction(point) * scale) for point in (TARGET, BIT_PIN))
    require(margin(Fraction(lo, scale))[0] > 0 and margin(Fraction(hi, scale))[1] < 0,
            "missing directed crossing signs")
    while hi - lo > 1:
        midpoint = (lo + hi) // 2
        lower, upper = margin(Fraction(midpoint, scale))
        if lower > 0:
            lo = midpoint
        else:
            require(upper < 0, "unresolved directed midpoint")
            hi = midpoint
    return lo, hi


def integer_histogram(histogram):
    return Counter({int(rank): count for rank, count in histogram.items()})


def normalized(invoice, calls):
    return {side: {r: str(Fraction(n, calls)) for r, n in invoice[side].items()}
            for side in ("paid", "targets")}


def prove_price(source, scripts):
    pins = bind_source(source, scripts)
    sys.path[:0] = [str(source), str(source / "vendor"), str(scripts)]
    from common import digest, inputs, jobs, physical
    from compare_recursive_invoices import compare_invoices, validate_invoice
    from evaluate_recursive_power import power_bounds
    from interval_gate_signed import B, add, gate, log, mul, power, smul
    from mixed_application import check_components, ordinary_for_batch
    from mixed_caller import layout_bindings, place_roots, split_templates
    from mixed_geometry import contact_atlas, masks_and_contacts
    from native import selected_interfaces

    original = read_json(source / "results/application.json")
    witness = read_json(source / "results/witness.json")
    emitted = read_json(source / "results/batch.json")["expansion"]
    require(emitted["event_stream_sha256"] == SOURCE_WORD and emitted["native_calls"] == 1024,
            "deposited comparator emitter receipt")
    graph, layout, moves, _, (main, _, _) = inputs()
    require(digest(graph) == witness["graph_sha256"] == original["graph_sha256"] == GRAPH_SHA256,
            "pinned native graph")
    frames = graph["frames"]
    native_paid = Counter(abs(len(frames[a]) - len(frames[b])) for a, b in moves.values())
    native_targets = Counter(
        len(frames[b]) - len(frames[a])
        for r, (a, b) in enumerate(zip(graph["initial"], graph["final"], strict=True))
        if r not in main
    )
    graph_paid, graph_targets, _ = jobs(graph, main, moves)
    native_model = original["physical"]["native"]
    require(
        native_paid == graph_paid == dict(witness["paid"]) == integer_histogram(native_model["paid_native_ranks"])
        and native_targets == graph_targets == dict(witness["productive"])
        == integer_histogram(native_model["positive_helper_ranks"]),
        "rebuilt native rank counts and two deposited records",
    )
    native = {"paid": native_paid, "targets": native_targets}
    caller = read_json(source / "data/CALLER.json.gz")
    profiles = template_profiles(source, caller)
    words = split_templates(caller)
    atlas = contact_atlas(layout, read_json(source / "data/CALLER-PHASE-BASES.json"))
    components = check_components(caller, physical, original["physical"]["scalars"]["coefficient_bits"])
    require(components == original["physical"]["components"], "retained scalar service model")
    contract = original["invoice"]["contract"]

    def replay_batch(calls):
        roots = place_roots(caller, calls)
        _, offsets, binding = layout_bindings(words, roots, layout, calls)
        counts = binding["template_roots"]
        require(counts == {"A": 5*calls//2+56, "B": 8, "mixed": 4*calls-64},
                "finite optimal placement counts")
        paid = weighted_profiles(profiles, counts, "paid")
        targets = weighted_profiles(profiles, counts, "targets")
        uses = weighted_profiles(profiles, counts, "uses")
        physical_paid, physical_targets, contacts = masks_and_contacts(words, roots, offsets, atlas)
        require((physical_paid, physical_targets) == (paid, targets) and
                contacts["canonical_normalizers"] == uses["LAMBDA"], "per-owner physical-axis price")
        require(binding["root_owners"] == sum(targets.values()), "all caller targets priced")
        signed = {
            "calls": calls,
            "uses": uses,
            "fixed_caller_paid": paid,
            "fixed_root_targets": targets,
            "root_owners": binding["root_owners"],
            "root_negative_q": sum(n * profiles[k]["negative_targets"] for k, n in counts.items()),
            "gaussian_literal_uses": sum(n * profiles[k]["gaussian_uses"] for k, n in counts.items()),
        }
        invoice = validate_invoice(construct_invoice(contract, native, profiles, calls, counts))
        ordinary = ordinary_for_batch(native_model, signed, components["coefficient_bits"])
        require(
            (sum(invoice["paid"].values()), sum(invoice["targets"].values()))
            == (ordinary["raw_paid_positions"], ordinary["raw_productive_targets"]),
            "ordinary model and complete recursive counts",
        )
        return invoice, signed, binding, contacts, ordinary

    base, base_signed, base_binding, base_contacts, base_ordinary = replay_batch(1024)
    new, new_signed, new_binding, new_contacts, new_ordinary = replay_batch(2048)
    source_sides = {"fixed_caller_paid", "fixed_root_targets"}
    original_signed = original["caller"]
    require(base == original["invoice"] and base_binding == original_signed["finite_binding"]
            and base_ordinary == original["physical"]["ordinary"], "exact 1024 application reconstruction")
    require(base_contacts == original["physical"]["caller_word"]["common_head_and_masks"],
            "1024 original physical-axis receipt")
    for side in source_sides:
        require(base_signed[side] == integer_histogram(original_signed[side]), f"1024 {side}")
    require(base_signed["uses"] == original_signed["uses"], "1024 literal operation totals")
    require(emitted["op_counts"] == dict(base_signed["uses"], NATIVE=1024, PORT_VIEWS=2048)
            and emitted["emitted_events"] == sum(emitted["op_counts"].values()),
            "deposited 1024 caller operation totals")

    base_roots, new_roots = base_binding["template_roots"], new_binding["template_roots"]
    copied_roots = {kind: 2 * n for kind, n in base_roots.items()}
    old = construct_invoice(contract, native, profiles, 2048, copied_roots)
    require(all(old[side] == {r: 2*n for r, n in base[side].items()} for side in ("paid", "targets")),
            "two copies of the exact comparator invoice")
    require(difference(new_roots, copied_roots) == {"A": -56, "B": -8, "mixed": 64},
            "literal root exchange")
    comparison = compare_invoices(old, new)
    require(comparison["delta_paid"] == {"1": -224, "8": -224, "9": -32}
            and comparison["delta_targets"] == {"9": -256}
            and comparison["power_moment"]["new_minus_old_sign"] == "strictly_negative",
            "strict signed rank exchange")

    def margin_fn(invoice):
        net = difference(invoice["targets"], invoice["paid"])
        return lambda point: weight(net, point, power_bounds)

    old_margin, new_margin = margin_fn(old), margin_fn(new)
    base_lo, base_hi = COMPARATOR_BRACKET
    require(original["bracket"] == [base_lo, base_hi] and
            old_margin(base_lo)[0] > 0 > old_margin(base_hi)[1], "source comparator bracket")
    old_at_target, new_at_target = old_margin(TARGET), new_margin(TARGET)
    net_credit = weight({1: 224, 8: 224, 9: -224}, TARGET, power_bounds)
    deficit = opposite(old_at_target)
    require(deficit[0] > 0 and net_credit[0] > deficit[1] and new_at_target[0] > 0,
            "insufficient directed credit at target")

    lo, hi = bracket(new_margin)
    claim, probe, low, high = (scaled_decimal(k, BRACKET_DIGITS) for k in (lo-8, lo-1, lo, hi))
    require(Fraction(base_hi) < Fraction(TARGET) < Fraction(claim) and
            new_margin(claim)[0] > 0 and new_margin(probe)[0] > 0, "successor onset")

    def compiler(invoice, probe, claim, bracket):
        tar = {"P": integer_histogram(invoice["paid"]), "T": integer_histogram(invoice["targets"])}
        return gate(tar, claim, probe, *bracket, BIT_PIN)

    require(selected_interfaces() == original["conditional_interfaces"], "selected conditional interfaces")
    require(compiler(base, original["probe"], original["claim"], COMPARATOR_BRACKET)
            == original["compiler"], "exact source compiler gate")
    compiler_report = compiler(new, probe, claim, (low, high))

    # Every B port in the first call needs a homogeneous B root. Extra B roots cost margin.
    # The emitted schedule meets this lower bound. Removing the single finite boundary
    # loss gives the limiting inventory per block of sixteen native calls.
    ideal = construct_invoice(contract, native, profiles, 16, {"A": 40, "mixed": 64})
    def limiting_loss(invoice, calls):
        ideal_net = difference(ideal["targets"], ideal["paid"])
        unbounded_net = {r: n * (calls // 16) for r, n in ideal_net.items()}
        finite_net = difference(invoice["targets"], invoice["paid"])
        return difference(unbounded_net, finite_net)

    require(limiting_loss(base, 1024) == limiting_loss(new, 2048) == {"1": 224, "8": 224, "9": -224},
            "one finite boundary penalty versus the ideal inventory")
    ideal_margin = margin_fn(ideal)
    limit_bracket = [scaled_decimal(k, BRACKET_DIGITS) for k in bracket(ideal_margin)]
    derivative = (0, 0)
    for rank, count in difference(ideal["targets"], ideal["paid"]).items():
        rank = int(rank)
        endpoint = Fraction(BIT_PIN) if count > 0 else Fraction(0)
        derivative = add(derivative, smul(mul(power(rank, endpoint), log(rank)), -count))
    require(derivative[1] < 0 and Fraction(high) < Fraction(limit_bracket[0]),
            "monotone limiting crossing and remaining fixed-template headroom")

    return {
        "schema": "p104-contiguous-caller-price/v1",
        "status": "passed",
        "source": pins,
        "power": {"tariff": "r^(1-kappa)", "dyadic_grid_bits": POWER_BITS,
                  "signed_margin": "productive minus paid", "compiler_weights_cap": BIT_PIN},
        "template_profiles": profiles,
        "native_ranks_per_call": native,
        "source_1024": {
            "invoice": base, "roots": base_roots, "binding": base_binding,
            "ordinary": base_ordinary,
            "deposited_emitter_operations": emitted["emitted_events"],
            "deposited_compiler_reproduced": True,
        },
        "two_1024_copies": {
            "invoice": old, "roots": copied_roots, "raw_bracket": COMPARATOR_BRACKET,
            "histograms_per_native_call": normalized(old, 2048),
            "bracket_signs": {point: enclosure(old_margin(point)) for point in COMPARATOR_BRACKET},
        },
        "contiguous_2048": {
            "invoice": new, "roots": new_roots, "binding": new_binding,
            "physical_axes": new_contacts, "literal_uses": new_signed["uses"], "ordinary": new_ordinary,
            "histograms_per_native_call": normalized(new, 2048),
            "claim": claim, "probe": probe, "raw_bracket": [low, high],
            "signed_margins": {point: enclosure(new_margin(point)) for point in (base_hi, claim, probe, low, high)},
            "gain_over_comparator_upper": scaled_decimal(int((Fraction(claim)-Fraction(base_hi))*10**14), 14),
            "conditional_interfaces": original["conditional_interfaces"],
            "compiler": compiler_report,
        },
        "rank_comparison": comparison,
        "comparison_at_target": {
            "kappa": TARGET,
            "two_copy_deficit": enclosure(deficit),
            "paid_savings": enclosure(weight({"1": 224, "8": 224, "9": 32}, TARGET, power_bounds)),
            "surrendered_target_cost": enclosure(weight({"9": 256}, TARGET, power_bounds)),
            "net_seam_credit": enclosure(net_credit),
            "net_seam_credit_per_native_call": enclosure(tuple(b/2048 for b in net_credit)),
            "contiguous_surplus": enclosure(new_at_target),
        },
        "fixed_template_limit": {
            "scope": "Identical chart, 96 A and 8 B ports per call, occupancy at every call, and the three pinned sixteen-visit templates with chronological visits and distinct colors.",
            "minimum_homogeneous_B_roots": 8,
            "optimal_roots_16n_calls": {"A": "40n+56", "B": "8", "mixed": "64n-64"},
            "signed_gain_per_replaced_B": "28*(1 + 8^(1-kappa) - 9^(1-kappa))",
            "finite_batch_signed_loss": "224*(1 + 8^(1-kappa) - 9^(1-kappa))",
            "limiting_invoice_per_16_calls": ideal,
            "raw_bracket": limit_bracket,
            "bracket_signs_per_16_calls": {point: enclosure(ideal_margin(point)) for point in limit_bracket},
            "derivative_upper_through_BIT_pin": str(Fraction(derivative[1], B)),
            "raw_headroom_upper_over_2048_claim": scaled_decimal(
                int((Fraction(limit_bracket[1])-Fraction(claim))*10**14), 14
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="pinned PR #7756 package directory")
    parser.add_argument("--scripts", type=Path, required=True, help="pinned canonical scripts directory")
    parser.add_argument("--output", type=Path, help="write the verification receipt to this path")
    args = parser.parse_args()
    require(__debug__, "run without -O so the compiler gate assertions execute")
    sys.dont_write_bytecode = True
    receipt = prove_price(args.source.resolve(), args.scripts.resolve())
    result = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
