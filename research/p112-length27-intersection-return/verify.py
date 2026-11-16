#!/usr/bin/env python3
"""One length-27 P112 generating set returns the eight-word intersection stream.

The seven partition supports are pairwise disjoint weight-16 codewords. Their
F2-span therefore contains exactly those seven words and zero at weight at
most 16. Appending the first twenty kernel-basis vectors that stay independent
under the engine's high-bit elimination produces an explicit 27-tuple inside
the same code. A binary-reflected Gray code lists every vector of that span.
The published intersection-counter engine is then called once, at batch size
20, and the yielded set is compared with that census and with hash
ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3.
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
TUPLE_LENGTH = 27
NAMED_BATCH = 20
LANE_GENERATORS = 20
HIGH_OFFSETS = 1 << (TUPLE_LENGTH - LANE_GENERATORS)
SPAN_WORDS = 1 << TUPLE_LENGTH
FREE_COORDINATES = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 25, 26,
    28, 30, 32, 34, 36, 40, 42, 48, 49, 50, 51, 52, 56, 58, 64, 80,
)
BASIS_WEIGHTS = (
    38, 34, 38, 30, 42, 34, 26, 30, 42, 30, 50, 30, 38, 42, 34, 22, 32, 32,
    32, 30, 32, 32, 30, 22, 24, 36, 20, 36, 28, 36, 28, 32, 32, 32, 32, 32,
)
SUPPORTS = (
    64691900160,
    1034819666160,
    280375465144335,
    4772259772306660006937399132160,
    15509841550538713979819718082560,
    1216944648758260568639796318044160,
    3955070108453721685622467917250560,
)
GENERATORS = (
    64691900160,
    1034819666160,
    280375465144335,
    4772259772306660006937399132160,
    15509841550538713979819718082560,
    1216944648758260568639796318044160,
    3955070108453721685622467917250560,
    4443670059850152665101255383351297,
    476478169960083547941896362557442,
    1235404508498744078868673813159940,
    9983029542622351334877321371656,
    1551087412582331123977819014078480,
    333427041513561210778684215566368,
    2596466671826523360078412021669952,
    389342703893815899092640717774976,
    3833216057007571418503107247251712,
    432611841641411318609815106396672,
    2920587414949371429908798658749440,
    454485081471164625171710277756928,
    1225342658187465785230322160381952,
    4146009544401891323911366300975104,
    3306510103253472586250966597304320,
    1622990553999583501864018977226752,
    263432417834582793991910927106048,
    2435278157458505060063050639343616,
    476517444942813366547851144855552,
    3172674985599289618361799917174784,
)
SUPPORT_SHA256 = (
    "ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3"
)
GENERATOR_LIST_SHA256 = (
    "2d580566f960c80d3f0f6f76342e83a4bf9b650ee9697226e58d8cc15da7da98"
)
BASIS_LIST_SHA256 = (
    "c93a6ec3f6d61b3bbf4086218c723761e517bc42ac2c26f551436d271a081e9d"
)
JSON_LIST_SHA256 = (
    "3a316d6d3226f84c1e46e4447fa8d5fd800bff4a1bc6498152523cd4a602b69b"
)
SELECTED_KAPPA = "781451/250000000"
PAIRS = ((0, 1), (2, 3), (4, 5), (6, 7))
MATCHINGS = (((0, 3), (1, 2)), ((0, 2), (1, 3)), ((0, 1), (2, 3)))
SPINOR_REPS = ((0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 1), (0, 1, 1, 0))
DIMENSION_MESSAGE = "dimension exceeds 27"
BATCH_COUNT_MESSAGE = "batch count exceeds 65536"
DEPENDENT_MESSAGE = "dependent generators"


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
    selected = json.loads(
        (ROOT / "certificates/selected-result.json").read_text(encoding="utf-8")
    )
    need(selected["kappa"] == SELECTED_KAPPA, "selected kappa changed")
    return checked


def support_hash(words):
    payload = json.dumps(sorted(word for word in words if word)).encode()
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
        run_name="p112_length27_model",
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
    need(len(frames) == len(set(frames)) == FRAME_COUNT, "live 8-frame count")
    frames = tuple(sorted(frames))
    degree = [0] * WIDTH
    for frame in frames:
        need(len(frame) == FRAME_SIZE, "frame length")
        for index in frame:
            degree[index] += 1
        need(
            all(
                dot(lines[live[i]], lines[live[j]]) == 0
                for i, j in combinations(frame, 2)
            ),
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
    free = tuple(coordinate for coordinate in range(WIDTH) if coordinate not in pivots)
    need(len(pivots) == RANK and free == FREE_COORDINATES, "P112 frame-code rank")
    basis = []
    for coordinate in free:
        vector = 1 << coordinate
        for pivot in order:
            if (pivots[pivot] & vector).bit_count() % 2:
                vector |= 1 << pivot
        basis.append(vector)
    basis = tuple(basis)
    need(tuple(vector.bit_count() for vector in basis) == BASIS_WEIGHTS, "basis weights")
    for index, vector in enumerate(basis):
        pattern = tuple((vector >> place) & 1 for place in free)
        identity = tuple(int(place == index) for place in range(DIMENSION))
        need(pattern == identity, "free coordinates are not a basis identity")
        need(all((vector & row).bit_count() % 2 == 0 for row in rows), "basis left the code")
    digest = sha256(json.dumps(list(basis)).encode()).hexdigest()
    need(digest == BASIS_LIST_SHA256, "basis-list hash " + digest)
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


def absorb(pivots, row):
    """Return whether `row` is independent under the engine's high-bit scan."""
    residual = row
    for pivot in range(WIDTH - 1, -1, -1):
        if residual >> pivot & 1:
            if pivot in pivots:
                residual ^= pivots[pivot]
            else:
                pivots[pivot] = residual
                return True
    return False


def extend_supports(supports, basis):
    """Published supports, then basis vectors that remain independent."""
    pivots = {}
    chosen = []
    for row in supports:
        need(absorb(pivots, row), "a published support is dependent")
        chosen.append(row)
    added = []
    for index, row in enumerate(basis):
        if len(chosen) == TUPLE_LENGTH:
            break
        if absorb(pivots, row):
            chosen.append(row)
            added.append(index)
    need(len(chosen) == TUPLE_LENGTH, "the extension did not reach length 27")
    need(tuple(added) == tuple(range(20)), "the first twenty basis vectors were not all used")
    return tuple(chosen)


def in_span(word, generators):
    pivots = {}
    for row in generators:
        need(absorb(pivots, row), "span test received a dependent generator")
    residual = word
    for pivot in range(WIDTH - 1, -1, -1):
        if residual >> pivot & 1:
            if pivot not in pivots:
                return False
            residual ^= pivots[pivot]
    return residual == 0


def disjoint_support_span(supports):
    """Proof check: disjoint weight-16 words have no other light combination.

    The XOR of a subset has weight 16 times the subset size, because bits from
    distinct supports never cancel. Weight at most 16 holds for the empty sum
    and the seven singletons, and for no other subset.
    """
    covered = 0
    for word in supports:
        need(word.bit_count() == WEIGHT_BOUND, "a support is not weight 16")
        need(covered & word == 0, "two supports meet")
        covered |= word
    need(covered == (1 << WIDTH) - 1, "the supports do not partition the 112 bits")
    for size in range(2, len(supports) + 1):
        need(WEIGHT_BOUND * size > WEIGHT_BOUND, "a multiple sum could stay at weight 16")


def gray_low(generators, maximum):
    """List every span word of weight at most `maximum`, each subset once.

    At index i the coefficient mask is the binary-reflected Gray code
    i xor (i >> 1). That map is a bijection of the coefficient integers, so
    the loop visits each of the 2**len(generators) combinations once. The
    bit flipped between i and i+1 is the trailing-zero count of i+1.
    """
    limit = 1 << len(generators)
    word = 0
    mask = 0
    found = []
    for index in range(limit):
        if mask != index ^ (index >> 1):
            raise ValueError("gray coefficient left index " + str(index))
        if word.bit_count() <= maximum:
            found.append(word)
        nxt = index + 1
        if nxt == limit:
            break
        bit = (nxt & -nxt).bit_length() - 1
        word ^= generators[bit]
        mask ^= 1 << bit
    return found


def toy_gray_control():
    found = gray_low((1, 2, 4, 8), 1)
    need(set(found) == {0, 1, 2, 4, 8}, "toy weight-1 census changed")
    entire = gray_low((1, 2, 4, 8), 4)
    need(len(entire) == len(set(entire)) == 16, "toy census missed a combination")


def bind_engine():
    binary = run_path(
        str(ROOT / "research/e7-bitsliced-exhaustion/binary.py"),
        run_name="p112_length27_population",
    )
    engine_ns = run_path(
        str(ROOT / "research/e7-intersection-counters/engine.py"),
        run_name="p112_length27_engine",
    )
    engine = engine_ns["low_weight_words"]
    signature = inspect.signature(engine)
    for name in ("population_planes", "at_most"):
        parameter = signature.parameters[name]
        need(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY,
            name + " is not keyword-only on the intersection engine",
        )
    source = inspect.getsource(engine_ns["checked_rows"])
    need('need(index < 27, "dimension exceeds 27")' in source, "dimension guard text changed")
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
    bound = partial(
        engine,
        population_planes=binary["population_planes"],
        at_most=binary["at_most"],
    )
    return bound, engine_ns["checked_rows"]


def stream_outcome(engine, generators, batch):
    stream = engine(generators, WIDTH, WEIGHT_BOUND, batch)
    try:
        return list(stream), None
    except ValueError as exc:
        return [], str(exc)
    finally:
        stream.close()


def check():
    need(
        sha256(json.dumps([1, 2]).encode()).hexdigest() == JSON_LIST_SHA256,
        "JSON list encoding changed",
    )
    need(len(GENERATORS) == TUPLE_LENGTH, "pinned tuple length")
    need(GENERATORS[: len(SUPPORTS)] == SUPPORTS, "the tuple does not start with the supports")
    need(
        sha256(json.dumps(list(GENERATORS)).encode()).hexdigest() == GENERATOR_LIST_SHA256,
        "pinned generator-list hash changed",
    )
    need(HIGH_OFFSETS == 128 and SPAN_WORDS == 134217728, "span shape")
    need(TUPLE_LENGTH - NAMED_BATCH == 7 and TUPLE_LENGTH - 10 == 17, "batch guards")
    authenticate()
    lines, live = pinned_model()
    frames = orthogonal_frames(lines, live)
    rows = tuple(sum(1 << index for index in frame) for frame in frames)
    basis = kernel(rows)
    rebuilt = partition_masks(lines, live)
    need(tuple(sorted(rebuilt)) == tuple(sorted(SUPPORTS)), "partition integers changed")
    digest = support_hash(SUPPORTS)
    need(digest == SUPPORT_SHA256, "support hash " + digest)
    dropped = support_hash(SUPPORTS[1:])
    need(dropped != SUPPORT_SHA256, "dropping one support kept the hash")
    disjoint_support_span(SUPPORTS)
    generators = extend_supports(SUPPORTS, basis)
    need(generators == GENERATORS, "the extension does not match the pinned 27-tuple")
    need(generators[len(SUPPORTS):] == basis[:20], "the tail is not basis vectors 0..19")
    need(generators != basis[:TUPLE_LENGTH], "the tuple collapsed to the ordered 27-prefix")
    inside = [word for word in SUPPORTS if in_span(word, basis[:TUPLE_LENGTH])]
    outside = [word for word in SUPPORTS if word not in inside]
    need(inside == list(SUPPORTS[:3]), "the ordered prefix does not contain the first three supports")
    need(outside == list(SUPPORTS[3:]), "the ordered prefix does not miss the last four supports")
    for word in SUPPORTS:
        need(in_span(word, generators), "a support left the 27-span")
    for vector in generators:
        need(0 < vector < 1 << WIDTH, "generator outside 1..2^112-1")
        need(
            all((vector & row).bit_count() % 2 == 0 for row in rows),
            "a generator leaves the frame code",
        )
    engine, checked_rows = bind_engine()
    admitted, count = checked_rows(generators, WIDTH, WEIGHT_BOUND, NAMED_BATCH)
    need(len(admitted) == TUPLE_LENGTH and count == LANE_GENERATORS, "batch 20 rejected the 27-tuple")
    toy_gray_control()
    census = gray_low(generators, WEIGHT_BOUND)
    need(len(census) == len(set(census)) == 8, "the 27-span census is not eight distinct words")
    need(set(census) == set(SUPPORTS) | {0}, "the 27-span census is not the eight-word set")
    need(support_hash(census) == SUPPORT_SHA256, "census hash changed")
    yielded, message = stream_outcome(engine, generators, NAMED_BATCH)
    need(message is None, "the engine refused the 27-tuple: " + str(message))
    need(len(yielded) == len(set(yielded)) == 8, "the engine stream is not eight distinct words")
    missed = sorted(set(SUPPORTS) - set(yielded))
    extra = sorted(set(yielded) - set(SUPPORTS) - {0})
    need(missed == [] and extra == [], "missed " + str(missed) + " extra " + str(extra[:8]))
    need(0 in yielded, "the engine omitted zero")
    need(set(yielded) == set(census), "the engine stream differs from the Gray-code census")
    need(support_hash(yielded) == SUPPORT_SHA256, "engine hash changed")
    duplicate, duplicate_message = stream_outcome(engine, (generators[0], generators[0]), NAMED_BATCH)
    need(
        duplicate == [] and duplicate_message == DEPENDENT_MESSAGE,
        "a repeated generator produced " + str(duplicate_message),
    )
    longer, longer_message = stream_outcome(engine, generators + (generators[0],), NAMED_BATCH)
    need(
        longer == [] and longer_message == DIMENSION_MESSAGE,
        "length 28 produced " + str(longer_message),
    )
    small_batch, small_message = stream_outcome(engine, generators, 10)
    need(
        small_batch == [] and small_message == BATCH_COUNT_MESSAGE,
        "batch size 10 produced " + str(small_message),
    )
    return {
        "status": "PASS_P112_LENGTH27_INTERSECTION_RETURN",
        "claim_proof": "seven disjoint weight-16 supports span exactly eight light words",
        "claim_census": "exhaustive Gray code of one 27-dimensional span",
        "claim_comparison": "one intersection-counter stream at batch size 20",
        "width": WIDTH,
        "frames": FRAME_COUNT,
        "rank": RANK,
        "code_dimension": DIMENSION,
        "generators": TUPLE_LENGTH,
        "support_generators": len(SUPPORTS),
        "appended_basis_indices": list(range(20)),
        "named_batch": NAMED_BATCH,
        "lane_generators": LANE_GENERATORS,
        "high_offset_batches": HIGH_OFFSETS,
        "span_words": SPAN_WORDS,
        "census_words": len(census),
        "engine_words": len(yielded),
        "sets_equal": True,
        "missed_supports": missed,
        "extra_words": extra,
        "prefix_contains_supports": len(inside),
        "prefix_misses_supports": len(outside),
        "supports_sha256": SUPPORT_SHA256,
        "generator_list_sha256": GENERATOR_LIST_SHA256,
        "dimension_guard_raised": False,
        "engine_source_edited": False,
        "codeword_enumeration_of_the_36_generator_code": False,
        "bit_lane_iterator_replayed": False,
        "timing_measured": False,
        "selected_kappa": SELECTED_KAPPA,
        "kappa_changed": False,
    }


if __name__ == "__main__":
    result = check()
    print(
        "PASS_P112_LENGTH27_INTERSECTION_RETURN"
        " batch={named_batch}"
        " generators={generators}"
        " span_words={span_words}"
        " words={engine_words}"
        " hash={supports_sha256}"
        " equal={sets_equal}"
        " missed={missed}"
        " extra={extra}"
        " timed=false"
        " no_new_kappa=true".format(
            missed=len(result["missed_supports"]),
            extra=len(result["extra_words"]),
            **result,
        )
    )
    print(json.dumps(result, indent=2, sort_keys=True))
