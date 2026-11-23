#!/usr/bin/env python3
"""Enumerate chronological reuse of the balanced Fano network's free stubs.

This changes the graph before scalar synthesis. It never appends a generic
decoder. A surviving topology must retain the three original routing demands
as an obstruction; every remaining input is still independent.
"""
from __future__ import annotations

import argparse
from itertools import product
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "references"))
from balanced_fano import balanced_fano


def partial_routes(width, pairs, prescribed):
    """Exact simultaneous routing of the three prescribed source tokens."""
    inputs = tuple(sorted(prescribed))
    states = {inputs}
    for a, b in pairs:
        states |= {tuple(b if p == a else a if p == b else p for p in s)
                   for s in states}
    destination = tuple(prescribed[p] for p in inputs)
    return {"routable": destination in states,
            "reachable_token_placements": len(states),
            "prescribed_destination": list(destination)}


def topologies():
    base = balanced_fano()
    time = {name: i for i, name in enumerate(base["gate_vertices"])}
    donors = [(name, role) for name, role in base["auxiliary_outputs"]
              if any(time[name] < time[rec] for rec, _ in base["auxiliary_inputs"])]
    recipients = [(name, role) for name, role in base["auxiliary_inputs"]
                  if any(time[don] < time[name] for don, _ in donors)]
    options = [[None] + [(don, role) for don, role in donors if time[don] < time[rec]]
               for rec, _ in recipients]
    count = 0
    for choice in product(*options):
        chosen = [p for p in choice if p is not None]
        if len(chosen) != len(set(chosen)):
            continue
        parent = list(range(base["W"]))

        def find(i):
            while parent[i] != i:
                i = parent[i]
            return i

        reused = []
        removed_inputs = set()
        for (receiver, r), donor in zip(recipients, choice):
            if donor is None:
                continue
            vertex, d = donor
            assert time[vertex] < time[receiver]
            assert find(r) != find(d)
            parent[find(r)] = find(d)
            reused.append({"from_vertex": vertex, "from_role": d,
                           "to_vertex": receiver, "to_role": r})
            removed_inputs.add(r)
        independent = [i for i in range(base["W"]) if i not in removed_inputs]
        assert len({find(i) for i in independent}) == len(independent)
        index = {find(i): k for k, i in enumerate(independent)}
        renumber = [index[find(i)] for i in range(base["W"])]
        pairs = [[renumber[a], renumber[b]] for a, b in base["pairs"]]
        assert all(a != b for a, b in pairs)
        prescribed = {renumber[i]: renumber[j] for i, j in base["prescribed"].items()}
        width = len(independent)
        donated = {d for _, d in chosen}
        final_roles = list(base["prescribed"].values()) + [
            r for _, r in base["auxiliary_outputs"] if r not in donated]
        assert sorted(renumber[r] for r in final_roles) == list(range(width))
        route = partial_routes(width, pairs, prescribed)
        yield {"id": count, "W": width, "pairs": pairs,
               "prescribed": prescribed, "reuse": reused,
               "independent_original_roles": independent,
               "old_to_new_roles": renumber, "routing": route}
        count += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = list(topologies())
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "topologies.json").write_text(json.dumps(cases, indent=2) + "\n")
    survivors = [c for c in cases if not c["routing"]["routable"]]
    lines = []
    for c in survivors:
        nums = [c["id"], c["W"], len(c["pairs"]), len(c["prescribed"])]
        nums += [x for pair in c["pairs"] for x in pair]
        nums += [x for pair in sorted(c["prescribed"].items()) for x in pair]
        lines.append(" ".join(map(str, nums)))
    (args.output / "search-input.txt").write_text("\n".join(lines) + "\n")
    print(json.dumps({"topologies": len(cases), "routing_obstruction_survivors": len(survivors),
                      "surviving_widths": sorted({c["W"] for c in survivors})}))


if __name__ == "__main__":
    main()
