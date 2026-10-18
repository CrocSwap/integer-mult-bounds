#!/usr/bin/env python3
"""Exact four-shear alphabet classification and complete exceptional census.

Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
Standard library only. Default replay is read-only; --record writes EVIDENCE.json.
"""
import argparse
from collections import Counter
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent

TARGET = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
TRANSFERS = ((0, 1, 1), (0, 1, -1), (1, 0, 1), (1, 0, -1))
ROWS = tuple(product((-1, 0, 1), repeat=3))
ROW_INDEX = {row: i for i, row in enumerate(ROWS)}
ZERO_MONOMIAL = (0, 0, 0, 0)
ONE = {ZERO_MONOMIAL: 1}
VARIABLES = [{tuple(int(i == j) for j in range(4)): 1} for i in range(4)]


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def add(a, b):
    result = dict(a)
    for monomial, value in b.items():
        result[monomial] = result.get(monomial, 0) + value
        if not result[monomial]:
            del result[monomial]
    return result


def scale(a, scalar):
    return {monomial: scalar * value for monomial, value in a.items() if scalar * value}


def multiply(a, b):
    result = {}
    for u, x in a.items():
        for v, y in b.items():
            monomial = tuple(i + j for i, j in zip(u, v))
            result[monomial] = result.get(monomial, 0) + x * y
    return {monomial: value for monomial, value in result.items() if value}


def polynomial_identity(n):
    return [[dict(ONE) if i == j else {} for j in range(n)] for i in range(n)]


def shear(matrix, destination, source, coefficient):
    matrix[destination] = [add(x, multiply(coefficient, y))
                           for x, y in zip(matrix[destination], matrix[source])]


def symbolic_root_shapes():
    """Check the polynomial identities used in the unbounded written reduction."""
    result = Counter()
    for directions in product((0, 1), repeat=4):
        matrix = polynomial_identity(2)
        for direction, coefficient in zip(directions, VARIABLES):
            shear(matrix, direction, 1 - direction, coefficient)
        count = directions.count(0)
        if count in (0, 4):
            result["one_way_shapes"] += 1
        elif count in (1, 3):
            exceptional = 0 if count == 1 else 1
            lone = directions.index(exceptional)
            need(matrix[exceptional][1 - exceptional] == VARIABLES[lone],
                 "three-one shape does not expose its lone nonzero shear")
            result["three_one_impossible_shapes"] += 1
        elif directions[0] != directions[1] and directions[1] != directions[2]:
            d = directions[0]
            need(matrix[d][d] == add(ONE, multiply(VARIABLES[1], VARIABLES[2])),
                 "alternating shape diagonal differs from 1+bc")
            result["alternating_impossible_shapes"] += 1
        else:
            # In every remaining shape each direction occurs twice; the two
            # coefficients in each direction must be opposite (written proof).
            first = {}
            restored = polynomial_identity(2)
            for direction in directions:
                if direction not in first:
                    first[direction] = VARIABLES[direction]
                    coefficient = first[direction]
                else:
                    coefficient = scale(first[direction], -1)
                shear(restored, direction, 1 - direction, coefficient)
            need(restored == polynomial_identity(2), "inverse excursion does not close")
            result["inverse_excursion_shapes"] += 1
    # Cross-port source/read equality is an equality up to an ordinary +/- sign.
    exceptional_pairs = set()
    for sign in (-1, 1):
        # (1,-b) = sign*(-a,1) gives a=b=-sign.
        a = b = -sign
        need((1, -b) == tuple(sign * x for x in (-a, 1)), "source switch equation")
        exceptional_pairs.add((a, b))
        # (1,a) = sign*(b,1) gives a=b=sign.
        a = b = sign
        need((1, a) == tuple(sign * x for x in (b, 1)), "reader switch equation")
        exceptional_pairs.add((a, b))
    return {**dict(sorted(result.items())), "cross_port_coefficient_pairs": sorted(exceptional_pairs)}


def interleave(groups):
    if not any(groups):
        yield ()
        return
    for i, group in enumerate(groups):
        if group:
            rest = groups[:i] + (group[1:],) + groups[i + 1:]
            for suffix in interleave(rest):
                yield (group[0],) + suffix


def symbolic_no_cross():
    """All same-port B/A placements, with indeterminate nonzero a and b.

    The proof shows that same-port cancellation has no exceptional nonzero
    coefficient stratum; these polynomial checks do not sample coefficients.
    """
    a, b = VARIABLES[:2]
    passes = ((0, 1, a), (0, 1, scale(a, -1)),
              (1, 0, b), (1, 0, scale(b, -1)))
    receipt = []
    for source_port, reader_port in ((0, 1), (1, 0)):
        counts = Counter()
        for events in interleave((("B+", "B-"), ("A+", "A-"), (0, 1, 2, 3))):
            # Rows: z,w,x,y. A=B=identity suffices for the scalar coefficient.
            matrix = polynomial_identity(4)
            for event in events:
                if isinstance(event, int):
                    d, s, coefficient = passes[event]
                    shear(matrix, d, s, coefficient)
                elif event[0] == "B":
                    shear(matrix, source_port, 2, scale(ONE, 1 if event[1] == "+" else -1))
                else:
                    shear(matrix, 3, reader_port, scale(ONE, 1 if event[1] == "+" else -1))
            restored_source = not matrix[0][2] and not matrix[1][2]
            clean_reader = not matrix[3][0] and not matrix[3][1]
            nonzero = bool(matrix[3][2])
            counts["placements"] += 1
            counts["admitted"] += restored_source and clean_reader
            counts["nonzero_admitted"] += restored_source and clean_reader and nonzero
            counts["nonzero_without_source_restoration"] += clean_reader and nonzero
            counts["nonzero_without_reader_dirt"] += restored_source and nonzero
        need(counts["placements"] == 420 and counts["nonzero_admitted"] == 0,
             "same-port polynomial cross coefficient survives")
        need(counts["nonzero_without_source_restoration"] > 0 and
             counts["nonzero_without_reader_dirt"] > 0, "restoration controls are insensitive")
        receipt.append({"source_port": source_port, "reader_port": reader_port, **dict(counts)})
    return receipt


def reader_mask(history):
    groups = {}
    for snapshot in history:
        for row in snapshot:
            dirty = row[:2]
            negative = tuple(-x for x in dirty)
            canonical = min(dirty, negative)
            sign = 1 if canonical == dirty else -1
            groups.setdefault(canonical, set()).add(tuple(sign * x for x in row[2:]))
    available = 0
    for values in groups.values():
        for left in values:
            for right in values:
                difference = tuple(b - a for a, b in zip(left, right))
                if difference in ROW_INDEX:
                    available |= 1 << ROW_INDEX[difference]
    return available


def chronological_census():
    """Chronological integer row propagation, retaining every closing port."""
    matrices = [((1, 0), (0, 1))]
    for destination, source, coefficient in TRANSFERS:
        matrix = list(matrices[-1])
        matrix[destination] = tuple(x + coefficient * y
                                    for x, y in zip(matrix[destination], matrix[source]))
        matrices.append(tuple(matrix))
    columns = [((g[1][1], -g[1][0]), (-g[0][1], g[0][0])) for g in matrices]
    initial = ((1, 0, 0, 0, 0), (0, 1, 0, 0, 0))
    records = {}

    def visit(stage, counts, starts, rows, history, word):
        if stage == 4 and counts == (2, 2, 2):
            need(rows == initial, "normalized source pairs failed literal restoration")
            need(word not in records, "chronological duplicate")
            records[word] = reader_mask(history)
            return
        if stage < 4:
            d, s, a = TRANSFERS[stage]
            next_rows = list(rows)
            next_rows[d] = tuple(x + a * y for x, y in zip(rows[d], rows[s]))
            next_rows = tuple(next_rows)
            visit(stage + 1, counts, starts, next_rows, history + (next_rows,),
                  word + (("T", d, s, a),))
        for j, count in enumerate(counts):
            if count == 2:
                continue
            for port in (0, 1):
                if count == 0:
                    sign = 1
                    next_starts = list(starts)
                    next_starts[j] = columns[stage][port]
                    next_starts = tuple(next_starts)
                else:
                    if columns[stage][port] == starts[j]:
                        sign = -1
                    elif columns[stage][port] == tuple(-x for x in starts[j]):
                        sign = 1
                    else:
                        continue
                    next_starts = starts
                next_rows = list(rows)
                changed = list(next_rows[port])
                changed[j + 2] += sign
                next_rows[port] = tuple(changed)
                next_rows = tuple(next_rows)
                next_counts = list(counts)
                next_counts[j] += 1
                visit(stage, tuple(next_counts), next_starts, next_rows,
                      history + (next_rows,), word + (("B", j, sign, port),))

    visit(0, (0, 0, 0), (None, None, None), initial, (initial,), ())
    return records


def summarize(records):
    histogram = [0] * 8
    switch_traces = 0
    all_ones = 0
    h = hashlib.sha256()
    for word, available in sorted(records.items()):
        h.update(encoded([word, available]) + b"\n")
        ports = [[event[3] for event in word if event[0] == "B" and event[1] == j]
                 for j in range(3)]
        switch_traces += any(a != b for a, b in ports)
        for signs in product((-1, 1), repeat=3):
            transformed = [tuple(row[j] * signs[j] for j in range(3)) for row in TARGET]
            row_bits = sum(1 << i for i, row in enumerate(transformed)
                           if available & (1 << ROW_INDEX[row]))
            histogram[row_bits] += 1
            all_ones += bool(available & (1 << ROW_INDEX[signs]))
    need(len(records) == 69948, "exceptional complete source-trace count changed")
    need(histogram[7] == 0 and all_ones > 0 and switch_traces > 0,
         "exceptional target exclusion or positive controls failed")
    return {"canonical_source_traces": len(records), "signed_source_traces": 8 * len(records),
            "source_port_switch_traces": switch_traces,
            "target_row_availability_histogram": histogram, "target_successes": histogram[7],
            "all_ones_target_successes": all_ones, "all_reader_masks_sha256": h.hexdigest()}


def one_root_control():
    histogram = [0] * 8
    for word in permutations(tuple(product(range(3), (-1, 1)))):
        state = [0, 0, 0]
        vertices = [tuple(state)]
        for j, sign in word:
            state[j] += sign
            vertices.append(tuple(state))
        differences = {tuple(b - a for a, b in zip(left, right))
                       for left in vertices for right in vertices}
        histogram[sum(1 << i for i, row in enumerate(TARGET) if row in differences)] += 1
    need(histogram == [72, 84, 84, 48, 264, 84, 84, 0], "inherited one-root control")
    return histogram


def inverse(word):
    return tuple((kind, a, b, -c) if kind == "T" else (kind, a, -b, c)
                 for kind, a, b, c in reversed(word))


def formal(word):
    # Eight independent arbitrary initial rows; monomials are noncommutative.
    rows = [{((), i): 1} for i in range(8)]
    for kind, a, b, c in word:
        if kind == "T":
            destination, source, coefficient, letter = 6 + a, 6 + b, c, None
        elif kind == "B":
            destination, source, coefficient, letter = 6 + c, a, b, "B" + str(a)
        elif kind == "A":
            destination, source, coefficient, letter = 3 + a, 6 + c, b, "A" + str(a)
        else:
            raise RuntimeError("unknown formal operation")
        need(destination != source and coefficient != 0, "illegal operation")
        for (monomial, origin), value in list(rows[source].items()):
            key = ((letter,) + monomial if letter else monomial, origin)
            total = rows[destination].get(key, 0) + coefficient * value
            if total:
                rows[destination][key] = total
            else:
                rows[destination].pop(key, None)
    return rows


def expected(target):
    result = formal(())
    for i in range(3):
        for j in range(3):
            if target[i][j]:
                result[3 + i][(("A" + str(i), "B" + str(j)), j)] = target[i][j]
    return result


def dense_control(word, target, n):
    """Separate integer block-array propagation of all 8*n input columns."""
    maps = {}
    for i in range(3):
        maps["A" + str(i)] = [[((2 * r + c + i) % 3) - 1 for c in range(n)] for r in range(n)]
        maps["B" + str(i)] = [[int(c == (r + i + 1) % n) for c in range(n)] for r in range(n)]
    maps["A0"][-1] = [0] * n  # Include a singular map.
    def matmul(a, b):
        return [[sum(a[r][k] * b[k][c] for k in range(n)) for c in range(n)] for r in range(n)]
    need(matmul(maps["A0"], maps["B0"]) != matmul(maps["B0"], maps["A0"]),
         "dense fixture accidentally commutes")
    size = 8 * n
    rows = [[int(i == j) for j in range(size)] for i in range(size)]
    for kind, a, b, c in word:
        if kind == "T":
            dst, src, sign = 6 + a, 6 + b, c
            matrix = [[int(i == j) for j in range(n)] for i in range(n)]
        else:
            dst, src = (6 + c, a) if kind == "B" else (3 + a, 6 + c)
            sign, matrix = b, maps[kind + str(a)]
        updates = [[sum(matrix[r][k] * rows[src * n + k][column] for k in range(n))
                    for column in range(size)] for r in range(n)]
        for r in range(n):
            rows[dst * n + r] = [x + sign * y for x, y in zip(rows[dst * n + r], updates[r])]
    wanted = [[int(i == j) for j in range(size)] for i in range(size)]
    for i in range(3):
        for j in range(3):
            block = matmul(maps["A" + str(i)], maps["B" + str(j)])
            for r in range(n):
                for c in range(n):
                    wanted[(3 + i) * n + r][j * n + c] += target[i][j] * block[r][c]
    need(rows == wanted, "dense dirty-input endpoint differs")
    return size


def semantic_controls(source_root):
    certificate = json.loads((source_root / "research/signed-connector-transfer-minimum/CERTIFICATE.json").read_text())
    word = tuple(("T", 0, 1, coefficient * sign) if kind == "R" else (kind, coefficient, sign, port)
                 for kind, coefficient, sign, port in certificate["word"])
    goal = expected(TARGET)
    need(formal(word) == goal, "credited one-way witness endpoint")
    need(formal(word + inverse(word)) == formal(()), "full inverse restoration")
    for cut in range(len(word)):
        need(formal(word[cut:] + word[:cut]) == goal, "cyclic rotation did not preserve central endpoint")
    failures = 0
    for index, event in enumerate(word):
        if event[0] == "T":
            need(formal(word[:index] + word[index + 1:]) != goal, "omitted shear escaped")
            failures += 1
    # Genuine exceptional port switches. These are legal AB pilots, not M.
    source_switch = (("A", 0, 1, 0), ("T", 0, 1, 1), ("B", 0, 1, 1),
                     ("T", 0, 1, -1), ("A", 0, -1, 0), ("T", 1, 0, 1),
                     ("B", 0, 1, 0), ("T", 1, 0, -1))
    reader_switch = (("T", 0, 1, 1), ("A", 0, -1, 0), ("T", 0, 1, -1),
                     ("B", 0, 1, 0), ("T", 1, 0, 1), ("A", 0, 1, 1),
                     ("T", 1, 0, -1), ("B", 0, -1, 0))
    small = ((1, 0, 0), (0, 0, 0), (0, 0, 0))
    for pilot in (source_switch, reader_switch):
        need(formal(pilot) == expected(small), "legal cross-port pilot rejected")
        need(formal(pilot + inverse(pilot)) == formal(()), "pilot inverse")
    need(source_switch[2][3] != source_switch[6][3], "source switch lost")
    need(reader_switch[1][3] != reader_switch[5][3], "reader switch lost")
    broken_source = source_switch[:6] + (("B", 0, -1, 0),) + source_switch[7:]
    need(formal(broken_source) != expected(small), "source restoration mutation escaped")
    dirty_alias = (("A", 0, -1, 0), ("B", 0, 1, 1), ("A", 0, 1, 1), ("B", 0, -1, 1))
    invalid = formal(dirty_alias)
    need(invalid != expected(small), "independent dirty roots were identified")
    # Dropping root-dirt monomials makes the invalid shortcut appear correct.
    erased = [{key: value for key, value in row.items() if not (i == 3 and key[1] in (6, 7))}
              for i, row in enumerate(invalid)]
    need(erased == expected(small), "dirty-alias control does not isolate the intended bug")
    dense_columns = sum(dense_control(program, target, n) for n in (2, 3)
                        for program, target in ((word, TARGET), (source_switch, small), (reader_switch, small)))
    return {"credited_one_way_queries": 12, "credited_one_way_transfers": 4,
            "cyclic_rotations": len(word), "omitted_shear_failures": failures,
            "valid_source_switch": source_switch, "valid_reader_switch": reader_switch,
            "source_restoration_failure": True, "dirty_alias_failure": True,
            "dense_dirty_basis_columns": dense_columns, "formal_inverse_restoration": True}


def check_pins(source_root):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    pins = [pin for pin in manifest["files"] if pin["usage"] == "input"]
    for pin in pins:
        actual = hashlib.sha256((source_root / pin["path"]).read_bytes()).hexdigest()
        need(actual == pin["sha256"], "source pin mismatch: " + pin["path"])
    return len(pins)


def verify(source_root):
    pin_count = check_pins(source_root)
    shapes = symbolic_root_shapes()
    no_cross = symbolic_no_cross()
    primary = chronological_census()
    secondary, domain = independent.census()
    need(primary == secondary, "independent full reader-mask maps differ")
    receipt = summarize(primary)
    return {"schema_version": 1, "status": "MIXED_FOUR_SHEARS_EXCLUDED",
            "target": TARGET, "source_pins": pin_count, "symbolic_root_shapes": shapes,
            "symbolic_same_port_cross_checks": no_cross,
            "exceptional_census": {**domain, **receipt},
            "inherited_one_root_histogram": one_root_control(),
            "semantic_controls": semantic_controls(source_root), "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=HERE.parents[1])
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--pins-only", action="store_true")
    args = parser.parse_args()
    if args.pins_only:
        print("PASS_FOUR_SHEAR_SOURCE_PINS inputs=" + str(check_pins(args.source_root)))
        return
    receipt = verify(args.source_root)
    # JSON normalization makes tuple/list representation irrelevant.
    canonical = json.loads(encoded(receipt))
    if args.record:
        (HERE / "EVIDENCE.json").write_text(json.dumps(canonical, indent=2) + "\n", encoding="utf-8")
    else:
        need(canonical == json.loads((HERE / "EVIDENCE.json").read_text()), "committed evidence differs")
    print("PASS_BIDIRECTIONAL_FOUR_SHEAR_RIGIDITY canonical_traces=69948 signed_traces=559584 mixed_successes=0 symbolic_shapes=16 no_new_kappa")


if __name__ == "__main__":
    main()
