#!/usr/bin/env python3
"""Separate free-associative right-covector check; no forward interpreter import."""

import gzip
import hashlib
import io
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(condition, message):
    if not condition:
        raise ValueError(message)


def append_letter(word, operator):
    result = word + (operator,)
    check(len(result) <= 256, "backward word bound")
    return result


def reverse_row(gates, output, dual):
    """Pull one output covector backwards, multiplying operators on the right."""
    check(len(gates) <= 6000, "backward gate bound")
    covector = {output: {(): Fraction(1)}}
    peak = 1
    for raw in reversed(gates):
        kind, target = raw[:2]
        if kind == "add":
            source, coefficient = raw[2], Fraction(raw[3], raw[4])
            if dual:
                target, source, coefficient = source, target, -coefficient
            if target in covector:
                terms = covector.setdefault(source, {})
                for word, value in covector[target].items():
                    total = terms.get(word, 0) + coefficient * value
                    if total:
                        terms[word] = total
                    else:
                        terms.pop(word, None)
                if not terms:
                    del covector[source]
        elif kind == "scale":
            coefficient = Fraction(raw[3], raw[2]) if dual else Fraction(raw[2], raw[3])
            if target in covector:
                covector[target] = {w: coefficient * c for w, c in covector[target].items()}
        elif kind == "warp":
            if target in covector:
                # In dual mode the alphabet denotes independent K_i^(-T) operators.
                covector[target] = {append_letter(w, raw[2]): c
                                   for w, c in covector[target].items()}
        else:
            raise ValueError("backward unknown gate")
        check(len(covector) <= 800, "backward register bound")
        touched = (target, source) if kind == "add" else (target,)
        for register in touched:
            polynomial = covector.get(register, {})
            check(len(polynomial) <= 4096, "backward polynomial bound")
            check(all(abs(c.numerator).bit_length() <= 4096 and c.denominator.bit_length() <= 4096
                      for c in polynomial.values()), "backward coefficient bound")
        peak = max(peak, len(covector))
    return covector, peak


def transposed_program(gates, dual):
    """Reverse order and transpose each gate, with an independent transpose alphabet."""
    check(len(gates) <= 6000, "transpose gate bound")
    result = []
    for raw in reversed(gates):
        gate = list(raw)
        if gate[0] == "add":
            if dual:
                gate[3] = -gate[3]
            else:
                gate[1], gate[2] = gate[2], gate[1]
        elif gate[0] == "scale" and dual:
            gate[2], gate[3] = gate[3], gate[2]
        result.append(gate)
    return result


def load_entries():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    entries = [entry for entry in manifest["files"] if entry["usage"] == "input"]
    check(len(entries) == 2, "backward provider count")
    return entries


def load_source(entry):
    path = ROOT / entry["path"]
    check(path.stat().st_size <= 4_000_000, "backward source capacity")
    raw = path.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == entry["sha256"], "backward source hash")
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        data = stream.read(4_000_001)
    check(len(data) <= 4_000_000, "backward payload capacity")
    word = json.loads(data)
    check(word["report"]["v"] == 112 and word["report"]["R"] == 480, "backward geometry")
    check(len(word["cleanup"]) == 5207, "backward cleanup length")
    return word


def audit():
    cases = []
    for entry in load_entries():
        word = load_source(entry)
        private = sorted(int(r) + 704 for r in word["helper_final"])
        check(len(private) == len(set(private)) == 91, "backward private count")
        for dual in (False, True):
            peak = 1
            columns = transposed_program(word["cleanup"], dual)
            for register in private:
                row, size = reverse_row(word["cleanup"], register, dual)
                check(row == {register: {(): Fraction(1)}}, "backward private row failed")
                column, column_size = reverse_row(columns, register, False)
                check(column == {register: {(): Fraction(1)}}, "backward private column failed")
                peak = max(peak, size, column_size)
            cases.append({"input": entry["path"], "dual": dual, "private_rows": 91,
                          "private_columns": 91, "peak_covector_registers": peak})
    return {"status": "PASS_RANK7_CLEANUP_BACKWARD", "cases": cases}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = audit()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        check(result == json.loads((HERE / "BACKWARD.json").read_text()), "backward receipt mismatch")
        print("PASS_RANK7_CLEANUP_BACKWARD private_covectors=728 rows_and_columns right_operator_multiplication")
