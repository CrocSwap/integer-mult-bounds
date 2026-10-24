#!/usr/bin/env python3
"""Check exact cover tables and formal group-algebra constructions.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    count = 0
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256")
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob")
        count += 1
    require(count == 3, "source count")
    return count


def groups():
    cyclic = [[(i + j) % 7 for j in range(7)] for i in range(7)]
    order21 = []
    for i, j in itertools.product(range(7), range(3)):
        order21.append([
            3 * ((i + pow(2, j) * k) % 7) + (j + l) % 3
            for k, l in itertools.product(range(7), range(3))
        ])
    # Entries encode 1,i,j,k,-1,-i,-j,-k. The group sign is part of the label.
    units = ((0, 1, 2, 3), (1, 4, 3, 6), (2, 7, 4, 1), (3, 2, 5, 4))
    quaternion = [[units[i % 4][j % 4] ^ (i & 4) ^ (j & 4)
                   for j in range(8)] for i in range(8)]
    return {"C7": cyclic, "C7:C3": order21, "Q8": quaternion}


def check_group(table):
    n = len(table)
    require(table[0] == list(range(n)), "left identity")
    require([r[0] for r in table] == list(range(n)), "right identity")
    require(all(sorted(r) == list(range(n)) for r in table), "Latin rows")
    require(all(table[table[a][b]][c] == table[a][table[b][c]]
                for a, b, c in itertools.product(range(n), repeat=3)), "associativity")


def cover(word, table):
    result = {}
    for mask in range(1 << len(word)):
        label = 0
        for j, g in enumerate(word):
            if mask >> j & 1:
                label = table[label][g]
        result.setdefault(label, mask)
    return result


def clean(poly, modulus=None):
    return {g: (c % modulus if modulus else c) for g, c in poly.items()
            if (c % modulus if modulus else c)}


def multiply(left, right, table, modulus=None):
    require(len(left[0]) == len(right), "matrix dimensions")
    out = [[{} for _ in right[0]] for _ in left]
    for i, row in enumerate(left):
        for k, x in enumerate(row):
            for j, y in enumerate(right[k]):
                for g, a in x.items():
                    for h, b in y.items():
                        label = table[g][h]
                        out[i][j][label] = out[i][j].get(label, 0) + a * b
    return [[clean(p, modulus) for p in row] for row in out]


def scalar(matrix, modulus=None):
    return [[clean({0: c}, modulus) for c in row] for row in matrix]


def identity(n):
    return [[{0: 1} if i == j else {} for j in range(n)] for i in range(n)]


def gate(projector, label, modulus=None):
    n = len(projector)
    require(all(len(row) == n for row in projector), "projector dimensions")
    differences = [sum(projector[i][k] * projector[k][j] for k in range(n))
                   - projector[i][j] for i in range(n) for j in range(n)]
    require(all((v % modulus if modulus else v) == 0 for v in differences), "idempotent")
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            p = {0: int(i == j) - projector[i][j]}
            p[label] = p.get(label, 0) + projector[i][j]
            row.append(clean(p, modulus))
        out.append(row)
    return out


def diagonal(labels):
    return [[{g: 1} if i == j else {} for j in range(len(labels))]
            for i, g in enumerate(labels)]


def compile_word(word, targets, table, workspace=0):
    masks = cover(word, table)
    require(all(t in masks for t in targets), "uncovered target")
    n = len(targets) + workspace
    result = identity(n)
    for j, g in enumerate(word):
        bits = [(masks[t] >> j) & 1 for t in targets] + [0] * workspace
        projector = [[bits[i] if i == k else 0 for k in range(n)] for i in range(n)]
        result = multiply(result, gate(projector, g), table)
    return result


def classify(table):
    n = len(table)
    two = {}
    for g, h in itertools.product(range(1, n), repeat=2):
        labels = tuple(sorted(set(cover((g, h), table)) - {0}))
        if len(labels) == 3:
            two.setdefault(labels, (g, h))
    records = []
    for targets in itertools.combinations(range(1, n), 3):
        word = two.get(targets, targets)
        require(compile_word(word, targets, table) == diagonal(targets), "formal endpoint")
        records.append([list(targets), len(word)])
    return {
        "triples": len(records), "two_calls": len(two),
        "three_calls": len(records) - len(two),
        "records_sha256": hashlib.sha256(canonical(records).encode()).hexdigest(),
        "regular_columns": len(records) * 5 * n,
    }


def scalar_interleavings(table):
    # Singular free maps and dense rank-two projectors occur in this finite check.
    count = 0
    seen_singular = False
    for p in (2, 3, 5):
        for seed in range(32):
            n = 5
            result = scalar([[int(i == j) for j in range(n)] for i in range(3)], p)
            word = (1 + seed % 20, 1 + (3 * seed + 1) % 20, 1 + (7 * seed + 2) % 20)
            for step, g in enumerate(word):
                a = [[int(i == j) for j in range(n)] for i in range(n)]
                a[0][2] = 1
                inv = [[int(i == j) for j in range(n)] for i in range(n)]
                inv[0][2] = -1
                d = [[int(i == j and i < 2) for j in range(n)] for i in range(n)]
                projector = [[sum(a[i][r] * d[r][s] * inv[s][j]
                                  for r in range(n) for s in range(n))
                              for j in range(n)] for i in range(n)]
                result = multiply(result, gate(projector, g, p), table, p)
                free = [[((i + 1) * (j + 2) + seed + step + int(i == j)) % p
                         for j in range(n)] for i in range(n)]
                free[4] = free[3][:]
                seen_singular = True
                result = multiply(result, scalar(free, p), table, p)
            result = multiply(result, scalar([[int(i == j) for j in range(3)]
                                              for i in range(n)], p), table, p)
            actual = {g for row in result for poly in row for g in poly}
            require(actual <= set(cover(word, table)), "free map added support")
            count += 1
    require(seen_singular, "singular free map control")
    return count


def rank(matrix, p):
    rows = [[x % p for x in row] for row in matrix]
    pivot = 0
    for col in range(len(rows[0])):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        inverse = pow(rows[pivot][col], -1, p)
        rows[pivot] = [(x * inverse) % p for x in rows[pivot]]
        for i in range(len(rows)):
            if i != pivot:
                factor = rows[i][col]
                rows[i] = [(x - factor*y) % p for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def rank_cuts(table):
    cases = 0
    for p in (2, 3, 5):
        require(rank([[1, 0, 0], [0, 0, 0], [0, 0, 1]], p) == 2,
                "target cut rank")
        for seed in range(32):
            n = 5
            c0 = [[(i+j+seed+int(i == j)) % p for j in range(n)] for i in range(3)]
            c1 = [[(i*j+seed+int(i == j)) % p for j in range(n)] for i in range(n)]
            c1[4] = c1[3][:]
            c2 = [[(i+2*j+seed+int(i == j)) % p for j in range(3)] for i in range(n)]
            projectors = []
            for width in (1 + seed % 2, 1 + (seed // 2) % 2):
                matrix = [[int(i == j and i < width) for j in range(n)] for i in range(n)]
                matrix[0][4] = -1
                projectors.append(matrix)
            left, middle, right = scalar(c0, p), scalar(c1, p), scalar(c2, p)
            result = left
            for factor in (gate(projectors[0], 1, p), middle, gate(projectors[1], 2, p), right):
                result = multiply(result, factor, table, p)
            for label, factors, projector in (
                (1, (left, scalar(projectors[0], p), middle, right), projectors[0]),
                (2, (left, middle, scalar(projectors[1], p), right), projectors[1]),
            ):
                cut = [[(poly.get(label, 0) + poly.get(3, 0)) % p for poly in row] for row in result]
                direct = factors[0]
                for factor in factors[1:]:
                    direct = multiply(direct, factor, table, p)
                require(cut == [[poly.get(0, 0) for poly in row] for row in direct], "coefficient cut")
                require(rank(cut, p) <= rank(projector, p), "rank cut")
            cases += 1
    return cases


def compute():
    tables = groups()
    for table in tables.values():
        check_group(table)
    summaries = {name: classify(table) for name, table in tables.items()}
    table = tables["C7:C3"]
    target = (3, 6, 12)
    require(all(set(target) - set(cover((g, h), table))
                for g, h in itertools.product(range(1, 21), repeat=2)), "actual two-call exclusion")
    require(compile_word(target, target, table, 2) == diagonal(target + (0, 0)), "dirty return")
    q8 = tables["Q8"]
    require(compile_word((1, 2), (1, 2, 3), q8) == diagonal((1, 2, 3)), "Q8 rank-two control")
    # Reuse the same diagonal projectors to test noncommuting gate order.
    n1 = [[int(i == j and i in (0, 2)) for j in range(3)] for i in range(3)]
    n2 = [[int(i == j and i in (1, 2)) for j in range(3)] for i in range(3)]
    require(multiply(gate(n2, 2), gate(n1, 1), q8) == diagonal((1, 2, 7)), "Q8 reversed order")
    require(7 != 3 and clean({7: 1, 3: 1}, 2), "group sign is not scalar sign")
    require(compile_word(target[:-1], target[:-1] + (0,), table) != diagonal(target), "deleted gate")
    require(compile_word((3, 6, 15), (3, 6, 15), table) != diagonal(target), "wrong label")
    require(diagonal(target + (0, 3)) != diagonal(target + (0, 0)), "dirty mutation")
    try:
        compile_word((3, 6), target, table)
    except ValueError as error:
        require(str(error) == "uncovered target", "wrong rejection")
    else:
        raise ValueError("uncovered compiler accepted")
    try:
        gate([[0, 1], [0, 0]], 3)
    except ValueError as error:
        require(str(error) == "idempotent", "wrong gate rejection")
    else:
        raise ValueError("nilpotent projector accepted")
    # The natural seven-point action loses this nonzero formal coefficient.
    alias = {3 * i: 1 for i in range(7)} | {3 * i + 1: -1 for i in range(7)}
    natural = [[sum(c for label, c in alias.items()
                    if (pow(2, label % 3) * x + label // 3) % 7 == y)
                for x in range(7)] for y in range(7)]
    require(len(alias) == 14 and not any(map(any, natural)), "natural alias")
    require(all(clean(alias, p) for p in (2, 3, 5)), "regular alias control")
    cover_checks = 0
    for word in itertools.product(range(1, 7), repeat=3):
        labels = tuple(sorted(cover(word, tables["C7"])))
        require(compile_word(word, labels, tables["C7"]) == diagonal(labels), "full cover")
        cover_checks += 1
    require(compile_word((), (0, 0), table) == diagonal((0, 0)), "empty cover")
    require(compile_word((3,), (3, 3, 0), table, 2) == diagonal((3, 3, 0, 0, 0)), "repeated target")
    return {
        "schema": "group-subproduct-cover/1", "groups": summaries,
        "source_inputs": sources(), "rank_cut_cases": rank_cuts(tables["Q8"]),
        "rank_one_triple_minimum": 3, "two_call_projector_rank_floor": 2, "integer_formal_endpoints": sum(x["triples"] for x in summaries.values()),
        "full_cover_constructions": cover_checks, "scalar_interleavings": scalar_interleavings(table),
        "controls": ["dirty_return", "Q8_rank_two", "Q8_reversed_order",
                     "group_sign", "deleted_gate", "changed_label", "dirty_mutation",
                     "uncovered_target", "non_idempotent", "natural_alias",
                     "empty_cover", "repeated_target"], "actual_order21_minimum": 3, "q8_relaxed_minimum": 2,
        "scope": "Written all-field/all-group cover proof; finite replay corroborates it; no new kappa",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = compute()
    if args.write_receipt:
        with (HERE / "RESULT.json").open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        require(canonical(result) == canonical(expected), "receipt mismatch")
    print(f"PASS_GROUP_SUBPRODUCT_COVER triples={result['integer_formal_endpoints']} "
          f"order21_min={result['actual_order21_minimum']} "
          f"q8_relaxed_min={result['q8_relaxed_minimum']} "
          f"controls={len(result['controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
