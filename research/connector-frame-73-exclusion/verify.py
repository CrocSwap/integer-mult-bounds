#!/usr/bin/env python3
"""Exact finite checks of the 73-map reduction. No predecessor code imports.

Arham Garg, with substantial OpenAI Codex assistance. Apache-2.0.
The arbitrary-dimension statement is the written proof in README.md.
"""
import json
from collections import Counter
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_unframed_word(word, sources, rows):
    # Each bit represents a distinct formal B_j x_j, plus independent z dirt.
    # An output's bits represent A_i applied to those formal expressions.
    z = 1 << sources
    outputs = [0] * len(rows)
    for kind, index in word:
        if kind == "B":
            require(0 <= index < sources, "invalid source index")
            z ^= 1 << index
        elif kind == "A":
            require(0 <= index < len(rows), "invalid output index")
            outputs[index] ^= z
        else:
            raise ValueError("unknown unframed operation")
    require(z == 1 << sources, "connector restoration failed")
    require(outputs == rows, "output map or arbitrary-dirty cancellation failed")
    return z, tuple(outputs)


def xor_matrices(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def apply(matrix, vector):
    return sum(((row & vector).bit_count() % 2) << i for i, row in enumerate(matrix))


def invertible(matrix):
    # Enumerate its kernel independently of the row arithmetic used elsewhere.
    return all(apply(matrix, v) != 0 for v in range(1, 1 << len(matrix)))


def inverse(matrix, group):
    n = len(matrix)
    return next(b for b in group if all(apply(b, apply(matrix, 1 << i)) == 1 << i for i in range(n)))


def sum_selected(triple, bits):
    value = (0,) * len(triple[0])
    for index, matrix in enumerate(triple):
        if bits >> index & 1:
            value = xor_matrices(value, matrix)
    return value


def phase_checks(n):
    matrices = list(product(range(1 << n), repeat=n))
    group = [a for a in matrices if invertible(a)]
    members = set(group)
    zero = (0,) * n
    triples = [(a, b, xor_matrices(a, b)) for a in group for b in group
               if xor_matrices(a, b) in members]
    count = 0
    for triple in triples:
        require(sum_selected(triple, 7) == zero, "tripled dirty coefficient")
        require(len(set(triple)) == 3, "nonzero phases must be distinct")
        sums = [sum_selected(triple, bits) for bits in range(8)]
        require(set(sums) == {zero, *triple}, "unexpected partial triple sum")
        for pivot, h in enumerate(triple):
            other = [k for k in range(3) if k != pivot]
            for bits, coefficient in enumerate(sums):
                equal = ((bits >> other[0]) & 1) == ((bits >> other[1]) & 1)
                require((coefficient in (zero, h)) == equal, "companion equality reduction")
                if equal:
                    bit = ((bits >> pivot) ^ (bits >> other[0])) & 1
                    require(coefficient == (h if bit else zero), "collapsed binary coefficient")
                count += 1
    require(len(group) == prod((1 << n) - (1 << k) for k in range(n)), "incomplete GL census")
    return group, triples, {"dimension": n, "invertible_matrices": len(group),
                            "ordered_zero_sum_triples": len(triples), "subset_checks": count}


def dense_coefficients(group, triples):
    matrices = list(product(range(4), repeat=2))
    count = 0
    for triple in triples:
        for h in triple:
            inv = inverse(h, group)
            for bits in range(8):
                coefficient = sum_selected(triple, bits)
                if coefficient not in ((0, 0), h):
                    continue
                active = coefficient == h
                for a, b in product(matrices, repeat=2):
                    for x in range(4):
                        bx = apply(b, x)
                        expected = apply(a, bx) if active else 0
                        readout = insertion = 0
                        for k, phase in enumerate(triple):
                            if bits >> k & 1:
                                readout ^= apply(a, apply(phase, apply(inv, bx)))
                                insertion ^= apply(a, apply(inv, apply(phase, bx)))
                        require(readout == expected, "triple-readout dense coefficient")
                        require(insertion == expected, "triple-source dense coefficient")
                        count += 2
    return count


def paired_words(n):
    """Restricted-growth recursion: open the next label, or close an open one."""
    def visit(word, opened, active):
        if len(word) == 2 * n:
            yield tuple(word)
            return
        if opened < n:
            yield from visit(word + [opened], opened + 1, active + (opened,))
        for label in active:
            yield from visit(word + [label], opened, tuple(x for x in active if x != label))
    yield from visit([], 0, ())


def prefixes(word):
    result = [0]
    for label in word:
        result.append(result[-1] ^ (1 << label))
    return result


def differences(values):
    return {a ^ b for a in values for b in values}


def pairing_census(certificate):
    words = list(paired_words(5))
    require(len(words) == len(set(words)) == prod(range(1, 10, 2)), "incomplete pairing domain")
    entries = sorted((list(w), sum(1 << x for x in differences(prefixes(w)))) for w in words)
    histogram = Counter(mask.bit_count() for _, mask in entries)
    receipt = {"sources": 5, "pairings": len(words),
               "histogram": {str(k): v for k, v in sorted(histogram.items())},
               "canonical_entries_sha256": sha256(json.dumps(entries, separators=(",", ":")).encode()).hexdigest(),
               "max_coverage": max(histogram)}
    pinned = next(x for x in certificate["censuses"] if x["sources"] == 5)
    require(receipt == pinned, "independent census differs from pinned predecessor")
    require(max(histogram) < 32, "five-source obstruction failed")
    return words, receipt


def check_phase_locking():
    checks = 0
    # Deleting any one exceptional output still couples every pair of sources.
    for omitted in range(1, 32):
        for j, k in combinations(range(5), 2):
            require(any(m != omitted and m >> j & 1 and m >> k & 1 for m in range(1, 32)),
                    "paired output does not lock source phases")
            checks += 1
    # With one tripled source, all four ordinary sources are coupled.
    for exceptional in range(5):
        for j, k in combinations([i for i in range(5) if i != exceptional], 2):
            require(any(m >> j & 1 and m >> k & 1 for m in range(1, 32)), "regular phase lock")
            checks += 1
    return checks


def triple_readouts(words):
    trials = accepted = 0
    for word in words:
        q = prefixes(word)
        ordinary = differences(q)
        for slots in combinations_with_replacement(range(len(q)), 3):
            for pivot in range(3):
                # 1,2,3 encode I,U,I+U in their two-dimensional F2 span.
                phases = [0, 0, 0]
                phases[pivot] = 1
                other = [k for k in range(3) if k != pivot]
                phases[other[0]], phases[other[1]] = 2, 3
                mask = 0
                legal = True
                for source in range(5):
                    coefficient = 0
                    for phase, slot in zip(phases, slots):
                        if q[slot] >> source & 1:
                            coefficient ^= phase
                    if coefficient not in (0, 1):
                        legal = False
                        break
                    mask |= coefficient << source
                if legal:
                    require(mask in ordinary, "third readout adds a new mask")
                    accepted += 1
                trials += 1
    return {"trials": trials, "scalar_mask_triples": accepted, "new_masks": 0}


def triple_sources():
    trials = maximum = 0
    wrong_deletion_witness = None
    for positions in combinations(range(11), 3):
        for paired in paired_words(4):
            remaining = iter(paired)
            word = [-1 if i in positions else next(remaining) + 1 for i in range(11)]
            for pivot in range(3):
                other = [k for k in range(3) if k != pivot]
                weights = {positions[pivot]: 1, positions[other[0]]: 2, positions[other[1]]: 3}
                values = [0]
                for i, label in enumerate(word):
                    values.append(values[-1] ^ (weights[i] if label == -1 else 1 << (label + 1)))
                require(values[-1] == 0, "triple-source restoration")
                masks = {((d >> 2) << 1) | (d & 3) for d in differences(values) if d & 3 in (0, 1)}
                projected = [max(0, label) for i, label in enumerate(word) if i != positions[other[1]]]
                cover = differences(prefixes(projected))
                # The exceptional singleton may use its own output phase.
                require(masks | {1} <= cover, "collapsed source word lost a requested mask")
                require(len(cover) < 32, "collapsed pairing covers all masks")
                maximum = max(maximum, len(masks | {1}))
                if wrong_deletion_witness is None:
                    wrong = [max(0, label) for i, label in enumerate(word) if i != positions[pivot]]
                    lost = (masks | {1}) - differences(prefixes(wrong))
                    if lost:
                        mask = min(lost)
                        encoded = ((mask >> 1) << 2) | (mask & 1)
                        interval = next((i, j) for i in range(12) for j in range(i, 12)
                                        if values[i] ^ values[j] == encoded)
                        wrong_deletion_witness = {
                            "source_word": [max(0, label) for label in word],
                            "distinguished_occurrence": pivot,
                            "wrong_deleted_position": positions[pivot],
                            "lost_mask": mask, "readout_boundaries": interval,
                        }
                trials += 1
    require(trials == 3 * 165 * 105, "incomplete triple-source domain")
    require(wrong_deletion_witness is not None, "wrong-event deletion control not detected")
    return {"annotated_source_words": trials, "max_coverage_with_singleton": maximum,
            "wrong_event_deletion_counterexample": wrong_deletion_witness}


def odd_restoration_control():
    t = (2, 3)
    cases = erasure_failures = 0
    for b in product(range(4), repeat=2):
        for x, dirty in product(range(4), repeat=2):
            z = dirty
            for _ in range(3):
                z ^= apply(b, x)
                z = apply(t, z)
            require(z == dirty, "odd-count restoration positive control")
            erased = dirty
            for _ in range(3):
                erased ^= apply(b, x)
            erasure_failures += erased != dirty
            cases += 1
    # Erasing these frames is invalid, unlike the proven 73-map reductions.
    require(erasure_failures > 0, "false general frame-erasure rule was not detected")
    return {"restored_cases": cases, "unframed_failures": erasure_failures}


def dense_positive(word):
    def replay(operations, initial, a, b):
        state = initial.copy()
        for kind, index in operations:
            if kind == "B":
                state[-1] ^= apply(b[index], state[index])
            else:
                state[5 + index] ^= apply(a[index], state[-1])
        return state

    cases = 0
    for n in (1, 2, 3):
        matrices = list(product(range(1 << n), repeat=n))
        a = [matrices[(i * 7 + 3) % len(matrices)] for i in range(31)]
        b = [matrices[(j * 11 + 5) % len(matrices)] for j in range(5)]

        # All basis columns certify the complete finite linear map, including
        # every independent source, target and connector dirt column.
        inputs = [[(1 << (column % n)) if row == column // n else 0
                   for row in range(37)] for column in range(37 * n)]
        inputs.append([(1 << n) - 1] * 37)
        for initial in inputs:
            expected = initial.copy()
            for i, mask in enumerate(range(1, 32)):
                for j in range(5):
                    if mask >> j & 1:
                        expected[5 + i] ^= apply(a[i], apply(b[j], initial[j]))
            actual = replay(word, initial, a, b)
            require(actual == expected, "dense 74-call endpoint")
            require(replay(word[::-1], actual, a, b) == initial, "dense 74-call inverse")
            cases += 1
    return {"forward_cases": cases, "inverse_cases": cases, "dimensions": [1, 2, 3]}


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            require(sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "pinned source changed: " + row["path"])
    certificate = json.loads((HERE.parent / "universal-connector-boundary/CERTIFICATE.json").read_text())
    positive = certificate["schedules"]["five_extra_output"]
    check_unframed_word(positive["word"], 5, list(range(1, 32)))
    require(len(positive["word"]) == 74, "attaining construction is not 74 calls")
    words, pairing = pairing_census(certificate)
    g2, t2, phase2 = phase_checks(2)
    _, _, phase3 = phase_checks(3)
    report = {"status": "PASS_CONNECTOR_FRAME_73_EXCLUSION", "pairings": pairing,
              "phase_censuses": [phase2, phase3], "dense_coefficients": dense_coefficients(g2, t2),
              "phase_lock_checks": check_phase_locking(), "triple_readouts": triple_readouts(words),
              "triple_sources": triple_sources(), "odd_restoration": odd_restoration_control(),
              "dense_positive": dense_positive(positive["word"]),
              "attaining_map_calls": len(positive["word"]),
              "scope": "Finite checks support the written generic one-connector proof. No supplier admission or new kappa."}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
