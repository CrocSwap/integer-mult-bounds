"""Audit the historical Johnson spectral bound with literal binary matrices."""
import argparse
import json
import sys
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from typing import Sequence, TypedDict

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from experiments.single_intersection import spectral_parity_bound


class AuditFailure(ValueError):
    """A source pin or exact mathematical comparison failed."""


class CaseResult(TypedDict):
    h: int
    k: int
    j: int
    order: int
    characteristic_polynomial_hex: str
    odd_eigenvalue_multiplicity: int
    binary_rank: int
    squared_binary_rank: int
    rank_gap: int
    rows_sha256: str


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditFailure(message)


def validate_rows(rows: Sequence[int]) -> None:
    limit = 1 << len(rows)
    require(all(type(row) is int and 0 <= row < limit for row in rows),
            "Rows must encode a square binary matrix")


def literal_rows(h: int, k: int, j: int) -> list[int]:
    require(all(type(value) is int for value in (h, k, j)) and
            2 <= k <= h // 2 and 0 <= j < k, "Invalid subset parameters")
    labels = [frozenset(label) for label in combinations(range(h), k)]
    return [sum(1 << column for column, target in enumerate(labels)
                if source == target or len(source & target) == j)
            for source in labels]


def binary_rank(rows: Sequence[int]) -> int:
    validate_rows(rows)
    work = list(rows)
    pivot_row = 0
    for column in range(len(rows)):
        pivot = next((row for row in range(pivot_row, len(rows))
                      if work[row] & (1 << column)), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        for row in range(pivot_row + 1, len(rows)):
            if work[row] & (1 << column):
                work[row] ^= work[pivot_row]
        pivot_row += 1
    return pivot_row


def binary_square(rows: Sequence[int]) -> list[int]:
    validate_rows(rows)
    squared = []
    for row in rows:
        value = 0
        indices = row
        while indices:
            bit = indices & -indices
            value ^= rows[bit.bit_length() - 1]
            indices ^= bit
        squared.append(value)
    return squared


def characteristic_polynomial(rows: Sequence[int]) -> int:
    """Return det(xI-A), with polynomial coefficients encoded as bits."""
    validate_rows(rows)
    work = list(rows)
    order = len(rows)
    for column in range(order - 1):
        target = column + 1
        pivot = next((row for row in range(target, order)
                      if work[row] & (1 << column)), None)
        if pivot is None:
            continue
        if pivot != target:
            work[pivot], work[target] = work[target], work[pivot]
            mask = (1 << target) | (1 << pivot)
            for row in range(order):
                if ((work[row] >> target) ^ (work[row] >> pivot)) & 1:
                    work[row] ^= mask
        for row in range(target + 1, order):
            if work[row] & (1 << column):
                work[row] ^= work[target]
                for index in range(order):
                    if work[index] & (1 << row):
                        work[index] ^= 1 << target
    require(all(not (work[row] & ((1 << (row - 1)) - 1))
                for row in range(2, order)), "Hessenberg reduction failed")
    leading = [1]
    for size in range(1, order + 1):
        column = size - 1
        polynomial = leading[-1] << 1
        if work[column] & (1 << column):
            polynomial ^= leading[-1]
        for row in range(column - 1, -1, -1):
            if not (work[row + 1] & (1 << row)):
                break
            if work[row] & (1 << column):
                polynomial ^= leading[row]
        leading.append(polynomial)
    return leading[-1]


def parity_polynomial(order: int, odd_multiplicity: int) -> int:
    require(type(order) is int and type(odd_multiplicity) is int and
            0 <= odd_multiplicity <= order, "Invalid spectral multiplicity")
    polynomial = 1
    for _ in range(odd_multiplicity):
        polynomial = (polynomial << 1) ^ polynomial
    return polynomial << (order - odd_multiplicity)


def check_spectrum(rows: Sequence[int], odd_multiplicity: int) -> int:
    polynomial = characteristic_polynomial(rows)
    require(polynomial == parity_polynomial(len(rows), odd_multiplicity),
            "Literal characteristic polynomial disagrees with claimed spectrum")
    actual_rank = binary_rank(rows)
    require(actual_rank >= odd_multiplicity,
            "Spectral rank lower bound exceeds literal binary rank")
    return polynomial


def audit_case(h: int, k: int, j: int) -> CaseResult:
    rows = literal_rows(h, k, j)
    claimed = spectral_parity_bound(h, k, j)
    odd_multiplicity = claimed["binary_rank_lower"]
    require(type(odd_multiplicity) is int, "Claimed multiplicity must be integral")
    polynomial = check_spectrum(rows, odd_multiplicity)
    actual_rank = binary_rank(rows)
    return CaseResult(h=h, k=k, j=j, order=len(rows),
                      characteristic_polynomial_hex=hex(polynomial),
                      odd_eigenvalue_multiplicity=odd_multiplicity,
                      binary_rank=actual_rank,
                      squared_binary_rank=binary_rank(binary_square(rows)),
                      rank_gap=actual_rank - odd_multiplicity,
                      rows_sha256=sha256(json.dumps(rows, separators=(",", ":"))
                                         .encode()).hexdigest())


def source_pins() -> dict[str, str]:
    source = json.loads((PACKAGE / "SOURCE.json").read_text())
    pins: dict[str, str] = source["source_sha256"]
    for path, expected in pins.items():
        require(sha256((ROOT / ('research/single-intersection-spectrum-audit/BASE-CHECKPOINT.json'
                        if path == 'certificates/selected-result.json' else path)).read_bytes()).hexdigest() == expected,
                "Changed pinned source: " + path)
    return pins


def negative_controls() -> dict[str, object]:
    rows = literal_rows(7, 3, 0)
    edges = ((0, 32), (1, 28), (0, 1), (28, 32))
    require(all(rows[left] & (1 << right) for left, right in edges[:2]) and
            all(not (rows[left] & (1 << right)) for left, right in edges[2:]),
            "Changed degree-preserving control fixture")
    mutated = list(rows)
    for left, right in edges:
        mutated[left] ^= 1 << right
        mutated[right] ^= 1 << left
    require([row.bit_count() for row in rows] ==
            [row.bit_count() for row in mutated], "Control changed row degrees")
    require(all((rows[index] ^ mutated[index]) & (1 << index) == 0
                for index in range(len(rows))), "Control changed diagonal")
    rejected = []
    for name, candidate, multiplicity in (
            ("wrong_odd_multiplicity", rows, 16),
            ("degree_preserving_two_switch", mutated, 15)):
        try:
            check_spectrum(candidate, multiplicity)
        except AuditFailure as failure:
            rejected.append({"name": name, "reason": str(failure)})
        else:
            raise AuditFailure("Negative control was accepted: " + name)
    nilpotent = literal_rows(4, 2, 0)
    require(binary_rank(nilpotent) == 3 and binary_square(nilpotent) == [0] * 6,
            "Changed nonsemisimple witness")
    return {"rejected": rejected,
            "two_switch": {"h": 7, "k": 3, "j": 0,
                           "removed_edges": [list(edge) for edge in edges[:2]],
                           "added_edges": [list(edge) for edge in edges[2:]],
                           "preserves_each_row_degree": True,
                           "integer_trace": 35, "integer_squared_trace": 175,
                           "original_polynomial_hex": hex(characteristic_polynomial(rows)),
                           "mutated_polynomial_hex": hex(characteristic_polynomial(mutated))},
            "nonsemisimple_witness": {"h": 4, "k": 2, "j": 0,
                                      "characteristic_polynomial_hex": "0x40",
                                      "odd_multiplicity": 0, "rank": 3,
                                      "square_is_zero": True}}


def certificate() -> dict[str, object]:
    pins = source_pins()
    cases = [audit_case(h, k, j) for h in range(4, 11)
             for k in range(2, min(4, h // 2) + 1) for j in range(k)]
    return {"status": "PASS_LITERAL_BINARY_SPECTRAL_AUDIT",
            "base_commit": "66849e1475c930fd7732b1a0067ffee7e1e95f60",
            "assignment_seed": 65,
            "domain": {"h": [4, 10], "k": "2 through min(4, floor(h/2))",
                       "j": "0 through k-1", "completed_cases": len(cases)},
            "maximum_order": max(case["order"] for case in cases),
            "strict_rank_gaps": sum(case["rank_gap"] > 0 for case in cases),
            "cases": cases, "source_sha256": pins,
            "controls": negative_controls(),
            "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope": "Finite audit of modular characteristic polynomials and the "
                     "associated binary rank lower bound. No all-size theorem, "
                     "supplier construction, or new kappa."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="Regenerate only this package's RESULT.json")
    arguments = parser.parse_args()
    result = certificate()
    target = PACKAGE / "RESULT.json"
    if arguments.write:
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads(target.read_text()),
                "Committed result does not match fresh exact audit")
    print(result["status"], result["domain"])


if __name__ == "__main__":
    main()
