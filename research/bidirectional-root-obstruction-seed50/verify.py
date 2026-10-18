#!/usr/bin/env python3
"""Exact evidence for the short elementary-root monodromy obstruction.
Cinna Davis (1337isnot1337), substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def root_census(n):
    coefficients = (-2, -1, 1, 2)
    identity = tuple(tuple(int(i == j) for j in range(n)) for i in range(n))
    gates = [(d, s, a) for d in range(n) for s in range(n) if d != s for a in coefficients]

    def update(matrix, gate):
        d, s, a = gate
        return tuple(tuple(x + a * y for x, y in zip(matrix[d], matrix[s])) if i == d else row
                     for i, row in enumerate(matrix))

    closed = {"1": 0, "2": 0, "3": 0}
    for g1 in gates:
        p1 = update(identity, g1)
        closed["1"] += p1 == identity
        for g2 in gates:
            p2 = update(p1, g2)
            closed["2"] += p2 == identity
            for g3 in gates:
                p3 = update(p2, g3)
                if p3 == identity:
                    need(g1[:2] == g2[:2] == g3[:2], "closed mixed short loop")
                    closed["3"] += 1
    need(closed == independent.closed_counts(n, coefficients), "independent monodromy counts")
    # Two nonzero inverse excursions form a mixed closed four-transfer loop.
    mixed = [(0, 1, 1), (0, 1, -1), (1, 0, 1), (1, 0, -1)]
    matrix = identity
    for g in mixed:
        matrix = update(matrix, g)
    need(matrix == identity, "four-transfer limit control")
    four = independent.four_root_counts(coefficients) if n == 2 else None
    signed_swap = [(0, 1, 1), (1, 0, -1), (0, 1, 1)]
    matrix = identity
    for g in signed_swap:
        matrix = update(matrix, g)
    need(matrix != identity and all(sum(abs(x) for x in row) == 1 for row in matrix),
         "signed permutation must not count as dirty restoration")
    return {"roots": n, "coefficient_domain": list(coefficients),
            "words_by_length": {str(k): len(gates) ** k for k in (1, 2, 3)}, "closed_by_length": closed,
            **({"four_transfer_control": four} if four else {})}


def interleave(groups):
    if not any(groups):
        yield ()
        return
    for i, group in enumerate(groups):
        if group:
            rest = groups[:i] + (group[1:],) + groups[i + 1:]
            for tail in interleave(rest):
                yield (group[0],) + tail


def short_lemma(heights):
    orders = admitted = nonzero = relaxed_source = relaxed_reader = 0
    for events in interleave(((("B", 1), ("B", -1)), (("A", 1), ("A", -1)),
                              tuple(("T", i) for i in range(len(heights) - 1)))):
        stage = 0
        w_signal = 0
        z_signal = (0, 0)
        output = (0, 0)
        dirty_read = (0, 0)
        for event in events:
            if event[0] == "B":
                w_signal += event[1]
            elif event[0] == "A":
                output = tuple(x + event[1] * y for x, y in zip(output, z_signal))
                dirty_read = tuple(x + event[1] * y for x, y in zip(dirty_read, heights[stage]))
            else:
                delta = tuple(b - a for a, b in zip(heights[stage], heights[stage + 1]))
                z_signal = tuple(x + w_signal * y for x, y in zip(z_signal, delta))
                stage += 1
        source_ok = w_signal == 0 and z_signal == (0, 0)
        reader_ok = dirty_read == (0, 0)
        cross = output != (0, 0)
        orders += 1
        admitted += source_ok and reader_ok
        nonzero += source_ok and reader_ok and cross
        relaxed_source += reader_ok and cross
        relaxed_reader += source_ok and cross
        values = [Fraction(2, 3) * a - Fraction(5, 7) * b for a, b in heights]
        ns, nr, nc = independent.numeric_short(events, values)
        need((ns, nr) == (source_ok, reader_ok), "numeric restoration classification")
        need(nc == Fraction(2, 3) * output[0] - Fraction(5, 7) * output[1], "numeric cross coefficient")
    return dict(event_orders=orders, admitted=admitted, nonzero_cross=nonzero,
                cross_if_source_restoration_dropped=relaxed_source,
                cross_if_reader_dirt_cancellation_dropped=relaxed_reader)


def one_root(target):
    histogram = Counter()
    moves = [(j, s) for j in range(3) for s in (-1, 1)]
    for word in itertools.permutations(moves):
        p = [0, 0, 0]
        vertices = [tuple(p)]
        for j, s in word:
            p[j] += s
            vertices.append(tuple(p))
        differences = {tuple(b[j] - a[j] for j in range(3)) for a in vertices for b in vertices}
        mask = sum(1 << i for i, row in enumerate(target) if tuple(row) in differences)
        histogram[mask] += 1
    counts = [histogram[i] for i in range(8)]
    need(counts == independent.one_root(target), "independent one-root census")
    need(counts == [72, 84, 84, 48, 264, 84, 84, 0], "inherited one-root obstruction")
    return counts


def inverse(program):
    return [(kind, f, -sign, src, dst) for kind, f, sign, src, dst in reversed(program)]


def lower(factors, src, dst, scratch):
    need(src != dst and src not in scratch and dst not in scratch, "child scratch aliases data")
    if len(factors) == 1:
        return [("F", factors[0], 1, src, dst)]
    need(bool(scratch), "child scratch insufficient")
    mid = len(factors) // 2
    a = lower(factors[:mid], src, scratch[0], scratch[1:])
    b = lower(factors[mid:], scratch[0], dst, scratch[1:])
    return a + b + inverse(a) + inverse(b)


def expand(word, factors):
    result = []
    for kind, op, sign, root in word:
        if kind == "R":
            need(root == 0, "pinned witness is one-way")
            result.append(("R", None, op * sign, 7, 6))
        else:
            src, dst = (op, 6 + root) if kind == "B" else (6 + root, 3 + op)
            child = lower(factors[kind + str(op)], src, dst, (8, 9, 10))
            result += child if sign == 1 else inverse(child)
    return result


def formal(program):
    rows = [{((), r): 1} for r in range(11)]
    for kind, f, sign, src, dst in program:
        need(src != dst, "aliased instruction")
        for (word, origin), value in list(rows[src].items()):
            key = (((f,) + word) if kind == "F" else word, origin)
            total = rows[dst].get(key, 0) + sign * value
            if total:
                rows[dst][key] = total
            else:
                rows[dst].pop(key, None)
    return rows


def witness(certificate):
    factors = {}
    next_factor = 0
    for name, length in [("B0", 2), ("B1", 3), ("B2", 4), ("A0", 5), ("A1", 6), ("A2", 7)]:
        factors[name] = tuple(range(next_factor, next_factor + length))
        next_factor += length
    word, target = certificate["word"], certificate["target"]
    program = expand(word, factors)
    normalized_source = [(kind, f if kind == "F" else None, sign if kind == "F" else f * sign, src, dst)
                         for kind, f, sign, src, dst in certificate["expanded_word"]]
    need(program == normalized_source, "literal predecessor lowering differs")
    expected = formal([])
    for i in range(3):
        for j in range(3):
            if target[i][j]:
                monomial = tuple(reversed(factors["A" + str(i)])) + tuple(reversed(factors["B" + str(j)]))
                expected[i + 3][monomial, j] = target[i][j]
    need(formal(program) == expected, "full free noncommutative identity")
    need(formal(program + inverse(program)) == formal([]), "literal inverse restores every row")
    # Each root pass is essential to this literal witness, not a global claim
    # about arbitrary words with more queries.
    root_positions = [i for i, e in enumerate(program) if e[0] == "R"]
    for i in root_positions:
        need(formal(program[:i] + program[i + 1:]) != expected, "removed pass control escaped")
    changed = list(program)
    kind, f, sign, src, dst = changed[root_positions[0]]
    changed[root_positions[0]] = (kind, f, -sign, src, dst)
    need(formal(changed) != expected, "wrong transfer sign escaped")
    dense = {str(n): digest(independent.dense(program, factors, target, n)) for n in (2, 3)}
    counts = Counter(e[0] for e in program)
    need(counts == {"F": 300, "R": 4}, "complete factor/pass bill")
    return {"queries": 12, "transfers": 4, "factor_calls": 300, "instructions": 304,
            "mutable_rows": 11, "borrowed_dirty_rows": 5, "word_sha256": digest(program),
            "restored_dirty_columns": 11, "dense_integer_receipts": dense,
            "controls": {"removed_root_passes": 4, "wrong_pass_sign": 1, "literal_inverse": 1}}


def verify():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for pin in sources["external_sources"]:
        need(hashlib.sha256((HERE / pin["local_path"]).read_bytes()).hexdigest() == pin["sha256"], "external source pin")
    certificate = json.loads((HERE / "references/PR1651-CERTIFICATE.json").read_text())
    zero, a, b = (0, 0), (1, 0), (0, 1)
    short = [short_lemma(h) for h in [(zero,), (zero, a, zero), (zero, a, b, zero)]]
    need([r["event_orders"] for r in short] == [6, 90, 210], "short event coverage")
    need([r["admitted"] for r in short] == [6, 42, 56], "short restoration coverage")
    need(all(r["nonzero_cross"] == 0 for r in short), "short cross-root obstruction")
    limit = short_lemma((zero, a, zero, a, zero))
    need(limit["nonzero_cross"] > 0, "four-pass cross-root limit control")
    need(all(short[i]["cross_if_source_restoration_dropped"] > 0 and
             short[i]["cross_if_reader_dirt_cancellation_dropped"] > 0 for i in (1, 2)), "restoration premise controls")
    return {"schema_version": 1, "base_commit": "2de86c77b4127d2f01f504e0c7c5e4db737caa3c", "assignment_seed": 50,
            "root_census": [root_census(n) for n in (2, 3, 4)], "short_transfer": short,
            "four_transfer_cross_control": limit, "one_root_histogram": one_root(certificate["target"]),
            "complete_witness": witness(certificate), "no_new_kappa": True}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-evidence", action="store_true")
    args = ap.parse_args()
    receipt = verify()
    path = HERE / "EVIDENCE.json"
    if args.write_evidence:
        path.write_text(json.dumps(receipt, indent=2) + "\n")
    else:
        need(receipt == json.loads(path.read_text()), "committed exact receipt differs")
    print("PASS_BIDIRECTIONAL_ROOT_OBSTRUCTION monodromy_words=127952 one_root_paths=720 factor_calls=300 transfers=4")


if __name__ == "__main__":
    main()
