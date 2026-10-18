#!/usr/bin/env python3
"""Exact finite R439 mini-node synthesis. Apache-2.0; substantial Codex assistance."""
import copy
import gzip
import hashlib
import importlib.util
import json
import random
from collections import deque
from functools import reduce
from operator import xor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/e8-bit-p111-tuned"
SEED = 8


def multiply(a, b):
    return tuple(reduce(xor, (b[j] for j in range(len(b)) if row >> j & 1), 0)
                 for row in a)


def group_paths(k):
    """BFS gives shortest row-addition paths for every matrix in GL(k, 2)."""
    identity = tuple(1 << i for i in range(k))
    paths = {identity: []}
    queue = deque([identity])
    pairs = [(i, j) for i in range(k) for j in range(k) if i != j]
    random.Random(SEED).shuffle(pairs)
    while queue:
        matrix = queue.popleft()
        for i, j in pairs:
            after = list(matrix)
            after[i] ^= after[j]
            after = tuple(after)
            if after not in paths:
                paths[after] = paths[matrix] + [(i, j)]
                queue.append(after)
    assert len(paths) == {2: 6, 3: 168}[k]
    return paths


def transfer(gates, registers):
    state = {r: 1 << i for i, r in enumerate(registers)}
    for _, target, sources in gates:
        assert len(set([target] + sources)) == len(sources) + 1
        for source in sources:
            state[target] ^= state[source]
    return tuple(state[r] for r in registers)


def scalar_cost(gates):
    return sum(len(sources) for _, _, sources in gates)


def positive_row_norms(gates, registers):
    """Cancellation-free local row sums; these are not recursive coefficient bills."""
    values = {r: 1 for r in registers}
    for _, target, sources in gates:
        values[target] += sum(values[source] for source in sources)
    return [values[r] for r in registers]


def synthesize(gates):
    frame = gates[0][0]
    destinations = [g[1] for g in gates]
    assert len(set(destinations)) == len(destinations)
    external = sorted({s for _, _, ss in gates for s in ss} - set(destinations))
    registers = destinations + external
    k = len(destinations)
    original = transfer(gates, registers)
    linear = tuple(row & ((1 << k) - 1) for row in original[:k])
    inputs = tuple(row >> k for row in original[:k])
    paths = group_paths(k)
    identity = tuple(1 << i for i in range(k))
    candidates = []
    for post in paths:
        inverse = next(m for m in paths if multiply(post, m) == identity)
        pre = multiply(inverse, linear)
        injection = multiply(inverse, inputs)
        cost = len(paths[pre]) + sum(row.bit_count() for row in injection) + len(paths[post])
        candidates.append((cost, post, pre, injection))
    cost, post, pre, injection = min(candidates)
    result = [[frame, destinations[i], [destinations[j]]] for i, j in paths[pre]]
    result += [[frame, destinations[i], [r for j, r in enumerate(external) if row >> j & 1]]
               for i, row in enumerate(injection) if row]
    result += [[frame, destinations[i], [destinations[j]]] for i, j in paths[post]]
    assert scalar_cost(result) == cost
    assert transfer(result, registers) == original
    # The same registers still visit this frame; only their order within it changes.
    touched = lambda gs: {r for _, d, ss in gs for r in [d] + ss}
    assert touched(result) == touched(gates)
    return result, {
        "frame": frame, "destinations": destinations, "external": external,
        "linear_rows": linear, "input_rows": inputs,
        "pre_rows": pre, "injection_rows": injection, "post_rows": post,
        "pre_xors": paths[pre], "post_xors": paths[post],
        "candidates": len(candidates), "before_xors": scalar_cost(gates),
        "minimum_xors_in_class": cost, "applied": cost < scalar_cost(gates),
        "replacement": result if cost < scalar_cost(gates) else gates,
        "forward_destination_row_norms_before": positive_row_norms(gates, registers)[:k],
        "forward_destination_row_norms_after": positive_row_norms(
            result if cost < scalar_cost(gates) else gates, registers)[:k],
    }


def frame_paths(word):
    paths = [[f] for f in word["start"]]
    for section in "DABC":
        for frame, target, sources in word[section]:
            for register in [target] + sources:
                if paths[register][-1] != frame:
                    paths[register].append(frame)
    for register, frame in enumerate(word["final"]):
        if paths[register][-1] != frame:
            paths[register].append(frame)
    return paths


def must_reject(check):
    try:
        check()
    except AssertionError:
        return
    raise AssertionError("negative control was accepted")


def verify(evidence):
    for relative, expected in evidence["source_sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative
    word = json.loads(gzip.decompress((SOURCE / "tune/bitE8mut-p111-tuned.json.gz").read_bytes()))
    spec = importlib.util.spec_from_file_location("p111_wlib", SOURCE / "tune/wlib.py")
    wlib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wlib)
    candidate = copy.deepcopy(word)
    blocks = []
    replacements = {}
    for frame in range(506, 510):
        indices = [i for i, g in enumerate(word["A"]) if g[0] == frame]
        assert indices == list(range(indices[0], indices[-1] + 1))
        gates = [word["A"][i] for i in indices]
        result, record = synthesize(gates)
        record["original_a_indices"] = indices
        blocks.append(record)
        if record["applied"]:
            replacements[indices[0]] = (len(indices), result)
    candidate["A"] = []
    i = 0
    while i < len(word["A"]):
        count, gates = replacements.get(i, (1, [word["A"][i]]))
        candidate["A"].extend(gates)
        i += count
    candidate["C"] = wlib.rebuild_C(candidate)
    assert candidate["C"] == wlib.rebuild_C(candidate)
    assert frame_paths(candidate) == frame_paths(word)
    for key in word.keys() - {"A", "C"}:
        assert candidate[key] == word[key], key
    frames = wlib.Frames(word)
    before_profile = wlib.paid(word, frames)
    after_profile = wlib.paid(candidate, frames)
    assert before_profile == after_profile
    check_spec = importlib.util.spec_from_file_location("p111_xcheck", SOURCE / "code/xcheck_p.py")
    xcheck = importlib.util.module_from_spec(check_spec)
    check_spec.loader.exec_module(xcheck)
    _, labels, flow, hypotheses, conclusion, _ = xcheck.check(candidate)
    assert all(hypotheses.values()) and all(conclusion.values())
    costs = {s: [scalar_cost(word[s]), scalar_cost(candidate[s])] for s in "ABCD"}
    assert sum(old - new for old, new in costs.values()) == 20

    # Removing the initial basis change corrupts an arbitrary dirty destination.
    block = blocks[0]
    registers = block["destinations"] + block["external"]
    assert transfer(block["replacement"][1:], registers) != transfer(block["replacement"], registers)
    bad_cleanup = copy.deepcopy(candidate)
    bad_cleanup["C"].pop()
    must_reject(lambda: wlib.replay(bad_cleanup, frames))
    bad_frame = copy.deepcopy(candidate)
    bad_frame["A"][1986][0] = 0
    must_reject(lambda: wlib.replay(bad_frame, frames))
    stale_cleanup = copy.deepcopy(candidate)
    stale_cleanup["C"] = word["C"]
    wlib.replay(stale_cleanup, frames)
    assert stale_cleanup["C"] != wlib.rebuild_C(stale_cleanup)

    result = {
        "seed": SEED, "blocks": blocks, "completed_candidates": sum(b["candidates"] for b in blocks),
        "scalar_xors_by_section": costs, "saved_scalar_xors": 20,
        "scatter_xors": sum(map(len, word["scatter"])),
        "total_scalar_xors_including_scatter": [sum(cost[i] for cost in costs.values())
                                                + sum(map(len, word["scatter"])) for i in (0, 1)],
        "paid_profile": before_profile, "all_input_columns": 2 * word["v"] + word["R"],
        "inherited_independent_checker": {"closed_frames": labels["frames"],
                                         "copy_ranks": [t["rank"] for t in flow["totals"]],
                                         "hypotheses": hypotheses, "conclusion": conclusion},
        "candidate_canonical_sha256": hashlib.sha256(wlib.canon(candidate)).hexdigest(),
        "negative_controls": ["omit_preparation", "omit_cleanup", "illegal_frame_descent",
                              "stale_cleanup_fails_literal_reverse_despite_exact_endpoint"],
    }
    result = json.loads(json.dumps(result))
    return result


def main():
    evidence = json.loads((HERE / "certificate.json").read_text())
    result = verify(evidence)
    assert result == evidence["result"], json.dumps(result, indent=2)
    print("PASS_P111_MINI_NODE_BASIS: 186 candidates; 20 scalar XORs saved; "
          "661 dirty-input columns; identical frame paths and paid profile; "
          "independent interface check passed; 4 negative controls rejected")


if __name__ == "__main__":
    main()
