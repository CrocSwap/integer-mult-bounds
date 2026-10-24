#!/usr/bin/env python3
"""Check the new 22-call witnesses, without replaying the cited lower bound."""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


PACKAGE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
WORD = tuple(int(x) for x in "1234656564321234565432")
RETIME = WORD[:3] + (6, 4) + WORD[5:]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_word(word: tuple[int, ...]) -> None:
    require(1 <= len(word) <= 22, "word length outside the fixed certificate")
    require(all(type(x) is int and 1 <= x <= 6 for x in word), "unknown call")


def interval_counts(word: tuple[int, ...]) -> tuple[int, ...]:
    """Integer scattered-subword counts for all 21 increasing intervals."""
    validate_word(word)
    answer = []
    for start in range(1, 7):
        counts = [0] * 7
        counts[start - 1] = 1
        for letter in word:
            if letter >= start:
                counts[letter] += counts[letter - 1]
        answer.extend(counts[start:])
    return tuple(answer)


def endpoint(word: tuple[int, ...], modulus: int = 2) -> tuple[tuple[int, ...], ...]:
    validate_word(word)
    require(modulus in (2, 3), "unsupported scalar control modulus")
    rows = [[int(i == j) for j in range(7)] for i in range(7)]
    for letter in word:
        rows[letter] = [(x + y) % modulus
                        for x, y in zip(rows[letter], rows[letter - 1])]
    return tuple(tuple(row) for row in rows)


def correct(word: tuple[int, ...]) -> bool:
    target = tuple(tuple(int(i == j) ^ int(i == 6 and j == 0)
                         for j in range(7)) for i in range(7))
    counts = interval_counts(word)
    expected = tuple(int(i == 1 and j == 6)
                     for i in range(1, 7) for j in range(i, 7))
    return tuple(x % 2 for x in counts) == expected and endpoint(word) == target


def blocked_pairs(word: tuple[int, ...]) -> tuple[tuple[int, int, int], ...]:
    """Return one noncommuting blocker for each consecutive equal-call pair."""
    validate_word(word)
    certificate = []
    for letter in range(1, 7):
        positions = [i for i, x in enumerate(word) if x == letter]
        for left, right in zip(positions, positions[1:]):
            blockers = [i for i in range(left + 1, right)
                        if abs(word[i] - letter) == 1]
            require(bool(blockers), "commuting moves can expose an equal-call pair")
            certificate.append((left, right, blockers[0]))
    return tuple(certificate)


def action(word: tuple[int, ...], maps: tuple[int, ...],
           initial: tuple[int, ...], dimension: int) -> tuple[int, ...]:
    """Literal dirty-register replay using bit-encoded linear maps."""
    validate_word(word)
    require(dimension in (1, 2), "unsupported replay dimension")
    limit = 1 << dimension
    require(len(maps) == 6 and all(0 <= x < limit ** dimension for x in maps),
            "invalid map tuple")
    require(len(initial) == 7 and all(0 <= x < limit for x in initial),
            "invalid initial tuple")
    values = list(initial)
    for letter in word:
        values[letter] ^= apply_map(maps[letter - 1], values[letter - 1], dimension)
    return tuple(values)


def apply_map(matrix: int, value: int, dimension: int) -> int:
    output = 0
    for row in range(dimension):
        bits = (matrix >> (row * dimension)) & ((1 << dimension) - 1)
        output |= ((bits & value).bit_count() % 2) << row
    return output


def expected_action(maps: tuple[int, ...], initial: tuple[int, ...],
                    dimension: int) -> tuple[int, ...]:
    value = initial[0]
    for matrix in maps:
        value = apply_map(matrix, value, dimension)
    return initial[:6] + (initial[6] ^ value,)


def replay_cases() -> tuple[int, int]:
    scalar_count = matrix_count = 0
    for maps in product(range(2), repeat=6):
        for initial in product(range(2), repeat=7):
            expected = expected_action(maps, initial, 1)
            for word in (WORD, RETIME):
                require(action(word, maps, initial, 1) == expected, "scalar replay")
                scalar_count += 1
    for seed in range(64):
        maps = tuple((seed * (2 * i + 1) + i * i + 3 * (seed >> 2)) % 16
                     for i in range(6))
        for coordinate in range(14):
            initial = tuple((1 << (coordinate % 2)) if i == coordinate // 2 else 0
                            for i in range(7))
            expected = expected_action(maps, initial, 2)
            for word in (WORD, RETIME):
                require(action(word, maps, initial, 2) == expected, "matrix replay")
                matrix_count += 1
    return scalar_count, matrix_count


def local_relation() -> int:
    comparisons = 0
    for first, second in product(range(16), repeat=2):
        maps = (0, 0, 0, 0, first, second)
        for coordinate in range(6):
            initial = tuple((1 << (coordinate % 2)) if i == 4 + coordinate // 2 else 0
                            for i in range(7))
            require(action((5, 6, 5), maps, initial, 2)
                    == action((6, 5, 6, 5, 6), maps, initial, 2), "local relation")
            comparisons += 1
    return comparisons


def controls() -> int:
    count = 0
    for bad in (WORD[:-1], WORD[1:], tuple(range(1, 7)),
                WORD[:4] + (5,) + WORD[5:]):
        require(not correct(bad), "bad endpoint was accepted")
        count += 1
    redundant = (6, 1, 6) + tuple(int(x) for x in "2345654321234565432")
    require(correct(redundant), "redundancy control must have the right endpoint")
    for word in (redundant, (1, 1), (1, 3, 1)):
        try:
            blocked_pairs(word)
        except ValueError:
            count += 1
        else:
            raise ValueError("reducible word was accepted")
    try:
        validate_word((0,))
    except ValueError:
        count += 1
    else:
        raise ValueError("unknown call was accepted")
    require(endpoint(WORD, 3) != endpoint(RETIME, 2), "odd-characteristic control")
    require(endpoint((5, 6, 5), 3) != endpoint((6, 5, 6, 5, 6), 3),
            "local relation was wrongly extended to characteristic three")
    return count + 2


def receipt() -> dict[str, str]:
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in PACKAGE_FILES:
        path = package / name
        require(path.is_file() and not path.is_symlink(), "invalid package file")
        require(path.stat().st_size <= 1024 * 1024, "oversized package file")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return hashes


def main() -> None:
    require(len(WORD) == len(RETIME) == 22 and WORD != RETIME, "witness shape")
    require(abs(WORD[3] - WORD[4]) > 1, "retimed calls must commute")
    require(correct(WORD) and correct(RETIME), "incorrect witness")
    certificates = [blocked_pairs(word) for word in (WORD, RETIME)]
    require(all(len(c) == 16 for c in certificates), "blocker coverage")
    scalar, matrix = replay_cases()
    relation = local_relation()
    negative = controls()
    print(json.dumps({"schema": "depth6-chain-retiming/v1", "python": sys.version,
                      "words": ["".join(map(str, w)) for w in (WORD, RETIME)],
                      "counts": [interval_counts(w) for w in (WORD, RETIME)],
                      "blockers": certificates, "package_sha256": receipt()}, sort_keys=True))
    print(f"PASS_DEPTH6_CHAIN_RETIMING calls=22 extra=2 blockers=32 "
          f"scalar={scalar} matrix={matrix} relation={relation} controls={negative}")


if __name__ == "__main__":
    main()
