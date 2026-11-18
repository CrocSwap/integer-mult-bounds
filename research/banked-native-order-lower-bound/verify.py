"""Check the all-order bank bound and the exact single-anchor rank ceiling.

Retained graph and upper-bound allocation: Nick Petalas, PR7724.
The graph, bank contract and integer coefficient method retain PR7674/7681 credit.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha1, sha256
from math import isqrt
from pathlib import Path
import json
import runpy

HERE = Path(__file__).resolve().parent
SOURCE = runpy.run_path(str(HERE / "retained/pr7724/verify.py"))
GRID, PRIME = 530841600, 1000003


def need(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def provenance():
    pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
    for pin in pins:
        raw = (HERE / pin["path"]).read_bytes()
        need(sha256(raw).hexdigest() == pin["sha256"]
             and sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == pin["git_blob"],
             "retained bytes: " + pin["path"])
    return len(pins)


def mandatory_sets(graph, forms):
    initial = [~i for i in range(len(graph["initial"]))]
    order = initial + graph["schedule"]
    need(len(set(order)) == len(order) and set(graph["schedule"]) == forms.keys(), "complete DAG inventory")
    index = {v: i for i, v in enumerate(order)}
    bits = {v: 1 << i for v, i in index.items()}
    users = defaultdict(list)
    for node, row in forms.items():
        need(len({d for d, _ in row}) == len(row), "distinct literal donors")
        for donor, _ in row:
            need(donor in index and index[donor] < index[node], "topological source order")
            users[donor].append(node)
    terminals = set(range(graph["first_output"], graph["first_output"] + len(graph["final"])))
    need(all(not users[v] for v in terminals), "terminals have no row consumers")
    ancestors = dict.fromkeys(initial, 0)
    for node in graph["schedule"]:
        mask = 0
        for donor, _ in forms[node]:
            mask |= ancestors[donor] | bits[donor]
        ancestors[node] = mask
    descendants = {}
    for node in reversed(order):
        mask = 0
        for user in users[node]:
            mask |= descendants[user] | bits[user]
        descendants[node] = mask
    row_mask = sum(bits[v] for v in graph["schedule"])
    result = {v: [] for v in graph["schedule"]}
    for owner in order:
        before_use = 0
        for user in users[owner]:
            before_use |= ancestors[user] | bits[user]
        live = before_use & (row_mask if owner < 0 else descendants[owner]) & row_mask
        for at in members(live):
            result[order[at]].append(owner)
    need(all({d for d, _ in forms[v]} <= set(result[v]) and v not in result[v] for v in result),
         "all donors and a separate new result")
    return result, users


def coefficients(graph, forms):
    values = {~i: {i: GRID} for i in range(len(graph["initial"]))}
    count = 0
    for node in graph["schedule"]:
        row = {}
        for donor, factor in forms[node]:
            for column, value in values[donor].items():
                part, remainder = divmod(factor.numerator*value, factor.denominator)
                need(remainder == 0, "exact coefficient product")
                total = row.get(column, 0) + part
                if total:
                    row[column] = total
                else:
                    row.pop(column, None)
                count += 1
        values[node] = row
    return values, count


def rank_mod(tokens, values):
    basis = {}
    for token in tokens:
        row = values[token].copy()
        while row:
            pivot = min(row)
            factor = row[pivot]
            if pivot not in basis:
                inverse = pow(factor, -1, PRIME)
                basis[pivot] = {i: value*inverse % PRIME for i, value in row.items()}
                break
            for i, value in basis[pivot].items():
                total = (row.get(i, 0) - factor*value) % PRIME
                if total:
                    row[i] = total
                else:
                    row.pop(i, None)
    return len(basis)


def check_certificate(cert, sets, users, values, modular):
    anchor = cert["anchor"]
    owners, basis = cert["owners"], cert["basis"]
    need(owners == sets[anchor] and len(owners) == 24 and len(set(basis)) == len(basis) == 19
         and set(basis) <= set(owners), "complete forced owner set and basis")
    need(rank_mod(basis, modular) == 19, "basis independence")
    paths = cert["paths"]
    need([row["owner"] for row in paths] == owners, "path owner inventory")
    for row in paths:
        owner, use = row["owner"], row["use"]
        birth, future = row["birth_path"], row["future_path"]
        need((not birth if owner < 0 else len(birth) >= 2 and birth[0] == owner and birth[-1] == anchor)
             and future[0] == anchor and future[-1] == use and use in users[owner], "path endpoints")
        need(all(b in users[a] for path in (birth, future) for a, b in zip(path, path[1:])),
             "literal dependency path")
    dependents = set(owners) - set(basis)
    need({row["dependent"] for row in cert["relations"]} == dependents
         and len(cert["relations"]) == len(dependents) == 5, "five relation pivots")
    products = 0
    for row in cert["relations"]:
        terms = {v: F(q) for v, q in row["coefficients"]}
        need(len(terms) == len(row["coefficients"]) and terms.get(row["dependent"]) == 1
             and set(terms) <= set(basis) | {row["dependent"]}, "triangular relation support")
        residual = defaultdict(F)
        for token, factor in terms.items():
            for column, value in values[token].items():
                residual[column] += factor*value
                products += 1
        need(not any(residual.values()), "nonzero rational relation residual")
    return dict(anchor=anchor, forced_owners=24, exact_rank=19, exact_defect=5,
                independent_relations=5, rational_relation_products=products,
                literal_path_edges=sum(len(row["birth_path"]) + len(row["future_path"])
                                       - int(bool(row["birth_path"])) - 1 for row in paths))


def calculate():
    pins = provenance()
    need(PRIME > 1 and all(PRIME % d for d in range(2, isqrt(PRIME)+1)) and GRID % PRIME,
         "prime field and invertible grid")
    graph = SOURCE["read_graph"]()
    forms = {v: [(d, F(q)) for d, q in row] for v, row in graph["forms"]}
    sets, users = mandatory_sets(graph, forms)
    values, products = coefficients(graph, forms)
    modular = {v: {i: z % PRIME for i, z in row.items() if z % PRIME} for v, row in values.items()}
    outputs = range(graph["first_output"], graph["first_output"] + len(graph["final"]))
    endpoint_rank = rank_mod(outputs, modular)
    need(endpoint_rank == len(graph["initial"]) == len(graph["final"]) == 1501, "full endpoint information")
    cache, defects, trace = {}, Counter(), sha256()
    maximum_size = max(map(len, sets.values()))
    for anchor in graph["schedule"]:
        owners = tuple(sets[anchor])
        if owners not in cache:
            cache[owners] = rank_mod(owners, modular)
        defect_upper = len(owners) - cache[owners]
        need(defect_upper <= 5, "all-anchor rational defect upper bound")
        defects[defect_upper] += 1
        trace.update(encoded([anchor, owners, cache[owners]]) + b"\n")
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    witness = check_certificate(cert, sets, users, values, modular)
    bad_relation, bad_path = deepcopy(cert), deepcopy(cert)
    bad_relation["relations"][0]["coefficients"][0][1] = "1"
    bad_path["paths"][0]["future_path"] = [cert["anchor"], cert["owners"][0], bad_path["paths"][0]["use"]]
    rejected = []
    for changed, reason in [(bad_relation, "nonzero rational relation residual"),
                            (bad_path, "literal dependency path")]:
        try:
            check_certificate(changed, sets, users, values, modular)
        except ValueError as error:
            need(str(error) == reason, "certificate control reason")
            rejected.append(reason)
        else:
            raise ValueError("changed certificate accepted")
    rows = {v: tuple(d for d, _ in row) for v, row in graph["forms"]}
    order = SOURCE["release_order"](rows)
    slots, capacity = SOURCE["allocate"](order, rows, [~i for i in range(1501)], outputs)
    peak, event, reads = SOURCE["replay"](graph, order, slots, capacity)
    need(peak == capacity == 2106 and reads == 169343, "retained attaining upper bound")
    lower = endpoint_rank + witness["exact_defect"] + 1
    return dict(status="PASS_BANKED_NATIVE_ORDER_LOWER_BOUND", graph_sha256=SOURCE["GRAPH_SHA256"],
                source_pins=pins, coefficient_products=products, grid=GRID, prime=PRIME,
                endpoint_rank=endpoint_rank, row_anchors=len(sets), distinct_forced_sets=len(cache),
                forced_owner_incidences=sum(map(len, sets.values())), maximum_fixed_forced_owners=maximum_size,
                modular_defect_upper_histogram={str(k): v for k, v in sorted(defects.items())},
                complete_rank_trace_sha256=trace.hexdigest(), witness=witness,
                universal_snapshot_lower_bound=lower, single_anchor_rank_family_ceiling=lower,
                source_order_upper_bound=capacity, remaining_bank_gap=capacity-lower,
                upper_bound_replay=dict(first_peak_event=event, donor_reads=reads),
                rejected_certificate_controls=rejected,
                scope="All legal row orders under the retained distinct-snapshot contract; the 1507 ceiling applies only to the stated single-anchor rank bound, not to the global optimum.")


if __name__ == "__main__":
    result = calculate()
    need(result == json.loads((HERE / "RESULT.json").read_text()), "receipt mismatch")
    print(result["status"], result["universal_snapshot_lower_bound"], "<= optimum <=", result["source_order_upper_bound"])
