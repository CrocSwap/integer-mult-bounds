#!/usr/bin/env python3
"""Full native cost exclusions and independent Python all-transfer incidence bound.

Native receipt binding alone is explicitly not a fresh native exclusion replay.
conorholds with substantial Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from math import comb, factorial
from pathlib import Path
import subprocess
import tempfile
from time import monotonic

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def pair_words(n):
    count = [0] * n; word = []
    def visit(opened):
        if len(word) == 2 * n:
            yield tuple(word); return
        for label in range(min(opened + 1, n)):
            if count[label] < 2:
                count[label] += 1; word.append(label)
                yield from visit(max(opened, label + 1))
                word.pop(); count[label] -= 1
    yield from visit(0)


def difference_set(word):
    prefix = 0; points = {0}
    for label in word:
        prefix ^= 1 << label; points.add(prefix)
    return {a ^ b for a in points for b in points}


def matching_words(n):
    """Separate least-unmatched perfect-matching enumeration."""
    word = [-1] * (2 * n)
    def visit(label):
        if label == n:
            yield tuple(word); return
        first = word.index(-1)
        for second in range(first + 1, 2 * n):
            if word[second] == -1:
                word[first] = word[second] = label
                yield from visit(label + 1)
                word[first] = word[second] = -1
    yield from visit(0)


def walsh_cover(word, n):
    size = 1 << n; a = [0] * size; prefix = 0; a[0] = 1
    for label in word:
        prefix ^= 1 << label; a[prefix] = 1
    def transform(a):
        step = 1
        while step < len(a):
            for start in range(0, len(a), 2 * step):
                for j in range(start, start + step):
                    x, y = a[j], a[j + step]; a[j], a[j + step] = x + y, x - y
            step *= 2
    transform(a); a = [x * x for x in a]; transform(a)
    require(all(x >= 0 and x % size == 0 for x in a), "invalid exact autocorrelation")
    return {i for i, x in enumerate(a) if x > 0}


def ideal_census(n):
    # All three normalized directions cannot cover a mask meeting every color.
    # Two colors see D(w), its projection on one color, and the complementary projection.
    primary = {word: difference_set(word) for word in pair_words(n)}
    independent = {word: walsh_cover(word, n) for word in matching_words(n)}
    require(primary == independent, "set/matching/Walsh census disagreement")
    require(len(primary) == factorial(2*n) // (2**n * factorial(n)), "incomplete source pairings")
    full = (1 << n) - 1; histogram = Counter(); universal = 0
    for word, differences in primary.items():
        for group in range(1, full):
            if not group & 1:
                continue  # unordered complementary color classes
            other = full ^ group
            cover = differences | {mask & group for mask in differences} | {mask & other for mask in differences}
            histogram[len(cover)] += 1
            universal += int(len(cover) == (1 << n))
    return {"sources": n, "words": len(primary), "partitions": sum(histogram.values()),
            "max_coverage": max(histogram), "universal": universal,
            "histogram": {str(k): histogram[k] for k in sorted(histogram)}}


def native_core(row):
    return {k: row[k] for k in ("transfers", "triple", "words", "placements", "assignments", "universal", "three_readout", "histogram", "controls")}


def check_native_domains(rows):
    require([(r["transfers"], r["triple"]) for r in rows] == [(4, False), (2, False), (2, True)], "native domain missing")
    for row in rows:
        expected_words = 17325 if row["triple"] else 945
        length = 11 if row["triple"] else 10
        direction_words = 6 if row["transfers"] == 4 else 2
        require(row["words"] == expected_words, "canonical source domain mismatch")
        require(row["placements"] == expected_words * direction_words * comb(length + row["transfers"], row["transfers"]), "incomplete interleavings")
        require(sum(row["histogram"]) == row["assignments"] and row["histogram"][32] == 0,
                "native histogram or exhaustive exclusion mismatch")
        require(row["universal"] == row["three_readout"] == 0 and row["controls"] == 3, "exclusion or positive/failure controls failed")


def native_replay(compiler, sdk):
    with tempfile.TemporaryDirectory(prefix="connector-census-") as temp:
        binary = str(Path(temp) / "census")
        argv = [compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-pedantic"]
        if sdk:
            require(sdk.is_dir(), "missing explicitly supplied SDK")
            argv += ["-isysroot", str(sdk)]
        argv += [str(HERE / "census.cpp"), "-o", binary]
        subprocess.run(argv, check=True, timeout=120)
        rows = []
        for transfers, triple in ((4, 0), (2, 0), (2, 1)):
            result = subprocess.run([binary, str(transfers), str(triple)], capture_output=True,
                                    text=True, check=True, timeout=300)
            row = json.loads(result.stdout); rows.append(row)
            print(f"NATIVE t={transfers} triple={triple} assignments={row['assignments']} "
                  f"elapsed={row['elapsed_seconds']:.3f}s", flush=True)
        check_native_domains(rows)
        return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--full", action="store_true")
    p.add_argument("--write-receipt", action="store_true")
    p.add_argument("--compiler", default="c++")
    p.add_argument("--sdk", type=Path)
    args = p.parse_args()
    require(not args.write_receipt or args.full, "receipt regeneration requires full native replay")
    path = HERE / "COST-RECEIPT.json"
    old = json.loads(path.read_text()) if path.exists() else None
    start = monotonic()
    ideals = [ideal_census(n) for n in (5, 6)]
    require(ideals[0]["max_coverage"] == 32 and ideals[0]["universal"] == 175, "five-source positive control")
    require(ideals[1]["max_coverage"] == 59 and ideals[1]["universal"] == 0, "six-source optimistic exclusion")
    digest = sha256((HERE / "census.cpp").read_bytes()).hexdigest()
    if args.full:
        rows = native_replay(args.compiler, args.sdk)
    else:
        require(old is not None and old["native_source_sha256"] == digest, "unbound native source/receipt")
        rows = old["native"]; check_native_domains(rows)
    result = {"schema": "connector-cost-v1", "native_source_sha256": digest,
              "native": [native_core(row) for row in rows], "ideal": ideals}
    if args.write_receipt:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(old == result, "proof receipt differs; regenerate only with a full replay")
    print(f"PASS_COST_CENSUSES native_replay={'fresh' if args.full else 'NOT_RUN_receipt_bound_only'} "
          f"ideal_two_engines=5,6 elapsed={monotonic()-start:.3f}s")


if __name__ == "__main__":
    main()
