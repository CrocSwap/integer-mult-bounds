#!/usr/bin/env python3
"""Batch size 20 on a dimension-36 copy of the intersection counter.

The published engine refuses the P112 36-generator basis before its lane
loop. This harness executes a copy of that source in which the single guard
statement admits dimension 36, then compares one batch-size-20 stream with
the recorded eight-word set. The file
research/e7-intersection-counters/engine.py is not written.
"""

import inspect
import json
import sys
import time
from functools import partial
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
WORD_COUNT = 8
NAMED_BATCH = 20
LANE_COUNT = 20
HIGH_BATCHES = 1 << (DIMENSION - LANE_COUNT)
YIELD_LIMIT = 64
FREE_COORDINATES = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 25, 26,
    28, 30, 32, 34, 36, 40, 42, 48, 49, 50, 51, 52, 56, 58, 64, 80,
)
BASIS_WEIGHTS = (
    38, 34, 38, 30, 42, 34, 26, 30, 42, 30, 50, 30, 38, 42, 34, 22, 32, 32,
    32, 30, 32, 32, 30, 22, 24, 36, 20, 36, 28, 36, 28, 32, 32, 32, 32, 32,
)
PUBLISHED_SUPPORTS = (
    64691900160,
    1034819666160,
    280375465144335,
    4772259772306660006937399132160,
    15509841550538713979819718082560,
    1216944648758260568639796318044160,
    3955070108453721685622467917250560,
)
SUPPORT_SHA256 = (
    "ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3"
)
GENERATOR_SHA256 = (
    "c93a6ec3f6d61b3bbf4086218c723761e517bc42ac2c26f551436d271a081e9d"
)
JSON_LIST_SHA256 = (
    "3a316d6d3226f84c1e46e4447fa8d5fd800bff4a1bc6498152523cd4a602b69b"
)
PAIRS = ((0, 1), (2, 3), (4, 5), (6, 7))
MATCHINGS = (((0, 3), (1, 2)), ((0, 2), (1, 3)), ((0, 1), (2, 3)))
SPINOR_REPS = ((0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 1), (0, 1, 1, 0))
GUARD_27 = 'need(index < 27, "dimension exceeds 27")'
GUARD_36 = 'need(index < 36, "dimension exceeds 36")'
DIMENSION_MESSAGE = "dimension exceeds 27"
COPY_DIMENSION_MESSAGE = "dimension exceeds 36"
BATCH_COUNT_MESSAGE = "batch count exceeds 65536"
DEPENDENT_MESSAGE = "dependent generators"
ENGINE_PATH = ROOT / "research/e7-intersection-counters/engine.py"


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


def canonical(vector):
    first = next(value for value in vector if value)
    return tuple(vector) if first > 0 else tuple(-value for value in vector)


def independent_lines():
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
    return tuple(lines), tuple(puncture)


def pinned_model():
    model = run_path(
        str(ROOT / "research/p112-rank6-frame-coverage/engine.py"),
        run_name="p112_dimension_guard_model",
    )["model"]()
    lines = tuple(tuple(row) for row in model["lines"])
    puncture = tuple(model["punctured_frame"])
    live = tuple(model["live"])
    own_lines, own_puncture = independent_lines()
    need(lines == own_lines, "pinned lines differ from the E8 builder")
    need(puncture == own_puncture, "pinned puncture differs")
    need(live == tuple(i for i in range(120) if i not in set(puncture)), "live order")
    need(len(live) == WIDTH, "width")
    need(all(dot(line, line) == 8 for line in lines), "norms")
    return lines, live


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
        need(steps <= 200000, "frame enumeration exceeded its state cap")
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
    degree = [0] * WIDTH
    for frame in frames:
        need(len(frame) == FRAME_SIZE, "frame length")
        for index in frame:
            degree[index] += 1
        need(
            all(dot(lines[live[i]], lines[live[j]]) == 0
                for i, j in combinations(frame, 2)),
            "frame not orthogonal",
        )
    need(set(degree) == {DEGREE}, "frame degree")
    need(steps == 56262, "frame search did not finish in 56262 states")
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
        basis.append(vector)
    basis = tuple(basis)
    need(tuple(vector.bit_count() for vector in basis) == BASIS_WEIGHTS,
         "basis weights changed")
    for index, vector in enumerate(basis):
        pattern = tuple((vector >> place) & 1 for place in free)
        identity = tuple(int(place == index) for place in range(DIMENSION))
        need(pattern == identity, "free coordinates are not a basis identity")
        need(0 < vector < 1 << WIDTH, "kernel vector outside F_2^112")
        need(all((vector & row).bit_count() % 2 == 0 for row in rows),
             "a frame parity survives")
    digest = sha256(json.dumps(list(basis)).encode()).hexdigest()
    need(digest == GENERATOR_SHA256, "generator-list hash " + digest)
    return basis


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

    spinors = [
        lines[old] for old in live if all(abs(value) == 1 for value in lines[old])
    ]
    need(len(spinors) == 64, "spinor line count")

    def relative(root):
        return tuple(
            0 if root[2 * pair] == root[2 * pair + 1] else 1 for pair in range(4)
        )

    def spin_mask(representative):
        patterns = {representative, tuple(1 - bit for bit in representative)}
        mask = 0
        for root in spinors:
            if relative(root) in patterns:
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


def guard_copy(source):
    """Return source whose only character changes are 27 -> 36 in one guard."""
    need(source.count(GUARD_27) == 1, "published guard text is not unique")
    need(GUARD_36 not in source, "published engine already contains the 36 guard")
    copied = source.replace(GUARD_27, GUARD_36, 1)
    need(copied.count(GUARD_36) == 1 and GUARD_27 not in copied, "guard copy drifted")
    need(len(copied) == len(source), "guard copy changed the source length")
    # Each "127" contains these two characters, and the guard states 27 twice.
    need(source.count("27") == 4, "published engine numeral count changed")
    guard_at = source.index(GUARD_27)
    first = guard_at + GUARD_27.index("27")
    second = guard_at + GUARD_27.index("27", GUARD_27.index("27") + 2)
    positions = [
        index for index, pair in enumerate(zip(source, copied)) if pair[0] != pair[1]
    ]
    need(positions == [first, first + 1, second, second + 1],
         "differing positions are not the two guard numerals")
    original_lines = source.splitlines()
    copied_lines = copied.splitlines()
    changed = [
        (left, right)
        for left, right in zip(original_lines, copied_lines)
        if left != right
    ]
    need(len(original_lines) == len(copied_lines), "the copy changed the line count")
    need(changed == [("        " + GUARD_27, "        " + GUARD_36)],
         "the source diff is not the one guard statement")
    return copied


def load_engines(binary):
    """Bind the published function and an in-memory dimension-36 copy."""
    before = ENGINE_PATH.read_bytes()
    source = before.decode("utf-8")
    published = run_path(str(ENGINE_PATH), run_name="p112_dimension_guard_published")
    copied_source = guard_copy(source)
    namespace = {"__name__": "p112_dimension_guard_36_copy"}
    exec(compile(copied_source, "<dimension-guard-36-copy>", "exec"), namespace)
    need(ENGINE_PATH.read_bytes() == before, "the published engine file changed")
    for label, module in (("published", published), ("copy", namespace)):
        signature = inspect.signature(module["low_weight_words"])
        for name in ("population_planes", "at_most"):
            parameter = signature.parameters[name]
            need(parameter.kind is inspect.Parameter.KEYWORD_ONLY,
                 label + " " + name + " is not keyword-only")
    injected = dict(
        population_planes=binary["population_planes"],
        at_most=binary["at_most"],
    )
    return (
        partial(published["low_weight_words"], **injected),
        partial(namespace["low_weight_words"], **injected),
        namespace["checked_rows"],
        published["checked_rows"],
    )


def consume(engine, generators, batch, limit):
    """Read one stream. A ValueError or the yield limit ends the read."""
    stream = engine(generators, WIDTH, WEIGHT_BOUND, batch)
    words = []
    seen = set()
    message = None
    try:
        for word in stream:
            if type(word) is not int or word < 0 or word >= 1 << WIDTH:
                message = "illegal yield"
                break
            if word.bit_count() > WEIGHT_BOUND:
                message = "yielded weight " + str(word.bit_count())
                break
            if word in seen:
                message = "repeated yield"
                break
            words.append(word)
            seen.add(word)
            if len(words) > limit:
                message = "yield limit exceeded"
                break
    except ValueError as exc:
        message = str(exc)
    finally:
        stream.close()
    return tuple(words), message


def refusal(engine, generators, batch, expected):
    words, message = consume(engine, generators, batch, 1)
    need(words == (), "a refused call yielded " + str(len(words)) + " words")
    need(message == expected, "unexpected refusal: " + str(message))


def agree_below_guard(published, copied, basis):
    """The copy matches the published engine on an 8-generator input."""
    sample = basis[:8]
    limit = 1 << len(sample)
    left, left_message = consume(published, sample, NAMED_BATCH, limit)
    right, right_message = consume(copied, sample, NAMED_BATCH, limit)
    need(left_message is None and right_message is None,
         "8-generator stream failed: " + str(left_message) + " / " + str(right_message))
    need(left == right and 0 in left, "copy and published engine differ below dimension 27")
    need(all(word.bit_count() <= WEIGHT_BOUND for word in left), "8-generator weight")


def compare_stream(words, message, supports, rows):
    digest, positive = support_hash(words)
    target = {0, *supports}
    got = set(words)
    missing = sorted(target - got)
    extra = sorted(got - target)
    report = {
        "words_yielded": len(words),
        "distinct_words": len(got),
        "stream_exhausted": message is None,
        "stream_message": message,
        "zero_yielded": 0 in got,
        "positive_words": len(positive),
        "positive_yield_order": [word for word in words if word],
        "positive_sha256": digest,
        "missing_count": len(missing),
        "extra_count": len(extra),
        "missing_head": missing[:4],
        "extra_head": extra[:4],
        "sets_equal": message is None and got == target,
        "weights": sorted({word.bit_count() for word in got}),
        "outside_code": 0,
    }
    if message is None:
        outside = [
            word for word in got
            if any((word & row).bit_count() % 2 for row in rows)
        ]
        report["outside_code"] = len(outside)
    need(message is None, "batch-20 copy stream ended early: " + str(message)
         + " after " + str(len(words)) + " words hash " + digest)
    need(report["outside_code"] == 0, "a yielded word leaves the frame code")
    need(got == target, "set disagreement missing "
         + str(len(missing)) + " extra " + str(len(extra))
         + " hash " + digest
         + " missing_head " + str(missing[:4])
         + " extra_head " + str(extra[:4]))
    need(digest == SUPPORT_SHA256, "positive-word hash " + digest)
    need(len(words) == WORD_COUNT and positive == sorted(supports),
         "the exhausted stream is not the eight recorded words")
    return report


def check():
    need(sha256(json.dumps([1, 2]).encode()).hexdigest() == JSON_LIST_SHA256,
         "JSON list encoding changed")
    need(len(FREE_COORDINATES) == DIMENSION and len(BASIS_WEIGHTS) == DIMENSION,
         "pinned basis shape")
    need(HIGH_BATCHES == 65536 and DIMENSION - NAMED_BATCH == 16, "lane split")
    need(NAMED_BATCH == LANE_COUNT, "batch size is the lane count on this input")
    authenticate()
    lines, live = pinned_model()
    frames = orthogonal_frames(lines, live)
    rows = tuple(sum(1 << index for index in frame) for frame in frames)
    basis = kernel(rows)
    supports = partition_masks(lines, live)
    need(tuple(sorted(supports)) == tuple(sorted(PUBLISHED_SUPPORTS)),
         "partition integers changed")
    digest, ordered = support_hash(supports)
    need(digest == SUPPORT_SHA256 and ordered == list(sorted(PUBLISHED_SUPPORTS)),
         "rebuilt support hash " + digest)
    dropped, _ = support_hash(PUBLISHED_SUPPORTS[1:])
    need(dropped != SUPPORT_SHA256, "dropping one support kept the hash")
    need(all(all((word & row).bit_count() % 2 == 0 for row in rows)
             for word in supports),
         "a recorded support leaves a frame")
    binary = run_path(
        str(ROOT / "research/e7-bitsliced-exhaustion/binary.py"),
        run_name="p112_dimension_guard_population",
    )
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
    published, copied, copied_rows, published_rows = load_engines(binary)
    refusal(published, basis, NAMED_BATCH, DIMENSION_MESSAGE)
    try:
        published_rows(basis, WIDTH, WEIGHT_BOUND, NAMED_BATCH)
    except ValueError as exc:
        published_rows_message = str(exc)
    else:
        published_rows_message = None
    need(published_rows_message == DIMENSION_MESSAGE,
         "published checked_rows produced " + str(published_rows_message))
    agree_below_guard(published, copied, basis)
    refusal(copied, (basis[0], basis[0]), NAMED_BATCH, DEPENDENT_MESSAGE)
    refusal(copied, basis + (rows[0],), NAMED_BATCH, COPY_DIMENSION_MESSAGE)
    for batch in range(1, NAMED_BATCH):
        try:
            copied_rows(basis, WIDTH, WEIGHT_BOUND, batch)
        except ValueError as exc:
            batch_message = str(exc)
        else:
            batch_message = None
        need(batch_message == BATCH_COUNT_MESSAGE,
             "batch " + str(batch) + " on the copy produced " + str(batch_message))
    for batch in (0, 21, True, 20.0):
        refusal(copied, basis, batch, "invalid batch size")
    accepted, count = copied_rows(basis, WIDTH, WEIGHT_BOUND, NAMED_BATCH)
    need(tuple(accepted) == basis and count == LANE_COUNT,
         "batch 20 did not admit the 36 generators into 20 lanes")
    started = time.perf_counter()
    print("stream_start batch=20 lanes=20 high_batches=65536", file=sys.stderr)
    words, message = consume(copied, basis, NAMED_BATCH, YIELD_LIMIT)
    elapsed = time.perf_counter() - started
    print("stream_done seconds={:.3f} words={} message={}".format(
        elapsed, len(words), message), file=sys.stderr)
    report = compare_stream(words, message, tuple(sorted(PUBLISHED_SUPPORTS)), rows)
    need(report["sets_equal"] is True, "comparison did not record equality")
    need(report["positive_yield_order"] == list(PUBLISHED_SUPPORTS),
         "positive yield order is not the recorded increasing list")
    need(words[0] == 0, "zero was not the first yield")
    need(ENGINE_PATH.read_text(encoding="utf-8").count(GUARD_27) == 1,
         "published engine text changed after the stream")
    report.update({
        "status": "PASS_P112_DIMENSION_GUARD_36",
        "claim": "exhaustive finite comparison of one copied stream",
        "width": WIDTH,
        "frames": FRAME_COUNT,
        "rank": RANK,
        "dimension": DIMENSION,
        "batch_bits": NAMED_BATCH,
        "lane_generators": count,
        "high_offset_batches": 1 << (len(accepted) - count),
        "guard_statement": GUARD_36,
        "published_guard": GUARD_27,
        "published_file_edited": False,
        "published_batch20_message": DIMENSION_MESSAGE,
        "supports_sha256": SUPPORT_SHA256,
        "generator_sha256": GENERATOR_SHA256,
        "host_elapsed_seconds": round(elapsed, 3),
        "timing_claimed_as_coverage": False,
        "bit_lane_iterator_replayed": False,
        "half_split_census_replayed": False,
        "e6_replayed": False,
        "d6_replayed": False,
        "e7_census_replayed": False,
        "selected_kappa": "781451/250000000",
        "kappa_changed": False,
    })
    return report


if __name__ == "__main__":
    result = check()
    print(
        "PASS_P112_DIMENSION_GUARD_36"
        " batch={batch_bits}"
        " lanes={lane_generators}"
        " high_batches={high_offset_batches}"
        " words={words_yielded}"
        " hash={supports_sha256}"
        " equal={sets_equal}"
        " published_edited={published_file_edited}"
        " enumerated_code=false"
        " timed_as_coverage=false"
        " no_new_kappa=true".format(**result)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
