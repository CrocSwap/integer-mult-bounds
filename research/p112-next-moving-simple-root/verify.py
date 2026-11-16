#!/usr/bin/env python3
"""The next moving simple root of the reflected P112 frame.

Continue the pinned simple-root, then punctured-line scan past the first
moving pair. The next simple root that moves a punctured line rebuilds its
own 112-line complement. One half-split of that kernel is compared with the
transported images of the seven supports recorded for the unreflected frame.
The scanner lists every kernel word once. It does not call the bit-lane
iterator, and it does not rerun the first reflection's half-split.
"""

import json
import subprocess
import sys
import tempfile
from fractions import Fraction
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
SPLIT_AT = 18
SIMPLE_INDEX = 3
PUNCTURE_INDEX = 0
MOVED_LINES = 4
FIXED_BITS = 62
FIXED_ROOTS = (1, 2, 4, 6)
LATER_ROOTS = (5, 7)
LINE_SHA256 = "36e3ad43dbfd53d71b20cfac522fbf9c0c1c065054994b9c81767a228d7e6f3c"
RECORDED_SUPPORT_SHA256 = "ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3"
TRANSPORTED_SUPPORT_SHA256 = "0ab33f7ea89182ea1cbc5ca06d5f3bdcaeb72a08aef3eaceb33e6a43bbb96636"
FIRST_LINE_SHA256 = "a2ac7049d9eef1cff8af1eec35b084e6d261efad5311625e5356cceafe260da7"
FIRST_TRANSPORTED_SHA256 = "9ce7e5edc72ee3104d62cb068146b73840e9a3c42c4132403dece70c8146cccb"
NAMED_ROOT = (2, 2, 0, 0, 0, 0, 0, 0)
IMAGE_ROOT = (2, 0, 2, 0, 0, 0, 0, 0)
IMAGE_PUNCTURE = (2, 3, 16, 17, 44, 45, 54, 55)
FREE_COORDINATES = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 20, 22, 24, 26,
    28, 32, 34, 36, 40, 42, 48, 49, 50, 51, 52, 56, 58, 64, 80,
)
FIRST_FREE_COORDINATES = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 17, 19, 21, 25, 26, 27,
    28, 30, 34, 36, 38, 42, 43, 52, 53, 54, 55, 56, 60, 68, 84,
)
BASIS_WEIGHTS = (
    38, 34, 38, 30, 42, 34, 26, 30, 42, 30, 50, 30, 38, 32, 32, 30, 32, 32, 42,
    34, 22, 32, 30, 22, 24, 36, 20, 36, 28, 36, 28, 32, 32, 32, 32, 32,
)
RECORDED_SUPPORTS = (
    64691900160,
    1034819666160,
    280375465144335,
    4772259772306660006937399132160,
    15509841550538713979819718082560,
    1216944648758260568639796318044160,
    3955070108453721685622467917250560,
)
TRANSPORTED_SUPPORTS = (
    68451290880,
    1031047741680,
    280375477678095,
    4814039611113066403813140725760,
    15468061711732307582943976488960,
    1216944811960755906164784113909760,
    3955069945251226348097480121384960,
)
# (simple index, punctured-line index, old line, image line), in the pinned
# order. The first four rows are the simple-root-0 reflection already compared
# by #7017. This package selects the first later simple root.
MOVING_PAIRS = (
    (0, 1, 1, 88),
    (0, 2, 26, 95),
    (0, 4, 44, 113),
    (0, 7, 55, 118),
    (3, 0, 0, 2),
    (3, 1, 1, 3),
    (3, 2, 26, 16),
    (3, 3, 27, 17),
    (5, 2, 26, 28),
    (5, 3, 27, 29),
    (5, 4, 44, 38),
    (5, 5, 45, 39),
    (7, 4, 44, 46),
    (7, 5, 45, 47),
    (7, 6, 54, 52),
    (7, 7, 55, 53),
)
CARTAN = (
    (2, 0, -1, 0, 0, 0, 0, 0),
    (0, 2, 0, -1, 0, 0, 0, 0),
    (-1, 0, 2, -1, 0, 0, 0, 0),
    (0, -1, -1, 2, -1, 0, 0, 0),
    (0, 0, 0, -1, 2, -1, 0, 0),
    (0, 0, 0, 0, -1, 2, -1, 0),
    (0, 0, 0, 0, 0, -1, 2, -1),
    (0, 0, 0, 0, 0, 0, -1, 2),
)
NEIGHBORS = (
    (2,),
    (3,),
    (0, 3),
    (1, 2, 4),
    (3, 5),
    (4, 6),
    (5, 7),
    (6,),
)
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


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def line_key(vector):
    return max(tuple(vector), tuple(-value for value in vector))


def reflect(vector, simple):
    pairing = dot(vector, simple)
    need(pairing % 4 == 0, "reflection coefficient is not integral")
    return tuple(value - pairing // 4 * coefficient
                 for value, coefficient in zip(vector, simple))


def support_digest(words):
    payload = json.dumps(sorted(words)).encode()
    return sha256(payload).hexdigest()


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
    need(support_digest(RECORDED_SUPPORTS) == RECORDED_SUPPORT_SHA256,
         "recorded support hash")
    need(support_digest(TRANSPORTED_SUPPORTS) == TRANSPORTED_SUPPORT_SHA256,
         "pinned transported hash")
    need(TRANSPORTED_SUPPORT_SHA256 != FIRST_TRANSPORTED_SHA256,
         "this transport repeats the first reflection")
    need(LINE_SHA256 != FIRST_LINE_SHA256, "line-list hash repeats the first reflection")
    return checked


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
        key = line_key(root)
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
    return tuple(lines), tuple(puncture), tuple(roots)


def pinned_model():
    model = run_path(
        str(ROOT / "research/p112-rank6-frame-coverage/engine.py"),
        run_name="p112_next_simple_model",
    )["model"]()
    lines = tuple(tuple(row) for row in model["lines"])
    puncture = tuple(model["punctured_frame"])
    live = tuple(model["live"])
    own_lines, own_puncture, signed = independent_lines()
    need(lines == own_lines, "pinned lines differ from the E8 builder")
    need(puncture == own_puncture, "pinned puncture differs")
    need(live == tuple(i for i in range(120) if i not in set(puncture)), "live order")
    need(len(live) == WIDTH, "unreflected width")
    need(all(dot(row, row) == 8 for row in lines), "line norms")
    need(all(dot(lines[i], lines[j]) == 0 for i, j in combinations(puncture, 2)),
         "unreflected frame is not orthogonal")
    return lines, puncture, live, signed


def load_simple():
    simple = run_path(
        str(ROOT / "research/p112-a3-six-flat/geometry.py"),
        run_name="p112_next_simple_geometry",
    )["SIMPLE"]
    need(len(simple) == 8, "simple count")
    need(simple[SIMPLE_INDEX] == (0, -2, 2, 0, 0, 0, 0, 0), "simple root 3 changed")
    return tuple(tuple(row) for row in simple)


def integer_combination(root, simples):
    rows = []
    for coordinate in range(8):
        rows.append([Fraction(simple[coordinate]) for simple in simples]
                    + [Fraction(root[coordinate])])
    for column in range(8):
        pivot = next((row for row in range(column, 8) if rows[row][column]), None)
        need(pivot is not None, "singular simple system")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for other in range(8):
            if other == column or not rows[other][column]:
                continue
            factor = rows[other][column]
            rows[other] = [value - factor * base
                           for value, base in zip(rows[other], rows[column])]
    coeffs = []
    for row in rows:
        value = row[-1]
        need(value.denominator == 1, "nonintegral simple coordinates")
        coeffs.append(int(value))
    built = [0] * 8
    for coeff, simple in zip(coeffs, simples):
        for coordinate in range(8):
            built[coordinate] += coeff * simple[coordinate]
    need(tuple(built) == tuple(root), "simple coordinates do not rebuild the root")
    return tuple(coeffs)


def check_simple_system(lines, signed, simple_roots):
    cartan = tuple(tuple(dot(left, right) // 4 for right in simple_roots)
                   for left in simple_roots)
    need(cartan == CARTAN, "Cartan matrix")
    neighbors = tuple(tuple(j for j in range(8) if j != i and cartan[i][j] == -1)
                      for i in range(8))
    need(neighbors == NEIGHBORS, "E8 diagram")
    need(all(dot(root, root) == 8 for root in simple_roots), "simple norms")
    index_of = {line_key(row): index for index, row in enumerate(lines)}
    for simple in simple_roots:
        images = {index_of[line_key(reflect(row, simple))] for row in lines}
        need(images == set(range(120)), "a simple reflection misses a line")
        for row in lines:
            need(reflect(reflect(row, simple), simple) == tuple(row),
                 "a simple reflection is not an involution on the stored vector")
    for simple in simple_roots:
        coeffs = integer_combination(simple, simple_roots)
        place = next(index for index, value in enumerate(coeffs) if value)
        need(coeffs == tuple(int(index == place) for index in range(8)),
             "simple roots are not the coordinate basis")
    for root in signed:
        coeffs = integer_combination(root, simple_roots)
        need(all(value >= 0 for value in coeffs) or all(value <= 0 for value in coeffs),
             "a root is neither positive nor negative on this system")
    return index_of


def moving_pairs(lines, puncture, index_of, simple_roots):
    found = []
    for simple_index, simple in enumerate(simple_roots):
        for puncture_index, line in enumerate(puncture):
            image = index_of[line_key(reflect(lines[line], simple))]
            if image != line:
                found.append((simple_index, puncture_index, line, image))
    need(tuple(found) == MOVING_PAIRS, "moving-pair census changed")
    need(len(simple_roots) * len(puncture) == 64, "the movement scan is not the full 8 by 8 grid")
    fixed = tuple(index for index in range(8)
                  if all(row[0] != index for row in found))
    need(fixed == FIXED_ROOTS, "fixed simple roots changed")
    return tuple(found)


def select_reflection(lines, puncture, index_of, simple_roots, pairs):
    need(pairs[0][:2] == (0, 1), "the first moving pair is no longer simple root 0")
    same_root = tuple(row for row in pairs if row[0] == pairs[0][0])
    need(len(same_root) == 4, "simple root 0 no longer moves four punctured lines")
    later = tuple(row for row in pairs if row[0] > pairs[0][0])
    need(later, "no later simple root moves a punctured line")
    chosen = later[0]
    need(chosen[:2] == (SIMPLE_INDEX, PUNCTURE_INDEX), "next moving simple root changed")
    need(chosen[2:] == (0, 2), "the first line moved by simple root 3 changed")
    later_roots = tuple(dict.fromkeys(row[0] for row in later if row[0] != chosen[0]))
    need(later_roots == LATER_ROOTS, "roots after simple root 3 changed")
    simple = simple_roots[chosen[0]]
    line = puncture[chosen[1]]
    need(lines[line] == NAMED_ROOT and reflect(NAMED_ROOT, simple) == IMAGE_ROOT,
         "named reflection arithmetic")
    image = index_of[line_key(IMAGE_ROOT)]
    need(image == chosen[3] and lines[image] == IMAGE_ROOT, "image line representative")
    images = tuple(index_of[line_key(reflect(lines[old], simple))] for old in puncture)
    need(images == IMAGE_PUNCTURE, "image frame")
    need(len(set(images)) == FRAME_SIZE, "image frame collapsed")
    need(all(dot(lines[i], lines[j]) == 0 for i, j in combinations(images, 2)),
         "image frame is not orthogonal")
    moved = tuple(pair for pair in zip(puncture, images) if pair[0] != pair[1])
    need(len(moved) == MOVED_LINES, "moved punctured-line count")
    need(set(images) != set(puncture), "reflection fixed the frame")
    return simple, images


def rebuilt_list(lines, puncture, images, index_of, simple):
    new_live = tuple(index for index in range(120) if index not in set(images))
    need(len(new_live) == WIDTH, "rebuilt width")
    roots = [list(lines[index]) for index in new_live]
    digest = sha256(json.dumps(roots).encode()).hexdigest()
    need(digest == LINE_SHA256, "rebuilt root-list hash")
    old_live = tuple(index for index in range(120) if index not in set(puncture))
    position = {line: bit for bit, line in enumerate(new_live)}
    permutation = []
    for line in old_live:
        image = index_of[line_key(reflect(lines[line], simple))]
        need(image in position, "a live line reflected into the new puncture")
        permutation.append(position[image])
    need(sorted(permutation) == list(range(WIDTH)), "transport misses a new line")
    fixed = sum(bit == image for bit, image in enumerate(permutation))
    need(fixed == FIXED_BITS, "transport moved a different number of positions")
    return new_live, tuple(permutation)


def transport_mask(mask, permutation):
    image = 0
    while mask:
        bit = (mask & -mask).bit_length() - 1
        image |= 1 << permutation[bit]
        mask &= mask - 1
    return image


def transported_supports(permutation):
    images = tuple(transport_mask(mask, permutation) for mask in RECORDED_SUPPORTS)
    need(images == TRANSPORTED_SUPPORTS, "transported integers changed")
    covered = 0
    for mask in images:
        need(mask.bit_count() == WEIGHT_BOUND, "transported weight")
        need(covered & mask == 0, "transported supports meet")
        covered |= mask
    need(covered == (1 << WIDTH) - 1, "transported supports miss a line")
    need(set(images) != set(RECORDED_SUPPORTS), "transport left the integers fixed")
    return images


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
    frames = tuple(sorted(set(frames)))
    need(len(frames) == FRAME_COUNT, "reflected 8-frame count")
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
    free = tuple(coordinate for coordinate in range(WIDTH) if coordinate not in pivots)
    need(len(pivots) == RANK and free == FREE_COORDINATES, "reflected frame-code rank")
    need(free != FIRST_FREE_COORDINATES, "free coordinates repeat the first reflection")
    basis = []
    for coordinate in free:
        vector = 1 << coordinate
        for pivot in order:
            if (pivots[pivot] & vector).bit_count() % 2:
                vector |= 1 << pivot
        need(all((vector & row).bit_count() % 2 == 0 for row in rows),
             "a frame parity survives a basis vector")
        basis.append(vector)
    weights = tuple(vector.bit_count() for vector in basis)
    need(weights == BASIS_WEIGHTS, "basis weights changed")
    for index, vector in enumerate(basis):
        pattern = tuple((vector >> place) & 1 for place in free)
        identity = tuple(int(place == index) for place in range(DIMENSION))
        need(pattern == identity, "free coordinates are not a basis identity")
    return tuple(basis)


def in_code(mask, rows):
    return all((mask & row).bit_count() % 2 == 0 for row in rows)


def half_split(basis):
    with tempfile.TemporaryDirectory(prefix="p112-next-simple-") as directory:
        work = Path(directory)
        binary = work / "scan"
        subprocess.run(
            ["gcc", "-O3", "-std=c11", "-pthread", "-Wall", "-Werror",
             "-o", str(binary), str(HERE / "scan.c")],
            check=True, cwd=work, timeout=60,
        )
        path = work / "basis.txt"
        path.write_text("".join("%028x\n" % vector for vector in basis), encoding="ascii")
        completed = subprocess.run(
            [str(binary), str(path), str(SPLIT_AT)],
            check=True, capture_output=True, text=True, timeout=480,
        )
    need(completed.stderr == "", "scan wrote to stderr")
    histogram = {}
    found = []
    seen = None
    reported = None
    for line in completed.stdout.splitlines():
        kind, *rest = line.split()
        if kind == "SPLIT":
            reported = int(rest[0])
        elif kind == "SEEN":
            seen = int(rest[0])
        elif kind == "THREADS":
            need(1 <= int(rest[0]) <= 4, "thread cap")
        elif kind == "HIST":
            histogram[int(rest[0])] = int(rest[1])
        elif kind == "LOW":
            need(len(rest[0]) == 28, "low-word width")
            found.append(int(rest[0], 16))
        else:
            raise ValueError("unexpected scan line")
    need(reported == SPLIT_AT, "scan split")
    need(seen == CODEWORDS, "half-split missed a codeword")
    need(sum(histogram.values()) == CODEWORDS, "histogram sum")
    for weight, count in histogram.items():
        need(histogram[WIDTH - weight] == count, "complement asymmetry")
    need(histogram == HISTOGRAM, "weight distribution changed")
    need(min(weight for weight in histogram if weight) == WEIGHT_BOUND, "minimum left 16")
    supports = set(found)
    need(len(found) == len(supports) == SUPPORT_COUNT, "support count")
    need(all(word.bit_count() == WEIGHT_BOUND for word in supports), "a lighter positive word")
    return supports


def positive_words_have_weight(words, weight):
    return all(word.bit_count() == weight for word in words if word)


def main():
    authenticate()
    lines, puncture, live, signed = pinned_model()
    need(live == tuple(index for index in range(120) if index not in set(puncture)),
         "live list")
    simple_roots = load_simple()
    index_of = check_simple_system(lines, signed, simple_roots)
    pairs = moving_pairs(lines, puncture, index_of, simple_roots)
    simple, images = select_reflection(lines, puncture, index_of, simple_roots, pairs)
    new_live, permutation = rebuilt_list(lines, puncture, images, index_of, simple)
    supports = transported_supports(permutation)
    frames = orthogonal_frames(lines, new_live)
    degree = [0] * WIDTH
    for frame in frames:
        for index in frame:
            degree[index] += 1
    need(set(degree) == {DEGREE}, "frame degree")
    rows = tuple(sum(1 << index for index in frame) for frame in frames)
    basis = kernel(rows)
    need(all(in_code(mask, rows) for mask in supports), "a transported support leaves a frame")
    need(in_code((1 << WIDTH) - 1, rows), "all-ones leaves a frame")
    need(all(not in_code(mask, rows) for mask in RECORDED_SUPPORTS),
         "an untransported support is a codeword of this frame")
    scanned = half_split(basis)
    need(scanned == set(supports), "half-split disagrees with the transported supports")
    dropped = set(supports)
    dropped.remove(supports[0])
    need(dropped != scanned, "dropping one support still compared equal")
    lighter = supports[0] ^ (1 << (supports[0].bit_length() - 1))
    need(lighter.bit_count() == WEIGHT_BOUND - 1, "clearing the top bit did not reduce weight")
    need(lighter not in scanned and not in_code(lighter, rows),
         "a weight-fifteen word was already in the code")
    forged = set(scanned)
    forged.add(lighter)
    need(not positive_words_have_weight(forged, WEIGHT_BOUND),
         "weight-fifteen injection was accepted")
    need(set(RECORDED_SUPPORTS) != scanned,
         "the untransported integers equal this low-weight set")
    print(
        "PASS_P112_NEXT_MOVING_SIMPLE_ROOT"
        " width=%d frames=%d dimension=%d minimum=%d supports=%d"
        " codewords=%d split=%d simple=%d punctured=%d moved_lines=%d"
        " fixed_roots=%d later_roots=%s same_frame=false first_pair=false"
        " unreflected_census=false engine=false no_new_kappa=true"
        % (WIDTH, FRAME_COUNT, DIMENSION, WEIGHT_BOUND, SUPPORT_COUNT,
           CODEWORDS, SPLIT_AT, SIMPLE_INDEX, PUNCTURE_INDEX, MOVED_LINES,
           len(FIXED_ROOTS), ",".join(str(index) for index in LATER_ROOTS))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
