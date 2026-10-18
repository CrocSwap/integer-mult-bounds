"""Corroborate all rank-six spaces in the canonical eight-dimensional fiber span."""

import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import require, root_data


def table(values):
    result = {0: 0}
    for value in values:
        if value not in result:
            bit = 1 << (len(result).bit_length() - 1)
            result.update(
                {x ^ value: coordinate | bit for x, coordinate in tuple(result.items())}
            )
    return result


def main():
    g, roots, labels = root_data()
    a, b = roots[:2]
    require(g.dot(a, b) == 0, "canonical orthogonal pair")
    axis = {i for i, r in enumerate(roots) if g.dot(a, r) and not g.dot(b, r)}
    mapping = table(tuple(labels[i] for i in sorted(axis)))
    require(len(mapping) == 256, "fiber span dimension eight")
    seen, maximum, maximizers = set(), 0, 0
    for x, y in combinations(range(1, 256), 2):
        key = frozenset((x, y, x ^ y))
        if key in seen:
            continue
        seen.add(key)
        closure = {
            i
            for i, value in enumerate(labels)
            if value in mapping
            and not (mapping[value] & x).bit_count() % 2
            and not (mapping[value] & y).bit_count() % 2
        }
        if closure - axis:
            size = len(closure & axis)
            require(size <= 13, "nonconcentrated capacity")
            if size > maximum:
                maximum, maximizers = size, 1
            elif size == maximum:
                maximizers += 1
    require(len(seen) == 10795 and maximum == 13, "complete canonical corroboration")
    print(
        f"PASS_D6_AXIS_CORROBORATION spaces={len(seen)} "
        f"max={maximum} maximizers={maximizers}"
    )


if __name__ == "__main__":
    main()
