#!/usr/bin/env python3
"""Compare the opt-in intersection-counter engine with one D6 support set.

The 20-generator basis is the F2 kernel of the 15 orthogonal 6-frames on the
30 stored D6 lines from research/d6-punctured-frame-code. A binary-reflected
Gray walk lists every codeword of that span. The engine is then called once,
at batch size 16, and its yielded words are compared with the weight-at-most-2
subset. The bit-lane enumerator is not called. No timing and no E7 census.
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
WIDTH = 30
FRAME_SIZE = 6
DIMENSION = 20
RANK = 10
FRAME_COUNT = 15
WEIGHT_BOUND = 2
SUPPORT_COUNT = 15
WORD_COUNT = 16
BATCH_BITS = 16
LANE_GENERATORS = 16
HIGH_OFFSET_BATCHES = 16
AXES = (2, 3, 4, 5, 6, 7)
ANCHORS = ((2, 2, 0, 0, 0, 0, 0, 0), (2, -2, 0, 0, 0, 0, 0, 0))
FREE_COORDINATES = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 20, 21, 22, 23, 24,
)
GENERATORS = (
    101451777,
    101451778,
    1007553540,
    168428552,
    168428560,
    1007553568,
    2112,
    1152,
    772279552,
    772279808,
    528384,
    270336,
    147456,
    504266752,
    504299520,
    537919488,
    270532608,
    138412032,
    75497472,
    50331648,
)
SUPPORTS = (
    3,
    24,
    36,
    768,
    1152,
    2112,
    98304,
    147456,
    270336,
    528384,
    50331648,
    75497472,
    138412032,
    270532608,
    537919488,
)
LINES_SHA256 = "bd3d7efd8a94a7d0a6a7339cfd95805bb6907f3951ff67e9669b317655869538"
SUPPORT_SHA256 = (
    "23a7b374a6bc62bc2aca47843d52a01fa8e791ed3a98085133829d816c5094e8"
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


def canon(vector):
    first = next(value for value in vector if value)
    return tuple(vector) if first > 0 else tuple(-value for value in vector)


def e8_lines():
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (2, -2):
            root = [0] * 8
            root[i], root[j] = 2, sign
            roots.append(canon(root))
    for tail in product((1, -1), repeat=7):
        root = (1,) + tail
        if root.count(-1) % 2 == 0:
            roots.append(root)
    need(len(roots) == len(set(roots)) == 120, "E8 line count")
    need(all(dot(root, root) == 8 for root in roots), "E8 norms")
    return set(roots)


def coordinate_lines(axes):
    lines = []
    for i, j in combinations(axes, 2):
        for sign in (2, -2):
            root = [0] * 8
            root[i], root[j] = 2, sign
            lines.append(canon(root))
    lines = tuple(sorted(set(lines)))
    need(len(lines) == WIDTH, "coordinate D6 line count")
    return lines


def load_lines():
    payload = json.loads(
        (ROOT / "research/d6-punctured-frame-code/ROOTS.json").read_text(
            encoding="utf-8"
        )
    )
    anchors = tuple(tuple(anchor) for anchor in payload["anchors"])
    axes = tuple(payload["axes"])
    stored = tuple(tuple(line) for line in payload["lines"])
    need(anchors == ANCHORS, "pinned anchors changed")
    need(axes == AXES, "pinned axes changed")
    need(len(stored) == len(set(stored)) == WIDTH, "pinned line count")
    digest = sha256(
        json.dumps(
            [list(line) for line in stored], separators=(",", ":")
        ).encode()
    ).hexdigest()
    need(digest == LINES_SHA256, "pinned line hash changed")
    roots = e8_lines()
    need(all(anchor in roots for anchor in anchors), "anchor is not an E8 line")
    need(dot(*anchors) == 0, "anchors are not orthogonal")
    complement = tuple(
        sorted(
            root
            for root in roots
            if all(dot(root, anchor) == 0 for anchor in anchors)
        )
    )
    coordinate = coordinate_lines(axes)
    need(stored == complement == coordinate, "pinned lines are not this D6 slice")
    return stored


def perfect_matchings(vertices):
    vertices = tuple(vertices)
    if not vertices:
        yield ()
        return
    first, rest = vertices[0], vertices[1:]
    for index, partner in enumerate(rest):
        remaining = rest[:index] + rest[index + 1 :]
        for tail in perfect_matchings(remaining):
            yield ((first, partner),) + tail


def support_of(line):
    return tuple(index for index, value in enumerate(line) if value)


def combinatorial_frames(lines):
    lookup = {line: index for index, line in enumerate(lines)}
    frames = []
    for matching in perfect_matchings(AXES):
        chosen = []
        for i, j in matching:
            for sign in (2, -2):
                root = [0] * 8
                root[i], root[j] = 2, sign
                chosen.append(lookup[canon(root)])
        frames.append(tuple(sorted(chosen)))
    frames = tuple(sorted(set(frames)))
    need(len(frames) == FRAME_COUNT, "perfect-matching frame count")
    for frame in frames:
        need(len(frame) == FRAME_SIZE, "frame length")
        need(
            all(dot(lines[i], lines[j]) == 0 for i, j in combinations(frame, 2)),
            "matching frame is not orthogonal",
        )
        covered = []
        for index in frame:
            covered.extend(support_of(lines[index]))
        need(
            sorted(covered) == sorted(AXES + AXES),
            "a frame does not use both signs on three edges",
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
    need(len(echelon) == RANK and free == FREE_COORDINATES, "D6 frame-code rank")
    basis = []
    for index, coordinate in enumerate(free):
        vector = 1 << coordinate
        for pivot in sorted(echelon):
            if (echelon[pivot] & vector).bit_count() % 2:
                vector |= 1 << pivot
        need(0 < vector < 1 << WIDTH, "kernel vector outside F_2^30")
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
    need(len(set(words)) == len(words) == 1 << len(generators), "span repeats a word")
    return set(words)


def literal_low_weight(basis):
    """Visit every span word once and keep those of weight at most 2.

    The bit flipped at step index is the lowest set bit of index. The
    coefficient vector at that step is index XOR (index >> 1). The free
    coordinates of the running word are checked against that Gray code at
    every index. Those coordinates are an identity basis, so each of the
    2^20 coefficients occurs once.
    """
    found = set()
    word = 0
    limit = 1 << DIMENSION
    for index in range(limit):
        if index:
            word ^= basis[(index & -index).bit_length() - 1]
        gray = index ^ (index >> 1)
        for place, coordinate in enumerate(FREE_COORDINATES):
            need(
                ((word >> coordinate) & 1) == ((gray >> place) & 1),
                "Gray step left the free-coordinate identity",
            )
        if word.bit_count() <= WEIGHT_BOUND:
            found.add(word)
    need(0 in found and len(found) == WORD_COUNT, "literal census is not 16 words")
    positive = tuple(sorted(item for item in found if item))
    need(positive == SUPPORTS, "literal supports are not the pinned 15 words")
    need(
        all(item.bit_count() == WEIGHT_BOUND for item in positive),
        "a lighter nonzero literal word",
    )
    return found


def incidence_basis():
    lines = load_lines()
    frames = combinatorial_frames(lines)
    rows = tuple(sum(1 << index for index in frame) for frame in frames)
    return kernel(rows)


def bind_engine():
    binary = run_path(
        str(ROOT / "research/e7-bitsliced-exhaustion/binary.py"),
        run_name="d6_population_helpers",
    )
    engine_ns = run_path(
        str(ROOT / "research/e7-intersection-counters/engine.py"),
        run_name="d6_intersection_engine",
    )
    engine = engine_ns["low_weight_words"]
    signature = inspect.signature(engine)
    for name in ("population_planes", "at_most"):
        need(
            signature.parameters[name].kind is inspect.Parameter.KEYWORD_ONLY,
            name + " is not keyword-only on the intersection engine",
        )
    try:
        binary["low_weight_words"](
            (1,),
            1,
            0,
            1,
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
    need(
        len(listed) == len(set(listed)) == WORD_COUNT,
        "engine stream is not 16 distinct words",
    )
    produced = set(listed)
    positive = tuple(sorted(word for word in produced if word))
    need(0 in produced and positive == SUPPORTS, "engine support list")
    need(
        all(word.bit_count() == WEIGHT_BOUND for word in positive),
        "engine emitted a word whose weight is not 2",
    )
    return produced


def reject_duplicate(engine, basis):
    try:
        list(engine((basis[0], basis[0]), WIDTH, WEIGHT_BOUND, BATCH_BITS))
    except ValueError as exc:
        need(str(exc) == "dependent generators", "unexpected rejection: " + str(exc))
        return True
    return False


def reject_small_batch(engine, basis):
    """Batch size 3 leaves 17 high generators, past the engine's 16-offset cap.

    This is one refusal control. It does not survey the other batch sizes.
    """
    try:
        list(engine(basis, WIDTH, WEIGHT_BOUND, 3))
    except ValueError as exc:
        need(
            str(exc) == "batch count exceeds 65536",
            "unexpected small-batch rejection: " + str(exc),
        )
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
    need(len(basis) == DIMENSION, "basis length")
    weight_two = tuple(word for word in basis if word.bit_count() == WEIGHT_BOUND)
    need(len(weight_two) == 10, "weight-2 generator count")
    high = basis[LANE_GENERATORS:]
    need(len(high) == DIMENSION - LANE_GENERATORS, "high-generator count")
    lane_span = span(basis[:LANE_GENERATORS])
    need(
        all(word.bit_count() == WEIGHT_BOUND and word not in lane_span for word in high),
        "a high generator lies in the lane span or does not have weight 2",
    )
    found = literal_low_weight(basis)
    need(set(high) <= found, "a high generator is outside the low-weight set")
    proper_sums = tuple(sorted(set(SUPPORTS) - set(basis)))
    need(len(proper_sums) == 5, "the support set is only the weight-2 generators")
    need(set(weight_two) <= set(SUPPORTS), "a weight-2 generator leaves the support set")
    literal_hash, literal_positive = support_hash(found)
    need(tuple(literal_positive) == SUPPORTS, "sorted literal supports moved")
    need(literal_hash == SUPPORT_SHA256, "rebuilt support hash " + literal_hash)
    lane_count = min(BATCH_BITS, DIMENSION)
    high_batches = 1 << (DIMENSION - lane_count)
    need(
        lane_count == LANE_GENERATORS and high_batches == HIGH_OFFSET_BATCHES,
        "batch 16 does not split this basis into 16 lanes and 16 high offsets",
    )
    engine = bind_engine()
    produced = engine_words(engine, basis)
    engine_hash, _ = support_hash(produced)
    missing = found - produced
    extra = produced - found
    need(
        not missing and not extra,
        "set mismatch missing={0} extra={1}".format(len(missing), len(extra)),
    )
    need(engine_hash == SUPPORT_SHA256, "engine support hash " + engine_hash)
    witness = min(word for word in produced if word)
    dropped = produced - {witness}
    dropped_hash, _ = support_hash(dropped)
    need(dropped != found, "dropping one support still compared equal")
    need(dropped_hash != SUPPORT_SHA256, "dropping one support kept the hash")
    rejected = reject_duplicate(engine, basis)
    need(rejected, "a repeated generator was accepted")
    small_batch = reject_small_batch(engine, basis)
    need(small_batch, "batch size 3 was accepted")
    return {
        "status": "PASS_D6_INTERSECTION_COUNTER_SUPPORT",
        "width": WIDTH,
        "frames": FRAME_COUNT,
        "rank": RANK,
        "dimension": DIMENSION,
        "free_coordinates": list(FREE_COORDINATES),
        "generators": list(basis),
        "batch_bits": BATCH_BITS,
        "lane_generators": lane_count,
        "high_offset_batches": high_batches,
        "literal_codewords": 1 << DIMENSION,
        "weight_at_most_2": len(found),
        "positive_supports": SUPPORT_COUNT,
        "weight_2_generators": len(weight_two),
        "high_generators_outside_lane_span": len(high),
        "proper_sums": len(proper_sums),
        "engine_stream_words": WORD_COUNT,
        "sets_equal": produced == found,
        "literal_supports_sha256": literal_hash,
        "engine_supports_sha256": engine_hash,
        "duplicate_generator_rejected": rejected,
        "batch_3_rejected": small_batch,
        "bit_lane_census_replayed": False,
        "e7_census_replayed": False,
        "p112_basis_checked": False,
        "timing_measured": False,
        "no_new_kappa": True,
    }


if __name__ == "__main__":
    result = check()
    print(
        "PASS_D6_INTERSECTION_COUNTER_SUPPORT"
        " batch={batch_bits}"
        " words={weight_at_most_2}"
        " supports={positive_supports}"
        " hash={engine_supports_sha256}"
        " equal={sets_equal}"
        " e7_census=false"
        " bit_lane_census=false"
        " timed=false"
        " no_new_kappa=true".format(**result)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
