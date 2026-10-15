"""Exact frame-class compression of the PR2163 temporal communication model.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0. The temporal model and cut are credited to Michael Yee/PR2163
and its P104 cut predecessors. This implementation uses only the PR1972 witness.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
SOURCE_HASH = "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e"
CUT = 2429
LIMIT = 104


class Invalid(ValueError):
    pass


def need(ok, why):
    if not ok:
        raise Invalid(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load_source(path=None):
    data = (Path(path) if path else ROOT / SOURCE).read_bytes()
    need(hashlib.sha256(data).hexdigest() == SOURCE_HASH, "source hash")
    return json.loads(data)


@lru_cache(None)
def span(vectors):
    """All 512 possible vectors are explicit bits; no basis convention needed."""
    members = {0}
    for v in vectors:
        need(type(v) is int and 0 <= v < 512, "frame vector")
        members |= {x ^ v for x in members}
    return sum(1 << x for x in members)


def dimension(frame):
    n = frame.bit_count()
    need(n > 0 and n & (n - 1) == 0, "subspace cardinality")
    return n.bit_length() - 1


def nested(a, b):
    return a & b in (a, b)


class Graph:
    def __init__(self):
        self.labels = ["source", "sink"]
        self.edges = []
        self.cut_nodes = {}
        self.facts = {}

    def node(self, cut, frame, count):
        self.labels.append([cut, hex(frame), count])
        return len(self.labels) - 1

    def edge(self, u, v, capacity, cost=0, kind="carry"):
        if capacity:
            self.edges.append([u, v, capacity, cost, kind])

    def fingerprint(self):
        return digest([self.labels, self.edges])


def build(w, paid=True, cut=CUT):
    """Contract unchanged frame-class chains; retain every membership event.

    Hubs have NO extra throughput constraint at the paid cut, exactly as in
    PR2163's nested_layers relaxation. All 104 flows may use a hub as transit.
    This explicitly optimistic graph does not model dirty-state restoration.
    """
    initial = w["initial_frames"]
    final = w["final_frames"]
    expected = {f"{f}{i}" for f, n in (("X", 104), ("Y", 104),
                ("G", 32), ("D", 32), ("Q", 8)) for i in range(n)}
    need(set(initial) == set(final) == expected, "register inventory")
    need(type(cut) is int and 0 <= cut <= len(w["program"]), "cut range")
    state = {r: span(tuple(v)) for r, v in initial.items()}
    counts = Counter(state.values())
    graph = Graph()
    hubs = {f: graph.node(0, f, counts[f]) for f in sorted(counts)}
    source_counts = Counter(f for r, f in state.items() if r.startswith("X"))
    for f in sorted(source_counts):
        graph.edge(0, hubs[f], source_counts[f], kind="source")
    kinds = Counter()
    rank_profile = Counter()
    births = 0

    def contact():
        graph.cut_nodes = {hex(f): hubs[f] for f in sorted(hubs)}
        graph.facts["cut_classes"] = [[hex(f), dimension(f), counts[f]]
                                       for f in sorted(hubs)]
        if paid:
            fs = sorted(hubs)
            for i, a in enumerate(fs):
                for b in fs[i + 1:]:
                    if nested(a, b):
                        gap = abs(dimension(a) - dimension(b))
                        need(gap > 0, "distinct nested dimensions")
                        graph.edge(hubs[a], hubs[b], LIMIT, gap, "paid")
                        graph.edge(hubs[b], hubs[a], LIMIT, gap, "paid")

    for index, event in enumerate(w["program"]):
        if index == cut:
            contact()
        kind = event[0]
        kinds[kind] += 1
        if kind in ("add", "copy"):
            need(len(event) == (5 if kind == "add" else 4), "scalar arity")
            dst, src = event[1:3]
            need(dst != src and dst in state and src in state, "scalar liveness")
            f = span(tuple(event[-1]))
            need(state[dst] == state[src] == f, "common frame")
            if kind == "add":
                need(Fraction(event[3]) != 0, "zero ADD")
            continue
        if kind == "transport":
            need(len(event) == 5, "transport arity")
            r, a, b, rank = event[1], span(tuple(event[2])), span(tuple(event[3])), event[4]
            need(r in state and state[r] == a, "transport source")
            need(nested(a, b), "nonnested transport")
            need(type(rank) is int and rank == abs(dimension(a) - dimension(b)) > 0,
                 "transport rank")
            old_a, old_b = hubs[a], hubs.get(b)
            na, nb = counts[a], counts[b]
            new_b = graph.node(index + 1, b, nb + 1)
            graph.edge(old_a, new_b, 1, kind="transport")
            if nb:
                graph.edge(old_b, new_b, nb)
            if na > 1:
                new_a = graph.node(index + 1, a, na - 1)
                graph.edge(old_a, new_a, na - 1)
                hubs[a] = new_a
            else:
                del hubs[a]
            hubs[b] = new_b
            counts[a] -= 1
            counts[b] += 1
            state[r] = b
            rank_profile[rank] += 1
        elif kind == "zero":
            need(len(event) == 3 and event[1] == "C" and "C" not in state, "private birth")
            f = span(tuple(event[2]))
            new = graph.node(index + 1, f, counts[f] + 1)
            if counts[f]:
                graph.edge(hubs[f], new, counts[f])
            hubs[f] = new
            counts[f] += 1
            state["C"] = f
            births += 1
        elif kind == "erase":
            need(len(event) == 3 and event[1] == "C" and "C" in state, "private erase")
            f = span(tuple(event[2]))
            need(state["C"] == f, "erase frame")
            if counts[f] > 1:
                new = graph.node(index + 1, f, counts[f] - 1)
                graph.edge(hubs[f], new, counts[f] - 1)
                hubs[f] = new
            else:
                del hubs[f]
            counts[f] -= 1
            del state["C"]
        else:
            raise Invalid("unknown event")
    if cut == len(w["program"]):
        contact()
    need(state == {r: span(tuple(v)) for r, v in final.items()}, "final frames")
    target_counts = Counter(f for r, f in state.items() if r.startswith("Y"))
    for f in sorted(target_counts):
        graph.edge(hubs[f], 1, target_counts[f], kind="sink")
    graph.facts.update({"cut": cut, "events": len(w["program"]),
                        "event_kinds": dict(sorted(kinds.items())),
                        "private_lifetimes": births,
                        "transport_profile": {str(r): n for r, n in sorted(rank_profile.items())},
                        "original_rank_mass": sum(r * n for r, n in rank_profile.items()),
                        "nodes": len(graph.labels), "edges": len(graph.edges),
                        "paid_edges": sum(e[4] == "paid" for e in graph.edges)})
    return graph
