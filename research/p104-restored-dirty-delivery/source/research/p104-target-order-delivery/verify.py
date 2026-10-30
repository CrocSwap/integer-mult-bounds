#!/usr/bin/env python3
"""Exact certificate replay for one P104 per-target delivery geometry.

Standard library only. All acceptance checks remain enabled under -O.
The supplied-copy boundary is explicit: no dirty-copy compiler is assumed.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
from itertools import combinations, product
from fractions import Fraction
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def basis(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return tuple(pivots.values())


def in_span(value, vectors):
    return len(basis((*vectors, value))) == len(basis(vectors))


def rank(rows):
    return len(basis(rows))


def inner(a, b):
    numerator = sum(x * y for x, y in zip(a, b))
    require(numerator % 4 == 0, "nonintegral E8 pairing")
    return numerator // 4


def roots():
    result = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            result.append(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            result.append((1, *signs))
    require(len(set(result)) == 120, "root count")
    require(all(inner(r, r) == 2 for r in result), "root norm")
    return sorted(result)


def source_check():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    pins = []
    for item in manifest["files"]:
        if item["usage"] != "input":
            continue
        data = (ROOT / item["path"]).read_bytes()
        require(sha256(data).hexdigest() == item["sha256"], "source hash: " + item["path"])
        pins.append(item["path"])
    return pins


def geometry():
    source = json.loads((ROOT / "research/biframe-decoder-ladder/RESULTS.json").read_text())
    fixture = source["section4_explicit_P104"]
    lines = roots()
    index = {r: i for i, r in enumerate(lines)}
    pairs = [(tuple(a), tuple(b)) for a, b in fixture["pairs_doubled_coordinates"]]
    require(len(pairs) == 8 and all(a in index and b in index for a, b in pairs), "centre roots")
    removed = {tuple(r) for r in fixture["F0"] + fixture["C"]}
    require(len(removed) == 16 and removed <= set(lines), "puncture")
    ports = [r for r in lines if r not in removed]
    gram = [[inner(a, b) for b in lines] for a in lines]
    binary = [sum(((entry + 1) & 1) << j for j, entry in enumerate(row)) for row in gram]
    indices = []
    independent = []
    for i, row in enumerate(binary):
        if not in_span(row, independent):
            independent.append(row)
            indices.append(i)
    require(len(indices) == 9, "binary pairing rank")
    # Coordinate restriction to independent columns is injective on the row space.
    labels = [sum(((row >> j) & 1) << k for k, j in enumerate(indices)) for row in binary]
    require(rank(labels) == 9 and len(set(labels)) == 120, "label embedding")
    for a in range(120):
        for b in range(120):
            require(((binary[a] >> b) & 1) == ((gram[a][b] + 1) & 1), "binary geometry")
    centre_labels = [labels[index[a]] for a, _ in pairs]
    require(rank(centre_labels) == 8, "eight independent survivor labels")
    d = [[inner(r, a) for a, _ in pairs] for r in ports]
    t = []
    for r in ports:
        row = []
        for a, b in pairs:
            ab = inner(a, b)
            require(abs(ab) == 1, "mixed centre pair")
            row.append(2 * inner(r, b) // ab)
        t.append(row)
    require(all(sum(d[i][k] * t[j][k] for k in range(8)) == 2 * inner(a, b)
                for i, a in enumerate(ports) for j, b in enumerate(ports)), "decoder identity")
    costs = []
    for k, (a, b) in enumerate(pairs):
        readers = [i for i, r in enumerate(ports) if d[i][k]]
        sources = [j for j, r in enumerate(ports) if t[j][k]]
        require(len(readers) == len(sources) == 52, "centre support count")
        rlabels = [labels[index[ports[i]]] for i in readers]
        slabels = [labels[index[ports[j]]] for j in sources]
        require(rank(rlabels) == rank(slabels) == 8, "centre hyperplanes")
        require(in_span(centre_labels[k], slabels), "survivor in gather span")
        require(all((inner(a, ports[i]) + 1) % 2 == 0 for i in readers), "survivor orthogonal to readers")
        pairing = [sum(((inner(ports[i], ports[j]) + 1) & 1) << v
                       for v, j in enumerate(sources)) for i in readers]
        costs.append(rank(pairing))
    require(costs == [7] * 8, "COPY56")
    masks = [sum(bool(value) << k for k, value in enumerate(row)) for row in d]
    require(len(set(masks)) == 104, "distinct target masks")
    require(Counter(m.bit_count() for m in masks) == {2: 12, 3: 24, 4: 32, 5: 24, 6: 12}, "target layers")
    return {"ports": ports, "pairs": pairs, "d": d, "t": t, "masks": masks,
            "labels": centre_labels, "best_global_order": fixture["staggered_best_global_order"]}


def minimum_chains(vertices):
    """Bipartite matching supplies an explicit minimum chain cover of subsets."""
    vertices = sorted(set(vertices), key=lambda s: (s.bit_count(), s))
    successors = [[j for j, b in enumerate(vertices) if a != b and a & b == a]
                  for a in vertices]
    matched = {}

    def augment(i, seen):
        for j in successors[i]:
            if j not in seen:
                seen.add(j)
                if j not in matched or augment(matched[j], seen):
                    matched[j] = i
                    return True
        return False

    for i in range(len(vertices)):
        augment(i, set())
    forward = {i: j for j, i in matched.items()}
    chains = []
    for i in range(len(vertices)):
        if i not in matched:
            chain = [vertices[i]]
            while i in forward:
                i = forward[i]
                chain.append(vertices[i])
            chains.append(chain)
    require(sum(map(len, chains)) == len(vertices), "matching cover")
    return chains


def orders_from_tree(certificate, masks):
    edges = certificate["parent_edges"]
    parent = {}
    for s, k in edges:
        require(isinstance(s, int) and 0 < s < 256 and isinstance(k, int) and 0 <= k < 8,
                "parent edge domain")
        require(s >> k & 1 and s not in parent, "parent edge uniqueness")
        parent[s] = k
    used = set()
    orders = []
    for mask in masks:
        reverse = []
        s = mask
        while s:
            require(s in parent, "missing path prefix")
            used.add(s)
            k = parent[s]
            reverse.append(k)
            s ^= 1 << k
        orders.append(list(reversed(reverse)))
    require(used == set(parent), "unused tree edges")
    return orders


def events_from_orders(orders, masks):
    require(len(orders) == len(masks), "target order count")
    events = []
    for target, (order, expected) in enumerate(zip(orders, masks)):
        mask = 0
        for k in order:
            require(isinstance(k, int) and 0 <= k < 8 and not (mask >> k & 1), "repeated or invalid read")
            mask |= 1 << k
            events.append((mask.bit_count(), mask, k, target))
        require(mask == expected, "missing or extra target read")
    require(len(events) == 416, "read event count")
    return sorted(events)


def evaluate(orders, chains, geo):
    events = events_from_orders(orders, geo["masks"])
    require(len(chains) == 8 and all(chains), "centre chain inventory")
    used = {(s, k) for _, s, k, _ in events}
    assignment = {}
    for k, centre_chains in enumerate(chains):
        for ci, chain in enumerate(centre_chains):
            require(chain, "empty chain")
            previous = 1 << k
            for s in chain:
                require(isinstance(s, int) and 0 < s < 256 and s >> k & 1, "chain frame domain")
                require(previous & s == previous, "nonnested copy chain")
                require((s, k) not in assignment, "duplicate chain frame")
                assignment[s, k] = ci
                previous = s
    require(set(assignment) == used, "chain event coverage")
    # Direct replay provides a chronological certificate, not just a path cover.
    target_frame = [0] * 104
    copy_frame = [[1 << k for _ in c] for k, c in enumerate(chains)]
    h_copy, h_target = Counter(), Counter()
    delivered = [[0] * 8 for _ in range(104)]
    reads_per_copy = defaultdict(list)
    for dimension, frame, k, target in events:
        require(frame == (target_frame[target] | (1 << k)), "target chronological frame")
        require(target_frame[target] != frame, "target read duplicated")
        ci = assignment[frame, k]
        previous = copy_frame[k][ci]
        require(previous & frame == previous, "copy chronological frame")
        delta = dimension - previous.bit_count()
        if delta:
            h_copy[delta] += 1
        h_target[dimension - target_frame[target].bit_count()] += 1
        copy_frame[k][ci] = frame
        target_frame[target] = frame
        delivered[target][k] += geo["d"][target][k]
        reads_per_copy[k, ci].append(target)
    require(delivered == geo["d"], "scalar delivery map")
    for k, frames in enumerate(copy_frame):
        for frame in frames:
            h_copy[9 - frame.bit_count()] += 1
    for mask in target_frame:
        h_target[8 - mask.bit_count()] += 1
    chain_count = sum(map(len, chains))
    require(sum(r * n for r, n in h_copy.items()) == 8 * chain_count, "copy tail mass")
    require(sum(r * n for r, n in h_target.items()) == 8 * 104, "target tail mass")
    # Every final target frame of rank four is a distinct required visit.
    rank_four = [m for m in geo["masks"] if m.bit_count() == 4]
    require(len(rank_four) == 32 and len(set(rank_four)) == 32, "rank-four antichain")
    require(all(a & b != a and a & b != b for a, b in combinations(rank_four, 2)), "antichain inclusion")
    # Extra dirty input on a supplied copy reaches a target with nonzero coefficient.
    # This certifies the boundary limitation, not a dirty-copy implementation.
    require(len(reads_per_copy) == chain_count, "unused copy")
    dirty_sensitivity = []
    for (k, ci), targets in sorted(reads_per_copy.items()):
        residual = [0] * 104
        for target in targets:
            residual[target] += geo["d"][target][k]
        require(any(residual), "dirty sensitivity unexpectedly zero")
        dirty_sensitivity.append({"centre": k, "chain": ci, "affected_targets": sum(bool(v) for v in residual)})
    return {"chains": chain_count, "chains_per_centre": list(map(len, chains)),
            "extra_arrays_beyond_eight": chain_count - 8,
            "events": len(events), "rank_four_antichain": rank_four,
            "copy_tail_profile": {str(k): v for k, v in sorted(h_copy.items())},
            "target_tail_profile": {str(k): v for k, v in sorted(h_target.items())},
            "copy_tail_mass": 8 * chain_count, "target_tail_mass": 832,
            "dirty_copy_sensitivity": dirty_sensitivity,
            "chronological_event_sha256": sha256(json.dumps(events, separators=(",", ":")).encode()).hexdigest()}

def conditional_price(new, old):
    """Price only the declared delivered-copy tails, not a supplier moment."""
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("p104_pinned_intervals", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    prices = {}
    for a in (Fraction(0), Fraction(3351, 2000000), Fraction(1, 99)):
        intervals = {}
        for name, profile in (("new", new), ("global_order_control", old)):
            lo = hi = Fraction(0)
            for r, count in profile.items():
                low, high = module.child_cost(int(r), 73, a)
                lo += count * low
                hi += count * high
            intervals[name] = (lo, hi)
        nlo, nhi = intervals["new"]
        olo, ohi = intervals["global_order_control"]
        require(nhi < olo, "conditional delivery-tail moment improvement")
        prices[str(a)] = {
            "new": [str(nlo), str(nhi)],
            "global_order_control": [str(olo), str(ohi)],
            "saving": [str(olo - nhi), str(ohi - nlo)],
        }
    return {"width": 73, "role_denominator": "none: this is a child-sum subtotal",
            "scope": "copy tails from supplied singleton frames to rank nine only",
            "intervals_by_saving_a": prices}



def global_control(geo):
    order = geo["best_global_order"]
    orders = [[k for k in order if mask >> k & 1] for mask in geo["masks"]]
    events = events_from_orders(orders, geo["masks"])
    chains = [minimum_chains([s for _, s, key, _ in events if key == k]) for k in range(8)]
    receipt = evaluate(orders, chains, geo)
    require(receipt["chains"] == 55, "predecessor global-order control")
    return receipt


def rejected(fn):
    try:
        fn()
    except (ValueError, KeyError):
        return True
    raise ValueError("mutation was accepted")


def run():
    pins = source_check()
    geo = geometry()
    certificate = json.loads((HERE / "SCHEDULE.json").read_text())
    orders = orders_from_tree(certificate, geo["masks"])
    chains = certificate["chains"]
    result = evaluate(orders, chains, geo)
    require(result["chains"] == 32, "sharp antichain attainment")
    directions = {}
    conflict = None
    for target, order in enumerate(orders):
        for i, k in enumerate(order):
            for other in order[i + 1:]:
                if (other, k) in directions and conflict is None:
                    conflict = {"first_target": directions[other, k], "second_target": target,
                                "first_precedence": [other, k], "second_precedence": [k, other]}
                directions[k, other] = target
    require(conflict is not None, "per-target order genuinely differs from global order")
    control = global_control(geo)
    difference = {r: control["copy_tail_profile"].get(r, 0) - result["copy_tail_profile"].get(r, 0)
                  for r in set(control["copy_tail_profile"]) | set(result["copy_tail_profile"])}
    require(all(count >= 0 for count in difference.values()) and any(difference.values()),
            "componentwise conditional tail dominance")
    single_cut = [len(minimum_chains([m for m in geo["masks"] if m >> k & 1])) for k in range(8)]
    require(single_cut == [19] * 8, "single-cut predecessor control")
    # Rebinding the matrix identity catches a coefficient error independently of scheduling.
    bad_d = deepcopy(geo["d"])
    bad_d[0][next(k for k, value in enumerate(bad_d[0]) if value)] += 1
    require(any(sum(bad_d[i][k] * geo["t"][j][k] for k in range(8)) != 2 * inner(a, b)
                for i, a in enumerate(geo["ports"]) for j, b in enumerate(geo["ports"])), "coefficient mutation")
    bad_orders = deepcopy(orders)
    bad_orders[0].pop()
    controls = {"omitted_read": rejected(lambda: evaluate(bad_orders, chains, geo))}
    repeated = deepcopy(orders)
    repeated[0].append(repeated[0][0])
    controls["duplicate_read"] = rejected(lambda: evaluate(repeated, chains, geo))
    missing = deepcopy(chains)
    missing[0].pop()
    controls["omitted_copy_chain"] = rejected(lambda: evaluate(orders, missing, geo))
    wrong = deepcopy(chains)
    wrong[0][0][0] ^= 1
    controls["wrong_survivor_frame"] = rejected(lambda: evaluate(orders, wrong, geo))
    reverse = deepcopy(chains)
    k, ci = next((k, ci) for k, cs in enumerate(reverse) for ci, c in enumerate(cs) if len(c) > 1)
    reverse[k][ci] = list(reversed(reverse[k][ci]))
    controls["reversed_chain"] = rejected(lambda: evaluate(orders, reverse, geo))
    bad_tree = deepcopy(certificate)
    bad_tree["parent_edges"].pop()
    controls["broken_target_path"] = rejected(lambda: orders_from_tree(bad_tree, geo["masks"]))
    controls["decoder_coefficient"] = True
    controls["all_dirty_copies_detected"] = len(result["dirty_copy_sensitivity"]) == 32
    return {"schema_version": 1, "claim": "exact 32-chain minimum in minimal-prefix per-target-order geometry",
            "source_inputs": pins, "decoder_entries": 10816, "binary_entries": 14400,
            "copy_ranks": [7] * 8, "target_layer_counts": {str(k): v for k, v in sorted(Counter(m.bit_count() for m in geo["masks"]).items())},
            "schedule": result, "global_order_control": control,
            "conditional_tail_price": conditional_price(result["copy_tail_profile"], control["copy_tail_profile"]),
            "tail_profile_difference": dict(sorted(difference.items(), key=lambda kv: int(kv[0]))),
            "incompatible_global_order_witness": conflict,
            "single_cut_control": single_cut, "controls": controls,
            "physical_supplier": False, "new_kappa": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate this package's exact receipt")
    args = parser.parse_args()
    result = run()
    destination = HERE / "RESULT.json"
    if args.write:
        destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(destination.read_text()) == result, "stored result mismatch")
    print("PASS_P104_TARGET_ORDER_DELIVERY chains=32 extra_arrays=24 reads=416 lower_bound=32 controls=8 no_new_kappa")


if __name__ == "__main__":
    main()
