"""Exact consecutive cancellation batches, produced by Nick Petalas.

Apache-2.0. The scalar cancellation interface is credited to woklerx/1853.
No predecessor executable is imported or replayed.
"""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceiling(value):
    return -(-value.numerator // value.denominator)


def analyze(coefficient, offset, gap):
    """Return the constant-size run census; integers denote coarse-grid units."""
    need(type(coefficient) is Fraction and type(offset) is Fraction,
         "Exact rational coefficient and offset required")
    need(type(gap) is int and 1 <= gap <= 256, "Gap must be an integer in 1..256")
    for value in (coefficient, offset):
        need(max(abs(value.numerator).bit_length(), value.denominator.bit_length()) <= 4096,
             "Rational input exceeds the 4096-bit reference limit")
    a, d = coefficient.numerator, coefficient.denominator
    whole = (d * offset) // 1
    theta = d * offset - whole
    radius = Fraction(d, 1 << (gap + 1))
    low, high = ceiling(-radius - theta), ceiling(radius - theta) - 1
    size = high - low + 1
    step = a - d * ((coefficient + Fraction(1, 2)) // 1)
    need(0 <= size <= d and (step != 0 or d == 1), "Residue and step invariants")
    if d == 1:
        return dict(period=1, safe=size, step=0, runs=[],
                    maximum=None if size else 0, start=0 if size else None)
    speed = abs(step)
    quotient, remainder = divmod(size, speed)
    runs = []
    if quotient and speed > remainder:
        runs.append([quotient, speed - remainder])
    if remainder:
        runs.append([quotient + 1, remainder])
    start = None
    if size:
        endpoint = low if step > 0 else high
        start = ((endpoint - whole) * pow(a, -1, d)) % d
    need(sum(length * count for length, count in runs) == size, "Run mass invariant")
    return dict(period=d, safe=size, step=step, runs=runs,
                maximum=(size + speed - 1) // speed, start=start)


def batch_count(record, length):
    need(type(length) is int and 1 <= length <= (1 << 4096),
         "Batch length must be a positive integer of at most 4097 bits")
    if record["period"] == 1:
        return record["safe"]
    return max(0, record["safe"] - (length - 1) * abs(record["step"]))


def rounded(value, bits):
    scale = 1 << bits
    return Fraction((scale * value + Fraction(1, 2)) // 1, scale)


def literal_period(coefficient, offset, gap):
    """Use literal Fraction rounding, with no residue or centered-step formula."""
    d = coefficient.denominator
    need(d <= 32, "Literal oracle is bounded to periods at most 32")
    return tuple(rounded(offset + coefficient * k, 0) ==
                 rounded(offset + coefficient * k, gap) for k in range(d))


def literal_runs(safe):
    d = len(safe)
    counts = Counter()
    if all(safe):
        need(d == 1, "A noninteger orbit cannot be entirely safe")
        return []
    for k in range(d):
        if safe[k] and not safe[(k - 1) % d]:
            length = 0
            for j in range(d):
                if not safe[(k + j) % d]:
                    break
                length += 1
            need(length < d, "Finite cyclic run must end")
            counts[length] += 1
    return [list(pair) for pair in sorted(counts.items())]


def check_case(coefficient, offset, gap, counts):
    record = analyze(coefficient, offset, gap)
    safe = literal_period(coefficient, offset, gap)
    counts["cases"] += 1
    counts["literal_points"] += len(safe)
    need(record["safe"] == sum(safe), "Literal safe count")
    runs = literal_runs(safe)
    need(record["runs"] == runs, "Complete literal cyclic run census")
    counts["runs"] += sum(count for _, count in runs)
    expected_maximum = None if all(safe) else max((n for n, _ in runs), default=0)
    need(record["maximum"] == expected_maximum, "Sharp maximum batch length")
    if record["maximum"]:
        start, length = record["start"], record["maximum"]
        need(not safe[(start - 1) % len(safe)] and
             not safe[(start + length) % len(safe)], "Attaining run boundaries")
        need(all(safe[(start + j) % len(safe)] for j in range(length)), "Attaining run")
        counts["attainers"] += 1
    for length in range(1, len(safe) + 2):
        actual = 0
        for k in range(len(safe)):
            actual += all(safe[(k + j) % len(safe)] for j in range(length))
        need(batch_count(record, length) == actual, "All-start batch count")
        counts["batch_counts"] += 1


def small_cases():
    counts = Counter()
    for d in range(2, 25):
        offsets = (Fraction(0), Fraction(1, 3), Fraction(-3, 8),
                   Fraction(1, 2 * d), Fraction(1, 4 * d))
        for a in range(-d, d + 1):
            if gcd(a, d) == 1:
                for offset in offsets:
                    for gap in range(1, 5):
                        check_case(Fraction(a, d), offset, gap, counts)
    for a in range(-3, 4):
        for c in range(-8, 9):
            for gap in range(1, 5):
                check_case(Fraction(a), Fraction(c, 8), gap, counts)
    return dict(sorted(counts.items()))


def dirty_updates():
    counts = Counter()
    for a in range(-4, 5):
        for k in range(-5, 6):
            for dirt in (Fraction(-7, 3), Fraction(0), Fraction(11, 8)):
                for p, w, gap in ((0, 0, 1), (1, 3, 2), (3, 2, 3)):
                    source = Fraction(k, 1 << p)
                    coefficient, offset = Fraction(a, 7), Fraction(3, 16)
                    value = offset + coefficient * source
                    coarse, fine = rounded(value, w), rounded(value, w + gap)
                    after = dirt + coarse - fine
                    scaled_a = coefficient * Fraction(1 << w, 1 << p)
                    record = analyze(scaled_a, offset * (1 << w), gap)
                    period = literal_period(scaled_a, offset * (1 << w), gap)
                    need((after == dirt) == period[k % len(period)], "Arbitrary dirty restoration")
                    need((coarse == fine) == period[k % len(period)], "Physical-grid rescaling")
                    need(batch_count(record, 1) == sum(period), "Rescaled batch frequency")
                    counts["dirty_grid_checks"] += 1
    return dict(counts)


def large_cases():
    rows = []
    for d, a, gap in ((1000, 1, 2), ((1 << 100) + 1, 1, 3),
                      ((1 << 256) + 1, -1, 8), ((1 << 128) + 1, 17, 4)):
        coefficient = Fraction(a, d)
        result = analyze(coefficient, Fraction(0), gap)
        start, length = result["start"], result["maximum"]
        need(length > 0, "Large fixture is nonempty")
        for delta, expected in ((-1, False), (0, True), (length - 1, True), (length, False)):
            value = coefficient * (start + delta)
            need((rounded(value, 0) == rounded(value, gap)) == expected,
                 "Exact large-fixture endpoint")
        need(batch_count(result, length) > 0 and batch_count(result, length + 1) == 0,
             "Sharp large-fixture batch boundary")
        rows.append(dict(coefficient=str(coefficient), gap=gap, **result))
    need(rows[0]["maximum"] == 250 and rows[1]["maximum"] == (1 << 97) + 1,
         "Displayed batch lengths")
    return rows


def expect_rejection(action):
    try:
        action()
    except ValueError:
        return 1
    raise ValueError("An invalid input was accepted")


def controls():
    count = 0
    for coefficient, offset, gap in ((0.125, Fraction(0), 2),
                                     (Fraction(1, 8), 0.0, 2),
                                     (Fraction(1, 8), Fraction(0), 0),
                                     (Fraction(1, 8), Fraction(0), True),
                                     (Fraction(1, 8), Fraction(0), 257),
                                     (Fraction(1 << 4096), Fraction(0), 1)):
        count += expect_rejection(lambda: analyze(coefficient, offset, gap))
    record = analyze(Fraction(1, 8), Fraction(0), 2)
    for length in (0, -1, True, 1.5, (1 << 4096) + 1):
        count += expect_rejection(lambda: batch_count(record, length))
    need(rounded(Fraction(-1, 8), 0) == rounded(Fraction(-1, 8), 2) and
         rounded(Fraction(1, 8), 0) != rounded(Fraction(1, 8), 2), "Asymmetric ties")
    count += 1
    need(analyze(Fraction(1, 2), Fraction(1, 4), 2)["safe"] == 0,
         "Offset can remove the complete safe set")
    count += 1
    need(analyze(Fraction(3, 8), Fraction(0), 1)["runs"] == [[1, 2], [2, 1]],
         "Remainder creates two positive run lengths")
    count += 1
    need(analyze(Fraction(7, 8), Fraction(0), 2)["maximum"] == 2,
         "Centered step, rather than raw numerator")
    count += 1
    return count


def source_hashes():
    root = HERE.parents[1]
    sources = json.loads((HERE / "SOURCES.json").read_text())
    pins = [row for row in sources["files"] if row["usage"] == "input"]
    need(len(pins) == 1, "One retained predecessor text input")
    hashes = {}
    for row in pins:
        path = root / row["path"]
        need(path.is_file() and not path.is_symlink(), "Regular source input")
        data = path.read_bytes()
        need(len(data) <= 65536, "Bounded predecessor text")
        digest = sha256(data).hexdigest()
        need(digest == row["sha256"], "Retained predecessor text SHA256")
        hashes[row["path"]] = digest
    for name in FILES:
        path = HERE / name
        need(path.is_file() and not path.is_symlink(), "Regular package file")
        data = path.read_bytes()
        need(len(data) <= 131072, "Bounded package source")
        hashes[name] = sha256(data).hexdigest()
    return hashes


def main():
    need(len(sys.argv) == 1, "This fixed verifier accepts no arguments")
    hashes = source_hashes()
    receipt = dict(status="PASS_CANCELLATION_SAFE_BATCHES", small=small_cases(),
                   dirty=dirty_updates(), large=large_cases(), controls=controls(),
                   source_sha256=hashes)
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
