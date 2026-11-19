#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the pinned f30 carrier and a fixed-boundary successor at the original BIT."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from math import gcd, isqrt, prod
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
DONOR = "f30aece9bbf9da00a428e61bc489dde0278f604b7cfd9fb3b1d2707990af2647"
DONOR_BRACKET = ("0.00384022183445", "0.00384022183446")
BIT = "0.00385248"
TARGET = "0.00383069832566"
ORIGINAL_UPPER = "0.00382069832566"
GRID = 10**14
CALLS = 48
BASE = "e54523517d0f03e58352e647c403a5af3e525a57"
BIT_CLAIM = Path("certificates/frontier7000/CLAIM.json")
BIT_CLAIM_SHA = "3f8add8252adb223b60418ec69351a69b6b5edfe601ec1c6b4b65cd9e2afd9b2"
BIT_SUPPLEMENT = Path("docs/research/pr-intake-evidence/pr7000-admission/check_bit_ambient.py")
BIT_PACKAGE = Path("research/paired-query-only-bit")
BIT_PRIMARY = BIT_PACKAGE / "check.py"
BIT_INDEPENDENT = BIT_PACKAGE / "independent/bit_review.py"
BIT_SOURCES = {
    BIT_SUPPLEMENT: "e8dabd0285c2ea84472a588a0f6f56e0a7865535ba5f0109db56b08cb7e79886",
    BIT_SUPPLEMENT.with_name("SOURCES.json"): "e7af347d42ee4931e1e4818213af6080a845a699bbdfea31330e136b42a16075",
    BIT_PRIMARY: "460ed9a77d66264b00c31d0a7f8dab1db9aab21ec4cc0eaf0452bd4be4ef585e",
    BIT_INDEPENDENT: "6db4b1657bac033ed526fb714b4830b51ae2260d2ce11c3ef0b9e907cadd47db",
}
ENGINES = Path("research/shared-wire-split-composition/frozen")
ENGINE_SHA = {
    "clifford_exact.py": "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    "native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
}
PREMISES = ["native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery"]
BOUNDARY = ("initial", "final", "frames", "first_output")


def need(ok, label):
    if not ok:
        raise ValueError(label)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def file_digest(path):
    return sha256(path.read_bytes()).hexdigest()


def save_report(path, report):
    staging = path.with_name(path.name + ".partial")
    staging.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    staging.replace(path)


def source_pins(donor, engines):
    source = json.loads((HERE / "DONOR-SOURCES.json").read_bytes())
    for name, pin in source["sha256"].items():
        need(file_digest(donor / name) == pin, f"changed public donor file {name}")
    for name, pin in ENGINE_SHA.items():
        need(file_digest(engines / name) == pin, f"changed Clifford engine {name}")
    return dict(repository=source["repository"], head=source["head"], path=source["path"],
                donor_manifest_sha256=file_digest(HERE / "DONOR-SOURCES.json"), engine_sha256=ENGINE_SHA)


def old_bit(repo):
    path = repo / BIT_CLAIM
    need(file_digest(path) == BIT_CLAIM_SHA, "admitted old BIT certificate changed")
    claim = json.loads(path.read_bytes())
    need(Fraction(claim["admitted_BIT_saving"]) == Fraction(BIT)
         and Fraction(claim["ordinary_BIT_saving"]) > Fraction(BIT)
         and [row["id"] for row in claim["assumptions"]] == PREMISES,
         "old BIT ordinary admission under the five premises")
    for source, pin in BIT_SOURCES.items():
        need(file_digest(repo / source) == pin, f"changed old BIT replay file {source}")

    def replay(script, *args):
        child = subprocess.run([sys.executable, "-I", "-B", str(script), *args], cwd=repo,
                               capture_output=True, text=True, check=True, timeout=120)
        return json.loads(child.stdout)

    primary = replay(BIT_PRIMARY)
    primary.pop("seconds", None)
    independent = replay(BIT_INDEPENDENT, "--efree", "--package", str(BIT_PACKAGE), "--out", "-")
    review = replay(BIT_SUPPLEMENT)
    bootstrap = review["bootstrap"]
    need(primary["status"] == "PASS_PAIRED_EFREE_BIT_EXISTING_00385248"
         and Fraction(primary["ordinary_admitted"]) == Fraction(BIT)
         and independent["status"] == "INDEPENDENT_BIT_REVIEW_PASS"
         and Fraction(independent["bootstrap"][-1]["admitted"]) == Fraction(BIT)
         and review["status"] == "PASS_PAIRED_BIT_134_AXIS_SUPPLEMENT"
         and Fraction(bootstrap[-1]["admitted"]) == Fraction(BIT)
         and Fraction(bootstrap[-1]["envelope"]) == Fraction(claim["ordinary_BIT_saving"])
         and Fraction(bootstrap[-1]["slack"]) > 0, "old BIT original 134-axis bootstrap")
    return dict(base=BASE, certificate=BIT_CLAIM.as_posix(), certificate_sha256=BIT_CLAIM_SHA,
                replay_sources={path.as_posix(): pin for path, pin in BIT_SOURCES.items()},
                admitted=BIT, ordinary=claim["ordinary_BIT_saving"],
                primary=primary, independent=independent, supplement=review)


def load_graph(path, pin):
    raw = path.read_bytes()
    if raw.startswith(b"\x1f\x8b"):
        with gzip.open(path, "rb") as source:
            raw = source.read(16 * 2**20 + 1)
    need(len(raw) <= 16 * 2**20, "frozen graph size limit")
    value = json.loads(raw)
    need(raw == canonical(value) and sha256(raw).hexdigest() == pin, "canonical frozen graph hash")
    return value


def graph_inputs(graph):
    need(graph.keys() == set(BOUNDARY) | {"forms", "moves", "schedule"}, "native graph fields")
    first, n = graph["first_output"], len(graph["initial"])
    moves = {k: (a, b) for k, a, b in graph["moves"]}
    rows = {k: [(i, Fraction(q)) for i, q in row] for k, row in graph["forms"]}
    schedule = graph["schedule"]
    need(len(moves) == len(graph["moves"]) and all(type(k) is int and 0 <= k < first for k in moves)
         and len(rows) == len(graph["forms"])
         and rows.keys() == moves.keys() | set(range(first, first+n))
         and len(schedule) == len(rows) and set(schedule) == rows.keys(), "complete literal row and bank catalogue")
    for (key, terms) in graph["forms"]:
        row = rows[key]
        need(all(type(d) is int and q and str(q) == literal for (d, q), (_, literal) in zip(row, terms, strict=True))
             and [d for d, _ in row] == sorted({d for d, _ in row}), f"canonical scalar incidence at {key}")
    return moves, rows


def count_caller(caller):
    from closed_caller import placement, templates
    from mixed_grid import census

    kinds = Counter(name for name, _ in placement(caller))
    need(kinds == {"A": 120, "rotated": 192}, "48-call caller census")
    targets, paid = Counter(), Counter()
    for name, (events, ends) in templates(caller).items():
        local_t, local_p, _, _ = census(events, ends)
        targets.update({r: n * kinds[name] for r, n in local_t.items()})
        paid.update({r: n * kinds[name] for r, n in local_p.items()})
    return targets, paid


def invoice(native, fixed):
    weights = {}
    for side, native_key, caller_side in (
        ("T", "positive_helper_ranks", fixed[0]), ("P", "paid_native_ranks", fixed[1])
    ):
        total = Counter({r: n * CALLS for r, n in native[native_key].items()})
        total.update(caller_side)
        weights[side] = dict(total)
    return weights


def dyadic_price(weights, price_point, bits=192):
    """Cross-check directed margins with bounded square roots on a dyadic grid.

    The enclosure uses the method in scripts/evaluate_recursive_power.py.
    """
    unit = 1 << bits
    exponent = 1 - Fraction(price_point)
    digits, remainder = divmod(exponent.numerator * unit, exponent.denominator)
    lower = upper = 0
    for rank in weights["T"].keys() | weights["P"].keys():
        count = weights["T"].get(rank, 0) - weights["P"].get(rank, 0)
        a = b = unit
        root_a = root_b = rank * unit
        for shift in reversed(range(bits)):
            root_a = isqrt(root_a * unit)
            radicand = root_b * unit
            root_b = isqrt(radicand)
            root_b += root_b * root_b < radicand
            if (digits >> shift) & 1:
                a = a * root_a // unit
                b = (b * root_b + unit - 1) // unit
        if remainder:
            b = (b * root_b + unit - 1) // unit
        lower += count * (a if count > 0 else b)
        upper += count * (b if count > 0 else a)
    return Fraction(lower, unit), Fraction(upper, unit)


def price(weights):
    from supplier_gate import moment, show, sub

    def value(q):
        return sub(moment(weights["T"], q), moment(weights["P"], q))

    def decimal(tick):
        return f"0.{tick:014d}"

    left, right = 0, int(Fraction("0.0069") * GRID)
    need(value(Fraction(left, GRID))[0] > 0 and value(Fraction(right, GRID))[1] < 0,
         "rank-power starting signs")
    while right - left > 1:
        mid = (left + right) // 2
        lower, upper = value(Fraction(mid, GRID))
        if lower > 0:
            left = mid
        else:
            need(upper < 0, "unresolved interval at a tested price")
            right = mid
    claim = min(left, int(Fraction(BIT) * GRID)) - 8
    lo, hi = decimal(left), decimal(right)
    probes = (lo, hi, decimal(claim), decimal(claim + 7), ORIGINAL_UPPER, TARGET, DONOR_BRACKET[1], BIT)
    independent = {probe: dyadic_price(weights, probe) for probe in probes}
    need(independent[lo][0] > 0 and independent[hi][1] < 0
         and independent[decimal(claim + 7)][0] > 0, "independent directed interval signs agree")
    return dict(claim=decimal(claim), tested=decimal(claim + 7), bracket=[lo, hi],
                signed_margins={k: show(value(Fraction(k))) for k in probes},
                independent_dyadic_margins={k: list(map(str, bounds)) for k, bounds in independent.items()})


def candidate_grid(physical, graph, moves, rows, coarse, expected):
    """Compute the minimum common entrance unit by testing each separate product."""
    n = len(graph["initial"])
    values = {~r: {r: coarse} for r in range(n)}
    product_gcd = snapshot_gcd = coarse
    count = nontrivial = 0
    peak = coarse
    decreases = []
    for key in graph["schedule"]:
        accum = {}
        mass = 0
        for donor, coefficient in rows[key]:
            a, b = coefficient.numerator, coefficient.denominator
            previous = values[donor]
            count += len(previous)
            if b != 1:
                nontrivial += len(previous)
            for column, v in previous.items():
                scaled, remainder = divmod(a * v, b)
                if remainder:
                    raise ValueError(f"coarse path grid exactness at {key}")
                if product_gcd > 1 and scaled % product_gcd:
                    reduced = gcd(product_gcd, scaled)
                    decreases.append(dict(row=key, donor=donor, input_owner=column, coefficient=str(coefficient),
                                          scaled_product=scaled, previous_gcd=product_gcd, gcd=reduced))
                    product_gcd = reduced
                mass += abs(scaled)
                result = accum.get(column, 0) + scaled
                if result:
                    accum[column] = result
                else:
                    accum.pop(column, None)
        peak = max(peak, mass)
        for value in accum.values():
            if snapshot_gcd > 1 and value % snapshot_gcd:
                snapshot_gcd = gcd(snapshot_gcd, value)
        if key in moves:
            values[key] = accum
        else:
            need(accum == expected[key-graph["first_output"]], f"all-column normalized endpoint {key}")
    grid = coarse // product_gcd
    _, height = physical.grid_parts(coarse)
    return dict(exact_all_public_rows=n, exact_source_columns=n, coefficient_products=count,
                checked_nontrivial_divisions=nontrivial, minimum_product_grid=grid,
                minimum_snapshot_grid=coarse // snapshot_gcd,
                maximum_exact_row_prefix_mass_scaled=str(Fraction(peak, 1 << height)),
                product_gcd_witnesses=decreases)


def factor_odd(odd):
    """Construct an explicit bounded conversion sequence for the derived grid."""
    limit = (1 << 24) - 1
    pending, atoms = odd, []
    divisor = 3
    while divisor <= limit and divisor * divisor <= pending:
        while not pending % divisor:
            atoms.append(divisor)
            pending //= divisor
        divisor += 2
    if pending > 1:
        need(pending <= limit, "odd product grid cannot use the retained bounded scalar components")
        atoms.append(pending)
    packed = []
    for factor in reversed(atoms):
        for j, prior in enumerate(packed):
            if factor * prior <= limit:
                packed[j] *= factor
                break
        else:
            packed.append(factor)
    need(prod(packed) == odd, "exact odd conversion factorization")
    return packed


def native_replay(supplier, graph, layout, owners, moves, rows, native, caller):
    physical = supplier.physical
    coarse = native["path_grid"]
    expected = physical.expected_rows(layout["public"], layout, owners, coarse)
    native.update(candidate_grid(physical, graph, moves, rows, coarse, expected))
    grid = native["minimum_product_grid"]
    odd, height = physical.grid_parts(grid)
    native.update(path_only_grid=coarse, path_grid=grid, path_grid_odd=odd, path_grid_height=height)
    need(moves, "nonempty native paid inventory")
    sender = physical.SURVIVOR
    if sender not in moves:
        physical.SURVIVOR = min(moves)
    try:
        expected = physical.expected_rows(layout["public"], layout, owners, grid)
        native.update(physical.held_schedule(graph, moves, rows, grid, expected, control=True),
                      live_sender_control_slot=physical.SURVIVOR)
    finally:
        physical.SURVIVOR = sender
    need(native["live_sender_alias_control_rejected"], "live sender overwrite fault rejected")
    factors = factor_odd(odd)
    cases = supplier.verify_conversions(layout["public"], grid, factors)
    scalars = physical.scalar_cases([rows], caller, (2025, *factors))
    return dict(odd_factors=factors, round_trips=cases, scalar_cases=scalars,
                partial_clear=physical.partial_clear_control())


def physical_catalogue(donor, the_graph, layout, mains, shard=0, shards=1):
    """Check all used signed relative routes and the 104 actual native main adapters."""
    import clifford_exact as producer
    import native_verify as checker

    frames = donor["frames"]
    donor_paid = {k: (a, b) for k, a, b in donor["moves"]}
    current_paid = {k: (a, b) for k, a, b in the_graph["moves"]}
    helpers = {(a, b) for r, (a, b) in enumerate(zip(donor["initial"], donor["final"], strict=True)) if r not in mains}
    donor_pairs = set(donor_paid.values()) | helpers
    candidate_pairs = set(current_paid.values()) | helpers
    union = donor_pairs | candidate_pairs
    changed = {pair for k, pair in current_paid.items() if donor_paid.get(k) != pair}
    dense = set(sorted(donor_pairs)[:3]) | ({(3, 288), (767, 127)} & donor_pairs) | changed
    selected_pairs = sorted(union)[shard::shards]
    dense.add(selected_pairs[0])
    records = []
    dense_records = []

    @cache
    def compile_frame(i):
        return producer.canonical_frame(9, tuple(frames[i]))

    @cache
    def check_frame(i):
        return checker.frame(tuple(frames[i]), 9)

    for index, (a, b) in enumerate(selected_pairs, 1):
        recipe, _ = producer.lower_child(compile_frame(a).adjoint().then(compile_frame(b)))
        need(recipe["rank"] == abs(len(frames[a])-len(frames[b])) > 0, f"charged physical rank at {(a,b)}")
        actual = checker.recipe(recipe)
        expected = checker.adjoint(check_frame(a)) + check_frame(b)
        checker.equal(actual, expected, f"signed action and absolute phase at {(a,b)}")
        digest = sha256(canonical(recipe)).hexdigest()
        records.append([a, b, digest])
        if (a, b) in dense:
            for observed, reference in ((actual, expected), (checker.adjoint(actual), checker.adjoint(expected))):
                need(all(checker.state(observed, j) == checker.state(reference, j) for j in range(512)),
                     f"literal forward and adjoint Gaussian equality at {(a,b)}")
            broken = deepcopy(recipe)
            broken["left"]["phase"] = (broken["left"]["phase"] + 1) % 4
            try:
                checker.equal(checker.recipe(broken), expected, "altered global phase")
            except ValueError as error:
                need(str(error) == "altered global phase: exact global phase", "wrong phase control failure")
            else:
                raise ValueError("altered physical phase accepted")
            dense_records.append([a, b, digest])
        if index % 500 == 0:
            print("checked relative chart pairs", index, "/", len(selected_pairs), flush=True)

    selected_ports = list(zip(layout["live"], layout["ports"], strict=True))[shard::shards]
    for x, q in selected_ports:
        a, b = donor["initial"][x], donor["final"][x + 112]
        first, _ = producer.lower_child(producer.cgate(9, q, 1).adjoint().then(compile_frame(a)))
        last, _ = producer.lower_child(compile_frame(b).adjoint().then(producer.cgate(9, q, -1).then(producer.fourier(9))))
        need(first["rank"] == last["rank"] == 0, "ordinary main adapters")
        checker.equal(checker.recipe(first), (("C", q, -1),) + check_frame(a), "main entrance phase")
        checker.equal(checker.recipe(last), checker.adjoint(check_frame(b)) + (("C", q, -1),) + checker.fourier(9),
                      "main exit phase")
        checker.equal(check_frame(donor["final"][x]), checker.fourier(9), "main Fourier exit")
    return dict(donor_pairs=len(donor_pairs), candidate_pairs=len(candidate_pairs), union_pairs=len(union),
                shard=shard, shards=shards, checked_pairs=len(records),
                absolute_main_port_adapters=len(selected_ports), new_pairs=sorted(candidate_pairs-donor_pairs),
                changed_paid_route_pairs=sorted(changed), dense_checks=dense_records,
                forward_and_adjoint_gaussian_columns=len(dense_records)*1024,
                altered_global_phase_rejected=True, checked_pairs_sha256=sha256(canonical(records)).hexdigest())


def qualify(supplier, graph, layout, owners, maps, native, price_result, caller, verified):
    from closed_application import apply

    signed, guard, _, coefficients = verified
    conversion = native_replay(supplier, graph, layout, owners, *maps, native, caller)
    print("native exact and guarded", len(graph["initial"]), len(graph["moves"]), native["path_grid"], flush=True)
    result = apply(native, signed, guard, coefficients, conversion["scalar_cases"]["coefficient_bits"],
                   supplier.physical, price_result["claim"], price_result["tested"], *price_result["bracket"], BIT)
    ordinary = result["ordinary"]
    extra = ordinary["raw_scalar_incidence_allowance_before_factor_32"]
    extra["additional_odd_factor_steps"] = max(0, len(conversion["odd_factors"])-1) * ordinary["odd_conversions"]
    ordinary["scalar_services"] = 32 * sum(extra.values())
    need(result["invoice"] == {"targets": price_result["invoice"]["T"], "paid": price_result["invoice"]["P"]},
         "preprice and complete physical signed invoice agree")
    return dict(native=native, conversion=conversion, application=result)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--donor", type=Path, required=True, help="complex/ from Ali Romman's pinned public package")
    p.add_argument("--repo", type=Path, required=True, help="checkout containing the selected #7000 BIT admission")
    p.add_argument("--engines", type=Path, help="override the frozen Clifford engine directory")
    p.add_argument("--graph", type=Path, help="candidate canonical native graph, JSON or gzip")
    p.add_argument("--graph-sha256", help="SHA-256 of the candidate's canonical JSON bytes")
    p.add_argument("--out", type=Path, required=True)
    scope = p.add_mutually_exclusive_group()
    scope.add_argument("--price-only", action="store_true", help="directed complete invoices without physical replay")
    scope.add_argument("--application-only", action="store_true", help="replay the native and compiler application")
    scope.add_argument("--chart-shard", choices=range(3), type=int, help="check one third of the used chart and adapter catalogue")
    args = p.parse_args()
    need(sys.flags.optimize == 0, "interval and source assertions require Python without -O")
    need(bool(args.graph) == bool(args.graph_sha256), "provide frozen candidate and its hash together")

    donor_path, repo = args.donor.resolve(), args.repo.resolve()
    engines = (args.engines or repo / ENGINES).resolve()
    pins = source_pins(donor_path, engines)
    sys.path[:0] = [str(donor_path), str(engines)]
    import supplier
    from closed_application import verify_caller

    donor, layout, _ = supplier.build()
    need(sha256(canonical(donor)).hexdigest() == DONOR, "independent full donor reconstruction hash")
    candidate = load_graph(args.graph, args.graph_sha256) if args.graph else None
    if candidate is not None:
        need(all(candidate[k] == donor[k] for k in BOUNDARY), "fixed f30 public charts, ownership and namespaces")
    host = layout["hosted"]
    mains = set(layout["live"]) | {r+112 for r in layout["live"]} | set(host["X2"]) | set(host["Y2"])
    need(len(mains) == 400 and len(layout["source_labels"]) == len(set(layout["source_labels"])) == layout["public"] == 1264,
         "400 real main owners, 864 independent helpers")
    owners = mains, set(host["Dports"]), list(zip(host["X2"], host["Y2"], strict=True))
    caller = supplier.read(supplier.SOURCE / "data/CALLER.json.gz")
    fixed = count_caller(caller)
    graphs = {"donor": donor}
    if candidate is not None:
        graphs["candidate"] = candidate
    reports = {}
    native_inputs = {}
    for name, graph in graphs.items():
        moves, rows = graph_inputs(graph)
        native = supplier.physical.graph_bounds(graph, moves, rows, mains)
        weights = invoice(native, fixed)
        result = price(weights)
        result.update(invoice=weights, graph_sha256=sha256(canonical(graph)).hexdigest(),
                      native_paid_ranks=native["paid_native_ranks"], native_helper_ranks=native["positive_helper_ranks"])
        native_inputs[name] = ((moves, rows), native, result)
        reports[name] = result
        print(name, "directed raw interval", result["bracket"], "claim", result["claim"], flush=True)
    need(tuple(reports["donor"]["bracket"]) == DONOR_BRACKET, "independent directed f30 comparator bracket")
    if candidate is not None:
        old, new = reports["donor"], reports["candidate"]
        need(new["invoice"]["T"] == old["invoice"]["T"], "unchanged complete productive histogram")
        ranks = old["native_paid_ranks"].keys() | new["native_paid_ranks"].keys()
        new["native_paid_delta"] = {r: new["native_paid_ranks"].get(r, 0)-old["native_paid_ranks"].get(r, 0)
                                    for r in sorted(ranks) if new["native_paid_ranks"].get(r, 0) != old["native_paid_ranks"].get(r, 0)}
    report = dict(schema="p104-common-old-bit-qualification/v1", status="priced",
                  sources=pins, layout_sha256=sha256(canonical(layout)).hexdigest(),
                  BIT=BIT, target=TARGET, original_comparator_upper=ORIGINAL_UPPER,
                  five_premises=PREMISES, price=reports)
    if candidate is not None:
        claim = Fraction(reports["candidate"]["claim"])
        report["directed_candidate_gains"] = {
            "above_f30_upper": str(claim - Fraction(DONOR_BRACKET[1])),
            "above_original_upper": str(claim - Fraction(ORIGINAL_UPPER)),
            "above_original_target": str(claim - Fraction(TARGET)),
        }
        report["strict_candidate_gain"] = claim > Fraction(DONOR_BRACKET[1]) and claim > Fraction(TARGET)
    save_report(args.out, report)
    if args.price_only:
        return
    need(candidate is None or report["strict_candidate_gain"], "priced candidate fails directed gain gate")
    if args.chart_shard is not None:
        report["physical_catalogue"] = physical_catalogue(donor, candidate or donor, layout, mains, args.chart_shard, 3)
        report["status"] = "chart_shard_passed"
        save_report(args.out, report)
        print("PASS_COMMON_ORIGINAL_BIT_CHART_SHARD", args.chart_shard, flush=True)
        return

    report["original_BIT_admission"] = old_bit(repo)
    verified = verify_caller(caller, donor, layout, supplier.read(supplier.SOURCE / "data/CALLER-PHASE-BASES.json"))
    signed, guard, proof, _ = verified
    report["caller"] = dict(invoice=signed, guard=guard, proof=proof)
    need(signed["calls"] == CALLS and dict(fixed[0]) == signed["fixed_root_targets"]
         and dict(fixed[1]) == signed["fixed_caller_paid"], "expanded exact signed caller matches preprice")
    print("closed caller", proof["readback"]["events"], "emitted events", flush=True)
    report["qualified"] = {}
    for name, graph in graphs.items():
        report["qualified"][name] = qualify(supplier, graph, layout, owners, *native_inputs[name], caller, verified)
    shared_root = supplier.physical.root_envelope({name: item["native"] for name, item in report["qualified"].items()}, guard)
    report["common_root"] = shared_root
    report["common_depth_guards"] = {
        name: supplier.physical.check_depth_guard(shared_root, int(item["application"]["compiler"]["H"]))
        for name, item in report["qualified"].items()
    }
    report["status"] = "application_passed"
    save_report(args.out, report)
    if args.application_only:
        print("PASS_COMMON_ORIGINAL_BIT_APPLICATION", BIT, flush=True)
        return
    report["physical_catalogue"] = physical_catalogue(donor, candidate or donor, layout, mains)
    report["status"] = "passed"
    save_report(args.out, report)
    print("PASS_COMMON_ORIGINAL_BIT", BIT, [(key, value["claim"]) for key, value in reports.items()], flush=True)


if __name__ == "__main__":
    main()
