#!/usr/bin/env python3
"""Literal localized-cube and three-star witnesses; Python 3.10+, stdlib.

Copyright 2026 Sam Sung. Apache-2.0. Substantial OpenAI Codex assistance.
This verifies constructions, not the uniform lower bounds in HIGHER-WEIGHTS.md.
"""
import argparse
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def ports(p, k):
    return [sum(1 << (2 * pair + sign) for pair, sign in zip(pairs, signs))
            for pairs in combinations(range(p), k) for signs in product((0, 1), repeat=k)]


def star(face, family):
    return sum(1 << i for i, port in enumerate(family) if port & face == face)


def xor(words):
    value = 0
    for word in words:
        value ^= word
    return value


def basis(words):
    pivots = {}
    for word in words:
        while word:
            pivot = word.bit_length() - 1
            if pivot in pivots:
                word ^= pivots[pivot]
            else:
                pivots[pivot] = word
                break
    return pivots


def belongs(word, pivots):
    for pivot in sorted(pivots, reverse=True):
        if word >> pivot & 1:
            word ^= pivots[pivot]
    return word == 0


def combination(mask, words):
    return xor(word for i, word in enumerate(words) if mask >> i & 1)


def support(words):
    union = 0
    for word in words:
        union |= word
    return union


def valid_faces(faces, k):
    return all(0 < face.bit_count() < k and
               all((face >> (2 * i)) & 3 != 3 for i in range(face.bit_length() // 2 + 1))
               for face in faces)


def cube_rows(k, family):
    fixed = sum(1 << (2 * i) for i in range(k - 4))
    variable = list(range(k - 4, k))
    outside = (k, k + 1)
    selectors = [1 << (2 * i) for i in variable] + [1 << (2 * variable[-1] + 1)]
    faces, rows = [], []
    selected_cube = sum(1 << i for i, port in enumerate(family)
                        if port & fixed == fixed and port >> (2 * k) == 0)
    require(selected_cube.bit_count() == 16, "localized cube size")
    for selector in selectors:
        terms = [fixed | selector | left | right
                 for left in (0, 1 << (2 * outside[0]), 1 << (2 * outside[0] + 1))
                 for right in (0, 1 << (2 * outside[1]), 1 << (2 * outside[1] + 1))]
        require(valid_faces(terms, k) and len(set(terms)) == 9, "nine allowed nonempty stars")
        row = xor(star(face, family) for face in terms)
        require(row == selected_cube & star(selector, family), "expanded versus factored selector")
        require(row.bit_count() == 8, "affine cube row weight")
        faces.append(terms)
        rows.append(row)
    require(rows[3] ^ rows[4] == selected_cube, "empty-free constant on localized cube")
    leaked = star(fixed | selectors[0], family) ^ xor(
        star(fixed | selectors[0] | (1 << (2 * outside[0] + sign)), family) for sign in (0, 1))
    require(bool(leaked & ~selected_cube), "omitting one exclusion must leak nuisance ports")
    require(rows[0] ^ star(faces[0][-1], family) != rows[0], "dropped term must change identity")
    return faces, rows


def decoder_case(k, family, faces, rows, rank):
    original = rows[:rank]
    words = original[:]
    coefficients = [1 << i for i in range(rank)]
    information = []
    for column in range(len(family)):
        pivot = len(information)
        found = next((i for i in range(pivot, rank) if words[i] >> column & 1), None)
        if found is None:
            continue
        words[pivot], words[found] = words[found], words[pivot]
        coefficients[pivot], coefficients[found] = coefficients[found], coefficients[pivot]
        for i in range(rank):
            if i != pivot and words[i] >> column & 1:
                words[i] ^= words[pivot]
                coefficients[i] ^= coefficients[pivot]
        information.append(column)
    require(len(information) == rank, "independent cube rows")
    union = support(original)
    expected = {3: 14, 4: 15, 5: 16}[rank]
    require(union.bit_count() == expected, "higher-weight witness support")
    target_mask = sum(1 << i for i in information)
    deleted = union ^ target_mask
    require(deleted.bit_count() == 11, "eleven deletions")
    surviving = ((1 << len(family)) - 1) ^ deleted
    expanded = []
    helper_words = {face: star(face, family) for terms in faces[:rank] for face in terms}
    for coefficient, word, target in zip(coefficients, words, information):
        terms = set()
        for i in range(rank):
            if coefficient >> i & 1:
                terms.symmetric_difference_update(faces[i])
        require(xor(helper_words[face] for face in terms) == word == combination(coefficient, original),
                "literal decoder expansion")
        require(word & surviving == 1 << target, "retained unit decoder")
        expanded.append(sorted(terms))
    for column in range(len(family)):
        if deleted >> column & 1:
            restored = surviving | 1 << column
            row_basis = basis(word & restored for word in original)
            require(not all(belongs(1 << target, row_basis) for target in information),
                    "single restoration must break simultaneous decoding within witness span")
    deleted_indices = [i for i in range(len(family)) if deleted >> i & 1]
    costs = dict(distinct_observations=len(helper_words),
                 original_row_xors=sum(len(terms) - 1 for terms in faces[:rank]),
                 direct_unit_row_xors=sum(len(terms) - 1 for terms in expanded),
                 cached_basis_to_unit_xors=sum(mask.bit_count() - 1 for mask in coefficients),
                 independent_helper_input_contributions=sum((word & surviving).bit_count()
                                                            for word in helper_words.values()),
                 independent_helper_sum_xors=sum(max(0, (word & surviving).bit_count() - 1)
                                                 for word in helper_words.values()))
    result = dict(rank=rank, support_size=expected, deletions=11,
                  information_indices=information, deleted_indices=deleted_indices,
                  decoder_coefficients=coefficients, basis_rows_sha256=digest(original),
                  costs_for_naive_scalar_evaluation_only=costs)
    if k == 4:
        result.update(information_ports=[family[i] for i in information],
                      deleted_ports=[family[i] for i in deleted_indices],
                      original_proper_star_faces=faces[:rank], decoder_proper_star_faces=expanded)
    return result


def cube_case(k):
    family = ports(k + 2, k)
    faces, rows = cube_rows(k, family)
    require([combination(mask, rows[:3]).bit_count() for mask in range(1, 8)] == [8] * 7,
            "all seven third-weight witness words have weight eight")
    return dict(k=k, p=k + 2, ports=len(family), port_order_sha256=digest(family),
                witnesses=[decoder_case(k, family, faces, rows, rank) for rank in (3, 4, 5)])


def triangle_case(k, q):
    family = ports(k + q, k)
    fixed = sum(1 << (2 * i) for i in range(k - 2))
    faces = [fixed | 1 << (2 * i) for i in range(k - 2, k + 1)]
    words = [star(face, family) for face in faces]
    require(valid_faces(faces, k) and len(basis(words)) == 3, "independent triangle stars")
    require([word.bit_count() for word in words] == [2 * (q + 1)] * 3, "triangle star weights")
    require(all((a & b).bit_count() == 1 for a, b in combinations(words, 2)), "triangle pair overlaps")
    require(words[0] & words[1] & words[2] == 0, "empty triple intersection")
    require(support(words).bit_count() == 6 * q + 3, "triangle support")
    return dict(k=k, q=q, ports=len(family), support_size=6 * q + 3,
                star_faces=faces, evaluation_sha256=digest(words))


def verify():
    cubes = [cube_case(k) for k in range(4, 9)]
    triangles = [triangle_case(k, q) for k in range(2, 7) for q in range(2, 7)]
    # A two-exclusion selector times a sign reaches forbidden degree k at k=3.
    require(not valid_faces([1 << 0 | 1 << 6 | 1 << 8], 3), "invalid k=3 degree rejected")
    return dict(status="PASS", arithmetic="exact binary evaluations on every full-family port",
                scope="Constructive witnesses only; uniform lower bounds are separate written proofs. "
                      "Restoration controls concern the displayed subcode, not a full ambient-code search. "
                      "Costs price naive scalar sums only; no complete supplier or kappa claim.",
                port_encoding="bit 2*i+s denotes sign s of pair i; combinations then lexicographic signs",
                cubes=cubes, triangles=triangles,
                negative_controls=["all single-deletion restorations break the displayed simultaneous span",
                                   "missing outside-pair exclusion leaks nuisance ports",
                                   "missing proper-star monomial changes the evaluation",
                                   "k=3 two-exclusion linear selector fails the proper-degree limit"])


def self_test(result):
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        script = directory / "cube_verify.py"
        script.write_bytes(Path(__file__).read_bytes())
        receipt = directory / "CUBE-RESULTS.json"
        receipt.write_text(json.dumps(result))
        command = [sys.executable, "-I", "-O", "-B", str(script)]
        run = subprocess.run(command, capture_output=True, text=True)
        require(run.returncode == 0, f"isolated optimized relocated replay: {run.stderr}")
        receipt.write_text(json.dumps(dict(result, status="CORRUPTED")))
        protected = directory / "protected.json"
        protected.write_text("preserve this output\n")
        run = subprocess.run(command + ["--check", str(receipt), "--write", str(protected)],
                             capture_output=True, text=True)
        require(run.returncode != 0, "corrupt receipt accepted")
        require(protected.read_text() == "preserve this output\n", "failed check overwrote output")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.check or not args.write:
        receipt = args.check or HERE / "CUBE-RESULTS.json"
        require(json.loads(receipt.read_text()) == result, f"receipt mismatch: {receipt}")
    if args.self_test:
        self_test(result)
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_CUBE: 15 literal simultaneous decoders on 5 full port families; "
          "165 restoration controls; 25 triangle witnesses; forbidden-degree and leakage controls")


if __name__ == "__main__":
    main()
