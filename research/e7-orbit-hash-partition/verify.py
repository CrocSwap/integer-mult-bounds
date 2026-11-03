#!/usr/bin/env python3
"""The independent E7 weight-12 set is the two receipt reflection orbits.

The half-split census does not call the predecessor Gray-code loop, orbit
search, or quadratic-rank checks. It lists one basis split by doubling. The
orbit maps are the frozen functions in source/verify.py.
"""

import json
from hashlib import sha256
from pathlib import Path
from runpy import run_path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH = 63
DIMENSION = 27
WEIGHT_BOUND = 12
DIAGONAL_HASH = "d08f659fab919baab7b2c87c0b7e55edb5a3e23e05a313522f0b17e684d8ee39"
PRODUCT_HASH = "a9bb36def7396f184d343e38f410d705a50be3188b40725235f866ad0753309b"


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
    need(checked == 4, "four live inputs")
    return checked


def span(generators):
    words = [0]
    for generator in generators:
        # Snapshot this span. A generator would also visit the elements extend appends.
        words.extend([word ^ generator for word in words])
    need(len(set(words)) == len(words), "half span repeats a word")
    return words


def half_split(basis, maximum, low_dimension):
    need(0 < low_dimension < len(basis), "split must use both halves")
    lows = span(basis[:low_dimension])
    highs = span(basis[low_dimension:])
    distinct = len(lows) * len(highs)
    need(distinct == 1 << len(basis), "halves do not cover the basis span")
    found = set()
    minimum = maximum + 1
    for high in highs:
        for low in lows:
            word = high ^ low
            weight = word.bit_count()
            if word and weight < minimum:
                minimum = weight
            if weight <= maximum:
                found.add(word)
    return found, minimum, distinct


def free_coordinate_identity(basis, free):
    need(len(basis) == len(free) == DIMENSION, "E7 kernel dimension")
    need(len(set(free)) == DIMENSION, "repeated free coordinate")
    for index, vector in enumerate(basis):
        need(0 < vector < 1 << WIDTH, "kernel vector outside F_2^63")
        pattern = tuple((vector >> coordinate) & 1 for coordinate in free)
        identity = tuple(int(place == index) for place in range(DIMENSION))
        need(pattern == identity, "free coordinates are not a basis identity")


def orbit_digest(words):
    return sha256(json.dumps(sorted(words)).encode()).hexdigest()


def mask_of(indices):
    mask = 0
    for index in indices:
        need(0 <= index < WIDTH, "support index outside F_2^63")
        bit = 1 << index
        need(mask & bit == 0, "repeated support index")
        mask |= bit
    return mask


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise ValueError("invalid control accepted")


def load_receipt():
    receipt = json.loads(
        (ROOT / "research/e7-bitsliced-exhaustion/source/RESULT.json").read_text(
            encoding="utf-8"
        )
    )
    orbits = receipt["orbits"]
    need(len(orbits) == 2, "receipt orbit count")
    need(orbits[0]["type"] == "diagonal" and orbits[0]["supports"] == 630, "diagonal orbit")
    need(orbits[1]["type"] == "product" and orbits[1]["supports"] == 1008, "product orbit")
    need(orbits[0]["orbit_sha256"] == DIAGONAL_HASH, "diagonal hash pin")
    need(orbits[1]["orbit_sha256"] == PRODUCT_HASH, "product hash pin")
    need(DIAGONAL_HASH != PRODUCT_HASH, "orbit hashes are not distinct")
    need(receipt["minimum_support"] == WEIGHT_BOUND, "receipt minimum")
    need(receipt["minimum_supports"] == 1638, "receipt support count")
    need(receipt["reflection_generators"] == 63, "receipt reflection count")
    return receipt


def check():
    authenticate()
    receipt = load_receipt()
    frozen = run_path(
        str(ROOT / "research/e7-bitsliced-exhaustion/source/verify.py"),
        run_name="e7_frozen_orbits",
    )
    geometry = run_path(
        str(ROOT / "research/e7-bitsliced-exhaustion/source/vendor/PR5238.py"),
        run_name="e7_orbit_geometry",
    )
    roots = geometry["intrinsic_e7"]()
    frames = geometry["orthogonal_frames"](roots)
    need(len(roots) == 63 and len(frames) == 135, "root or frame count")
    rows = tuple(sum(1 << index for index in frame) for frame in frames)
    basis, free = geometry["binary_kernel"](rows)
    free_coordinate_identity(basis, free)
    permutations = frozen["reflections"](roots, frames, geometry["dot"])
    need(len(permutations) == 63, "frozen reflection count")
    need(all(sorted(perm) == list(range(63)) for perm in permutations), "root permutation")

    splits = {}
    for low_dimension in (13, 16):
        found, minimum, distinct = half_split(basis, WEIGHT_BOUND, low_dimension)
        splits[low_dimension] = (found, minimum, distinct)
    need(splits[13][0] == splits[16][0], "two basis splits disagree")
    need(splits[13][1] == splits[16][1] == WEIGHT_BOUND, "minimum left twelve")
    need(splits[13][2] == splits[16][2] == 1 << DIMENSION, "span missed a codeword")
    found = splits[16][0]
    supports = found - {0}
    need(0 in found and len(supports) == 1638, "support count")
    need(all(word.bit_count() == WEIGHT_BOUND for word in supports), "a lighter nonzero word")

    engine = run_path(
        str(ROOT / "research/e7-bitsliced-exhaustion/binary.py"),
        run_name="e7_orbit_engine",
    )["low_weight_words"]
    for batch_bits in (16, 8):
        produced = set(engine(basis, WIDTH, WEIGHT_BOUND, batch_bits))
        need(produced == found, "engine batch " + str(batch_bits) + " is not the census")

    built = []
    for row in receipt["orbits"]:
        mask = mask_of(row["representative_support"])
        need(mask.bit_count() == WEIGHT_BOUND, "representative weight")
        current = frozen["orbit"](mask, permutations)
        need(mask in current, "representative left its orbit")
        need(len(current) == row["supports"], "orbit size")
        need(orbit_digest(current) == row["orbit_sha256"], "orbit hash")
        need(current <= supports, "orbit left the weight-12 set")
        need(all(word.bit_count() == WEIGHT_BOUND for word in current), "orbit weight")
        built.append(current)
    frozen["partition"](supports, built)
    need(built[0].isdisjoint(built[1]), "orbits meet")
    need(built[0] | built[1] == supports, "orbit union missed a weight-12 word")

    witness = next(iter(supports))
    reject(lambda: frozen["partition"](supports - {witness}, built))
    reject(lambda: frozen["partition"](supports, [built[0], built[1] | built[0]]))
    damaged = set(built[0])
    damaged.pop()
    need(orbit_digest(damaged) != DIAGONAL_HASH, "a deleted orbit word kept the receipt hash")
    moved = mask_of(receipt["orbits"][0]["representative_support"])
    moved ^= 1 << receipt["orbits"][0]["representative_support"][0]
    moved_orbit = frozen["orbit"](moved, permutations)
    need(orbit_digest(moved_orbit) != DIAGONAL_HASH, "a moved representative kept the receipt hash")
    need(not moved_orbit <= supports, "a weight-11 seed stayed inside the weight-12 set")
    return {
        "status": "PASS_E7_ORBIT_HASH_PARTITION",
        "minimum_supports": len(supports),
        "diagonal_supports": len(built[0]),
        "product_supports": len(built[1]),
        "diagonal_sha256": DIAGONAL_HASH,
        "product_sha256": PRODUCT_HASH,
        "reflection_generators": len(permutations),
        "splits": [13, 16],
        "engine_batches": [16, 8],
        "quadratic_ranks_replayed": False,
        "no_new_kappa": True,
    }


if __name__ == "__main__":
    result = check()
    print(
        "PASS_E7_ORBIT_HASH_PARTITION"
        " supports={minimum_supports}"
        " diagonal={diagonal_supports}"
        " product={product_supports}"
        " reflections={reflection_generators}"
        " quadratic_ranks_replayed=false"
        " no_new_kappa=true".format(**result)
    )
    print(json.dumps(result, indent=2, sort_keys=True))
