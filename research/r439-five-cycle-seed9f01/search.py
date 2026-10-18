#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exhaust the declared five-helper cyclic-sweep domain on the pinned R439 word."""
import gzip
import hashlib
import itertools
import json
import gzip
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_WORD = ROOT / "research/r439-bsection-stars-seed01/candidate.json.gz"
TOP = 20
WIDTH = 5


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_word(path=BASE_WORD):
    return json.loads(gzip.decompress(path.read_bytes()))


def split_d(word):
    """Identify helper prep, target prep, injection, target restore, helper restore."""
    v, base = word["v"], 2 * word["v"]
    parts = {"helper_prep": [], "target_prep": [], "injection": [],
             "target_restore": [], "helper_restore": []}
    stage = "helper_prep"
    for gate in word["D"]:
        frame, dest, srcs = gate
        if frame != 0:
            raise ValueError("D gate left frame zero")
        dest_target = v <= dest < 2 * v
        dest_helper = dest >= base
        src_targets = bool(srcs) and all(v <= s < 2 * v for s in srcs)
        src_helpers = bool(srcs) and all(s >= base for s in srcs)
        if stage == "helper_prep" and dest_target:
            stage = "target_prep"
        if stage == "target_prep" and dest_target and src_helpers:
            stage = "injection"
        if stage == "injection" and dest_target and src_targets:
            stage = "target_restore"
        if stage == "target_restore" and dest_helper:
            stage = "helper_restore"
        if stage == "helper_prep":
            if not (dest_helper and src_helpers and len(srcs) == 1):
                raise ValueError("malformed helper preparation")
            parts[stage].append(gate)
        elif stage in ("target_prep", "target_restore"):
            if not (dest_target and src_targets and len(srcs) == 1):
                raise ValueError("malformed target basis change")
            parts[stage].append(gate)
        elif stage == "injection":
            if not (dest_target and src_helpers):
                raise ValueError("malformed D injection")
            parts[stage].append(gate)
        else:
            if not (dest_helper and src_helpers and len(srcs) == 1):
                raise ValueError("malformed helper restoration")
            parts[stage].append(gate)
    expected = {"helper_prep": 236, "target_prep": 306, "injection": 111,
                "target_restore": 306, "helper_restore": 236}
    if {k: len(vv) for k, vv in parts.items()} != expected:
        raise ValueError("unexpected D block lengths")
    return parts


def injection_columns(word, injection):
    v, R, base = word["v"], word["R"], 2 * word["v"]
    columns = [0] * R
    seen_targets = set()
    for _, dest, srcs in injection:
        row = dest - v
        if row in seen_targets or not 0 <= row < v:
            raise ValueError("duplicate or invalid injection target")
        seen_targets.add(row)
        if len(set(srcs)) != len(srcs):
            raise ValueError("duplicate injection source")
        for src in srcs:
            columns[src - base] |= 1 << row
    if seen_targets != set(range(v)):
        raise ValueError("injection does not cover all target rows")
    return columns


def ranking(columns):
    scores = [sum((columns[i] & columns[j]).bit_count()
                  for j in range(len(columns)) if j != i)
              for i in range(len(columns))]
    return sorted(range(len(columns)),
                  key=lambda i: (-scores[i], -columns[i].bit_count(), i))


def rank_bits(vectors):
    pivots = {}
    for x in vectors:
        while x:
            bit = x.bit_length() - 1
            if bit in pivots:
                x ^= pivots[bit]
            else:
                pivots[bit] = x
                break
    return len(pivots)


def apply_cycle(columns, permutation):
    """Return J H^{-1}; H is the chronological five-edge helper sweep."""
    out = columns.copy()
    edges = [(permutation[k], permutation[(k + 1) % WIDTH])
             for k in range(WIDTH)]
    # A prep edge h_dest ^= h_src left-multiplies H by T. Right multiplication
    # of J by H^{-1} updates its source column by its destination column.
    for dest, src in edges:
        out[src] ^= out[dest]
    return out, edges


def optimistic_ceiling(columns, top):
    best = None
    for support in itertools.combinations(top, WIDTH):
        old = sum(columns[i].bit_count() for i in support)
        rank = rank_bits([columns[i] for i in support])
        # Any invertible basis has at least rank(J|support) nonzero output columns.
        # Pay ten ADDs for the five-edge preparation and inverse restoration.
        ceiling = old - rank - 2 * WIDTH
        item = (ceiling, support, old, rank)
        if best is None or item > best:
            best = item
    return best


def search():
    word = load_word()
    parts = split_d(word)
    columns = injection_columns(word, parts["injection"])
    total = sum(col.bit_count() for col in columns)
    top = ranking(columns)[:TOP]
    ceiling = optimistic_ceiling(columns, top)

    best_key = None
    best = []
    candidates = 0
    positive = 0
    for support in itertools.combinations(top, WIDTH):
        support_weight = sum(columns[i].bit_count() for i in support)
        for permutation in itertools.permutations(support):
            candidates += 1
            changed, edges = apply_cycle(columns, permutation)
            new_weight = total - support_weight + sum(changed[i].bit_count() for i in support)
            saving = total - new_weight - 2 * WIDTH
            if saving <= 0:
                continue
            positive += 1
            # Retain the best 64 by exact completed D ADD saving, then stable IDs.
            key = (-saving, tuple(sorted(support)), permutation)
            if best_key is None or key < best_key:
                best_key = key
            item = {"saving": saving, "support": list(sorted(support)),
                    "permutation": list(permutation), "edges": [list(e) for e in edges],
                    "old_support_weight": support_weight,
                    "new_support_weight": sum(changed[i].bit_count() for i in support),
                    "injection_weight": new_weight}
            best.append((key, item))
            if len(best) > 64:
                best.sort(key=lambda x: x[0])
                best.pop()
    best.sort(key=lambda x: x[0])
    return word, parts, columns, {
        "top_helpers": top,
        "top_scores": [sum((columns[i] & columns[j]).bit_count()
                            for j in range(len(columns)) if j != i) for i in top],
        "supports": 15504,
        "sweeps_per_support": 120,
        "candidates": candidates,
        "positive_saving_candidates": positive,
        "base_injection_adds": total,
        "optimistic_max_net_ADD_saving": {
            "net": ceiling[0], "support": list(ceiling[1]),
            "old_weight": ceiling[2], "rank": ceiling[3],
            "preparation_and_restoration_ADDs": 10},
        "best_64": [x[1] for x in best],
        "stopping_rule": "complete all 15,504 five-subsets of the top 20 helpers and all 120 directed cyclic sweeps per subset",
    }


def candidate_for(word, parts, columns, item):
    out = json.loads(json.dumps(word))
    v, base = out["v"], 2 * out["v"]
    permutation = item["permutation"]
    changed, edges = apply_cycle(columns, permutation)
    prep = [[0, base + dest, [base + src]] for dest, src in edges]
    restore = [[0, base + dest, [base + src]] for dest, src in reversed(edges)]
    target_order = [gate[1] for gate in parts["injection"]]
    injection = []
    for dest in target_order:
        srcs = [base + i for i, col in enumerate(changed) if (col >> (dest - v)) & 1]
        injection.append([0, dest, srcs])
    out["D"] = (parts["helper_prep"] + prep + parts["target_prep"] + injection +
                parts["target_restore"] + restore + parts["helper_restore"])
    return out


def main():
    word, parts, columns, result = search()
    best = result["best_64"]
    if best:
        candidate = candidate_for(word, parts, columns, best[0])
        payload = canonical(candidate)
        (HERE / "CANDIDATE.json.gz").write_bytes(gzip.compress(payload, mtime=0))
        result["candidate_sha256"] = hashlib.sha256(payload).hexdigest()
        result["candidate_gzip_sha256"] = hashlib.sha256((HERE / "CANDIDATE.json.gz").read_bytes()).hexdigest()
        result["selected_candidate"] = best[0]
    else:
        result["candidate_sha256"] = None
        result["candidate_gzip_sha256"] = None
        result["selected_candidate"] = None
        (HERE / "CANDIDATE.json.gz").unlink(missing_ok=True)
    (HERE / "SEARCH-RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_R439_FIVE_CYCLE_SEARCH candidates=%d positive=%d best_ADD_saving=%d ceiling=%d" % (
        result["candidates"], result["positive_saving_candidates"],
        best[0]["saving"] if best else 0,
        result["optimistic_max_net_ADD_saving"]["net"]))


if __name__ == "__main__":
    main()
