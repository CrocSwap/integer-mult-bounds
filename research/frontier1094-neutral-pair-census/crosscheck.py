#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Hanson Sun, with substantial OpenAI Codex assistance.
"""Enumerate all rank-class products after every neutral prefix.

Shares pinned input decoding/geometry with verify.py, but uses neither its
move mutator, candidate pruning, neutrality test nor census. Both algorithms
were written by the same AI agent; this is not independent human review.
"""
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def encode(value):
    return json.dumps(json.loads(json.dumps(value)), sort_keys=True, separators=(",", ":")).encode()


def enumerate_all(bins, roles):
    locations = [r["bin"] for r in roles]
    free = [b["capacity"] for b in bins]
    members = defaultdict(set)
    busy = {}
    for i, role in enumerate(roles):
        b = locations[i]
        free[b] -= role["width"]
        members[b].add(i)
        busy[bins[b]["family"], role["time"]] = i
    groups, destinations = defaultdict(set), defaultdict(set)
    for i, role in enumerate(roles):
        groups[free[locations[i]], role["width"]].add(i)
    for b, r in enumerate(free):
        destinations[r].add(b)

    def neutral(x, y, w):
        return (x + w) ** 2 + (y - w) ** 2 == x*x + y*y

    prefixes = []
    singles_capacity = singles_legal = 0
    for (x, w), ids in sorted(groups.items()):
        for y, dests in sorted(destinations.items()):
            if y < w:
                continue
            gain = (x + w) ** 2 + (y - w) ** 2 - x*x - y*y
            if gain < 0:
                continue
            for i in sorted(ids):
                time = roles[i]["time"]
                for b in sorted(dests):
                    if b == locations[i]:
                        continue
                    legal = (time in bins[b]["allowed"]
                             and busy.get((bins[b]["family"], time)) in (None, i))
                    if gain > 0:
                        singles_capacity += 1
                        singles_legal += legal
                    elif legal and neutral(x, y, w):
                        prefixes.append((i, b))
    if singles_legal:
        raise ValueError("baseline has improving single moves")

    profile_counts, witnesses, classes = Counter(), {}, Counter()
    sequence_hash = hashlib.sha256()
    productive = 0
    paths, final_allocations = [], set()
    candidate_checks = 0
    for i, dest in sorted(prefixes):
        origin = locations[i]
        x, y, width = free[origin], free[dest], roles[i]["width"]
        classes[x, width, y] += 1
        changed = {origin: x + width, dest: y - width}
        # Rebuild the affected class memberships, then enumerate EVERY class product.
        current = {k: set(v) for k, v in groups.items()}
        for j in members[origin] | members[dest]:
            old_bin = locations[j]
            new_bin = dest if j == i else old_bin
            w = roles[j]["width"]
            current[free[old_bin], w].remove(j)
            current.setdefault((changed[new_bin], w), set()).add(j)
        targets = {k: set(v) for k, v in destinations.items()}
        for b, r in changed.items():
            targets[free[b]].remove(b)
            targets.setdefault(r, set()).add(b)
        freed_key = bins[origin]["family"], roles[i]["time"]
        occupied_key = bins[dest]["family"], roles[i]["time"]
        hits = []
        for (u, w), ids in sorted(current.items()):
            if not ids:
                continue
            for v, dests in sorted(targets.items()):
                if not dests or v < w or (u + w)**2 + (v - w)**2 <= u*u + v*v:
                    continue
                for j in sorted(ids):
                    source = dest if j == i else locations[j]
                    time = roles[j]["time"]
                    for end in sorted(dests):
                        if end == source:
                            continue
                        candidate_checks += 1
                        key = bins[end]["family"], time
                        occupant = i if key == occupied_key else None if key == freed_key else busy.get(key)
                        if time not in bins[end]["allowed"] or occupant not in (None, j):
                            continue
                        delta = Counter()
                        for rank, count in ((u, -1), (v, -1), (u+w, 1), (v-w, 1)):
                            if rank:
                                delta[rank] += count
                        profile = tuple(sorted((r, c) for r, c in delta.items() if c))
                        hits.append((j, end, profile))
        productive += bool(hits)
        for j, end, profile in sorted(hits):
            path = [i, dest, j, end]
            paths.append(path)
            final = {i: dest, j: end}
            final_allocations.add(tuple(sorted((k, b) for k, b in final.items() if locations[k] != b)))
            profile_counts[profile] += 1
            witnesses.setdefault(profile, path)
            sequence_hash.update(encode(path) + b"\n")
    result = dict(single_capacity_improvements=singles_capacity, single_legal_improvements=0,
                  legal_neutral_prefixes=len(prefixes), productive_neutral_prefixes=productive,
                  neutral_classes=[dict(free_source=x, width=w, free_destination=y, count=n)
                                   for (x, w, y), n in sorted(classes.items())],
                  improving_sequences=sum(profile_counts.values()), sequence_sha256=sequence_hash.hexdigest(),
                  neutral_prefix_sha256=hashlib.sha256(encode(sorted(prefixes))).hexdigest(),
                  distinct_final_allocations=len(final_allocations), sequences=paths,
                  profiles=[dict(delta=dict(key), count=n, witness=witnesses[key])
                            for key, n in sorted(profile_counts.items())])
    return result, candidate_checks


def main():
    spec = importlib.util.spec_from_file_location("input_loader", HERE / "verify.py")
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    state, _, _ = loader.load_problem()
    result, checked = enumerate_all(state.bins, state.roles)
    expected = json.loads((HERE / "RESULT.json").read_text())["census"]
    if encode(result) != encode(expected):
        raise ValueError("all-class census disagrees with stored result")
    print("PASS_PR1094_ALL_CLASS_CROSSCHECK", "neutral=" + str(result["legal_neutral_prefixes"]),
          "sequences=" + str(result["improving_sequences"]), "capacity_pairs_checked=" + str(checked))


if __name__ == "__main__":
    main()
