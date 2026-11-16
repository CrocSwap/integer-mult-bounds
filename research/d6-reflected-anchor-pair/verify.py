#!/usr/bin/env python3
"""One simple reflection of the pinned D6 anchor pair.

The reflected complement is a different 30-line list. Every coordinate
permutation that carries the image pair back to the pinned pair transports
the partner supports onto the recorded support set. The weight-at-most-2
words of the reflected frame code are exactly those partner indicators.
"""

import json
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations, product
from math import factorial
from pathlib import Path
from runpy import run_path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH = 30
FRAME_COUNT = 15
RANK = 10
DIMENSION = 20
VECTORS_AT_MOST_2 = 1 + 30 + 435
PERMUTATIONS = 40320
CARRYING = 1440
CHOSEN = 3
ANCHORS = ((2, 2, 0, 0, 0, 0, 0, 0), (2, -2, 0, 0, 0, 0, 0, 0))
ALPHA = (0, -2, 2, 0, 0, 0, 0, 0)
IMAGES = ((2, 0, 2, 0, 0, 0, 0, 0), (2, 0, -2, 0, 0, 0, 0, 0))
SPINOR_IMAGES = ((2, 2, 0, 0, 0, 0, 0, 0), (1, -1, 1, 1, 1, 1, 1, -1))
SIGMA = (0, 2, 1, 3, 4, 5, 6, 7)
IDENTITY = tuple(range(8))
MOVES = (True, False, False, True, False, False, False, False)
CARRYING_BY_ROOT = (0, 1440, 1440, 1440, 1440, 1440, 1440, 1440)
SIMPLE = (
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)
LINES_SHA256 = "bd3d7efd8a94a7d0a6a7339cfd95805bb6907f3951ff67e9669b317655869538"
NEW_LINES_SHA256 = "bcc5dc15f642aca7bdcc1249d2588869b6510aa8e08cde8688fe340c665435b5"
SUPPORTS_SHA256 = "23a7b374a6bc62bc2aca47843d52a01fa8e791ed3a98085133829d816c5094e8"
SUPPORTS = (
    3, 24, 36, 768, 1152, 2112, 98304, 147456, 270336, 528384,
    50331648, 75497472, 138412032, 270532608, 537919488,
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
    need(checked == 2, "two live inputs")
    return checked


def dot(left, right):
    return sum(value * other for value, other in zip(left, right, strict=True))


def canon(vector):
    first = next(value for value in vector if value)
    return tuple(vector) if first > 0 else tuple(-value for value in vector)


def reflect(vector, alpha):
    pairing = dot(vector, alpha)
    need(pairing % 4 == 0, "reflection coefficient is not integral")
    coefficient = pairing // 4
    return tuple(value - coefficient * step for value, step in zip(vector, alpha, strict=True))


def permute(vector, sigma):
    """(P_sigma v)[i] = v[sigma[i]]."""
    return tuple(vector[sigma[index]] for index in range(8))


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
    lines = set(roots)
    need(len(roots) == len(lines) == 120, "E8 line count")
    need(all(dot(root, root) == 8 for root in lines), "E8 norms")
    return lines


def coordinate_lines(axes):
    lines = []
    for i, j in combinations(axes, 2):
        for sign in (2, -2):
            root = [0] * 8
            root[i], root[j] = 2, sign
            lines.append(canon(root))
    return tuple(sorted(set(lines)))


def support_of(line):
    return tuple(index for index, value in enumerate(line) if value)


def line_digest(lines):
    payload = json.dumps([list(line) for line in lines], separators=(",", ":"))
    return sha256(payload.encode()).hexdigest()


def support_digest(masks):
    return sha256(json.dumps(list(masks)).encode()).hexdigest()


def pair_of(vectors):
    return frozenset(canon(vector) for vector in vectors)


def orthogonal_lines(lines, anchors):
    return tuple(sorted(line for line in lines if all(dot(line, anchor) == 0 for anchor in anchors)))


def load_simple_system():
    loaded = run_path(str(ROOT / "research/p112-a3-six-flat/geometry.py"))["SIMPLE"]
    need(tuple(loaded) == SIMPLE, "pinned simple system changed")
    need(SIMPLE[CHOSEN] == ALPHA, "chosen simple root changed")
    return SIMPLE


def solve(matrix, rhs):
    rows = [
        [Fraction(entry) for entry in row] + [Fraction(value)]
        for row, value in zip(matrix, rhs, strict=True)
    ]
    for column in range(8):
        pivot = next((index for index in range(column, 8) if rows[index][column]), None)
        need(pivot is not None, "singular simple system")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [entry / scale for entry in rows[column]]
        for index in range(8):
            if index != column:
                factor = rows[index][column]
                rows[index] = [
                    entry - factor * other
                    for entry, other in zip(rows[index], rows[column], strict=True)
                ]
    return tuple(row[8] for row in rows)


def certify_simple_system(lines):
    need(len(SIMPLE) == 8, "simple-root count")
    for alpha in SIMPLE:
        need(dot(alpha, alpha) == 8, "simple norm")
        need(canon(alpha) in lines, "simple root is not an E8 line")
    for alpha in SIMPLE:
        for line in lines:
            image = canon(reflect(line, alpha))
            need(image in lines, "simple reflection leaves E8")
    matrix = tuple(zip(*SIMPLE, strict=True))
    one_sign = 0
    simple_recovered = []
    for line in sorted(lines):
        coordinates = solve(matrix, line)
        need(all(value.denominator == 1 for value in coordinates), "nonintegral simple coordinates")
        positive = all(value >= 0 for value in coordinates)
        negative = all(value <= 0 for value in coordinates)
        need(positive or negative, "a root has mixed simple coordinates")
        one_sign += 1
        if sum(abs(value) for value in coordinates) == 1:
            simple_recovered.append(canon(line))
    need(one_sign == 120, "one-sign census missed a line")
    need(len(simple_recovered) == 8, "simple-line count")
    need(pair_of(simple_recovered) == pair_of(SIMPLE), "simple roots are not the coefficient-one lines")
    for index, alpha in enumerate(SIMPLE):
        coordinates = solve(matrix, alpha)
        identity = tuple(Fraction(int(place == index)) for place in range(8))
        need(coordinates == identity, "simple root is not a basis vector")
    gram = [[dot(left, right) // 4 for right in SIMPLE] for left in SIMPLE]
    need(all(gram[index][index] == 2 for index in range(8)), "Cartan diagonal")
    edges = [
        (left, right)
        for left in range(8)
        for right in range(left)
        if gram[left][right] == -1
    ]
    need(all(gram[left][right] in (0, -1) for left in range(8) for right in range(left)),
         "Cartan off-diagonal")
    need(len(edges) == 7, "E8 has seven simple edges")
    degrees = [sum(node in edge for edge in edges) for node in range(8)]
    need(sorted(degrees) == [1, 1, 1, 2, 2, 2, 2, 3], "E8 simple degrees")
    joint = next(node for node, degree in enumerate(degrees) if degree == 3)
    arms = []
    starts = [next(node for node in edge if node != joint) for edge in edges if joint in edge]
    need(len(starts) == 3, "E8 branch")
    for start in starts:
        previous, current, length = joint, start, 1
        while True:
            nxt = [
                next(node for node in edge if node != current)
                for edge in edges
                if current in edge and previous not in edge
            ]
            if not nxt:
                break
            need(len(nxt) == 1, "simple Dynkin arm")
            previous, current = current, nxt[0]
            length += 1
        arms.append(length)
    need(sorted(arms) == [1, 2, 4], "E8 Dynkin arm lengths")
    return gram


def load_pinned_lines(lines):
    payload = json.loads((ROOT / "research/d6-punctured-frame-code/ROOTS.json").read_text(encoding="utf-8"))
    anchors = tuple(tuple(anchor) for anchor in payload["anchors"])
    stored = tuple(tuple(line) for line in payload["lines"])
    need(anchors == ANCHORS, "pinned anchors changed")
    need(pair_of(anchors) <= lines, "pinned anchor is not an E8 line")
    need(dot(*anchors) == 0, "pinned anchors are not orthogonal")
    complement = orthogonal_lines(lines, anchors)
    need(stored == complement, "ROOTS.json is not the orthogonal complement")
    need(line_digest(stored) == LINES_SHA256, "pinned line hash changed")
    need(stored == coordinate_lines((2, 3, 4, 5, 6, 7)), "pinned lines are not the coordinate D6")
    return stored


def partner_masks(lines):
    groups = {}
    for index, line in enumerate(lines):
        groups.setdefault(support_of(line), []).append(index)
    masks = []
    for indices in groups.values():
        need(len(indices) == 2, "an edge does not have two signs")
        masks.append((1 << indices[0]) | (1 << indices[1]))
    masks = tuple(sorted(masks))
    need(len(masks) == FRAME_COUNT and len(set(masks)) == FRAME_COUNT, "partner count")
    covered = 0
    for mask in masks:
        need(mask.bit_count() == 2 and covered & mask == 0, "partners overlap")
        covered |= mask
    need(covered == (1 << WIDTH) - 1, "a line has no partner")
    return masks


def transport_mask(mask, mapping):
    transported = 0
    while mask:
        bit = (mask & -mask).bit_length() - 1
        mask ^= 1 << bit
        transported |= 1 << mapping[bit]
    return transported


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


def matching_frames(lines, axes):
    lookup = {line: index for index, line in enumerate(lines)}
    frames = []
    for matching in perfect_matchings(axes):
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
        need(len(frame) == 6, "frame length")
        need(all(dot(lines[i], lines[j]) == 0 for i, j in combinations(frame, 2)),
             "matching frame is not orthogonal")
        covered = []
        for index in frame:
            covered.extend(support_of(lines[index]))
        need(sorted(covered) == sorted(axes + axes), "a frame does not cover both signs")
    return frames


def enumerated_frames(lines):
    """Every increasing 6-clique, once.

    i < j < k < x < y < z is enforced by keeping only higher indices in each
    neighborhood. The search finishes under the state cap, so the list is the
    whole set of orthogonal 6-frames.
    """
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
    return frames, steps


def frame_rows(frames):
    rows = []
    degree = [0] * WIDTH
    for frame in frames:
        row = 0
        for index in frame:
            degree[index] += 1
            row |= 1 << index
        rows.append(row)
    need(len(set(degree)) == 1 and degree[0] == 3, "frame degree is not 3")
    total = 0
    for row in rows:
        total ^= row
    need(total == (1 << WIDTH) - 1, "frame sum is not the all-one word")
    return tuple(rows)


def in_kernel(word, rows):
    return all((word & row).bit_count() % 2 == 0 for row in rows)


def screen_low_weight(rows, partners):
    found = {0}
    tested = 1
    for index in range(WIDTH):
        tested += 1
        word = 1 << index
        if in_kernel(word, rows):
            found.add(word)
    for left, right in combinations(range(WIDTH), 2):
        tested += 1
        word = (1 << left) | (1 << right)
        if in_kernel(word, rows):
            found.add(word)
    need(tested == VECTORS_AT_MOST_2, "weight-at-most-2 domain changed")
    need(found == set(partners) | {0}, "weight at most 2 is not the partner partition")
    return found, tested


def incidence_rank(rows):
    echelon = {}
    for row in rows:
        for pivot in range(WIDTH - 1, -1, -1):
            if row >> pivot & 1:
                if pivot in echelon:
                    row ^= echelon[pivot]
                else:
                    echelon[pivot] = row
                    break
    return len(echelon)


def positive_words_have_weight(words, weight):
    return all(word.bit_count() == weight for word in words if word)


def survey_simple_roots(pinned_lines, pinned_masks, reflected_lines, reflected_masks):
    """Every simple root, and every coordinate permutation of the eight axes.

    itertools.permutations(range(8)) yields each of the 8! tuples once, in
    lexicographic order. For the chosen root the same pass transports every
    carrying permutation.
    """
    pinned = pair_of(ANCHORS)
    old_index = {line: index for index, line in enumerate(pinned_lines)}
    counts = []
    moves = []
    images_by_root = []
    first = None
    identity_carries = False
    saw_identity_map = False
    saw_moved_map = False
    axis_count = 0
    seen_total = 0
    for index, alpha in enumerate(SIMPLE):
        images = tuple(canon(reflect(anchor, alpha)) for anchor in ANCHORS)
        images_by_root.append(images)
        moved = pair_of(images) != pinned
        moves.append(moved)
        count = 0
        seen = 0
        for sigma in permutations(range(8)):
            seen += 1
            carried = pair_of(permute(image, sigma) for image in images) == pinned
            if index == CHOSEN:
                axis_ok = {sigma[0], sigma[1]} == {0, 2}
                if axis_ok:
                    axis_count += 1
                need(carried == axis_ok, "carrying permutations are not the axis transports")
            if not carried:
                continue
            count += 1
            if index != CHOSEN:
                continue
            if first is None:
                first = sigma
            if sigma == IDENTITY:
                identity_carries = True
            mapping = []
            for line in reflected_lines:
                image = canon(permute(line, sigma))
                need(image in old_index, "a transported line left the pinned list")
                mapping.append(old_index[image])
            need(len(set(mapping)) == WIDTH, "transport is not a bijection of the lines")
            transported = tuple(sorted(transport_mask(mask, mapping) for mask in reflected_masks))
            need(transported == pinned_masks, "a carrying permutation changed the support set")
            if mapping == list(range(WIDTH)):
                saw_identity_map = True
            else:
                saw_moved_map = True
        need(seen == PERMUTATIONS, "coordinate-permutation census is short")
        seen_total += seen
        counts.append(count)
    need(seen_total == 8 * PERMUTATIONS, "simple-root census missed a permutation")
    need(factorial(8) == PERMUTATIONS, "8! changed")
    need(tuple(moves) == MOVES, "which simple roots move the pair changed")
    need(tuple(counts) == CARRYING_BY_ROOT, "carrying-permutation counts changed")
    need(first == SIGMA, "lexicographic carrying permutation changed")
    need(not identity_carries, "the identity carries the reflected pair")
    need(saw_identity_map and saw_moved_map, "transport saw only one index-map kind")
    need(axis_count == CARRYING, "axis-transport count changed")
    need(images_by_root[0] == SPINOR_IMAGES, "spinor image changed")
    need(images_by_root[CHOSEN] == IMAGES, "chosen image changed")
    need(counts[CHOSEN] == 2 * factorial(6) == CARRYING, "2!·6! count changed")
    chosen_moves = [index for index, moved in enumerate(moves) if moved and counts[index]]
    need(chosen_moves[0] == CHOSEN, "the first movable carried root changed")
    return {
        "moves": moves,
        "carrying": counts,
        "first_permutation": list(first),
        "identity_index_map_seen": saw_identity_map,
        "moved_index_map_seen": saw_moved_map,
    }


def outside_root_premise(lines):
    """The next coordinate root moves the pair. Its transport is not run."""
    outside = (0, 2, 0, -2, 0, 0, 0, 0)
    need(canon(outside) in lines, "the outside root is not an E8 line")
    need(all(canon(outside) != canon(alpha) for alpha in SIMPLE), "the outside root is simple")
    images = tuple(canon(reflect(anchor, outside)) for anchor in ANCHORS)
    need(pair_of(images) != pair_of(ANCHORS), "the outside root fixes the pair")
    need(dot(*images) == 0, "the outside image is not orthogonal")
    return images


def absolute_obstruction():
    """No signed coordinate permutation preserves both absolute multisets."""
    spinor = SPINOR_IMAGES[1]
    need(tuple(sorted(abs(value) for value in spinor)) == (1,) * 8, "spinor absolute values")
    for anchor in ANCHORS:
        absolute = tuple(sorted(abs(value) for value in anchor))
        need(absolute == (0, 0, 0, 0, 0, 0, 2, 2), "pinned absolute values")
        need(absolute != tuple(sorted(abs(value) for value in spinor)),
             "a signed permutation could match the spinor")


def check():
    authenticate()
    lines = e8_lines()
    simple = load_simple_system()
    certify_simple_system(lines)
    pinned_lines = load_pinned_lines(lines)
    pinned_masks = partner_masks(pinned_lines)
    need(pinned_masks == SUPPORTS, "pinned partner masks changed")
    need(support_digest(pinned_masks) == SUPPORTS_SHA256, "pinned support hash changed")
    absolute_obstruction()
    outside_root_premise(lines)
    images = tuple(canon(reflect(anchor, ALPHA)) for anchor in ANCHORS)
    need(images == IMAGES, "reflected anchors changed")
    need(dot(*images) == 0, "reflected anchors are not orthogonal")
    need(pair_of(images) <= lines, "reflected anchor leaves E8")
    need(pair_of(images) != pair_of(ANCHORS), "the reflection fixes the pair")
    need(dot(reflect(ANCHORS[0], ALPHA), ANCHORS[1]) != 0,
         "the unreflected partner stayed orthogonal")
    reflected_lines = orthogonal_lines(lines, images)
    image_of_pinned = tuple(sorted(canon(reflect(line, ALPHA)) for line in pinned_lines))
    need(image_of_pinned == reflected_lines, "the reflection does not rebuild the complement")
    need(line_digest(reflected_lines) == NEW_LINES_SHA256, "reflected line hash changed")
    need(line_digest(reflected_lines) != LINES_SHA256, "the reflected list repeats the pinned list")
    occupied = {index for anchor in images for index, value in enumerate(anchor) if value}
    need(occupied == {0, 2}, "reflected anchors do not occupy axes 0 and 2")
    axes = tuple(index for index in range(8) if index not in occupied)
    need(reflected_lines == coordinate_lines(axes), "the complement is not the coordinate D6")
    for line in lines:
        if any(abs(value) == 1 for value in line):
            need(any(dot(line, anchor) != 0 for anchor in images),
                 "a spinor root is orthogonal to both reflected anchors")
    for left, right in combinations(range(WIDTH), 2):
        orthogonal = dot(reflected_lines[left], reflected_lines[right]) == 0
        same = support_of(reflected_lines[left]) == support_of(reflected_lines[right])
        disjoint = set(support_of(reflected_lines[left])).isdisjoint(support_of(reflected_lines[right]))
        need(orthogonal == (same or disjoint), "orthogonality is not the edge rule")
    reflected_masks = partner_masks(reflected_lines)
    frames = matching_frames(reflected_lines, axes)
    enumerated, steps = enumerated_frames(reflected_lines)
    need(enumerated == frames, "clique search missed a matching frame")
    rows = frame_rows(frames)
    screened, tested = screen_low_weight(rows, reflected_masks)
    rank = incidence_rank(rows)
    need(rank == RANK and WIDTH - rank == DIMENSION, "reflected incidence rank changed")
    survey = survey_simple_roots(pinned_lines, pinned_masks, reflected_lines, reflected_masks)
    need(support_digest(reflected_masks) == SUPPORTS_SHA256, "reflected supports changed the hash")
    dropped = tuple(mask for mask in reflected_masks if mask != reflected_masks[0])
    need(dropped != reflected_masks, "dropping one support left the list unchanged")
    need(support_digest(dropped) != SUPPORTS_SHA256, "dropping one support kept the hash")
    witness = reflected_masks[0]
    lighter = witness ^ (1 << (witness.bit_length() - 1))
    need(lighter.bit_count() == 1 and lighter not in screened, "a weight-1 word stayed in the set")
    forged = set(screened)
    forged.add(lighter)
    need(not positive_words_have_weight(forged, 2), "a weight-1 injection was accepted")
    stranger = (1 << 0) | (1 << 2)
    need(stranger.bit_count() == 2 and stranger not in screened, "a non-partner was in the set")
    need(permute(images[0], SIGMA) == ANCHORS[0], "sigma misses the first anchor")
    need(permute(images[1], SIGMA) == ANCHORS[1], "sigma misses the second anchor")
    need(simple[CHOSEN] == ALPHA, "simple root pin drifted")
    return {
        "status": "PASS_D6_REFLECTED_ANCHOR_PAIR",
        "simple_index": CHOSEN,
        "simple_root": list(ALPHA),
        "image_anchors": [list(anchor) for anchor in images],
        "axes": list(axes),
        "lexicographic_permutation": survey["first_permutation"],
        "carrying_permutations": survey["carrying"][CHOSEN],
        "carrying_by_simple_root": survey["carrying"],
        "pair_moves": survey["moves"],
        "identity_index_map_seen": survey["identity_index_map_seen"],
        "moved_index_map_seen": survey["moved_index_map_seen"],
        "width": WIDTH,
        "frames": FRAME_COUNT,
        "frame_degree": 3,
        "rank": rank,
        "dimension": DIMENSION,
        "clique_steps": steps,
        "vectors_at_most_2": tested,
        "supports": len(reflected_masks),
        "support_masks": list(reflected_masks),
        "lines_sha256": LINES_SHA256,
        "reflected_lines_sha256": NEW_LINES_SHA256,
        "supports_sha256": SUPPORTS_SHA256,
        "spinor_coordinate_permutations": survey["carrying"][0],
        "engine_loaded": False,
        "gray_census_run": False,
        "p112_built": False,
        "e6_census_replayed": False,
        "no_new_kappa": True,
    }


if __name__ == "__main__":
    result = check()
    print(
        "PASS_D6_REFLECTED_ANCHOR_PAIR"
        " simple={simple_index}"
        " permutations={carrying_permutations}"
        " width={width}"
        " frames={frames}"
        " dimension={dimension}"
        " supports={supports}"
        " vectors={vectors_at_most_2}"
        " hash_match=true"
        " spinor_coordinate_permutations={spinor_coordinate_permutations}"
        " engine=false"
        " no_new_kappa=true".format(**result)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
