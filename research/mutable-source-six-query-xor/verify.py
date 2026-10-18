#!/usr/bin/env python3
"""Exact five-source six-query XOR endpoint; stdlib; read-only default.

Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def operators(n):
    edges = list(itertools.combinations(range(n), 2))
    return [(s, t, 1 << edges.index(tuple(sorted((s, t)))))
            for s in range(n) for t in range(n) if s != t]


def component_count(n, graph):
    labels = list(range(n))
    for k, (s, t) in enumerate(itertools.combinations(range(n), 2)):
        if graph >> k & 1:
            a, b = labels[s], labels[t]
            labels = [a if c == b else c for c in labels]
    return len(set(labels))


def shear(rows, s, t):
    out = list(rows)
    out[t] ^= out[s]
    return tuple(out)


def half_layers(n, depth):
    """All (exact matrix, all-used-edge graph) states at each depth."""
    layers = [{tuple(1 << j for j in range(n)): {0}}]
    for _ in range(depth):
        nxt = {}
        for rows, graphs in layers[-1].items():
            for s, t, bit in operators(n):
                nxt.setdefault(shear(rows, s, t), set()).update(g | bit for g in graphs)
        layers.append(nxt)
    return layers


def meet_census(n=5, bound=7):
    """u reverse(v) restores iff M(u)=M(v); graphs combine by union."""
    layers = half_layers(n, (bound + 1) // 2)
    by_length = []
    for length in range(bound + 1):
        a, b = length // 2, (length + 1) // 2
        unions = set()
        for rows, left in layers[a].items():
            unions.update(x | y for x in left for y in layers[b].get(rows, ()))
        by_length.append({
            "length": length, "identity_graphs": len(unions),
            "connected_identity_graphs": sum(component_count(n, g) == 1 for g in unions),
            "minimum_components": min((component_count(n, g) for g in unions), default=None),
            "graphs_sha256": hashlib.sha256(json.dumps(sorted(unions), separators=(",", ":")).encode()).hexdigest(),
        })
    digest_rows = [[list(rows), sorted(gs)] for rows, gs in sorted(layers[-1].items())]
    return {
        "n": n, "excluded_xor_lengths": [0, bound],
        "raw_half_word_counts": [(n*(n-1))**k for k in range(len(layers))],
        "half_distinct_matrices": [len(layer) for layer in layers],
        "half_matrix_graph_states": [sum(len(gs) for gs in layer.values()) for layer in layers],
        "last_layer_sha256": hashlib.sha256(json.dumps(digest_rows, separators=(",", ":")).encode()).hexdigest(),
        "by_length": by_length,
    }


def witness():
    """Reconstruct the credited predecessor's minimum-query construction."""
    prefixes = [0, 1, 3, 7, 15, 31]
    slots = {}
    for flags in range(64):
        if flags.bit_count() % 2:
            continue
        chosen = [k for k in range(6) if flags >> k & 1]
        mask = 0
        for k in chosen:
            mask ^= prefixes[k]
        require(mask not in slots, "nonunique even-subset mask")
        slots[mask] = chosen
    word = []
    for boundary in range(6):
        for mask in range(1, 32):
            if boundary in slots[mask]:
                word.append(["R", mask])
        if boundary < 5:
            word.append(["Q", boundary])
    word += [["X", s, 0] for s in range(1, 5)]
    word += [["Q", 0]]
    word += [["X", s, 0] for s in range(4, 0, -1)]
    return word, slots


def root_replay(word):
    """Free noncommutative operator words on independent incoming rows."""
    names = [f"x{j}" for j in range(5)] + ["z"] + [f"y{m}" for m in range(1, 32)]
    state = {name: {(name, ())} for name in names}
    for event in word:
        if event[0] == "X":
            _, s, t = event
            state[f"x{t}"].symmetric_difference_update(state[f"x{s}"])
        elif event[0] == "Q":
            state["z"].symmetric_difference_update((v, ("B",)+ops) for v, ops in state[f"x{event[1]}"])
        elif event[0] == "R":
            m = event[1]
            state[f"y{m}"].symmetric_difference_update((v, (f"A{m}",)+ops) for v, ops in state["z"])
        else:
            raise ValueError("invalid event")
    return state


def expected_map():
    state = {f"x{j}": {(f"x{j}", ())} for j in range(5)}
    state["z"] = {("z", ())}
    for m in range(1, 32):
        state[f"y{m}"] = {(f"y{m}", ())} | {(f"x{j}", (f"A{m}", "B")) for j in range(5) if m >> j & 1}
    return state


def source_check():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for rec in sources["files"]:
        if rec["usage"] == "input":
            require(hashlib.sha256((ROOT / rec["path"]).read_bytes()).hexdigest() == rec["sha256"], "source bytes mismatch: "+rec["path"])


def calculate():
    source_check()
    census = meet_census()
    require(all(r["connected_identity_graphs"] == 0 for r in census["by_length"]), "short connected restored word found")
    word, slots = witness()
    counts = {k: sum(e[0] == k for e in word) for k in ("Q", "R", "X")}
    require(counts == {"Q": 6, "R": 96, "X": 8}, "wrong endpoint bill")
    require(root_replay(word) == expected_map(), "dirty root map mismatch")
    require(root_replay(list(reversed(word))) == expected_map(), "inverse root map mismatch")
    source = json.loads((ROOT / "research/mutable-source-minimum-queries/CERTIFICATE.json").read_text())
    require(source["prefixes"] == [0, 1, 3, 7, 15, 31, 0], "predecessor prefix drift")
    require(source["readout_slots"] == {str(m): slots[m] for m in range(1, 32)}, "predecessor readout drift")
    rows, graph = (1, 2, 4, 8, 16), 0
    for event in word:
        if event[0] == "X":
            _, s, t = event
            rows = shear(rows, s, t)
            graph |= next(b for a, c, b in operators(5) if a == s and c == t)
    require(rows == (1, 2, 4, 8, 16) and component_count(5, graph) == 1, "eight-X positive control failed")
    broken = root_replay(word[:-1])
    require(all(broken[f"y{m}"] == expected_map()[f"y{m}"] for m in range(1, 32)), "control not target-invisible")
    require(broken != expected_map(), "missing source uncompute not detected")
    require(root_replay(word[:1]+word[2:]) != expected_map(), "missing readout not detected")
    require(root_replay([e for e in word if e[0] != "X"]) != expected_map(), "unpaid source mutation not detected")
    rows = (1, 2, 4, 8, 16)
    for s in range(1, 5):
        rows = shear(rows, s, 0)
    require(rows != (1, 2, 4, 8, 16), "nonrestored connected control")
    require(shear(shear((1,2,4,8,16), 1, 0), 1, 0) == (1,2,4,8,16), "two-X identity control")
    require(component_count(5, 1) > 1, "disconnected identity control")
    return {"schema_version": 1, "census": census, "endpoint": counts,
            "complete_tariff": "6*b + 96*a + 8*x", "abstract_tariff_38_2_2": 436,
            "positive_control": "connected restored eight-X word",
            "negative_controls": ["source-uncompute omitted with correct outputs", "readout omitted", "source-XORs omitted", "connected but nonrestored four-X word", "restored but disconnected two-X word"],
            "root_word": word}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    result = calculate()
    if args.write_receipt:
        args.write_receipt.write_text(json.dumps(result, indent=2)+"\n")
    else:
        require(json.loads((HERE / "RESULT.json").read_text()) == result, "receipt mismatch")
    print("PASS_MUTABLE_SOURCE_SIX_QUERY_XOR min_x=8 Q=6 R=96 tariff=436 no_new_kappa")


if __name__ == "__main__":
    main()
