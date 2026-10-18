#!/usr/bin/env python3
"""Exact evidence for the written restored-source connectivity theorem.

Prepared for Adam Gall with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported. Finite evidence is not an all-n proof.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREDECESSOR = "research/mutable-source-minimum-queries/CERTIFICATE.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def bind_sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    bound = []
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            payload = (ROOT / entry["path"]).read_bytes()
            require(hashlib.sha256(payload).hexdigest() == entry["sha256"],
                    "source hash mismatch: " + entry["path"])
            bound.append(entry["path"])
    selection = json.loads((PACKAGE / "SELECTION.json").read_text())
    task = json.loads((PACKAGE / "TASK.json").read_text())
    require(selection["seed"] == task["chooser_seed"], "selection seed mismatch")
    require(selection["base_commit"] == manifest["base_commit"] == task["base_commit"],
            "selection base mismatch")
    return bound


def join(parts, a, b):
    """Canonical partition after adding an undirected edge."""
    aa = next(part for part in parts if a in part)
    bb = next(part for part in parts if b in part)
    if aa == bb:
        return parts
    return tuple(sorted([part for part in parts if part not in (aa, bb)]
                        + [tuple(sorted(aa + bb))]))


def support_partition(rows):
    """Bipartite row/column graph, with all 2n vertices explicitly retained."""
    n = len(rows)
    parts = tuple((i,) for i in range(2 * n))
    for i, row in enumerate(rows):
        for j in range(n):
            if row >> j & 1:
                parts = join(parts, i, n + j)
    return parts


def intersection_partition(rows):
    """Separate oracle: flood row-intersection graph, then attach columns."""
    n = len(rows)
    unseen = set(range(n))
    result = []
    while unseen:
        members = {min(unseen)}
        pending = list(members)
        unseen -= members
        while pending:
            i = pending.pop()
            neighbors = {j for j in unseen if rows[i] & rows[j]}
            unseen -= neighbors
            members |= neighbors
            pending.extend(neighbors)
        columns = {n + j for i in members for j in range(n) if rows[i] >> j & 1}
        result.append(tuple(sorted(members | columns)))
    return tuple(sorted(result))


def bases(n, rows=(), span=frozenset({0})):
    if len(rows) == n:
        yield rows
        return
    for row in range(1, 1 << n):
        if row not in span:
            yield from bases(n, rows + (row,), span | {x ^ row for x in span})


def changed(rows, s, t):
    out = list(rows)
    out[t] ^= out[s]
    return tuple(out)


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            lead = value.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = value
                break
            value ^= pivots[lead]
    return len(pivots)


def single_gate_census():
    receipts = {}
    caches = {}
    for n in range(1, 5):
        states = {rows: support_partition(rows) for rows in bases(n)}
        expected = 1
        for j in range(n):
            expected *= (1 << n) - (1 << j)
        require(len(states) == expected, "incomplete GL enumeration")
        transitions = Counter()
        augmented_count = 0
        for rows, before in states.items():
            require(before == intersection_partition(rows), "graph oracle disagreement")
            require(all(len([v for v in part if v < n]) * 2 == len(part)
                        for part in before), "unbalanced invertible support component")
            for s in range(n):
                for t in range(n):
                    if s == t:
                        continue
                    after = states[changed(rows, s, t)]
                    delta = len(after) - len(before)
                    require(abs(delta) <= 1, "single gate changes count by more than one")
                    require(join(before, s, t) == join(after, s, t),
                            "auxiliary-edge partition is not invariant")
                    distinct = not any(s in part and t in part for part in before)
                    if distinct:
                        require(delta == -1, "distinct components did not merge")
                    transitions[str(delta)] += 1
                    augmented_count += 1
        receipts[str(n)] = {"matrices": len(states),
                            "transitions": augmented_count,
                            "component_delta_histogram": dict(sorted(transitions.items()))}
        caches[n] = states
    return receipts, caches


def closed_word_census(caches):
    receipts = {}
    for n, depth in ((3, 6), (4, 4)):
        identity = tuple(1 << i for i in range(n))
        gates = [(s, t) for s in range(n) for t in range(n) if s != t]
        states = caches[n]
        visits = 0
        closed = Counter()
        odd_connected = None

        def visit(rows, history, downs, ups, word):
            nonlocal visits, odd_connected
            visits += 1
            require(downs >= n - len(history), "historical mergers were not paid")
            if rows == identity:
                require(downs == ups, "closed source word has unbalanced potential")
                require(len(word) >= 2 * (n - len(history)), "closed connectivity bound fails")
                closed[f"{len(word)}:{len(history)}"] += 1
                if len(word) % 2 and len(history) == 1 and odd_connected is None:
                    odd_connected = word
            if len(word) == depth:
                return
            for s, t in gates:
                next_rows = changed(rows, s, t)
                next_history = join(history, s, t)
                delta = len(states[next_rows]) - len(states[rows])
                if len(next_history) < len(history):
                    require(delta == -1, "historical join not a current merge")
                visit(next_rows, next_history, downs + (delta == -1),
                      ups + (delta == 1), word + [(s, t)])

        visit(identity, tuple((i,) for i in range(n)), 0, 0, [])
        require(visits == sum(len(gates) ** d for d in range(depth + 1)),
                "closed-word coverage incomplete")
        if n == 3:
            require(odd_connected is not None, "odd closed-word control absent")
        receipts[str(n)] = {"max_length": depth, "words": visits,
                            "closed_length_components_histogram": dict(sorted(closed.items())),
                            "odd_connected_example": odd_connected}
    return receipts


def integer_partitions(n, minimum=1):
    if n == 0:
        yield ()
    for first in range(minimum, n + 1):
        for rest in integer_partitions(n - first, first):
            yield (first,) + rest


def block_skeleton(sizes):
    word = []
    start = 0
    for size in sizes:
        block = list(range(start, start + size))
        word.extend(("Q", j) for j in block)
        word.extend(("X", j, start) for j in block[1:])
        word.append(("Q", start))
        word.extend(("X", j, start) for j in reversed(block[1:]))
        start += size
    return word


def prefix_data(n, skeleton):
    rows = tuple(1 << i for i in range(n))
    q = 0
    points = [0]
    increments = []
    history = tuple((i,) for i in range(n))
    min_current_components = n
    downs = ups = 0
    for event in skeleton:
        if event[0] == "Q":
            v = rows[event[1]]
            increments.append(v)
            q ^= v
        else:
            _, s, t = event
            before = len(support_partition(rows))
            rows = changed(rows, s, t)
            after = len(support_partition(rows))
            history = join(history, s, t)
            downs += after < before
            ups += after > before
            min_current_components = min(min_current_components, after)
        points.append(q)
    return {"rows": rows, "prefixes": points, "increments": increments,
            "history": history, "downs": downs, "ups": ups,
            "min_current_components": min_current_components}


def attach_readouts(n, skeleton):
    data = prefix_data(n, skeleton)
    require(data["rows"] == tuple(1 << i for i in range(n)), "sources not restored")
    require(data["prefixes"][-1] == 0, "connector not restored")
    require(rank(data["increments"]) == n, "queries do not span requested masks")
    first_boundary = {}
    for index, point in enumerate(data["prefixes"]):
        first_boundary.setdefault(point, index)
    # Exact minimum-subset dynamic programming on (mask, cardinality parity).
    best = {(0, 0): ()}
    for point, boundary in first_boundary.items():
        following = dict(best)
        for (mask, parity), slots in best.items():
            key = mask ^ point, parity ^ 1
            candidate = slots + (boundary,)
            old = following.get(key)
            if old is None or (len(candidate), candidate) < (len(old), old):
                following[key] = candidate
        best = following
    by_boundary = {}
    slots = {}
    for mask in range(1, 1 << n):
        chosen = best.get((mask, 0))
        require(chosen is not None, "missing even readout subset")
        slots[str(mask)] = list(chosen)
        for boundary in chosen:
            by_boundary.setdefault(boundary, []).append(mask)
    word = []
    for boundary in range(len(skeleton) + 1):
        word.extend(("R", mask) for mask in by_boundary.get(boundary, []))
        if boundary < len(skeleton):
            word.append(skeleton[boundary])
    return word, slots, data


def lower_product(factors, source, target, scratch):
    if len(factors) == 1:
        return [(source, target, (factors[0],))], 0
    require(scratch, "private dirty scratch unavailable")
    split = len(factors) // 2
    right, right_nodes = lower_product(factors[:split], source, scratch[0], scratch[1:])
    left, left_nodes = lower_product(factors[split:], scratch[0], target, scratch[1:])
    return right + left + right[::-1] + left[::-1], 1 + 2 * right_nodes + 2 * left_nodes


def program(n, word, factors=("B",), expand=False):
    z = n + (1 << n) - 1
    height = (len(factors) - 1).bit_length() if expand else 0
    scratch = tuple(range(z + 1, z + 1 + height))
    leaves = []
    nodes = 0
    for event in word:
        if event[0] == "Q":
            if expand:
                lowered, executed = lower_product(factors, event[1], z, scratch)
                leaves.extend(lowered)
                nodes += executed
            else:
                leaves.append((event[1], z, tuple(factors)))
        elif event[0] == "R":
            leaves.append((z, n + event[1] - 1, (f"A{event[1]}",)))
        elif event[0] == "X":
            leaves.append((event[1], event[2], ()))
        else:
            raise ValueError("unknown root event")
    return leaves, z + 1 + height, nodes


def formal_replay(leaves, state):
    state = [set(row) for row in state]
    for source, target, factors in leaves:
        require(source != target and 0 <= source < len(state) and 0 <= target < len(state),
                "invalid or aliased leaf ports")
        contribution = {(origin, suffix + tuple(factors)) for origin, suffix in state[source]}
        state[target].symmetric_difference_update(contribution)
    return state


def identity_state(rows):
    return [{(j, ())} for j in range(rows)]


def expected_state(n, rows, factors):
    expected = identity_state(rows)
    for mask in range(1, 1 << n):
        expected[n + mask - 1] |= {(j, tuple(factors) + (f"A{mask}",))
                                  for j in range(n) if mask >> j & 1}
    return expected


def check_formal(n, word, factors=("B",), expand=False):
    leaves, rows, nodes = program(n, word, factors, expand)
    initial = identity_state(rows)
    final = formal_replay(leaves, initial)
    require(final == expected_state(n, rows, factors), "formal dirty endpoint mismatch")
    require(formal_replay(leaves[::-1], final) == initial, "formal inverse mismatch")
    return {"rows": rows, "events": len(leaves), "echo_nodes": nodes,
            "endpoint_sha256": digest([sorted(row) for row in final])}


def invoice(n, word, factors):
    counts = Counter(event[0] for event in word)
    leaves, rows, nodes = program(n, word, factors, True)
    maps = sum(bool(event[2]) for event in leaves)
    x = counts["X"]
    root = len(word)
    q_leaves, q_nodes = lower_product(factors, 0, 1, tuple(range(2, 2 + (len(factors) - 1).bit_length())))
    prices = {"b": len(q_leaves) + q_nodes + 1, "a": 2, "x": 2}
    bill = maps + nodes + x + root
    require(bill == counts["Q"] * prices["b"] + counts["R"] * prices["a"] + x * prices["x"],
            "complete invoice disagrees with literal expansion")
    return {"Q": counts["Q"], "R": counts["R"], "X": x,
            "map_leaves": maps, "echo_nodes": nodes, "root_dispatches": root,
            "dirty_rows": rows, "borrowed_dirty_rows": rows - n - ((1 << n) - 1),
            "prices": prices, "tariff": bill}


def partition_witnesses():
    evidence = []
    words = []
    for n in range(1, 9):
        for sizes in integer_partitions(n):
            skeleton = block_skeleton(sizes)
            word, slots, data = attach_readouts(n, skeleton)
            counts = Counter(event[0] for event in word)
            k = len(sizes)
            require(counts["Q"] == n + k and counts["X"] == 2 * (n - k), "frontier counts")
            require(counts["R"] == (n + 1) * (1 << (n - 1)), "affine-basis readout count")
            require(len(data["history"]) == k and data["downs"] == data["ups"] == n - k,
                    "frontier historical/potential counts")
            check_formal(n, word)
            evidence.append({"n": n, "block_sizes": sizes, "Q": counts["Q"],
                             "R": counts["R"], "X": counts["X"]})
            words.append({"n": n, "blocks": sizes, "word": word, "readout_slots": slots})
    return evidence, digest(words)


def cost_cone_controls():
    cases = 0
    for n in range(2, 9):
        endpoint_reads = (n + 1) * (1 << (n - 1))
        min_reads = 2 * ((1 << n) - 1)
        delta = endpoint_reads - min_reads
        require(delta >= 0, "negative readout gap")
        for a in (1, 2, 7):
            for x in (1, 3, 11):
                for margin in (0, 1, 14):
                    b = delta * a + 2 * x + margin
                    endpoint = (n + 1) * b + endpoint_reads * a + 2 * (n - 1) * x
                    for q in range(n + 2, 2 * n + 5):
                        lower = q * b + min_reads * a + max(0, 2 * (2 * n - q)) * x
                        require(lower >= endpoint, "price-cone lower bound failed")
                        if margin:
                            require(lower > endpoint, "strict price-cone inequality failed")
                        cases += 1
    return cases


def must_reject(fn, label):
    try:
        fn()
    except (ValueError, KeyError, IndexError):
        return label
    raise ValueError("negative control accepted: " + label)


def semantic_controls(word, factors, full_invoice):
    controls = []
    for label, tag, occurrence in (("missing_source_restoration", "X", -1),
                                    ("missing_connector_restoration", "Q", -1),
                                    ("connector_dirt_readout", "R", 0)):
        bad = list(word)
        index = [i for i, event in enumerate(bad) if event[0] == tag][occurrence]
        del bad[index]
        controls.append(must_reject(lambda bad=bad: check_formal(5, bad, factors), label))
    bad = list(word)
    at = next(i for i, event in enumerate(bad) if event[0] == "R")
    bad[at] = ("R", 2 if bad[at][1] == 1 else 1)
    controls.append(must_reject(lambda: check_formal(5, bad, factors), "wrong_output_mask"))
    leaves, rows, _ = program(5, word, factors, True)
    initial = identity_state(rows)
    expected = expected_state(5, rows, factors)
    damaged = list(leaves)
    first_q = next(i for i, event in enumerate(word) if event[0] == "Q")
    prefix_leaves = len(program(5, word[:first_q], factors, True)[0])
    q_leaves = len(program(5, [word[first_q]], factors, True)[0])
    # Final leaf of inverse(L) in the first full Q: this is private uncompute.
    cleanup = prefix_leaves + q_leaves - 1
    require(damaged[cleanup][1] >= 37, "cleanup control does not target private scratch")
    del damaged[cleanup]
    controls.append(must_reject(lambda: require(formal_replay(damaged, initial) == expected,
                                                "private cleanup missing"), "missing_private_uncompute"))
    reversed_factors, _, _ = program(5, word, factors[::-1], True)
    controls.append(must_reject(lambda: require(formal_replay(reversed_factors, initial) == expected,
                                                "factor order differs"), "noncommuting_factor_order"))
    heterogeneous, hrows, _ = program(5, word, factors, False)
    z = 5 + 31
    heterogeneous = [(s, t, (f"different_B{s}",) if t == z else ops)
                     for s, t, ops in heterogeneous]
    controls.append(must_reject(lambda: require(formal_replay(heterogeneous, identity_state(hrows))
                                                == expected_state(5, hrows, factors), "B not common"),
                                 "heterogeneous_source_map"))
    for field in ("echo_nodes", "root_dispatches", "X"):
        bad_invoice = dict(full_invoice)
        bad_invoice[field] -= 1
        controls.append(must_reject(lambda bad_invoice=bad_invoice: require(
            bad_invoice == invoice(5, word, factors), "unpaid obligation"), "unpaid_" + field))
    unclosed = [("Q", 0), ("Q", 1), ("Q", 2), ("X", 1, 0), ("X", 2, 0), ("Q", 0)]
    data = prefix_data(3, unclosed)
    require(data["prefixes"][-1] == 0 and rank(data["increments"]) == 3,
            "restoration-premise control is not otherwise feasible")
    controls.append(must_reject(lambda: attach_readouts(3, unclosed), "unrestored_source_premise"))
    controls.append(must_reject(lambda: attach_readouts(3, [("Q", 0), ("Q", 0)]),
                                 "missing_full_span_premise"))
    return controls


def compute():
    bound = bind_sources()
    gates, caches = single_gate_census()
    closed = closed_word_census(caches)
    partitions, words_hash = partition_witnesses()
    inherited = json.loads((ROOT / PREDECESSOR).read_text())
    word = [tuple(event) for event in inherited["schedules"]["minimum_queries"]["word"]]
    generated, slots, _ = attach_readouts(5, block_skeleton((5,)))
    require(generated == word, "credited root word differs from regenerated endpoint")
    require(slots == inherited["readout_slots"], "credited readout subset mismatch")
    factors = tuple(f"B{j}" for j in range(8))
    expanded = check_formal(5, word, factors, True)
    whole_invoice = invoice(5, word, factors)
    require(whole_invoice["tariff"] == 724, "eight-factor bill")
    b, a, x = (whole_invoice["prices"][name] for name in ("b", "a", "x"))
    require(b > 34 * a + 2 * x, "fixture outside strict global-optimality region")
    larger_q_floor = 7 * b + 62 * a + 6 * x
    require(larger_q_floor == 738, "larger-query tariff floor")
    # Historical connectivity need never occur in one current matrix.
    serial = [("Q", 0), ("X", 0, 1), ("Q", 1), ("X", 0, 1),
              ("X", 1, 2), ("Q", 2), ("X", 1, 2), ("Q", 2)]
    serial_word, _, serial_data = attach_readouts(3, serial)
    check_formal(3, serial_word)
    require(len(serial_data["history"]) == 1 and serial_data["min_current_components"] == 2,
            "serial connectivity control does not separate historical/current graphs")
    controls = semantic_controls(word, factors, whole_invoice)
    return {"schema_version": 1, "claim": "written all-n theorem; exact finite evidence, no new kappa",
            "source_inputs": bound, "single_gate_census": gates, "closed_word_census": closed,
            "partition_witnesses": partitions, "partition_word_sha256": words_hash,
            "credited_root_word_sha256": digest(word), "eight_factor_formal": expanded,
            "eight_factor_invoice": whole_invoice, "every_Q_at_least_7_tariff_lower_bound": larger_q_floor,
            "price_cone_integer_checks": cost_cone_controls(),
            "serial_connectivity_control": {"skeleton": serial, "increments": serial_data["increments"],
                                             "historical_components": 1, "minimum_current_components": 2,
                                             "Q": 4, "R": 16, "X": 4},
            "semantic_controls": controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate exact RESULT.json")
    args = parser.parse_args()
    # JSON arrays are the canonical representation of both tuples and lists.
    result = json.loads(canonical(compute()))
    path = PACKAGE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        require(result == json.loads(path.read_text()), "RESULT.json differs from exact recomputation")
    print("PASS_MUTABLE_SOURCE_CONNECTIVITY "
          f"GL_transitions={sum(v['transitions'] for v in result['single_gate_census'].values())} "
          f"partition_witnesses={len(result['partition_witnesses'])} "
          f"controls={len(result['semantic_controls'])} minQ_X=8 global_tariff=724 next_Q_floor=738 no_new_kappa")


if __name__ == "__main__":
    main()
