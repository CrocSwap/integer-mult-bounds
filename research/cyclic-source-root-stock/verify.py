#!/usr/bin/env python3
"""Exact corroboration of the fixed cyclic-source root-stock theorem."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dimension(n):
    require(type(n) is int and 1 <= n <= 10, "source count must be 1..10")


def span(basis):
    require(len(basis) <= 10, "basis exceeds replay capacity")
    result = [0]
    for vector in basis:
        result += [value ^ vector for value in result]
    return frozenset(result)


def differences(n):
    dimension(n)
    prefixes = [0]
    for label in list(range(n)) * 2:
        prefixes.append(prefixes[-1] ^ (1 << label))
    return {left ^ right for left in prefixes for right in prefixes}


def arcs(n):
    dimension(n)
    result = {0, (1 << n) - 1}
    for start in range(n):
        mask = 0
        for length in range(1, n):
            mask |= 1 << ((start + length - 1) % n)
            result.add(mask)
    return result


def all_subspaces(d):
    """Unique binary RREF bases, with every rank included, for d <= 6."""
    require(type(d) is int and 0 <= d <= 6, "RREF dimension must be 0..6")
    for rank in range(d + 1):
        for pivots in itertools.combinations(range(d), rank):
            free = [(row, col) for row, pivot in enumerate(pivots)
                    for col in range(pivot + 1, d) if col not in pivots]
            for assignments in range(1 << len(free)):
                basis = [1 << pivot for pivot in pivots]
                for index, (row, col) in enumerate(free):
                    if (assignments >> index) & 1:
                        basis[row] |= 1 << col
                yield span(basis)


def code_census():
    rows = []
    expected_codes = [1, 2, 5, 16, 67, 374, 2825]
    expected_minimum = [1, 1, 1, 2, 4, 5, 6]
    for n in range(1, 8):
        ones = (1 << n) - 1
        ds = differences(n)
        seen = set()
        feasible_by_dimension = [0] * (n + 1)
        for subspace in all_subspaces(n - 1):
            code = frozenset(subspace | {value ^ ones for value in subspace})
            require(code not in seen, "duplicate code in complete inventory")
            seen.add(code)
            covered = {h & d for h in code for d in ds}
            if len(covered) == 1 << n:
                feasible_by_dimension[len(code).bit_length() - 1] += 1
        minimum = next(k for k, count in enumerate(feasible_by_dimension) if count)
        require(len(seen) == expected_codes[n - 1], "incomplete code domain")
        require(minimum == expected_minimum[n - 1], "wrong root minimum")
        if n >= 5:
            require(feasible_by_dimension[n - 1:] == [(1 << (n - 1)) - 1, 1],
                    "hyperplane classification differs")
        rows.append({"n": n, "codes": len(seen), "minimum": minimum,
                     "feasible_by_dimension": feasible_by_dimension})
    return rows


def quotient(vector, columns):
    result = 0
    for index, column in enumerate(columns):
        if (vector >> index) & 1:
            result ^= column
    return result


def quotient_census():
    """Every surjective rank-two quotient killing ones, n=5..9."""
    rows = []
    for n in range(5, 10):
        count = 0
        for prefix in itertools.product(range(4), repeat=n - 1):
            last = 0
            for value in prefix:
                last ^= value
            columns = prefix + (last,)
            if len(set(columns) - {0}) < 2:
                continue
            count += 1
            pairs = [(i, j) for i in range(n) for j in range(i + 1, n)
                     if (j - i) not in (1, n - 1) and columns[i] and columns[j]
                     and columns[i] != columns[j]]
            require(bool(pairs), "rank-two cyclic obstruction has no witness")
            i, j = pairs[0]
            ones = (1 << n) - 1
            missing = ones ^ (1 << i) ^ (1 << j)
            for candidate in (missing, missing ^ (1 << i), missing ^ (1 << j)):
                require(quotient(candidate, columns) != 0, "invalid quotient witness")
            if n <= 6:
                kernel = [h for h in range(1 << n) if quotient(h, columns) == 0]
                require(all((h & d) != missing for h in kernel for d in differences(n)),
                        "direct coverage accepts a claimed missing mask")
        require(count == 4 ** (n - 1) - 3 * 2 ** (n - 1) + 2,
                "wrong surjective quotient domain")
        rows.append({"n": n, "rank_two_quotients": count})
    return rows


def reader(n, mask):
    dimension(n)
    require(type(mask) is int and 0 < mask < 1 << n, "invalid output mask")
    if n >= 5:
        h = mask
        if (mask & 1) == ((mask >> 1) & 1):
            cuts = (0, n)
        else:
            absent = 0 if not (mask & 1) else 1
            h |= 1 << absent
            cuts = (absent + 1, absent + n)
        return (h & 1) | ((h >> 2) << 1), cuts
    axes = [1] * n if n <= 3 else [1, 2, 1, 2]
    prefixes = [0]
    for label in list(range(n)) * 2:
        prefixes.append(prefixes[-1] ^ (1 << label))
    for r in range(1, 2 if n <= 3 else 4):
        h = sum(((r & axis).bit_count() % 2) << j for j, axis in enumerate(axes))
        for left in range(2 * n + 1):
            for right in range(left + 1, 2 * n + 1):
                if h & (prefixes[left] ^ prefixes[right]) == mask:
                    return r, (left, right)
    raise ValueError("small attaining code lacks a mask")


def program(n):
    dimension(n)
    roots = 1 if n <= 3 else 2 if n == 4 else n - 1
    ports = [0] * n if n <= 3 else [0, 1, 0, 1] if n == 4 else [0, 0] + list(range(1, n - 1))
    schedule = [[] for _ in range(2 * n + 1)]
    for mask in range(1, 1 << n):
        covector, cuts = reader(n, mask)
        support = [j for j in range(roots) if (covector >> j) & 1]
        require(bool(support), "zero reader cannot serve a nonzero output")
        pivot = support[0]
        block = [("X", pivot, j) for j in support[1:]]
        block += [("A", mask, pivot)]
        block += [("X", pivot, j) for j in reversed(support[1:])]
        for cut in cuts:
            schedule[cut].extend(block)
    word = []
    for cut, blocks in enumerate(schedule):
        word.extend(blocks)
        if cut < 2 * n:
            label = cut % n
            word.append(("B", label, ports[label]))
    require(len(word) <= 2 * n + 2 * ((1 << n) - 1) + 4 * (roots - 1) * ((1 << n) - 1),
            "compiled word exceeds its finite invoice")
    return roots, word


def endpoint(n, roots, word):
    """Free linear response symbols retain arbitrary root dirt and map order."""
    dimension(n)
    require(1 <= roots <= n and len(word) <= 45000, "program exceeds replay capacity")
    z = [1 << j for j in range(roots)]
    # Each target has its own A_m image space; bit roots+n is its untouched dirt.
    dirt = 1 << (roots + n)
    y = [dirt] * (1 << n)
    for kind, left, right in word:
        if kind == "X":
            z[left] ^= z[right]
        elif kind == "B":
            z[right] ^= 1 << (roots + left)
        elif kind == "A":
            y[left] ^= z[right]
        else:
            raise ValueError("unknown operation")
    return (z == [1 << j for j in range(roots)]
            and y == [dirt ^ (mask << roots) for mask in range(1 << n)])


def construction_checks():
    rows = []
    for n in range(1, 11):
        roots, word = program(n)
        require(endpoint(n, roots, word), "wrong dirty endpoint")
        require(endpoint(n, roots, list(reversed(word))), "inverse endpoint differs")
        sources = [left for kind, left, _ in word if kind == "B"]
        require(sources == list(range(n)) * 2, "source order changed")
        outputs = [0] * (1 << n)
        for kind, left, _ in word:
            if kind == "A":
                outputs[left] += 1
        require(outputs == [0] + [2] * ((1 << n) - 1), "readout incidence changed")
        shears = sum(kind == "X" for kind, _, _ in word)
        if n >= 5:
            require(shears == (2 * n - 5) * (1 << n) + 4, "wrong explicit shear bill")
        rows.append({"n": n, "roots": roots, "source_calls": len(sources),
                     "readouts": sum(outputs), "root_shears": shears})
    roots, word = program(5)
    for index in range(len(word)):
        require(not endpoint(5, roots, word[:index] + word[index + 1:]),
                "single omitted operation escaped")
    return rows, len(word)


def boundary_controls():
    rejected = 0
    for invalid in (0, 11, -1, True, 5.0):
        try:
            program(invalid)
        except ValueError:
            rejected += 1
    require(rejected == 5, "source-count validation failed")
    for mask in (0, 32, -1, True):
        try:
            reader(5, mask)
        except ValueError:
            rejected += 1
    require(rejected == 9, "mask validation failed")
    # C4 contains K2,2: alternating quotient columns are a real exception.
    columns = (1, 2, 1, 2)
    kernel = [h for h in range(16) if quotient(h, columns) == 0]
    require(len({h & d for h in kernel for d in differences(4)}) == 16,
            "four-cycle exception lost")
    return rejected


def compute():
    interval_checks = []
    for n in range(1, 11):
        ds = differences(n)
        require(ds == arcs(n), "prefix differences are not exactly cyclic arcs")
        require(len(ds) == n * (n - 1) + 2, "wrong cyclic-arc count")
        interval_checks.append({"n": n, "masks": len(ds)})
    constructions, omissions = construction_checks()
    return {"claim_type": "scoped proof with finite exact corroboration",
            "interval_checks": interval_checks, "code_census": code_census(),
            "quotient_census": quotient_census(), "constructions": constructions,
            "omission_rejections": omissions, "boundary_rejections": boundary_controls()}


def receipt():
    root = Path(__file__).resolve().parent
    files = ("verify.py", "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files}
    return {"schema": "cyclic-source-root-stock/v1", "sources_sha256": hashes, "result": compute()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print a generated receipt instead of comparing it")
    args = parser.parse_args()
    actual = receipt()
    if args.emit:
        print(json.dumps(actual, sort_keys=True, indent=2))
        return
    expected_path = Path(__file__).resolve().with_name("RESULT.json")
    require(expected_path.stat().st_size <= 100000, "receipt exceeds capacity")
    expected = json.loads(expected_path.read_text())
    require(json.dumps(expected, sort_keys=True) == json.dumps(actual, sort_keys=True),
            "source-bound receipt differs")
    print("PASS_CYCLIC_SOURCE_ROOT_STOCK codes=3290 quotients=85818 omissions=236 roots=n-1_for_n>=5")


if __name__ == "__main__":
    main()
