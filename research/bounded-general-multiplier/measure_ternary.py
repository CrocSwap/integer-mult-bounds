"""Measure construction of the same ordered good-leaf coefficients at a placed chart."""

from pathlib import Path
from statistics import median
from timeit import repeat
from random import Random
import json
import platform
import sys
import tracemalloc

from ternary_leaf import lower_coefficient, lower_slot, ordered_chart, select_pivot
from ternary_frames import covered_factors

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
from leaf import good_column


def measure(n):
    if n % 3 != 1:
        raise ValueError("The all-ones projector must have trace one")
    p = [[1] * n for _ in range(n)]
    u = v = a = [1] * n

    def predecessor():
        return good_column(p, a, 3)

    def thin(line=(u, v)):
        column, covector = line
        order, b, c = ordered_chart(column, covector, select_pivot(column, covector), 3)
        lower, inv = [], pow(c[0], -1, 3)
        for s in range(4 * (n - 1)):
            dst, src, i = lower_slot(n, s)
            alpha = lower_coefficient(s // (n - 1), i, b, c, a[order[0]], a[order[i]], inv, 3)
            lower.append(["lower", dst, src, alpha])
        return lower + [["weighted_swap", 0, 2 * n - 1, a[order[0]] * c[0] % 3]] + [
            ["lower", dst, src, -x % 3] for _, dst, src, x in reversed(lower)
        ]

    original = predecessor()
    redundant = 3 * (n - 1)
    assert original[redundant] == original[-1 - redundant] == ["lower", 2 * n - 1, 0, 0]
    original.pop(-1 - redundant)
    original.pop(redundant)
    assert original == thin()

    origin = [1] + [0] * (n - 1)
    cover = [[1] + [int(i == j) - int(i == 0) for j in range(1, n)] for i in range(n)]
    rng = Random(n)
    for _ in range(8 * n):
        src, dst = rng.sample(range(1, n), 2)
        coefficient = rng.choice((1, 2))
        for row in cover:
            row[dst] = (row[dst] + coefficient * row[src]) % 3
    assert covered_factors((origin, origin), cover, 1) == (u, v)

    def full_predecessor():
        row, column = covered_factors((origin, origin), cover, 1)
        matrix = [[x * y % 3 for y in column] for x in row]
        return good_column(matrix, a, 3)

    def full_thin():
        return thin(covered_factors((origin, origin), cover, 1))
    assert full_predecessor() == predecessor() and full_thin() == thin()

    def runs(fn, count):
        elapsed = median(repeat(fn, number=count, repeat=5)) / count
        tracemalloc.start()
        fn()
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        return {"seconds": elapsed, "peak_python_bytes": peak}
    return {"N": n, "placed_predecessor": runs(predecessor, 1), "placed_ternary": runs(thin, 100),
            "from_cover_predecessor": runs(full_predecessor, 1), "from_cover_ternary": runs(full_thin, 3)}


if __name__ == "__main__":
    print(json.dumps({"python": platform.python_version(), "machine": platform.machine(),
                      "cases": [measure(n) for n in (16, 34, 64)]}, indent=2))
