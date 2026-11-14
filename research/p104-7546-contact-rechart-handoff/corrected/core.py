#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Current-word adaptation of the #7122/#7124 boundary rechart contract.

The contact graph follows 1337isnot1337's fresh-helper-boundary discovery.
Normalized-coordinate return and causal reconstruction follow Rohan Arun.
Prepared for Clear1nsight with substantial OpenAI Pro/Codex assistance.
Floating discovery is not a supplier, physical certificate, or kappa claim.
"""
from collections import Counter
from copy import deepcopy
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def span(basis):
    values = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in values, "chart basis")
        values |= {v ^ x for x in tuple(values)}
    return frozenset(values)


def main_roles(word):
    h = word["hosted"]
    return set(word["live"]) | {r + 112 for r in word["live"]} | set(h["X2"]) | set(h["Y2"])


def ascend(spaces, a, b):
    return a == b or spaces[a] < spaces[b]


def native_targets(word, spaces):
    result = Counter()
    for r in range(word["public"]):
        if r in main_roles(word):
            continue
        a, b = word["initial"][r], word["final"][r]
        need(spaces[a] < spaces[b], "strict productive helper target")
        result[len(word["frames"][b]) - len(word["frames"][a])] += 1
    return result


def inventory(word, spaces):
    n, m = word["public"], word["owned_fields"]
    current = list(word["initial"]) + [None] * m
    paid, owned_moves, lives, clear, copies = Counter(), [], {}, [], []
    last_write, peak = {}, 0
    for i, e in enumerate(word["program"]):
        op, r = e[:2]
        need(type(r) is int and 0 <= r < n + m, "role range")
        if op == "INIT":
            need(r >= n and current[r] is None and r not in lives, "INIT")
            current[r] = e[2]
            lives[r] = i
            peak = max(peak, len(lives))
            last_write[r] = ("INIT", i)
        elif op == "CLEAR":
            need(r in lives and current[r] == e[2], "CLEAR")
            clear.append({"role": r, "init": lives.pop(r), "clear": i, "frame": e[2]})
            current[r] = None
            last_write[r] = ("CLEAR", i)
        elif op == "MOVE":
            _, _, a, b, owned = e
            need(type(owned) is bool and owned == (r >= n), "MOVE ownership")
            need(current[r] == a and (r < n or r in lives), "MOVE source")
            need(spaces[a] < spaces[b] or (owned and spaces[b] < spaces[a]), "MOVE nesting")
            paid[abs(len(word["frames"][b]) - len(word["frames"][a]))] += 1
            if owned:
                owned_moves.append(e)
            current[r] = b
        else:
            need(op in ("ADD", "COPY", "SCALE"), "scalar opcode")
            s = r if op == "SCALE" else e[2]
            need(type(s) is int and 0 <= s < n + m, "source range")
            need(current[r] is not None and current[r] == current[s] == e[-1], "scalar coframe")
            need((r == s) == (op == "SCALE"), "scalar distinctness")
            if op == "COPY":
                need(r in lives and last_write[r][0] == "INIT", "COPY guard")
                copies.append({"clock": i, "destination": r, "zero_from_INIT": last_write[r][1]})
            last_write[r] = (op, i)
    need(not lives and current == word["final"] + [None] * m, "final charts/lifecycles")
    return {"paid": paid, "targets": native_targets(word, spaces), "owned_moves": owned_moves,
            "lifetimes": clear, "peak": peak, "copies": copies}


def build_graph(word, protected):
    """Retain separate chronological contacts and immutable timed MOVE anchors."""
    n = word["public"]
    mains = main_roles(word)
    nodes, paths, scalar_nodes, initial, final = [], [[] for _ in range(n)], {}, [], []

    def node(kind, before, after, roles, clock, entry=False, exit=False):
        index = len(nodes)
        nodes.append(dict(kind=kind, before=before, after=after, roles=roles, clock=clock,
                          entry=entry, exit=exit))
        for r in roles:
            paths[r].append(index)
        return index

    for r, f in enumerate(word["initial"]):
        initial.append(node("initial", f, f, [r], -1, r not in mains | protected))
    for i, e in enumerate(word["program"]):
        op, r = e[:2]
        if op == "MOVE" and r < n and r in protected:
            node("anchor", e[2], e[3], [r], i)
        elif op in ("ADD", "COPY", "SCALE"):
            roles = e[1:3] if op != "SCALE" else e[1:2]
            public = [s for s in roles if s < n]
            if public:
                mutable = len(public) == len(roles) and not (set(roles) & protected)
                scalar_nodes[i] = node("scalar", e[-1], e[-1], public, i, mutable, mutable)
    for r, f in enumerate(word["final"]):
        final.append(node("final", f, f, [r], len(word["program"]), False, r not in mains | protected))
    edges = [[a, b, r] for r, path in enumerate(paths) for a, b in zip(path, path[1:])]
    helpers = [r for r in range(n) if r not in mains | protected]
    return dict(nodes=nodes, edges=edges, initial=initial, final=final,
                helpers=helpers, scalar_nodes=scalar_nodes)


def validate_labels(word, graph, labels, mode, protected, spaces):
    need(mode in ("entry", "exit", "baseline"), "mode")
    need(len(labels) == len(graph["nodes"]), "assignment cardinality")
    for i, (node, f) in enumerate(zip(graph["nodes"], labels)):
        need(type(f) is int and 0 <= f < len(spaces), "assignment frame")
        if mode == "baseline" or not node[mode]:
            need(f == node["before"], "pinned contact/boundary/anchor")
        need(not (set(node["roles"]) & protected) or f == node["before"], "protected assignment")
    for a, b, _r in graph["edges"]:
        na, nb = graph["nodes"][a], graph["nodes"][b]
        fa = na["after"] if na["kind"] == "anchor" else labels[a]
        fb = nb["before"] if nb["kind"] == "anchor" else labels[b]
        need(ascend(spaces, fa, fb), "illegal/equal-span-different-ID path edge")
    for r in graph["helpers"]:
        need(spaces[labels[graph["initial"][r]]] < spaces[labels[graph["final"][r]]], "zero helper target")


def reconstruct(word, graph, labels, protected, spaces):
    out = deepcopy(word)
    out["initial"] = [labels[i] for i in graph["initial"]]
    out["final"] = [labels[i] for i in graph["final"]]
    n = word["public"]
    current = list(out["initial"]) + [None] * word["owned_fields"]
    program, bindings = [], []

    def move(r, target, clock):
        old = current[r]
        if old == target:
            return
        need(r < n and r not in protected and old is not None, "forbidden inserted transport")
        need(spaces[old] < spaces[target], "new public transport")
        bindings.append([len(program), clock, "causal_public_move"])
        program.append(["MOVE", r, old, target, False])
        current[r] = target

    for i, e in enumerate(word["program"]):
        op, r = e[:2]
        if op == "MOVE":
            if r >= n or r in protected:
                need(current[r] == e[2], "timed MOVE anchor")
                bindings.append([len(program), i, "retained_anchor"])
                program.append(e.copy())
                current[r] = e[3]
        elif op in ("INIT", "CLEAR"):
            bindings.append([len(program), i, "retained_owned_boundary"])
            program.append(e.copy())
            current[r] = e[2] if op == "INIT" else None
        else:
            f = labels[graph["scalar_nodes"][i]] if i in graph["scalar_nodes"] else e[-1]
            for s in (e[1:3] if op != "SCALE" else e[1:2]):
                if s >= n or s in protected:
                    need(current[s] == f, "fixed owned/protected coframe")
                else:
                    move(s, f, i)
            bindings.append([len(program), i, "scalar"])
            program.append([*e[:-1], f])
    for r, target in enumerate(out["final"]):
        if r in protected:
            need(current[r] == target, "protected final anchor")
        else:
            move(r, target, len(word["program"]))
    out["program"] = program
    return out, bindings


def validate_reconstruction(old, new, bindings, protected, spaces):
    n = old["public"]
    fixed = [r for r in range(n) if r in main_roles(old) | protected]
    need(all(old[k][r] == new[k][r] for k in ("initial", "final") for r in fixed), "fixed main/protected boundary")
    need({k: v for k, v in old.items() if k not in ("initial", "final", "program")} ==
         {k: v for k, v in new.items() if k not in ("initial", "final", "program")}, "fixed source metadata")
    scalars = lambda w: [e[:-1] if e[0] in ("ADD", "COPY", "SCALE") else e
                         for e in w["program"] if e[0] != "MOVE"]
    need(scalars(old) == scalars(new), "complete normalized scalar chronology")
    by_new = {i: (clock, kind) for i, clock, kind in bindings}
    need(set(by_new) == set(range(len(new["program"]))), "complete source-clock bindings")
    need([i for i, _c, _k in bindings] == list(range(len(new["program"]))), "ordered new bindings")
    clocks = [c for _i, c, _k in bindings]
    need(clocks == sorted(clocks) and all(0 <= c <= len(old["program"]) for c in clocks), "monotone source clocks")
    old_scalars = [i for i, e in enumerate(old["program"]) if e[0] in ("ADD", "COPY", "SCALE")]
    need([c for _i, c, k in bindings if k == "scalar"] == old_scalars, "each original scalar bound once")
    anchors = [(i, e) for i, e in enumerate(old["program"])
               if (e[0] == "MOVE" and (e[1] >= n or e[1] in protected)) or e[0] in ("INIT", "CLEAR")]
    actual = [(clock, new["program"][i]) for i, clock, kind in bindings if kind in ("retained_anchor", "retained_owned_boundary")]
    need(actual == anchors, "exact timed protected/owned anchor subsequence")
    for i, clock, kind in bindings:
        if kind != "scalar":
            continue
        e, before = new["program"][i], old["program"][clock]
        need(e[:-1] == before[:-1] and e[0] in ("ADD", "COPY", "SCALE"), "scalar clock-to-event binding")
        roles = before[1:3] if before[0] != "SCALE" else before[1:2]
        if any(r >= n or r in protected for r in roles):
            need(e == before, "owned/protected scalar contact")
    before, after = inventory(old, spaces), inventory(new, spaces)
    need(before["owned_moves"] == after["owned_moves"] and before["peak"] == after["peak"], "owned paths/stock")
    need([(e["role"], e["frame"]) for e in before["lifetimes"]] ==
         [(e["role"], e["frame"]) for e in after["lifetimes"]], "all erasure-channel correspondences")
    return after


def narrow_forced_spaces(graph, spaces):
    """Reuse the old full-contact DAG bounds, retaining old IDs at singleton corridors.

    This is a declared conservative nomination restriction, not a completeness
    claim over alternative equal-span chart IDs.
    """
    nodes = graph["nodes"]
    predecessors, successors = [[] for _ in nodes], [[] for _ in nodes]
    for a, b, _r in graph["edges"]:
        need(a < b, "chronological contact DAG")
        predecessors[b].append(a)
        successors[a].append(b)

    masks = [sum(1 << x for x in space) for space in spaces]

    def join(a, b):
        if not a & ~b:
            return b
        if not b & ~a:
            return a
        result = a
        pending = b
        while pending:
            bit = pending & -pending
            pending ^= bit
            x = bit.bit_length() - 1
            if not result & bit:
                members = result
                translated = 0
                while members:
                    member = members & -members
                    members ^= member
                    translated |= 1 << (x ^ (member.bit_length() - 1))
                result |= translated
        return result

    report = {}
    for mode in ("entry", "exit"):
        lower, upper = [], [None] * len(nodes)
        for v, node in enumerate(nodes):
            lo = masks[node["after"]] if not node[mode] else 1
            if node[mode]:
                for u in predecessors[v]:
                    lo = join(lo, lower[u])
            need(not lo & ~masks[node["after"]], "source lower corridor")
            lower.append(lo)
        for v in reversed(range(len(nodes))):
            node = nodes[v]
            hi = masks[node["before"]] if not node[mode] else (1 << 512) - 1
            if node[mode]:
                for u in successors[v]:
                    hi = hi & upper[u]
            need(not masks[node["before"]] & ~hi, "source upper corridor")
            upper[v] = hi
        forced = [v for v, node in enumerate(nodes) if node[mode] and lower[v] == upper[v]]
        for v in forced:
            need(lower[v] == masks[nodes[v]["before"]], "forced source chart space")
            nodes[v][mode] = False
        report[mode] = {"forced_to_old_ID": forced,
                        "remaining_mutable": sum(n[mode] for n in nodes)}
    return report


def changes(word, new, bindings):
    n = word["public"]
    initial = [[r, word["initial"][r], new["initial"][r]] for r in range(n) if word["initial"][r] != new["initial"][r]]
    final = [[r, word["final"][r], new["final"][r]] for r in range(n) if word["final"][r] != new["final"][r]]
    scalar = [[clock, word["program"][clock][-1], new["program"][i][-1]]
              for i, clock, kind in bindings if kind == "scalar" and word["program"][clock][-1] != new["program"][i][-1]]
    return dict(initial=initial, final=final, scalar=scalar)
