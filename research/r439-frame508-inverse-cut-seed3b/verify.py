#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact inverse-column obstruction for the exceptional R439 frame-508 source."""

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R439 = ROOT / "research/r439-bsection-stars-seed01"
STAR = ROOT / "research/r439-helper-stars-seed19"
PREDECESSOR = ROOT / "research/r439-bblock-frame-barrier"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span_basis(lines, indices):
    """Return an exact rational basis as selected line indices."""
    pivots = {}
    chosen = []
    for i in sorted(set(indices)):
        row = list(map(Fraction, lines[i]))
        for p in sorted(pivots):
            t = row[p]
            if t:
                row = [x - t * y for x, y in zip(row, pivots[p])]
        p = next((j for j, x in enumerate(row) if x), None)
        if p is not None:
            t = row[p]
            pivots[p] = [x / t for x in row]
            chosen.append(i)
    return chosen


def inverse_rows(rows):
    n = len(rows)
    aug = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for p in range(n):
        k = next((k for k in range(p, n) if (aug[k] >> p) & 1), None)
        need(k is not None, "singular frame-508 matrix")
        aug[p], aug[k] = aug[k], aug[p]
        for k in range(n):
            if k != p and ((aug[k] >> p) & 1):
                aug[k] ^= aug[p]
    need([row & ((1 << n) - 1) for row in aug] == [1 << i for i in range(n)],
         "inverse reduction")
    return [row >> n for row in aug]


def inverse_column_support(rows, column):
    vector = inverse_column_vector(rows, column)
    return [i for i in range(len(rows)) if (vector >> i) & 1]


def inverse_column_vector(rows, column):
    inv = inverse_rows(rows)
    return sum(((row >> column) & 1) << i for i, row in enumerate(inv))


def cut_obstruction(support, low_wires, proper_frame):
    """A proper low-phase cannot produce an inverse-column coordinate outside it."""
    return bool(proper_frame and not set(support) <= set(low_wires))


def load_source_word():
    # The upstream package verifies every content pin before we reconstruct its
    # exact composed word. We use only its deterministic block splice, not its
    # separate search.
    builder = runpy.run_path(str(R439 / "build.py"))
    builder["pins"](ROOT)
    helper_star = builder["load"](STAR / "candidate.json.gz")
    programs = builder["programs"](ROOT)
    return builder["splice"](helper_star, programs)


def verify():
    task = json.loads((HERE / "TASK.json").read_text(encoding="utf-8"))
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    need(pins["base_commit"] == task["base_commit"], "package base pin")
    for item in pins["files"]:
        raw = (ROOT / item["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"],
             "source pin: " + item["path"])

    selected_sha = hashlib.sha256((ROOT / "certificates/selected-result.json").read_bytes()).hexdigest()
    catalog_sha = hashlib.sha256((ROOT / "docs/research/agent-task-catalog.json").read_bytes()).hexdigest()
    need(selected_sha == task["selected_record_sha256"], "selected-record pin")
    need(catalog_sha == task["catalog_sha256"], "task-catalogue pin")

    word = load_source_word()
    barrier = json.loads((PREDECESSOR / "CERTIFICATE.json").read_text(encoding="utf-8"))
    expected = next(block for block in barrier["blocks"] if block["frame"] == 508)
    ops = [gate for gate in word["B"] if gate[0] == 508]
    positions = [i for i, gate in enumerate(word["B"]) if gate[0] == 508]
    need(positions == list(range(positions[0], positions[-1] + 1)), "frame-508 block is contiguous")
    need(ops and all(gate[0] == 508 for gate in ops), "frame-508 block operations")
    registers = sorted({wire for _, dest, sources in ops for wire in (dest, *sources)})
    need(registers == expected["registers"], "frame-508 wire alphabet")

    local = {wire: i for i, wire in enumerate(registers)}
    rows = [1 << i for i in range(len(registers))]
    for _, dest, sources in ops:
        for source in sources:
            rows[local[dest]] ^= rows[local[source]]
    need(rows == expected["matrix_rows"], "reconstructed exact frame-508 matrix")

    entry = list(word["start"])
    for section in "DA":
        for frame, dest, sources in word[section]:
            for wire in (dest, *sources):
                entry[wire] = frame
    first = positions[0]
    for frame, dest, sources in word["B"][:first]:
        for wire in (dest, *sources):
            entry[wire] = frame
    need([entry[wire] for wire in registers] ==
         [item["entry_frame"] for item in expected["dependencies"]],
         "frame-508 entry-frame witnesses")

    lines = word["lines"]
    frames = word["frames"]
    frame_rank = lambda frame: len(span_basis(lines, frames[frame]))
    full_rank = frame_rank(508)
    need(full_rank == 4, "frame 508 has exact rank four")
    source = 19
    source_i = local[source]
    need(rows[source_i] == 1 << source_i, "source 19 output row is identity")
    inverse_support_indices = inverse_column_support(rows, source_i)
    inverse_support = [registers[i] for i in inverse_support_indices]
    need(inverse_support == [19, 35, 66, 89, 97, 466], "exact inverse-column support")
    inverse_vector = inverse_column_vector(rows, source_i)
    image = sum(((row & inverse_vector).bit_count() & 1) << i for i, row in enumerate(rows))
    need(image == 1 << source_i, "inverse-column endpoint")

    dependencies = []
    for i, wire in enumerate(registers):
        required = set(frames[entry[wire]])
        for j, other in enumerate(registers):
            if (rows[i] >> j) & 1:
                required.update(frames[entry[other]])
        root_basis = span_basis(lines, required)
        entry_rank = frame_rank(entry[wire])
        dependencies.append({
            "register": wire,
            "entry_frame": entry[wire],
            "entry_rank": entry_rank,
            "required_exit_rank": len(root_basis),
            "required_root_basis": root_basis,
        })
    need(all(item["required_exit_rank"] == 4 for item in dependencies if item["register"] != source),
         "all ten non-source exits forced to frame 508")
    source_dep = next(item for item in dependencies if item["register"] == source)
    full_donor = 466
    donor_dep = next(item for item in dependencies if item["register"] == full_donor)
    need(source_dep["entry_rank"] == 2 and source_dep["required_exit_rank"] == 2,
         "source 19 is the unique dependency-span exception")
    need(donor_dep["entry_frame"] == 508 and donor_dep["entry_rank"] == 4,
         "inverse-column donor 466 enters at full frame 508")
    maximal_proper_low_set = set(registers) - {full_donor}
    need(cut_obstruction(inverse_support, maximal_proper_low_set, True),
         "inverse-column cut excludes every proper low-wire set")

    # Baseline has one direct climb per wire to F, so this local histogram is
    # the concavity-minimal cost once the cut lemma forces source 19 to F too.
    climb_histogram = Counter(4 - item["entry_rank"] for item in dependencies)
    climb_histogram.pop(0, None)
    need(dict(sorted(climb_histogram.items())) == {2: 6, 3: 2},
         "frame-508 direct-climb histogram")

    certificate = {
        "status": "PASS_R439_FRAME508_INVERSE_CUT",
        "frame": 508,
        "frame_rank": full_rank,
        "registers": registers,
        "matrix_rows": rows,
        "inverse_column_source_register": source,
        "inverse_column_vector_bits_in_register_order": inverse_vector,
        "inverse_column_support": inverse_support,
        "entry_dependencies": dependencies,
        "cut_witness": {
            "full_frame_donor": full_donor,
            "donor_entry_frame": donor_dep["entry_frame"],
            "donor_not_in_any_proper_subframe": True,
            "source_forced_to_full_frame": True,
            "maximal_proper_low_wire_set": sorted(maximal_proper_low_set),
        },
        "baseline_block_climb_histogram": dict(sorted(climb_histogram.items())),
        "moment_domain": "q = 1-a, 0 < a < 1",
        "moment_conclusion": "every path to the forced rank-four exit costs at least the existing direct climb",
        "scope": [
            "the exact 11-wire frame-508 matrix",
            "monotone frame changes within the original rank-four frame",
            "no extra wires, COPY/ERASE, or cross-block operations",
        ],
        "not_established": [
            "a new selected kappa or supplier adoption",
            "frame 509 source 22",
            "extra wires, cross-block rewrites, or operations outside the block frame",
            "native/hosted admission, all-size realization, precision/tape, or analytic-transfer obligations",
        ],
    }
    out = HERE / "CERTIFICATE.json"
    out.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS_R439_FRAME508_INVERSE_CUT support=19,35,66,89,97,466 donor=466 full_frame=4 climbs=6x2+2x3 no_new_kappa")
    return certificate


if __name__ == "__main__":
    verify()
