"""Exact new-phase and literal lifecycle checks; no files are written."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adapter import PACKAGE, compile_add, need, physical_fixture


def run_phase(table, receipt, bits, parity):
    """Independent bounded interpreter, starting at the numerator delimiter."""
    tape = [6, *bits, 2]
    position, reads, moves = len(tape) - 1, 0, 0
    pc = receipt["phase_entries"][parity]
    for steps in range(3 * len(bits) + 5):
        if pc in receipt["phase_exits"]:
            key = receipt["phase_exits"][pc]
            need(position == 1, "rewound exactly to first numerator bit")
            need(key[3] == parity, "component parity retained")
            return -key[2], reads, moves, steps
        row = table[pc]
        if row[0] == "goto":
            pc = row[1]
        elif row[0] == "move":
            need(row[1] == 2 and row[2] in (-1, 1), "confined unit movement")
            position += row[2]
            need(0 <= position < len(tape), "marker confinement")
            moves += 1
            pc += 1
        elif row[0] == "branch":
            need(row[1] == 2, "only numerator read")
            reads += 1
            pc = dict(row[2]).get(tape[position], row[3])
        else:
            raise ValueError("unexpected phase instruction")
    raise ValueError("phase step bound exhausted")


def phase_cases():
    words = states = rows = 0
    for odd in range(3, 126, 2):
        table, receipt = compile_add(Fraction(1, odd))
        need(receipt["reverse_states"] == 8 * odd + 2, "exact phase-state count")
        need(receipt["reverse_rows"] == 14 * odd + 4, "exact phase-row count")
        states += receipt["reverse_states"]
        rows += receipt["reverse_rows"]
        for width in range(1, 9):
            for unsigned in range(1 << width):
                bits = [(unsigned >> j) & 1 for j in range(width)]
                signed = unsigned - (bits[-1] << width)
                for parity in (0, 1):
                    residue, reads, moves, steps = run_phase(table, receipt, bits, parity)
                    need(residue == signed % odd, "direct signed-integer residue")
                    need((reads, moves, steps) == (width + 1, width + 2, 3 * width + 4),
                         "exact local operation counts")
                    words += 1
    return dict(odd_divisors=62, signed_phase_cases=words,
                enumerated_phase_states=states, enumerated_phase_rows=rows)


def check_call(fixture, table, coefficient, target, source, width, work=None):
    result = fixture.execute(table, "ADD", target, source, width, work,
                             count_rows=True)
    a, b = coefficient.numerator, coefficient.denominator
    expected = tuple(x + (a * y + b // 2) // b for x, y in zip(target, source))
    fits = all(-(1 << (width - 1)) <= value < (1 << (width - 1)) for value in expected)
    need((result["error"] is None) == fits, "whole-field final-range iff")
    if fits:
        need(result["output"] == expected, "direct integer nearest-up ADD")
    return result


def arithmetic_cases(fixture):
    cases = successes = 0
    coefficients = (Fraction(0), Fraction(-1), Fraction(1, 2), Fraction(-2, 3),
                    Fraction(1, 5), Fraction(-5, 6), Fraction(7, 10), Fraction(13, 12))
    for coefficient in coefficients:
        table, receipt = compile_add(coefficient)
        need(all(row[0] in ("branch", "goto", "move", "write", "halt", "reject")
                 for row in table), "literal six-opcode table")
        for width in range(1, 5):
            values = range(-(1 << (width - 1)), 1 << (width - 1))
            for x in values:
                for y in values:
                    result = check_call(fixture, table, coefficient, (x, 0), (y, 0), width)
                    successes += result["error"] is None
                    cases += 1
        if receipt["odd_divisor"] == 1:
            original, _ = compile_add(coefficient, baseline=True)
            need(table == original, "dyadic and integral tables byte-identical")
    return dict(coefficients=len(coefficients), complete_calls=cases,
                successes=successes, range_rejections=cases - successes)


def improvement_cases(fixture):
    samples = ((Fraction(-14729531, 163840), 100, 2, 8),
               (Fraction(-1379, 250), 7, 2, 4),
               (Fraction(1085645, 393216), -7, 3, 4))
    evidence = []
    for coefficient, x, y, width in samples:
        table, receipt = compile_add(coefficient)
        original, before = compile_add(coefficient, baseline=True)
        changed = check_call(fixture, table, coefficient, (x, 0), (y, 0), width)
        control = fixture.execute(original, "ADD", (x, 0), (y, 0), width, count_rows=True)
        need(changed["error"] is None, "new source-compatible cancellation case")
        need(control["output"] == changed["output"], "resource comparator endpoint")
        component_width = width + receipt["extra_width"]
        need(control["actions"] - changed["actions"] == 56 * (component_width + 1),
             "two-component physical-action saving")
        need(control["table_rows"] - changed["table_rows"] == 8 * component_width + 12,
             "two-component executed-row saving")
        need(receipt["rows"] < before["rows"], "strict fixed-table improvement")
        evidence.append(dict(coefficient=str(coefficient), width=width,
                             output=list(changed["output"]),
                             old_rows=before["rows"], new_rows=receipt["rows"],
                             saved_rows=before["rows"] - receipt["rows"],
                             saved_physical_actions=control["actions"] - changed["actions"],
                             saved_executed_rows=control["table_rows"] - changed["table_rows"]))
    return evidence


def controls(fixture):
    caught = []
    for mutant in ("unsigned", "missing-double"):
        table, receipt = compile_add(Fraction(-2, 3), mutant=mutant)
        failures = 0
        for unsigned in range(8):
            bits = [(unsigned >> j) & 1 for j in range(3)]
            residue, _, _, _ = run_phase(table, receipt, bits, 0)
            failures += residue != (unsigned - (bits[-1] << 3)) % 3
        need(failures > 0, "mutant changes literal phase")
        caught.append(dict(mutant=mutant, enumerated_failures=failures))
    table, _ = compile_add(Fraction(-2, 3))
    work = [fixture.Tape((1, 0) * 400, 101), fixture.Tape((0, 1) * 500, 1201)]
    work[0].pos += 799
    work[1].pos += 1000
    for width in (12, 2, 7, 1):
        check_call(fixture, table, Fraction(-2, 3), (0, 0), (0, 0), width, work)
    late = check_call(fixture, table, Fraction(-2, 3), (0, -8), (0, 7), 4, work)
    need(late["error"] is not None, "late overflow keeps the whole target unchanged")
    check_call(fixture, table, Fraction(-2, 3), (0, 0), (0, 0), 2, work)
    for coefficient in (Fraction(1, 127), Fraction(1, 1 << 24)):
        try:
            compile_add(coefficient)
        except ValueError:
            continue
        raise ValueError("executable domain guard missing")
    return dict(semantic_mutants=caught, dirty_history_calls=6, invalid_coefficients=2)


def main():
    fixture = physical_fixture()
    result = dict(status="PASS_REVERSE_HORNER_RESIDUE", python=platform.python_version(),
                  phase=phase_cases(), arithmetic=arithmetic_cases(fixture),
                  improvement=improvement_cases(fixture), controls=controls(fixture))
    result["package_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(PACKAGE.iterdir()) if path.is_file()
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
