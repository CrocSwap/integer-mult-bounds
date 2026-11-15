#!/usr/bin/env python3
"""Compare low_weight_words with the reflected P112 transported supports.

Rebuild the reflected 36-generator basis from open PR #7017 and run the
published bit-lane iterator at its default batch size. The comparison is the
set of yielded words against the seven transported supports. No half-split
and no kappa change.
"""

import inspect
import json
import sys
import time
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
ENGINE_BATCH = 16
HIGH_BATCHES = 1 << (DIMENSION - ENGINE_BATCH)
LANE_COUNT = 1 << ENGINE_BATCH
SIMPLE_INDEX = 0
PUNCTURE_INDEX = 1
MOVED_LINES = 4
FIXED_BITS = 1
LINE_SHA256 = "a2ac7049d9eef1cff8af1eec35b084e6d261efad5311625e5356cceafe260da7"
RECORDED_SUPPORT_SHA256 = "ff8861dab18040c03d403a860773218df7c120d03770d701afb61b78c941e3d3"
TRANSPORTED_SUPPORT_SHA256 = "9ce7e5edc72ee3104d62cb068146b73840e9a3c42c4132403dece70c8146cccb"
GENERATOR_SHA256 = "f71157e487ad45377cb6a92651d3a8d8b1055b6978f14a44dea511049ca7da8c"
SELECTED_KAPPA = "781451/250000000"
SELECTED_DECIMAL = "0.003125804"
NAMED_ROOT = (2, -2, 0, 0, 0, 0, 0, 0)
IMAGE_ROOT = (1, -1, 1, 1, 1, 1, 1, -1)
IMAGE_PUNCTURE = (0, 88, 95, 27, 113, 45, 54, 118)
FREE_COORDINATES = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 17, 19, 21, 25, 26, 27,
    28, 30, 34, 36, 38, 42, 43, 52, 53, 54, 55, 56, 60, 68, 84,
)
BASIS_WEIGHTS = (
    24, 30, 34, 38, 38, 30, 34, 26, 38, 42, 40, 32, 42, 40, 40, 40, 22, 24, 32,
    38, 24, 36, 24, 34, 36, 24, 36, 24, 34, 34, 26, 32, 30, 30, 30, 28,
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
    12726038110963558112484457976320,
    61084916320812443394843581087904,
    2433889152476423258413102440464394,
    6363012028601310481939177671680,
    954453281446482856702353473856,
    580303949270928947429810196,
    2677278706012631304342476888735745,
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


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def line_key(vector):
    return max(tuple(vector), tuple(-value for value in vector))


def support_hash(words):
    return sha256(json.dumps(sorted(words)).encode()).hexdigest()


def reflect(vector, simple):
    pairing = dot(vector, simple)
    need(pairing % 4 == 0, "reflection coefficient is not integral")
    return tuple(value - (pairing // 4) * coefficient
                 for value, coefficient in zip(vector, simple))


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
    need(support_hash(RECORDED_SUPPORTS) == RECORDED_SUPPORT_SHA256,
         "recorded support hash")
    need(support_hash(TRANSPORTED_SUPPORTS) == TRANSPORTED_SUPPORT_SHA256,
         "pinned transported hash")
    need(len(FREE_COORDINATES) == len(set(FREE_COORDINATES)) == DIMENSION,
         "free-coordinate count")
    need(len(BASIS_WEIGHTS) == DIMENSION, "basis-weight count")
    selected = json.loads(
        (ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    need(selected["kappa"] == SELECTED_KAPPA, "selected kappa changed")
    need(selected["decimal"] == SELECTED_DECIMAL, "selected decimal changed")
    return checked


def independent_lines():
    roots = []
    for i, j in combinations(range(8), 2):
        for signs in product((2, -2), repeat=2):
            root = [0] * 8
            root[i], root[j] = signs
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
        run_name="p112_reflected_lane_model",
    )["model"]()
    lines = tuple(tuple(row) for row in model["lines"])
    puncture = tuple(model["punctured_frame"])
    live = tuple(model["live"])
    own_lines, own_puncture, signed = independent_lines()
    need(lines == own_lines, "pinned lines differ from the E8 builder")
    need(puncture == own_puncture, "pinned puncture differs")
    need(live == tuple(i for i in range(120) if i not in set(puncture)),
         "live order")
    need(len(live) == WIDTH, "unreflected width")
    need(all(dot(row, row) == 8 for row in lines), "line norms")
    need(all(dot(lines[i], lines[j]) == 0 for i, j in combinations(puncture, 2)),
         "unreflected frame is not orthogonal")
    return lines, puncture, signed


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
            rows[other] = [left - factor * right
                           for left, right in zip(rows[other], rows[column])]
    coefficients = []
    for row in rows:
        value = row[-1]
        need(value.denominator == 1, "nonintegral simple coordinates")
        coefficients.append(int(value))
    built = [0] * 8
    for coefficient, simple in zip(coefficients, simples):
        for coordinate in range(8):
            built[coordinate] += coefficient * simple[coordinate]
    need(tuple(built) == tuple(root), "simple coordinates do not rebuild the root")
    return tuple(coefficients)


def load_simple_system():
    geometry = run_path(
        str(ROOT / "research/p112-a3-six-flat/geometry.py"),
        run_name="p112_reflected_lane_geometry",
    )
    simple = tuple(tuple(row) for row in geometry["SIMPLE"])
    need(simple[0] == (1, -1, -1, -1, -1, -1, -1, 1), "first simple root")
    need(all(len(row) == 8 for row in simple) and len(simple) == 8, "simple shape")
    return simple


def check_simple_system(lines, signed, simple):
    cartan = tuple(tuple(dot(left, right) // 4 for right in simple) for left in simple)
    need(cartan == CARTAN, "Cartan matrix")
    neighbors = tuple(tuple(j for j in range(8) if j != i and cartan[i][j] == -1)
                      for i in range(8))
    need(neighbors == NEIGHBORS, "E8 diagram")
    need(all(dot(root, root) == 8 for root in simple), "simple norms")
    index_of = {line_key(row): index for index, row in enumerate(lines)}
    for root in simple:
        images = {index_of[line_key(reflect(row, root))] for row in lines}
        need(images == set(range(120)), "a simple reflection misses a line")
        for row in lines:
            image = reflect(row, root)
            need(reflect(image, root) == tuple(row),
                 "a simple reflection is not an involution on the stored vector")
    for root in simple:
        coefficients = integer_combination(root, simple)
        place = next(index for index, value in enumerate(coefficients) if value)
        need(coefficients == tuple(int(index == place) for index in range(8)),
             "simple roots are not the coordinate basis")
    for root in signed:
        coefficients = integer_combination(root, simple)
        need(all(value >= 0 for value in coefficients)
             or all(value <= 0 for value in coefficients),
             "a root is neither positive nor negative on this system")
    return index_of


def select_reflection(lines, puncture, index_of, simple_system):
    found = None
    for simple_index, simple in enumerate(simple_system):
        for puncture_index, line in enumerate(puncture):
            image = index_of[line_key(reflect(lines[line], simple))]
            if image != line:
                found = (simple_index, puncture_index, line, image, simple)
                break
        if found:
            break
    need(found is not None, "every simple root fixes every punctured line")
    simple_index, puncture_index, line, image, simple = found
    need((simple_index, puncture_index, line, image)
         == (SIMPLE_INDEX, PUNCTURE_INDEX, 1, 88),
         "first moving pair changed")
    need(lines[line] == NAMED_ROOT and reflect(NAMED_ROOT, simple) == IMAGE_ROOT,
         "named reflection arithmetic")
    need(lines[image] == IMAGE_ROOT, "image line representative")
    images = tuple(index_of[line_key(reflect(lines[old], simple))]
                   for old in puncture)
    need(images == IMAGE_PUNCTURE, "image frame")
    need(len(set(images)) == FRAME_SIZE, "image frame collapsed")
    need(all(dot(lines[i], lines[j]) == 0 for i, j in combinations(images, 2)),
         "image frame is not orthogonal")
    moved = sum(old != new for old, new in zip(puncture, images))
    need(moved == MOVED_LINES, "moved punctured-line count")
    need(set(images) != set(puncture), "reflection fixed the frame")
    return simple, images


def rebuilt_list(lines, puncture, images, index_of, simple):
    new_live = tuple(index for index in range(120) if index not in set(images))
    need(len(new_live) == WIDTH, "rebuilt width")
    digest = sha256(json.dumps([list(lines[index]) for index in new_live]).encode()).hexdigest()
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
                 for i, j in combinations(frame, 2)),
             "frame not orthogonal")
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


def positive_words_have_weight(words, weight):
    return all(word.bit_count() == weight for word in words if word)


def engine_words(engine, basis, maximum, batch_bits):
    listed = list(engine(tuple(basis), WIDTH, maximum, batch_bits))
    need(len(listed) == len(set(listed)), "engine repeated a word")
    return set(listed)


def build_basis():
    lines, puncture, signed = pinned_model()
    simple = load_simple_system()
    index_of = check_simple_system(lines, signed, simple)
    root, images = select_reflection(lines, puncture, index_of, simple)
    live, permutation = rebuilt_list(lines, puncture, images, index_of, root)
    supports = transported_supports(permutation)
    frames = orthogonal_frames(lines, live)
    degree = [0] * WIDTH
    for frame in frames:
        for index in frame:
            degree[index] += 1
    need(set(degree) == {DEGREE}, "frame degree")
    rows = tuple(sum(1 << index for index in frame) for frame in frames)
    basis = kernel(rows)
    generator_hash = sha256(json.dumps(list(basis)).encode()).hexdigest()
    print("generator_sha256=" + generator_hash, file=sys.stderr)
    need(generator_hash == GENERATOR_SHA256, "generator hash changed")
    need(all(in_code(mask, rows) for mask in supports),
         "a transported support misses a frame parity")
    need(all(not in_code(mask, rows) for mask in RECORDED_SUPPORTS),
         "an untransported support is a reflected codeword")
    witness = supports[0]
    lighter = witness ^ (1 << (witness.bit_length() - 1))
    need(lighter.bit_count() == WEIGHT_BOUND - 1, "clearing the top bit kept the weight")
    need(not in_code(lighter, rows), "a weight-fifteen word meets every frame")
    return basis, rows, supports, lighter, generator_hash


def load_engine():
    engine = run_path(
        str(ROOT / "research/e7-bitsliced-exhaustion/binary.py"),
        run_name="p112_reflected_lane_engine",
    )["low_weight_words"]
    signature = inspect.signature(engine)
    need(list(signature.parameters) == ["generators", "width", "maximum", "batch_bits"],
         "bit-lane signature changed")
    need(signature.parameters["batch_bits"].default == ENGINE_BATCH,
         "default batch size changed")
    return engine


def check(mode):
    need(mode in ("engine", "basis"), "mode")
    authenticate()
    started = time.perf_counter()
    basis, rows, supports, lighter, generator_hash = build_basis()
    basis_seconds = time.perf_counter() - started
    target = set(supports)
    if mode == "basis":
        return {
            "status": "BASIS_ONLY",
            "generator_sha256": generator_hash,
            "basis_seconds": round(basis_seconds, 3),
        }
    engine = load_engine()
    engine_started = time.perf_counter()
    produced = engine_words(engine, basis, WEIGHT_BOUND, ENGINE_BATCH)
    engine_seconds = time.perf_counter() - engine_started
    positive = produced - {0}
    digest = support_hash(positive)
    print("engine_positive_sha256=" + digest, file=sys.stderr)
    need(produced == target | {0}, "engine set differs from the transported supports")
    need(0 in produced and positive_words_have_weight(produced, WEIGHT_BOUND),
         "engine minimum")
    need(len(positive) == SUPPORT_COUNT, "support count")
    need(digest == TRANSPORTED_SUPPORT_SHA256, "engine support hash")
    need(produced - {supports[0]} != target | {0},
         "dropping one support still compared equal")
    need(lighter not in produced, "a weight-fifteen word was yielded")
    forged = set(produced)
    forged.add(lighter)
    need(not positive_words_have_weight(forged, WEIGHT_BOUND),
         "weight-fifteen injection was accepted")
    need(positive != set(RECORDED_SUPPORTS), "engine returned the untransported integers")
    toy = engine_words(engine, (1, 2, 4), 1, 3)
    need(toy == {0, 1, 2, 4}, "toy weight-1 set")
    need(engine_words(engine, (1, 2, 4), 0, 3) == {0}, "toy bound change was ignored")
    try:
        list(engine((basis[0], basis[0]), WIDTH, WEIGHT_BOUND, 4))
    except ValueError as error:
        need(str(error) == "binary generators must be independent",
             "unexpected dependent-generator message")
        rejected = True
    else:
        rejected = False
    need(rejected, "a repeated generator was accepted")
    need(all(in_code(word, rows) for word in produced),
         "a yielded word leaves a frame")
    return {
        "status": "PASS_P112_REFLECTED_FRAME_LANE",
        "width": WIDTH,
        "frames": FRAME_COUNT,
        "rank": RANK,
        "dimension": DIMENSION,
        "free_coordinates": list(FREE_COORDINATES),
        "engine_batch": ENGINE_BATCH,
        "high_batches": HIGH_BATCHES,
        "lanes": LANE_COUNT,
        "minimum_positive_weight": WEIGHT_BOUND,
        "supports": SUPPORT_COUNT,
        "yielded_with_zero": len(produced),
        "supports_sha256": digest,
        "generator_sha256": generator_hash,
        "lines_sha256": LINE_SHA256,
        "simple_index": SIMPLE_INDEX,
        "punctured_index": PUNCTURE_INDEX,
        "half_split_rerun": False,
        "unreflected_engine_rerun": False,
        "intersection_engine_called": False,
        "batch_20_run": False,
        "dependent_generator_rejected": rejected,
        "basis_seconds": round(basis_seconds, 3),
        "engine_seconds": round(engine_seconds, 3),
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }


if __name__ == "__main__":
    selected = sys.argv[1] if len(sys.argv) > 1 else "engine"
    result = check(selected)
    print(
        "{status}"
        " width={width}"
        " dimension={dimension}"
        " batch={batch}"
        " supports={supports}"
        " hash={digest}"
        " half_split_rerun=false"
        " intersection_engine=false"
        " no_new_kappa=true".format(
            status=result["status"],
            width=result.get("width", WIDTH),
            dimension=result.get("dimension", DIMENSION),
            batch=result.get("engine_batch", "not-run"),
            supports=result.get("supports", SUPPORT_COUNT),
            digest=result.get("supports_sha256", "not-run"),
        )
    )
    print(json.dumps(result, indent=2, sort_keys=True))
