#!/usr/bin/env python3
"""Check the fixed factory interface and its frame obstructions."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(test, message):
    if not test:
        raise ValueError(message)


def basis(vectors):
    pivots = {}
    for vector in vectors:
        for p in sorted(pivots, reverse=True):
            if vector >> p & 1:
                vector ^= pivots[p]
        if vector:
            p = vector.bit_length() - 1
            for k in pivots:
                if pivots[k] >> p & 1:
                    pivots[k] ^= vector
            pivots[p] = vector
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def points(frame):
    result = {0}
    for vector in frame:
        result |= {x ^ vector for x in result}
    return result


def contained(first, second):
    return points(first) <= points(second)


def antichain(frames):
    require(len(set(frames)) == len(frames), "duplicate demand frame")
    for first, second in combinations(frames, 2):
        require(not contained(first, second) and not contained(second, first),
                "comparable demand frames")


def rank(matrix):
    rows = [[Q(x) for x in row] for row in matrix]
    pivot = 0
    for column in range(len(rows[0])):
        found = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        scale = rows[pivot][column]
        rows[pivot] = [x / scale for x in rows[pivot]]
        for i in range(len(rows)):
            if i != pivot:
                scale = rows[i][column]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def apply(event, rows):
    target = event[1]
    if event[0] == "scale":
        q = Q(event[2], event[3])
        rows[target] = {k: q * x for k, x in rows[target].items()}
        return [target]
    require(event[0] == "add", "unknown scalar event")
    source = event[2]
    q = Q(event[3], event[4])
    for k, x in list(rows[source].items()):
        value = rows[target].get(k, Q(0)) + q * x
        if value:
            rows[target][k] = value
        else:
            rows[target].pop(k, None)
    return [target, source]


def serialized_row(row):
    return [[k, str(q)] for k, q in sorted(row.items())]


def normalized(row):
    scale = row[min(row)]
    return tuple((k, q / scale) for k, q in sorted(row.items()))


def factory_demands(modules, word):
    demands = {}
    k_pairs = {(0, 1), (2, 3), (4, 5), (6, 7)}
    require(len(modules) == 14, "factory block count")
    all_sources = [s - 8 for module in modules for s in module["receipt"]["source_lines"]]
    require(sorted(all_sources) == list(range(112)), "factory source partition")
    for module in modules:
        block = module["receipt"]["block"]
        keys = [(pair, sign) for pair in combinations(block, 2) for sign in (-1, 1)]
        frames = [basis(x) for x in module["start_frames"]]
        require(len(frames) == 24 and all(not frame for frame in frames[8:]), "factory helper allocation")
        labels = [basis(x)[0] for x in module["start_frames"][:8]]
        require(labels == [word["ports"][s - 8] for s in module["receipt"]["source_lines"]],
                "factory labels do not match word")
        rows = [{r: Q(1)} if r < 8 else {} for r in range(24)]
        for index, event in enumerate(module["events"]):
            if index == 40:
                pair_frames, pair_rows = frames[:], [dict(row) for row in rows]
            target, source = event[:2]
            require(0 <= target < 24 and 0 <= source < 24 and target != source,
                    "factory register allocation")
            frame = basis(module["event_frames"][index])
            require(contained(frames[target], frame) and contained(frames[source], frame),
                    "factory frame descent")
            apply(["add"] + event + [list(frame)], rows)
            frames[target] = frames[source] = frame
            for register in (target, source):
                require(contained(basis(labels[k] for k in rows[register]), frame),
                        "factory support outside frame")
            if index < 40:
                continue
            pair, sign = keys[index - 40]
            if pair in k_pairs:
                choices = [(r, pair_frames[r], pair_rows[r], "leaver") for r in (target, source)]
            else:
                choices = [(target, frame, rows[target], "face")]
            for register, wanted, row, kind in choices:
                require(basis(labels[k] for k in row) == wanted, "factory support hull")
                global_row = {module["receipt"]["source_lines"][k] - 8: q for k, q in row.items()}
                demand = demands.setdefault(wanted, {"kind": kind, "block": block, "clean_rows": set()})
                demand["clean_rows"].add(normalized(global_row))
    antichain(list(demands))
    require(Counter(x["kind"] for x in demands.values()) == {"face": 144, "leaver": 24},
            "factory interface changed")
    require(sum(len(x["clean_rows"]) for x in demands.values()) == 192, "factory value count changed")
    return demands


def word_witnesses(word, demands):
    v = word["report"]["v"]
    n = 2 * v + word["report"]["R"]
    rows = [{r: Q(1)} if r < v else {} for r in range(n)]
    frames = [(p,) for p in word["ports"]] + [()] * (n - v)
    for register, frame in word["start_extra"].items():
        frames[int(register)] = basis(frame)
    found = {}
    for phase in ("A", "B"):
        for index, event in enumerate(word[phase]):
            if event[0] == "add":
                require(not (v <= event[2] < 2 * v and not v <= event[1] < 2 * v),
                        "target feedback into source circuit")
            touched = apply(event, rows)
            frame = basis(event[-1])
            for register in touched:
                require(contained(frames[register], frame), "word frame descent")
                frames[register] = frame
                if v <= register < 2 * v:
                    continue
                hull = basis(word["ports"][k] for k in rows[register])
                require(contained(hull, frame), "source support outside frame")
                if frame in demands and hull == frame:
                    clean = normalized(rows[register])
                    key = frame, clean
                    if clean in demands[frame]["clean_rows"] and key not in found:
                        found[key] = {"phase": phase, "event": index, "register": register,
                                      "frame": list(frame), "clean_row": serialized_row(rows[register]),
                                      "kind": demands[frame]["kind"], "block": demands[frame]["block"]}
    expected = {(frame, row) for frame, demand in demands.items() for row in demand["clean_rows"]}
    require(set(found) == expected, "word does not supply the demand interface")
    return [found[key] for key in sorted(found)]


def check_witness(word, witness):
    v = word["report"]["v"]
    n = 2 * v + word["report"]["R"]
    rows = [{r: Q(1)} if r < v else {} for r in range(n)]
    for phase in ("A", "B"):
        for index, event in enumerate(word[phase]):
            apply(event, rows)
            if (phase, index) == (witness["phase"], witness["event"]):
                require(serialized_row(rows[witness["register"]]) == witness["clean_row"],
                        "demand row mismatch")
                require(basis(event[-1]) == tuple(witness["frame"]), "demand frame mismatch")
                return
    raise ValueError("demand event missing")


def cap_witnesses(frames, ports):
    result = []
    for frame in frames:
        witnesses = []
        for port in ports:
            odd = next((x for x in sorted(points(frame)) if (x & port).bit_count() % 2), None)
            require(odd is not None, "frame fits a target cap")
            witnesses.append(odd)
        result.append({"frame": list(frame), "odd_vectors_by_target": witnesses})
    return result


def cold_groups(word):
    groups = defaultdict(list)
    for register, frame in word["helper_final"].items():
        if len(frame) == 4 and register not in word["start_extra"]:
            groups[basis(frame)].append(int(register))
    require(len(groups) == 8 and all(len(hs) == 4 for hs in groups.values()), "cold groups changed")
    return groups


def cold_restoration(word, groups, omit=None):
    v = word["report"]["v"]
    n = 2 * v + word["report"]["R"]
    rows = [{r: Q(1)} for r in range(n)]
    for event in word["A"]:
        apply(event, rows)
    results = []
    for frame, helpers in sorted(groups.items()):
        require(all(not set(event[1:3] if event[0] == "add" else event[1:2]) & set(helpers)
                    for event in word["B"]), "cold helper has a B use")
        tails = [(index, word["cleanup"][index][:-1] + [level])
                 for index, level in word["early_cleanup"]
                 if word["cleanup"][index][1] in helpers]
        fresh = [dict(row) for row in rows]
        for index, event in tails:
            if index != omit:
                apply(event, fresh)
        require(all(fresh[h] == {h: Q(1)} for h in helpers), "cold dirt not restored")
        results.append({"frame": list(frame), "helpers": sorted(helpers),
                        "tail_indices": [index for index, event in tails], "arbitrary_columns": n})
    return results


def split_carriers(word, modules, groups):
    results = []
    for module in modules:
        sources = [i - 8 for i in module["receipt"]["source_lines"]]
        labels = [word["ports"][i] for i in sources]
        frame = basis(labels)
        if frame not in groups:
            continue
        block = module["receipt"]["block"]
        matrix = [[word["root_lines"][j][i] for j in sources] for i in block]
        masks = defaultdict(list)
        for target, port in enumerate(word["ports"]):
            mask = sum(1 << j for j, label in enumerate(labels) if (label & port).bit_count() % 2 == 0)
            masks[mask].append(target)
        require(len(masks) == 15 and 255 not in masks, "target mask class changed")
        require(all(mask.bit_count() in (0, 4) for mask in masks), "target mask support size")
        partitions = []
        for mask in sorted(masks):
            other = 255 ^ mask
            if mask >= other or other not in masks:
                continue
            ranks = [rank([[row[j] for j in range(8) if side >> j & 1] for row in matrix])
                     for side in (mask, other)]
            partitions.append({"masks": [mask, other], "ranks": ranks,
                               "target_pairs": len(masks[mask]) * len(masks[other])})
        require(Counter(tuple(item["ranks"]) for item in partitions) == {(3, 3): 6, (4, 4): 1},
                "two-cap split ranks changed")
        carriers, targets = [], []
        for a, b in ((0, 1), (2, 3)):
            for sign in (1, -1):
                row = [matrix[a][j] + sign * matrix[b][j] for j in range(8)]
                mask = sum(1 << j for j, q in enumerate(row) if q)
                target = next(t for t in masks[mask] if t not in targets)
                targets.append(target)
                require(len(basis(labels[j] for j, q in enumerate(row) if q)) == 3, "mixed carrier rank")
                carriers.append(row)
        require(rank(carriers) == 4, "mixed carriers dependent")
        for pair, (a, b) in enumerate(((0, 1), (2, 3))):
            plus, minus = carriers[2 * pair:2 * pair + 2]
            require([Q(x + y, 2) for x, y in zip(plus, minus)] == matrix[a], "mixed sum decoder")
            require([Q(x - y, 2) for x, y in zip(plus, minus)] == matrix[b], "mixed difference decoder")
        results.append({"block": block, "sources": sources,
                        "target_masks": [{"mask": mask, "targets": masks[mask]} for mask in sorted(masks)],
                        "two_cap_partitions": partitions,
                        "four_cap_escape": {"targets": targets, "rows": carriers,
                                            "rational_rank": 4, "frame_ranks": [3] * 4}})
    require(len(results) == 8, "split block coverage")
    return results


def expect_failure(operation, reason):
    try:
        operation()
    except ValueError as error:
        require(str(error) == reason, "wrong control rejection: " + str(error))
        return reason
    raise ValueError("control accepted: " + reason)


def controls(word, demands, witnesses, groups):
    frames = list(demands)
    result = [expect_failure(lambda: antichain([frames[0], frames[0]]), "duplicate demand frame")]
    larger = basis(list(frames[0]) + [x for x in range(1, 512) if x not in points(frames[0])][:1])
    result.append(expect_failure(lambda: antichain([frames[0], larger]), "comparable demand frames"))
    changed = dict(witnesses[0])
    changed["clean_row"] = [list(entry) for entry in changed["clean_row"]]
    changed["clean_row"][0][1] = str(Q(changed["clean_row"][0][1]) + 1)
    result.append(expect_failure(lambda: check_witness(word, changed), "demand row mismatch"))
    full_frame = next(iter(groups))
    orthogonal = next(p for p in range(1, 512) if all((x & p).bit_count() % 2 == 0 for x in full_frame))
    result.append(expect_failure(lambda: cap_witnesses([full_frame], [orthogonal]), "frame fits a target cap"))
    tails = cold_restoration(word, groups)
    result.append(expect_failure(lambda: cold_restoration(word, groups, tails[0]["tail_indices"][0]),
                                 "cold dirt not restored"))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    pins = json.loads((HERE / "SOURCES.json").read_text())
    inputs = {}
    for name, pin in pins["inputs"].items():
        data = (HERE / "inputs" / name).read_bytes()
        if name.endswith(".gz"):
            data = gzip.decompress(data)
        require(hashlib.sha256(data).hexdigest() == pin["content_sha256"], "input pin mismatch: " + name)
        inputs[name] = json.loads(data)
    word = inputs["SEVEN-SLOT-WORD.json.gz"]
    modules = inputs["PACKET-PROGRAMS.json.gz"]
    slot_pins = inputs["SLOT-PINS-k8.json"]
    require(slot_pins["word_sha256"] == pins["inputs"]["SEVEN-SLOT-WORD.json.gz"]["content_sha256"],
            "word does not match slot source pin")
    require(word["report"]["v"] == 112 and word["report"]["R"] == 480, "word size changed")
    require(len(word["center_frames"]) == 8 and all(len(basis(x)) == 8 for x in word["center_frames"]),
            "center frame inventory changed")
    demands = factory_demands(modules, word)
    witnesses = word_witnesses(word, demands)
    groups = cold_groups(word)
    prices = []
    for stages in (9, 37):
        m = 8 * stages + 1
        require(m * 9 ** 32 < 11 ** 32, "descent cost screen failed")
        prices.append({"stages": stages, "parent_rank": m, "max_b": "1/32",
                       "max_removed_width": 9, "extra_rank_per_reused_role": 2,
                       "integer_slack": 11 ** 32 - m * 9 ** 32})
    result = {"status": "PASS_K8_FRAME_ANTICHAIN", "base_commit": pins["base_commit"],
              "scope": "fixed factory value/frame interface; no kappa claim",
              "factory": {"demand_frame_count": 168, "demand_value_count": 192,
                          "frame_ranks": {"2": 24, "3": 144},
                          "source_registers": 112, "register_lower_bound": 336,
                          "helper_lower_bound": 224, "attained_helpers": 14 * 16,
                          "upper_witness": {"modules": len(modules), "registers_per_module": 24,
                                            "source_partition": list(range(112)),
                                            "executed_adds": sum(len(m["events"]) for m in modules)},
                          "witnesses": witnesses},
              "whole_block_target_exclusion": cap_witnesses(sorted(groups), word["ports"]),
              "center_target_exclusion": cap_witnesses([basis(x) for x in word["center_frames"]], word["ports"]),
              "early_scalar_restoration": cold_restoration(word, groups),
              "split_carriers": split_carriers(word, modules, groups),
              "descent_only_cost_screen": prices,
              "negative_controls": controls(word, demands, witnesses, groups)}
    certificate = HERE / "CERTIFICATE.json"
    if args.write_certificate:
        certificate.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(result == json.loads(certificate.read_text()), "certificate differs from replay")
    print("PASS_K8_FRAME_ANTICHAIN demands=168 helpers=224 cold_caps=896 center_caps=896 split_blocks=8 controls=5")


if __name__ == "__main__":
    main()
