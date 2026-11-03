"""Finite corroboration. Produced by Nick Petalas. Apache-2.0."""

import hashlib
import json
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (audit_flagged, block, conjugate_ports, identity, image_rank,
                   install, inverse, multiply, pairs, rank_bits, rank_mod,
                   require, scalar_minimum)


def binary_rows(n, active, codes):
    rows = [1 << i for i in range(2 * n)]
    layers = [[1 << i for i in range(n)] for _ in range(2)]
    for (i, j), code in zip(active, codes):
        a, b, c = code & 1, (code >> 1) & 1, (code >> 2) & 1
        rows[2 * i] |= (a << (2 * j)) | (b << (2 * j + 1))
        rows[2 * i + 1] |= c << (2 * j + 1)
        layers[0][i] |= a << j
        layers[1][i] |= c << j
    return rows, layers


def binary_census():
    count, oracle_count, scalar_count = 0, 0, 0
    minima, rank_counts = [], [0] * 7
    edges = pairs(3)
    for mask in range(64):
        minimum, _, checked = scalar_minimum(3, mask, 2)
        scalar_count += checked
        active = [edge for k, edge in enumerate(edges) if (mask >> k) & 1]
        block_minimum = 7
        for codes in product(range(8), repeat=len(active)):
            rows, layers = binary_rows(3, active, codes)
            rank = rank_bits(rows, 6)
            lower = sum(rank_bits(layer, 3) for layer in layers)
            require(rank >= lower >= 2 * minimum, "binary theorem failure")
            block_minimum = min(block_minimum, rank)
            rank_counts[rank] += 1
            count += 1
            if not any(codes) or all(code == 7 for code in codes):
                require(rank == image_rank(rows, 6), "binary image oracle")
                oracle_count += 1
        require(block_minimum == 2 * minimum, "binary minimum not attained")
        minima.append(minimum)
    for bits in range(512):
        rows = [(bits >> (3 * i)) & 7 for i in range(3)]
        require(rank_bits(rows, 3) == image_rank(rows, 3), "scalar image oracle")
    require(count == 531441 and scalar_count == 729 and len(minima) == 64,
            "incomplete binary census")
    require(sum(rank_counts) == count, "unaccounted binary ranks")
    return {"masks": 64, "block_matrices": count, "scalar_fits": scalar_count,
            "full_image_oracle_cases": oracle_count, "scalar_image_cases": 512,
            "scalar_minima": minima, "block_rank_counts": rank_counts}


def port_chart(d, port, p):
    matrix = identity(d)
    matrix = matrix[port % d:] + matrix[:port % d]
    for a in range(d):
        for b in range(d):
            if a != b:
                scale = (a + b + port + 1) % p
                matrix[a] = [(x + scale * y) % p for x, y in zip(matrix[a], matrix[b])]
    inv = inverse(matrix, p)
    require(multiply(matrix, inv, p) == multiply(inv, matrix, p) == identity(d), "chart inverse")
    return matrix


def scalar_lift(scalar, d):
    n = len(scalar)
    matrix = [[0] * (n * d) for _ in range(n * d)]
    for i in range(n):
        for j in range(n):
            install(matrix, i, j, [[scalar[i][j] * int(a == b)
                                   for b in range(d)] for a in range(d)], d)
    return matrix


def chart_cases():
    cases, strict = 0, 0
    for p, d, mask in product((2, 3, 5), (2, 3, 4), (0, 13, 21, 42, 63)):
        minimum, scalar, _ = scalar_minimum(3, mask, p)
        charts = [port_chart(d, i, p) for i in range(3)]
        matrix = scalar_lift(scalar, d)
        dense = conjugate_ports(matrix, charts, p)
        rank, layers = audit_flagged(dense, mask, d, charts, p)
        require(rank == d * minimum and layers == [minimum] * d, "charted attainer")
        for k, (i, j) in enumerate(pairs(3)):
            if not (mask >> k) & 1:
                continue
            value = block(matrix, i, j, d)
            for a in range(d):
                for b in range(a + 1, d):
                    value[a][b] = (i + 2 * j + 3 * a + 5 * b + 1) % p
            install(matrix, i, j, value, d)
        dense = conjugate_ports(matrix, charts, p)
        rank, layers = audit_flagged(dense, mask, d, charts, p)
        require(layers == [minimum] * d and rank >= d * minimum, "charted extension")
        strict += int(rank > d * minimum)
        cases += 2
    require(cases == 90, "incomplete chart domain")
    return {"charted_cases": cases, "extensions_strict_above_minimum": strict}


def c5_matrix():
    """Classical five-edge, two-coordinate C5 representation."""
    matrix = [[0] * 10 for _ in range(10)]
    coordinates = [((i - 1) % 5, i) for i in range(5)]
    for i, j, a, b in product(range(5), range(5), range(2), range(2)):
        matrix[2 * i + a][2 * j + b] = int(coordinates[i][a] == coordinates[j][b])
    mask = sum(1 << k for k, (i, j) in enumerate(pairs(5)) if (i - j) % 5 in (1, 4))
    return matrix, mask


def rejection_controls():
    def rejected(matrix, mask, d, charts, p, reason):
        try:
            audit_flagged(matrix, mask, d, charts, p)
        except ValueError as error:
            require(str(error) == reason, "wrong rejection cause")
            return 1
        raise ValueError("fault accepted: " + reason)

    count = 0
    unit = identity(4)
    charts = [identity(2), identity(2)]
    changed = [row[:] for row in unit]
    changed[0][0] = 0
    count += rejected(changed, 0, 2, charts, 2, "nonidentity diagonal")
    changed = [row[:] for row in unit]
    changed[0][2] = 1
    count += rejected(changed, 0, 2, charts, 2, "forbidden block")
    changed = [row[:] for row in unit]
    changed[1][2] = 1
    count += rejected(changed, 1, 2, charts, 2, "incompatible flag")
    count += rejected(unit, 0, 2, [[[1, 0], [0, 0]], identity(2)], 2, "singular chart")
    count += rejected(unit, 0, 2, charts, 4, "unsupported finite field")
    count += rejected(unit, 4, 2, charts, 2, "mask range")
    count += rejected(unit[:-1], 0, 2, charts, 2, "matrix shape")
    count += rejected(unit, 0, 2, [identity(3), identity(3)], 2, "chart size")
    count += rejected(unit, 0, 5, charts, 2, "audit capacity")
    return count


def boundary_cases():
    charts = [identity(2), [[0, 1], [1, 0]], [[1, 1], [0, 1]]]
    matrix = conjugate_ports(scalar_lift([[1] * 3 for _ in range(3)], 2), charts, 2)
    rank, _ = audit_flagged(matrix, 63, 2, charts, 2)
    require(rank == 2, "portwise sharp fixture")
    lines = ((1, 0), (0, 1), (1, 1))
    global_lines = 0
    for line in lines:
        preserves = True
        for i, j in product(range(3), repeat=2):
            image = [sum(x * y for x, y in zip(row, line)) % 2 for row in block(matrix, i, j, 2)]
            preserves &= tuple(image) in ((0, 0), line)
        global_lines += int(preserves)
    require(global_lines == 0, "fixture unexpectedly has a global flag")
    upper = [identity(3) for _ in range(3)]
    upper[1][0][1], upper[2][1][2] = 1, 1
    matrix = conjugate_ports(scalar_lift([[1] * 3 for _ in range(3)], 3), upper, 3)
    rank, _ = audit_flagged(matrix, 63, 3, [identity(3)] * 3, 3)
    a, b = block(matrix, 0, 1, 3), block(matrix, 0, 2, 3)
    require(rank == 3 and multiply(a, b, 3) != multiply(b, a, 3), "noncommuting sharp fixture")
    c5, mask = c5_matrix()
    rows = [sum(x << j for j, x in enumerate(row)) for row in c5]
    require(rank_mod(c5, 2) == image_rank(rows, 10) == 5, "C5 rank")
    flags = (identity(2), [[0, 1], [1, 0]], [[1, 0], [1, 1]])
    incompatible = 0
    for choice in product(flags, repeat=5):
        try:
            audit_flagged(c5, mask, 2, choice, 2)
        except ValueError as error:
            require(str(error) == "incompatible flag", "C5 wrong rejection")
            incompatible += 1
    require(incompatible == 243, "C5 flag-breaking boundary")
    return {"portwise_attaining_rank": 2, "global_binary_flags": global_lines,
            "noncommuting_attaining_rank": 3, "classical_C5_rank": 5,
            "C5_incompatible_local_flag_tuples": incompatible}


def source_receipt():
    directory = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "model.py", "verify.py")
    receipt = {}
    for name in names:
        path = directory / name
        require(path.is_file() and path.stat().st_size <= 131072, "package file capacity")
        receipt[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return receipt


def main():
    output = {"claim_type": "scoped written proof with exact finite corroboration",
              "binary_census": binary_census(), "chart_cases": chart_cases(),
              "boundary_cases": boundary_cases(), "rejections": rejection_controls(),
              "package_sha256": source_receipt(), "status": "PASS_COMPATIBLE_FLAG_FITTING_RANK"}
    print(json.dumps(output, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
