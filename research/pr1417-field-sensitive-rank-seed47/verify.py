#!/usr/bin/env python3
"""Recompute PR1417's P112 edge-tensor rank in two characteristics."""
from collections import Counter
import gzip
import hashlib
import io
import json
from math import isqrt
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
BASE = "410026dc5513b87db92ae98571d1d5984c69a983"
TARGET_HEAD = "c755bf393bea26d2275e1516b0560ca92de7a52e"
PRIME = 1009


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def source_bytes(path):
    return __import__("subprocess").check_output(
        ["git", "show", f"{BASE}:{path}"], cwd=ROOT
    )


def rank_gf2(rows):
    pivots = {}
    for row in rows:
        while row:
            col = row.bit_length() - 1
            if col in pivots:
                row ^= pivots[col]
            else:
                pivots[col] = row
                break
    return len(pivots)


def rank_mod(rows, p):
    pivots = {}
    pivot_edges = []
    for edge, raw in rows:
        row = [x % p for x in raw]
        for col in range(len(row)):
            value = row[col]
            if not value:
                continue
            old = pivots.get(col)
            if old is not None:
                row = [(x - value*y) % p for x, y in zip(row, old)]
                continue
            inv = pow(value, -1, p)
            pivots[col] = [(x*inv) % p for x in row]
            pivot_edges.append(edge)
            break
    return len(pivots), pivot_edges


def det_mod(matrix, p):
    a = [[x % p for x in row] for row in matrix]
    n = len(a)
    need(all(len(row) == n for row in a), "square minor dimensions")
    det = 1
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col]), None)
        need(pivot is not None, "selected minor has nonzero pivot")
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            det = -det
        value = a[col][col]
        det = det * value % p
        inv = pow(value, -1, p)
        a[col] = [(x*inv) % p for x in a[col]]
        for r in range(col + 1, n):
            factor = a[r][col]
            if factor:
                a[r] = [(x-factor*y) % p for x, y in zip(a[r], a[col])]
    return det % p


def load_ports():
    archive_path = "research/community-frontier1094-audit/selected-replay.tar.gz"
    archive_raw = source_bytes(archive_path)
    with tarfile.open(fileobj=io.BytesIO(archive_raw), mode="r:gz") as archive:
        member = "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz"
        packed = archive.extractfile(member)
        need(packed is not None, "selected canonical word member exists")
        word = json.loads(gzip.decompress(packed.read()))
    ports = word["ports"]
    need(len(ports) == 112 and len(set(ports)) == 112, "112 distinct selected ports")
    need(all(type(x) is int and 0 < x < 512 and x.bit_count() % 2 == 1 for x in ports),
         "selected ports are odd nonzero 9-bit labels")
    labels = [[(x >> j) & 1 for j in range(9)] for x in ports]
    return ports, labels


def main():
    sources = json.loads((PKG / "SOURCES.json").read_text())
    need(sources["base_commit"] == BASE, "exact research base pin")
    external = sources["external_sources"]
    need(external["pr"] == 1417 and external["head"] == TARGET_HEAD,
         "exact target PR head pin")
    for row in external["files"]:
        data = (PKG / row["snapshot"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["snapshot_sha256"],
             "target snapshot hash: " + row["name"])
    proof = (PKG / "TARGET-PROOF.md").read_text()
    need("F2^9 tensor V" in proof and "Characteristic two" in proof,
         "the target proof states the binary-field contract")
    certificate = json.loads((PKG / "TARGET-CERTIFICATE.json").read_text())
    need(len(certificate["basis_edges"]) == 80, "published 80-edge basis receipt")

    ports, labels = load_ports()
    weight_hist = Counter(map(sum, labels))
    edges = []
    gf2_rows = []
    modular_rows = []
    dots = Counter()
    for a, x in enumerate(labels):
        for b, y in enumerate(labels):
            if a == b:
                continue
            dot = sum(u*v for u, v in zip(x, y))
            if dot % 2:
                continue
            edge = (a, b)
            row = [x[i]*y[j] for i in range(9) for j in range(9)]
            bitrow = sum(value << (9*i+j)
                         for i in range(9) for j, value in enumerate(y)
                         if x[i])
            edges.append(edge)
            dots[dot] += 1
            gf2_rows.append(bitrow)
            modular_rows.append((edge, row))
    need(len(edges) == 5824, "selected ordered graph edge count")
    need(weight_hist == Counter({3: 77, 7: 35}), "exact port weight distribution")
    need(dots == Counter({0: 1400, 2: 3948, 6: 476}), "exact integer dot distribution on parity edges")
    edge_set = set(edges)
    basis = [tuple(edge) for edge in certificate["basis_edges"]]
    need(len(set(basis)) == 80 and all(e in edge_set for e in basis),
         "published basis edges belong to the selected graph")
    basis_rows = []
    for a, b in basis:
        x, y = labels[a], labels[b]
        basis_rows.append(sum(x[i]*y[j] << (9*i+j)
                              for i in range(9) for j in range(9)))
    need(rank_gf2(basis_rows) == 80, "published basis independent over F2")
    binary_rank = rank_gf2(gf2_rows)
    need(binary_rank == 80, "full graph tensor rank over F2")

    need(all(PRIME % d for d in range(2, isqrt(PRIME)+1)), "1009 is prime")
    odd_rank, pivot_edges = rank_mod(modular_rows, PRIME)
    need(odd_rank == 81 and len(pivot_edges) == 81,
         "full graph tensor rank over F1009")
    by_edge = {edge: row for edge, row in modular_rows}
    minor = [by_edge[e] for e in pivot_edges]
    minor_det = det_mod(minor, PRIME)
    need(minor_det != 0, "81x81 pivot minor has nonzero determinant mod 1009")

    port0_weight = sum(labels[0])
    edge01_dot = sum(u*v for u, v in zip(labels[0], labels[1]))
    need((0, 1) in edge_set and port0_weight == 3 and edge01_dot == 2,
         "concrete characteristic-zero S=I9 counterexample witnesses")
    need(port0_weight % 2 == 1 and edge01_dot % 2 == 0,
         "same witnesses satisfy the intended F2 identities")

    result = {
        "status": "PASS_PR1417_P112_EDGE_TENSOR_FIELD_SENSITIVITY_AUDIT",
        "base_commit": BASE,
        "target_pr": 1417,
        "target_head": TARGET_HEAD,
        "ordered_edges": len(edges),
        "port_weight_histogram": {str(k): v for k, v in sorted(weight_hist.items())},
        "edge_integer_dot_histogram": {str(k): v for k, v in sorted(dots.items())},
        "tensor_dimensions": [len(edges), 81],
        "rank_over_F2": binary_rank,
        "rank_over_F1009": odd_rank,
        "F1009_prime_divisors_checked_through": isqrt(PRIME),
        "F1009_full_rank_minor_edges": [list(e) for e in pivot_edges],
        "F1009_full_rank_minor_determinant": minor_det,
        "identity_form_witness": {
            "port_0_squared_norm_over_Z": port0_weight,
            "edge_0_1_dot_over_Z": edge01_dot,
            "port_0_squared_norm_mod2": port0_weight % 2,
            "edge_0_1_dot_mod2": edge01_dot % 2,
        },
        "interpretation": "The rank-80 certificate is valid in the explicitly stated F2/characteristic-two contract. The rank-81 result over F1009 proves that it cannot be transported unchanged to characteristic zero. This is not a counterexample to PR1417 under its stated binary-field assumptions and does not audit the full endpoint or cost theorem.",
        "controls": [
            "published 80-edge basis checked over F2",
            "full 5824-edge graph independently reduced over F2 and F1009",
            "nonzero 81x81 determinant modulo verified prime 1009",
            "identity-form witnesses distinguished modulo 2 and over integers",
            "pinned proof explicitly states F2 and characteristic two",
        ],
    }
    expected_path = PKG / "RESULT.json"
    if expected_path.exists():
        expected = json.loads(expected_path.read_text())
        need(result == expected, "stored exact field-sensitivity receipt")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
