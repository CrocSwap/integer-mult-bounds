#!/usr/bin/env python3
"""Check the spatial support witness and a 63-equation integer minor."""

import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
CORE = LANES / "new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz"
INVENTORY = LANES / "oblique-native-20261017/interior-cut/ALL-CUT-EDGES.json.gz"
WARP_SOURCE = LANES / "new-native-recipes-20261017/sources/bw_adapters.py"
PRIME = 1000003


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path, pin):
    raw = gzip.decompress(path.read_bytes())
    need(hashlib.sha256(raw).hexdigest() == pin, "Input pin: " + path.name)
    return json.loads(raw)


def linear(columns, vector):
    out = 0
    for bit, column in enumerate(columns):
        if vector >> bit & 1:
            out ^= column
    return out


def inverse(columns):
    values = [linear(columns, x) for x in range(512)]
    need(len(set(values)) == 512, "Every warp map is invertible")
    back = {value: x for x, value in enumerate(values)}
    return [back[1 << bit] for bit in range(9)]


def contains(vectors, vector):
    basis = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit not in basis:
                basis[bit] = value
                break
            value ^= basis[bit]
    while vector:
        bit = vector.bit_length() - 1
        if bit not in basis:
            return False
        vector ^= basis[bit]
    return True


def independent(basis, row):
    row = dict(row)
    while row:
        pivot = min(row)
        if pivot not in basis:
            scale = pow(row[pivot], -1, PRIME)
            basis[pivot] = {key: value*scale % PRIME for key, value in row.items()}
            return True
        scale = row[pivot]
        for key, value in basis[pivot].items():
            result = (row.get(key, 0) - scale*value) % PRIME
            if result:
                row[key] = result
            else:
                row.pop(key, None)
    return False


def determinant(matrix):
    matrix = [list(row) for row in matrix]
    sign, previous = 1, 1
    for i in range(len(matrix)-1):
        pivot_row = next(j for j in range(i, len(matrix)) if matrix[j][i])
        if pivot_row != i:
            matrix[i], matrix[pivot_row] = matrix[pivot_row], matrix[i]
            sign = -sign
        pivot = matrix[i][i]
        for j in range(i+1, len(matrix)):
            for k in range(i+1, len(matrix)):
                value = matrix[j][k]*pivot - matrix[j][i]*matrix[i][k]
                need(value % previous == 0, "Exact integer determinant division")
                matrix[j][k] = value // previous
            matrix[j][i] = 0
        previous = pivot
    return sign*matrix[-1][-1]


def main():
    core_pin = "a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa"
    inventory_pin = "18c89367243fc7c09411f28a8022884130373ce4886de806f4b011edec030418"
    warp_pin = "c5907050a9a7fa36d4fcba3ad4fe440d1bec2063360c095013891785ba65c3ce"
    core, inventory = read(CORE, core_pin), read(INVENTORY, inventory_pin)
    need(hashlib.sha256(WARP_SOURCE.read_bytes()).hexdigest() == warp_pin,
         "Logical warp definition pin")
    need(core["providers"]["base"]["programs"] == core["providers"]["extra"]["programs"],
         "The two providers have the same event indices and frame IDs")
    r = [{int(key): int(value) for key, value in row.items()} for row in core["R"]]
    provider_checks = {}
    for name, provider in core["providers"].items():
        word = provider["canonical"]
        ports = word["ports"]
        maps = {w["op"]: w["G_columns"] for w in word["warps"]}
        maps.update({-key: inverse(columns) for key, columns in list(maps.items())})
        counts = Counter()
        for product in inventory["products"]:
            frame = word["frames"][product["frame"]]
            tail = inventory["tail_columns"][product["tail_column"]]
            for t, _, _ in tail:
                need(all((value & ports[t]).bit_count() % 2 == 0 for value in frame),
                     "The cut frame lies in every final target hole")
            for s, history, numerator, denominator in inventory["source_rows"][product["source_row"]]["constrained"]:
                if s >= 112:
                    continue
                need(numerator != 0 and denominator > 0, "Nonzero rational source term")
                vector = ports[s]
                for operator, sign in history:
                    need(operator[0] == "K" and sign in (-1, 1), "Forward warp word")
                    vector = linear(maps[sign*operator[1]], vector)
                need(contains(frame, vector), "The transported source line lies in the cut frame")
                counts["source_terms"] += 1
                counts["nonempty_source_words"] += bool(history)
                for t, _, _ in tail:
                    counts["tail_incidences"] += 1
                    need((ports[t] & vector).bit_count() % 2 == 0, "Physical spatial support")
                    if (ports[t] & ports[s]).bit_count() % 2:
                        need(vector != ports[s], "The forbidden spatial diagonal entry is zero")
                        counts["forbidden_spatial_diagonal_controls"] += 1
        provider_checks[name] = dict(counts)
    ports = core["providers"]["base"]["canonical"]["ports"]
    basis, pairs, all_equations = {}, [], 0
    for t in range(112):
        for s in range(112):
            if t == s or not (ports[t] & ports[s]).bit_count() % 2:
                continue
            row = {8*a+b: r[a].get(t, 0)*r[b].get(s, 0)
                   for a in range(8) for b in range(8)
                   if r[a].get(t, 0)*r[b].get(s, 0)}
            need(sum(row.get(9*a, 0) for a in range(8)) == 0, "I8 is an exact solution")
            all_equations += 1
            if independent(basis, {key: value % PRIME for key, value in row.items()}):
                pairs.append([t, s])
    need(len(pairs) == 63, "Sixty-three independent centre equations")
    columns = list(range(63))
    matrix = [[r[a].get(t, 0)*r[b].get(s, 0)
               for a in range(8) for b in range(8) if 8*a+b in columns]
              for t, s in pairs]
    det = determinant(matrix)
    need(det != 0, "The integer minor is nonzero")
    diagonal_counts = Counter(str(1-Fraction(sum(row.get(p, 0) for row in r)**2, 32))
                              for p in range(112))
    need(diagonal_counts == {"1": 42, "7/8": 56, "1/2": 14},
         "The rank-seven dense projection has a nonzero diagonal")
    result = {
        "status": "PASS_SPATIAL_SUPPORT_AND_INTEGER_MINOR",
        "input_pins": {"core_decompressed": core_pin, "inventory_decompressed": inventory_pin,
                       "logical_warp_source": warp_pin},
        "provider_checks": provider_checks,
        "forbidden_offdiagonal_pairs": all_equations,
        "independent_pairs": pairs,
        "centre_entry_columns": columns,
        "integer_minor_determinant": str(det),
        "exact_centre_kernel": "span(I8)",
        "rank_seven_projection": "I8 - ones(8,8)/8",
        "rank_seven_projection_diagonal_counts": dict(diagonal_counts),
        "scope": "The supplied all-cut inventory, with its complete current native source states and unchanged Y tail. Actual monomial phases do not alter the spatial support witness. Inventory completeness is a separate source dependency.",
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "SUPPORT.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"], "determinant", det, provider_checks, flush=True)


if __name__ == "__main__":
    main()
