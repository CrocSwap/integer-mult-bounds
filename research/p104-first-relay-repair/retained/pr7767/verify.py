#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify the P104 relay and restoration differentials, exact rows and signed price."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import cache
from graphlib import CycleError, TopologicalSorter
from hashlib import sha256
from math import isqrt
from pathlib import Path
import gzip
import json
import subprocess
import sys
import tempfile

PARENT_HEAD = "d5219594c9b0e80c002a75e79b85766256496b07"
NATIVE_HEAD = "6b0044123aad114cf71ca2bb0e98741e5a27c7b5"
PARENT_GRAPH = "c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84"
JOINT_GRAPH = "91af585f71ff53cf5771d532f90b5f3f4acb21abaf9381d219539a679f2969db"
DIFFERENTIAL = "a0c386cbb7d777cea8638a4b6d99aa60342c69e30683762bf1dae60110253ebf"
STACK_GRAPH = "eb8a9cbf477308f8baa949a780a5a3b6d998ff9a64934591839a4b5690186702"
STACK_DIFFERENTIAL = "664da8fec58eacb6bb205f5baf884af76af1a98e9bad33edcf764093bb4d2f92"
PRICE = "9d7cb0ebcf4a83b9ffa2596c4a1c178b79c9fa91a6a54b195be3083b411726f6"
CALLER = "3b326189234984d7797566fa4732d4e2698db778f117cd09bb5654ea740c5563"
BRACKETS = {"nine": ("0.00382275513694", "0.00382275513695"),
            "seventeen": ("0.00382815604916", "0.00382815604917")}
PAID_DELTAS = {"nine": {1: -14, 2: 9, 3: -2, 6: -2, 7: 2},
               "seventeen": {1: -14, 2: 1, 3: -2, 4: -8, 6: 6, 7: 2}}
TARGET = "0.00383069832566"
BIT = "0.00385248"
CALLS = 2048
GRID = 5_558_973_235_200
GRAPH_LIMIT = 16 * 2**20
HERE = Path(__file__).resolve().parent
GRAPH_FIELDS = {"first_output", "frames", "initial", "final", "moves", "forms", "schedule"}
PATCH_FIELDS = {
    "schema", "parent_graph_sha256", "joint_graph_sha256", "deleted_moves",
    "relocated_hub_moves", "rerouted_moves", "scalar_form_changes", "schedule",
}
STACK_FIELDS = PATCH_FIELDS - {"relocated_hub_moves", "rerouted_moves"} | {"added_moves"}
CONSTRUCTOR_FILES = {
    "construction.py": "037c66277636cf5cd860e88f4f5998de46d34c726280c787fcb9f611091d634b",
    "linear.py": "bc0aaa0e4ce28260907d29083e4f788e08ae60f050800257b39d1070d545e30e",
    "vendor/network.py": "a9169fd6ad0a13c69cf39bd32649d53256f6d6fa2ed2ceda854f848b64f4c546",
    "vendor/physical.py": "24c9cf906596c9ef1533c1d25f61403db3ff6389478f64359d9d12c5fef87b69",
    "data/BASE-GRAPH.json.gz": "843ac970a0ea02f0852f0b03b71f9bc473d792a739ac44efa288b553ddb8b275",
    "data/BASE-INTERFACE.json": "1cd2de69e6e49fb74abc3b1dea2366901e1a227704c62e0f624096b22853d582",
    "EDITS.json": "7ced0e7a5d39f1ebc1468899e1f66da84d2f7160d8c979763ee33bcd2e6e93c0",
}
DELETIONS = (91461, 92308, 99490, 99531, 101201, 101943, 101949)
HUB_MOVES = (95493, 95914, 96293, 97908)
REROUTES = (91467, 92315, 103740, 103754, 103786, 103808, 104319)
RESTORATIONS = {
    2: (98700, 104395), 3: (98373, 103615), 4: (93308, 100230), 5: (93401, 100226),
    6: (91332, 99643), 7: (90714, 98671), 8: (91141, 91550), 9: (90658, 91120),
}
TERMINAL_REPAIRS = {
    155466: (97908, Fraction(1, 2)),
    155505: (95914, Fraction(-1)),
    155520: (95914, Fraction(-1)),
    155537: (97908, Fraction(-1, 2)),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(raw):
    return sha256(raw).hexdigest()


def pinned_bytes(path, expected):
    raw = path.read_bytes()
    need(digest(raw) == expected, f"wrong SHA-256 for {path.name}")
    return raw


def reconstruct_parent(package, snapshot):
    if snapshot is not None:
        with snapshot.open("rb") as stream:
            compressed = stream.read(2) == b"\x1f\x8b"
            stream.seek(0)
            if compressed:
                with gzip.GzipFile(fileobj=stream) as graph_stream:
                    raw = graph_stream.read(GRAPH_LIMIT + 1)
            else:
                raw = stream.read(GRAPH_LIMIT + 1)
        need(len(raw) <= GRAPH_LIMIT, "parent graph exceeds size limit")
        method = "sha256-checked graph snapshot"
    else:
        # Stage only authenticated public sources in a private directory.
        # A fresh isolated interpreter cannot load checkout-local bytecode.
        with tempfile.TemporaryDirectory(prefix="p104-native-parent-") as area:
            stage = Path(area)
            for name, pin in CONSTRUCTOR_FILES.items():
                out = stage / name
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(pinned_bytes(package / "pr7756" / name, pin))
            raw = subprocess.check_output(
                [sys.executable, "-I", "-B", "-X", f"pycache_prefix={stage/'cache'}", str(stage/"construction.py")],
                cwd=stage, timeout=90,
            )
        method = "authenticated pr7756 construction.build"
    graph = json.loads(raw)
    need(digest(encoded(graph)) == PARENT_GRAPH, "canonical parent graph SHA-256")
    return graph, method


def schedule_from_rows(forms):
    # Insert forms and their paid donors in increasing clock order. The
    # standard topological iterator emits whole ready batches in that order.
    dependencies = {k: sorted(j for j in row if j >= 0) for k, row in sorted(forms.items())}
    need(all(j in dependencies for row in dependencies.values() for j in row), "unknown paid donor in schedule")
    try:
        return list(TopologicalSorter(dependencies).static_order())
    except CycleError as exc:
        raise ValueError("cyclic graph after applying differential") from exc


@cache
def coefficient(text):
    need(isinstance(text, str), "coefficient must be a rational string")
    q = Fraction(text)
    need(q and str(q) == text, "zero or noncanonical coefficient")
    return q.numerator, q.denominator


def apply_delta(parent, patch):
    need(patch.keys() == PATCH_FIELDS and patch["schema"] == "p104-nine-relay-differential/v1",
         "differential fields or schema")
    need((patch["parent_graph_sha256"], patch["joint_graph_sha256"]) == (PARENT_GRAPH, JOINT_GRAPH),
         "differential graph pins")
    moves = {k: [a,b] for k,a,b in parent["moves"]}
    forms = {k: dict(row) for k,row in parent["forms"]}
    need(tuple(row[0] for row in patch["deleted_moves"]) == DELETIONS, "paid deletion inventory")
    for k, prior in patch["deleted_moves"]:
        need(moves.get(k) == prior, f"deleted move preimage {k}")
        del moves[k]
        del forms[k]
    for field, inventory in (("relocated_hub_moves", HUB_MOVES), ("rerouted_moves", REROUTES)):
        need(tuple(row[0] for row in patch[field]) == inventory, "relocation or reroute inventory")
        for k, prior, replacement in patch[field]:
            need(moves.get(k) == prior and prior != replacement, f"changed move preimage {k}")
            moves[k] = replacement
    return finish_delta(parent, patch, moves, forms, 182)


def finish_delta(parent, patch, moves, forms, changed_count):
    scalar = patch["scalar_form_changes"]
    keys = [row[0] for row in scalar]
    need(len(keys) == changed_count and keys == sorted(set(keys)) and set(keys) <= forms.keys(),
         "edited scalar form inventory")
    for k, edits in scalar:
        donors = [edit[0] for edit in edits]
        need(donors and donors == sorted(set(donors)), "edited donor order")
        for j, prior, replacement in edits:
            need(forms[k].get(j) == prior and prior != replacement, f"scalar preimage {k}/{j}")
            if replacement is None:
                del forms[k][j]
            else:
                coefficient(replacement)
                forms[k][j] = replacement
    schedule = schedule_from_rows(forms)
    expected = {"recipe": "sorted-forms-ready-batches", "rows": len(schedule), "sha256": digest(encoded(schedule))}
    need(patch["schedule"] == expected, "schedule size or digest")
    return dict(parent, moves=[[k, *ab] for k, ab in sorted(moves.items())],
                forms=[[k, sorted(row.items())] for k,row in sorted(forms.items())], schedule=schedule)


def apply_stack(parent, patch):
    need(patch.keys() == STACK_FIELDS and patch["schema"] == "p104-eight-restoration-differential/v1",
         "restoration differential fields or schema")
    need((patch["parent_graph_sha256"], patch["joint_graph_sha256"]) == (JOINT_GRAPH, STACK_GRAPH),
         "restoration graph pins")
    need(digest(encoded(parent)) == JOINT_GRAPH, "canonical nine-relay intermediate")
    moves = {k: [a,b] for k,a,b in parent["moves"]}
    forms = {k: dict(row) for k,row in parent["forms"]}
    starts = dict(moves)
    deleted = [k for k,_ in patch["deleted_moves"]]
    need(deleted == sorted(k for pair in RESTORATIONS.values() for k in pair) and len(set(deleted)) == 16,
         "restoration deletion inventory")
    for k, prior in patch["deleted_moves"]:
        need(moves.get(k) == prior, "restoration deleted move preimage")
        del moves[k]
        del forms[k]
    need([row[0] for row in patch["added_moves"]] == list(RESTORATIONS), "restoration addition inventory")
    frames = parent["frames"]

    def rank(pair):
        a,b = pair
        need(all(type(c) is int and 0 <= c < len(frames) for c in pair), "restoration chart bounds")
        return abs(len(frames[a])-len(frames[b]))

    for k, route, row in patch["added_moves"]:
        need(k not in starts and sorted(rank(starts[j]) for j in RESTORATIONS[k]) == [2,4]
             and rank(route) == 6, "4+2 to 6 restoration ranks")
        terms = [j for j,_ in row]
        need(terms == sorted(set(terms)) and terms, "restored scalar row order")
        for _, q in row:
            coefficient(q)
        moves[k], forms[k] = route, dict(row)
    need(not (set(RESTORATIONS) & {k for k,_ in patch["scalar_form_changes"]}),
         "retained scalar edits cannot modify inserted rows")
    return finish_delta(parent, patch, moves, forms, 231)


def check_public_boundary(parent, candidate):
    need(candidate.keys() == parent.keys() == GRAPH_FIELDS, "graph schema")
    need(all(candidate[k] == parent[k] for k in ("first_output", "frames", "initial", "final")),
         "protected public interface")


def span(basis):
    result = {0}
    for axis in basis:
        need(type(axis) is int and 0 < axis < 512 and axis not in result, "nonindependent chart basis")
        result |= {axis ^ vector for vector in result}
    return result


def graph_rows(graph):
    n = len(graph["initial"])
    first = graph["first_output"]
    need(n == len(graph["final"]) == 1262 and first == 154768, "public owner count and namespace")
    spans = list(map(span, graph["frames"]))
    need(all(type(i) is int and 0 <= i < len(spans) for i in graph["initial"] + graph["final"]),
         "public chart bounds")
    moves = {}
    for k, a, b in graph["moves"]:
        need(type(k) is int and 0 <= k < first and k not in moves, "paid namespace")
        need(all(type(i) is int and 0 <= i < len(spans) for i in (a,b)), "paid chart bounds")
        need(spans[a] < spans[b] or spans[b] < spans[a], f"paid chart nesting {k}")
        moves[k] = (a,b)
    rows = {}
    for k, terms in graph["forms"]:
        donors = [j for j, _ in terms]
        need(k not in rows and donors == sorted(set(donors)), "unique canonical scalar row")
        rows[k] = [(j, coefficient(q)) for j, q in terms]
    schedule = graph["schedule"]
    expected = moves.keys() | set(range(first, first+n))
    need(expected == rows.keys() == set(schedule) and len(schedule) == len(expected), "topological row inventory")
    return moves, rows, schedule


def transposed(n, first, moves, rows, order):
    def opposite(k):
        if k < 0:
            return first + ~k
        return ~(k - first) if k >= first else k

    reverse_rows = {k: [] for k in rows}
    for k, terms in rows.items():
        for donor, q in terms:
            reverse_rows[opposite(donor)].append((opposite(k), q))
    reverse_order = [k for k in reversed(order) if k < first] + list(range(first, first+n))
    return {k: (b,a) for k,(a,b) in moves.items()}, reverse_rows, reverse_order


def exact_rows(graph, ledger, reverse=False, capture=()):
    first = graph["first_output"]
    starts, ends = graph["initial"], graph["final"]
    if reverse:
        starts, ends = ends, starts
        ledger = transposed(len(starts), first, *ledger)
    moves, rows, order = ledger
    available = {~r: chart for r,chart in enumerate(starts)}
    values = {~r: {r: GRID} for r in range(len(starts))}
    public, samples = {}, {}
    products = 0
    for k in order:
        src = moves[k][0] if k < first else ends[k-first]
        result = {}
        for donor, (p,q) in rows[k]:
            need(donor in available and available[donor] == src, f"unavailable or nonlocal donor at {k}")
            vec = values[donor]
            products += len(vec)
            for r, value in vec.items():
                term, rem = divmod(p*value, q)
                if rem:
                    raise ValueError(f"nonintegral grid product at row {k}, column {r}")
                total = result.get(r,0) + term
                if total:
                    result[r] = total
                else:
                    result.pop(r, None)
        if k < first:
            available[k] = moves[k][1]
            values[k] = result
            if k in capture:
                samples[k] = result
        else:
            public[k] = result
    return public, samples, products


def expect_failure(check, needle):
    try:
        check()
    except (ValueError, CycleError) as exc:
        need(needle in str(exc), f"unexpected control failure {exc}")
    else:
        raise ValueError(f"failed control {needle}")


def controls(parent, patch, candidate, public, samples):
    wrong = dict(patch, initial=candidate["initial"])
    expect_failure(lambda: apply_delta(parent, wrong), "differential fields")
    wrong = deepcopy(patch)
    wrong["rerouted_moves"][0][1][0] = -1
    expect_failure(lambda: apply_delta(parent, wrong), "changed move preimage")
    wrong = deepcopy(patch)
    wrong["scalar_form_changes"][0][1][0][1] = "123"
    expect_failure(lambda: apply_delta(parent, wrong), "scalar preimage")
    wrong = dict(candidate, initial=candidate["initial"][::-1])
    expect_failure(lambda: check_public_boundary(parent, wrong), "protected public interface")
    expect_failure(lambda: schedule_from_rows({0: {1: "1"}, 1: {0: "1"}}), "cyclic graph")
    omit = {}
    for row, (bank,q) in TERMINAL_REPAIRS.items():
        witness = next((i for i,v in sorted(samples[bank].items()) if v), None)
        need(witness is not None, "inactive terminal repair")
        normal = Fraction(public[row].get(witness,0), GRID)
        omitted = normal - q*Fraction(samples[bank][witness], GRID)
        need(normal != omitted, "required terminal repair omission does not change row")
        omit[str(row)] = {"independent_input": witness, "with_repair": str(normal), "omitted": str(omitted)}
    return {"forbidden_edit_field_rejected": True, "wrong_move_preimage_rejected": True,
            "wrong_scalar_preimage_rejected": True, "public_change_rejected": True,
            "cyclic_schedule_rejected": True, "terminal_repair_omission_witnesses": omit}


@cache
def power_interval(rank, exponent, bits=256):
    """Enclose r**t using dyadic exponents and directed integer square roots."""
    unit = 1 << bits
    digits, excess = divmod(exponent.numerator * unit, exponent.denominator)
    root_lo = root_hi = rank * unit
    lo = hi = unit
    for i in range(bits-1, -1, -1):
        root_lo = isqrt(root_lo * unit)
        radicand = root_hi * unit
        root_hi = isqrt(radicand)
        if root_hi * root_hi < radicand:
            root_hi += 1
        if digits >> i & 1:
            lo = lo * root_lo // unit
            hi = -(-hi * root_hi // unit)
    if excess:
        hi = -(-hi * root_hi // unit)
    return Fraction(lo, unit), Fraction(hi, unit)


def series_log(y):
    running = y
    square = y*y
    total = Fraction()
    for i in range(64):
        total += 2*running / (2*i + 1)
        running *= square
    return total, total + 2*running / (129*(1-square))


@cache
def log_bounds(rank):
    p = rank.bit_length()-1
    factor = 1 << p
    lo, hi = series_log(Fraction(rank-factor, rank+factor))
    half_lo, half_hi = series_log(Fraction(1,3))
    return lo+p*half_lo, hi+p*half_hi


def margin(signed, point):
    lower = upper = Fraction()
    for r,c in signed.items():
        lo, hi = power_interval(r, 1-Fraction(point))
        lower += c*(lo if c >= 0 else hi)
        upper += c*(hi if c >= 0 else lo)
    return lower, upper


def decimal_interval(interval, digits=24):
    def decimal(scaled):
        sign = "-" if scaled < 0 else ""
        integer, residue = divmod(abs(scaled), 10**digits)
        return f"{sign}{integer}.{residue:0{digits}d}"
    lo,hi = (v*10**digits for v in interval)
    return [decimal(lo//1), decimal(-(-hi//1))]


def price(package, parent, candidate, old_moves, new_moves, variant):
    record = json.loads(pinned_bytes(package / "evidence/price.json", PRICE))
    need(record["source"]["unchanged_native_graph_sha256"] == PARENT_GRAPH, "source invoice native binding")
    baseline = record["contiguous_2048"]
    binding = baseline["binding"]
    need(binding["calls"] == CALLS and binding["native_main_bindings"] == 400*CALLS
         and binding["stage_helper_owners"] == 862*CALLS and binding["root_owners"] == 420096
         and binding["template_roots"] == {"A": 5176, "B": 8, "mixed": 8128}, "protected caller inventory")
    invoice = baseline["invoice"]
    need(invoice["contract"]["ambient_rank"] == 137 and
         invoice["contract"]["model"] == "mixed-target-unnormalized-power-v1", "signed rank tariff")
    frames = parent["frames"]
    need(frames == candidate["frames"], "unchanged chart stock")
    def rank_count(table):
        return Counter(abs(len(frames[a])-len(frames[b])) for a,b in table.values())
    removed = rank_count(new_moves)
    removed.subtract(rank_count(old_moves))
    delta = {r: n for r,n in sorted(removed.items()) if n}
    need(delta == PAID_DELTAS[variant], "joint paid rank change")
    base_paid = {int(r): n for r,n in invoice["paid"].items()}
    targets = {int(r): n for r,n in invoice["targets"].items()}
    joint_paid = Counter(base_paid)
    joint_paid.update({r: n*CALLS for r,n in delta.items()})
    need(all(n >= 0 for n in joint_paid.values())
         and sum(joint_paid.values()) == 12161504 + CALLS * sum(delta.values())
         and sum(targets.values()) == 2185472, "complete finite invoice census")
    signed = Counter(targets)
    signed.subtract(joint_paid)
    bracket = BRACKETS[variant]
    low, high = (margin(signed, point) for point in bracket)
    require_target = margin(signed, TARGET)
    need(low[0] > 0 > high[1] and require_target[1] < 0, "directed bracket or under-target sign")
    derivative_upper = Fraction()
    for r,c in signed.items():
        log_lo,log_hi = log_bounds(r)
        f_lo = power_interval(r, 1-Fraction(BIT))[0]
        derivative_upper += -c*(f_lo*log_lo if c > 0 else r*log_hi)
    need(derivative_upper < 0, "negative signed derivative to common BIT pin")
    credit = margin({r: -n for r,n in delta.items()}, TARGET)
    return {
        "calls": CALLS, "caller_sha256": CALLER, "source_invoice_sha256": PRICE,
        "paid_delta_per_native": delta, "productive_delta": {},
        "paid_jobs": sum(joint_paid.values()), "productive_jobs": sum(targets.values()),
        "invoice": {"schema": invoice["schema"], "contract": invoice["contract"],
                    "paid": dict(sorted(joint_paid.items())), "targets": targets},
        "raw_bracket": list(bracket), "bracket_margin_bounds": list(map(decimal_interval, (low,high))),
        "negative_derivative_upper_on_0_to_common_bit": decimal_interval((derivative_upper,derivative_upper))[1],
        "common_bit": BIT, "target": TARGET,
        "target_shortfall_per_native_call": decimal_interval((-require_target[1]/CALLS, -require_target[0]/CALLS)),
        "target_shortfall_batch": decimal_interval((-require_target[1],-require_target[0])),
        "credit_per_native_call_at_target": decimal_interval(credit),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-package", required=True, type=Path,
                        help="exact #7761 research/p104-mixed-batch-boundary directory")
    parser.add_argument("--baseline-graph", type=Path, help="optional parent graph JSON or gzip")
    parser.add_argument("--variant", choices=("seventeen", "nine"), default="seventeen",
                        help="graph variant to replay (default seventeen)")
    parser.add_argument("--write-graph", type=Path, help="write verified canonical candidate graph JSON")
    args = parser.parse_args()
    parent, method = reconstruct_parent(args.parent_package, args.baseline_graph)
    patch = json.loads(pinned_bytes(HERE / "DELTA.json", DIFFERENTIAL))
    nine = apply_delta(parent, patch)
    check_public_boundary(parent, nine)
    need(digest(encoded(nine)) == JOINT_GRAPH, "canonical nine-relay graph SHA-256")
    candidate, candidate_pin, candidate_slots = nine, JOINT_GRAPH, 5739
    if args.variant == "seventeen":
        stack_patch = json.loads(pinned_bytes(HERE / "STACK-DELTA.json", STACK_DIFFERENTIAL))
        candidate = apply_stack(nine, stack_patch)
        check_public_boundary(nine, candidate)
        candidate_pin, candidate_slots = STACK_GRAPH, 5731
        wrong = deepcopy(stack_patch)
        wrong["added_moves"][0][1] = [0, 0]
        expect_failure(lambda: apply_stack(nine, wrong), "4+2 to 6 restoration ranks")
    graph_raw = encoded(candidate)
    need(digest(graph_raw) == candidate_pin, "canonical candidate graph SHA-256")
    old, new = graph_rows(parent), graph_rows(candidate)
    need((len(old[0]), len(new[0])) == (5746,candidate_slots), "paid native slot census")
    result = {"schema": "p104-native-replay/v1", "variant": args.variant, "parent_head": PARENT_HEAD,
              "native_head": NATIVE_HEAD, "parent_graph_sha256": PARENT_GRAPH,
              "nine_relay_graph_sha256": JOINT_GRAPH, "candidate_graph_sha256": candidate_pin,
              "differential_sha256": DIFFERENTIAL, "parent_replay": method,
              "paid_native_moves": len(new[0])}
    if args.variant == "seventeen":
        result["stack_differential_sha256"] = STACK_DIFFERENTIAL
    for orientation in (False, True):
        old_rows, _, pcount = exact_rows(parent, old, reverse=orientation)
        capture = () if orientation else tuple(bank for bank,_ in TERMINAL_REPAIRS.values())
        new_rows, samples, count = exact_rows(candidate, new, reverse=orientation, capture=capture)
        need(len(old_rows) == 1262 and old_rows == new_rows, "all independent public rows")
        name = "transpose" if orientation else "forward"
        result[name] = {"exact_public_rows": len(new_rows), "grid": GRID,
                        "exact_products_before_after": [pcount,count]}
        if not orientation:
            result["controls"] = controls(parent, patch, candidate, new_rows, samples)
            if args.variant == "seventeen":
                result["controls"]["invalid_restoration_rank_rejected"] = True
    result["price"] = price(args.parent_package, parent, candidate, old[0], new[0], args.variant)
    if args.write_graph is not None:
        args.write_graph.write_bytes(graph_raw)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
