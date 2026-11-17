#!/usr/bin/env python3
"""New five-term reduction checks. Nick Petalas, Apache-2.0."""

import argparse
from collections import Counter
import hashlib
from itertools import combinations, combinations_with_replacement
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def xor_all(values):
    result = 0
    for value in values:
        result ^= value
    return result


def rank(vectors, dimension):
    pivots = [0] * dimension
    for original in vectors:
        value = original
        for bit in range(dimension - 1, -1, -1):
            if not (value >> bit) & 1:
                continue
            if pivots[bit]:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return sum(bool(value) for value in pivots)


def kernel(equations, variables):
    pivots = [0] * variables
    for original in equations:
        row = original
        for bit in range(variables - 1, -1, -1):
            if not (row >> bit) & 1:
                continue
            if pivots[bit]:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    basis = []
    for free in range(variables):
        if pivots[free]:
            continue
        value = 1 << free
        for bit in range(variables):
            if pivots[bit] and (pivots[bit] & value).bit_count() % 2:
                value ^= 1 << bit
        need(all((row & value).bit_count() % 2 == 0 for row in equations),
             "kernel vector violates its equation")
        basis.append(value)
    need(len(basis) + rank(equations, variables) == variables,
         "kernel dimension violates rank-nullity")
    need(rank(basis, variables) == len(basis), "kernel basis is dependent")
    return basis


def linear_combinations(basis):
    return [xor_all(value for bit, value in enumerate(basis) if mask >> bit & 1)
            for mask in range(1 << len(basis))]


def pattern_basis(frames, dimension):
    counts = Counter(frames)
    if dimension == 2:
        need(sorted(counts.values()) == [1, 1, 3], "wrong dimension-two type")
        repeated = next(value for value in counts if counts[value] == 3)
        single = next(value for value in counts if counts[value] == 1)
        return [repeated, single]
    if dimension == 3:
        need(sorted(counts.values()) == [1, 1, 1, 2], "wrong dimension-three type")
        triple = [value for value in counts if counts[value] == 1]
        pair = next(value for value in counts if counts[value] == 2)
        need(xor_all(triple) == 0, "dimension-three triple does not sum to zero")
        need(rank([*triple, pair], dimension) == 3, "pair is not independent")
        return [triple[0], triple[1], pair]
    need(dimension == 4 and len(counts) == 5, "wrong dimension-four type")
    need(all(rank(subset, 4) == 4 for subset in combinations(frames, 4)),
         "dimension-four type is not a five-circuit")
    return list(frames[:4])


def syzygy_check(frames, basis):
    """Check every pointwise kernel-basis syzygy in ambient dimension six."""
    ambient = 6
    equations = []
    for row in range(ambient):
        for column in range(row, ambient):
            equation = 0
            for index, frame in enumerate(frames):
                if frame >> row & 1:
                    equation ^= 1 << (index * ambient + column)
                if row != column and frame >> column & 1:
                    equation ^= 1 << (index * ambient + row)
            equations.append(equation)
    solutions = kernel(equations, 5 * ambient)
    combinations_of_basis = linear_combinations(basis)
    coordinates = [combinations_of_basis.index(frame) for frame in frames]
    allowed = [set(linear_combinations(basis[:i] + basis[i + 1:]))
               for i in range(len(basis))]
    for solution in solutions:
        images = [(solution >> (ambient * j)) & 63 for j in range(5)]
        for index in range(len(basis)):
            coefficient = xor_all(images[j] for j in range(5)
                                  if coordinates[j] >> index & 1)
            need(coefficient in allowed[index], "syzygy image escaped the other forms")
    return len(solutions)


def multiplicity_census():
    counts = {}
    syzygy_dimensions = Counter()
    for dimension in range(1, 5):
        count = 0
        for frames in combinations_with_replacement(range(1, 1 << dimension), 5):
            if xor_all(frames) or rank(frames, dimension) != dimension:
                continue
            basis = pattern_basis(frames, dimension)
            need(rank(basis, dimension) == dimension, "pattern basis lost rank")
            syzygy_dimensions[syzygy_check(frames, basis)] += 1
            count += 1
        counts[str(dimension)] = count
    need(counts == {"1": 0, "2": 3, "3": 28, "4": 168}, "multiplicity census changed")
    return {"full_span_multisets": counts,
            "pointwise_syzygy_kernel_dimensions": dict(sorted(syzygy_dimensions.items()))}


def field_mul(left, right, modulus, dimension):
    result = 0
    for bit in range(dimension):
        if right >> bit & 1:
            result ^= left
        left <<= 1
        if left >> dimension & 1:
            left ^= modulus
    return result


def field_inverse(value, modulus, dimension):
    need(0 < value < 1 << dimension, "invalid nonzero field element")
    result = 1
    power = value
    exponent = (1 << dimension) - 2
    for bit in range(dimension):
        if exponent >> bit & 1:
            result = field_mul(result, power, modulus, dimension)
        power = field_mul(power, power, modulus, dimension)
    need(field_mul(value, result, modulus, dimension) == 1, "field inverse failed")
    return result


def multiplication_matrix(value, modulus, dimension):
    result = 0
    for column in range(dimension):
        image = field_mul(value, 1 << column, modulus, dimension)
        for row in range(dimension):
            result |= ((image >> row) & 1) << (row * dimension + column)
    return result


def matrix_mul(left, right, dimension):
    result = 0
    mask = (1 << dimension) - 1
    for row in range(dimension):
        value = 0
        for middle in range(dimension):
            if left >> (row * dimension + middle) & 1:
                value ^= (right >> (middle * dimension)) & mask
        result |= value << (row * dimension)
    return result


def matrix_rank(value, dimension):
    mask = (1 << dimension) - 1
    return rank([(value >> (row * dimension)) & mask for row in range(dimension)],
                dimension)


def symmetric_product(left, right, dimension):
    result = 0
    for row in range(dimension):
        if not left >> row & 1:
            continue
        for column in range(dimension):
            if right >> column & 1:
                low, high = min(row, column), max(row, column)
                result ^= 1 << (low * dimension + high)
    return result


def make_witness(dimension, modulus):
    x, y = 1, 1 << dimension
    # Split the first x of the credited four-term witness into y and x+y.
    return {"dimension": dimension, "modulus": modulus,
            "frames": [y, x ^ y, x, x, x],
            "left": [1, 1, 2, 3, 3], "right": [3, 3, 3, 1, 2]}


def witness_check(data):
    m, modulus = data["dimension"], data["modulus"]
    need(4 <= m <= 8 and modulus.bit_length() == m + 1, "invalid fixture size")
    frames, left, right = data["frames"], data["left"], data["right"]
    need(len(frames) == len(left) == len(right) == 5, "wrong contribution arity")
    need(all(0 < frame < 1 << (m * m) and matrix_rank(frame, m) == 1
             for frame in frames), "frame is not rank one")
    need(xor_all(frames) == 0, "constant condition failed")
    matrices = [multiplication_matrix(value, modulus, m) for value in left]
    rights = [multiplication_matrix(value, modulus, m) for value in right]
    inverses = [multiplication_matrix(field_inverse(value, modulus, m), modulus, m)
                for value in left]
    inverse_rights = [multiplication_matrix(field_inverse(value, modulus, m), modulus, m)
                      for value in right]
    for column in range(m * m):
        total = 0
        for index in range(5):
            image = matrix_mul(matrix_mul(matrices[index], 1 << column, m), rights[index], m)
            restored = matrix_mul(matrix_mul(inverses[index], image, m), inverse_rights[index], m)
            need(restored == 1 << column, "transport inverse failed")
            total ^= symmetric_product(frames[index], image, m * m)
        need(total == 0, "quadratic condition failed")
    beta = xor_all(matrix_mul(matrix_mul(inverses[j], frames[j], m), inverse_rights[j], m)
                   for j in range(5))
    need(matrix_rank(beta, m) == 2, "residue rank is not two")
    need(rank(frames, m * m) == 2, "witness frame span changed")
    need(len(set(zip(left, right))) == 4, "witness transport multiplicity changed")
    return {"dimension": m, "modulus": modulus, "frames": frames,
            "left": left, "right": right, "beta": beta, "beta_rank": 2}


def rejection_controls(data):
    mutations = []
    missing = {key: list(value) if isinstance(value, list) else value
               for key, value in data.items()}
    for key in ("frames", "left", "right"):
        missing[key].pop()
    mutations.append((missing, "arity"))
    frame = {**data, "frames": list(data["frames"])}
    frame["frames"][0] ^= 1
    mutations.append((frame, "constant"))
    transport = {**data, "left": list(data["left"])}
    transport["left"][0] = 2
    mutations.append((transport, "quadratic"))
    rejected = []
    for mutation, expected in mutations:
        try:
            witness_check(mutation)
        except ValueError as error:
            need(expected in str(error), "mutation failed at the wrong condition")
            rejected.append(expected)
        else:
            raise ValueError("mutation was accepted: " + expected)
    need(symmetric_product(1, 1, 6) != 0, "polynomial square was discarded")
    return rejected + ["retained polynomial square"]


def authenticated_sources(package):
    root = package.parents[1]
    sources = json.loads((package / "SOURCES.json").read_text())
    need(len(sources["files"]) == 4, "source manifest row count changed")
    expected = {"research/bit-four-term-twist-escape/PROOF.md",
                "research/bit-three-term-twist-rigidity/PROOF.md"}
    authenticated = {}
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        need(row["path"] in expected, "unexpected proof path")
        source = root / row["path"]
        need(source.is_file() and not source.is_symlink(), "source is not regular")
        need(source.stat().st_size <= 262144, "source exceeds capacity")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        need(digest == row["sha256"], "source digest differs: " + row["path"])
        authenticated[row["path"]] = digest
    need(set(authenticated) == expected, "wrong cited proof inputs")
    return authenticated


def run(package):
    expected = {"README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"}
    files = sorted(path for path in package.iterdir() if path.is_file())
    need({path.name for path in files} == expected, "unexpected package file inventory")
    need(all(not path.is_symlink() and path.stat().st_size <= 262144 for path in files),
         "package capacity or regular-file condition failed")
    sources = authenticated_sources(package)
    census = multiplicity_census()
    fixtures = [(4, 0x13), (5, 0x25), (6, 0x43), (7, 0x83), (8, 0x11B)]
    witnesses = []
    for dimension, modulus in fixtures:
        for value in range(1, 1 << dimension):
            field_inverse(value, modulus, dimension)
        witnesses.append(witness_check(make_witness(dimension, modulus)))
    controls = rejection_controls(make_witness(4, 0x13))
    return {"status": "PASS_FIVE_TERM_RESIDUE_BOUND", "claim_type": "scoped written proof",
            "census": census, "new_five_frame_witnesses": witnesses,
            "controls": controls, "cited_proof_sha256": sources,
            "package_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in files}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a fresh receipt outside the repository")
    arguments = parser.parse_args()
    package = Path(__file__).resolve().parent
    if arguments.receipt is not None:
        need(not arguments.receipt.resolve().is_relative_to(package.parents[1]),
             "receipt must be outside the repository")
    result = run(package)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.receipt is not None:
        with arguments.receipt.open("x") as output:
            output.write(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
