"""Compare local Bell projections with complete sums over independent assignments."""

from itertools import product as choices
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contraction import Chart, events, project


def value(chart, assignment):
    if chart is None:
        return 0
    raw = (assignment << 1) | 1
    if any((row & raw).bit_count() % 2 for row in chart.rows):
        return 0
    sign = sum((term & raw) == term for term in chart.phase) % 2
    return 1 - 2 * sign


def compare(chart, pairs):
    checked = 0
    for digit in range(3):
        new, power = project(chart, pairs, digit)
        for low in range(1 << (2 * pairs - 2)):
            required = sum(value(chart, low | (x << (2 * pairs - 2)) | (y << (2 * pairs - 1)))
                           for x, y in choices((0, 1), repeat=2) if x + y == digit)
            actual = (1 << power) * value(new, low)
            if required != actual:
                raise ValueError((pairs, digit, chart, low, required, actual))
            checked += 1
    return checked


def main():
    total = 0
    # All two-variable phase functions and all systems of affine equations.
    for equation_set in range(256):
        rows = tuple(i for i in range(8) if equation_set & (1 << i))
        for phase in range(16):
            terms = frozenset(t for i, t in enumerate((0, 2, 4, 6)) if phase & (1 << i))
            total += compare(Chart(rows, terms), 1)
    rng = Random(7850)
    for pairs in range(2, 6):
        n = 2 * pairs
        atoms = [1 << (i + 1) for i in range(n)]
        terms = [0, *atoms, *(x | y for i, x in enumerate(atoms) for y in atoms[:i])]
        for k in range(64):
            rows = tuple(rng.randrange(2 << n) for _ in range(k % (n + 1)))
            phase = frozenset(t for t in terms if rng.randrange(2))
            total += compare(Chart(rows, phase), pairs)
    for m in range(9):
        for chart in (Chart((), frozenset()), None):
            trace = list(events(chart, m))
            n = 3 ** m
            # One advance per leaf and at most two additional moves per edge.
            if trace.count(">") - trace.count("<") != n or len(trace) > 5 * n:
                raise ValueError("The event stream exceeded the proved travel")
    print("exact_projection_values", total, "traversals", 18)


if __name__ == "__main__":
    main()
