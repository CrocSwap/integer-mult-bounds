#!/usr/bin/env python3
"""First physical PR4940 pair, independently evaluated with signed PR4933 K.

Apache-2.0. Prepared for JoyboyBrian with substantial OpenAI Codex assistance.
Source authors and inherited proof obligations are credited in README.md.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P = 65537
IMAG = 256
OWNERS = 112
SIZE = 512


def need(ok, message):
    if not ok:
        raise ValueError(message)


def parity(x):
    return x.bit_count() & 1


def mv(rows, x):
    return sum(parity(row & x) << bit for bit, row in enumerate(rows))


def transpose(rows):
    return [sum(((row >> bit) & 1) << j for j, row in enumerate(rows))
            for bit in range(9)]


def signed_map(record, x, inverse=False, unsigned=False):
    rows, mask = record["G_rows"], record["Z_mask"]
    y = mv(transpose(rows) if inverse else rows, x)
    sign = 1 if unsigned else 1 - 2 * parity(mask & (x if inverse else y))
    return y, sign


def block(record_i, record_j, vector, coefficient, unsigned=False):
    out = {}
    for x, value in vector.items():
        y, sj = signed_map(record_j, x, unsigned=unsigned)
        z, si = signed_map(record_i, y, inverse=True, unsigned=unsigned)
        out[z] = out.get(z, 0) + coefficient * si * sj * value
    return {x: value for x, value in out.items() if value}


def sparse_q(vector, inverse=False):
    # Gaussian-rational pairs retain absolute phase without complex floats.
    s = -1 if inverse else 1
    out = {}
    for x, (re, im) in vector.items():
        for y, a, b in ((x, F(1, 2), F(s, 2)),
                        (x ^ 1, F(1, 2), F(-s, 2))):
            old = out.get(y, (F(0), F(0)))
            out[y] = (old[0] + a * re - b * im,
                      old[1] + a * im + b * re)
    return {x: value for x, value in out.items() if value != (0, 0)}


def sparse_block(ri, rj, vector, coefficient):
    out = {}
    for component in (0, 1):
        values = block(ri, rj, {x: v[component] for x, v in vector.items()}, coefficient)
        for x, value in values.items():
            old = list(out.get(x, (F(0), F(0))))
            old[component] = value
            out[x] = tuple(old)
    return {x: value for x, value in out.items() if value != (0, 0)}


def empty():
    return [[0] * SIZE for _ in range(OWNERS)]


def add(x, y, sign=1):
    return [[(a + sign * b) % P for a, b in zip(xi, yi)]
            for xi, yi in zip(x, y)]


def gaussian(bank, axes, inverse=False):
    a = (1 + (-IMAG if inverse else IMAG)) * pow(2, -1, P) % P
    b = (1 - (-IMAG if inverse else IMAG)) * pow(2, -1, P) % P
    out = [row[:] for row in bank]
    for bit in axes:
        step = 1 << bit
        for row in out:
            for start in range(0, SIZE, 2 * step):
                for x in range(start, start + step):
                    u, v = row[x], row[x + step]
                    row[x] = (a * u + b * v) % P
                    row[x + step] = (b * u + a * v) % P
    return out


def scalar_code(bank, modes, inverse=False):
    temp = [[sum(sign * bank[i][x] for i, sign in contacts) % P
             for x in range(SIZE)] for contacts in modes]
    denominator = pow(52 if inverse else 4, -1, P)
    out = [row[:] for row in bank]
    for mode, contacts in enumerate(modes):
        for i, sign in contacts:
            out[i] = [(a - sign * denominator * b) % P
                      for a, b in zip(out[i], temp[mode])]
    return out


def physical_code(bank, records, modes):
    mixed = empty()
    for i, row in enumerate(bank):
        for x, value in enumerate(row):
            if value:
                y, sign = signed_map(records[i], x)
                mixed[i][y] = sign * value % P
    mixed = scalar_code(mixed, modes)
    out = empty()
    for i, row in enumerate(mixed):
        for x, value in enumerate(row):
            if value:
                y, sign = signed_map(records[i], x, inverse=True)
                out[i][y] = sign * value % P
    return out


def run():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            need(sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                 "Changed pinned source: " + row["path"])
    source = ROOT / "research/coded-native-caller"
    receipt = json.loads((source / "NORMALIZERS.json").read_text())
    records = receipt["ports"]
    canonical = json.loads(gzip.decompress((source / "native-source.json.gz").read_bytes()))["canonical"]
    A = [[F(value) for value in row]
         for row in json.loads((source / "CODE.json").read_text())["A"]]
    columns = receipt["mode_columns"]
    need(len(records) == len(A) == OWNERS and all(len(row) == OWNERS for row in A), "112 owners")
    need(len(columns) == 8, "Eight source modes")
    need(all(A[i][j] == F(i == j) - F(sum(c[i] * c[j] for c in columns), 4)
             for i in range(OWNERS) for j in range(OWNERS)), "Every scalar code block")
    need(all(sum(a * b for a, b in zip(u, v)) == 56 * (j == k)
             for j, u in enumerate(columns) for k, v in enumerate(columns)), "Inverse factorization")
    for i, record in enumerate(records):
        rows, z = record["G_rows"], record["Z_mask"]
        need(record["port"] == i and record["q"] == canonical["ports"][i], "Actual owner ports")
        need(mv(rows, 1) == record["q"], "Central line image")
        need(all(parity(u & v) == (j == k)
                 for j, u in enumerate(rows) for k, v in enumerate(rows)), "Orthogonal K")
        need(all((mv(transpose(rows), x).bit_count() - x.bit_count() - 2 * parity(z & x)) % 4 == 0
                 for x in range(SIZE)), "Signed absolute-phase centralizer")
    ri, rj = records[:2]
    need(A[0][1] == F(-1, 2), "Actual off-diagonal source coefficient")
    actual = block(ri, rj, {1: F(1)}, A[0][1])
    formal = {1: A[0][1]}
    need(actual == {22: F(1, 2)} and actual != formal, "First physical C != scalar A witness")
    need(block(ri, rj, {1: F(1)}, A[0][1], unsigned=True) == {22: F(-1, 2)},
         "Omitted K phase changes exact signed witness")
    v = {0: (F(1), F(0))}
    cq = sparse_block(ri, rj, sparse_q(v), A[0][1])
    qc = sparse_q(sparse_block(ri, rj, v, A[0][1]))
    need(cq != qc, "Commuting C through Q is rejected")
    y_only = sparse_q(sparse_block(ri, rj, {1: (F(1), F(0))}, A[0][1]), inverse=True)
    need(y_only != qc, "Old Y-only backward Q^2 conjugation is rejected")

    # Independent direct modular address oracle includes actual Q and all eight D axes.
    need(IMAG * IMAG % P == P - 1, "Valid exact Gaussian-rational reduction")
    modes = [[(i, sign) for i, sign in enumerate(column) if sign] for column in columns]
    y = empty()
    y[1][1] = 1
    c_y = physical_code(y, records, modes)
    x_after_b = add(empty(), gaussian(gaussian(c_y, [0]), range(1, 9)), sign=-1)
    y_after_b = gaussian(y, range(1, 9))
    query = gaussian(scalar_code(x_after_b, modes, inverse=True), [0], inverse=True)
    y_after_pair = add(y_after_b, query)
    residual = gaussian(add(y, scalar_code(c_y, modes, inverse=True), sign=-1), range(1, 9))
    need(y_after_pair == residual and any(any(row) for row in residual), "Actual D(I-A^-1 C) y residual")
    # The actual x-only boundary cannot alter the retained y block.
    x_after_boundary = scalar_code(x_after_b, modes, inverse=True)
    expected_x = add(empty(), gaussian(gaussian(y, [0]), range(1, 9)), sign=-1)
    need(x_after_boundary != expected_x, "Actual x-only output boundary also differs")
    diagnostic = scalar_code(gaussian(residual, range(1, 9), inverse=True), modes)
    expected = add(scalar_code(y, modes), c_y, sign=-1)
    need(diagnostic == expected, "Invertible diagnostic A D^-1 yields (A-C)y")
    need(diagnostic[0][1] == diagnostic[0][22] == -pow(2, -1, P) % P,
         "Literal diagnostic output coefficient")
    a_y = scalar_code(y, modes)
    formal_query = gaussian(scalar_code(gaussian(gaussian(a_y, [0]), range(1, 9)), modes, inverse=True), [0], inverse=True)
    need(formal_query == y_after_b, "Scalar-A predecessor positive control cancels")
    helpers = {("helper", k) for k in range(408)}
    owned = {("mode", k) for k in range(8)} | {("query", k) for k in range(112)}
    cleanup = [("CLEAR", ("mode", k)) for _ in range(6) for k in range(8)]
    cleanup += [(op, ("query", k)) for op in ("CLEAR", "ERASE") for k in range(112)]
    def check_cleanup(word):
        need(all(target in owned and target not in helpers for _, target in word),
             "Arbitrary helper owner was changed or erased")
    check_cleanup(cleanup)
    try:
        check_cleanup(cleanup + [("ERASE", ("helper", 17))])
    except ValueError as error:
        need("erased" in str(error), "Helper rejection reason")
    else:
        raise ValueError("Arbitrary helper erasure accepted")
    return {"status": "PASS_CODED_REVERSE_PHYSICAL_PAIR_GAP",
            "scope": "First literal PR4940 pair under the signed PR4933 physical binding; no general caller obstruction",
            "width": 1, "owners": OWNERS, "addresses_per_owner": SIZE,
            "chronological_cut": {"p": 19, "backward_stage": 37, "next_thin_stage": 38,
                                  "intervening_bridge_or_idle": False},
            "exact_witness": {"source_port": 1, "destination_port": 0, "input_address": 1,
                              "A_01": "-1/2", "C_01_output": {"22": "1/2"},
                              "A_01_output": {"1": "-1/2"},
                              "diagnostic_A_Dinv_y": {"1": "-1/2", "22": "-1/2"}},
            "modular_oracle": {"prime": P, "i": IMAG, "actual_D_axes": list(range(1, 9)),
                               "nonzero_residual_coordinates": sum(bool(v) for row in residual for v in row)},
            "pair_y_to_y_block": "D*(I-A^-1*C)",
            "all_width_argument": "Evaluate each signed K tensor lift inside each owner block; A is applied once. C_f != A tensor I at every f>=1 and D_f is invertible.",
            "independent_helper_owners": len(helpers),
            "controls": ["scalar-A predecessor cancels", "omitted K sign changes witness", "C-Q commutation fails", "Y-only backward convention fails", "arbitrary helper erasure rejected"],
            "local_invoice": {"paid_gaussian_profile": {"1": 2313, "2": 412, "3": 510, "4": 127, "5": 40},
                              "native_helper_profile_retained": {"4": 28, "7": 7, "8": 47, "9": 326},
                              "native_wrapper_maps_upper": 896, "thin_inverse_query_pauli_maps": 112,
                              "scalar_A_or_Ainv_evaluations": 3, "recoding_adds": 2688,
                              "query_destination_adds": 112, "owned_recoding_clears": 48,
                              "owned_query_initial_clears": 112, "owned_query_copies": 112,
                              "owned_query_erasures": 112, "peak_added_owned_fields": 120,
                              "new_recursive_jobs_beyond_native": {"1": 112},
                              "denominators": [4, 52],
                              "unknown_not_zero": ["inherited native ordinary work", "fixed-tape matching/routing and field-map tariff", "odd-denominator precision and rounding", "whole-controller productive endpoint and compiler"]}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = run()
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(json.loads(path.read_text()) == result, "Changed mathematical receipt")
    print(result["status"])


if __name__ == "__main__":
    main()
