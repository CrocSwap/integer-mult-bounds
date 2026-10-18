"""Independent, standard-library audit of one frozen R420 block replacement.

No producer, optimizer, primary verifier, or predecessor checker is imported.
F2 semantics are checked one input column at a time, using sets of active
registers (rather than simultaneous bit-packed rows). Nonnegative propagation
uses the literal scalar COPY/ADD/ERASE recipe of the predecessor exporter.

Prepared for yongjae321 with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


class Rejected(ValueError):
    """The supplied certificate fails an explicit audit condition."""


def need(condition, message):
    if not condition:
        raise Rejected(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def load(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith(".gz") else raw)


def rank(rows):
    """Exact rational rank, with a separate incremental echelon implementation."""
    basis = {}
    for source in rows:
        row = [Fraction(x) for x in source]
        for pivot in sorted(basis):
            if row[pivot]:
                scale = row[pivot]
                row = [a - scale * b for a, b in zip(row, basis[pivot])]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is not None:
            scale = row[pivot]
            basis[pivot] = [value / scale for value in row]
    return len(basis)


def validate_word(word):
    need((word["h"], word["v"], word["R"], word["form"]) ==
         (8, 120, 420, "<x,y>/2"), "unexpected word header")
    n = 2 * word["v"] + word["R"]
    need(len(word["start"]) == len(word["final"]) == n,
         "incorrect start/final register count")
    nf = len(word["frames"])
    for section in ("D", "A", "B", "C"):
        for number, gate in enumerate(word[section]):
            need(isinstance(gate, list) and len(gate) == 3,
                 f"malformed {section} gate {number}")
            frame, destination, sources = gate
            need(type(frame) is int and 0 <= frame < nf, "invalid gate frame")
            need(isinstance(sources, list) and sources, "empty gate sources")
            operands = [destination] + sources
            need(all(type(r) is int and 0 <= r < n for r in operands),
                 "invalid register operand")
            need(len(set(operands)) == len(operands), "repeated gate operand")
    need(len(word["scatter"]) == word["v"], "incorrect scatter row count")
    need(len(word["ret"]) == len(set(word["ret"])) == 9,
         "incorrect retained helper set")
    need(all(type(r) is int and 240 <= r < n for r in word["ret"]),
         "retained register is not a helper")
    for row in word["scatter"]:
        need(len(row) == len(set(row)) and
             all(type(k) is int and 0 <= k < 9 for k in row),
             "invalid scatter index")
    return n


def selected_block(word):
    """Derive the ten contiguous source-only phase-B block runs from the word."""
    v = word["v"]
    runs = []
    for index, (frame, destination, sources) in enumerate(word["B"]):
        source_only = destination < v and len(sources) == 1 and sources[0] < v
        if source_only:
            if runs and runs[-1][1] == index and runs[-1][2] == frame:
                runs[-1][1] += 1
            else:
                runs.append([index, index + 1, frame])
    need(len(runs) == 10, "expected ten source-only block runs")
    start, stop, frame = runs[3]
    registers = sorted({r for _, d, ss in word["B"][start:stop] for r in [d] + ss})
    need(len(registers) == 12, "block 3 must act on twelve registers")
    need((start, stop, frame) == (263, 313, 545), "unexpected frozen block location")
    index = {r: k for k, r in enumerate(registers)}
    operations = [[index[d], index[ss[0]]] for _, d, ss in word["B"][start:stop]]
    return start, stop, frame, registers, operations


def literal_cleanup(word, full_frame):
    v = word["v"]
    return [[full_frame, d, list(ss)]
            for _, d, ss in reversed(word["A"] + word["B"])
            if not v <= d < 2 * v]


def assemble(baseline, certificate):
    """Independently bind the local operations to physical registers and cleanup."""
    validate_word(baseline)
    start, stop, frame, registers, old = selected_block(baseline)
    expected = {"block_index": 3, "b_start": start, "b_stop": stop,
                "frame": frame, "registers": registers, "original_local_ops": old}
    for key, value in expected.items():
        need(certificate.get(key) == value, f"certificate disagrees with baseline: {key}")
    operations = certificate["replacement_local_ops"]
    need(isinstance(operations, list) and operations, "empty replacement")
    for op in operations:
        need(isinstance(op, list) and len(op) == 2 and
             all(type(i) is int and 0 <= i < 12 for i in op) and op[0] != op[1],
             "invalid replacement operation")
    # The inherited full frame is the unique frame containing all 120 lines.
    full = [k for k, lines in enumerate(baseline["frames"])
            if set(lines) == set(range(120))]
    need(len(full) == 1, "missing unique full frame")
    need(baseline["C"] == literal_cleanup(baseline, full[0]),
         "baseline cleanup is not the literal reverse")
    candidate = copy.deepcopy(baseline)
    candidate["B"][start:stop] = [[frame, registers[a], [registers[b]]]
                                     for a, b in operations]
    candidate["C"] = literal_cleanup(candidate, full[0])
    validate_word(candidate)
    return candidate, old, operations


def column_map(operations, width):
    columns = []
    for source in range(width):
        active = {source}
        for destination, operand in operations:
            if operand in active:
                active.symmetric_difference_update({destination})
        columns.append(sorted(active))
    return columns


def word_columns(word):
    """Exhaust all independent source, target, and dirty-helper input columns."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    output = []
    for source in range(n):
        active = {source}
        for phase in ("D", "A", "scatter", "B", "C"):
            if phase == "scatter":
                retained = [r in active for r in word["ret"]]
                for t, row in enumerate(word[phase]):
                    if sum(retained[k] for k in row) % 2:
                        active.symmetric_difference_update({v + t})
            else:
                for _, destination, operands in word[phase]:
                    if sum(r in active for r in operands) % 2:
                        active.symmetric_difference_update({destination})
        expected = {source, source + v} if source < v else {source}
        need(active == expected, f"full-word map failed on input column {source}")
        output.append(sorted(active))
    return output


def scalar_stream(word):
    """Expand export_records.py semantics, omitting frame-only MOVE records.

    Each ADD has coefficient +1. Scatter uses fresh copies grouped by retained
    helper, exactly as the exporter does; the copied helper is unchanged inside
    each such block. This includes a separate temporary-register lifecycle.
    """
    stream = []
    temporary = 2 * word["v"] + word["R"]
    for phase in ("D", "A", "scatter", "B", "C"):
        if phase == "scatter":
            for k, center in enumerate(word["ret"]):
                stream.append(("copy", temporary, center))
                for t, row in enumerate(word[phase]):
                    if k in row:
                        stream.append(("add", word["v"] + t, temporary))
                stream.append(("erase", temporary, center))
        else:
            for _, destination, sources in word[phase]:
                stream.extend(("add", destination, source) for source in sources)
    return stream


def scalar_prefix(word):
    stream = scalar_stream(word)
    n = 2 * word["v"] + word["R"]
    results = {}
    for reverse in (False, True):
        weights = [1] * n + [0]
        maximum, opened = 1, None
        for kind, destination, source in (reversed(stream) if reverse else stream):
            if reverse and kind != "add":
                kind = "erase" if kind == "copy" else "copy"
            if kind == "add":
                need(destination != opened, "copied center modified while copy is live")
                need(source != n or opened is not None, "read from closed temporary")
                weights[destination] += weights[source]
                maximum = max(maximum, weights[destination])
            elif kind == "copy":
                need(opened is None, "nested temporary copy")
                opened = source
                weights[n] = weights[source]
            else:
                need(opened == source, "mismatched temporary erase")
                opened = None
                weights[n] = 0
        need(opened is None and weights[n] == 0, "temporary work remains live")
        results["reverse" if reverse else "forward"] = maximum
    payload = 64 * results["forward"] ** 3 * results["reverse"] ** 2
    return {**results, "payload_prefix_upper": payload,
            "payload_prefix_bits": payload.bit_length(),
            "scalar_additions": sum(kind == "add" for kind, _, _ in stream),
            "fresh_copies": sum(kind == "copy" for kind, _, _ in stream)}


def local_nonnegative(operations):
    def transfer(sequence):
        rows = [[int(a == b) for b in range(12)] for a in range(12)]
        for a, b in sequence:
            rows[a] = [x + y for x, y in zip(rows[a], rows[b])]
        return rows
    forward = transfer(operations)
    reverse = transfer(list(reversed(operations)))
    round_trip = transfer(operations + list(reversed(operations)))
    return {"forward_transfer": forward, "reverse_transfer": reverse,
            "round_trip_unit_max": max(map(sum, round_trip))}


def frame_profile(word, dimensions):
    """Replay promotions, including copied-center rank charges, independently."""
    frames = [set(f) for f in word["frames"]]
    current = list(word["start"])
    histogram = Counter()
    paths = [[f] for f in current]

    def move(register, frame):
        old = current[register]
        if old != frame:
            need(frames[old] <= frames[frame] and dimensions[old] < dimensions[frame],
                 f"non-nested frame movement at register {register}")
            histogram[dimensions[frame] - dimensions[old]] += 1
            current[register] = frame
            paths[register].append(frame)

    for phase in ("D", "A", "scatter", "B", "C"):
        if phase == "scatter":
            for retained in word["ret"]:
                need(dimensions[current[retained]] == 8,
                     "retained center is not full-dimensional")
                histogram[8] += 1
        else:
            for frame, destination, sources in word[phase]:
                for register in [destination] + sources:
                    move(register, frame)
    for register, frame in enumerate(word["final"]):
        move(register, frame)
    return {"raw_H": dict(sorted(histogram.items())),
            "rank_mass": sum(rank * count for rank, count in histogram.items()),
            "per_register_frame_paths_sha256": digest(paths), "paths": paths}


def audit(baseline, certificate, supplied_word=None):
    candidate, old_ops, new_ops = assemble(baseline, certificate)
    if supplied_word is not None:
        need(candidate == supplied_word, "supplied full word differs from independent reconstruction")
    old_columns, new_columns = column_map(old_ops, 12), column_map(new_ops, 12)
    need(old_columns == new_columns, "12-column fixed-output map changed")
    need(column_map(new_ops + list(reversed(new_ops)), 12) == [[i] for i in range(12)],
         "local reverse cleanup fails")
    old_word_columns, new_word_columns = word_columns(baseline), word_columns(candidate)
    need(old_word_columns == new_word_columns, "full-word maps differ")
    old_norm, new_norm = local_nonnegative(old_ops), local_nonnegative(new_ops)
    old_prefix, new_prefix = scalar_prefix(baseline), scalar_prefix(candidate)
    dimensions = [rank([baseline["lines"][i] for i in frame])
                  for frame in baseline["frames"]]
    old_frames, new_frames = frame_profile(baseline, dimensions), frame_profile(candidate, dimensions)
    need(old_frames == new_frames, "paid rank histogram or a register frame path changed")
    no_worse = {direction: new_prefix[direction] <= old_prefix[direction]
                for direction in ("forward", "reverse", "payload_prefix_upper")}
    dominance = {key: all(a <= b for ar, br in zip(new_norm[key], old_norm[key])
                          for a, b in zip(ar, br))
                 for key in ("forward_transfer", "reverse_transfer")}
    need(all(dominance.values()),
         "forward or reverse nonnegative transfer is not componentwise dominated")
    need(len(new_ops) < len(old_ops), "replacement does not save binary XOR gates")
    need(new_norm["round_trip_unit_max"] <= old_norm["round_trip_unit_max"],
         "local cancellation-free round-trip unit maximum increased")
    need(all(no_worse.values()), "emitted local scalar prefix bound increased")
    return {
        "status": "PASS_INDEPENDENT_BLOCK_AND_ALL_DIRTY_INPUT_COLUMNS",
        "method": "One F2 input column at a time; active-register sets; no builder or checker imports",
        "baseline_content_sha256": digest(baseline), "candidate_content_sha256": digest(candidate),
        "certificate_sha256": digest(certificate), "block_columns_checked": 12,
        "full_word_columns_checked_per_word": 660, "dirty_helper_columns": 420,
        "full_word_map_sha256": digest(new_word_columns), "block_map_sha256": digest(new_columns),
        "sources_restored": True, "helpers_restored": True, "targets_equal_y_plus_x": True,
        "literal_reversed_cleanup": True, "fixed_physical_output_assignment": True,
        "local_gates": {"baseline": len(old_ops), "candidate": len(new_ops),
                        "whole_word_binary_ADD_saving": 2 * (len(old_ops) - len(new_ops))},
        "local_round_trip_unit_max": {"baseline": old_norm["round_trip_unit_max"],
                                      "candidate": new_norm["round_trip_unit_max"]},
        "componentwise_nonnegative_transfer_dominance": dominance,
        "exported_local_scalar_prefix": {"baseline": old_prefix, "candidate": new_prefix,
                                         "no_increase": no_worse},
        "paid_frame_profile": {k: value for k, value in new_frames.items() if k != "paths"},
        "unchanged_each_register_frame_path": True,
        "scope": "Finite local word and cohort prefix only; no hosted invoice or kappa claim."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--word", type=Path, help="also check the producer's full emitted word")
    parser.add_argument("--out", type=Path, help="write a new JSON report; existing files are refused")
    args = parser.parse_args()
    try:
        result = audit(load(args.baseline), load(args.certificate),
                       load(args.word) if args.word else None)
    except (Rejected, KeyError, TypeError, ValueError) as error:
        print(json.dumps({"status": "REJECT", "reason": str(error)}, indent=2))
        return 1
    rendered = json.dumps(result, indent=2) + "\n"
    if args.out:
        with args.out.open("x", encoding="utf-8") as output:
            output.write(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
