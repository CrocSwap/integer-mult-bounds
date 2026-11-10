#!/usr/bin/env python3
"""Compare the opt-in intersection-counter engine with one E6 support set.

The 7-generator basis is the F2 kernel of the 135 orthogonal 4-frames on the
36 stored E6 lines. A literal doubling lists that span. The engine is then
called once, at batch size 16, and its yielded words are compared with the
weight-at-most-16 subset. No timing and no E7 census.
"""

import inspect
import json
from functools import partial
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
FRAME_DEGREE = 15
WEIGHT_BOUND = 16
SUPPORT_COUNT = 63
WORD_COUNT = 64
BATCH_BITS = 16
FREE_COORDINATES = (0, 1, 2, 4, 6, 8, 20)
GENERATORS = (
    6591703721,
    6306835114,
    13904919564,
    45813124144,
    28344004800,
    68452089600,
    68718428160,
)
SUPPORT_SHA256 = (
    "ad4a1d101774e6c2da40cde3d097d39aa56ee5668dcdca858513c5fec3578215"
)
JSON_LIST_SHA256 = (
    "3a316d6d3226f84c1e46e4447fa8d5fd800bff4a1bc6498152523cd4a602b69b"
)


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
    need(checked == 3, "three live inputs")
    return checked


def support_hash(words):
    """SHA256 of the sorted positive words, as a default JSON list."""
    positive = sorted(word for word in words if word)
    payload = json.dumps(positive).encode()
    return sha256(payload).hexdigest(), positive


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
            tail = tuple(
                k for k in candidates[offset + 1:] if k in adjacency[index]
            )
            if len(tail) >= need_more:
                stack.append((frame + (index,), tail))
    frames = tuple(sorted(frames))
    need(len(frames) == len(set(frames)) == FRAME_COUNT, "E6 4-frame count")
    for frame in frames:
        need(len(frame) == FRAME_SIZE, "frame length")
        need(
            all(j in adjacency[i] for i, j in combinations(frame, 2)),
            "frame not orthogonal",
        )
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
    need(free == FREE_COORDINATES, "free coordinates are not the pinned basis")
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
        need(
            all((vector & row).bit_count() % 2 == 0 for row in rows),
            "a frame parity survives",
        )
        basis.append(vector)
    return tuple(basis)


def span(generators):
    words = [0]
    for generator in generators:
        # Snapshot the current list. A live generator would follow new words.
        words.extend([word ^ generator for word in words])
    need(len(set(words)) == len(words) == 1 << DIMENSION, "span is not 128 words")
    return words


def low_weight(words):
    found = {word for word in words if word.bit_count() <= WEIGHT_BOUND}
    positive = {word for word in found if word}
    minimum = min(word.bit_count() for word in positive)
    need(0 in found and len(found) == WORD_COUNT, "literal census is not 64 words")
    need(len(positive) == SUPPORT_COUNT and minimum == WEIGHT_BOUND,
         "literal supports are not 63 words of weight 16")
    need(all(word.bit_count() == WEIGHT_BOUND for word in positive),
         "a lighter nonzero literal word")
    return found


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
    need(
        {canonical(line) for line in lines} == line_set(anchors, roots),
        "stored lines are not the A2 complement",
    )
    return lines


def incidence_basis():
    lines = load_lines()
    frames = orthogonal_frames(lines)
    degree = [0] * WIDTH
    for frame in frames:
        for index in frame:
            degree[index] += 1
    need(set(degree) == {FRAME_DEGREE}, "frame degree is not 15")
    rows = tuple(sum(1 << index for index in frame) for frame in frames)
    return kernel(rows)


def bind_engine():
    binary = run_path(
        str(ROOT / "research/e7-bitsliced-exhaustion/binary.py"),
        run_name="e6_population_helpers",
    )
    engine_ns = run_path(
        str(ROOT / "research/e7-intersection-counters/engine.py"),
        run_name="e6_intersection_engine",
    )
    engine = engine_ns["low_weight_words"]
    signature = inspect.signature(engine)
    for name in ("population_planes", "at_most"):
        need(signature.parameters[name].kind is inspect.Parameter.KEYWORD_ONLY,
             name + " is not keyword-only on the intersection engine")
    try:
        binary["low_weight_words"](
            (1,), 1, 0, 1,
            population_planes=binary["population_planes"],
            at_most=binary["at_most"],
        )
    except TypeError:
        separated = True
    else:
        separated = False
    need(separated, "the bit-lane enumerator accepted the intersection keywords")
    return partial(
        engine,
        population_planes=binary["population_planes"],
        at_most=binary["at_most"],
    )


def engine_words(engine, basis):
    listed = list(engine(basis, WIDTH, WEIGHT_BOUND, BATCH_BITS))
    need(len(listed) == len(set(listed)) == WORD_COUNT,
         "engine stream is not 64 distinct words")
    produced = set(listed)
    positive = {word for word in produced if word}
    need(0 in produced and len(positive) == SUPPORT_COUNT, "engine support count")
    need(all(word.bit_count() == WEIGHT_BOUND for word in positive),
         "engine emitted a word whose weight is not 16")
    return produced


def reject_duplicate(engine, basis):
    try:
        list(engine((basis[0], basis[0]), WIDTH, WEIGHT_BOUND, BATCH_BITS))
    except ValueError as exc:
        need(str(exc) == "dependent generators", "unexpected rejection: " + str(exc))
        return True
    return False


def check():
    need(
        sha256(json.dumps([1, 2]).encode()).hexdigest() == JSON_LIST_SHA256,
        "JSON list encoding changed",
    )
    authenticate()
    basis = incidence_basis()
    need(basis == GENERATORS, "kernel basis integers changed")
    found = low_weight(span(basis))
    literal_hash, _ = support_hash(found)
    need(literal_hash == SUPPORT_SHA256,
         "rebuilt support hash " + literal_hash)
    # Batch 16 covers dimension 7 in one lane block, so this call is the
    # whole span rather than a sample of high offsets.
    lane_count = min(BATCH_BITS, DIMENSION)
    need(lane_count == DIMENSION and (1 << (DIMENSION - lane_count)) == 1,
         "batch 16 does not put every generator in one block")
    engine = bind_engine()
    produced = engine_words(engine, basis)
    engine_hash, _ = support_hash(produced)
    missing = found - produced
    extra = produced - found
    need(not missing and not extra,
         "set mismatch missing={0} extra={1}".format(len(missing), len(extra)))
    need(engine_hash == SUPPORT_SHA256, "engine support hash " + engine_hash)
    witness = min(word for word in produced if word)
    dropped = produced - {witness}
    dropped_hash, _ = support_hash(dropped)
    need(dropped != found, "dropping one support still compared equal")
    need(dropped_hash != SUPPORT_SHA256, "dropping one support kept the hash")
    rejected = reject_duplicate(engine, basis)
    need(rejected, "a repeated generator was accepted")
    return {
        "status": "PASS_E6_INTERSECTION_COUNTER_SUPPORT",
        "width": WIDTH,
        "frames": FRAME_COUNT,
        "frame_degree": FRAME_DEGREE,
        "rank": RANK,
        "dimension": DIMENSION,
        "free_coordinates": list(FREE_COORDINATES),
        "generators": list(basis),
        "batch_bits": BATCH_BITS,
        "lane_generators": lane_count,
        "high_offset_batches": 1,
        "literal_codewords": 1 << DIMENSION,
        "weight_at_most_16": len(found),
        "positive_supports": SUPPORT_COUNT,
        "engine_stream_words": WORD_COUNT,
        "sets_equal": produced == found,
        "literal_supports_sha256": literal_hash,
        "engine_supports_sha256": engine_hash,
        "duplicate_generator_rejected": rejected,
        "e7_census_replayed": False,
        "timing_measured": False,
        "no_new_kappa": True,
    }


if __name__ == "__main__":
    result = check()
    print(
        "PASS_E6_INTERSECTION_COUNTER_SUPPORT"
        " batch={batch_bits}"
        " words={weight_at_most_16}"
        " supports={positive_supports}"
        " hash={engine_supports_sha256}"
        " equal={sets_equal}"
        " e7_census=false"
        " timed=false"
        " no_new_kappa=true".format(**result)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
