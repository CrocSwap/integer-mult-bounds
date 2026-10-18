#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Hanson Sun, with substantial OpenAI Codex assistance.
"""Exact two-relocation neighborhood of the pinned PR1094 owner map.

Geometry and owner admission reuse Josie Elliston's PR1091 auditor.
The neighborhood census below is separate; no supplier adoption is claimed.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = "research/complex-t16-rare-pattern-exchanges/data/"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def canonical(value):
    # JSON object keys are strings, including rank keys originally held as ints.
    normalized = json.loads(json.dumps(value))
    return json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()


def check_sources(root=ROOT):
    pins = read(HERE / "SOURCES.json")
    for item in pins["files"]:
        if item["usage"] == "input":
            need(hashlib.sha256((root / item["path"]).read_bytes()).hexdigest()
                 == item["sha256"], "source drift: " + item["path"])


class State:
    """Whole roles, fixed bins, strict windows and per-call family exclusion."""

    def __init__(self, bins, roles):
        self.bins = bins
        self.roles = roles
        self.location = [r["bin"] for r in roles]
        self.free = [b["capacity"] for b in bins]
        self.members = [set() for _ in bins]
        self.occupied = {}
        self.by_free = defaultdict(set)
        self.by_family = defaultdict(list)
        self.by_time = defaultdict(list)
        for b, item in enumerate(bins):
            self.by_family[item["family"]].append(b)
        for i, role in enumerate(roles):
            b = self.location[i]
            need(0 <= b < len(bins) and role["width"] > 0, "bad role")
            self.free[b] -= role["width"]
            self.members[b].add(i)
            key = (bins[b]["family"], role["time"])
            need(key not in self.occupied, "family collision")
            self.occupied[key] = i
            self.by_time[role["time"]].append(i)
            need(role["time"] in bins[b]["allowed"], "role outside window")
        for b, free in enumerate(self.free):
            need(free >= 0, "overfull bin")
            self.by_free[free].add(b)

    def legal(self, i, dest):
        role = self.roles[i]
        return (dest != self.location[i] and role["width"] <= self.free[dest]
                and role["time"] in self.bins[dest]["allowed"]
                and self.occupied.get((self.bins[dest]["family"], role["time"])) in (None, i))

    def move(self, i, dest):
        need(self.legal(i, dest), "illegal relocation")
        source = self.location[i]
        role = self.roles[i]
        for b in (source, dest):
            self.by_free[self.free[b]].remove(b)
        self.free[source] += role["width"]
        self.free[dest] -= role["width"]
        for b in (source, dest):
            self.by_free[self.free[b]].add(b)
        del self.occupied[self.bins[source]["family"], role["time"]]
        self.occupied[self.bins[dest]["family"], role["time"]] = i
        self.members[source].remove(i)
        self.members[dest].add(i)
        self.location[i] = dest
        return source

    def strict_candidates(self, role_ids=None):
        """All capacity-feasible concentrating moves, before time/family checks."""
        for i in range(len(self.roles)) if role_ids is None else sorted(role_ids):
            w = self.roles[i]["width"]
            source = self.location[i]
            for free in sorted(self.by_free):
                if w <= free < self.free[source] + w:
                    for dest in sorted(self.by_free[free]):
                        if dest != source:
                            yield i, dest

    def neutral_moves(self):
        for i, role in enumerate(self.roles):
            free = self.free[self.location[i]] + role["width"]
            for dest in sorted(self.by_free.get(free, ())):
                if self.legal(i, dest):
                    yield i, dest

    def histogram(self):
        return Counter(f for f in self.free if f)


def load_problem():
    check_sources()
    path = ROOT / "research/t16-owner-audit-seed67/verify.py"
    spec = importlib.util.spec_from_file_location("retained_owner_audit", path)
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)
    word = read(auditor.WORD)
    geo = auditor.geometry(read(ROOT / auditor.TEMPLATE), read(ROOT / auditor.PHASES))
    widths = auditor.word_widths(word)
    local = auditor.as_profile(word["report"]["local_profile"])
    source_roles = read(ROOT / PACKAGE / "OWNERS.json.gz")
    plan = read(ROOT / PACKAGE / "PLAN.json")
    supply = read(ROOT / PACKAGE / "SPEC.json")
    idle = auditor.as_profile(supply["expected"]["idle_remainder_profile"])
    need(local == auditor.as_profile(supply["providers"]["gauge44"]["expected_profile"]), "local profile")
    need(Counter(widths) == auditor.as_profile(supply["providers"]["gauge44"]["inventory"]), "helper inventory")
    baseline = auditor.audit(geo, widths, local, source_roles, plan, idle, 16)
    need(Counter(baseline["profile"]) == auditor.as_profile(plan["profile"]), "plan profile")
    windows, callpos = auditor.windows(geo, [tuple(x) for x in plan["order"]])
    bins = []
    for owner, child in sorted(windows):
        lo, hi = windows[owner, child]
        pair, side = geo["place"][child]
        allowed = frozenset(t for t, (stage, replica) in enumerate(plan["order"])
                            if lo < callpos[stage, replica] < hi
                            and (owner, pair) != (replica, geo["stage_pair"][stage]))
        for port in range(112):
            bins.append(dict(key=(owner, child, port), capacity=geo["rank"][child],
                             family=owner * 896 + (2 * pair + side) * 112 + port,
                             allowed=allowed))
    index = {b["key"]: i for i, b in enumerate(bins)}
    roles = [dict(bin=index[z["owner_replica"], z["child"], z["port"]],
                  width=z["width"], time=z["time"]) for z in source_roles]
    state = State(bins, roles)
    need(state.histogram() == idle, "initial histogram")
    context = (auditor, geo, widths, local, source_roles, plan)
    return state, baseline, context


def next_candidates(state, first, origin, original_groups):
    """Complete dependency neighborhood after a first move; see README proof."""
    i, dest = first
    changed = {origin, dest}
    candidates = set(state.strict_candidates(set().union(*(state.members[b] for b in changed))))
    # Other roles keep their old donor free rank. Both destination capacities changed.
    for b in changed:
        free = state.free[b]
        for (old_free, width), ids in original_groups.items():
            if width <= free < old_free + width:
                candidates.update((j, b) for j in ids)
    # Removing the first role can release its family for other roles of that call.
    for b in state.by_family[state.bins[origin]["family"]]:
        candidates.update((j, b) for j in state.by_time[state.roles[i]["time"]])
    return sorted(candidates)


def census(state):
    initial_hist = state.histogram()
    single_candidates = list(state.strict_candidates())
    improving_singles = [p for p in single_candidates if state.legal(*p)]
    need(not improving_singles, "baseline has an improving single relocation")
    groups = defaultdict(list)
    for i, role in enumerate(state.roles):
        groups[state.free[state.location[i]], role["width"]].append(i)
    prefixes = list(state.neutral_moves())
    neutral_classes, profile_counts, witnesses = Counter(), Counter(), {}
    productive = 0
    paths, final_allocations = [], set()
    sequences = hashlib.sha256()
    for first in prefixes:
        i, dest = first
        source = state.location[i]
        x, y = state.free[source], state.free[dest]
        neutral_classes[x, state.roles[i]["width"], y] += 1
        state.move(i, dest)
        hits = 0
        for j, end in next_candidates(state, first, source, groups):
            origin = state.location[j]
            u, v, w = state.free[origin], state.free[end], state.roles[j]["width"]
            if u + w <= v or not state.legal(j, end):
                continue
            delta = Counter()
            for r, c in ((u, -1), (v, -1), (u + w, 1), (v - w, 1)):
                if r:
                    delta[r] += c
            key = tuple(sorted((r, c) for r, c in delta.items() if c))
            profile_counts[key] += 1
            path = [i, dest, j, end]
            paths.append(path)
            placements = {i: dest, j: end}
            final_allocations.add(tuple(sorted((k, b) for k, b in placements.items()
                                               if state.roles[k]["bin"] != b)))
            witnesses.setdefault(key, path)
            sequences.update(canonical(path) + b"\n")
            hits += 1
        productive += bool(hits)
        state.move(i, source)
    need(state.histogram() == initial_hist, "census mutated initial histogram")
    return dict(single_capacity_improvements=len(single_candidates), single_legal_improvements=0,
                legal_neutral_prefixes=len(prefixes), productive_neutral_prefixes=productive,
                neutral_classes=[dict(free_source=x, width=w, free_destination=y, count=n)
                                 for (x, w, y), n in sorted(neutral_classes.items())],
                improving_sequences=sum(profile_counts.values()), sequence_sha256=sequences.hexdigest(),
                neutral_prefix_sha256=hashlib.sha256(canonical(prefixes)).hexdigest(),
                distinct_final_allocations=len(final_allocations), sequences=paths,
                profiles=[dict(delta=dict(key), count=n, witness=witnesses[key])
                          for key, n in sorted(profile_counts.items())])


def materialize(state, source_roles):
    """Compact surviving slices in offset order, then append incoming roles."""
    result = [dict(z) for z in source_roles]
    for b, members in enumerate(state.members):
        owner, child, port = state.bins[b]["key"]
        offset = 0
        for i in sorted(members, key=lambda j: (state.roles[j]["bin"] != b,
                                                source_roles[j]["offset"], j)):
            result[i].update(owner_replica=owner, child=child, port=port, offset=offset,
                             family=state.bins[b]["family"], copy=owner * 112 + port)
            offset += result[i]["width"]
    return result


def run():
    state, baseline, context = load_problem()
    initial = canonical(materialize(state, context[4]))
    need(initial == canonical(context[4]), "baseline materialization changed source roles")
    result = census(state)
    need(canonical(materialize(state, context[4])) == initial, "census changed allocation")
    auditor, geo, widths, local, source_roles, plan = context
    checks = []
    all_owner_checks = hashlib.sha256()
    witness_profiles = {tuple(p["witness"]): p for p in result["profiles"]}
    for path in result["sequences"]:
        i, dest, j, end = path
        first_source = state.move(i, dest)
        need(state.histogram() == Counter(baseline["idle"]), "non-neutral prefix")
        middle = auditor.audit(geo, widths, local, materialize(state, source_roles), plan,
                               state.histogram(), 16)
        second_source = state.move(j, end)
        final = auditor.audit(geo, widths, local, materialize(state, source_roles), plan,
                              state.histogram(), 16)
        check = dict(path=path, intermediate=middle, final=final)
        all_owner_checks.update(canonical(check) + b"\n")
        if tuple(path) in witness_profiles:
            want = Counter(baseline["idle"])
            want.update(witness_profiles[tuple(path)]["delta"])
            need(+want == state.histogram(), "witness delta")
            checks.append(check)
        state.move(j, second_source)
        state.move(i, first_source)
    need(canonical(materialize(state, source_roles)) == initial, "witness checks changed allocation")
    return dict(status="PASS_PR1094_NEUTRAL_PAIR_CENSUS", bins=len(state.bins), baseline=baseline,
                census=result, witness_owner_checks=checks,
                all_paths_owner_check=dict(sequences=len(result["sequences"]),
                                           full_map_checks=2 * len(result["sequences"]),
                                           sha256=all_owner_checks.hexdigest()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a fresh proposed receipt instead of comparing")
    args = parser.parse_args()
    result = run()
    if args.write:
        with args.write.open("x") as f:
            f.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(result) == canonical(read(HERE / "RESULT.json")), "receipt differs from fresh census")
    c = result["census"]
    print(result["status"], "neutral=" + str(c["legal_neutral_prefixes"]),
          "sequences=" + str(c["improving_sequences"]), "profiles=" + str(len(c["profiles"])))


if __name__ == "__main__":
    main()
