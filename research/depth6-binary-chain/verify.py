#!/usr/bin/env python3
"""Classify all shortest unsigned binary depth-six dirty-chain schedules."""

import hashlib
import json
import random
from pathlib import Path

import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
DEPTH = 6
PAIRS = tuple((i, j) for i in range(7) for j in range(i + 1, 7))
INDEX = {pair: bit for bit, pair in enumerate(PAIRS)}
STATES = 1 << len(PAIRS)
TARGET = 1 << INDEX[0, 6]
CHUNK = 1 << 18
MAX_DISTANCE = 20
FILES = ("README.md", "RESULT.json", "SOURCES.json", "TASK.json",
         "VERIFY.json", "verify.py")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def step(states: np.ndarray, letter: int) -> np.ndarray:
    """Right multiply encoded UT7 matrices by I + e_(letter,letter+1)."""
    require(0 <= letter < DEPTH, "invalid generator")
    answer = states ^ np.uint32(1 << INDEX[letter, letter + 1])
    for row in range(letter):
        source = (states >> INDEX[row, letter]) & 1
        answer ^= source << INDEX[row, letter + 1]
    return answer


def matrix_step(state: int, letter: int) -> int:
    """Independent full 7-by-7 binary matrix multiplication oracle."""
    acc = [[int(i == j) for j in range(7)] for i in range(7)]
    for bit, (i, j) in enumerate(PAIRS):
        acc[i][j] = (state >> bit) & 1
    gen = [[int(i == j) for j in range(7)] for i in range(7)]
    gen[letter][letter + 1] = 1
    product = [[sum(acc[i][k] * gen[k][j] for k in range(7)) % 2
                for j in range(7)] for i in range(7)]
    return sum(product[i][j] << bit for bit, (i, j) in enumerate(PAIRS))


def check_generators() -> int:
    # Both formulas are affine over F2. Zero and every basis vector determine
    # each entire map, including its constant term, on all 2^21 states.
    samples = np.array([0] + [1 << bit for bit in range(21)], dtype=np.uint32)
    checked = 0
    for letter in range(DEPTH):
        actual = step(samples, letter)
        expected = np.array([matrix_step(int(s), letter) for s in samples],
                            dtype=np.uint32)
        require(np.array_equal(actual, expected), "generator oracle mismatch")
        require(np.array_equal(step(actual, letter), samples), "not involutive")
        checked += len(samples)
    return checked


def shortest_schedules() -> dict:
    """Complete BFS with exact geodesic counts, followed by path enumeration."""
    require(DEPTH ** MAX_DISTANCE < np.iinfo(np.uint64).max, "path-count overflow")
    seen = np.full(STATES, 255, dtype=np.uint8)
    ways = np.zeros(STATES, dtype=np.uint64)
    current = np.empty(STATES, dtype=np.uint32)
    following = np.empty(STATES, dtype=np.uint32)
    seen[0], current[0], ways[0] = 0, 0, 1
    count, layers, distance = 1, [1], None
    for level in range(1, MAX_DISTANCE + 1):
        size = 0
        for letter in range(DEPTH):
            for start in range(0, count, CHUNK):
                part = current[start:min(start + CHUNK, count)]
                candidates = step(part, letter)
                eligible = (seen[candidates] == 255) | (seen[candidates] == level)
                # Distinct sources have distinct images under this bijection.
                # Current-layer counts are final before the next layer starts.
                ways[candidates[eligible]] += ways[part[eligible]]
                fresh = candidates[seen[candidates] == 255]
                end = size + len(fresh)
                require(end <= STATES, "frontier capacity exhausted")
                # Each generator is a bijection, so this chunk has no repeats.
                # Mark immediately to deduplicate subsequent generators/chunks.
                seen[fresh] = level
                following[size:end] = fresh
                size = end
        layers.append(size)
        current, following, count = following, current, size
        if seen[TARGET] != 255:
            distance = int(seen[TARGET])
            break
        require(count > 0, "target unreachable")
    require(distance is not None, "target absent within declared distance bound")
    total = int(ways[TARGET])
    require(0 < total <= 100, "geodesic enumeration capacity exceeded")
    words = enumerate_schedules(seen, distance, total)
    require(sum(layers) == int(np.count_nonzero(seen != 255)), "layer partition")
    return {"distance": distance, "layers": layers,
            "shortest_word_count": total, "words": words}


def enumerate_schedules(seen: np.ndarray, distance: int, total: int) -> list:
    """Enumerate every decreasing-distance path using full matrix products."""
    paths = [(TARGET, "")]
    for level in range(distance, 0, -1):
        following = []
        for state, suffix in paths:
            for letter in range(DEPTH):
                previous = matrix_step(state, letter)
                if int(seen[previous]) == level - 1:
                    following.append((previous, str(letter + 1) + suffix))
                    require(len(following) <= total, "too many predecessor paths")
        paths = following
    require(len(paths) == total, "path count disagrees with forward counting")
    require(all(state == 0 for state, _ in paths), "path misses identity")
    words = sorted(suffix for _, suffix in paths)
    require(len(set(words)) == total, "duplicate labelled path")
    return words


def interval_signature(word: str) -> tuple:
    """Integer scattered-subword counts, reduced only at the end."""
    require(len(word) <= MAX_DISTANCE, "word exceeds replay bound")
    require(all(letter in "123456" for letter in word), "invalid word")
    counts = {(i, j): 0 for i in range(1, 7) for j in range(i, 7)}
    for event in word:
        letter = int(event)
        for first in range(1, letter + 1):
            counts[first, letter] += 1 if first == letter else counts[first, letter - 1]
    return tuple(counts[i + 1, j] % 2 for i, j in PAIRS)


def correct(word: str) -> bool:
    return interval_signature(word) == tuple(int(pair == (0, 6)) for pair in PAIRS)


def matvec(matrix: tuple, vector: tuple) -> tuple:
    return tuple(sum(matrix[i][j] * vector[j] for j in range(2)) % 2
                 for i in range(2))


def replay(word: str, maps: tuple, initial: tuple) -> bool:
    registers = list(initial)
    for event in word:
        letter = int(event)
        gain = matvec(maps[letter - 1], registers[letter - 1])
        registers[letter] = tuple(a ^ b for a, b in zip(registers[letter], gain))
    gain = initial[0]
    for matrix in maps:
        gain = matvec(matrix, gain)
    wanted = tuple(a ^ b for a, b in zip(initial[6], gain))
    return tuple(registers[:6]) == initial[:6] and registers[6] == wanted


def dirty_checks(word: str) -> tuple:
    scalar_cases = 0
    for map_mask in range(64):
        for initial_mask in range(128):
            initial = [(initial_mask >> i) & 1 for i in range(7)]
            registers = initial[:]
            for event in word:
                letter = int(event)
                registers[letter] ^= ((map_mask >> (letter - 1)) & 1) * registers[letter - 1]
            wanted = initial[6] ^ (int(map_mask == 63) * initial[0])
            require(registers[:6] == initial[:6] and registers[6] == wanted,
                    "scalar dirty replay")
            scalar_cases += 1
    rng = random.Random(1022)
    swap, projection = ((0, 1), (1, 0)), ((1, 0), (0, 0))
    families = [(swap, projection) * 3, (((0, 0), (0, 0)),) * 6]
    for _ in range(62):
        families.append(tuple(tuple(tuple(rng.randrange(2) for _ in range(2))
                                    for _ in range(2)) for _ in range(6)))
    matrix_cases = 0
    for maps in families:
        for basis in range(14):
            initial = tuple(tuple(int(2 * row + column == basis) for column in range(2))
                            for row in range(7))
            require(replay(word, maps, initial), "noncommuting dirty replay")
            matrix_cases += 1
    return scalar_cases, matrix_cases


def controls(word: str) -> int:
    mutants = [word[:-1], word[1:], word[:-1] + "2", "123456",
               word[:3] + word[4] + word[3] + word[5:]]
    require(all(not correct(mutant) for mutant in mutants), "invalid-word control")
    try:
        interval_signature(word[:-1] + "7")
    except ValueError as error:
        require(str(error) == "invalid word", "wrong rejection reason")
    else:
        raise ValueError("unknown generator accepted")
    return len(mutants) + 1


def source_hashes() -> dict:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    require(len(sources["files"]) == 4, "source inventory size")
    hashes = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "source input changed: " + row["path"])
            hashes[row["path"]] = digest
    return hashes


def main() -> None:
    hashes = source_hashes()
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    require(expected["schema_version"] == 1, "result schema")
    oracle_cases = check_generators()
    actual = shortest_schedules()
    require(actual == expected["bfs"], "BFS result differs from committed certificate")
    base = "1234565432" * 2
    rotations = sorted({base[i:] + base[:i] for i in range(len(base))})
    require(actual["words"] == rotations, "not precisely the ten cyclic rotations")
    scalar_cases, matrix_cases = 0, 0
    for word in actual["words"]:
        require(correct(word), "chronological interval identity")
        require([word.count(str(i)) for i in range(1, 7)] == [2, 4, 4, 4, 4, 2],
                "unexpected minimal count vector")
        require(all(abs(int(a) - int(b)) == 1 for a, b in zip(word, word[1:])),
                "commuting neighbors in a shortest word")
        state = 0
        for event in word:
            state = matrix_step(state, int(event) - 1)
        require(state == TARGET, "full matrix word product")
        scalar, matrix = dirty_checks(word)
        scalar_cases += scalar
        matrix_cases += matrix
    rejected = controls("23456543212345654321")
    for filename in FILES:
        hashes[str((PACKAGE / filename).relative_to(ROOT))] = hashlib.sha256(
            (PACKAGE / filename).read_bytes()).hexdigest()
    receipt = {"result": actual, "generator_oracle_cases": oracle_cases,
               "scalar_dirty_cases": scalar_cases, "matrix_dirty_cases": matrix_cases,
               "rejected_controls": rejected, "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_DEPTH6_BINARY_CHAIN shortest_words=10 rotation_classes=1 distance=20 "
          "oracle=132 scalar=81920 matrix=8960 controls=6")


if __name__ == "__main__":
    main()
