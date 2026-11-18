"""Construct and check a field allocation on the frozen forward graph of PR 7674."""

import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
from heapq import heapify, heappop, heappush
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
# Clear1nsight, PR 7682, evidence/WIRE-RESULT.json, graphs.peer.canonical_sha256.
GRAPH_SHA256 = "d81ec9f47740852a4bf7bd83100feff5cb66b70e1973466e1609bbac8af75098"
CAPACITY = 2106


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_graph():
    raw = gzip.decompress((ROOT / "PEER-GRAPH.json.gz").read_bytes())
    require(sha256(raw).hexdigest() == GRAPH_SHA256, "wrong forward graph")
    return json.loads(raw)


def release_order(rows):
    """Choose a ready row with the most last-use donors; break ties by token."""
    users = defaultdict(set)
    for node, donors in rows.items():
        for donor in donors:
            users[donor].add(node)

    last_uses = Counter()
    for readers in users.values():
        if len(readers) == 1:
            last_uses[next(iter(readers))] += 1

    pending = {n: sum(d >= 0 for d in donors) for n, donors in rows.items()}
    ready = {n for n in rows if pending[n] == 0}
    order = []
    for _ in range(len(rows)):
        require(ready, "cycle in row dependencies")
        node = min(ready, key=lambda n: (-last_uses[n], n))
        ready.remove(node)
        order.append(node)
        for donor in rows[node]:
            readers = users[donor]
            readers.remove(node)
            if len(readers) == 1:
                last_uses[next(iter(readers))] += 1
        for reader in users[node]:
            pending[reader] -= 1
            if pending[reader] == 0:
                ready.add(reader)
    return order


def allocate(order, rows, entrances, outputs):
    """Assign disjoint closed lifetimes to slots in order of birth."""
    last = dict.fromkeys(entrances, 0)
    for event, node in enumerate(order, 1):
        last[node] = event
        for donor in rows[node]:
            last[donor] = event
    last.update(dict.fromkeys(outputs, len(order) + 1))
    slots = {node: slot for slot, node in enumerate(entrances)}
    active = [(last[node], slot) for node, slot in slots.items()]
    heapify(active)
    free = []
    capacity = len(active)
    for event, node in enumerate(order, 1):
        # A last read at this event still occupies a bank during this birth.
        while active and active[0][0] < event:
            _, slot = heappop(active)
            heappush(free, slot)
        if free:
            slot = heappop(free)
        else:
            slot = capacity
            capacity += 1
        slots[node] = slot
        heappush(active, (last[node], slot))
    return slots, capacity


def replay(graph, order, slots, capacity):
    """Check the supplied order and slots using live owners and unread edge counts."""
    forms = dict(graph["forms"])
    moves = {node: (src, dst) for node, src, dst in graph["moves"]}
    entrances = {~i: chart for i, chart in enumerate(graph["initial"])}
    outputs = {graph["first_output"] + i: chart for i, chart in enumerate(graph["final"])}
    require(len(order) == len(forms) and set(order) == forms.keys(), "row inventory")
    require(slots.keys() == entrances.keys() | forms.keys(), "slot inventory")
    require(all(0 <= slot < capacity for slot in slots.values()), "bank capacity")

    owners = {slots[token]: (token, chart) for token, chart in entrances.items()}
    require(len(owners) == len(entrances), "entrance bank collision")
    reads = Counter(d for row in forms.values() for d, _ in row)
    total_reads = reads.total()
    peak = len(owners)
    peak_event = 0
    for token in entrances:
        if reads[token] == 0:
            del owners[slots[token]]
    for event, node in enumerate(order, 1):
        src, dst = moves[node] if node in moves else (outputs[node], outputs[node])
        require(slots[node] not in owners, "overwrite of a live bank")
        owners[slots[node]] = (node, dst)
        if len(owners) > peak:
            peak, peak_event = len(owners), event

        # The frozen row carries its original ordered list of (donor, coefficient).
        for donor, _ in forms[node]:
            require(owners.get(slots[donor]) == (donor, src), "missing donor or wrong chart")

        # Release only after every donor was read and the child returned.
        for donor, _ in forms[node]:
            reads[donor] -= 1
            if reads[donor] == 0:
                del owners[slots[donor]]
        if node in moves and reads[node] == 0:
            del owners[slots[node]]

    require(all(count == 0 for count in reads.values()), "unconsumed scalar reads")
    require(len(owners) == len(outputs), "unexpected owner at installation")
    for token, chart in outputs.items():
        require(owners.pop(slots[token], None) == (token, chart), "missing public output")
    require(not owners, "incomplete final retirement")
    return peak, peak_event, total_reads


def negative_controls(graph, order, slots):
    forms = dict(graph["forms"])
    # The first nonempty row's first donor has to coexist with its result.
    node = next(n for n in order if forms[n])
    donor = forms[node][0][0]
    collided = dict(slots)
    collided[node] = slots[donor]
    for assignment, capacity, expected in (
        (collided, CAPACITY, "overwrite of a live bank"),
        (slots, CAPACITY - 1, "bank capacity"),
    ):
        try:
            replay(graph, order, assignment, capacity)
        except ValueError as exc:
            require(str(exc) == expected, f"unexpected rejection: {exc}")
        else:
            raise ValueError(f"accepted negative control: {expected}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--certificate", action="store_true", help="print the complete allocation as TSV")
    mode.add_argument("--receipt", action="store_true", help="print the computed result and hashes")
    args = parser.parse_args()
    graph = read_graph()
    rows = {n: tuple(d for d, _ in terms) for n, terms in graph["forms"]}
    entrances = [~i for i in range(len(graph["initial"]))]
    outputs = range(graph["first_output"], graph["first_output"] + len(graph["final"]))
    order = release_order(rows)
    slots, capacity = allocate(order, rows, entrances, outputs)
    peak, event, terms = replay(graph, order, slots, capacity)
    require(peak == capacity == CAPACITY, "wrong allocation peak")
    negative_controls(graph, order, slots)

    certificate = ["event\ttoken\tbank\n"]
    certificate.extend(f"0\t{n}\t{slots[n]}\n" for n in entrances)
    certificate.extend(f"{i}\t{n}\t{slots[n]}\n" for i, n in enumerate(order, 1))
    data = "".join(certificate).encode("ascii")
    paid = len(graph["moves"])
    homes = capacity + 1 + 4
    lifetimes = len(slots) + paid + 4
    receipt = {
        "graph_sha256": GRAPH_SHA256,
        "verifier_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "certificate_sha256": sha256(data).hexdigest(),
        "entrances": len(entrances), "paid_rows": paid, "terminal_rows": len(outputs),
        "row_events": len(order), "snapshot_assignments": len(slots), "scalar_terms": terms,
        "snapshot_banks": capacity, "first_peak_event": event, "first_peak_token": order[event - 1],
        "private_homes_per_occurrence": homes, "private_homes_for_16": 16 * homes,
        "lifetimes_per_occurrence": lifetimes, "full_resets_per_occurrence": 2 * lifetimes,
        "reset_allowance_for_16": 16 * (2 * lifetimes + 4 * (terms + len(order))),
    }
    if args.receipt:
        print(json.dumps(receipt, indent=2))
    elif args.certificate:
        sys.stdout.buffer.write(data)
    else:
        require(receipt == json.loads((ROOT / "RESULT.json").read_bytes()), "receipt mismatch")
        print(f"PASS_BANKED_NATIVE_ROW_ORDER {capacity} banks, {homes} private homes, {terms} reads")


if __name__ == "__main__":
    main()
