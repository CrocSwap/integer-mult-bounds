"""Check the address leaf against direct rank-one projection on the whole small ring."""

from collections import Counter
from itertools import product
import json
from pathlib import Path
from random import Random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cover import require
from leaf import column_program, run_columns


def direct(projector, weights, head, tail, modulus):
    """Scatter the projected head-tail difference back to both physical banks."""
    m = len(head)
    f = len(weights)
    result = [row.copy() for row in head + tail]
    for j, a in enumerate(weights):
        delta = [
            (tail[m - 1 - i][f - 1 - j] - pow(a[i], -1, modulus) * head[i][j]) % modulus
            for i in range(m)
        ]
        for i, row in enumerate(projector):
            change = sum(x * y for x, y in zip(row, delta, strict=True))
            result[i][j] = (head[i][j] + a[i] * change) % modulus
            result[2 * m - 1 - i][f - 1 - j] = (
                tail[m - 1 - i][f - 1 - j] - change
            ) % modulus
    return result


def run():
    q, width, m = 3, 2, 2
    modulus = q**width
    vectors = list(product(range(modulus), repeat=m))
    projectors = {
        tuple(tuple(x * y % modulus for y in v) for x in u)
        for u in vectors
        for v in vectors
        if sum(x * y for x, y in zip(u, v, strict=True)) % modulus == 1
    }
    units = [i for i in range(modulus) if i % q]
    rng = Random(7913)
    topologies = {}
    count = Counter()
    for projector in sorted(projectors):
        low = tuple(tuple(z % q for z in row) for row in projector)
        for f in (1, 2, 3, 5):
            weights = [[rng.choice(units) for _ in range(m)] for _ in range(f)]
            head, tail = [
                [[rng.randrange(modulus) for _ in range(f)] for _ in range(m)]
                for _ in range(2)
            ]
            actual, good, calls = run_columns(projector, weights, head, tail, q, width)
            require(
                actual == direct(projector, weights, head, tail, modulus),
                "complete physical projection",
            )
            require(
                all(0 < j <= f for j in calls) and len(calls) <= 32 * m * m,
                "paid child widths",
            )
            if good:
                require(calls == [f], "single reversed child")
            for a in weights:
                plan, _ = column_program(projector, a, q, width)
                slots = tuple(tuple(ins[:3]) for ins in plan)
                require(
                    topologies.setdefault(low, slots) == slots,
                    "unweighted low schedule",
                )
            count["good" if good else "bad"] += 1
    require(
        len(projectors) == 108 and len(topologies) == 12,
        "complete split rank-one enumeration over Z/9",
    )
    return dict(
        projectors=len(projectors), low_types=len(topologies), instances=dict(count)
    )


if __name__ == "__main__":
    result = run()
    if "--emit" not in sys.argv:
        require(
            result == json.loads((HERE / "RESULT.json").read_bytes())["leaves"],
            "independent leaf receipt",
        )
    print(json.dumps(result, sort_keys=True))
    print("PASS_GRADE14_COMPLETE_LOCAL_RING")
