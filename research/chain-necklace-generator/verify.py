"""Independent literal comparison and exact checks; writes only to stdout."""

import hashlib
import json
import sys
from bisect import bisect_left, bisect_right
from itertools import combinations, product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate import can_finish, domain, representatives, suffix_table


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def matrix_signature(word: tuple[int, ...]) -> tuple[int, int, int]:
    rows = [[int(i == j) for j in range(4)] for i in range(4)]
    for symbol in word:
        source, target = rows[symbol], rows[symbol + 1]
        rows[symbol + 1] = [x + y for x, y in zip(source, target)]
    return rows[2][0], rows[3][1], rows[3][0]


def canonical(word: tuple[int, ...]) -> tuple[int, ...]:
    return min(word[j:] + word[:j] for j in range(len(word)))


def literal_classes(modulus: int, target: int) -> tuple[set, dict]:
    domain(modulus, target)
    length = 3 * modulus
    classes = set()
    work = dict(literal_words=0, pair_scans=0, valid_words=0, rotation_tests=0)
    for ones in combinations(range(length), modulus):
        one_set = set(ones)
        rest = tuple(j for j in range(length) if j not in one_set)
        for twos in combinations(rest, modulus):
            work["literal_words"] += 1
            two_set = set(twos)
            threes = tuple(j for j in rest if j not in two_set)
            a = b = t = 0
            for middle in twos:
                left = bisect_left(ones, middle)
                right = modulus - bisect_right(threes, middle)
                a += left
                b += right
                t += left * right
                work["pair_scans"] += 1
            if (a % modulus, b % modulus, t % modulus) != (0, 0, target):
                continue
            word = tuple(0 if j in one_set else 1 if j in two_set else 2
                         for j in range(length))
            classes.add(canonical(word))
            work["valid_words"] += 1
            work["rotation_tests"] += length
    return classes, work


def small_suffix_checks() -> dict:
    states = queries = 0
    for modulus in range(1, 4):
        table, _ = suffix_table(modulus)
        for counts in product(range(min(2, modulus) + 1), repeat=3):
            words = (w for w in product(range(3), repeat=sum(counts))
                     if tuple(w.count(j) for j in range(3)) == counts)
            signatures = {tuple(x % modulus for x in matrix_signature(w))
                          for w in words}
            need(table[counts] == signatures, "suffix table differs from matrices")
            states += len(signatures)
        for size in range(4):
            for prefix in product(range(3), repeat=size):
                counts = tuple(prefix.count(j) for j in range(3))
                if max(counts, default=0) > modulus:
                    continue
                a, b, t = matrix_signature(prefix)
                remaining = tuple(modulus - n for n in counts)
                for target in range(modulus):
                    expected = any((a + aa + counts[0] * remaining[1]) % modulus == 0
                                   and (b + bb + counts[1] * remaining[2]) % modulus == 0
                                   and (t + tt + a * remaining[2] + counts[0] * bb)
                                   % modulus == target
                                   for aa, bb, tt in table[remaining])
                    need(can_finish(modulus, target, counts, (a, b, t), table)
                         == expected, "completion composition differs")
                    queries += 1
    return dict(suffix_states_checked=states, completion_queries=queries)


def controls() -> int:
    cases = [(0, 0), (6, 0), (True, 0), (2, -1), (2, 2), (2, True)]
    for modulus, target in cases:
        try:
            representatives(modulus, target)
        except ValueError:
            continue
        raise RuntimeError("invalid domain accepted")
    words, _ = representatives(3, 1)
    need(len(words) == 4, "periodic boundary lost")
    periods = [min(j for j in range(1, len(w) + 1)
                   if w == w[j:] + w[:j]) for w in words]
    need(sorted(periods) == [3, 3, 9, 9], "nonprimitive classes lost")
    need(canonical((2, 0, 1)) != (2, 0, 1), "noncanonical control failed")
    need(matrix_signature((0, 1, 2) * 3)[2] % 3 == 1, "cubic direction lost")
    need(matrix_signature((2, 1, 0))[2] == 0, "reversal control lost")
    return len(cases) + 5


def package_hashes() -> dict:
    names = ("README.md", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json",
             "generate.py", "verify.py", "benchmark.py")
    root = Path(__file__).resolve().parent
    need({p.name for p in root.iterdir() if p.is_file()} == set(names),
         "unexpected package inventory")
    hashes = {}
    for name in names:
        path = root / name
        need(path.stat().st_size <= 262144, "oversized package source")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main() -> None:
    cases = []
    for modulus in range(1, 6):
        for target in range(modulus):
            words, work = representatives(modulus, target)
            baseline, literal_work = literal_classes(modulus, target)
            need(len(words) == len(set(words)), "duplicate output")
            need(words == tuple(sorted(words)), "output order is not lexicographic")
            need(set(words) == baseline, "literal class mismatch")
            for word in words:
                need(word == canonical(word), "noncanonical output")
                need(tuple(word.count(j) for j in range(3)) == (modulus,) * 3,
                     "wrong content")
                need(tuple(x % modulus for x in matrix_signature(word))
                     == (0, 0, target), "literal matrix endpoint failed")
            cases.append(dict(modulus=modulus, target=target,
                              generator=work, literal=literal_work,
                              words_sha256=hashlib.sha256(bytes(x for w in words
                                                               for x in w)).hexdigest()))
    first = next(row for row in cases if (row["modulus"], row["target"]) == (5, 1))
    need(first["generator"]["outputs"] == 356, "first working example failed")
    checks = small_suffix_checks()
    checks["controls"] = controls()
    checks["cases"] = cases
    checks["files"] = package_hashes()
    print(json.dumps(checks, sort_keys=True))
    print("PASS_CHAIN_NECKLACE_GENERATOR")


if __name__ == "__main__":
    main()
