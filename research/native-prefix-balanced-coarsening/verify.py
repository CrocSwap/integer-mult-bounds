"""Check the new rounded interface, exact inverse, and rejection controls."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

from model import Native, balanced, flatten, require

PACKAGE = Path(__file__).resolve().parent


def moments(numerators: tuple[int, ...], denominator: int) -> int:
    first = [0] * len(numerators)
    second = [0] * len(numerators)
    prefix_first = [0] * len(numerators)
    prefix_second = [0] * len(numerators)
    for seed in range(denominator):
        output = balanced(numerators, denominator, seed)
        exact_sum = 0
        rounded_sum = 0
        for j, (value, rounded) in enumerate(zip(numerators, output, strict=True)):
            exact_sum += value
            rounded_sum += rounded
            error = denominator * rounded - value
            prefix_error = denominator * rounded_sum - exact_sum
            first[j] += error
            second[j] += error * error
            prefix_first[j] += prefix_error
            prefix_second[j] += prefix_error * prefix_error
            require(abs(error) < denominator, "coordinate nearest neighbors")
            require(abs(prefix_error) < denominator, "prefix nearest neighbors")
            require(rounded_sum == (exact_sum + seed) // denominator, "dense prefix oracle")
    exact_sum = 0
    for j, value in enumerate(numerators):
        exact_sum += value
        residue = value % denominator
        prefix_residue = exact_sum % denominator
        require(first[j] == prefix_first[j] == 0, "exact unbiasedness")
        require(second[j] == denominator * residue * (denominator - residue), "coordinate optimum")
        require(prefix_second[j] == denominator * prefix_residue * (denominator - prefix_residue),
                "prefix optimum")
    return denominator


def exhaustive_rounding() -> dict[str, int]:
    fixtures = 0
    seeds = 0
    translations = 0
    for denominator in (2, 4, 8):
        for length in range(1, 5):
            for residues in itertools.product(range(denominator), repeat=length):
                offsets = tuple((-1 if j % 2 else 1) * (j + 1) for j in range(length))
                signed = tuple(r + denominator * z for r, z in zip(residues, offsets, strict=True))
                seeds += moments(signed, denominator)
                fixtures += 1
                for seed in (0, denominator - 1):
                    old = balanced(residues, denominator, seed)
                    new = balanced(signed, denominator, seed)
                    require(new == tuple(q + z for q, z in zip(old, offsets, strict=True)), "translation")
                    translations += 1
    return dict(fixtures=fixtures, seed_vectors=seeds, translations=translations)


def quotient_endpoints() -> int:
    endpoints = 0
    for size, active, precision in ((2, 1, 1), (4, 2, 1)):
        native = Native(size, active, precision)
        coarse_fields = (
            tuple((0, 0) for _ in range(size)),
            tuple((j - 3, 2 - j) for j in range(size)),
            tuple((7 - j, -5 - j) for j in range(size)),
        )
        for label in range(1 << native.label_bits):
            for seed in range(native.denominator):
                for coarse in coarse_fields:
                    fine = native.decode(coarse, label, seed)
                    require(native.encode(fine, seed) == (coarse, label), "two-sided endpoint")
                    endpoints += 1
    return endpoints


def native_fields() -> dict[str, int]:
    seeds = 0
    roundtrips = 0
    for active in range(1, 9):
        native = Native(512, active, 5)
        values = tuple(((17 * j + 3) % 23 - 11, (19 * j + 5) % 29 - 14) for j in range(512))
        seeds += moments(flatten(native.numerators(values)), native.denominator)
        for seed in (0, native.denominator // 2, native.denominator - 1):
            coarse, label = native.encode(values, seed)
            require(native.decode(coarse, label, seed) == values, "native fine roundtrip")
            arbitrary = tuple((p + j % 3 - 1, q - j % 5 + 2)
                              for j, (p, q) in enumerate(coarse))
            fine = native.decode(arbitrary, label, seed)
            require(native.encode(fine, seed) == (arbitrary, label), "native coarse roundtrip")
            roundtrips += 2
    return dict(ranks=8, complete_seed_vectors=seeds, two_sided_roundtrips=roundtrips)


def improvement() -> dict[str, int]:
    native = Native(512, 8, 5)
    half_field = tuple((16, 16) for _ in range(512))
    numerators = flatten(native.numerators(half_field))
    require(set(numerators) == {native.denominator // 2}, "reachable half-grid input")
    common_square_sum = 0
    balanced_square_sum = 0
    for seed in range(native.denominator):
        common = tuple((n + seed) // native.denominator for n in numerators)
        new = balanced(numerators, native.denominator, seed)
        common_square_sum += (sum(common) - 512) ** 2
        balanced_square_sum += (sum(new) - 512) ** 2
    require(common_square_sum == native.denominator * 512**2, "old reader variance")
    require(balanced_square_sum == 0, "exact new reader")
    sharp = tuple((16, 0) if j == 0 else (0, 0) for j in range(512))
    sharp_n = flatten(native.numerators(sharp))
    require(sum(sharp_n) * 2 == native.denominator, "sharp total mean")
    square = sum((2 * sum(balanced(sharp_n, native.denominator, seed)) - 1) ** 2
                 for seed in range(native.denominator))
    require(square == native.denominator, "sharp quarter variance")
    return dict(common_variance=512**2, balanced_variance=0, sharp_bound_numerator=1,
                sharp_bound_denominator=4, coordinates=1024, retained_bits=native.label_bits,
                fair_seed_bits=native.denominator.bit_length() - 1)


def controls() -> int:
    rejected = 0
    for numerators, denominator, seed in (((1,), 0, 0), ((1,), 2, -1), ((1,), 2, 2), ((), 2, 0)):
        try:
            balanced(numerators, denominator, seed)
        except ValueError:
            rejected += 1
    for args in ((3, 1, 1), (2, 2, 1), (2, 1, 0)):
        try:
            Native(*args)
        except ValueError:
            rejected += 1
    native = Native(2, 1, 1)
    for label in (-1, 1 << native.label_bits):
        try:
            native.representative(label)
        except ValueError:
            rejected += 1
    require(rejected == 9, "domain rejection count")
    require(sum((n + 0) // 2 for n in (1, 1)) != sum(balanced((1, 1), 2, 0)),
            "reset-carry mutant rejected")
    require(balanced((1, 0), 2, 0) != balanced((1, 0), 2, 1), "missing-seed mutant rejected")
    zero = ((0, 0), (0, 0))
    first = native.decode(zero, 0, 0)
    second = native.decode(zero, 1, 0)
    require(first != second and native.quantize(first, 0) == native.quantize(second, 0),
            "missing-residue collision")
    return rejected + 3


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    arguments = parser.parse_args()
    origin = json.loads((PACKAGE / "ORIGIN.json").read_text())
    source = PACKAGE / "inputs" / "PR6540-PROOF.md"
    require(hashlib.sha256(source.read_bytes()).hexdigest() == origin["sha256"], "source provenance")
    result = dict(rounding=exhaustive_rounding(), quotient_endpoints=quotient_endpoints(),
                  native=native_fields(), improvement=improvement(), controls=controls())
    result["package_sha256"] = {
        path.relative_to(PACKAGE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(PACKAGE.rglob("*")) if path.is_file() and "__pycache__" not in path.parts
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.receipt:
        require(not arguments.receipt.resolve().is_relative_to(PACKAGE), "receipt must be outside package")
        require(arguments.receipt.write_text(payload) == len(payload), "complete receipt write")
    print(payload, end="")
    print("PASS_NATIVE_PREFIX_BALANCED_COARSENING")


if __name__ == "__main__":
    main()
