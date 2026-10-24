#!/usr/bin/env python3
"""Check the new two-short-row obstruction and its characteristic-8t family.

The all-modulus statements are proved in README.md. This bounded replay checks
the arithmetic relaxation and new words, without importing predecessor code.
"""
import hashlib
import json
import math
import random
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAX_T = 64
MAX_MODULUS = 96
FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
INPUTS = ("research/depth3-chain-connector/README.md",
          "research/depth4-chain-rowmodel/README.md",
          "research/universal-connector-boundary/README.md")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def family(t: int) -> tuple[int, list[int], list[int], list[int]]:
    require(type(t) is int and 1 <= t <= MAX_T, "t outside replay domain")
    m = 8 * t
    rows = [m, 6 * t, 2 * t] + [0] * (m - 3)
    rho = [m - 4, 4, 0] + [0] * (m - 3)
    beta = [v for v in (5, 4, 2, 2, 1, 1, 1, 0) for _ in range(t)]
    return m, rows, rho, beta


def row_conditions(m: int, rows: list[int], rho: list[int],
                   beta: list[int]) -> tuple[tuple[int, ...], int]:
    require(2 <= m <= 8 * MAX_T, "modulus outside replay domain")
    for profile in (rows, rho, beta):
        require(len(profile) == m, "profile length")
        require(all(type(v) is int and 0 <= v <= m for v in profile), "profile range")
        require(all(profile[i] >= profile[i + 1] for i in range(m - 1)), "profile order")
    cumulative = [0] * (m + 1)
    for i in range(m):
        cumulative[i + 1] = cumulative[i] + beta[i]
    vanish = (sum(rows), sum(rho), sum(beta),
              sum(r * length for r, length in zip(rho, rows)),
              sum(cumulative[length] for length in rows))
    coefficient = -sum(r * cumulative[length] for r, length in zip(rho, rows)) % m
    return tuple(v % m for v in vanish), coefficient


def build_word(m: int, rows: list[int], rho: list[int], beta: list[int]) -> list[int]:
    """Place calls at the levels in #4280's row-model definitions."""
    ones = [0] * (m + 1)
    fours = [0] * (m + 1)
    for q in range(1, m + 1):
        following = rho[q] if q < m else 0
        ones[m - q] = rho[q - 1] - following
        following_beta = beta[q] if q < m else 0
        fours[q] = beta[q - 1] - following_beta
    ones[m] = m - rho[0]
    fours[0] = m - beta[0]
    word = [1] * ones[0] + [4] * fours[0]
    previous_twos = 0
    for p in range(1, m + 1):
        twos = m - sum(length >= p for length in rows)
        for level in range(previous_twos + 1, twos + 1):
            word.extend([2] + [1] * ones[level])
        word.extend([3] + [4] * fours[p])
        previous_twos = twos
    for level in range(previous_twos + 1, m + 1):
        word.extend([2] + [1] * ones[level])
    require(len(word) == 4 * m, "decoded word budget")
    return word


def interval_counts(word: list[int], m: int) -> dict[tuple[int, int], int]:
    require(len(word) <= 4 * m + 1, "word exceeds replay capacity")
    count = {(i, j): 0 for i in range(1, 5) for j in range(i, 5)}
    for letter in word:
        require(type(letter) is int and 1 <= letter <= 4, "unknown call")
        for start in range(1, letter + 1):
            gain = 1 if start == letter else count[start, letter - 1]
            count[start, letter] = (count[start, letter] + gain) % m
    return count


def correct_word(word: list[int], m: int, c: int) -> bool:
    count = interval_counts(word, m)
    return (len(word) == 4 * m and all(word.count(i) == m for i in range(1, 5))
            and all(value == (c if key == (1, 4) else 0)
                    for key, value in count.items()))


def check_matrix(word: list[int], m: int, c: int) -> None:
    """Right multiply upper-unitriangular matrices, separately from counts."""
    product = [[int(i == j) for j in range(5)] for i in range(5)]
    for letter in word:
        for i in range(5):
            product[i][letter] = (product[i][letter] + product[i][letter - 1]) % m
    expected = [[int(i == j) for j in range(5)] for i in range(5)]
    expected[0][4] = c
    require(product == expected, "UT5 product")


def apply(matrix: list[list[int]], vector: list[int], m: int) -> list[int]:
    return [sum(matrix[i][j] * vector[j] for j in range(2)) % m for i in range(2)]


def check_dirty(word: list[int], m: int, c: int, rng: random.Random) -> None:
    """Literal calls on arbitrary dirty vectors with noncommuting maps."""
    maps = [[[1, 1], [0, 1]], [[1, 0], [1, 1]]]
    maps.extend([[[rng.randrange(m) for _ in range(2)] for _ in range(2)]
                 for _ in range(2)])
    initial = [[rng.randrange(m) for _ in range(2)] for _ in range(5)]
    state = [v.copy() for v in initial]
    for letter in word:
        gain = apply(maps[letter - 1], state[letter - 1], m)
        state[letter] = [(state[letter][i] + gain[i]) % m for i in range(2)]
    composed = initial[0]
    for matrix in maps:
        composed = apply(matrix, composed, m)
    expected_y = [(initial[4][i] + c * composed[i]) % m for i in range(2)]
    require(state[:4] == initial[:4], "dirty intermediates not restored")
    require(state[4] == expected_y, "literal target gain")


def check_annihilator() -> tuple[int, int]:
    """Exhaust the necessary two-row algebra, relaxing profile realizability."""
    cases = 0
    nonzero = 0
    for m in range(2, MAX_MODULUS + 1):
        for length in range((m + 1) // 2, m):
            for delta in range(m):
                if delta * length % m:
                    continue
                for prefix_sum in range(m):
                    c = -delta * prefix_sum % m
                    require(c * length % m == 0, "short-row annihilator")
                    require(length % (m // math.gcd(m, c)) == 0, "divisibility form")
                    if c:
                        require(math.gcd(c, m) > 1, "unit escaped two-row obstruction")
                        nonzero += 1
                    cases += 1
    require(nonzero > 0, "composite relaxation must remain nonempty")
    return cases, nonzero


def check_controls() -> int:
    m, rows, rho, beta = family(1)
    word = build_word(m, rows, rho, beta)
    require(not correct_word(word, m, 1), "wrong coefficient accepted")
    require(not correct_word(word[:-1], m, 4), "dropped call accepted")
    require(not correct_word(word + [1], m, 4), "extra call accepted")
    changed_rho = rho.copy()
    changed_rho[1] -= 1
    vanish, _ = row_conditions(m, rows, changed_rho, beta)
    require(any(vanish), "changed rho passed row conditions")
    swaps_rejected = 0
    for i in range(len(word) - 1):
        changed = word.copy()
        changed[i], changed[i + 1] = changed[i + 1], changed[i]
        swaps_rejected += not correct_word(changed, m, 4)
    require(swaps_rejected > 0, "chronology control did not detect any swap")
    return 4 + swaps_rejected


def receipt() -> dict[str, dict[str, str]]:
    source_path = PACKAGE / "SOURCES.json"
    require(source_path.stat().st_size <= 65536, "source manifest capacity")
    sources = json.loads(source_path.read_text(encoding="utf-8"))
    rows = sources["files"]
    require(len(rows) == 5, "source inventory size")
    live = {row["path"]: row["sha256"] for row in rows if row["usage"] == "input"}
    require(set(live) == set(INPUTS), "live input inventory")
    inputs = {}
    for name in INPUTS:
        digest = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        require(digest == live[name], "source mismatch: " + name)
        inputs[name] = digest
    package = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() for name in FILES}
    return {"package_sha256": package, "input_sha256": inputs}


def main() -> None:
    hashes = receipt()
    rng = random.Random(4280)
    for t in range(1, MAX_T + 1):
        m, rows, rho, beta = family(t)
        c = 4 * t
        vanish, actual_c = row_conditions(m, rows, rho, beta)
        require(not any(vanish) and actual_c == c, "family row congruences")
        require(sum(0 < length < m for length in rows) == 2, "short-row count")
        word = build_word(m, rows, rho, beta)
        require(correct_word(word, m, c), "chronological interval counts")
        check_matrix(word, m, c)
        for _ in range(2):
            check_dirty(word, m, c, rng)
    cases, nonzero = check_annihilator()
    controls = check_controls()
    print(json.dumps({**hashes, "family_cases": MAX_T, "dirty_replays": 2 * MAX_T,
                      "algebra_cases": cases, "nonzero_algebra_cases": nonzero,
                      "rejection_controls": controls}, sort_keys=True))
    print(f"PASS_DEPTH4_TWO_ROW_OBSTRUCTION family_cases={MAX_T} "
          f"algebra_cases={cases} controls={controls}")


if __name__ == "__main__":
    main()
