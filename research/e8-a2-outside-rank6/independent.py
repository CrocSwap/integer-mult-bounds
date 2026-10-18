"""Separate dual-plane and bitmask census. Shared authenticated root model."""

import json
import runpy
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise ValueError(message)


def dense_basis(values):
    rows = [[(x >> i) & 1 for i in range(9)] for x in values]
    check(len(rows) <= 512, "bounded dense rows")
    pivot = 0
    for col in range(9):
        candidates = [i for i in range(pivot, len(rows)) if rows[i][col]]
        if not candidates:
            continue
        chosen = candidates[0]
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        for i in range(len(rows)):
            if i != pivot and rows[i][col]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[pivot], strict=True)]
        pivot += 1
    return tuple(sum(bit << i for i, bit in enumerate(row)) for row in rows[:pivot])


def ordered_space(rows):
    check(len(rows) <= 9, "bounded dimension")
    return tuple(xor_selected(rows, code)
                 for code in range(1 << len(rows)))


def xor_selected(rows, code):
    value = 0
    for i, row in enumerate(rows):
        if code >> i & 1:
            value ^= row
    return value


def mask(values):
    return sum(1 << x for x in values)


def enumerate_spaces(roots, live, fiber):
    w = ordered_space(dense_basis(fiber))
    check(len(w) == 128 and len(set(w)) == 128, "dense fiber rank")
    wm, rm, lm, am = map(mask, (w, roots, live, fiber))
    counts, u_counts = Counter(), Counter()
    total, live_equal, eligible = 0, 0, 0
    # Each two-dimensional dual space has a unique sorted nonzero triple.
    for a in range(1, 128):
        for b in range(a + 1, 128):
            if not b < (a ^ b):
                continue
            u = tuple(w[x] for x in range(128)
                      if not (a & x).bit_count() % 2
                      and not (b & x).bit_count() % 2)
            check(len(u) == 32, "two independent equations")
            um = mask(u)
            j = (um & am).bit_count()
            u_counts[j] += 1
            eligible += j == 10
            extensions = 0
            for t in range(512):
                if wm >> t & 1 or t != min(x ^ t for x in u):
                    continue
                vm = um | mask(tuple(x ^ t for x in u))
                score = (vm & rm).bit_count() + j
                check(score <= 30, "independent upper bound")
                counts[score] += 1
                total += 1
                extensions += 1
                if score == 30 and vm & rm & ~lm == 0:
                    live_equal += 1
            check(extensions == 12, "quotient extension coverage")
    check(total == 32004 and eligible == 216, "independent coverage totals")
    return counts, u_counts, live_equal


def main():
    # Authentication is shared; no primary census, basis or extension is called.
    api = runpy.run_path(str(PACKAGE / "verify.py"))
    roots, live, fiber, _ = api["model"]()
    counts, u_counts, live_equal = enumerate_spaces(roots, live, fiber)
    result = json.loads((PACKAGE / "RESULT.json").read_text())
    check({str(k): v for k, v in counts.items()} == result["joint_histogram"],
          "independent joint histogram")
    check({str(k): v for k, v in u_counts.items()}
          == result["fiber_intersection_histogram"], "independent U histogram")
    witness = result["witness"]
    v = set(ordered_space(dense_basis(witness["basis"])))
    w = set(ordered_space(dense_basis(fiber)))
    check(len(v) == 64 and not v <= w and len(v & w) == 32, "outside rank six")
    check(sorted(v & roots) == witness["support"], "witness root closure")
    check(sorted(v & fiber) == witness["fiber_support"], "witness fiber closure")
    check(v & roots <= live and len(v & roots) + len(v & fiber) == 30,
          "actual live sharpness")
    check(counts[30] == 1080 and live_equal == 144, "independent equality counts")
    print("PASS_INDEPENDENT_OUTSIDE_RANK6 spaces=32004 equality=1080 P112=144")


if __name__ == "__main__":
    main()
