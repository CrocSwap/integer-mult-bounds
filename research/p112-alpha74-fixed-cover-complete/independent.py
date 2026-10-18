"""Second implementation: transpose RREF over F103, independent space enumeration."""

import itertools
import runpy
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / "verify.py"))


def dense_rref(matrix, modulus=None):
    rows = [
        [x % modulus for x in row] if modulus else list(map(Fraction, row))
        for row in matrix
    ]
    pivots, rank = [], 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = (
            pow(rows[rank][column], -1, modulus) if modulus else 1 / rows[rank][column]
        )
        rows[rank] = [x * scale % modulus if modulus else x * scale for x in rows[rank]]
        for i in range(len(rows)):
            if i == rank:
                continue
            scale = rows[i][column]
            if scale:
                rows[i] = [
                    (x - scale * y) % modulus if modulus else x - scale * y
                    for x, y in zip(rows[i], rows[rank], strict=True)
                ]
        pivots.append(column)
        rank += 1
        if rank == len(rows):
            break
    return rows, pivots


def deletion_candidates(points, ids):
    matrix = [[points[i][j] for i in ids] for j in range(8)]
    reduced, pivots = dense_rref(matrix, 103)
    V["require"](len(pivots) == 8, "second baseline modular rank")
    free = [j for j in range(len(ids)) if j not in pivots]
    columns = {}
    for k, pivot in enumerate(pivots):
        columns[ids[pivot]] = tuple(-reduced[k][j] % 103 for j in free)
    for k, j in enumerate(free):
        columns[ids[j]] = tuple(int(i == k) for i in range(len(free)))
    buckets, zero = {}, []
    for index, column in columns.items():
        pivot = next((x for x in column if x), None)
        if pivot is None:
            zero.append(index)
        else:
            scale = pow(pivot, -1, 103)
            key = tuple(x * scale % 103 for x in column)
            buckets.setdefault(key, []).append(index)
    candidates = {(i,) for i in zero}
    for i in zero:
        candidates |= {tuple(sorted((i, j))) for j in ids if i != j}
    for bucket in buckets.values():
        candidates |= {
            tuple(sorted(pair)) for pair in itertools.combinations(bucket, 2)
        }
    return sorted(candidates)


def rational_kernel(points, ids):
    matrix, pivots = dense_rref([points[i] for i in ids])
    answer = []
    for free in range(8):
        if free in pivots:
            continue
        vector = [Fraction(int(i == free)) for i in range(8)]
        for k, pivot in enumerate(pivots):
            vector[pivot] = -matrix[k][free]
        answer.append(V["primitive"](vector))
    return answer


def classify(points, labels, fixture, allowed):
    cover = set(fixture["U_roots"] + fixture["V_roots"])
    outside = [i for i in range(111, -1, -1) if i not in cover]
    masks = [
        sum(
            1 << i for i, label in enumerate(labels) if (x & label).bit_count() % 2 == 0
        )
        for x in range(512)
    ]
    count, active, candidates, records = 0, 0, 0, set()
    for a in range(1, 512):
        for b in range(a + 1, 512):
            if b >= a ^ b:
                continue  # Exactly the smallest two nonzero vectors of each two-space.
            count += 1
            mask = masks[a] & masks[b]
            ids = [i for i in outside if not (mask >> i & 1)]
            cuts = deletion_candidates(points, ids)
            active += bool(cuts)
            for cut in cuts:
                candidates += 1
                nullspace = rational_kernel(points, [i for i in ids if i not in cut])
                V["require"](len(nullspace) <= 1, "second nullspace dimension")
                for h in nullspace:
                    V["require"](h in allowed, "second additional direction")
                    required = sorted(
                        i
                        for i in ids
                        if sum(x * y for x, y in zip(h, points[i], strict=True))
                    )
                    V["require"](required == [allowed[h]], "second necessary cut")
                    records.add((a, b, required[0], h))
    V["require"](count == 43_435, "second incomplete space count")
    return active, candidates, records


def main():
    geometry = V["authenticate"]()
    data = V["load_fixture"](geometry)
    active, candidates, records = classify(*data)
    expected = V["read_json"](HERE / "RESULT.json")
    target = {
        (
            r["annihilator"][0],
            r["annihilator"][1],
            r["required_root"],
            tuple(r["direction"]),
        )
        for r in expected["classification"]
    }
    V["require"](records == target and len(records) == 8, "second classification")
    V["require"]((active, candidates) == (8, 320), "second candidate counts")
    print("PASS_ALPHA74_SECOND_RREF spaces=43435 candidates=320 directions=8")


if __name__ == "__main__":
    main()
