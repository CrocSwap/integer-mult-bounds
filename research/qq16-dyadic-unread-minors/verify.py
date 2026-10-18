#!/usr/bin/env python3
"""Exact dyadic-admission census for a fixed QQ16 unread-basis neighborhood.

Standard library only. All validation remains active under -O. Apache-2.0.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path


PACKET = "research/joint-query/certificate.json.gz"
PACKET_SHA256 = "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7"
PAYLOAD_SHA256 = "2efe83c59978aa9c0db2c3e4eccc14cbfdcd3c9ce499432601b5dd34083472ef"
BASE_PORTS = (1, 2, 3, 4, 5, 6, 8, 12)
BAD_PORTS = (1, 25, 3, 4, 5, 6, 8, 12)
KERNEL_VECTOR = (1, 2, 1, 1, 1, 1, 3, -2)
A_PORTS = (0, 7, 20, 27, 36, 46, 57, 111)
T_PORTS = (21, 37, 47, 76, 81, 87, 92, 110)
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_matrix(root):
    path = root / PACKET
    require(path.stat().st_size <= 8_000_000, "source container too large")
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == PACKET_SHA256, "packet source pin differs")
    payload = gzip.decompress(raw)
    require(sha256(payload).hexdigest() == PAYLOAD_SHA256, "packet payload differs")
    packet = json.loads(payload)
    require(len(packet["R_rows"]) == 8, "wrong query dimension")
    matrix = [[Q(row.get(str(p), "0")) for p in range(112)]
              for row in packet["R_rows"]]
    require(all(x.denominator == 1 and abs(x) <= 1
                for row in matrix for x in row), "query matrix is not signed binary")
    ordinary = tuple(packet["U_ports"])
    selected = tuple(packet["A_ports"] + packet["T_ports"])
    require(tuple(packet["A_ports"]) == A_PORTS
            and tuple(packet["T_ports"]) == T_PORTS, "selected minors differ")
    require(len(ordinary) == len(set(ordinary)) == 96, "wrong ordinary partition")
    require(len(selected) == len(set(selected)) == 16, "wrong selected partition")
    require(set(ordinary).isdisjoint(selected)
            and set(ordinary + selected) == set(range(112)), "incomplete partition")
    gram = [[sum(matrix[i][p] * matrix[j][p] for p in ordinary)
             for j in range(8)] for i in range(8)]
    require(gram == [[Q(48 * (i == j)) for j in range(8)]
                     for i in range(8)], "ordinary Gram differs")
    for ports in (A_PORTS, T_PORTS):
        selected_gram = [[sum(matrix[i][p] * matrix[j][p] for p in ports)
                          for j in range(8)] for i in range(8)]
        require(selected_gram == [[Q(4 * (i == j)) for j in range(8)]
                                  for i in range(8)], "selected Gram differs")
    return matrix, ordinary


def minor(matrix, ports):
    require(len(ports) == len(set(ports)) == 8, "minor needs eight distinct ports")
    require(all(0 <= p < 112 for p in ports), "port outside matrix")
    return [[row[p] for p in ports] for row in matrix]


def inverse(matrix):
    """Return the rational inverse and signed determinant, or None and zero."""
    n = len(matrix)
    require(n == 8 and all(len(row) == n for row in matrix), "expected 8x8 matrix")
    work = [list(map(Q, row)) + [Q(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    determinant = Q(1)
    for i in range(n):
        pivot = next((j for j in range(i, n) if work[j][i]), None)
        if pivot is None:
            return None, Q(0)
        if pivot != i:
            work[i], work[pivot] = work[pivot], work[i]
            determinant = -determinant
        value = work[i][i]
        determinant *= value
        work[i] = [x / value for x in work[i]]
        for j in range(n):
            if j != i:
                value = work[j][i]
                work[j] = [x - value * y for x, y in zip(work[j], work[i])]
    return [row[n:] for row in work], determinant


def product(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(8))
             for j in range(8)] for i in range(8)]


def identity():
    return [[Q(i == j) for j in range(8)] for i in range(8)]


def dyadic(value):
    denominator = Q(value).denominator
    return denominator & (denominator - 1) == 0


def determinant_unit(value):
    value = abs(Q(value))
    return bool(value) and dyadic(value) and dyadic(1 / value)


def integer(value):
    value = Q(value)
    require(value.denominator == 1, "nonintegral determinant or coordinate")
    return value.numerator


def census(matrix, ordinary, base_inverse, base_determinant):
    """Use the one-/two-column determinant lemma, with integral scaled coordinates."""
    outside = tuple(p for p in ordinary if p not in BASE_PORTS)
    require(len(outside) == 88, "wrong exchange alphabet")
    coordinates = {
        p: [integer(4 * sum(base_inverse[i][k] * matrix[k][p]
                            for k in range(8))) for i in range(8)]
        for p in outside
    }
    histograms = [Counter({abs(integer(base_determinant)): 1}), Counter(), Counter()]
    for i in range(8):
        for p in outside:
            det = integer(base_determinant * coordinates[p][i] / 4)
            histograms[1][abs(det)] += 1
    for i, j in combinations(range(8), 2):
        for p, q in combinations(outside, 2):
            small_det = (coordinates[p][i] * coordinates[q][j]
                         - coordinates[q][i] * coordinates[p][j])
            det = integer(base_determinant * small_det / 16)
            histograms[2][abs(det)] += 1
    expected_counts = (1, 704, 107184)
    require(tuple(sum(h.values()) for h in histograms) == expected_counts,
            "exchange domain incomplete")
    return [{str(d): count for d, count in sorted(h.items())} for h in histograms]


def witness(matrix):
    base = minor(matrix, BASE_PORTS)
    base_inverse, base_det = inverse(base)
    require(base_det == -32, "base determinant differs")
    require(product(base, base_inverse) == product(base_inverse, base) == identity(),
            "base inverse differs")
    require(all(dyadic(x) for row in base_inverse for x in row),
            "positive base is not dyadically invertible")
    bad = minor(matrix, BAD_PORTS)
    bad_inverse, bad_det = inverse(bad)
    require(bad_det == -80, "obstructed determinant differs")
    require(product(bad, bad_inverse) == product(bad_inverse, bad) == identity(),
            "rational inverse does not exist")
    image = [integer(sum(row[j] * KERNEL_VECTOR[j] for j in range(8)))
             for row in bad]
    require(image == [0, 10, 0, 0, 0, 0, 0, 0], "mod-five certificate differs")
    require(KERNEL_VECTOR[0] % 5 != 0 and all(x % 5 == 0 for x in image),
            "mod-five kernel is trivial")
    require(bad_inverse[0][1] == Q(1, 10), "non-dyadic coefficient differs")
    require(not determinant_unit(bad_det)
            and not all(dyadic(x) for row in bad_inverse for x in row),
            "bad example admits a dyadic inverse")
    return base_inverse, base_det, {
        "base_ports_ordered": list(BASE_PORTS),
        "base_determinant": integer(base_det),
        "base_inverse": [[str(x) for x in row] for row in base_inverse],
        "bad_ports_ordered": list(BAD_PORTS),
        "exchange": {"removed": 2, "inserted": 25},
        "bad_determinant": integer(bad_det),
        "bad_inverse": [[str(x) for x in row] for row in bad_inverse],
        "modular_prime": 5, "integer_vector": list(KERNEL_VECTOR),
        "integer_image": image,
        "non_dyadic_inverse_entry": {"row": 0, "column": 1, "value": "1/10"},
    }


def cut_witness(matrix, ordinary):
    """Replay the constant-owner two-cut family, including its selected dirt."""
    def query(values, ports):
        return [sum(row[p] * values[p] for p in ports) for row in matrix]

    def section(q, p):
        return sum(matrix[k][p] * q[k] for k in range(8)) / 4

    selected = A_PORTS + T_PORTS
    x, y = [Q(0)] * 112, [Q(0)] * 112
    for p, value in zip(BAD_PORTS, KERNEL_VECTOR):
        x[p] = Q(value)
    q = query(x, ordinary)
    for p in A_PORTS:
        x[p], y[p] = -section(q, p), section(q, p)
    f, c = query(x, range(112)), query(x, T_PORTS)
    require(f == c == [Q(0)] * 8, "constant-family F0 driver differs")
    x1, y1 = x[:], y[:]
    for p in ordinary:
        x1[p] = x[p] - section(f, p)
        y1[p] = y[p] + x1[p]
    for p in selected:
        x1[p] = section(c if p in A_PORTS else f, p)
        y1[p] = x[p] + y[p] - x1[p]
    u = y1[:]
    future = query(y1, range(112))
    for p in A_PORTS:
        u[p] = section(future, p)
    # The exact B1 equations give y2_A=u_A and C=x1_U-y1_U.
    observed_a = [u[p] for p in A_PORTS]
    observed_other = ([x1[p] for p in ordinary if p not in BAD_PORTS]
                      + [x1[p] for p in selected] + [y1[p] for p in selected]
                      + [x1[p] - y1[p] for p in ordinary])
    require(all(value == 0 for value in observed_other), "other cut records nonzero")
    require(any(observed_a) and all(dyadic(value / 5) for value in observed_a),
            "observed records are not in the ideal 5 Z[1/2]")
    require(x[BAD_PORTS[0]] == 1, "required output has no unit coordinate")
    return {"constant_owner_and_payload": True,
            "observed_y2_A_order": list(A_PORTS),
            "observed_y2_A": [str(value) for value in observed_a],
            "other_observed_arrays_zero": len(observed_other),
            "required_original_X_port": BAD_PORTS[0], "required_value": "1",
            "query_image": [str(value) for value in q]}


def controls(matrix, base_inverse):
    duplicate = minor(matrix, BASE_PORTS)
    for row in duplicate:
        row[1] = row[0]
    require(inverse(duplicate) == (None, Q(0)), "singular control accepted")
    wrong = [row[:] for row in base_inverse]
    wrong[0][0] = -wrong[0][0]
    require(product(wrong, minor(matrix, BASE_PORTS)) != identity(),
            "wrong inverse control accepted")
    require(dyadic(Q(1, 4)) and not dyadic(Q(1, 10)), "denominator control failed")
    require(determinant_unit(-32) and not determinant_unit(-80),
            "nonzero-as-unit control accepted")
    changed = list(KERNEL_VECTOR)
    changed[0] += 1
    image = [sum(row[j] * changed[j] for j in range(8))
             for row in minor(matrix, BAD_PORTS)]
    require(any(x % 5 for x in image), "changed modular witness accepted")
    try:
        minor(matrix, BASE_PORTS[:-1] + (BASE_PORTS[0],))
    except ValueError:
        pass
    else:
        raise ValueError("duplicate-port control accepted")
    return ["singular minor", "wrong inverse sign", "odd denominator",
            "nonzero determinant is not a dyadic unit", "changed modular vector",
            "duplicate unread port"]


def report(root):
    matrix, ordinary = load_matrix(root)
    base_inverse, base_det, certificate = witness(matrix)
    histograms = census(matrix, ordinary, base_inverse, base_det)
    totals = Counter()
    for histogram in histograms:
        for det, count in histogram.items():
            label = ("singular" if det == "0" else
                     "dyadic_unit" if determinant_unit(int(det)) else "odd_factor")
            totals[label] += count
    require(dict(totals) == {"dyadic_unit": 59023, "singular": 46365,
                             "odd_factor": 2501}, "census totals differ")
    return {
        "schema_version": 1, "status": "PASS_QQ16_DYADIC_UNREAD_MINORS",
        "source_sha256": PACKET_SHA256, "payload_sha256": PAYLOAD_SHA256,
        "domain": {"ports": 96, "unread": 8, "maximum_exchanges": 2,
                   "sets": 107889, "sets_at_distance": [1, 704, 107184]},
        "absolute_determinant_histograms_by_distance": histograms,
        "classification_totals": dict(sorted(totals.items())),
        "certificate": certificate, "constant_two_cut_witness": cut_witness(matrix, ordinary),
        "rejecting_controls": controls(matrix, base_inverse),
        "scope": "Dyadic-linear complete-input decoding under the PR2443 two-cut contract; not a selected-input obstruction, native implementation or supplier.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--receipt", type=Path, default=PACKAGE / "RESULT.json")
    parser.add_argument("--emit", action="store_true", help="emit a receipt without reading one")
    args = parser.parse_args()
    result = report(args.repo)
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.emit:
        print(encoded, end="")
        return
    expected = json.loads(args.receipt.read_text(encoding="utf-8"))
    require(json.dumps(expected, sort_keys=True, indent=2) + "\n" == encoded,
            "receipt differs from complete recomputation")
    print("PASS_QQ16_DYADIC_UNREAD_MINORS sets=107889 dyadic=59023 odd_factor=2501 singular=46365")


if __name__ == "__main__":
    main()
