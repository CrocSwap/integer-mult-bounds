"""Exact positive-prefix accounting and optimal cuts of one rooted forest.

This module owns unsigned coefficient growth, not scalar F2 correctness.
The dynamic program minimizes XOR count over all subsets of the fixed MST's
nonroot edges, subject to the unchanged 104-bit local prefix allowance.
"""

from __future__ import annotations

from functools import lru_cache
from math import isqrt

from construct import construct, extract_kernels


def scalar_events(word: dict) -> list[tuple[str, int, int, str]]:
    """Flatten the exporter order; frame moves do not affect scalar norms."""
    events = []
    count = 2 * word["v"] + word["R"]
    for phase in ("D", "A"):
        for _, destination, sources in word[phase]:
            events.extend(("add", destination, source, phase) for source in sources)
    for index, helper in enumerate(word["ret"]):
        events.append(("copy", count, helper, "scatter"))
        events.extend(("add", word["v"] + target, count, "scatter")
                      for target, row in enumerate(word["scatter"]) if index in row)
        events.append(("erase", count, helper, "scatter"))
    for phase in ("B", "C"):
        for _, destination, sources in word[phase]:
            events.extend(("add", destination, source, phase) for source in sources)
    return events


def positive_pass(word: dict, reverse: bool = False, omit_d: bool = False) -> dict:
    """Use the official unit-start, absolute-ADD, COPY/ERASE convention."""
    count = 2 * word["v"] + word["R"]
    values = [1] * (count + 1)
    events = scalar_events(word)
    if reverse:
        events.reverse()
    largest = 1
    opened = False
    for operation, destination, source, phase in events:
        if omit_d and phase == "D":
            continue
        if reverse:
            operation = {"copy": "erase", "erase": "copy"}.get(operation, operation)
        if operation == "add":
            if destination == source or destination == count:
                raise ValueError("invalid scalar ADD")
            values[destination] += values[source]
            largest = max(largest, values[destination])
        elif operation == "copy":
            if opened:
                raise ValueError("overlapping copied-center lifetimes")
            values[count] = values[source]
            opened = True
        else:
            if operation != "erase" or not opened:
                raise ValueError("unmatched copied-center erase")
            values[count] = 0
            opened = False
    if opened:
        raise ValueError("unclosed copied center")
    return {"maximum": largest, "final_norms": values[:count]}


def prefix_bill(word: dict, allowance_bits: int = 104) -> dict:
    if type(allowance_bits) is not int or allowance_bits <= 0:
        raise ValueError("allowance_bits must be a positive integer")
    forward = positive_pass(word)["maximum"]
    backward = positive_pass(word, reverse=True)["maximum"]
    payload = 64 * forward ** 3 * backward ** 2
    return {"forward_maximum": forward, "reverse_maximum": backward,
            "payload_upper": payload, "payload_bits": payload.bit_length(),
            "allowance_bits": allowance_bits,
            "within_allowance": payload < 1 << allowance_bits}


def solve_budget(word: dict, seed: int = 6, allowance_bits: int = 104) -> dict:
    """Optimize every cut subset by ancestor-state dynamic programming.

    For the pinned word, work-register growth fixes F=144651 independently
    of D. Removing an ancestor edge cannot increase any positive D output:
    weighted |K_i| <= weighted |K_i xor K_p| + weighted |K_p|, and all
    initial target norms are nonnegative. The unchanged tail never reads a
    target, so every cut forest retains this same forward maximum.
    """
    kernels = extract_kernels(word)
    candidate, recipe = construct(word, seed=seed)
    count = word["v"]
    dummy = count
    parents = recipe["mst_parents"]
    children = [[] for _ in range(count)]
    roots = []
    for vertex, parent in enumerate(parents):
        if parent == dummy:
            roots.append(vertex)
        else:
            children[parent].append(vertex)
    for phase in ("A", "B", "C"):
        for _, _, sources in word[phase]:
            if any(count <= source < 2 * count for source in sources):
                raise ValueError("forward cut monotonicity requires a target-free tail")
    forward = positive_pass(candidate)
    work_maximum = max(forward["final_norms"][:count] +
                       forward["final_norms"][2 * count:])
    if work_maximum != forward["maximum"]:
        raise ValueError("uncut forward bound is not fixed by unchanged work rows")
    if type(allowance_bits) is not int or allowance_bits <= 0:
        raise ValueError("allowance_bits must be a positive integer")
    cap = isqrt(((1 << allowance_bits) - 1) // (64 * work_maximum ** 3))
    boundary = positive_pass(word, reverse=True, omit_d=True)
    if boundary["maximum"] > cap:
        raise ValueError("unchanged reverse tail already exceeds the allowance")
    incoming = boundary["final_norms"][count:2 * count]
    helper_weights = boundary["final_norms"]
    root_norm = [incoming[i] + sum(helper_weights[h] for h in kernels[i])
                 for i in range(count)]
    edge_norm = [0 if parent == dummy else
                 incoming[i] + incoming[parent] +
                 sum(helper_weights[h] for h in kernels[i] ^ kernels[parent])
                 for i, parent in enumerate(parents)]
    root_cost = [len(kernel) for kernel in kernels]
    edge_cost = [0 if parent == dummy else
                 len(kernels[i] ^ kernels[parent]) + 2
                 for i, parent in enumerate(parents)]

    @lru_cache(maxsize=count * count)
    def path_norm(vertex: int, ancestor: int) -> int:
        if vertex == ancestor:
            return root_norm[vertex]
        parent = parents[vertex]
        if parent == dummy:
            raise ValueError("invalid ancestor state")
        return edge_norm[vertex] + path_norm(parent, ancestor)

    states = []

    @lru_cache(maxsize=count * count)
    def best(vertex: int, ancestor: int) -> tuple[int, tuple[int, ...]] | None:
        norm = path_norm(vertex, ancestor)
        if norm > cap:
            states.append({"vertex": vertex, "root": ancestor, "norm": norm,
                           "cost": None, "cuts": None})
            return None
        cost = root_cost[vertex] if vertex == ancestor else edge_cost[vertex]
        cuts = ()
        for child in children[vertex]:
            options = []
            retained = best(child, ancestor)
            if retained is not None:
                options.append(retained)
            detached = best(child, child)
            if detached is not None:
                options.append((detached[0], tuple(sorted((child,) + detached[1]))))
            if not options:
                states.append({"vertex": vertex, "root": ancestor, "norm": norm,
                               "cost": None, "cuts": None})
                return None
            chosen_cost, chosen_cuts = min(options)
            cost += chosen_cost
            cuts = tuple(sorted(cuts + chosen_cuts))
        states.append({"vertex": vertex, "root": ancestor, "norm": norm,
                       "cost": cost, "cuts": list(cuts)})
        return cost, cuts

    total = 0
    cuts = ()
    for root in roots:
        optimum = best(root, root)
        if optimum is None:
            raise ValueError("no cut subset meets the unchanged prefix allowance")
        total += optimum[0]
        cuts = tuple(sorted(cuts + optimum[1]))
    selected, selected_recipe = construct(word, seed=seed, cuts=cuts)
    bill = prefix_bill(selected, allowance_bits)
    if not bill["within_allowance"] or bill["forward_maximum"] != work_maximum:
        raise ValueError("dynamic program disagrees with the full literal prefix pass")
    if selected_recipe["metrics"]["tree_weight"] != total:
        raise ValueError("dynamic program disagrees with emitted XOR count")
    return {"format": "r420-target-forest-budget/1", "seed": seed,
            "source_canonical_sha256": recipe["source"]["canonical_sha256"],
            "uncut_canonical_sha256": recipe["candidate_canonical_sha256"],
            "selected_canonical_sha256": selected_recipe["candidate_canonical_sha256"],
            "scope": "all cut subsets of the fixed seeded MST; no claim over other forests",
            "cut_positions": sum(parent != dummy for parent in parents),
            "subsets_covered": 1 << sum(parent != dummy for parent in parents),
            "forward_maximum_for_every_cut_subset": work_maximum,
            "reverse_maximum_allowed": cap, "minimum_D_xors": total,
            "cuts": list(cuts), "prefix": bill,
            "states": sorted(states, key=lambda row: (row["vertex"], row["root"])),
            "state_count": len(states),
            "reverse_boundary_target_norms": incoming,
            "reverse_boundary_helper_norms": helper_weights[2 * count:]}
