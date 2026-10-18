#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Weyl roots, set-based frames and row-dual enumeration; no primary imports."""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def indices(mask):
    return [i for i in range(120) if mask & (1 << i)]


def check_roots(lines):
    simple = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0)]
    for i in range(6):
        root = [0] * 8
        root[i], root[i+1] = -2, 2
        simple.append(tuple(root))
    roots, pending = {simple[0]}, [simple[0]]
    while pending:
        root = pending.pop()
        for normal in simple:
            dot = sum(x*y for x, y in zip(root, normal))
            require(dot % 4 == 0, "nonintegral Weyl reflection")
            reflected = tuple(x-(dot//4)*y for x, y in zip(root, normal))
            if reflected not in roots:
                roots.add(reflected)
                pending.append(reflected)
    advertised = {tuple(r) for r in lines} | {tuple(-x for x in r) for r in lines}
    require(len(roots) == 240 and roots == advertised, "Weyl root model disagreement")


def row_coordinates(rows):
    pivots, dimension = {}, 0
    for value in rows:
        coefficients = 0
        while value:
            pivot = value.bit_length()-1
            if pivot in pivots:
                value ^= pivots[pivot][0]
                coefficients ^= pivots[pivot][1]
            else:
                pivots[pivot] = (value, coefficients ^ (1 << dimension))
                dimension += 1
                break
    coordinates = []
    for value in rows:
        coefficients = 0
        while value:
            pivot = value.bit_length()-1
            require(pivot in pivots, "row outside selected span")
            value ^= pivots[pivot][0]
            coefficients ^= pivots[pivot][1]
        coordinates.append(coefficients)
    return dimension, coordinates


def independent_geometry(data):
    lines, live = data["lines"], data["live"]
    check_roots(lines)
    require(len(live) == 112 and set(live) == set(range(120))-set(data["punctured_frame"]),
            "invalid puncture")
    puncture_roots = []
    for k in range(4):
        for sign in (1, -1):
            root = [0] * 8
            root[2*k], root[2*k+1] = 2, 2*sign
            puncture_roots.append(root)
    require([lines[i] for i in data["punctured_frame"]] == puncture_roots, "wrong punctured frame")
    ip = [[sum(x*y for x, y in zip(a, b))//4 for b in lines] for a in lines]
    n = [sum(((v+1) % 2) << j for j, v in enumerate(row)) for row in ip]
    supports = []
    for a in range(120):
        star = sum(1 << i for i in live if ip[a][i] != 0)
        supports.extend((star, star & ~(1 << a)))
    orthogonal = [{j for j in live if j != i and ip[i][j] == 0} for i in range(120)]
    frames = []

    def complete(prefix, candidates):
        if len(prefix) == 8:
            frames.append(tuple(prefix))
            return
        if len(candidates) < 8-len(prefix):
            return
        candidates = set(candidates)
        while candidates:
            i = min(candidates)
            candidates.remove(i)
            complete(prefix+[i], candidates.intersection(orthogonal[i]))
    complete([], set(live))
    require(len(frames) == 1260, "independent frame census changed")
    through = Counter(i for frame in frames for i in frame)
    require(set(through) == set(live) and set(through.values()) == {90}, "independent incidence failed")
    coframe = {pair for frame in frames for pair in itertools.combinations(frame, 2)}
    require(all((i, j) in coframe for i, j in itertools.combinations(live, 2)
                if ip[i][j] == 0), "independent orthogonal pair has no live frame")
    return ip, n, supports, frames


def check_cover(data, n, supports, frames, cover):
    terms = cover["terms"]
    require(len(terms) == 10, "wrong cover term count")
    counts = [0] * len(frames)
    diagonal = {i: 0 for i in data["live"]}
    for a, b, cut_hex in terms:
        require(type(a) is int and type(b) is int and 0 <= a < 240 and 0 <= b < 240,
                "invalid cover tags")
        left, right = supports[a], supports[b]
        ids = indices(left)
        rows = [n[i] & right for i in ids]
        dimension, coords = row_coordinates(rows)
        require(dimension == 7, "cover parent not rank seven")
        cut = int(cut_hex, 16)
        codes = {sum(((c & dual).bit_count() % 2) << i for i, c in zip(ids, coords))
                 for dual in range(1, 128)}
        require(cut in codes, "cover cut not a dual-functional zero set")
        kept = left ^ cut
        dimension, _ = row_coordinates([n[i] & right for i in indices(kept)])
        require(dimension == 6, "cover term not rank six")
        for k, frame in enumerate(frames):
            counts[k] += (any(kept & (1 << i) for i in frame) and
                          any(right & (1 << i) for i in frame))
        for i in diagonal:
            diagonal[i] += bool(kept & right & (1 << i))
    require(min(counts) >= 8, "independent cover fails frame demand")
    actual = dict(terms=10, copy_bill=60, minimum_hits=min(counts),
                  hit_histogram=dict(sorted(Counter(counts).items())),
                  frame_counts_sha256=hashlib.sha256(bytes(counts)).hexdigest())
    actual_diagonal = dict(minimum=min(diagonal.values()),
                           histogram=dict(sorted(Counter(diagonal.values()).items())))
    require(json.loads(json.dumps(actual)) == cover["exact_check"], "cover counts disagree")
    require(json.loads(json.dumps(actual_diagonal)) == cover["diagonal_support_coverage"],
            "diagonal counts disagree")


def main():
    try:
        sources = json.loads((HERE / "SOURCES.json").read_text())
        for source in sources["archives"]:
            path = Path(source["local_path"])
            require(not path.is_absolute() and ".." not in path.parts, "unsafe archive path")
            require(hashlib.sha256((HERE/path).read_bytes()).hexdigest() == source["sha256"], "archive drift")
        data = json.loads((HERE / "inputs/PR1323-MODEL.json").read_text())
        ip, n, supports, frames = independent_geometry(data)
        frame_masks = [sum(1 << i for i in f) for f in frames]
        cache, row_masks = {}, set()

        def hits(mask):
            if mask not in cache:
                cache[mask] = sum(1 << i for i, f in enumerate(frame_masks) if mask & f)
            return cache[mask]
        parent_ranks, cut_ranks, hit_counts = Counter(), Counter(), Counter()
        table = []
        for a, left in enumerate(supports):
            ids = indices(left)
            for b, right in enumerate(supports):
                rows = [n[i] & right for i in ids]
                dimension, coordinates = row_coordinates(rows)
                parent_ranks[dimension] += 1
                if dimension != 7:
                    continue
                require((a % 2 or a//2 in data["punctured_frame"]) and
                        (b % 2 or b//2 in data["punctured_frame"]) and
                        ip[a//2][b//2] % 2, "independent cheap-parent classification failed")
                words = sorted(sum(((c & dual).bit_count() % 2) << i
                                   for i, c in zip(ids, coordinates)) for dual in range(1, 128))
                require(len(words) == len(set(words)) == 127 and words[0] > 0, "incomplete dual code")
                values = []
                right_hits = hits(right)
                for word in words:
                    kept = left ^ word
                    dimension, _ = row_coordinates([row for i, row in zip(ids, rows)
                                                     if not word & (1 << i)])
                    require(dimension == 6, "independent maximal slice not rank six")
                    cut_ranks[dimension] += 1
                    row_masks.add(kept)
                    met = (hits(kept) & right_hits).bit_count()
                    hit_counts[met] += 1
                    values.append((word, met))
                maximum = max(h for _, h in values)
                choices = [word for word, h in values if h == maximum]
                cut = min(choices, key=lambda w: (w.bit_count(), w))
                digest = hashlib.sha256("".join(f"{w:x}\t{h}\n" for w, h in values).encode()).hexdigest()
                table.append([a, b, maximum, format(cut, "x"), cut.bit_count(), len(choices), digest])
        recorded = [json.loads(line) for line in (HERE / "generated/COVERAGE.jsonl").read_text().splitlines()]
        require(table == recorded, "independent complete coverage table disagreement")
        lookup = {(row[0], row[1]): row for row in table}
        one_axis = Counter(row[2] for row in table)
        joint = Counter(max(row[2], lookup[row[1], row[0]][2]) for row in table)
        maximum = max(one_axis)
        selected = min((row for row in table if row[2] == maximum),
                       key=lambda row: ((row[0]-20) % 240, (row[1]-20) % 240, int(row[3], 16)))
        a, b, h, cut_hex = selected[:4]
        table_raw = "".join(json.dumps(row, separators=(",", ":"))+"\n" for row in table).encode()
        certificate = dict(
            status="PASS_COMPLETE_RANK6_FRAME_CENSUS", frames=1260, required_frame_hits=10080,
            rank7_tagged_parents=len(table), codeword_cases=sum(cut_ranks.values()),
            distinct_row_slice_supports=len(row_masks), parent_rank_histogram=dict(sorted(parent_ranks.items())),
            slice_rank_histogram=dict(cut_ranks), slice_frame_hit_histogram=dict(sorted(hit_counts.items())),
            one_axis_parent_maximum_histogram=dict(sorted(one_axis.items())),
            arbitrary_joint_parent_maximum_histogram=dict(sorted(joint.items())),
            maximum_frame_hits=maximum, averaged_frame_bound=str(Fraction(10080*6, maximum)),
            all_rank6_term_count_lower_bound=10,
            witness=dict(left_tag=a, right_tag=b, row_cut_hex=cut_hex,
                         retained_row_ids=indices(supports[a] ^ int(cut_hex, 16)),
                         column_ids=indices(supports[b]), copy_rank=6, frame_hits=h),
            table_sha256=hashlib.sha256(table_raw).hexdigest())
        require(json.loads(json.dumps(certificate)) == json.loads((HERE / "generated/CERTIFICATE.json").read_text()),
                "independent full certificate disagreement")
        check_cover(data, n, supports, frames, json.loads((HERE / "COVERING.json").read_text()))
        print("PASS_INDEPENDENT_P112_RANK6_COVERAGE atoms=7616 slices=967232 max_hits=1120 cover_bill=60")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("REJECT_INDEPENDENT_P112_RANK6_COVERAGE: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
