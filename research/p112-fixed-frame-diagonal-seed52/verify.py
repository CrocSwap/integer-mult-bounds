#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Exact support census for the ten fixed maximum-hit P112 frame masks."""
from collections import Counter
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
PINNED = {
    "PR1347-engine.py": "b59101564855a89de04f39fd28b0a853aa3c46ce0ce99951d93d7dd018543536",
    "PR1347-COVERING.json": "27d567a56500f857962ddc69a9baed691a945e5a2979a26632e84c23133f1c95",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_engine():
    path = INPUTS / "PR1347-engine.py"
    spec = importlib.util.spec_from_file_location("p112_pr1347_engine", path)
    require(spec is not None and spec.loader is not None, "cannot load pinned predecessor engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def enum_bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def candidate_record(group, a, b, cut, diagonal):
    return {"group": group, "left_tag": a, "right_tag": b,
            "cut_hex": format(cut, "x"), "diagonal_mask_hex": format(diagonal, "x")}


def make_result():
    for name, expected in PINNED.items():
        path = INPUTS / name
        require(path.is_file(), f"missing pinned input: {name}")
        require(sha256(path.read_bytes()) == expected, f"source pin mismatch: {name}")

    engine = load_engine()
    data = engine.model()
    _, normals, supports, frames = engine.geometry(data)
    frame_masks = [sum(1 << i for i in frame) for frame in frames]
    live = data["live"]
    live_mask = sum(1 << i for i in live)
    cover = json.loads((INPUTS / "PR1347-COVERING.json").read_text())
    require(len(cover["terms"]) == 10, "predecessor cover no longer has ten terms")

    hit_cache = {}

    def hits(support):
        if support not in hit_cache:
            hit_cache[support] = sum(1 << j for j, frame in enumerate(frame_masks)
                                     if frame & support)
        return hit_cache[support]

    patterns = []
    baseline_terms = []
    for term_index, (a, b, cut_hex) in enumerate(cover["terms"]):
        require(0 <= a < len(supports) and 0 <= b < len(supports),
                "predecessor cover has an out-of-range parent tag")
        cut = int(cut_hex, 16)
        left, right = supports[a], supports[b]
        require(engine.rank(normals, left, right) == 7,
                "predecessor cover parent rank changed")
        require(cut in engine.column_code(normals, left, right),
                "predecessor cover cut is outside its exact parent code")
        row = left ^ cut
        require(engine.rank(normals, row, right) == 6,
                "predecessor cover row rank changed")
        pattern = hits(row) & hits(right)
        require(pattern.bit_count() == 1120,
                "a fixed predecessor term is no longer maximum-hit")
        patterns.append(pattern)
        baseline_terms.append((term_index, a, b, cut, row, right))
    require(len(set(patterns)) == 10, "fixed cover does not have ten distinct frame masks")
    pattern_to_group = {pattern: i for i, pattern in enumerate(patterns)}
    groups = [[] for _ in patterns]

    rank7_pairs = 0
    code_words = 0
    for a, left in enumerate(supports):
        for b, right in enumerate(supports):
            if engine.rank(normals, left, right) != 7:
                continue
            rank7_pairs += 1
            words = engine.column_code(normals, left, right)
            require(len(words) == 127 and all(words), "rank-seven parent code changed")
            right_hits = hits(right)
            code_words += len(words)
            for cut in words:
                row = left ^ cut
                frame_hits = hits(row) & right_hits
                if frame_hits.bit_count() != 1120:
                    continue
                group = pattern_to_group.get(frame_hits)
                if group is None:
                    continue
                require(engine.rank(normals, row, right) == 6,
                        "maximum-hit candidate is not rank six")
                diagonal = row & right & live_mask
                groups[group].append((a, b, cut, diagonal))

    require(rank7_pairs == 7616, "rank-seven tagged-parent count changed")
    require(code_words == 967232, "complete parent/cut domain changed")
    require(all(groups), "a fixed frame-mask class has no enumerated representative")

    group_receipts = []
    all_candidate_union = 0
    canonical_candidates = []
    for group_index, records in enumerate(groups):
        records.sort(key=lambda row: (row[0], row[1], row[2]))
        masks = sorted(set(row[3] for row in records))
        maximal = [mask for mask in masks
                   if not any(mask != other and (mask & ~other) == 0 for other in masks)]
        group_union = 0
        for mask in masks:
            group_union |= mask
        all_candidate_union |= group_union
        group_receipts.append({
            "group": group_index,
            "frame_hit_mask_hex": format(patterns[group_index], "x"),
            "frame_hits": patterns[group_index].bit_count(),
            "support_triples": len(records),
            "unique_diagonal_masks": len(masks),
            "inclusion_maximal_diagonal_masks": len(maximal),
            "maximal_masks_hex": [format(mask, "x") for mask in maximal],
            "diagonal_union_hex": format(group_union, "x"),
            "diagonal_union_size": group_union.bit_count(),
            "candidates": [candidate_record(group_index, *row) for row in records],
        })
        canonical_candidates.extend(candidate_record(group_index, *row) for row in records)

    # Independent exact positive control: replay the predecessor's fixed ten terms.
    frame_counts = [0] * len(frames)
    diagonal_counts = Counter()
    baseline_candidate_ids = []
    for term_index, a, b, cut, row, right in baseline_terms:
        for j, frame in enumerate(frame_masks):
            frame_counts[j] += bool(row & frame and right & frame)
        diagonal = row & right & live_mask
        diagonal_counts.update(enum_bits(diagonal))
        group = pattern_to_group[hits(row) & hits(right)]
        match = candidate_record(group, a, b, cut, diagonal)
        require(match in group_receipts[group]["candidates"],
                "predecessor witness is absent from the complete representative census")
        baseline_candidate_ids.append(match)
    frame_histogram = dict(sorted(Counter(frame_counts).items()))
    frame_sha = sha256(bytes(frame_counts))
    require(min(frame_counts) >= 8, "predecessor positive control misses a frame demand")
    require({"terms": 10, "copy_bill": 60, "minimum_hits": min(frame_counts),
             "hit_histogram": {str(k): v for k, v in frame_histogram.items()},
             "frame_counts_sha256": frame_sha} == cover["exact_check"],
            "predecessor frame-count receipt changed")
    baseline_diag_histogram = dict(sorted(Counter(diagonal_counts[i] for i in live).items()))
    expected_diag_histogram = {int(k): v for k, v in
                               cover["diagonal_support_coverage"]["histogram"].items()}
    require(min(diagonal_counts[i] for i in live) == cover["diagonal_support_coverage"]["minimum"],
            "predecessor diagonal minimum changed")
    require(baseline_diag_histogram == expected_diag_histogram,
            "predecessor diagonal histogram changed")

    missing = [i for i in live if not (all_candidate_union & (1 << i))]
    candidate_bytes = json.dumps(canonical_candidates, sort_keys=True,
                                 separators=(",", ":")).encode()
    require(len(canonical_candidates) == sum(len(g) for g in groups),
            "canonical candidate serialization changed")

    # Negative controls exercise the exact membership and coverage gates.
    first = groups[0][0]
    invalid_zero_cut_rejected = 0 not in engine.column_code(
        normals, supports[first[0]], supports[first[1]])
    require(invalid_zero_cut_rejected, "zero-cut negative control unexpectedly admitted")
    wrong_pattern_rejected = patterns[0] != patterns[1]
    require(wrong_pattern_rejected and
            (hits(supports[first[0]] ^ first[2]) & hits(supports[first[1]])) != patterns[1],
            "cross-pattern negative control unexpectedly admitted")
    require(len(missing) > 0, "this package is intended to certify a support obstruction")
    require(all_candidate_union.bit_count() + len(missing) == len(live),
            "diagonal union complement is inconsistent")

    return {
        "schema_version": 1,
        "status": "PASS_EXACT_FIXED_FRAME_PATTERN_DIAGONAL_OBSTRUCTION",
        "base_commit": "bce54fb3f895cbe5cd4c0eb477c3afeed100190f",
        "predecessor": {
            "pr": 1347,
            "commit": "64fd5f9e91961dedc16118fcc7ad71ee82efe28f",
            "cover_sha256": PINNED["PR1347-COVERING.json"],
            "engine_sha256": PINNED["PR1347-engine.py"],
        },
        "domain": {
            "live_diagonal_positions": len(live),
            "live_line_ids": live,
            "rank_seven_tagged_parent_pairs": rank7_pairs,
            "nonzero_code_words_per_parent": 127,
            "complete_parent_cut_cases": code_words,
            "fixed_frame_mask_classes": len(patterns),
            "required_frame_hits_per_class": 1120,
            "matching_support_triples": len(canonical_candidates),
            "unique_diagonal_masks": sum(g["unique_diagonal_masks"] for g in group_receipts),
        },
        "groups": group_receipts,
        "candidate_table_sha256": sha256(candidate_bytes),
        "all_candidate_diagonal_union_hex": format(all_candidate_union, "x"),
        "all_candidate_diagonal_union_size": all_candidate_union.bit_count(),
        "uncovered_live_line_ids": missing,
        "uncovered_live_lines": [
            {"line_id": i, "root_representative": data["lines"][i]}
            for i in missing
        ],
        "fixed_cover_positive_control": {
            "minimum_frame_hits": min(frame_counts),
            "frame_hit_histogram": {str(k): v for k, v in frame_histogram.items()},
            "frame_counts_sha256": frame_sha,
            "minimum_diagonal_multiplicity": min(diagonal_counts[i] for i in live),
            "diagonal_multiplicity_histogram": {str(k): v for k, v in baseline_diag_histogram.items()},
            "candidate_terms_present": len(baseline_candidate_ids),
        },
        "controls": {
            "predecessor_cover_replays_frame_and_diagonal_receipts": True,
            "all_predecessor_terms_appear_in_full_census": True,
            "zero_cut_is_rejected_by_parent_code_membership": invalid_zero_cut_rejected,
            "cross_pattern_substitution_is_rejected": wrong_pattern_rejected,
            "missing_diagonal_is_absent_from_every_candidate": True,
        },
        "interpretation": (
            "The union of every maximum-hit rank-six support representative in these ten "
            "fixed frame-mask classes omits the listed live lines. Therefore no selection "
            "of one representative per class can cover all live diagonals. This is a "
            "support-only negative for this fixed ten-mask cover, not for other frame covers."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true",
                        help="regenerate RESULT.json after the exact replay")
    args = parser.parse_args()
    result = make_result()
    path = HERE / "RESULT.json"
    encoded = json.dumps(result, indent=2) + "\n"
    if args.write_result:
        path.write_text(encoded)
    else:
        require(path.is_file(), "RESULT.json is missing; use --write-result to generate it")
        require(path.read_text() == encoded, "RESULT.json does not match the exact replay")
    print("PASS_EXACT_FIXED_FRAME_PATTERN_DIAGONAL_OBSTRUCTION "
          f"patterns={result['domain']['fixed_frame_mask_classes']} "
          f"support_triples={result['domain']['matching_support_triples']} "
          f"diagonal_union={result['all_candidate_diagonal_union_size']}/"
          f"{result['domain']['live_diagonal_positions']} "
          f"uncovered={len(result['uncovered_live_line_ids'])}")


if __name__ == "__main__":
    main()
