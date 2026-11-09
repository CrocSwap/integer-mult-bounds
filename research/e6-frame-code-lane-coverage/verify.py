#!/usr/bin/env python3
"""Coverage of the published bit-lane iterator on the E6 4-frame code.

The half-split and the literal doubling census do not call low_weight_words.
They list the kernel by doubling and score words by integer popcount. The
engine is then compared with that set on this basis alone.
"""

import json
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
from runpy import run_path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH = 36
FRAME_SIZE = 4
DIMENSION = 7
RANK = 29
FRAME_COUNT = 135
WEIGHT_BOUND = 16
SUPPORT_COUNT = 63


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


def e8_roots():
    roots = []
    for i, j in combinations(range(8), 2):
        for si, sj in product((2, -2), repeat=2):
            root = [0] * 8
            root[i], root[j] = si, sj
            roots.append(tuple(root))
    for signs in product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(signs)
    need(len(roots) == len(set(roots)) == 240, "E8 root count")
    need(all(dot(root, root) == 8 for root in roots), "E8 norms")
    return set(roots)


def canonical(vector):
    first = next(value for value in vector if value)
    return tuple(vector) if first > 0 else tuple(-value for value in vector)


def line_set(anchors, roots):
    return {
        canonical(root)
        for root in roots
        if all(dot(root, anchor) == 0 for anchor in anchors)
    }


def orthogonal_frames(lines):
    adjacency = [
        {j for j in range(WIDTH) if j != i and dot(lines[i], lines[j]) == 0}
        for i in range(WIDTH)
    ]
    frames = []
    stack = [((), tuple(range(WIDTH)))]
    steps = 0
    while stack:
        steps += 1
        need(steps <= 100000, "frame enumeration exceeded its state cap")
        frame, candidates = stack.pop()
        if len(frame) == FRAME_SIZE:
            frames.append(frame)
            continue
        need_more = FRAME_SIZE - 1 - len(frame)
        for offset, index in enumerate(candidates):
            tail = tuple(k for k in candidates[offset + 1:] if k in adjacency[index])
            if len(tail) >= need_more:
                stack.append((frame + (index,), tail))
    frames = tuple(sorted(frames))
    need(len(frames) == len(set(frames)) == FRAME_COUNT, "E6 4-frame count")
    for frame in frames:
        need(len(frame) == FRAME_SIZE, "frame length")
        need(all(j in adjacency[i] for i, j in combinations(frame, 2)), "frame not orthogonal")
    return frames


def kernel(rows):
    echelon = {}
    for row in rows:
        for pivot in range(WIDTH - 1, -1, -1):
            if row >> pivot & 1:
                if pivot in echelon:
                    row ^= echelon[pivot]
                else:
                    echelon[pivot] = row
                    break
    free = tuple(j for j in range(WIDTH) if j not in echelon)
    need(len(echelon) == RANK and len(free) == DIMENSION, "E6 frame-code rank")
    basis = []
    for index, coordinate in enumerate(free):
        vector = 1 << coordinate
        for pivot in sorted(echelon):
            if (echelon[pivot] & vector).bit_count() % 2:
                vector |= 1 << pivot
        need(0 < vector < 1 << WIDTH, "kernel vector outside F_2^36")
        pattern = tuple((vector >> place) & 1 for place in free)
        identity = tuple(int(place == index) for place in range(DIMENSION))
        need(pattern == identity, "free coordinates are not a basis identity")
        need(all((vector & row).bit_count() % 2 == 0 for row in rows),
             "a frame parity survives")
        basis.append(vector)
    return tuple(basis), free


def span(generators):
    words = [0]
    for generator in generators:
        # Snapshot the current list. Extending from a live view of `words`
        # would follow the newly written vectors and never stop.
        words.extend([word ^ generator for word in words])
    need(len(set(words)) == len(words), "span repeats a word")
    return words


def low_weight(words, maximum):
    found = set()
    minimum = maximum + 1
    for word in words:
        weight = word.bit_count()
        if word and weight < minimum:
            minimum = weight
        if weight <= maximum:
            found.add(word)
    return found, minimum


def half_split(basis, maximum, low_dimension):
    need(0 < low_dimension < len(basis), "split must use both halves")
    lows = span(basis[:low_dimension])
    highs = span(basis[low_dimension:])
    distinct = len(lows) * len(highs)
    need(distinct == 1 << len(basis), "halves do not cover the basis span")
    found, minimum = low_weight((high ^ low for high in highs for low in lows), maximum)
    return found, minimum, distinct


def engine_words(engine, basis, maximum, batch_bits):
    listed = list(engine(basis, WIDTH, maximum, batch_bits))
    need(len(listed) == len(set(listed)), "engine repeated a word")
    return set(listed)


def load_lines():
    witness = json.loads(
        (ROOT / "research/e6-e7-shadow-minrank-upper/WITNESSES.json").read_text(
            encoding="utf-8"
        )
    )
    item = witness["units"]["E6"]
    anchors = tuple(tuple(anchor) for anchor in item["anchors"])
    lines = tuple(tuple(line) for line in item["lines"])
    roots = e8_roots()
    need(len(anchors) == 2 and anchors[0] != anchors[1], "two A2 anchors")
    need(all(anchor in roots for anchor in anchors), "anchor is not an E8 root")
    need(abs(dot(*anchors)) == 4, "anchors are not an A2")
    need(len(lines) == len(set(lines)) == WIDTH, "stored line count")
    need(all(dot(line, line) == 8 for line in lines), "stored line norms")
    need({canonical(line) for line in lines} == line_set(anchors, roots),
         "stored lines are not the A2 complement")
    return lines


def positive_words_have_weight(words, weight):
    return all(word.bit_count() == weight for word in words if word)


def check():
    authenticate()
    lines = load_lines()
    frames = orthogonal_frames(lines)
    degree = [0] * WIDTH
    for frame in frames:
        for index in frame:
            degree[index] += 1
    need(len(set(degree)) == 1 and degree[0] > 0, "frame degree is not regular")
    rows = tuple(sum(1 << index for index in frame) for frame in frames)
    basis, free = kernel(rows)
    literal = span(basis)
    need(len(literal) == 1 << DIMENSION, "literal span missed a codeword")
    found, minimum = low_weight(literal, WEIGHT_BOUND)
    supports = found - {0}
    need(0 in found, "zero word missing")
    need(minimum == WEIGHT_BOUND, "minimum left sixteen")
    need(len(supports) == SUPPORT_COUNT, "support count")
    need(positive_words_have_weight(found, WEIGHT_BOUND), "a lighter nonzero word")
    splits = {}
    for low_dimension in (3, 4):
        split_found, split_minimum, distinct = half_split(basis, WEIGHT_BOUND, low_dimension)
        need(split_found == found and split_minimum == WEIGHT_BOUND, "half-split changed the set")
        need(distinct == 1 << DIMENSION, "half-split span")
        splits[low_dimension] = distinct
    engine = run_path(
        str(ROOT / "research/e7-bitsliced-exhaustion/binary.py"),
        run_name="e6_frame_lane_engine",
    )["low_weight_words"]
    for batch_bits in (16, 8):
        produced = engine_words(engine, basis, WEIGHT_BOUND, batch_bits)
        need(produced == found, "engine batch " + str(batch_bits) + " dropped or added a word")
    sharp = engine_words(engine, basis, WEIGHT_BOUND - 1, 8)
    need(sharp == {0}, "weight bound 15 still emitted a positive word")
    witness = next(iter(supports))
    need(engine_words(engine, basis, WEIGHT_BOUND, 16) - {witness} != found,
         "dropping one support still compared equal")
    lighter = witness ^ (1 << (witness.bit_length() - 1))
    need(lighter.bit_count() == WEIGHT_BOUND - 1, "clearing the top bit did not reduce weight")
    need(lighter not in found, "a weight-fifteen word was already in the code")
    forged = set(found)
    forged.add(lighter)
    need(not positive_words_have_weight(forged, WEIGHT_BOUND),
         "weight-fifteen injection was accepted")
    try:
        list(engine((basis[0], basis[0]), WIDTH, WEIGHT_BOUND, 4))
    except ValueError:
        rejected = True
    else:
        rejected = False
    need(rejected, "a repeated generator was accepted")
    digest = sha256(json.dumps(sorted(supports)).encode()).hexdigest()
    return {
        "status": "PASS_E6_FRAME_CODE_LANE_COVERAGE",
        "width": WIDTH,
        "frames": FRAME_COUNT,
        "frame_size": FRAME_SIZE,
        "frame_degree": degree[0],
        "rank": RANK,
        "dimension": DIMENSION,
        "free_coordinates": list(free),
        "minimum_positive_weight": minimum,
        "weight_at_most_16": len(found),
        "minimum_supports": len(supports),
        "distinct_codewords": 1 << DIMENSION,
        "splits": [3, 4],
        "engine_batches": [16, 8],
        "bound_15_words": len(sharp),
        "dependent_generator_rejected": rejected,
        "supports_sha256": digest,
        "e7_kernel_replayed": False,
        "timing_remeasured": False,
        "no_new_kappa": True,
    }


if __name__ == "__main__":
    result = check()
    print(
        "PASS_E6_FRAME_CODE_LANE_COVERAGE"
        " frames={frames}"
        " dimension={dimension}"
        " minimum={minimum_positive_weight}"
        " supports={minimum_supports}"
        " codewords={distinct_codewords}"
        " batches=16,8"
        " splits=3,4"
        " e7_kernel_replayed=false"
        " no_new_kappa=true".format(**result)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
