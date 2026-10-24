"""Exact local lemma and finite corroboration for the uniform character bound."""

import hashlib
import itertools
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def checked_rows(rows):
    k = len(rows)
    need(2 <= k <= 8, "finite checker supports dimensions 2 through 8")
    need(all(type(row) is int and 0 <= row < 1 << k for row in rows),
         "invalid binary row")
    need(all(not (row >> i & 1) for i, row in enumerate(rows)),
         "character matrix must have zero diagonal")
    return k


def character(rows, fields=0):
    """Literal three-state sum, including arbitrary unary fields."""
    k = checked_rows(rows)
    need(type(fields) is int and 0 <= fields < 1 << (2 * k), "invalid field")
    total = 0
    for states in itertools.product(range(3), repeat=k):
        right = sum(1 << j for j, state in enumerate(states) if state == 2)
        parity = sum((rows[i] & right).bit_count()
                     for i, state in enumerate(states) if state == 1)
        parity += sum(fields >> (2 * i + state - 1) & 1
                      for i, state in enumerate(states) if state)
        total += 1 if parity % 2 == 0 else -1
    return total


def subset_character(rows):
    """Sum out all label-2 coordinates by exact binary orthogonality."""
    k = checked_rows(rows)
    total = 0
    for left in range(1 << k):
        xor_row = 0
        for i in range(k):
            if left >> i & 1:
                xor_row ^= rows[i]
        if xor_row & (((1 << k) - 1) ^ left) == 0:
            total += 1 << (k - left.bit_count())
    return total


def matrix(k, mask):
    edges = tuple((i, j) for i in range(k) for j in range(k) if i != j)
    need(0 <= mask < 1 << len(edges), "edge mask outside finite domain")
    rows = [0] * k
    for bit, (i, j) in enumerate(edges):
        if mask >> bit & 1:
            rows[i] |= 1 << j
    return tuple(rows)


def local_lemma():
    """Enumerate every local graph and every induced unary field."""
    summary = {}
    for k in (2, 3):
        maxima = {}
        counts = {}
        witnesses = {}
        for mask in range(1 << (k * (k - 1))):
            weight = mask.bit_count()
            if not weight:
                continue
            for fields in range(1 << (2 * k)):
                value = abs(character(matrix(k, mask), fields))
                counts[weight] = counts.get(weight, 0) + 1
                if weight not in maxima or value > maxima[weight]:
                    maxima[weight] = value
                    witnesses[weight] = [mask, fields]
        expected = {1: 7, 2: 5} if k == 2 else {
            1: 21, 2: 19, 3: 17, 4: 15, 5: 13, 6: 15}
        need(maxima == expected, "conditioned local lemma failed")
        summary[k] = {"max_abs_by_entries": maxima,
                      "field_cases_by_entries": counts,
                      "maximizers": witnesses}
    return summary


def structural_case(rows):
    """Return the exhaustive graph case used by the universal proof."""
    k = checked_rows(rows)
    edges = tuple((i, j) for i in range(k) for j in range(k)
                  if rows[i] >> j & 1)
    if len(edges) <= 1:
        return "zero" if not edges else "single"
    for i, j in edges:
        if rows[j] >> i & 1:
            return "reciprocal"
    for a in range(len(edges)):
        for b in range(a):
            if set(edges[a]) & set(edges[b]):
                return "three_vertices"
    need(len({v for edge in edges for v in edge}) == 2 * len(edges),
         "remaining graph is not a directed matching")
    return "matching"


def finite_corroboration():
    counts = {}
    for k in range(2, 5):
        classes = dict.fromkeys(
            ("zero", "single", "reciprocal", "three_vertices", "matching"), 0)
        for mask in range(1 << (k * (k - 1))):
            rows = matrix(k, mask)
            value = character(rows)
            need(value == subset_character(rows) and value >= 1 << k,
                 "positive subset identity differs from literal character")
            case = structural_case(rows)
            classes[case] += 1
            if case == "zero":
                need(value == 3 ** k, "zero character differs")
            elif case == "single":
                need(value == 7 * 3 ** (k - 2), "single-entry mode differs")
            elif k == 2:
                need(value == 5, "two-coordinate reciprocal value differs")
            else:
                need(value <= 19 * 3 ** (k - 3), "uniform remainder bound fails")
        counts[k] = classes
    return counts


def rejection_controls():
    invalid = ((0,), (1, 0), (0, -1), (False, 0), (0,) * 9)
    rejected = 0
    for rows in invalid:
        try:
            character(rows)
        except ValueError:
            rejected += 1
    need(rejected == len(invalid), "invalid-domain control was accepted")
    star = (6, 0, 0)
    need(character(star) == 19 and character(star) > 18,
         "strictly smaller remainder bound must fail")
    need(character((2, 1)) == 5 and character((2, 1)) != 7,
         "two reciprocal entries cannot be a single-entry mode")
    for k in range(3, 9):
        need(character((6,) + (0,) * (k - 1)) == 19 * 3 ** (k - 3),
             "padded sharpness example fails")
    need(49 * 27 < 19 * 81, "matching comparison fails")
    return {"invalid_domains_rejected": rejected,
            "false_strict_bound_rejected": True,
            "reciprocal_misclassification_rejected": True,
            "sharpness_dimensions": list(range(3, 9))}


def source_hashes():
    package = Path(__file__).resolve().parent
    expected = {"README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"}
    files = {path.name for path in package.iterdir() if path.is_file()}
    need(files == expected, "unexpected or missing package file")
    hashes = {}
    for name in sorted(expected):
        path = package / name
        need(path.stat().st_size <= 1024 * 1024, "package file exceeds read bound")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    result = {"status": "PASS_BINARY_CHARACTER_REMAINDER_GAP",
              "local_lemma": local_lemma(),
              "finite_characters": finite_corroboration(),
              "controls": rejection_controls(),
              "source_sha256": source_hashes(),
              "no_new_kappa": True}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
