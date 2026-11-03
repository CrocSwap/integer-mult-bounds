"""Exact finite corroboration of the Fourier integrality lemma.

Produced by Nick Petalas. Apache-2.0.
No predecessor scientific executable is imported or replayed.
"""

from hashlib import sha256
from itertools import combinations_with_replacement
from math import comb
import json
from pathlib import Path
import sys


PACKAGE_FILES = (
    "PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(dimension: int, polars: tuple[int, ...]) -> None:
    require(type(dimension) is int and 1 <= dimension <= 4, "dimension domain")
    require(type(polars) is tuple, "tuple domain")
    require(1 <= len(polars) <= 9 and len(polars) % 2 == 1, "odd size domain")
    require(all(type(p) is int and 0 < p < (1 << dimension) for p in polars),
            "nonzero polar domain")


def character_weights(dimension: int, polars: tuple[int, ...]) -> tuple[int, ...]:
    """Direct character evaluation, independent of the butterfly transform."""
    return tuple(sum((p & chi).bit_count() % 2 for p in polars)
                 for chi in range(1 << dimension))


def walsh(values: tuple[int, ...]) -> tuple[int, ...]:
    require(len(values) in (2, 4, 8, 16), "transform size domain")
    result = list(values)
    for level in range(len(values).bit_length() - 1):
        step = 1 << level
        for start in range(0, len(values), 2 * step):
            for offset in range(step):
                left = start + offset
                a, b = result[left], result[left + step]
                result[left], result[left + step] = a + b, a - b
    return tuple(result)


def is_subspace_indicator(multiplicities: tuple[int, ...]) -> bool:
    if any(value not in (0, 1) for value in multiplicities):
        return False
    support = tuple(i for i, value in enumerate(multiplicities) if value)
    return 0 in support and all(multiplicities[a ^ b] == 1
                               for a in support for b in support)


def analyze(dimension: int, polars: tuple[int, ...]) -> bool:
    validate(dimension, polars)
    counts = [0] * (1 << dimension)
    counts[0] = 1
    for polar in polars:
        counts[polar] += 1
    weights = character_weights(dimension, polars)
    spectrum = walsh(tuple(counts))
    require(spectrum == tuple(1 + len(polars) - 2 * t for t in weights),
            "direct and butterfly characters differ")
    inversion = walsh(spectrum)
    require(inversion == tuple(len(counts) * x for x in counts),
            "Fourier inversion failed")
    positive = min(spectrum) >= 0
    require(positive == (max(weights) <= (len(polars) + 1) // 2),
            "threshold mismatch")
    require(positive == is_subspace_indicator(tuple(counts)),
            "subspace rigidity failed")
    if positive:
        require((len(polars) + 1).bit_count() == 1, "non-power subspace order")
        require(len(set(polars)) == len(polars), "repeated positive polar")
    else:
        require(max(weights) >= (len(polars) + 3) // 2,
                "missing strict character witness")
    return positive


def subspace_count(dimension: int, size: int) -> int:
    if (size + 1).bit_count() != 1:
        return 0
    rank = (size + 1).bit_length() - 1
    if rank > dimension:
        return 0
    numerator = denominator = 1
    for i in range(rank):
        numerator *= (1 << dimension) - (1 << i)
        denominator *= (1 << rank) - (1 << i)
    require(numerator % denominator == 0, "nonintegral subspace count")
    return numerator // denominator


def enumerate_multisets() -> list[dict[str, int]]:
    rows = []
    for dimension, maximum_size in ((1, 9), (2, 9), (3, 9), (4, 5)):
        for size in range(1, maximum_size + 1, 2):
            total = positive = 0
            for polars in combinations_with_replacement(range(1, 1 << dimension), size):
                positive += analyze(dimension, polars)
                total += 1
            require(total == comb((1 << dimension) + size - 2, size),
                    "multiset enumeration incomplete")
            require(positive == subspace_count(dimension, size),
                    "subspace count disagrees with direct enumeration")
            rows.append({"dimension": dimension, "size": size,
                         "multisets": total, "rigid": positive})
    return rows


def matched_boundary(banks: int) -> dict[str, int]:
    require(type(banks) is int and banks in (1, 4), "bank domain")
    # These dimensions and rank bounds are cited PR2070 premises.
    span, defect = 112 * banks, 16 * banks
    old_bound = (4 * span - 2 * defect + 2) // 3
    cap = defect - 2 * span + 2 * old_bound
    require(old_bound % 2 == 1, "odd boundary missing")
    require(cap == (old_bound + 1) // 2, "half-weight boundary missing")
    require((old_bound + 1).bit_count() != 1, "simplex boundary cannot be excluded")
    return {"banks": banks, "cited_span_each": span, "cited_defect_cap": defect,
            "cited_average_bound": old_bound, "active_cap_at_boundary": cap,
            "forced_active_witness": (old_bound + 3) // 2,
            "new_event_lower_bound": old_bound + 1}


def rejection_controls() -> int:
    invalid = ((0, (1,)), (5, (1,)), (True, (1,)), (2, ()),
               (2, (1, 2)), (2, (0, 1, 2)), (2, (1, 2, 4)),
               (2, (True,)), (2, [1]), (2, (1,) * 11))
    for dimension, polars in invalid:
        try:
            analyze(dimension, polars)
        except ValueError:
            continue
        raise ValueError("invalid multiset accepted")
    require(analyze(2, (1, 2, 3)), "simplex positive control failed")
    require(analyze(3, tuple(range(1, 8))), "larger simplex control failed")
    require(not analyze(2, (1, 1, 1)), "repeated-polar control failed")
    require(max(character_weights(2, (0, 0, 1, 2, 3))) <= 3,
            "zero-polar scope witness disappeared")
    require(max(character_weights(2, (1, 2, 3))) > 1,
            "incorrect lower threshold would pass simplex")
    for invalid_banks in (0, 2, True):
        try:
            matched_boundary(invalid_banks)
        except ValueError:
            continue
        raise ValueError("invalid bank count accepted")
    return len(invalid) + 3


def main() -> None:
    require(len(sys.argv) == 1, "this verifier accepts no arguments")
    rows = enumerate_multisets()
    boundaries = [matched_boundary(banks) for banks in (1, 4)]
    controls = rejection_controls()
    package = Path(__file__).resolve().parent
    hashes = {name: sha256((package / name).read_bytes()).hexdigest()
              for name in PACKAGE_FILES}
    receipt = {"marker": "PASS_MATCHED_PHASE_INTEGRALITY",
               "claim_type": "scoped proof with exact finite corroboration",
               "source_premises": "cited PR2070 conclusions, not replayed",
               "multisets": sum(row["multisets"] for row in rows),
               "rigid_multisets": sum(row["rigid"] for row in rows),
               "domain_rejections": controls, "semantic_control_groups": 5,
               "domains": rows, "matched_boundaries": boundaries,
               "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
