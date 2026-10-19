#!/usr/bin/env python3
"""Audit one exact helper-quartet preparation/injection cut. Apache-2.0."""
import hashlib
import json
from pathlib import Path
import runpy
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PIN_BASE = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
PRE = ROOT / "research/r439-helper-quartets-seed07"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(Path(path).read_text())


def pin(path, expected_sha, expected_blob):
    raw = (ROOT / path).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == expected_sha, "sha256 pin: " + path)
    blob = subprocess.check_output(
        ["git", "rev-parse", PIN_BASE + ":" + path], cwd=ROOT, text=True
    ).strip()
    need(blob == expected_blob, "git blob pin: " + path)


def apply_rows(word):
    rows = [1, 2, 4, 8]
    for dest, source in word:
        rows[dest] ^= rows[source]
    return rows


def apply_values(values, word):
    out = values[:]
    for dest, source in word:
        out[dest] ^= out[source]
    return out


def inject(coefficients, helper_values):
    value = 0
    for j, bit in enumerate(helper_values):
        if bit:
            value ^= coefficients[j]
    return value


def run():
    sources = load(HERE / "SOURCES.json")
    for row in sources["files"]:
        pin(row["path"], row["sha256"], row["git_blob"])

    # Validate the complete predecessor source closure before using its
    # frozen certificate, selected matching and candidate builder.
    predecessor_sources = load(PRE / "SOURCES.json")
    need(predecessor_sources["base_commit"] == "2921874911956718fcaaaf9396fe8267b3cfa9f0",
         "predecessor base commit")
    need(len(predecessor_sources["files"]) == 43, "predecessor source count")
    for path, expected in predecessor_sources["files"].items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        need(actual == expected, "predecessor source pin: " + path)

    cert = load(PRE / "CERTIFICATE.json")
    winner = cert["winner"]
    need(winner["indices"] == [114, 126], "chosen pair indices")
    need(winner["helpers"] == [269, 88, 288, 153], "chosen helper labels")
    word = [tuple(g) for g in winner["word"]]
    need(word == [(0, 1), (2, 3), (1, 2)], "chosen chronological word")
    need(apply_rows(word) == winner["matrix"] == [3, 14, 12, 8],
         "exact prefix matrix")
    restored_rows = apply_rows(word)
    for dest, source in reversed(word):
        restored_rows[dest] ^= restored_rows[source]
    need(restored_rows == [1, 2, 4, 8], "reverse word restores four helper coordinates")

    search = runpy.run_path(str(PRE / "search.py"))
    original, parent, _previous, target, pairs, columns = search["inputs"]()
    del original  # The cut audit consumes the reconstructed parent and D map.
    need(parent["v"] == 111 and parent["R"] == 439, "source dimensions")
    need(len(pairs) == 199 and len(target) == 306, "frozen matching dimensions")
    labels = pairs[114] + pairs[126]
    need(labels == winner["helpers"], "quartet-to-selected-pairs binding")

    # Rebuild the helper prefix by its declared pair order, independently of
    # the package's helper_operations() routine.
    operations = []
    for i, pair in enumerate(pairs):
        if i == 114:
            operations.extend((labels[d], labels[s]) for d, s in word)
        elif i != 126:
            operations.append(tuple(pair))
    need(operations == search["helper_operations"](pairs, [114, 126], word),
         "helper-operation schedule")
    need(len(operations) == 200, "helper preparation count")

    v = parent["v"]
    helper_regs = [2 * v + h for h in winner["helpers"]]
    q_start = 114  # One operation for each earlier selected pair.
    q_gates = [[0, 2 * v + labels[d], [2 * v + labels[s]]] for d, s in word]
    helper_gates = [[0, 2 * v + d, [2 * v + s]] for d, s in operations]

    # Each compiled middle column is K H^{-1}. These are the exact source
    # columns used by the frozen PR941 reconstruction.
    coefficients = columns[:]
    for d, s in operations:
        coefficients[s] ^= coefficients[d]
    middle = [
        [0, v + i, [2 * v + j for j, col in enumerate(coefficients) if col >> i & 1]]
        for i in range(v)
    ]
    candidate = search["construct"](parent, target, columns, operations)
    D = candidate["D"]
    cut = len(operations) + len(target)
    target_restore_start = cut + v
    cleanup_start = target_restore_start + len(target)
    q_cleanup_start = cleanup_start + len(operations) - (q_start + len(word))

    need(D[:len(helper_gates)] == helper_gates, "helper preparation in D")
    need(D[len(helper_gates):cut] == target, "target preparation before injection")
    need(D[cut:cut + v] == middle, "compiled middle injection")
    need(D[target_restore_start:cleanup_start] == target[::-1], "target restoration")
    need(D[cleanup_start:] == helper_gates[::-1], "literal reverse helper cleanup")
    need(D[q_start:q_start + len(q_gates)] == q_gates, "quartet preparation position")
    need(D[q_cleanup_start:q_cleanup_start + len(q_gates)] == q_gates[::-1],
         "quartet cleanup position")
    need(q_start == 114 and cut == 506 and q_cleanup_start == 1006,
         "named chronological cuts")

    # Under the pinned xcheck_p frame convention, these operands begin at
    # frame 0. Walk D through cleanup and verify that no climb or
    # source-register excursion is needed anywhere in this word.
    frames = candidate["frames"]
    current = list(candidate["start"])
    need(frames[0] == [], "frame 0 is the zero frame")
    need(all(current[r] == 0 for r in range(v, len(current))),
         "target/helper frame-zero start")
    for gi, gate in enumerate(D):
        frame, dest, srcs = gate
        need(frame == 0, "D frame-zero gate %d" % gi)
        need(v <= dest < len(current), "D destination is not target/helper")
        for r in [dest] + srcs:
            need(v <= r < len(current), "D operand is not target/helper")
            need(current[r] == frame, "frame unavailable at D gate %d register %d" % (gi, r))
            current[r] = frame

    need(all(current[r] == 0 for r in helper_regs), "quartet frame 0 at injection cut")
    late_writes = [gi for gi in range(q_start + len(q_gates), cut)
                   if D[gi][1] in set(helper_regs)]
    need(not late_writes, "quartet helper overwritten before injection")
    helper_reads = {r: 0 for r in helper_regs}
    for gate in D[cut:cut + v]:
        for r in gate[2]:
            if r in helper_reads:
                helper_reads[r] += 1
    need(all(count > 0 for count in helper_reads.values()), "every quartet helper reaches injection")

    # Check the local arbitrary-dirty boundary for the compiled middle word,
    # then a within-frame control that changes only the dependent chronology.
    wrong_operations = operations[:]
    wrong_operations[q_start:q_start + 3] = [operations[q_start], operations[q_start + 2],
                                             operations[q_start + 1]]
    need(apply_rows([word[0], word[2], word[1]]) == [3, 6, 12, 8],
         "reordered-matrix control")
    wrong_outputs = []
    first_witness = None
    for mask in range(16):
        initial = [0] * parent["R"]
        expected = 0
        for j, helper in enumerate(winner["helpers"]):
            if mask >> j & 1:
                initial[helper] = 1
                expected ^= columns[helper]
        correct_state = apply_values(initial, operations)
        correct_output = inject(coefficients, correct_state)
        need(correct_output == expected, "correct local dirty input %d" % mask)
        wrong_state = apply_values(initial, wrong_operations)
        wrong_output = inject(coefficients, wrong_state)
        if wrong_output != expected:
            wrong_outputs.append(mask)
            if first_witness is None:
                first_witness = (mask, expected, wrong_output)
    need(first_witness is not None, "reordered word must have a local boundary witness")
    mask, expected, wrong_output = first_witness
    need(mask == 8, "canonical smallest reorder witness is helper 153")
    delta = expected ^ wrong_output
    support = [i for i in range(v) if delta >> i & 1]
    need(expected == 0x4001480001100e2040150e2110, "expected helper-153 output")
    need(wrong_output == 0x4041402001008a6004150c2118, "reordered helper-153 output")
    need(support == [3, 17, 34, 38, 46, 50, 55, 60, 77, 83, 94],
         "reordered output support")

    print(
        "PASS_R439_QUARTET_FRAME_CUT "
        "prep=114:117 injection=506 helpers_frame0=true "
        "helper_reads=9,11,8,15 local_inputs=16 "
        "reorder_failures=%d reorder_witness=153 "
        "delta_support=3,17,34,38,46,50,55,60,77,83,94 no_supplier_claim"
        % len(wrong_outputs)
    )


if __name__ == "__main__":
    run()
