#!/usr/bin/env python3
"""Check forward level drops and their complete paid profiles.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The enumeration follows Mark / Matarener's PR5426. The word is from
ahrazzle / PR5350, with Cinna Davis's PR4692 compression methods.
The exact-cost question follows Nick Petalas's released handoff.
"""
import argparse
from collections import Counter, deque
from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check_sources():
    for row in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if row["usage"] == "input":
            require(sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "Source mismatch: " + row["path"])


def dependency_pairs(w, contacts):
    positions = {w.contacts[k]["op"]: i for i, k in enumerate(contacts)}
    pairs = set()
    for source, i in positions.items():
        todo, seen = [source], {source}
        while todo:
            node = todo.pop()
            for following in w.succ[node]:
                if following not in seen:
                    seen.add(following)
                    todo.append(following)
                    if following in positions:
                        pairs.add((i, positions[following]))
    return sorted(pairs)


@contextmanager
def move(w, field, removed, contacts, choices):
    touched = {field}
    for k in contacts:
        touched.update((w.contacts[k]["d"], w.contacts[k]["s"]))
    chains = {f: list(w.chain[f]) for f in touched}
    sets = {f: set(w.cset[f]) for f in touched}
    saved = {k: dict(w.contacts[k]) for k in contacts}
    old_at = {key: set(value) for key, value in w.at.items() if key[0] in touched}
    old_frames = {key: value for key, value in w.frame_of.items() if key[0] in touched}
    try:
        for k, (frame, partner) in zip(contacts, choices):
            c = w.contacts[k]
            if partner is not None and frame not in w.cset[partner]:
                w.chain[partner].append(frame)
                w.chain[partner].sort(key=w.dim)
                w.cset[partner].add(frame)
                w.frame_of[partner, frame] = frame
            w.at[c["d"], c["kd"]].discard(k)
            w.at[c["s"], c["ks"]].discard(k)
            c.update(F=frame, kd=frame, ks=frame)
            w.at[c["d"], frame].add(k)
            w.at[c["s"], frame].add(k)
        w.chain[field].remove(removed)
        w.cset[field].remove(removed)
        yield touched
    finally:
        for f in touched:
            w.chain[f], w.cset[f] = chains[f], sets[f]
        for k, c in saved.items():
            w.contacts[k] = c
        for key in [key for key in w.at if key[0] in touched]:
            del w.at[key]
        w.at.update(old_at)
        for key in [key for key in w.frame_of if key[0] in touched]:
            del w.frame_of[key]
        w.frame_of.update(old_frames)


class StaticOrder:
    """Use a full Kahn scan. Do not retain a dynamic topological order."""

    def __init__(self, w):
        self.w = w
        self.ids = {}
        self.out = [set() for _ in range(w.n)]
        self.indegree = [0] * w.n
        self.base = [self.field_edges(f) for f in range(w.nf)]
        edges = {(p, node) for node, predecessors in enumerate(w.pred) for p in predecessors}
        for field in self.base:
            edges.update(field)
        for source, target in edges:
            self.out[source].add(target)
            self.indegree[target] += 1

    def node(self, field, frame, side):
        key = (field, frame, side)
        if key not in self.ids:
            self.ids[key] = len(self.out)
            self.out.append(set())
            self.indegree.append(0)
        return self.ids[key]

    def field_edges(self, field):
        w = self.w
        chain = w.chain[field]
        active = [(pos, frame) for pos, frame in enumerate(chain) if w.at.get((field, frame))]
        edges, previous = set(), None
        for pos, frame in active:
            entry, leave = (self.node(field, frame, side) for side in (0, 1))
            if previous is not None:
                edges.add((previous, entry))
            previous = leave
            for k in w.at[field, frame]:
                operation = w.contacts[k]["op"]
                edges.update(((entry, operation), (operation, leave)))
            for operation, owner, visit, before, after in w.warp_ops:
                if owner != field:
                    continue
                if field in w.pinned:
                    edges.add((leave, operation) if frame[1] <= visit else (operation, entry))
                elif pos <= chain.index(before):
                    edges.add((leave, operation))
                elif pos >= chain.index(after):
                    edges.add((operation, entry))
        return edges

    def acyclic(self, touched=()):
        old, new = set(), set()
        for field in touched:
            old.update(self.base[field])
            new.update(self.field_edges(field))
        removed, added = old - new, new - old
        out_added, indegree = {}, list(self.indegree)
        for source, target in removed:
            indegree[target] -= 1
        for source, target in added:
            indegree[target] += 1
            out_added.setdefault(source, []).append(target)
        ready = deque(i for i, value in enumerate(indegree) if value == 0)
        visited = 0
        while ready:
            source = ready.popleft()
            visited += 1
            for target in self.out[source]:
                if (source, target) in removed:
                    continue
                indegree[target] -= 1
                if indegree[target] == 0:
                    ready.append(target)
            for target in out_added.get(source, ()):
                indegree[target] -= 1
                if indegree[target] == 0:
                    ready.append(target)
        return visited == len(indegree)


def paid(w):
    counts = Counter()
    for field, chain in enumerate(w.chain):
        for before, after in zip(chain, chain[1:]):
            rank = w.fdim(field, after) - w.fdim(field, before)
            if rank > 0:
                counts[rank] += 1
    for contact in w.contacts:
        if contact["kind"] == "Cread":
            counts[w.dim(contact["F"])] += 1
    return dict(sorted(counts.items()))


def difference(before, after):
    return {str(rank): after.get(rank, 0) - before.get(rank, 0)
            for rank in sorted(before.keys() | after.keys())
            if after.get(rank, 0) != before.get(rank, 0)}


def enumerate_moves(model, word, arithmetic, pin_centre=True):
    w = model["Word"](word, arithmetic, pin_centre=pin_centre)
    dynamic = model["LevelGraph"](w)
    dynamic.index_owners()
    static = StaticOrder(w)
    require(static.acyclic(), "The source graph must be acyclic")
    baseline = paid(w)
    if pin_centre:
        require(baseline == {int(k): v for k, v in arithmetic["local_paid"].items()},
                "Complete source invoice")
    counts, feasible = Counter(), []
    for field in range(w.nf):
        if field in w.pinned:
            continue
        for removed in list(w.chain[field]):
            if removed in (w.S[field], w.T[field]) or removed in w.warp_frames[field]:
                continue
            contacts = sorted(w.at.get((field, removed), ()))
            if not contacts:
                continue
            counts["levels"] += 1
            options = [model["options_for"](w, k, field, removed) for k in contacts]
            if any(not choices for choices in options):
                counts["no_options"] += 1
                continue
            pairs = dependency_pairs(w, contacts)
            positions = {frame: index for index, frame in enumerate(w.chain[field])}
            found = False
            for choices in product(*options):
                counts["plans"] += 1
                if any(positions[choices[a][0]] > positions[choices[b][0]] for a, b in pairs):
                    counts["dependency_rejections"] += 1
                    continue
                with move(w, field, removed, contacts, choices) as touched:
                    exact = static.acyclic(touched)
                    require(exact == dynamic.try_state(touched), "Static/dynamic graph disagreement")
                    counts["independent_graph_checks"] += 1
                    if exact:
                        found = True
                        counts["feasible_plans"] += 1
                        feasible.append({"field": field, "removed_frame": removed,
                                         "contacts": contacts, "choices": choices,
                                         "paid_delta": difference(baseline, paid(w))})
                    else:
                        counts["cycle_rejections"] += 1
            counts["feasible_levels" if found else "cyclic_levels"] += 1
            if counts["levels"] % 500 == 0:
                print("Checked", counts["levels"], "levels", flush=True)
    require(counts["plans"] == counts["dependency_rejections"] + counts["cycle_rejections"]
            + counts["feasible_plans"], "Complete plan partition")
    require(paid(w) == baseline, "Invoice restored after enumeration")
    return {"counts": dict(sorted(counts.items())), "baseline_paid": baseline,
            "feasible": feasible, "operations": w.n, "contacts": len(w.contacts)}


def check_claim(result):
    expected = {"1": -1, "4": -1, "5": 1, "8": -1, "9": 1}
    require(len(result["feasible"]) == 8, "Eight feasible plans")
    require(all(row["paid_delta"] == expected for row in result["feasible"]), "Complete paid delta")


def controls(model, word, arithmetic, result):
    check_claim(result)
    require(100 ** 100 > 9 * 97 ** 100, "Rational power envelope")
    require(97 * (9 + 5) - 100 * (8 + 4 + 1) == 58, "Tariff lower bound 29/50")
    for false_delta in ({"1": 1, "7": 1, "8": -2, "9": 1},
                        {"1": -1, "4": -1, "5": 1}):
        altered = deepcopy(result)
        altered["feasible"][0]["paid_delta"] = false_delta
        try:
            check_claim(altered)
        except ValueError:
            pass
        else:
            raise ValueError("An incorrect paid delta was accepted")
    corrupted = deepcopy(word)
    for event in corrupted["programs"]["forward"]:
        if event[0] == "climb":
            event[5] += 1
            break
    try:
        model["Word"](corrupted, arithmetic)
    except SystemExit:
        pass
    else:
        raise ValueError("A false climb rank was accepted")
    w = model["Word"](word, arithmetic)
    graph = StaticOrder(w)
    source, target = next((u, v) for u, row in enumerate(graph.out) for v in row)
    graph.out[target].add(source)
    graph.indegree[source] += 1
    require(not graph.acyclic(), "Independent cycle rejection")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    check_sources()
    constructor = runpy.run_path(str(ROOT / "research/cao-trace-retiming-20261023/construct.py"))
    _, word, stages = constructor["construct"]()
    require(digest(word) == "7eb2f5c6e3291be8bc266f76076d49565e0687eb56311facede72b368ed48773",
            "Compressed word identity")
    arithmetic = json.loads((ROOT / "research/kappa-round3-warp-20261022/ARITHMETIC.json").read_text())
    model = runpy.run_path(str(ROOT / "research/fragmentation-reorder-rigidity/verify.py"))
    result = enumerate_moves(model, word, arithmetic)
    controls(model, word, arithmetic, result)
    relaxed = enumerate_moves(model, word, arithmetic, pin_centre=False)
    require(relaxed["counts"]["feasible_plans"] == 51, "The centre relaxation must unlock moves")
    require({tuple(sorted(row["paid_delta"].items())) for row in relaxed["feasible"]}
            == {(("1", -1), ("3", -1), ("4", 1)), (("1", -1), ("4", -1), ("5", 1))},
            "Relaxed invoice controls")
    receipt = {"schema_version": 1, "word_sha256": digest(word), "compression": stages,
               "exact": result, "relaxed_centre": relaxed,
               "tariff_interval": ["99/100", "1"], "tariff_lower_bound": "29/50"}
    receipt = json.loads(json.dumps(receipt))
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        require(receipt == json.loads((HERE / "RESULT.json").read_text()), "Stored receipt mismatch")
    print("PASS_COMPRESSED_WORD_DROP_INVOICE", json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
