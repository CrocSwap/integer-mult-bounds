#!/usr/bin/env python3
"""Independent exact checks of original-core shortening; Python 3.10+.

Copyright 2026 Sam Sung. Apache-2.0. Substantial OpenAI Codex assistance.
Finite checks supplement CORE-SHORTENING.md; they are not formal proofs.
"""
import argparse
import subprocess
import tempfile
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
from math import comb
from pathlib import Path
import json
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def partials(p, size):
    for pairs in combinations(range(p), size):
        for signs in product((0, 1), repeat=size):
            yield sum(1 << (2 * pair + sign) for pair, sign in zip(pairs, signs))


def echelon(rows):
    pivots = {}
    for word in rows:
        while word:
            pivot = word.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = word
                break
            word ^= pivots[pivot]
    return sorted(pivots.values(), key=int.bit_length, reverse=True)


def remainder(word, basis):
    for pivot in basis:
        if word >> (pivot.bit_length() - 1) & 1:
            word ^= pivot
    return word


def shorten(rows, allowed):
    pivots, inside = {}, []
    for word in rows:
        while word & ~allowed:
            pivot = (word & ~allowed).bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = word
                break
            word ^= pivots[pivot]
        else:
            inside.append(word)
    return echelon(inside)


def same_space(left, right):
    return len(left) == len(right) and all(remainder(word, right) == 0 for word in left)


def words(basis):
    word = 0
    yield word
    for index in range(1, 1 << len(basis)):
        word ^= basis[(index & -index).bit_length() - 1]
        yield word


def unsigned_ladder():
    family = [sum(1 << i for i in subset) for subset in combinations(range(6), 3)]
    rows = [sum(1 << i for i, point in enumerate(family) if point & monomial == monomial)
            for degree in range(3)
            for subset in combinations(range(6), degree)
            for monomial in [sum(1 << j for j in subset)]]
    result = []
    for excluded in range(4):
        mask = (1 << excluded) - 1
        allowed = sum(1 << i for i, point in enumerate(family) if point & mask == 0)
        actual = shorten(rows, allowed)
        degree_bound = 2 - excluded
        expected = echelon(sum(1 << i for i, point in enumerate(family)
                              if point & mask == 0 and point & monomial == monomial)
                           for degree in range(degree_bound + 1)
                           for subset in combinations(range(excluded, 6), degree)
                           for monomial in [sum(1 << j for j in subset)])
        require(same_space(actual, expected), 'unsigned shortening ladder')
        result.append({'excluded_vertices': excluded, 'remaining_coordinates': allowed.bit_count(),
                       'dimension': len(actual), 'degree_bound': degree_bound})
    return result


def residual_spaces():
    family = list(partials(5, 2))
    vertex_stars = [sum(1 << i for i, port in enumerate(family) if port & star == star)
                    for degree in (0, 1) for star in partials(5, degree)]
    blocks, affine = [], []
    for a, b in combinations(range(5), 2):
        block = sum(1 << i for i, port in enumerate(family)
                    if port & (3 << (2 * a)) and port & (3 << (2 * b)))
        blocks.append(block)
        affine.extend((block, block & vertex_stars[2 * a + 2], block & vertex_stars[2 * b + 2]))
    spaces = {0: echelon(vertex_stars), 2: echelon(vertex_stars + blocks),
              3: echelon(affine), 4: echelon(1 << i for i in range(40))}
    require([len(spaces[j]) for j in (0, 2, 3, 4)] == [10, 15, 30, 40], 'residual dimensions')
    for previous, following in ((0, 2), (2, 3), (3, 4)):
        require(all(remainder(word, spaces[following]) == 0 for word in spaces[previous]), 'nested spaces')
    spectra = {j: Counter(word.bit_count() for word in words(spaces[j])) for j in (0, 2)}
    require(min(w for w in spectra[0] if w) == 8 and spectra[0][14] == 40, 'residual cut weights')
    require(min(w for w in spectra[2] if w) == 4, 'unsigned extension distance')
    adjacent = {vertex_stars[i + 1] ^ vertex_stars[j + 1]
                for i, j in combinations(range(10), 2) if i // 2 != j // 2}
    require({word for word in words(spaces[0]) if word.bit_count() == 14} == adjacent, 'weight14 residual classification')
    require(remainder(blocks[0], spaces[0]) != 0, 'unsigned block must defeat naive tensor')
    return family, spaces, blocks, spectra


def build(k, residual, spaces, blocks):
    p, c = k + 3, k - 2
    family = list(partials(p, k))
    stars = [star for degree in range(k) for star in partials(p, degree)]
    rows = [sum(1 << i for i, port in enumerate(family) if port & star == star) for star in stars]
    allowed = sum(1 << i for i, port in enumerate(family)
                  if all(port & (3 << (2 * j)) for j in range(c)))
    basis = shorten(rows, allowed)
    full_rank = len(echelon(rows))
    require(len(basis) == full_rank - len(echelon(row & ~allowed for row in rows)), 'independent shortening rank identity')
    residual_index = {port: i for i, port in enumerate(residual)}
    coordinates = []
    for i, port in enumerate(family):
        if allowed >> i & 1:
            sign = sum(((port >> (2 * j + 1)) & 1) << j for j in range(c))
            coordinates.append((i, sign, residual_index[port >> (2 * c)]))
    def transform(word):
        components = [0] * (1 << c)
        for i, sign, index in coordinates:
            if word >> i & 1:
                components[sign] |= 1 << index
        for j in range(c):
            for sign in range(1 << c):
                if sign >> j & 1:
                    components[sign] ^= components[sign ^ (1 << j)]
        return sum(component << (40 * sign) for sign, component in enumerate(components))
    transformed = echelon(transform(word) for word in basis)
    require(len(transformed) == len(basis), 'ANF transform injective')
    dimensions, predicted_rows = [], []
    for sign in range(1 << c):
        omitted = c - sign.bit_count()
        layer = 0 if omitted < 2 else min(omitted, 4)
        projection = echelon((word >> (40 * sign)) & ((1 << 40) - 1) for word in transformed)
        require(same_space(projection, spaces[layer]), 'full-generator ANF projection versus filtration')
        dimensions.append(len(projection))
        predicted_rows.extend(word << (40 * sign) for word in spaces[layer])
    predicted = echelon(predicted_rows)
    require(same_space(transformed, predicted), 'independence of ANF components')
    formula = 40 * (1 << c) - 30 * (1 + c) - 25 * comb(c, 2) - 10 * comb(c, 3)
    require(len(basis) == formula, 'dimension formula')
    naive = echelon(word << (40 * sign) for sign in range(1 << c) for word in spaces[0])
    require(all(remainder(word, transformed) == 0 for word in naive), 'naive tensor inclusion')
    extra_weight = None
    if c >= 2:
        monomial = (1 << (c - 2)) - 1
        extra = blocks[0] << (40 * monomial)
        require(remainder(extra, transformed) == 0 and remainder(extra, naive) != 0, 'extra layer control')
        extra_weight = 4 * (1 << (c - monomial.bit_count()))
        require(extra_weight == 16, 'sharp extra-word weight')
    enumerated = 0
    low_spectrum = None
    if k == 3:
        low_spectrum = Counter()
        for word in words(basis):
            enumerated += 1
            weight = word.bit_count()
            if weight and weight < 16:
                low_spectrum[weight] += 1
                core_signs = {sign for i, sign, index in coordinates if word >> i & 1}
                require(len(core_signs) == 1, 'low weight must fix core sign')
        require(dict(low_spectrum) == {8: 20, 14: 80}, 'complete k3 low-weight census')
    return {'k': k, 'p': p, 'full_ports': len(family), 'global_star_generators': len(stars),
            'global_rank': full_rank, 'shortening_coordinates': allowed.bit_count(),
            'shortening_dimension': len(basis), 'ANF_component_dimensions': dimensions,
            'naive_tensor_dimension': len(naive), 'sharp_extra_word_weight': extra_weight,
            'full_codewords_enumerated': enumerated, 'nonzero_spectrum_below16': low_spectrum,
            'predicted_ANF_basis_sha256': sha256(json.dumps(predicted).encode()).hexdigest()}


def rm_distances():
    result = []
    for c in range(2, 5):
        for layer in range(2, min(c, 4) + 1):
            degree = c - layer
            rows = echelon(sum(1 << point for point in range(1 << c) if point & monomial == monomial)
                           for size in range(degree + 1)
                           for subset in combinations(range(c), size)
                           for monomial in [sum(1 << j for j in subset)])
            distance = min(word.bit_count() for word in words(rows) if word)
            require(distance == 1 << layer, 'core polynomial weight bound')
            result.append({'core_bits': c, 'layer': layer, 'dimension': len(rows),
                           'enumerated_polynomials': 1 << len(rows), 'minimum_weight': distance})
    return result


def verify():
    residual, spaces, blocks, spectra = residual_spaces()
    return {
        'status': 'PASS',
        'scope': 'Exact full-generator q3 shortening for k3..6, elementary unsigned ladder, residual spaces and finite low-weight checks; uniform proof is separate.',
        'unsigned_shortening_ladder': unsigned_ladder(),
        'residual_spectra': spectra,
        'core_polynomial_distances': rm_distances(),
        'cases': [build(k, residual, spaces, blocks) for k in (3, 4, 5, 6)],
        'negative_controls': [
            'unsigned residual block is outside C+_(5,2)',
            'naive tensor omits a verified weight16 shortened word for every tested k>=4',
        ],
    }

RECEIPT = 'CORE-SHORTENING-RESULTS.json'


def self_test(result):
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        script = directory / Path(__file__).name
        script.write_bytes(Path(__file__).read_bytes())
        receipt = directory / RECEIPT
        receipt.write_text(json.dumps(result))
        command = [sys.executable, "-I", "-O", "-B", str(script)]
        run = subprocess.run(command, capture_output=True, text=True)
        require(run.returncode == 0, f"isolated optimized relocated replay failed: {run.stderr}")
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
    result = json.loads(json.dumps(verify()))
    if args.check or not args.write:
        receipt = args.check or Path(__file__).resolve().with_name(RECEIPT)
        require(json.loads(receipt.read_text()) == result, f"receipt mismatch: {receipt}")
    if args.self_test:
        self_test(result)
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS", Path(__file__).name)


if __name__ == "__main__":
    main()
