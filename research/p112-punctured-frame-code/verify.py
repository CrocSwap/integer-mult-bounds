#!/usr/bin/env python3
"""Coverage of the published bit-lane iterator on one P112 punctured frame code.

The half-split census is scan.c. It lists each half of an ordered kernel
basis by doubling and scores high XOR low by integer popcount. It does not
call low_weight_words. The engine is then compared with that set on this
basis alone.
"""

import json
import subprocess
import sys
import tempfile
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
from runpy import run_path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH = 112
FRAME_SIZE = 8
FRAME_COUNT = 1260
RANK = 76
DIMENSION = 36
DEGREE = 90
WEIGHT_BOUND = 16
SUPPORT_COUNT = 7
CODEWORDS = 1 << DIMENSION
SPLIT_POINTS = (18, 16)
ENGINE_BATCH = 20
PAIRS = ((0, 1), (2, 3), (4, 5), (6, 7))
MATCHINGS = (((0, 3), (1, 2)), ((0, 2), (1, 3)), ((0, 1), (2, 3)))
SPINOR_REPS = ((0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 1), (0, 1, 1, 0))
FREE_COORDINATES = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 25, 26,
    28, 30, 32, 34, 36, 40, 42, 48, 49, 50, 51, 52, 56, 58, 64, 80,
)
BASIS_WEIGHTS = (
    38, 34, 38, 30, 42, 34, 26, 30, 42, 30, 50, 30, 38, 42, 34, 22, 32, 32,
    32, 30, 32, 32, 30, 22, 24, 36, 20, 36, 28, 36, 28, 32, 32, 32, 32, 32,
)
LINE_SHA256 = "4db9ba14034f55b0b95d69451e809a0c3bf618473209ae3d47d4992e180d14ab"
SUPPORT_SHA256 = "ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3"
HISTOGRAM = {
    0: 1,
    16: 7,
    20: 336,
    22: 3584,
    24: 3752,
    26: 10752,
    28: 6864,
    30: 50176,
    32: 872613,
    34: 2243584,
    36: 5633600,
    38: 21482496,
    40: 123827424,
    42: 275960832,
    44: 878407488,
    46: 1531507712,
    48: 3797117779,
    50: 4774038528,
    52: 8574631520,
    54: 8427087872,
    56: 11893702896,
    58: 8427087872,
    60: 8574631520,
    62: 4774038528,
    64: 3797117779,
    66: 1531507712,
    68: 878407488,
    70: 275960832,
    72: 123827424,
    74: 21482496,
    76: 5633600,
    78: 2243584,
    80: 872613,
    82: 50176,
    84: 6864,
    86: 10752,
    88: 3752,
    90: 3584,
    92: 336,
    96: 7,
    112: 1,
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    checked = 0
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        digest = sha256(path.read_bytes()).hexdigest()
        need(digest == row["sha256"], "input hash mismatch: " + row["path"])
        checked += 1
    need(checked == 2, "two live inputs")
    return checked


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def canonical(vector):
    first = next(value for value in vector if value)
    return tuple(vector) if first > 0 else tuple(-value for value in vector)


def independent_lines():
    roots = []
    for i, j in combinations(range(8), 2):
        for si in (2, -2):
            for sj in (2, -2):
                root = [0] * 8
                root[i], root[j] = si, sj
                roots.append(tuple(root))
    for signs in product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(signs)
    need(len(roots) == len(set(roots)) == 240, "E8 root count")
    lines = []
    seen = set()
    for root in roots:
        key = max(root, tuple(-value for value in root))
        if key not in seen:
            seen.add(key)
            lines.append(root)
    need(len(lines) == 120, "E8 line count")
    puncture = []
    for pair in range(4):
        for sign in (1, -1):
            root = [0] * 8
            root[2 * pair] = 2
            root[2 * pair + 1] = 2 * sign
            puncture.append(lines.index(tuple(root)))
    return lines, tuple(puncture)


def pinned_model():
    model = run_path(
        str(ROOT / "research/p112-rank6-frame-coverage/engine.py"),
        run_name="p112_frame_model",
    )["model"]()
    lines = tuple(tuple(row) for row in model["lines"])
    puncture = tuple(model["punctured_frame"])
    live = tuple(model["live"])
    own_lines, own_puncture = independent_lines()
    need(lines == tuple(own_lines), "pinned lines differ from the E8 builder")
    need(puncture == own_puncture, "pinned puncture differs")
    need(live == tuple(i for i in range(120) if i not in set(puncture)), "live order")
    need(len(live) == WIDTH, "width")
    need(all(dot(lines[i], lines[i]) == 8 for i in range(120)), "norms")
    need(all(dot(lines[i], lines[j]) == 0 for i, j in combinations(puncture, 2)),
         "punctured frame is not orthogonal")
    roots = [list(lines[i]) for i in live]
    digest = sha256(json.dumps(roots).encode()).hexdigest()
    need(digest == LINE_SHA256, "live root-list hash")
    return lines, puncture, live


def orthogonal_frames(lines, live):
    adjacency = []
    for index in live:
        mask = 0
        for bit, other in enumerate(live):
            if index != other and dot(lines[index], lines[other]) == 0:
                mask |= 1 << bit
        adjacency.append(mask)
    frames = []
    stack = [((), (1 << WIDTH) - 1)]
    steps = 0
    while stack:
        steps += 1
        need(steps <= 5000000, "frame enumeration exceeded its state cap")
        chosen, candidates = stack.pop()
        if len(chosen) == FRAME_SIZE:
            frames.append(chosen)
            continue
        need_more = FRAME_SIZE - len(chosen)
        while candidates:
            if candidates.bit_count() < need_more:
                break
            bit = candidates & -candidates
            candidates ^= bit
            index = bit.bit_length() - 1
            stack.append((chosen + (index,), candidates & adjacency[index]))
    frames = tuple(sorted(frames))
    need(len(frames) == len(set(frames)) == FRAME_COUNT, "live 8-frame count")
    for frame in frames:
        need(all(dot(lines[live[i]], lines[live[j]]) == 0
                 for i, j in combinations(frame, 2)), "frame not orthogonal")
    return frames


def kernel(rows):
    pivots = {}
    for row in rows:
        reduced = row
        while reduced:
            pivot = reduced.bit_length() - 1
            if pivot in pivots:
                reduced ^= pivots[pivot]
            else:
                pivots[pivot] = reduced
                break
    order = sorted(pivots)
    for pivot in order:
        row = pivots[pivot]
        for other in order:
            if other != pivot and (pivots[other] >> pivot) & 1:
                pivots[other] ^= row
    free = tuple(j for j in range(WIDTH) if j not in pivots)
    need(len(pivots) == RANK and free == FREE_COORDINATES, "P112 frame-code rank")
    basis = []
    for coordinate in free:
        vector = 1 << coordinate
        for pivot in order:
            if (pivots[pivot] & vector).bit_count() % 2:
                vector |= 1 << pivot
        need(all((vector & row).bit_count() % 2 == 0 for row in rows),
             "a frame parity survives")
        basis.append(vector)
    weights = tuple(vector.bit_count() for vector in basis)
    need(weights == BASIS_WEIGHTS, "basis weights changed")
    for index, vector in enumerate(basis):
        pattern = tuple((vector >> place) & 1 for place in free)
        identity = tuple(int(place == index) for place in range(DIMENSION))
        need(pattern == identity, "free coordinates are not a basis identity")
    return tuple(basis)


def relative_differences(root):
    return tuple(0 if root[2 * pair] == root[2 * pair + 1] else 1 for pair in range(4))


def partition_masks(lines, live):
    by_root = {lines[old]: bit for bit, old in enumerate(live)}

    def pair_mask(matching):
        mask = 0
        for left, right in matching:
            for i in PAIRS[left]:
                for j in PAIRS[right]:
                    for sign in (1, -1):
                        root = [0] * 8
                        root[i] = 2
                        root[j] = 2 * sign
                        mask |= 1 << by_root[canonical(root)]
        return mask

    spinors = [lines[old] for old in live if all(abs(value) == 1 for value in lines[old])]
    need(len(spinors) == 64, "spinor line count")

    def spin_mask(representative):
        patterns = {representative, tuple(1 - bit for bit in representative)}
        mask = 0
        for root in spinors:
            if relative_differences(root) in patterns:
                mask |= 1 << by_root[root]
        return mask

    masks = tuple(pair_mask(item) for item in MATCHINGS) + tuple(
        spin_mask(item) for item in SPINOR_REPS
    )
    covered = 0
    for mask in masks:
        need(mask.bit_count() == WEIGHT_BOUND, "partition block weight")
        need(covered & mask == 0, "partition blocks meet")
        covered |= mask
    need(covered == (1 << WIDTH) - 1, "partition misses a live line")
    return masks


def in_code(mask, rows):
    return all((mask & row).bit_count() % 2 == 0 for row in rows)


def compile_scan(work):
    binary = work / "scan"
    subprocess.run(
        ["gcc", "-O3", "-std=c11", "-pthread", "-Wall", "-Werror",
         "-o", str(binary), str(HERE / "scan.c")],
        check=True, cwd=work, timeout=60,
    )
    return binary


def run_split(binary, basis, split, work):
    path = work / ("basis-%d.txt" % split)
    path.write_text("".join("%028x\n" % vector for vector in basis), encoding="ascii")
    completed = subprocess.run(
        [str(binary), str(path), str(split)],
        check=True, capture_output=True, text=True, timeout=180,
    )
    need(completed.stderr == "", "scan wrote to stderr")
    histogram = {}
    found = []
    seen = None
    reported = None
    weights = []
    for line in completed.stdout.splitlines():
        kind, *rest = line.split()
        if kind == "SPLIT":
            reported = int(rest[0])
        elif kind == "SEEN":
            seen = int(rest[0])
        elif kind == "HIST":
            histogram[int(rest[0])] = int(rest[1])
        elif kind == "LOW":
            found.append(int(rest[0], 16))
        elif kind == "BASIS":
            weights.append(int(rest[1]))
        else:
            raise ValueError("unexpected scan line")
    need(reported == split, "scan split")
    need(seen == CODEWORDS, "half-split missed a codeword")
    need(tuple(weights) == BASIS_WEIGHTS, "scan read a different basis")
    need(histogram == HISTOGRAM, "weight distribution changed at split " + str(split))
    need(sum(histogram.values()) == CODEWORDS, "histogram sum")
    for weight, count in histogram.items():
        need(histogram[WIDTH - weight] == count, "complement asymmetry")
    supports = set(found)
    need(len(found) == len(supports) == SUPPORT_COUNT, "support count")
    need(all(word.bit_count() == WEIGHT_BOUND for word in supports), "a lighter positive word")
    need(min(weight for weight in histogram if weight) == WEIGHT_BOUND, "minimum left 16")
    return supports


def engine_words(engine, basis, maximum, batch_bits):
    listed = list(engine(basis, WIDTH, maximum, batch_bits))
    need(len(listed) == len(set(listed)), "engine repeated a word")
    return set(listed)


def positive_words_have_weight(words, weight):
    return all(word.bit_count() == weight for word in words if word)


def check(mode):
    need(mode in ("all", "census", "engine"), "mode")
    do_census = mode in ("all", "census")
    do_engine = mode in ("all", "engine")
    authenticate()
    lines, puncture, live = pinned_model()
    frames = orthogonal_frames(lines, live)
    degree = [0] * WIDTH
    for frame in frames:
        for index in frame:
            degree[index] += 1
    need(set(degree) == {DEGREE}, "frame degree")
    rows = tuple(sum(1 << index for index in frame) for frame in frames)
    basis = kernel(rows)
    supports = partition_masks(lines, live)
    need(all(in_code(mask, rows) for mask in supports), "partition block leaves a frame")
    need(in_code((1 << WIDTH) - 1, rows), "all-ones leaves a frame")
    moved = (supports[0] ^ (1 << (supports[0].bit_length() - 1))
             ^ (1 << (supports[1].bit_length() - 1)))
    need(moved.bit_count() == WEIGHT_BOUND and moved not in supports,
         "moved block collapsed onto the partition")
    need(not in_code(moved, rows), "a moved block still meets every frame evenly")
    if do_census:
        with tempfile.TemporaryDirectory(prefix="p112-frame-") as directory:
            work = Path(directory)
            binary = compile_scan(work)
            scanned = []
            for split in SPLIT_POINTS:
                scanned.append(run_split(binary, basis, split, work))
        need(scanned[0] == scanned[1] == set(supports), "half-split changed the set")
    produced = None
    rejected = None
    if do_engine:
        engine = run_path(
            str(ROOT / "research/e7-bitsliced-exhaustion/binary.py"),
            run_name="p112_frame_lane_engine",
        )["low_weight_words"]
        produced = engine_words(engine, basis, WEIGHT_BOUND, ENGINE_BATCH)
        need(produced == set(supports) | {0}, "engine dropped or added a word")
        need(0 in produced and positive_words_have_weight(produced, WEIGHT_BOUND),
             "engine minimum")
        witness = supports[0]
        need(produced - {witness} != set(supports) | {0},
             "dropping one support still compared equal")
        lighter = witness ^ (1 << (witness.bit_length() - 1))
        need(lighter.bit_count() == WEIGHT_BOUND - 1,
             "clearing the top bit did not reduce weight")
        need(lighter not in produced and not in_code(lighter, rows),
             "a weight-fifteen word was already in the code")
        forged = set(produced)
        forged.add(lighter)
        need(not positive_words_have_weight(forged, WEIGHT_BOUND),
             "weight-fifteen injection was accepted")
        toy = engine_words(engine, (1, 2, 4), 1, 3)
        need(toy == {0, 1, 2, 4}, "toy weight-1 set")
        need(engine_words(engine, (1, 2, 4), 0, 3) == {0}, "toy bound change was ignored")
        try:
            list(engine((basis[0], basis[0]), WIDTH, WEIGHT_BOUND, 4))
        except ValueError:
            rejected = True
        else:
            rejected = False
        need(rejected, "a repeated generator was accepted")
    digest = sha256(json.dumps(sorted(supports)).encode()).hexdigest()
    need(digest == SUPPORT_SHA256, "support hash")
    return {
        "status": "PASS_P112_PUNCTURED_FRAME_CODE",
        "width": WIDTH,
        "frames": FRAME_COUNT,
        "frame_size": FRAME_SIZE,
        "frame_degree": DEGREE,
        "rank": RANK,
        "dimension": DIMENSION,
        "free_coordinates": list(FREE_COORDINATES),
        "puncture_indices": list(puncture),
        "minimum_positive_weight": WEIGHT_BOUND,
        "weight_at_most_16": SUPPORT_COUNT + 1,
        "minimum_supports": SUPPORT_COUNT,
        "distinct_codewords": CODEWORDS,
        "splits": list(SPLIT_POINTS) if do_census else [],
        "mode": mode,
        "engine_batch": ENGINE_BATCH if do_engine else None,
        "supports": sorted(supports),
        "supports_sha256": digest,
        "lines_sha256": LINE_SHA256,
        "dependent_generator_rejected": rejected,
        "e6_replayed": False,
        "d6_replayed": False,
        "intersection_engine_replayed": False,
        "timing_remeasured": False,
        "no_new_kappa": True,
    }


if __name__ == "__main__":
    selected = sys.argv[1] if len(sys.argv) > 1 else "all"
    result = check(selected)
    shown = dict(result)
    shown["engine_batch"] = (
        "20" if result["engine_batch"] == ENGINE_BATCH else "not-run"
    )
    shown["splits"] = (
        "18,16" if result["splits"] == [18, 16] else "not-run"
    )
    print(
        "PASS_P112_PUNCTURED_FRAME_CODE"
        " width={width}"
        " frames={frames}"
        " dimension={dimension}"
        " minimum={minimum_positive_weight}"
        " supports={minimum_supports}"
        " codewords={distinct_codewords}"
        " mode={mode}"
        " batches={engine_batch}"
        " splits={splits}"
        " e6_replayed=false"
        " d6_replayed=false"
        " no_new_kappa=true".format(**shown)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
