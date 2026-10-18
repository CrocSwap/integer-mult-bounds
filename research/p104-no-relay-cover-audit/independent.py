#!/usr/bin/env python3
"""Second certificate replay: explicit sets and complete recursive chains.

Does not import verify.py, generate.py or any predecessor executable. This
checks the cover certificate by a different representation and enumeration,
not the scalar/native channel or all of the primary parser's frame contracts.
Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(ok, message):
    if not ok:
        raise SystemExit("FAIL_INDEPENDENT: " + message)


def subspace(generators):
    result = {0}
    for g in generators:
        result.update([x ^ g for x in tuple(result)])
    return frozenset(result)


def all_chains(start, larger, port_sets):
    answers = set()
    visited = set()

    def walk(frame, ports):
        key = (frame, ports)
        if key in visited:
            return
        visited.add(key)
        answers.add(ports)
        for nxt in port_sets:
            if (frame < nxt if larger else nxt < frame):
                walk(nxt, ports | port_sets[nxt])

    walk(start, port_sets[start])
    return answers


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    word_path = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
    pin = next(p for p in pins["files"] if p["path"] == word_path)
    raw = (ROOT / word_path).read_bytes()
    need(sha256(raw).hexdigest() == pin["sha256"], "word source pin")
    word = json.loads(raw)
    paths = {r: [subspace(f)] for r, f in word["initial_frames"].items()
             if r.startswith(("X", "Y"))}
    for event in word["program"]:
        if event[0] == "transport" and event[1] in paths:
            need(paths[event[1]][-1] == subspace(event[2]), "data transport entry")
            frame = subspace(event[3])
            need(paths[event[1]][-1] < frame, "data path is not monotone")
            paths[event[1]].append(frame)
    source_nodes, target_nodes = defaultdict(set), defaultdict(set)
    labels = []
    for i in range(104):
        labels.append(next(x for x in paths[f"X{i}"][0] if x))
        for f in paths[f"X{i}"]:
            source_nodes[f].add(i)
        for f in paths[f"Y{i}"]:
            if len(f) > 1:
                target_nodes[f].add(i)
    source_nodes = {f: frozenset(p) for f, p in source_nodes.items()}
    target_nodes = {f: frozenset(p) for f, p in target_nodes.items()}
    sc = {f: all_chains(f, False, source_nodes) for f in source_nodes}
    tc = {f: all_chains(f, True, target_nodes) for f in target_nodes}
    rectangles = set()
    for f, aa in sc.items():
        for g, bb in tc.items():
            if f <= g:
                rectangles.update(frozenset((t, s) for s in a for t in b)
                                  for a in aa for b in bb)
    support = {(t, s) for t in range(104) for s in range(104)
               if labels[s] in paths[f"Y{t}"][-1]}
    need(set().union(*rectangles) == support, "support coverage")
    nonsingle = set().union(*(r for r in rectangles if len(r) > 1))
    forced = support - nonsingle
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    extra = [tuple(p) for p in certificate["extra_packing"]]
    need(len(set(extra)) == len(extra) and not set(extra) & forced, "dual duplicate")
    packing = forced | set(extra)
    need(packing <= support, "dual outside support")
    need(all(len(r & packing) <= 1 for r in rectangles), "dual capacity")
    chosen = [frozenset((t, s) for s in x["sources"] for t in x["targets"])
              for x in certificate["extra_cover"]]
    need(len(set(chosen)) == len(chosen), "primal duplicate")
    need(all(r in rectangles for r in chosen), "primal rectangle unavailable")
    need(forced | set().union(*chosen) == support, "primal coverage")
    need(len(packing) == len(forced) + len(chosen) == certificate["optimum"] == 4580,
         "primal/dual objective")
    # Drop-one primal and add-one dual controls on the reconstructed family.
    need(forced | set().union(*chosen[:-1]) != support, "missing cover control")
    r = next(r for r in rectangles if len(r) > 1 and r & packing)
    bad = packing | {next(e for e in r if e not in packing)}
    need(any(len(r & bad) > 1 for r in rectangles), "dual capacity control")
    print(f"PASS_INDEPENDENT_P104_COVER pairs={len(support)} all_chain_rectangles={len(rectangles)} forced={len(forced)} primal=4580 dual=4580 controls=2")


if __name__ == "__main__":
    main()
