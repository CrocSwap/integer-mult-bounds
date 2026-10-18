#!/usr/bin/env python3
"""Exact finite research verification; Python 3.10+, standard library only.

Copyright 2026 Sam Sung. Apache-2.0. Substantial OpenAI Codex assistance.
Finite checks supplement the written proofs; they are not formal proofs.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
from fractions import Fraction
from itertools import combinations, product
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ports(p, k):
    return [sum(1 << (2*i+s) for i, s in zip(pairs, signs))
            for pairs in combinations(range(p), k) for signs in product((0, 1), repeat=k)]


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def rational_rank(columns):
    pivots = {}
    for column in columns:
        column = [Fraction(x) for x in column]
        for pivot in sorted(pivots):
            coefficient = column[pivot]
            if coefficient:
                column = [x - coefficient*y for x, y in zip(column, pivots[pivot])]
        pivot = next((i for i, value in enumerate(column) if value), None)
        if pivot is not None:
            coefficient = column[pivot]
            pivots[pivot] = [x/coefficient for x in column]
    return len(pivots)


def xor(words):
    result = 0
    for word in words:
        result ^= word
    return result


def check_case(p, k):
    family = ports(p, k)
    count = len(family)
    certificate = [sum(((1 + (target & source).bit_count()) % 2) << j
                       for j, source in enumerate(family)) for target in family]
    require(all(row >> i & 1 for i, row in enumerate(certificate)), "certificate diagonal")
    require(all(not (row >> j & 1) for target, row in zip(family, certificate)
                for j, source in enumerate(family) if (target & source).bit_count() == 1),
            "certificate fails to annihilate cap-readable entries")
    # Independently expand one anchored proper-star formula per target.
    recipes = []
    used = set()
    for target in family:
        coordinates = [i for i in range(2*p) if target >> i & 1]
        anchor, others = coordinates[0], coordinates[1:]
        recipe = []
        for degree in range(k - 1):
            for subset in combinations(others, degree):
                face = (1 << anchor) | sum(1 << i for i in subset)
                recipe.append(face)
                used.add(face)
        recipes.append(recipe)
    faces = sorted(used)
    observations = {face: sum(1 << j for j, source in enumerate(family) if source & face == face)
                    for face in faces}
    coefficients = {face: [i for i, recipe in enumerate(recipes) if face in recipe] for face in faces}
    decoder = [xor(observations[face] for face in recipe) for recipe in recipes]
    require(all(row >> i & 1 for i, row in enumerate(decoder)), "missing own-source coefficient")
    for i, row in enumerate(decoder):
        correction = row ^ (1 << i)
        require(all((family[i] & source).bit_count() == 1 for j, source in enumerate(family)
                    if correction >> j & 1), "non-readable correction in decoder")
        require(row & certificate[i] == 1 << i, "Hadamard identity failed")
    reconstructed = [0] * count
    total_frame_rank = 0
    total_term_rank = 0
    term_summary = {}
    for face, observation in observations.items():
        target_indices = coefficients[face]
        terms = [certificate[i] & observation for i in target_indices]
        term_rank = binary_rank(terms)
        sources = [source for j, source in enumerate(family) if observation >> j & 1]
        augmented_binary_rank = binary_rank(1 | source << 1 for source in sources)
        coordinates = [[(source >> i) & 1 for i in range(2*p)] for source in sources]
        label_rank = rational_rank(coordinates)
        augmented_rational_rank = rational_rank([[1] + column for column in coordinates])
        require(label_rank == augmented_rational_rank, "constant-weight rational augmentation")
        require(term_rank <= augmented_binary_rank <= augmented_rational_rank,
                "binary/rational rank bridge")
        for i, term in zip(target_indices, terms):
            reconstructed[i] ^= term
        total_frame_rank += label_rank
        total_term_rank += term_rank
        key = (face.bit_count(), term_rank, augmented_binary_rank, label_rank)
        term_summary[str(key)] = term_summary.get(str(key), 0) + 1
    require(reconstructed == [1 << i for i in range(count)], "rank-one sum is not identity")
    require(count <= total_term_rank <= total_frame_rank, "summed copy-rank bound")
    # The broader fixed-observation lower bound is tight: copy each source alone.
    require(all(rational_rank([[(source >> i) & 1 for i in range(2*p)]]) == 1
                for source in family), "singleton-frame tightness")
    return dict(p=p, k=k, ports=count, observations=len(faces),
                total_term_rank=total_term_rank, total_literal_frame_rank=total_frame_rank,
                tight_individual_copy_cost=count, term_types=term_summary)


def negative_controls():
    odd = ports(4, 3)
    require(all((1 + target.bit_count()) % 2 == 0 for target in odd), "odd-k control")
    family = ports(6, 4)
    require(any((a & b).bit_count() == 0 and (1+(a & b).bit_count()) % 2 == 1
                for a in family for b in family), "overlap-zero readability must violate annihilation")
    require(any((a & b).bit_count() == 2 and (1+(a & b).bit_count()) % 2 == 1
                for a in family for b in family), "overlap-two readability must violate annihilation")
    # Recovering all targets cannot be certified after deleting a required summand.
    require(binary_rank([1 << i for i in range(7)]) < 8, "missing-observation rank control")
    return ["odd-k diagonal vanishes", "overlap-zero correction survives certificate",
            "overlap-two correction survives certificate", "missing observation loses identity rank"]


def sequential_innovations():
    """A protocol fragment where raw copy supports exceed their native frames."""
    family = ports(3, 2)
    copied = []
    innovations = []
    violations = 0
    for i, source in enumerate(family):
        # Add the prior frame-zero copied prefix to the next native source.
        # The new copy comes from that source's rank-one frame.
        word = (1 << (i+1)) - 1
        innovation = word
        for previous in reversed(copied):
            pivot = previous.bit_length() - 1
            if innovation >> pivot & 1:
                innovation ^= previous
        require(innovation == 1 << i, "chronological native representative")
        require(binary_rank(copied + [word]) == binary_rank(copied + [innovation]),
                "triangular copied-span replacement")
        copied.append(word)
        innovations.append(innovation)
        raw_labels = [[(label >> bit) & 1 for bit in range(6)] for label in family[:i+1]]
        violations += int(rational_rank(raw_labels) > 1)
        require(rational_rank([[(source >> bit) & 1 for bit in range(6)]]) == 1,
                "native innovation frame rank")
    recovered = [word ^ (copied[i-1] if i else 0) for i, word in enumerate(copied)]
    require(recovered == innovations == [1 << i for i in range(len(family))],
            "prefix copy decoding")
    require(violations > 0, "raw support containment must fail after copy reuse")
    return dict(copy_episodes=len(copied), charged_native_rank=len(copied),
                raw_copies_exceeding_native_frame_rank=violations,
                scope="Chronological source-row invariant on a copy-reuse fragment; "
                      "not a complete restored supplier schedule.")



def verify():
    cases = [check_case(p, 2) for p in range(3, 7)]
    cases += [check_case(p, 4) for p in range(4, 8)]
    return dict(status="PASS", scope="Exact finite rank-certificate and anchored decoder checks; "
                "not a physical supplier replay or a substitute for the uniform proof.",
                cases=cases, negative_controls=negative_controls(),
                sequential_copy_fragment=sequential_innovations())

RECEIPT = 'COPY-OBSTRUCTION-RESULTS.json'


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
