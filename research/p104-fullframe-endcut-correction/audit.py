#!/usr/bin/env python3
"""Reconstruct and price one P104 full-frame end-cut correction word."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WITNESS = ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
CHANNEL_RESULT = ROOT / "research/p104-native-channel/inputs/LOWRANK-RESULT.json"
FLAG_CERTIFICATE = ROOT / "research/p104-joint-unit-flags/CERTIFICATE.json"
SOURCES = json.loads((PACKAGE / "SOURCES.json").read_text())
FULL = [1 << i for i in range(9)]

PINNED_SHA256 = {
    WITNESS: "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    CHANNEL_RESULT: "7143ec7780f6f38a8c294df8009c3621936b281d05ae79946ce22f581b73d1b1",
    FLAG_CERTIFICATE: "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
    ROOT / "research/p104-native-channel/PROOF.md":
        "5d743145d389ffdfaffc66096fa7e32c7155b18f73d74755403151d0435bb94c",
}
INPUT_NAME = re.compile(r"([A-Z]+)([0-9]+)\Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frame_rank(vectors: list[int]) -> int:
    pivots: dict[int, int] = {}
    for value in vectors:
        x = value
        while x:
            pivot = x.bit_length() - 1
            if pivot in pivots:
                x ^= pivots[pivot]
            else:
                pivots[pivot] = x
                break
    return len(pivots)


def vector_add(row: dict[tuple[str, int], Fraction],
               source: dict[tuple[str, int], Fraction],
               coefficient: Fraction) -> dict[tuple[str, int], Fraction]:
    result = row.copy()
    for variable, value in source.items():
        updated = result.get(variable, Fraction(0)) + coefficient * value
        if updated:
            result[variable] = updated
        else:
            result.pop(variable, None)
    return result


def correction_rows(entries: list[list[object]]) -> list[dict]:
    terms: dict[int, list[list[object]]] = {target: [] for target in range(104)}
    for target, source, coefficient in entries:
        terms[int(target)].append([int(source), str(coefficient)])
    return [{"target": target, "terms": terms[target]} for target in range(104)]


def compact_array_document(document: dict, array_key: str) -> str:
    items = sorted(document.items())
    lines = ["{"]
    for index, (key, value) in enumerate(items):
        comma = "," if index < len(items) - 1 else ""
        if key == array_key:
            lines.append(f"  {json.dumps(key)}: [")
            for row_index, row in enumerate(value):
                row_comma = "," if row_index < len(value) - 1 else ""
                lines.append("    " + json.dumps(
                    row, sort_keys=True, separators=(",", ":")
                ) + row_comma)
            lines.append("  ]" + comma)
        else:
            lines.append("  " + json.dumps(key) + ": " + json.dumps(
                value, sort_keys=True, separators=(",", ":")
            ) + comma)
    lines.append("}")
    return "\n".join(lines) + "\n"


def reconstruct_channel(witness: dict) -> tuple[dict, Counter]:
    rows: dict[str, dict[tuple[str, int], Fraction]] = {}
    for register in witness["initial_frames"]:
        match = INPUT_NAME.fullmatch(register)
        require(match is not None, f"Unrecognized initial register: {register}")
        kind, index = match.groups()
        rows[register] = {(kind, int(index)): Fraction(1)}

    counts: Counter = Counter()
    for event_index, event in enumerate(witness["program"]):
        operation = event[0]
        counts[operation] += 1
        if operation == "add":
            _, destination, source, raw_coefficient, _frame = event
            require(destination in rows, f"Missing destination row at event {event_index}")
            require(source in rows, f"Missing source row at event {event_index}")
            rows[destination] = vector_add(
                rows[destination], rows[source], Fraction(str(raw_coefficient))
            )
        elif operation == "transport":
            _, register, _old_frame, _new_frame, _rank = event
            require(register in rows, f"Missing transported row at event {event_index}")
        elif operation == "copy":
            _, destination, source, _frame = event
            require(source in rows, f"Missing copy source at event {event_index}")
            rows[destination] = rows[source].copy()
        elif operation in ("zero", "erase"):
            _, register, _frame = event
            rows[register] = {}
        else:
            raise ValueError(f"Unknown event at {event_index}: {event!r}")
    return rows, counts


def run() -> dict:
    for path, expected in PINNED_SHA256.items():
        require(path.is_file(), f"Missing pinned source: {path.relative_to(ROOT)}")
        require(sha256(path) == expected, f"Source hash mismatch: {path.relative_to(ROOT)}")

    selected = ROOT / "certificates/selected-result.json"
    selected_pin = next(
        row["sha256"] for row in SOURCES["files"]
        if row["path"] == "certificates/selected-result.json"
    )
    require(
        sha256(selected) == selected_pin,
        "Selected-result record hash mismatch",
    )
    require(SOURCES["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
            "Unexpected scientific base pin")

    witness = json.loads(WITNESS.read_text())
    channel_result = json.loads(CHANNEL_RESULT.read_text())
    flag_certificate = json.loads(FLAG_CERTIFICATE.read_text())

    # The named collection uses every endpoint twice across its 208 static flags.
    helpers = flag_certificate["helpers"]
    require(len(helpers) == 208, "Unexpected joint-flag record count")
    source_counts = Counter(record["source"] for record in helpers)
    target_counts = Counter(record["target"] for record in helpers)
    require(source_counts == Counter({i: 2 for i in range(104)}),
            "Joint flags do not use each source endpoint twice")
    require(target_counts == Counter({i: 2 for i in range(104)}),
            "Joint flags do not use each target endpoint twice")

    rows, event_counts = reconstruct_channel(witness)
    initial_registers = set(witness["initial_frames"])
    require(len(initial_registers) == 280, "Unexpected arbitrary-input register count")
    for register in sorted(initial_registers - {f"Y{i}" for i in range(104)}):
        match = INPUT_NAME.fullmatch(register)
        assert match is not None
        kind, index = match.groups()
        require(rows[register] == {(kind, int(index)): Fraction(1)},
                f"Channel fails to restore input {register}")
    require(rows.get("C") == {}, "Owned private copy C was not erased")

    for target in range(104):
        row = rows[f"Y{target}"]
        require(row.get(("Y", target)) == 1, f"Y{target} lost its dirty input")
        require(
            not any(kind == "Y" and index != target for kind, index in row),
            f"Y{target} depends on another dirty target",
        )
        require(
            not any(kind in ("G", "D", "Q") for kind, _index in row),
            f"Y{target} retains a dirty helper",
        )

    final_frames = witness["final_frames"]
    require(all(final_frames[f"X{i}"] == FULL for i in range(104)),
            "Source endpoints are not all in F9 at the cut")
    target_frames: dict[int, list[int]] = {}
    for target in range(104):
        frame = final_frames[f"Y{target}"]
        require(len(frame) == 8 and frame_rank(frame) == 8,
                f"Y{target} is not an eight-dimensional target frame")
        require(all(0 <= vector < 512 for vector in frame),
                f"Y{target} has a label outside F9")
        target_frames[target] = frame

    # The retained channel produces H=G/2. Its complement is I-H.
    entries: list[list[object]] = []
    coefficient_counts: Counter = Counter()
    row_degrees: Counter = Counter()
    column_degrees: Counter = Counter()
    for target in range(104):
        for source in range(104):
            channel_coefficient = rows[f"Y{target}"].get(("X", source), Fraction(0))
            correction = Fraction(target == source) - channel_coefficient
            if correction:
                require(correction in (Fraction(-1, 2), Fraction(1, 2)),
                        f"Unexpected correction coefficient at ({target},{source})")
                entries.append([target, source, str(correction)])
                coefficient_counts[str(correction)] += 1
                row_degrees[target] += 1
                column_degrees[source] += 1

    require(len(entries) == 4992, "Unexpected correction support size")
    require(coefficient_counts == Counter({"-1/2": 3376, "1/2": 1616}),
            "Unexpected correction coefficient histogram")
    require(set(row_degrees.values()) == {48}, "Correction is not 48-sparse per target")
    require(set(column_degrees.values()) == {48}, "Correction is not 48-sparse per source")

    # Compose the end-cut word. Each Y is raised once, receives its row's
    # additions while X remains unchanged, and is lowered to its exact frame.
    corrected_targets = {i: rows[f"Y{i}"].copy() for i in range(104)}
    for target, source, coefficient in entries:
        corrected_targets[target] = vector_add(
            corrected_targets[target], rows[f"X{source}"], Fraction(coefficient)
        )
    for target in range(104):
        require(
            corrected_targets[target]
            == {("Y", target): Fraction(1), ("X", target): Fraction(1)},
            f"End-cut composition is not Y{target} = y{target} + x{target}",
        )

    word_path = PACKAGE / "CORRECTION.json"
    word_document = {
        "format": "p104-fullframe-endcut-correction/v1",
        "base_commit": SOURCES["base_commit"],
        "flag_certificate_sha256": PINNED_SHA256[FLAG_CERTIFICATE],
        "channel_witness_sha256": PINNED_SHA256[WITNESS],
        "schedule": "target-major; raise Y_t to F9; apply each listed addition; lower Y_t",
        "full_source_frame": FULL,
        "target_output_frames": {str(i): target_frames[i] for i in range(104)},
        "transport_rank_per_target": 1,
        "rows": correction_rows(entries),
    }
    if word_path.exists() and word_path.stat().st_size:
        require(json.loads(word_path.read_text()) == word_document,
                "Retained CORRECTION.json differs from reconstructed word")

    base_profile = {str(k): int(v) for k, v in channel_result["paid_profile"].items()}
    require(sum(int(rank) * count for rank, count in base_profile.items())
            == int(channel_result["rank_mass"]), "Base profile does not sum to rank mass")
    combined_profile = base_profile.copy()
    combined_profile["1"] = combined_profile.get("1", 0) + 208
    combined_profile = dict(sorted(combined_profile.items(), key=lambda item: int(item[0])))
    base_events = len(witness["program"])
    correction_transports = 2 * 104
    correction_adds = len(entries)
    suffix_events = correction_transports + correction_adds
    frame_width = 104 * 9 + 104 * 8 + 1

    return {
        "status": "PASS_P104_FULLFRAME_ENDCUT_CORRECTION",
        "flag_collection": "PR #2981; 208 records; all 104 X and 104 Y endpoints used twice",
        "cut": "after the pinned 4058-event PR #1972 channel",
        "base_channel": {
            "events": base_events,
            "event_counts": dict(sorted(event_counts.items())),
            "rank_mass": int(channel_result["rank_mass"]),
            "paid_profile": base_profile,
        },
        "correction": {
            "identity": "C = I - G/2, derived from the exact channel output rows",
            "entries": len(entries),
            "coefficient_counts": dict(sorted(coefficient_counts.items())),
            "row_degree": 48,
            "column_degree": 48,
            "target_transports": 208,
            "transport_profile_delta": {"1": 208},
            "new_dirty_or_private_registers": 0,
            "exact_endpoint_map": "Y_t = y_t + x_t; X, G, D, Q unchanged",
        },
        "combined_finite_word": {
            "events": base_events + suffix_events,
            "scalar_adds": event_counts["add"] + correction_adds,
            "transports": event_counts["transport"] + correction_transports,
            "rank_mass": int(channel_result["rank_mass"]) + correction_transports,
            "paid_profile": combined_profile,
        },
        "chosen_suffix_occupancy": {
            "endpoint_frame_width_peak": frame_width,
            "events": suffix_events,
            "frame_coordinate_event_holds": frame_width * suffix_events,
            "convention": "all 104 sources and all 104 targets remain live; one target is promoted",
        },
        "scope_limit": "No recursive owner/idle tariff, precision, consumer, or all-size admission is proved.",
        "sources": {str(path.relative_to(ROOT)): PINNED_SHA256[path]
                    for path in PINNED_SHA256},
        "correction_sha256": hashlib.sha256(
            json.dumps(entries, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--emit-word", action="store_true",
        help="emit the exact correction schedule as JSON on stdout",
    )
    args = parser.parse_args()
    try:
        summary = run()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL_P104_FULLFRAME_ENDCUT_CORRECTION: {error}", file=sys.stderr)
        return 1

    if args.emit_word:
        witness = json.loads(WITNESS.read_text())
        rows, _ = reconstruct_channel(witness)
        entries = []
        for target in range(104):
            for source in range(104):
                coefficient = Fraction(target == source) - rows[f"Y{target}"].get(
                    ("X", source), Fraction(0)
                )
                if coefficient:
                    entries.append([target, source, str(coefficient)])
        document = {
            "format": "p104-fullframe-endcut-correction/v1",
            "base_commit": SOURCES["base_commit"],
            "flag_certificate_sha256": PINNED_SHA256[FLAG_CERTIFICATE],
            "channel_witness_sha256": PINNED_SHA256[WITNESS],
            "schedule": "target-major; raise Y_t to F9; apply each listed addition; lower Y_t",
            "full_source_frame": FULL,
            "target_output_frames": {
                str(i): witness["final_frames"][f"Y{i}"] for i in range(104)
            },
            "transport_rank_per_target": 1,
            "rows": correction_rows(entries),
        }
        sys.stdout.write(compact_array_document(document, "rows"))
    else:
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
