"""Independent literal integer-cube oracle, without the matrix model.

Produced by Nick Petalas. Apache-2.0.
"""

from __future__ import annotations

import itertools
import json


def scalar_census(n: int, depth: int) -> dict:
    if (n, depth) not in ((2, 6), (3, 4)):
        raise ValueError("oracle domain")
    symbols = tuple((i, j, sign) for i in range(n) for j in range(n)
                    if i != j for sign in (-1, 1))
    corners = tuple(itertools.product((-1, 1), repeat=n))
    counts = []
    fib = [0, 1]
    for _ in range(depth + 2):
        fib.append(fib[-1] + fib[-2])
    for length in range(depth + 1):
        words = closed = 0
        maximum = 1
        for instructions in itertools.product(symbols, repeat=length):
            words += 1
            restores = True
            cut_peaks = [1] * (length + 1)
            for original in corners:
                cells = list(original)
                for cut, (target, source, sign) in enumerate(instructions, 1):
                    cells[target] += sign * cells[source]
                    cut_peaks[cut] = max(cut_peaks[cut], *map(abs, cells))
                restores = restores and tuple(cells) == original
            if restores:
                closed += 1
                for cut, actual in enumerate(cut_peaks):
                    if actual > fib[min(cut, length - cut) + 2]:
                        raise ValueError("literal cube exceeds closed-word guard")
                maximum = max(maximum, *cut_peaks)
        counts.append({"length": length, "words": words, "closed": closed,
                       "max_norm": maximum if closed else None})
    return {"rows": n, "depth": depth, "by_length": counts}


if __name__ == "__main__":
    print(json.dumps([scalar_census(2, 6), scalar_census(3, 4)], sort_keys=True))
    print("PASS_RESTORED_SHEAR_LITERAL_CUBE")
