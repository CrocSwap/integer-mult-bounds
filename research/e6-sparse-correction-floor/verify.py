"""Exact support-invoice obstruction. Produced by Nick Petalas. Apache-2.0."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys


INPUT = "research/e6-one-extra-frame-seed4dd9/CERTIFICATE.json"
INPUT_SHA256 = "8fb24266bef48d57bee29573404b04c7b3eb996a733db02fa57538a1ce3dd0ae"
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
BASELINE = (6, 7, 6, 6, 6, 6)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inherited_data(root):
    with (root / INPUT).open("rb") as source_file:
        data = source_file.read(65537)
    require(len(data) <= 65536, "bounded source certificate")
    require(sha256(data).hexdigest() == INPUT_SHA256, "source certificate bytes")
    source = json.loads(data)
    require(source["positive_controls"]["six_term_reference_ranks"] == list(BASELINE),
            "declared baseline premise")
    require(source["model"]["per_term_floor_w"] == 5, "declared tariff premise")
    h = tuple(tuple(Fraction(value) for value in row)
              for row in source["root_input"]["basis_gram"])
    require(len(h) == 6 and all(len(row) == 6 for row in h), "six-dimensional Gram")
    return h


def support_mask(vector):
    require(len(vector) == 6, "six coordinates")
    return sum(1 << i for i, value in enumerate(vector) if value)


def lower_histogram(mask):
    require(type(mask) is int and 1 <= mask < 64, "nonempty six-bit support")
    size = mask.bit_count()
    exceptional = int(bool(mask & 2))
    result = (size + 1, 5 - size + exceptional, 1 - exceptional)
    require(all(value >= 0 for value in result) and sum(result) == 7,
            "seven-term lower histogram")
    return result


def scalar_bill(histogram):
    return sum(count * rank for count, rank in zip(histogram, (5, 6, 7)))


def enumerate_invoices():
    invoices = 0
    attaining_relaxations = 0
    for mask in range(1, 64):
        changed = tuple(i for i in range(6) if mask & (1 << i))
        lower = lower_histogram(mask)
        minimum = 50
        for choices in product((5, 6, 7), repeat=len(changed) + 1):
            ranks = list(BASELINE) + [choices[-1]]
            for index, rank in zip(changed, choices):
                ranks[index] = rank
            require(all(ranks[i] >= 5 for i in range(7)), "charged term floor")
            require(all(sorted(ranks)[i] >= sorted(
                [rank for rank, count in zip((5, 6, 7), lower)
                 for _ in range(count)])[i] for i in range(7)),
                "coordinatewise lower moment profile")
            bill = sum(ranks)
            require(bill >= scalar_bill(lower), "support-sensitive scalar floor")
            minimum = min(minimum, bill)
            invoices += 1
        require(minimum == scalar_bill(lower), "sharp abstract relaxation")
        require(minimum == 42 - len(changed) - int(bool(mask & 2)),
                "closed-form scalar floor")
        if len(changed) <= 2:
            require(minimum >= 39, "every two-coordinate support is excluded below 39")
        attaining_relaxations += 1
    return invoices, attaining_relaxations


def factor_identity(h, direction, lam):
    require(len(direction) == 6 and any(direction) and lam != 0, "genuine input")
    columns = tuple(tuple(h[k][i] - lam * direction[i] * direction[k]
                          for k in range(6)) for i in range(6))
    reconstructed = tuple(tuple(columns[i][j] + lam * direction[i] * direction[j]
                                for j in range(6)) for i in range(6))
    require(reconstructed == h, "new-parameter coefficient identity")
    for i in range(6):
        if direction[i] == 0:
            require(columns[i] == tuple(h[k][i] for k in range(6)),
                    "zero direction coordinate preserves its term")
    return columns


def rational_fixtures(h):
    lambdas = (Fraction(-3, 2), Fraction(-1), Fraction(1, 3), Fraction(2))
    ratios = (Fraction(-5, 3), Fraction(-1, 2), Fraction(1, 2), Fraction(7, 4))
    count = 0
    for left in range(6):
        for right in range(left + 1, 6):
            for ratio, lam in product(ratios, lambdas):
                direction = [Fraction(0)] * 6
                direction[left], direction[right] = Fraction(1), ratio
                columns = factor_identity(h, direction, lam)
                require(all(any(column) for column in columns), "seven nonzero factors")
                require(scalar_bill(lower_histogram(support_mask(direction))) >= 39,
                        "new rational fixture floor")
                count += 1
    return count


def controls(h):
    for bad in (0, 64, -1, True, 1.5):
        try:
            lower_histogram(bad)
        except ValueError:
            continue
        raise ValueError("invalid support accepted")
    require(scalar_bill(lower_histogram(3)) == 39, "exceptional column debit")
    require(scalar_bill(lower_histogram(5)) == 40, "ordinary pair debit")
    require(scalar_bill(lower_histogram(2)) == 40, "one-coordinate boundary")
    require(scalar_bill(lower_histogram(63)) == 35, "fully supported boundary")
    require(all(sum(bool(h[k][i]) for k in range(6)) >= 4 for i in range(6)),
            "two-coordinate corrections cannot erase a base factor")
    return 5


def main():
    require(len(sys.argv) == 1, "no command-line arguments")
    package = Path(__file__).resolve().parent
    h = inherited_data(package.parents[1])
    invoices, supports = enumerate_invoices()
    require((invoices, supports) == (12285, 63), "complete declared finite domain")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in FILES}
    print(json.dumps({
        "marker": "PASS_E6_SPARSE_CORRECTION_FLOOR",
        "claim_type": "scoped written invoice proof with exact finite corroboration",
        "support_sets": supports,
        "abstract_invoices": invoices,
        "new_rational_fixtures": rational_fixtures(h),
        "invalid_supports_rejected": controls(h),
        "two_coordinate_charged_floor": 39,
        "decoder_attainment_of_floor": "unclaimed",
        "sha256": hashes,
        "source_sha256": INPUT_SHA256,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
