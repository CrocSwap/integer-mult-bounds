#!/usr/bin/env python3
"""Coverage of the published bit-lane iterator on one D6 punctured frame code.

The closed-form screen, the literal doubling and the half-split do not call
low_weight_words. They score kernel membership by frame parity or by integer
popcount. The engine is then compared with that set on this basis alone.
"""

import json
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
SPLIT_AT = 10
AXES = (2, 3, 4, 5, 6, 7)
ANCHORS = ((2, 2, 0, 0, 0, 0, 0, 0), (2, -2, 0, 0, 0, 0, 0, 0))
FREE_COORDINATES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 20, 21, 22, 23, 24)
LINES_SHA256 = "bd3d7efd8a94a7d0a6a7339cfd95805bb6907f3951ff67e9669b317655869538"
SUPPORTS_SHA256 = "23a7b374a6bc62bc2aca47843d52a01fa8e791ed3a98085133829d816c5094e8"
WEIGHT_COUNTS = (
    1, 0, 15, 0, 105, 0, 1095, 0, 10965, 0, 59067, 0, 170125, 0, 282915, 0,
    282915, 0, 170125, 0, 59067, 0, 10965, 0, 1095, 0, 105, 0, 15, 0, 1,
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
        digest = sha256((ROOT / row["path"]).read_bytes()).hexdigest()
        need(digest == row["sha256"], "input hash mismatch: " + row["path"])
        checked += 1
    need(checked == 1, "one live input")
    return checked


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


def support_of(line):
    return tuple(index for index, value in enumerate(line) if value)


def load_lines():
    payload = json.loads((HERE / "ROOTS.json").read_text(encoding="utf-8"))
    anchors = tuple(tuple(anchor) for anchor in payload["anchors"])
    axes = tuple(payload["axes"])
    stored = tuple(tuple(line) for line in payload["lines"])
    need(anchors == ANCHORS, "pinned anchors changed")
    need(axes == AXES, "pinned axes changed")
    need(len(stored) == len(set(stored)) == WIDTH, "pinned line count")
    digest = sha256(json.dumps([list(line) for line in stored], separators=(",", ":")).encode()).hexdigest()
    need(digest == LINES_SHA256, "pinned line hash changed")
    roots = e8_lines()
    need(all(anchor in roots for anchor in anchors), "anchor is not an E8 line")
    need(dot(*anchors) == 0, "anchors are not orthogonal")
    complement = tuple(sorted(root for root in roots if all(dot(root, anchor) == 0 for anchor in anchors)))
    coordinate = coordinate_lines(axes)
    need(stored == complement == coordinate, "pinned lines are not this D6 slice")
    need(all(set(support_of(line)) <= set(axes) for line in stored), "a line leaves the six axes")
    return stored


def orthogonality_law(lines):
    supports = [support_of(line) for line in lines]
    need(all(len(item) == 2 for item in supports), "a line is not a coordinate edge")
    need(len(set(supports)) == FRAME_COUNT, "the fifteen edges are not simple")
    for left, right in combinations(range(WIDTH), 2):
        orthogonal = dot(lines[left], lines[right]) == 0
        same = supports[left] == supports[right]
        disjoint = set(supports[left]).isdisjoint(supports[right])
        need(orthogonal == (same or disjoint), "orthogonality is not the edge rule")
    return supports


def perfect_matchings(vertices):
    vertices = tuple(vertices)
    if not vertices:
        yield ()
        return
    first, rest = vertices[0], vertices[1:]
    for index, partner in enumerate(rest):
        remaining = rest[:index] + rest[index + 1:]
        for tail in perfect_matchings(remaining):
            yield ((first, partner),) + tail


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
        need(all(dot(lines[i], lines[j]) == 0 for i, j in combinations(frame, 2)),
             "matching frame is not orthogonal")
        covered = []
        for index in frame:
            covered.extend(support_of(lines[index]))
        need(sorted(covered) == sorted(AXES + AXES), "a frame does not use both signs on three edges")
    return frames


def enumerated_frames(lines):
    adjacency = [0] * WIDTH
    for i, j in combinations(range(WIDTH), 2):
        if dot(lines[i], lines[j]) == 0:
            adjacency[i] |= 1 << j
            adjacency[j] |= 1 << i
    frames = []
    steps = 0
    for i in range(WIDTH):
        first = adjacency[i] & ~((1 << (i + 1)) - 1)
        bits_i = first
        while bits_i:
            j = (bits_i & -bits_i).bit_length() - 1
            bits_i ^= 1 << j
            second = first & adjacency[j] & ~((1 << (j + 1)) - 1)
            bits_j = second
            while bits_j:
                steps += 1
                need(steps <= 100000, "frame enumeration exceeded its state cap")
                k = (bits_j & -bits_j).bit_length() - 1
                bits_j ^= 1 << k
                third = second & adjacency[k] & ~((1 << (k + 1)) - 1)
                pool = [t for t in range(k + 1, WIDTH) if third >> t & 1]
                if len(pool) < 3:
                    continue
                for x, y, z in combinations(pool, 3):
                    if (adjacency[x] >> y & 1) and (adjacency[x] >> z & 1) and (adjacency[y] >> z & 1):
                        frames.append((i, j, k, x, y, z))
    frames = tuple(sorted(frames))
    need(len(frames) == len(set(frames)), "enumerated frame repeated")
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
        pattern = tuple((vector >> place) & 1 for place in free)
        identity = tuple(int(place == index) for place in range(DIMENSION))
        need(pattern == identity, "free coordinates are not a basis identity")
        need(all((vector & row).bit_count() % 2 == 0 for row in rows), "a frame parity survives")
        basis.append(vector)
    return tuple(basis)


def partner_masks(supports):
    groups = {}
    for index, support in enumerate(supports):
        groups.setdefault(support, []).append(index)
    masks = []
    for indices in groups.values():
        need(len(indices) == 2, "an edge does not have two signs")
        masks.append((1 << indices[0]) | (1 << indices[1]))
    masks = tuple(sorted(masks))
    need(len(masks) == SUPPORT_COUNT, "partner count")
    need(len(set(masks)) == SUPPORT_COUNT, "partner mask repeated")
    covered = 0
    for mask in masks:
        need(mask.bit_count() == 2 and covered & mask == 0, "partners do not partition the lines")
        covered |= mask
    need(covered == (1 << WIDTH) - 1, "a line has no partner")
    return masks


def in_kernel(word, rows):
    return all((word & row).bit_count() % 2 == 0 for row in rows)


def screen_low_weight(rows, partners):
    found = {0}
    for index in range(WIDTH):
        word = 1 << index
        if in_kernel(word, rows):
            found.add(word)
    for left, right in combinations(range(WIDTH), 2):
        word = (1 << left) | (1 << right)
        if in_kernel(word, rows):
            found.add(word)
    need(found == set(partners) | {0}, "weight at most 2 is not the partner partition")
    need(all(in_kernel(mask, rows) for mask in partners), "a partner misses the kernel")
    return found


def span(generators):
    words = [0]
    for generator in generators:
        # Snapshot the current list. Extending from a live view of `words`
        # would follow the newly written vectors and never stop.
        words.extend([word ^ generator for word in words])
    need(len(set(words)) == len(words) == 1 << len(generators), "span repeats a word")
    return words


def census(basis):
    """Visit every kernel word once along the binary-reflected Gray code.

    The bit flipped between steps index-1 and index is the lowest set bit
    of index. The coefficient vector at that step is index XOR (index >> 1).
    Checking those free bits at every index shows the visit is bijective.
    """
    counts = [0] * (WIDTH + 1)
    low = set()
    word = 0
    limit = 1 << DIMENSION
    for index in range(limit):
        if index:
            word ^= basis[(index & -index).bit_length() - 1]
        gray = index ^ (index >> 1)
        for place, coordinate in enumerate(FREE_COORDINATES):
            need(((word >> coordinate) & 1) == ((gray >> place) & 1),
                 "Gray step left the free-coordinate identity")
        weight = word.bit_count()
        counts[weight] += 1
        if weight <= WEIGHT_BOUND:
            low.add(word)
    need(tuple(counts) == WEIGHT_COUNTS, "weight distribution changed")
    need(sum(counts) == limit, "census missed a codeword")
    return low, counts


def half_split(basis, low_dimension):
    need(0 < low_dimension < len(basis), "split must use both halves")
    lows = span(basis[:low_dimension])
    highs = span(basis[low_dimension:])
    need(len(lows) * len(highs) == 1 << len(basis), "halves do not cover the basis span")
    found = set()
    for high in highs:
        for low in lows:
            word = high ^ low
            if word.bit_count() <= WEIGHT_BOUND:
                found.add(word)
    return found


def engine_words(engine, basis, maximum, batch_bits):
    listed = list(engine(basis, WIDTH, maximum, batch_bits))
    need(len(listed) == len(set(listed)), "engine repeated a word")
    return set(listed)


def positive_words_have_weight(words, weight):
    return all(word.bit_count() == weight for word in words if word)


def check():
    authenticate()
    lines = load_lines()
    supports = orthogonality_law(lines)
    frames = combinatorial_frames(lines)
    need(enumerated_frames(lines) == frames, "clique search missed a matching frame")
    degree = [0] * WIDTH
    rows = []
    for frame in frames:
        row = 0
        for index in frame:
            degree[index] += 1
            row |= 1 << index
        rows.append(row)
    need(len(set(degree)) == 1 and degree[0] == 3, "frame degree is not 3")
    need(0 not in rows, "empty frame")
    total = 0
    for row in rows:
        total ^= row
    need(total == (1 << WIDTH) - 1, "frame sum is not the all-one word")
    partners = partner_masks(supports)
    screened = screen_low_weight(tuple(rows), partners)
    basis = kernel(tuple(rows))
    literal, counts = census(basis)
    need(literal == screened, "doubling changed the low-weight set")
    split = half_split(basis, SPLIT_AT)
    need(split == screened, "half-split changed the low-weight set")
    engine = run_path(
        str(ROOT / "research/e7-bitsliced-exhaustion/binary.py"),
        run_name="d6_frame_lane_engine",
    )["low_weight_words"]
    produced = {}
    for batch_bits in (16, 8):
        produced[batch_bits] = engine_words(engine, basis, WEIGHT_BOUND, batch_bits)
        need(produced[batch_bits] == screened, "engine batch " + str(batch_bits) + " changed the set")
    sharp = engine_words(engine, basis, WEIGHT_BOUND - 1, 8)
    need(sharp == {0}, "weight bound 1 still emitted a positive word")
    witness = partners[0]
    need(produced[16] - {witness} != screened, "dropping one support still compared equal")
    lighter = witness ^ (1 << (witness.bit_length() - 1))
    need(lighter.bit_count() == 1 and lighter not in screened, "clearing one partner bit stayed in the set")
    forged = set(screened)
    forged.add(lighter)
    need(not positive_words_have_weight(forged, WEIGHT_BOUND), "weight-one injection was accepted")
    stranger = (1 << 0) | (1 << 2)
    need(stranger not in screened and stranger.bit_count() == 2, "a non-partner weight-2 word was absent from the control")
    try:
        list(engine((basis[0], basis[0]), WIDTH, WEIGHT_BOUND, 4))
    except ValueError:
        rejected = True
    else:
        rejected = False
    need(rejected, "a repeated generator was accepted")
    positive = sorted(word for word in screened if word)
    digest = sha256(json.dumps(positive).encode()).hexdigest()
    need(digest == SUPPORTS_SHA256, "support-set hash changed")
    need(positive == list(partners), "the sorted supports are not the partner masks")
    return {
        "status": "PASS_D6_PUNCTURED_FRAME_CODE",
        "width": WIDTH,
        "frames": FRAME_COUNT,
        "frame_size": FRAME_SIZE,
        "frame_degree": degree[0],
        "rank": RANK,
        "dimension": DIMENSION,
        "free_coordinates": list(FREE_COORDINATES),
        "minimum_positive_weight": WEIGHT_BOUND,
        "weight_at_most_2": len(screened),
        "minimum_supports": len(positive),
        "support_masks": positive,
        "distinct_codewords": 1 << DIMENSION,
        "weight_counts": list(counts),
        "split": SPLIT_AT,
        "engine_batches": [16, 8],
        "bound_1_words": len(sharp),
        "dependent_generator_rejected": rejected,
        "lines_sha256": LINES_SHA256,
        "supports_sha256": digest,
        "e6_census_replayed": False,
        "p112_built": False,
        "intersection_engine_loaded": False,
        "timing_remeasured": False,
        "no_new_kappa": True,
    }


if __name__ == "__main__":
    result = check()
    print(
        "PASS_D6_PUNCTURED_FRAME_CODE"
        " width={width}"
        " frames={frames}"
        " dimension={dimension}"
        " minimum={minimum_positive_weight}"
        " supports={minimum_supports}"
        " codewords={distinct_codewords}"
        " batches=16,8"
        " split=10"
        " e6_census_replayed=false"
        " p112_built=false"
        " no_new_kappa=true".format(**result)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
