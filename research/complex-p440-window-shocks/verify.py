#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact, bounded pivot-440 donor-window obstruction; no supplier admission.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
The suffix-response approach follows the credited PR1337/PR1297 lineage.
This module imports no predecessor executable code.
"""
import argparse
import collections
from fractions import Fraction as Q
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path

PKG = Path(__file__).resolve().parent
PIVOT = 440
MAX_READS = 4
WORD_SHA256 = "e8e6e78ff7422275c38324499e1f33fb2ecd30de9503aef2b8f1ee80d8c4df8e"
WORD_BLOB = "eacf8c773cb50637f93a762342b3b5f0853fe29a"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load_word(path):
    raw = Path(path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == WORD_SHA256, "word SHA256 mismatch")
    require(hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == WORD_BLOB,
            "word Git blob mismatch")
    return json.loads(gzip.decompress(raw))


def check_source_metadata(path):
    sources = json.loads(Path(path).read_text())
    require(sources["base_commit"] == "bce54fb3f895cbe5cd4c0eb477c3afeed100190f", "source base mismatch")
    inputs = sources.get("vendored_inputs", [])
    require(len(inputs) == 1, "vendored input inventory mismatch")
    record = inputs[0]
    expected = {
        "path": "inputs/BASE-WORD.json.gz", "sha256": WORD_SHA256, "git_blob": WORD_BLOB,
        "source_commit": "4abf710a7f0d2a46f522f3f13c15769d003f9495",
        "source_path": "research/global-mixed-four-cold-kernels/gauge44-word.json.gz",
        "copied_from_commit": "abd7384d9a5e35048723512ae70d970909ffd522",
        "copied_from_path": "research/frontier1305-kernel-census/inputs/BASE-WORD.json.gz",
    }
    require(record == expected, "vendored source identity mismatch")
    for name, expected_hash in sources["retained_notices"].items():
        require(hashlib.sha256((PKG / name).read_bytes()).hexdigest() == expected_hash, "notice mismatch")


def coefficient(gate):
    return Q(gate[3], gate[4]) if gate[0] == "add" else Q(gate[2], gate[3])


def plus(left, right, scalar=Q(1)):
    out = dict(left)
    for key, value in right.items():
        new = out.get(key, Q(0)) + scalar * value
        if new:
            out[key] = new
        else:
            out.pop(key, None)
    return out


def column(gates, source):
    values = {source: Q(1)}
    for gate in gates:
        target = gate[1]
        if gate[0] == "add":
            new = values.get(target, Q(0)) + coefficient(gate) * values.get(gate[2], Q(0))
        else:
            new = coefficient(gate) * values.get(target, Q(0))
        if new:
            values[target] = new
        else:
            values.pop(target, None)
    return values


def primitive(vector):
    """Canonical projective direction: primitive integers, first entry positive."""
    require(bool(vector), "zero has no projective direction")
    denominator = math.lcm(*(value.denominator for value in vector.values()))
    entries = [(key, int(value * denominator)) for key, value in sorted(vector.items())]
    divisor = math.gcd(*(value for _, value in entries))
    if entries[0][1] < 0:
        divisor = -divisor
    return tuple((key, value // divisor) for key, value in entries)


def encoded(vector):
    return [[key, str(value)] for key, value in sorted(vector.items())]


def support(vector):
    return sum(1 << key for key in vector)


def in_span(columns, target):
    """Rational RREF, including singular columns and zero coefficients."""
    width = len(columns)
    keys = sorted(set(target).union(*(set(c) for c in columns)))
    rows = [[Q(c.get(k, 0)) for c in columns] + [Q(target.get(k, 0))] for k in keys]
    pivot_row = 0
    for j in range(width):
        other = next((i for i in range(pivot_row, len(rows)) if rows[i][j]), None)
        if other is None:
            continue
        rows[pivot_row], rows[other] = rows[other], rows[pivot_row]
        scale = rows[pivot_row][j]
        rows[pivot_row] = [v / scale for v in rows[pivot_row]]
        for i in range(len(rows)):
            if i != pivot_row and rows[i][j]:
                scale = rows[i][j]
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
    return not any(not any(row[:width]) and row[width] for row in rows)


def enumerate_windows(word, pivot=PIVOT, max_reads=MAX_READS):
    B = word["B"]
    require(not any(g[1] == pivot for g in B), "pivot is written in B")
    deleted = {i for i, g in enumerate(B) if g[0] == "add" and g[2] == pivot}
    tail = [word["cleanup"][i] for i, _ in word["early_cleanup"]]
    sequence = B + tail
    reduced = [g for i, g in enumerate(sequence) if i not in deleted]
    error = plus(column(sequence, pivot), column(reduced, pivot), -1)
    columns = {}
    responses = {}
    for i in range(len(sequence) - 1, -1, -1):
        if i in deleted:
            continue
        gate = sequence[i]
        target, amount = gate[1], coefficient(gate)
        output = columns.get(target, {target: Q(1)})
        if gate[0] == "add":
            responses[i] = {k: amount * v for k, v in output.items()}
            source = gate[2]
            columns[source] = plus(columns.get(source, {source: Q(1)}), output, amount)
        else:
            columns[target] = {k: amount * v for k, v in output.items()}
    segments = []
    pending = collections.defaultdict(list)
    for i, gate in enumerate(B):
        if i in deleted:
            continue
        target = gate[1]
        if pending[target]:
            segments.append((target, pending.pop(target)))
        if gate[0] == "add" and gate[2] != pivot and gate[2] != target:
            pending[gate[2]].append(i)
    segments.extend(sorted(pending.items()))
    windows = []
    zero_windows = 0
    for donor, reads in segments:
        for j, start in enumerate(reads):
            response = {}
            for offset, stop in enumerate(reads[j:j + max_reads], start=1):
                response = plus(response, responses[stop])
                window = {"donor": donor, "start": start, "end": stop + 1,
                          "reads": reads[j:j + offset]}
                if response:
                    windows.append((window, dict(response)))
                else:
                    zero_windows += 1
    windows.sort(key=lambda x: (x[0]["donor"], x[0]["start"], x[0]["end"]))
    return error, windows, sorted(deleted), zero_windows


def exclude_three(error, directions, anchor=588):
    """Cover every span of at most three directions, without coefficient bounds."""
    vectors = [dict(v) for v in directions]
    masks = [support(v) for v in vectors]
    marked = [i for i, v in enumerate(vectors) if anchor in v]
    unmarked = [i for i, v in enumerate(vectors) if anchor not in v]
    require(error.get(anchor) != 0, "anchor must occur in the error")
    require(bool(unmarked), "padding direction absent")
    counts = collections.Counter()
    per_anchor = []
    for i in marked:
        amount = error[anchor] / Q(vectors[i][anchor])
        residual = plus(error, vectors[i], -amount)
        require(bool(residual), "one-window repair exists")
        bitmask = support(residual)
        row = min(residual, key=lambda k: (sum(k in vectors[j] for j in unmarked), k))
        active = [j for j in unmarked if row in vectors[j]]
        local = collections.Counter()
        # Some remaining direction must hit this row. Repeated j=k and zero
        # coefficients also cover every one- and two-direction repair.
        for j in active:
            for k in unmarked:
                if row in vectors[k] and k < j:
                    continue
                counts["one_anchor_pairs"] += 1
                local["pairs"] += 1
                if bitmask & ~(masks[j] | masks[k]):
                    counts["support_rejections"] += 1
                    local["support_rejections"] += 1
                    continue
                counts["rational_rejections"] += 1
                local["rational_rejections"] += 1
                require(not in_span([vectors[j], vectors[k]], residual),
                        "three-window repair exists (one anchor)")
        per_anchor.append({"direction": [list(e) for e in directions[i]],
                           "forced_coefficient": str(amount), "residual": encoded(residual),
                           "screen_row": row, "active_directions": len(active),
                           "counts": dict(sorted(local.items()))})
    for i, j in itertools.combinations(marked, 2):
        for k in unmarked:
            counts["two_anchor_triples"] += 1
            if support(error) & ~(masks[i] | masks[j] | masks[k]):
                counts["support_rejections"] += 1
                continue
            counts["rational_rejections"] += 1
            require(not in_span([vectors[i], vectors[j], vectors[k]], error),
                    "three-window repair exists (two anchors)")
    for ids in itertools.combinations(marked, 3):
        counts["three_anchor_triples"] += 1
        counts["rational_rejections"] += 1
        require(not in_span([vectors[i] for i in ids], error),
                "three-window repair exists (three anchors)")
    return {"anchor_register": anchor, "anchor_directions": len(marked),
            "other_directions": len(unmarked), "counts": dict(sorted(counts.items())),
            "one_anchor_cases": per_anchor, "repairs_with_at_most_three_windows": 0}


def positive_windows():
    # Four algebraic shocks, not a physically admitted supplier circuit.
    return [
        {"donor": 518, "start": 41, "end": 42, "reads": [41], "coefficient": "-1"},
        {"donor": 641, "start": 160, "end": 161, "reads": [160], "coefficient": "4"},
        {"donor": 42, "start": 493, "end": 494, "reads": [493], "coefficient": "1"},
        {"donor": 106, "start": 527, "end": 528, "reads": [527], "coefficient": "1"},
    ]


def compute(word):
    error, windows, deleted, zero = enumerate_windows(word)
    require(deleted == [892, 928, 1192], "unexpected pivot early reads")
    directions = sorted({primitive(v) for _, v in windows})
    encoded_windows = [{**w, "response": encoded(v)} for w, v in windows]
    census = exclude_three(error, directions)
    by = {(w["donor"], w["start"], w["end"]): (w, v) for w, v in windows}
    total = {}
    for shock in positive_windows():
        key = (shock["donor"], shock["start"], shock["end"])
        require(key in by and shock["reads"] == by[key][0]["reads"], "invalid positive window")
        total = plus(total, by[key][1], Q(shock["coefficient"]))
    require(total == error, "four-window positive control does not repair the map")
    return {
        "schema_version": 1, "status": "EXACT_SCOPED_THREE_WINDOW_OBSTRUCTION",
        "source_sha256": WORD_SHA256, "pivot": PIVOT, "max_consecutive_reads": MAX_READS,
        "coefficient_domain": "arbitrary rational (equivalently complex for these rational linear systems)",
        "original_B_gates": len(word["B"]), "early_cleanup_gates": len(word["early_cleanup"]),
        "deleted_B_indices": deleted, "deletion_error": encoded(error),
        "nonzero_windows": len(windows), "zero_windows": zero,
        "projective_directions": len(directions), "directions_sha256": digest(directions),
        "windows_sha256": digest(encoded_windows), "census": census,
        "positive_control": {"windows": positive_windows(), "opening_and_closing_ADDs": 8,
                             "net_B_ADD_change": 5, "B_gates_after_edit": len(word["B"]) + 5,
                             "scope": "algebraic map identity only; frames and paid moment unverified"},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--word", type=Path, default=PKG / "inputs/BASE-WORD.json.gz")
    ap.add_argument("--certificate", type=Path, default=PKG / "CERTIFICATE.json")
    ap.add_argument("--sources", type=Path, default=PKG / "SOURCES.json")
    ap.add_argument("--write-certificate", action="store_true")
    args = ap.parse_args()
    check_source_metadata(args.sources)
    certificate = compute(load_word(args.word))
    if args.write_certificate:
        args.certificate.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    else:
        require(certificate == json.loads(args.certificate.read_text()), "saved certificate mismatch")
    print("PASS_P440_THREE_WINDOW_OBSTRUCTION windows=%s directions=%s arbitrary_rational=yes four_window_identity=yes no_new_kappa"
          % (certificate["nonzero_windows"], certificate["projective_directions"]))


if __name__ == "__main__":
    main()
