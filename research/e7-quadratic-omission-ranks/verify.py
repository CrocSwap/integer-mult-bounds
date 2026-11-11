#!/usr/bin/env python3
"""Quadratic ranks and single-omission frame ranks of the two E7 representatives.

This evaluates form_a, form_b, quadratic_matrix and supported_rank from the
pinned classification verifier. It does not enumerate the 2^27 kernel, build
reflection orbits, or call low_weight_words.
"""

import json
from fractions import Fraction
from hashlib import sha256
from math import gcd
from pathlib import Path
from runpy import run_path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CLASSIFIER = ROOT / "research/e7-bitsliced-exhaustion/source/verify.py"
RECEIPT = ROOT / "research/e7-bitsliced-exhaustion/source/RESULT.json"
SELECTED = ROOT / "certificates/selected-result.json"
SLICE = (
    (1, 0, 0, 0, 0, 0, 0, 0),
    (0, 1, 0, 0, 0, 0, 0, 0),
    (0, 0, 1, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 1, 0, 0, 0),
    (0, 0, 0, 0, 0, 1, 0, 0),
    (0, 0, 0, 0, 0, 0, 1, 0),
    (1, 0, 0, 0, -1, 0, 0, 0),
)
DIAGONAL_MATRIX = (
    (1, 0, 0, 0, 0, 0, 0),
    (0, 1, 0, 0, 0, 0, 0),
    (0, 0, 1, 0, 0, 0, 0),
    (0, 0, 0, -1, 0, 0, 0),
    (0, 0, 0, 0, -1, 0, 0),
    (0, 0, 0, 0, 0, -1, 0),
    (0, 0, 0, 0, 0, 0, 0),
)
PRODUCT_MATRIX = (
    (0, Fraction(-1, 2), Fraction(1, 2), 0, 0, 0, 0),
    (Fraction(-1, 2), 0, 0, 0, 0, 0, Fraction(1, 2)),
    (Fraction(1, 2), 0, 0, 0, 0, 0, Fraction(-1, 2)),
    (0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0),
    (0, Fraction(1, 2), Fraction(-1, 2), 0, 0, 0, 0),
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
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    need(selected["kappa"] == "363005817/100000000000", "selected frontier changed")
    return checked


def load_classifier():
    module = run_path(str(CLASSIFIER), run_name="pinned_e7_classifier")
    for name in ("form_a", "form_b", "quadratic_matrix", "supported_rank", "rank", "geometry"):
        need(callable(module.get(name)), "missing classifier function: " + name)
    return module


def fractions(rows):
    return tuple(tuple(Fraction(entry) for entry in row) for row in rows)


def column_kernel(rows):
    """Return the primitive integer basis of the right kernel."""
    width = len(rows[0])
    matrix = [list(map(Fraction, row)) for row in rows]
    working = [[matrix[row][col] for row in range(len(matrix))] for col in range(width)]
    ops = [[Fraction(int(i == j)) for j in range(width)] for i in range(width)]
    used = set()
    for column in range(len(matrix)):
        pivot = next((row for row in range(width) if row not in used and working[row][column] != 0), None)
        if pivot is None:
            continue
        used.add(pivot)
        scale = working[pivot][column]
        working[pivot] = [entry / scale for entry in working[pivot]]
        ops[pivot] = [entry / scale for entry in ops[pivot]]
        for row in range(width):
            factor = working[row][column]
            if row == pivot or factor == 0:
                continue
            working[row] = [left - factor * right for left, right in zip(working[row], working[pivot])]
            ops[row] = [left - factor * right for left, right in zip(ops[row], ops[pivot])]
    kernel = [ops[row] for row in range(width) if all(entry == 0 for entry in working[row])]
    primitive = []
    for vector in kernel:
        denominator = 1
        for entry in vector:
            denominator = denominator * entry.denominator // gcd(denominator, entry.denominator)
        integers = [int(entry * denominator) for entry in vector]
        divisor = 0
        for entry in integers:
            divisor = gcd(divisor, abs(entry))
        need(divisor > 0, "zero kernel vector")
        primitive.append(tuple(entry // divisor for entry in integers))
    return tuple(primitive)


def apply(matrix, vector):
    return tuple(
        sum((Fraction(entry) * coefficient for entry, coefficient in zip(row, vector)), Fraction(0))
        for row in matrix
    )


def representative(module, form, roots, frames):
    values = tuple(form(root) for root in roots)
    support = [index for index, value in enumerate(values) if value]
    matrix = fractions(module["quadratic_matrix"](form))
    indicators = [[int(index in frame) for index in support] for frame in frames]
    kernel = column_kernel(indicators)
    need(len(kernel) == 1, "frame-indicator kernel dimension")
    relation = kernel[0]
    need(all(coordinate != 0 for coordinate in relation), "a kernel coordinate vanishes")
    need(all(entry == 0 for entry in apply(indicators, relation)), "kernel vector is not a relation")
    frame_rank = module["supported_rank"](frames, support)
    omissions = []
    for omitted in support:
        kept = [index for index in support if index != omitted]
        omissions.append(module["supported_rank"](frames, kept))
    for frame in frames:
        need(sum(values[index] for index in frame) == 0, "frame sum is nonzero")
    return {
        "values": list(values),
        "support": support,
        "matrix": matrix,
        "quadratic_rank": module["rank"](matrix),
        "frame_rank": frame_rank,
        "kernel": relation,
        "omissions": omissions,
    }


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise ValueError("invalid control accepted")


def controls(module, diagonal, product, frames):
    counted = 0

    def wrong_diagonal_rank():
        need(module["rank"](DIAGONAL_MATRIX) == 7, "diagonal rank is not 7")

    def broken_relation():
        changed = list(diagonal["values"])
        changed[diagonal["support"][0]] += 1
        for frame in frames:
            need(sum(changed[index] for index in frame) == 0, "perturbed frame sum")

    def zero_coordinate():
        broken = list(product["kernel"])
        broken[0] = 0
        indicators = [[int(index in frame) for index in product["support"]] for frame in frames]
        need(all(entry == 0 for entry in apply(indicators, broken)), "zeroed coordinate stayed in the kernel")

    def moved_support():
        moved = list(diagonal["support"])
        moved[0] = 62 if moved[0] != 62 else 61
        need(moved == diagonal["support"], "support changed")

    for check in (wrong_diagonal_rank, broken_relation, zero_coordinate, moved_support):
        reject(check)
        counted += 1
    need(counted == 4, "four rejecting controls")
    return counted


def check():
    authenticate()
    module = load_classifier()
    geometry = module["geometry"]()
    roots = geometry["intrinsic_e7"]()
    frames = geometry["orthogonal_frames"](roots)
    need(len(roots) == 63 and len(frames) == 135, "pinned root and frame counts")
    diagonal = representative(module, module["form_a"], roots, frames)
    product = representative(module, module["form_b"], roots, frames)
    need(diagonal["matrix"] == fractions(DIAGONAL_MATRIX), "diagonal polarization")
    need(product["matrix"] == fractions(PRODUCT_MATRIX), "product polarization")
    need(diagonal["quadratic_rank"] == 6 and product["quadratic_rank"] == 2, "quadratic ranks")
    need(diagonal["frame_rank"] == product["frame_rank"] == 11, "full support rank")
    need(diagonal["omissions"] == [11] * 12 and product["omissions"] == [11] * 12, "omission ranks")
    need(diagonal["kernel"] == (-1, -1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1), "diagonal kernel")
    need(product["kernel"] == (1, -1, 1, -1, -1, -1, -1, -1, 1, 1, 1, 1), "product kernel")
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    orbits = receipt["orbits"]
    need(len(orbits) == 2, "receipt orbit count")
    expected = {"diagonal": diagonal, "product": product}
    for orbit in orbits:
        found = expected[orbit["type"]]
        need(orbit["quadratic_rank"] == found["quadratic_rank"], orbit["type"] + " receipt rank")
        need(orbit["restricted_frame_rank"] == found["frame_rank"], orbit["type"] + " receipt frame rank")
        need(orbit["representative_support"] == found["support"], orbit["type"] + " receipt support")
        need(orbit["representative_values"] == found["values"], orbit["type"] + " receipt values")
        need(orbit["rational_lift_dimension"] == 1, orbit["type"] + " lift dimension")
    counted = controls(module, diagonal, product, frames)
    return {
        "status": "PASS_E7_QUADRATIC_OMISSION_RANKS",
        "diagonal_quadratic_rank": 6,
        "product_quadratic_rank": 2,
        "frame_rank": 11,
        "omissions": 24,
        "frames": 135,
        "roots": 63,
        "rejecting_controls": counted,
        "kernel_words_scanned": 0,
        "selected_kappa": "363005817/100000000000",
        "no_new_kappa": True,
    }


def main():
    result = check()
    print(result["status"])
    print(
        "diagonal=6 product=2 frame_rank=11 omissions=24 frames=135 "
        "controls=4 kernel_words_scanned=0 no_new_kappa=true "
        "kappa=363005817/100000000000"
    )


if __name__ == "__main__":
    main()
