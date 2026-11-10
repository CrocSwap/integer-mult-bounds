#!/usr/bin/env python3
"""The intersection-counter engine refuses the P112 36-generator basis.

The basis is the F2 kernel of the 1260 live orthogonal 8-frames. The target
is the seven weight-16 supports recorded with hash
ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3.
low_weight_words is called at every legal batch size. Each call raises
before yielding. Batch size 20 is the named comparison.
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
WIDTH = 112
FRAME_SIZE = 8
FRAME_COUNT = 1260
RANK = 76
DIMENSION = 36
DEGREE = 90
WEIGHT_BOUND = 16
SUPPORT_COUNT = 7
NAMED_BATCH = 20
LEGAL_BATCHES = tuple(range(1, 21))
PREFIX = 27
LATE = DIMENSION - PREFIX
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
DIMENSION_MESSAGE = "dimension exceeds 27"
BATCH_COUNT_MESSAGE = "batch count exceeds 65536"
DEPENDENT_MESSAGE = "dependent generators"
BATCH_MESSAGE = "invalid batch size"


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
    payload = json.dumps(sorted(words)).encode()
    return sha256(payload).hexdigest()


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
        run_name="p112_capacity_model",
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


def bind_engine():
    binary = run_path(
        str(ROOT / "research/e7-bitsliced-exhaustion/binary.py"),
        run_name="p112_capacity_population",
    )
    engine_ns = run_path(
        str(ROOT / "research/e7-intersection-counters/engine.py"),
        run_name="p112_capacity_engine",
    )
    engine = engine_ns["low_weight_words"]
    signature = inspect.signature(engine)
    for name in ("population_planes", "at_most"):
        parameter = signature.parameters[name]
        need(parameter.kind is inspect.Parameter.KEYWORD_ONLY,
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
    bound = partial(
        engine,
        population_planes=binary["population_planes"],
        at_most=binary["at_most"],
    )
    return bound, engine_ns["checked_rows"]


def stream_outcome(engine, generators, batch, limit):
    """Read at most `limit` yields. A ValueError aborts the stream."""
    stream = engine(generators, WIDTH, WEIGHT_BOUND, batch)
    yielded = []
    try:
        for word in stream:
            yielded.append(word)
            if len(yielded) >= limit:
                break
    except ValueError as exc:
        return yielded, str(exc)
    finally:
        stream.close()
    return yielded, None


def require_refusal(engine, generators, batch):
    yielded, message = stream_outcome(engine, generators, batch, 1)
    need(yielded == [], "a refused call yielded " + str(len(yielded)) + " words")
    need(message == DIMENSION_MESSAGE, "unexpected refusal: " + str(message))
    return message


def coordinate_word(word, basis, free):
    assembled = 0
    for bit, vector in zip(free, basis):
        if (word >> bit) & 1:
            assembled ^= vector
    return assembled


def prefix_split(supports, basis):
    """Split the seven supports by the identity coordinates of this basis."""
    inside = []
    outside = []
    for word in supports:
        need(coordinate_word(word, basis, FREE_COORDINATES) == word,
             "a recorded support is outside this kernel basis")
        late = [bit for bit in FREE_COORDINATES[PREFIX:] if (word >> bit) & 1]
        short = coordinate_word(word, basis[:PREFIX], FREE_COORDINATES[:PREFIX])
        if late:
            outside.append(word)
            need(short != word, "a late support still lay in the 27-prefix")
        else:
            inside.append(word)
            need(short == word, "a zero late-coordinate support left the 27-prefix span")
    return inside, outside


def guard_controls(engine, checked_rows, basis):
    yielded, message = stream_outcome(engine, (basis[0], basis[0]), NAMED_BATCH, 1)
    need(yielded == [] and message == DEPENDENT_MESSAGE,
         "a repeated generator produced " + str(message))
    yielded, message = stream_outcome(engine, basis[:PREFIX], 10, 1)
    need(yielded == [] and message == BATCH_COUNT_MESSAGE,
         "the 27-prefix at batch 10 produced " + str(message))
    rows, count = checked_rows(basis[:PREFIX], WIDTH, WEIGHT_BOUND, NAMED_BATCH)
    need(len(rows) == PREFIX and count == NAMED_BATCH,
         "batch 20 rejected the 27-prefix inside checked_rows")
    yielded, message = stream_outcome(engine, basis[:PREFIX], NAMED_BATCH, 1)
    need(message is None and yielded == [0],
         "the admitted 27-prefix did not yield zero first")
    duplicated = basis[:PREFIX] + (basis[0],)
    require_refusal(engine, duplicated, NAMED_BATCH)
    for batch in (0, 21, True, 20.0):
        yielded, message = stream_outcome(engine, basis, batch, 1)
        need(yielded == [] and message == BATCH_MESSAGE,
             "batch " + repr(batch) + " produced " + str(message))
    require_refusal(engine, tuple(reversed(basis)), NAMED_BATCH)


def check():
    need(sha256(json.dumps([1, 2]).encode()).hexdigest() == JSON_LIST_SHA256,
         "JSON list encoding changed")
    need(len(FREE_COORDINATES) == DIMENSION and len(BASIS_WEIGHTS) == DIMENSION,
         "pinned basis shape")
    need(len(LEGAL_BATCHES) == 20 and NAMED_BATCH in LEGAL_BATCHES, "batch domain")
    need(DIMENSION - NAMED_BATCH == 16 and DIMENSION - 16 > 16,
         "batch 20 is the only legal size whose later guard admits dimension 36")
    authenticate()
    lines, live = pinned_model()
    frames = orthogonal_frames(lines, live)
    rows = tuple(sum(1 << index for index in frame) for frame in frames)
    basis = kernel(rows)
    supports = partition_masks(lines, live)
    need(set(supports) == set(PUBLISHED_SUPPORTS), "partition integers changed")
    digest = support_hash(supports)
    need(digest == SUPPORT_SHA256, "rebuilt support hash " + digest)
    dropped = support_hash(PUBLISHED_SUPPORTS[1:])
    need(dropped != SUPPORT_SHA256, "dropping one support kept the hash")
    need(all(all((word & row).bit_count() % 2 == 0 for row in rows) for word in supports),
         "a recorded support leaves a frame")
    inside, outside = prefix_split(PUBLISHED_SUPPORTS, basis)
    need(inside == list(PUBLISHED_SUPPORTS[:3]), "prefix membership of the first three")
    need(outside == list(PUBLISHED_SUPPORTS[3:]), "four supports use a later generator")
    engine, checked_rows = bind_engine()
    for batch in LEGAL_BATCHES:
        require_refusal(engine, basis, batch)
    guard_controls(engine, checked_rows, basis)
    return {
        "status": "PASS_P112_INTERSECTION_COUNTER_CAPACITY",
        "claim": "exhaustive finite census of legal batch sizes on one input",
        "width": WIDTH,
        "frames": FRAME_COUNT,
        "rank": RANK,
        "dimension": DIMENSION,
        "named_batch": NAMED_BATCH,
        "legal_batches": list(LEGAL_BATCHES),
        "engine_message": DIMENSION_MESSAGE,
        "words_yielded": 0,
        "engine_returned_set": False,
        "sets_equal": False,
        "disagreement": "capacity refusal before any yield",
        "supports_sha256": digest,
        "positive_supports": SUPPORT_COUNT,
        "prefix_contains_supports": len(inside),
        "prefix_misses_supports": len(outside),
        "generator_sha256": GENERATOR_SHA256,
        "codeword_enumeration": False,
        "bit_lane_iterator_replayed": False,
        "half_split_census_replayed": False,
        "e7_census_replayed": False,
        "timing_measured": False,
        "selected_kappa": "781451/250000000",
        "kappa_changed": False,
    }


if __name__ == "__main__":
    result = check()
    print(
        "PASS_P112_INTERSECTION_COUNTER_CAPACITY"
        " batch={named_batch}"
        " legal_batches={count}"
        " yielded={words_yielded}"
        " message={engine_message}"
        " hash={supports_sha256}"
        " returned={engine_returned_set}"
        " prefix_misses={prefix_misses_supports}"
        " enumerated=false"
        " timed=false"
        " no_new_kappa=true".format(count=len(result["legal_batches"]), **result)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
