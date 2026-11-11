#!/usr/bin/env python3
"""Exact binary endpoint constructions and complete small singleton models."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform

MAX_DIMENSION = 545


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows, width):
    require(0 <= width <= MAX_DIMENSION, "rank width outside finite check domain")
    require(len(rows) <= 2 * MAX_DIMENSION, "too many rank rows")
    pivots = [0] * width
    result = 0
    for original in rows:
        require(isinstance(original, int) and 0 <= original < 1 << width,
                "rank row outside binary ambient space")
        row = original
        for bit in range(width - 1, -1, -1):
            if not row >> bit & 1:
                continue
            if pivots[bit]:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                result += 1
                break
    return result


def span_rank(rows, width):
    """Independent exhaustive span cardinality, only in small ambient spaces."""
    require(0 <= width <= 6, "span oracle is restricted to six dimensions")
    span = {0}
    for row in rows:
        require(0 <= row < 1 << width, "span row outside binary space")
        span |= {value ^ row for value in span}
    size = len(span)
    require(size & (size - 1) == 0, "binary span size must be a power of two")
    return size.bit_length() - 1


def base_differences(n, b):
    """Use the predecessor support partition 3+3+2+4 when b=12."""
    blocks = (3, 3, 2, 4) if b == 12 else (2,) * (b // 2)
    differences = []
    offset = n
    for size in blocks:
        if size == 3:
            a, c, d = (1 << (offset + j) for j in range(3))
            differences.extend((c, d, a ^ c))
        else:
            for j in range(0, size, 2):
                a, c = 1 << (offset + j), 1 << (offset + j + 1)
                differences.extend((c, a ^ c))
        offset += size
    require(len(differences) == b, "base block dimension mismatch")
    return tuple(differences)


def construction(n, b, s, h):
    require(0 <= h <= n <= 523 and b in (0, 2, 4, 6, 12),
            "construction parameters outside the registered check domain")
    width = n + b + s
    require(0 <= s <= 10 and width <= MAX_DIMENSION, "invalid singleton count")
    unmarked = [1 << j for j in range(n)]
    differences = list(base_differences(n, b)) + [0] * s
    pairs = min(h, s // 2)
    for j in range(pairs):
        u = 1 << j
        a, c = 1 << (n + b + 2 * j), 1 << (n + b + 2 * j + 1)
        unmarked[j] = a ^ c
        differences[b + 2 * j] = a ^ u
        differences[b + 2 * j + 1] = u
    if s % 2 and h > pairs:
        u, a = 1 << pairs, 1 << (n + b + 2 * pairs)
        unmarked[pairs] = a
        differences[b + 2 * pairs] = a ^ u
    marked = tuple((1 << (n + j)) ^ d for j, d in enumerate(differences))
    return tuple(unmarked), marked, tuple(differences)


def check_construction(n, b, s, h):
    unmarked, marked, differences = construction(n, b, s, h)
    width = n + b + s
    require(rank(unmarked, width) == n, "unmarked arrivals lost rank")
    require(rank(unmarked + marked, width) == width, "terminal endpoint lost rank")
    changed = sum(row != 1 << j for j, row in enumerate(unmarked))
    require(changed <= h, "unmarked change budget exceeded")
    base_mask = (1 << (n + b)) - 1
    require(all(row & ~base_mask == 0 for row in differences[:b]),
            "base difference escaped its fixed library")
    for j in range(s):
        allowed = ((1 << n) - 1) | (1 << (n + b + j))
        require(differences[b + j] & ~allowed == 0, "singleton library escaped")
    stock = rank(unmarked + differences, width) - n
    require(stock == min(b + s, b + 2 * h), "sharp construction missed capacity")
    if width <= 6:
        require(span_rank(unmarked + marked, width) == width,
                "independent span oracle rejects endpoint")
        require(span_rank(unmarked + differences, width) - n == stock,
                "independent span oracle rejects stock")
    return {"unmarked": n, "base": b, "singletons": s, "budget": h,
            "changed": changed, "stock": stock}


def exhaustive_singletons(n, s):
    """Enumerate every unmarked replacement and every maximal-library choice."""
    width = n + s
    require((n == 0 and 1 <= s <= 4) or (n == 1 and 1 <= s <= 4)
            or (n == 2 and 1 <= s <= 2), "unregistered exhaustive domain")
    libraries = tuple(tuple(u | (coefficient << (n + j))
                            for coefficient in range(2) for u in range(1 << n))
                      for j in range(s))
    maxima = [-1] * (n + 1)
    endpoints = [0] * (n + 1)
    checked = 0
    for unmarked in itertools.product(range(1 << width), repeat=n):
        changed = sum(row != 1 << j for j, row in enumerate(unmarked))
        for differences in itertools.product(*libraries):
            checked += 1
            marked = tuple((1 << (n + j)) ^ d for j, d in enumerate(differences))
            endpoint_rank = span_rank(unmarked + marked, width)
            if endpoint_rank != width:
                continue
            require(rank(unmarked + marked, width) == endpoint_rank,
                    "independent endpoint ranks disagree")
            stock = span_rank(unmarked + differences, width) - n
            require(rank(unmarked + differences, width) - n == stock,
                    "independent difference ranks disagree")
            endpoints[changed] += 1
            for budget in range(changed, n + 1):
                maxima[budget] = max(maxima[budget], stock)
    expected = [min(s, 2 * h) for h in range(n + 1)]
    require(maxima == expected, "complete singleton model disagrees with theorem")
    require(checked == (1 << (width * n)) * (1 << ((n + 1) * s)),
            "incomplete enumeration")
    return {"unmarked": n, "singletons": s, "assignments": checked,
            "endpoints_by_exact_changes": endpoints, "maxima_by_budget": maxima}


def controls():
    require(rank((0, 1, 2), 3) == 2, "own-pivot cancellation was accepted")
    # Two marked cancellations cannot be rescued by a single changed arrival.
    require(rank((6, 1, 1), 3) < 3, "two cancelled singleton pivots accepted")
    # With the old unmarked arrival, differences inside U earn no quotient rank.
    require(rank((1, 1, 1), 3) - 1 == 0, "old-U payload was credited twice")
    # F_3 escapes the binary theorem: d=p keeps p+d nonzero.
    require((1 + 1) % 3 == 2, "characteristic-three scope control failed")
    rejected = 0
    for arguments in ((1, 0, 2, 2), (1, 1, 2, 0), (524, 0, 0, 0)):
        try:
            construction(*arguments)
        except ValueError:
            rejected += 1
    require(rejected == 3, "out-of-domain construction accepted")
    return {"mathematical_controls": 4, "invalid_parameter_controls": rejected}


def certificate():
    small = []
    for n, b, s in itertools.product(range(5), (0, 2, 4, 6, 12), range(11)):
        for h in range(n + 1):
            small.append(check_construction(n, b, s, h))
    actual_shape = [check_construction(523, 12, 10, h) for h in range(6)]
    census = [exhaustive_singletons(n, s)
              for n, upper in ((0, 4), (1, 4), (2, 2))
              for s in range(1, upper + 1)]
    return {"schema_version": 1, "claim_type": "scoped proof with finite corroboration",
            "construction_cases": len(small), "complete_small_models": census,
            "complete_assignments": sum(row["assignments"] for row in census),
            "same_dimension_synthetic_witnesses": actual_shape, "controls": controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = certificate()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in names}
    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    receipt = {"result": result, "result_sha256": hashlib.sha256(payload).hexdigest(),
               "source_sha256": hashes, "python": platform.python_version()}
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        require(not args.receipt.resolve().is_relative_to(package.parents[1]),
                "generated receipts must stay outside the checkout")
        require(args.receipt.write_text(rendered, encoding="utf-8") == len(rendered),
                "receipt write incomplete")
    print("PASS_BIT_TERMINAL_TWO_FOR_ONE " + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
