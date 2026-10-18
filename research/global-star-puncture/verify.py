#!/usr/bin/env python3
"""Exact global-star puncture certificates. Apache-2.0; see README.md."""

import json
from itertools import combinations, product
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
SEED = 40


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ports(p, k):
    return [
        sum(1 << (2 * pair + sign) for pair, sign in zip(support, signs))
        for support in combinations(range(p), k)
        for signs in product((0, 1), repeat=k)
    ]


def row_for_star(port_list, star):
    return sum(1 << i for i, port in enumerate(port_list) if port & star == star)


def basis_with_witness(rows):
    basis = {}
    for i, row in enumerate(rows):
        witness = 1 << i
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (row, witness)
                break
            value, used = basis[pivot]
            row ^= value
            witness ^= used
    return basis


def solve(basis, row):
    witness = 0
    for pivot in sorted(basis, reverse=True):
        if row >> pivot & 1:
            value, used = basis[pivot]
            row ^= value
            witness ^= used
    return None if row else witness


def xor_selected(rows, selection):
    value = 0
    for i, row in enumerate(rows):
        if selection >> i & 1:
            value ^= row
    return value


def dual_rows(port_list, p):
    missing = [next(i for i in range(p) if not port & (3 << (2 * i)))
               for port in port_list]
    rows = [sum(1 << n for n, m in enumerate(missing) if m == i)
            for i in range(p)]
    for i, j in combinations(range(p), 2):
        rows.append(sum(
            1 << n for n, (port, m) in enumerate(zip(port_list, missing))
            if (m == i and port >> (2 * j + 1) & 1)
            or (m == j and port >> (2 * i + 1) & 1)
        ))
    return rows, missing


def check_dual(rows, checks):
    require(all((row & check).bit_count() % 2 == 0
                for row in rows for check in checks), "dual does not annihilate stars")


def check_decoder(port_list, stars, target, deleted, coefficients):
    # Evaluate the literal identity separately from binary elimination.
    require(0 <= coefficients < 1 << len(stars), "coefficient mask out of range")
    require(len(set(deleted)) == len(deleted) and target not in deleted,
            "invalid deletion set")
    require(all(0 <= d < len(port_list) for d in deleted), "invalid port")
    selected = [star for i, star in enumerate(stars) if coefficients >> i & 1]
    for i, port in enumerate(port_list):
        if i not in deleted:
            value = sum(port & star == star for star in selected) % 2
            require(value == (i == target), "decoder identity failed")


def rejected(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control accepted")


def experiment():
    p, k = 5, 4
    port_list = ports(p, k)
    stars = [star for d in range(1, k) for star in ports(p, d)]
    rows = [row_for_star(port_list, star) for star in stars]
    target = SEED % len(port_list)
    target_port = port_list[target]
    corrections = [sum(1 << i for i, port in enumerate(port_list)
                       if (port & target_port).bit_count() == j)
                   for j in range(1, k)]
    elementary = [0] * k
    for star, row in zip(stars, rows):
        if star & target_port == star:
            elementary[star.bit_count()] ^= row
    for j, correction in enumerate(corrections, 1):
        expansion = 0
        for d in range(j, k):
            if comb(d, j) % 2:
                expansion ^= elementary[d]
        require(correction == expansion, "correction expansion failed")

    basis = basis_with_witness(rows)
    checks, missing = dual_rows(port_list, p)
    check_dual(rows, checks)
    require(len(basis) == 65 and len(basis_with_witness(checks)) == 15,
            "rank certificate failed")
    require(xor_selected(checks, (1 << p) - 1) == (1 << len(port_list)) - 1,
            "even-weight certificate failed")
    signatures = [sum(((check >> i) & 1) << j for j, check in enumerate(checks))
                  for i in range(len(port_list))]
    require(len(set(signatures)) == 80 and all(signatures), "port separation failed")

    local_rows = [row for star, row in zip(stars, rows) if star & target_port == star]
    local_basis = basis_with_witness(local_rows + corrections)
    available = [i for i in range(len(port_list)) if i != target]
    coverage, certificates = [], []
    for deleted_count in range(4):
        feasible = []
        for deleted in combinations(available, deleted_count):
            desired = (1 << target) | sum(1 << i for i in deleted)
            witness = solve(basis, desired)
            dual_ok = all((desired & check).bit_count() % 2 == 0 for check in checks)
            require((witness is not None) == dual_ok, "primal/dual mismatch")
            if witness is not None:
                require(xor_selected(rows, witness) == desired, "witness lift failed")
                check_decoder(port_list, stars, target, deleted, witness)
                feasible.append({"deleted": list(deleted), "stars_hex": hex(witness),
                                 "target_local": solve(local_basis, desired) is not None})
        coverage.append({"deleted_count": deleted_count,
                         "tested_exact_supports": comb(79, deleted_count),
                         "feasible": len(feasible)})
        certificates.extend(feasible)
    require([c["feasible"] for c in coverage] == [0, 0, 0, 67], "puncture census failed")
    require(sum(c["target_local"] for c in certificates) == 4, "local census failed")
    same_cube = [c for c in certificates if all(missing[i] == missing[target]
                                               for i in c["deleted"])]
    require(len(same_cube) == 35, "same-cube classification failed")
    example_stars = [sum(1 << i for i in coordinates)
                     for coordinates in ((2, 6), (2, 4, 6), (2, 5, 6))]
    example = sum(1 << stars.index(star) for star in example_stars)
    check_decoder(port_list, stars, target, [32, 33, 41], example)
    require(any(c["deleted"] == [32, 33, 41] and not c["target_local"]
                for c in certificates), "explicit off-target example failed")
    for cert in certificates:
        support = [target] + cert["deleted"]
        cubes = {missing[i] for i in support}
        if len(cubes) == 1:
            require(xor_selected(port_list, sum(1 << i for i in support)) == 0,
                    "affine plane classification failed")
        else:
            require(len(cubes) == 2, "two-cube classification failed")
            a, b = sorted(cubes)
            for m, flipped in ((a, b), (b, a)):
                pair = [port_list[i] for i in support if missing[i] == m]
                require(len(pair) == 2 and pair[0] ^ pair[1] == 3 << (2 * flipped),
                        "cross-cube edge classification failed")

    controls = []
    rejected(lambda: check_dual(rows, [checks[0] ^ (1 << target)] + checks[1:]))
    controls.append("one-bit dual corruption")
    rejected(lambda: check_dual(rows + [1 << target], checks))
    controls.append("forbidden degree-k singleton")
    cert = certificates[0]
    coefficients = int(cert["stars_hex"], 16)
    rejected(lambda: check_decoder(port_list, stars, target, cert["deleted"], 0))
    controls.append("zero decoder")
    rejected(lambda: check_decoder(port_list, stars, target, cert["deleted"][:-1], coefficients))
    controls.append("restore one required puncture")
    require(xor_selected(rows, coefficients) >> cert["deleted"][0] & 1,
            "punctured source coefficient missing")
    rejected(lambda: check_decoder(port_list, stars, target, [target], coefficients))
    controls.append("deleted target")
    rejected(lambda: check_decoder(port_list, stars, target, cert["deleted"], 1 << len(stars)))
    controls.append("out-of-range star")
    small_ports = ports(4, 3)
    small_target = small_ports[0]
    require(any((port & small_target).bit_count() == 1 for port in small_ports),
            "non-power-of-two control is empty")
    # For k=3, e1+C1 equals the target indicator: parity(k)=1.
    require(all(((port & small_target).bit_count() % 2)
                ^ ((port & small_target).bit_count() == 1) == (port == small_target)
                for port in small_ports), "k=3 positive control failed")
    small_checks, _ = dual_rows(small_ports, 4)
    correction = sum(1 << i for i, port in enumerate(small_ports)
                     if (port & small_target).bit_count() == 1)
    require(any((correction & row).bit_count() % 2 for row in small_checks),
            "power-of-two hypothesis control failed")
    controls.append("k=3 correction escapes dual")

    binary_ports = ports(3, 2)
    binary_rows = [row_for_star(binary_ports, star) for star in ports(3, 1)]
    binary_checks, _ = dual_rows(binary_ports, 3)
    check_dual(binary_rows, binary_checks)
    binary_signatures = [sum(((row >> i) & 1) << j
                             for j, row in enumerate(binary_checks))
                         for i in range(len(binary_ports))]
    require(len(set(binary_signatures)) == 12
            and all(row.bit_count() == 4 for row in binary_rows),
            "k=2 companion check failed")

    return {"status": "PASS_GLOBAL_STAR_PUNCTURE", "seed": SEED,
            "p": p, "k": k, "target_index": target,
            "port_encoding": "bit 2*i+s selects sign s from pair i; combination/product order",
            "ports": port_list, "stars": stars, "star_rank": len(basis),
            "dual_rows_hex": [hex(row) for row in checks], "dual_rank": 15,
            "coverage": coverage, "same_cube_witnesses": len(same_cube),
            "cross_cube_witnesses": 67 - len(same_cube),
            "target_local_witnesses": 4, "certificates": certificates,
            "controls": controls, "companion_cases": ["k=2,p=3", "k=3,p=4"],
            "new_kappa": False}


def main():
    actual = experiment()
    expected = json.loads((HERE / "results.json").read_text())
    require(actual == expected, "committed receipt differs from fresh computation")
    print("PASS_GLOBAL_STAR_PUNCTURE threshold=3 supports=82240 witnesses=67 "
          "local=4 dual_rank=15 controls=7 no_new_kappa")


if __name__ == "__main__":
    main()
