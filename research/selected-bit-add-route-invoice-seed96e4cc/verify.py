#!/usr/bin/env python3
"""Replay the selected same-family ADD route invoice on pinned inputs."""

from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
ROUTE_SHA256 = "4dc53efa6768b44316e2ee661fb8df07cf956a35cb6f35981d00cd2f7b4f44ac"
ROUTE_HEAD = "eb1bf93950e9b14f7fadca7892866e9f29a26ad3"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def transpose(matrix):
    return [list(col) for col in zip(*matrix)]


def multiply(left, right):
    rows, inner, cols = len(left), len(right), len(right[0])
    need(len(left[0]) == inner, "matrix dimensions")
    out = [[F(0) for _ in range(cols)] for _ in range(rows)]
    for i, row in enumerate(left):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(right[k]):
                    if y:
                        out[i][j] += x * y
    return out


def replay(word, n=64):
    matrix = eye(n)
    for kind, dest, src, coefficient in word:
        coefficient = F(coefficient)
        for row in matrix:
            if kind == "swap":
                row[dest], row[src] = row[src], row[dest]
            elif kind == "scale":
                row[dest] *= coefficient
            elif kind == "add":
                row[dest] += coefficient * row[src]
            else:
                raise ValueError("unknown route factor")
    return matrix


def column_word(matrix):
    """The exact Gaussian column compiler used for inverse directions."""
    n = len(matrix)
    reduced = [list(row) for row in matrix]
    word = []
    for col in range(n):
        pivot = next((row for row in range(col, n) if reduced[row][col]), None)
        need(pivot is not None, "inverse route is singular")
        if pivot != col:
            reduced[col], reduced[pivot] = reduced[pivot], reduced[col]
            word.append(("swap", pivot, col, F(1)))
        diagonal = reduced[col][col]
        if diagonal != 1:
            reduced[col] = [x / diagonal for x in reduced[col]]
            word.append(("scale", col, col, diagonal))
        for row in range(n):
            if row == col:
                continue
            coefficient = reduced[row][col]
            if coefficient:
                reduced[row] = [x - coefficient * y for x, y in zip(reduced[row], reduced[col])]
                word.append(("add", col, row, coefficient))
    need(reduced == eye(n), "Gaussian inverse endpoint")
    need(replay(word, n) == matrix, "Gaussian route factor product")
    return word


def bill(word):
    counts = Counter({
        "ordinary": 0,
        "double_half": 0,
        "negation": 0,
        "controlled_shift": 0,
        "constant_shift": 0,
        "low_permutation": len(word),
    })
    for kind, dest, src, coefficient in word:
        coefficient = F(coefficient)
        numerator, denominator = abs(coefficient.numerator), coefficient.denominator
        need(numerator & (numerator - 1) == 0, "dyadic numerator")
        need(denominator & (denominator - 1) == 0, "dyadic denominator")
        if kind == "swap":
            counts["ordinary"] += 64
        elif kind == "add":
            counts["ordinary"] += 128 * (src > dest)
            counts["double_half"] += 128 * (denominator.bit_length() - 1)
            counts["controlled_shift"] += 64
        elif kind == "scale":
            counts["double_half"] += 64 * (numerator.bit_length() + denominator.bit_length() - 2)
            counts["negation"] += 64 * (coefficient < 0)
            counts["constant_shift"] += 64
        else:
            raise ValueError("unknown bill operation")
    return dict(counts)


def basis(port):
    q = port["q"]
    complement = port["complement_columns"]
    return [[F(q[i], 2)] + [F(x) for x in complement[i]] for i in range(8)]


def expected_route_matrix(record, geometry):
    slots = record["slots"]
    need(len(slots) == 8 and len(set(slots)) == 8, "eight distinct hosted axes")
    permutation = list(range(64))
    domain, image = set(range(8)), set(slots)
    for i, s in zip(sorted(domain - image), sorted(image - domain)):
        permutation[i], permutation[s] = s, i
    need(record["permutation"] == permutation, "route support permutation")
    pi = [[F(i == permutation[j]) for j in range(64)] for i in range(64)]
    local = min(slots) < 8
    if not local:
        need(record["port"] is None, "nonlocal route has no port")
        sigma = pi
        expected = transpose(pi)
    else:
        need(isinstance(record["port"], int) and 0 <= record["port"] < len(geometry["ports"]),
             "selected local route port")
        need(slots == list(range(1, 9)), "selected local route support")
        port = geometry["ports"][record["port"]]
        b = basis(port)
        embedded_b = eye(64)
        embedded_bt = eye(64)
        for i in range(8):
            for j in range(8):
                embedded_b[i][j] = b[i][j]
                embedded_bt[i][j] = b[j][i]
        sigma = multiply(embedded_b, pi)
        expected = multiply(transpose(pi), embedded_bt)
    identity = eye(64)
    need(multiply(expected, sigma) == identity, "route inverse on right")
    need(multiply(sigma, expected) == identity, "route inverse on left")
    return expected


def validate_route(key, record, geometry):
    need(record["family"] == "hosted", "hosted route record")
    expected = expected_route_matrix(record, geometry)
    word = [(k, i, j, F(c)) for k, i, j, c in record["word"]]
    need(replay(word) == expected, "route word matches selected chart")
    need(record["bill"] == bill(word), "route bill matches word")
    need(key.startswith("host:"), "hosted route key")
    key_slots = [int(x) for x in key.split(":")[1].split(",")]
    key_port = int(key.split(":")[2]) if key.count(":") == 2 else None
    need(key_slots == record["slots"] and key_port == record["port"], "route key binding")
    return expected


def source_bytes(path):
    return (ROOT / path).read_bytes()


def load_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    need(manifest["base_commit"] == BASE, "exact research base")
    selected_source = next(
        entry for entry in manifest["files"]
        if entry["path"] == "certificates/selected-result.json"
    )
    for entry in manifest["files"]:
        raw = source_bytes(entry["path"])
        need(sha256(raw).hexdigest() == entry["sha256"], "source pin: " + entry["path"])
    need(selected_source["sha256"] == SELECTED_SHA256, "selected-record pin")
    route_raw = (HERE / "ROUTES.json").read_bytes()
    need(sha256(route_raw).hexdigest() == ROUTE_SHA256, "captured predecessor route pin")
    routes_file = json.loads(route_raw)
    need(routes_file["predecessor_commit"] == ROUTE_HEAD, "route compiler head")
    need(routes_file["predecessor_pr"] == 2157, "route compiler predecessor")
    routes = routes_file["routes"]
    paths = {entry["path"]: ROOT / entry["path"] for entry in manifest["files"]}
    template = json.loads(gzip.decompress(paths[
        "research/community-hyperplane599-audit/pr589/bit589/v9/hosted/GLOBAL-TEMPLATE.json.gz"
    ].read_bytes()))
    geometry = json.loads(paths[
        "research/community-hyperplane599-audit/pr589/bit589/v9/nine/GEOMETRY.json"
    ].read_bytes())
    return manifest, routes, template, geometry


def route_key(call, role, children):
    family, route = call["owners"][role]
    need(role >= 222 and route[0] == "hosted", "same-family ADD uses hosted owners")
    _, child, offset, width = route
    entry = children[child]
    first, last = entry["source_level"], entry["target_level"]
    pending = list(range(1 if first == -1 else 8 + 7 * first, 8 + 7 * last))
    slots = pending[offset:offset + width]
    need(width == 8 and len(slots) == 8, "complete width-eight owner")
    port = family % 111
    return "host:" + ",".join(map(str, slots)) + (f":{port}" if min(slots) < 8 else "")


def xor_add(vector, event):
    need(event[0] == 1 and event[3] == 1, "unit F2 ADD event")
    vector[event[1]] ^= vector[event[2]]


def noncommutation_control(template):
    call = next(c for c in template["calls"] if c["stage"] == 0 and c["replica"] == 0)
    program = template["local_programs"][call["orientation"]]
    first, middle, second = program[19422], program[19424], program[19448]
    need(first[:3] == [1, 243, 244], "first selected family ADD")
    need(middle[:3] == [1, 243, 236], "intervening update of the target role")
    need(second[:3] == [1, 244, 243], "second selected family ADD")
    baseline = [0] * 661
    baseline[236] = 1
    reordered = baseline.copy()
    for event in (first, middle, second):
        xor_add(baseline, event)
    for event in (first, second, middle):
        xor_add(reordered, event)
    need(baseline != reordered and baseline[244] == 1 and reordered[244] == 0,
         "family scan grouping must preserve intervening state")
    return {
        "family": 451,
        "positions": [19422, 19448, 26620, 26642],
        "intervening_position": 19424,
        "intervening_event": middle,
        "baseline_output_role244": baseline[244],
        "reordered_output_role244": reordered[244],
    }


def compute_receipt(routes, template, geometry):
    children = {e["idx"]: e for e in template["schedule"] if e["kind"] == "idle"}
    route_matrices = {}
    inverse_bills = {}
    for key, record in routes.items():
        matrix = validate_route(key, record, geometry)
        route_matrices[key] = matrix
        inverse = transpose(matrix)
        need(multiply(matrix, inverse) == eye(64) and multiply(inverse, matrix) == eye(64),
             "orthogonal selected route")
        inverse_bills[key] = bill(column_word(inverse))

    total = Counter()
    calls = []
    groups = 0
    route_keys = set()
    first_event = None
    for call in template["calls"]:
        owners = call["owners"]
        program = template["local_programs"][call["orientation"]]
        bill_call = Counter()
        by_family = Counter()
        add_count = 0
        for position, event in enumerate(program):
            if event[0] != 1:
                continue
            target, source = event[1:3]
            if target < 222 or source < 222 or owners[target][0] != owners[source][0]:
                continue
            target_key = route_key(call, target, children)
            source_key = route_key(call, source, children)
            need(target_key in routes and source_key in routes, "selected route present")
            route_keys.update((target_key, source_key))
            bill_call.update(routes[target_key]["bill"])
            bill_call.update(routes[source_key]["bill"])
            bill_call.update(inverse_bills[target_key])
            by_family[owners[target][0]] += 1
            add_count += 1
            if (call["stage"], call["replica"], position) == (0, 0, 19422):
                first_event = {
                    "stage": 0,
                    "replica": 0,
                    "position": position,
                    "family": owners[target][0],
                    "target_role": target,
                    "source_role": source,
                    "target_route": target_key,
                    "source_route": source_key,
                    "three_route_bill": dict(Counter(routes[target_key]["bill"])
                        + Counter(routes[source_key]["bill"])
                        + Counter(inverse_bills[target_key])),
                }
        groups += len(by_family)
        total.update(bill_call)
        calls.append({
            "stage": call["stage"],
            "replica": call["replica"],
            "same_family_adds": add_count,
            "family_groups": len(by_family),
            "route_bill": dict(sorted(bill_call.items())),
        })

    need(len(calls) == 288, "all selected calls")
    adds = sum(c["same_family_adds"] for c in calls)
    need(adds == 11072, "selected same-family ADD census")
    need(len(route_keys) == 43 == len(routes), "exact used route-type inventory")
    route_actions = 3 * adds
    ordinary = sorted(c["route_bill"].get("ordinary", 0) for c in calls)
    med = F(ordinary[143] + ordinary[144], 2)
    stage0 = next(c for c in calls if (c["stage"], c["replica"]) == (0, 0))
    need(stage0["same_family_adds"] == 28, "selected stage-zero call count")
    need(first_event is not None, "selected event 19422")
    controls = noncommutation_control(template)
    totals = dict(sorted(total.items()))
    expected_totals = {
        "ordinary": 19398656,
        "double_half": 3407872,
        "negation": 417792,
        "controlled_shift": 4177920,
        "constant_shift": 1097728,
        "low_permutation": 321408,
    }
    need(totals == expected_totals, "complete selected route invoice")
    return {
        "status": "PASS_SELECTED_BIT_ADD_ROUTE_INVOICE",
        "base_commit": BASE,
        "selected_record_sha256": SELECTED_SHA256,
        "route_predecessor_commit": ROUTE_HEAD,
        "calls": len(calls),
        "same_family_adds": adds,
        "route_actions": route_actions,
        "route_types": len(routes),
        "family_groups": groups,
        "naive_family_scan_reduction": adds - groups,
        "per_call_ordinary": {
            "min": ordinary[0],
            "median": str(med),
            "max": ordinary[-1],
            "stage0_replica0": stage0["route_bill"]["ordinary"],
        },
        "route_bill": totals,
        "first_event": first_event,
        "noncommutation_control": controls,
        "negative_controls": [
            "route-word mutation rejected by exact chart replay",
            "omitted target-return direction changes the invoice",
            "naive same-family ADD reordering changes role-244 output",
        ],
        "per_call_invoices": calls,
        "scope": "Conditional exact chart-route bill for the selected same-family ADD subset; scans, XOR payload cost, fixed-tape wrapper, recursive child costs, descriptors, precision and restoration remain unpriced.",
        "new_kappa": False,
        "calls_receipt_sha256": digest(calls),
    }


def run_controls(routes, geometry, receipt):
    first_key = receipt["first_event"]["target_route"]
    mutated = json.loads(json.dumps(routes[first_key]))
    mutated["word"] = mutated["word"][:-1]
    rejected = False
    try:
        validate_route(first_key, mutated, geometry)
    except (ValueError, IndexError, StopIteration):
        rejected = True
    need(rejected, "mutated route word must fail")
    direct = Counter()
    for key in (receipt["first_event"]["target_route"], receipt["first_event"]["source_route"]):
        direct.update(routes[key]["bill"])
    need(direct != receipt["first_event"]["three_route_bill"], "omitted target return is detected")


def main():
    manifest, routes, template, geometry = load_inputs()
    need(len(routes) == 43, "captured route subset size")
    receipt = compute_receipt(routes, template, geometry)
    run_controls(routes, geometry, receipt)
    result_path = HERE / "RESULT.json"
    if "--write" in sys.argv:
        result_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads(result_path.read_text())
        need(receipt == expected, "stored result receipt")
    print(
        "PASS_SELECTED_BIT_ADD_ROUTE_INVOICE "
        f"adds={receipt['same_family_adds']} routes={receipt['route_actions']} "
        f"types={receipt['route_types']} ordinary={receipt['route_bill']['ordinary']} "
        f"groups={receipt['family_groups']} controls={len(receipt['negative_controls'])} no_new_kappa"
    )


if __name__ == "__main__":
    main()
