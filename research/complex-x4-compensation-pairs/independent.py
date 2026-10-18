"""Independent exact scalar replay using integer rows and dyadic denominators.

No constructor, retained auditor, or search implementation is imported. Every
register starts with its own independent input column, including dirty helpers.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""

import hashlib
import json
from fractions import Fraction


def _require(condition, message):
    if not condition:
        raise RuntimeError(message)


def _power(value):
    _require(type(value) is int and value > 0 and value & (value - 1) == 0,
             "denominator is not a positive power of two")
    return value.bit_length() - 1


def _normalize(row, denominator_power):
    """Remove common factors of two, without introducing negative powers."""
    if not row:
        return {}, 0
    if denominator_power:
        shift = min(denominator_power,
                    min((abs(value) & -abs(value)).bit_length() - 1
                        for value in row.values()))
        if shift:
            row = {column: value >> shift for column, value in row.items()}
            denominator_power -= shift
    return row, denominator_power


def _run(program, n, dual):
    _require(type(n) is int and n > 0, "invalid register count")
    rows = [({register: 1}, 0) for register in range(n)]
    largest = 1
    for index, gate in enumerate(program):
        _require(isinstance(gate, (list, tuple)) and gate,
                 "malformed gate at %d" % index)
        op = gate[0]
        _require(op in ("add", "scale"), "unknown operation at %d" % index)
        _require(len(gate) == (6 if op == "add" else 5),
                 "malformed %s gate at %d" % (op, index))
        target = gate[1]
        registers = [target, gate[2]] if op == "add" else [target]
        _require(all(type(r) is int and 0 <= r < n for r in registers),
                 "register out of range at %d" % index)
        numerator, denominator = gate[3:5] if op == "add" else gate[2:4]
        _require(type(numerator) is int, "noninteger numerator at %d" % index)
        _require(type(denominator) is int and denominator != 0,
                 "invalid denominator at %d" % index)
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        power = _power(denominator)
        if op == "add":
            source = gate[2]
            _require(source != target, "self-add at %d" % index)
            if dual:
                target, source, numerator = source, target, -numerator
            target_row, target_power = rows[target]
            source_row, source_power = rows[source]
            if not numerator or not source_row:
                continue
            common_power = max(target_power, source_power + power)
            new_row = {column: value << (common_power - target_power)
                       for column, value in target_row.items()}
            source_shift = common_power - source_power - power
            for column, value in source_row.items():
                result = new_row.get(column, 0) + numerator * (value << source_shift)
                if result:
                    new_row[column] = result
                else:
                    new_row.pop(column, None)
            rows[target] = _normalize(new_row, common_power)
        else:
            _require(numerator != 0, "zero scale at %d" % index)
            absolute = abs(numerator)
            _require(absolute & (absolute - 1) == 0,
                     "scale is not a signed binary unit at %d" % index)
            if dual:
                numerator, power = (-1 if numerator < 0 else 1) << power, absolute.bit_length() - 1
            row, old_power = rows[target]
            rows[target] = _normalize({column: numerator * value
                                       for column, value in row.items()}, old_power + power)
        largest = max(largest, max((abs(value).bit_length()
                                    for value in rows[target][0].values()), default=0))
    return rows, largest


def _endpoint(rows, expected, largest, label):
    for register, (actual, denominator_power) in enumerate(rows):
        wanted = expected(register)
        scale = 1 << denominator_power
        _require(set(actual) == set(wanted) and
                 all(Fraction(value, scale) == wanted[column]
                     for column, value in actual.items()),
                 "%s endpoint mismatch at register %d" % (label, register))
    canonical = [[power, sorted(row.items())] for row, power in rows]
    return dict(status="PASS_INDEPENDENT_ALL_COLUMN_" + label,
                checked_columns=len(rows), max_numerator_bits=largest,
                endpoint_sha256=hashlib.sha256(json.dumps(
                    canonical, separators=(",", ":")).encode()).hexdigest())


def check(program, n, dual=False, v=112):
    """Check the complete forward shear or chronological inverse transpose.

    ``v=112`` is the selected X4 port count. A smaller explicit ``v`` is useful
    for independent controls. Every source, target, and helper input is checked.
    """
    _require(type(n) is int and n > 0, "invalid register count")
    _require(type(v) is int and v > 0 and n >= 2 * v, "invalid port count")
    rows, largest = _run(program, n, dual)

    def expected(register):
        row = {register: 1}
        if dual and register < v:
            row[v + register] = -1
        elif not dual and v <= register < 2 * v:
            row[register - v] = 1
        return row

    return _endpoint(rows, expected, largest, "DUAL" if dual else "FORWARD")


def check_compensation(program, C, v, n):
    """Check ``target += C * helper`` with arbitrary target and helper dirt.

    C is a mapping from target register to a mapping from helper register to an
    exact rational coefficient. A list of row mappings indexed by target-v is
    also accepted. All other registers must retain their independent inputs.
    """
    _require(type(n) is int and n > 0, "invalid register count")
    _require(type(v) is int and v > 0 and n >= 2 * v, "invalid port count")
    if isinstance(C, (list, tuple)):
        _require(len(C) == v, "compensation matrix row count")
        C = {v + index: row for index, row in enumerate(C)}
    _require(isinstance(C, dict), "compensation must be a row mapping")
    wanted = {}
    for target, row in C.items():
        _require(type(target) is int and v <= target < 2 * v,
                 "compensation target out of range")
        _require(isinstance(row, dict), "compensation row is not a mapping")
        wanted[target] = {}
        for source, value in row.items():
            _require(type(source) is int and 2 * v <= source < n,
                     "compensation helper out of range")
            value = Fraction(*value) if isinstance(value, (list, tuple)) else Fraction(value)
            _power(value.denominator)
            if value:
                wanted[target][source] = value
    rows, largest = _run(program, n, False)
    return _endpoint(rows, lambda register: {register: 1, **wanted.get(register, {})},
                     largest, "COMPENSATION")


def self_test():
    """Exercise noncommuting dirty-helper cancellation and rejection controls."""
    program = [["add", 2, 0, 1, 2, []], ["add", 1, 2, 2, 1, []],
               ["add", 2, 0, -1, 2, []], ["add", 1, 2, -2, 1, []],
               ["scale", 2, -2, 1, []], ["scale", 2, -1, 2, []],
               ["scale", 2, 1, -1, []], ["scale", 2, -1, 1, []],
               ["add", 2, 0, 3, 4, []], ["add", 2, 0, -3, 4, []]]
    check(program, 3, v=1)
    check(program, 3, dual=True, v=1)
    block = [["add", 1, 2, 3, 4, []]]
    check_compensation(block, {1: {2: Fraction(3, 4)}}, 1, 3)
    controls = [program[:3], [["add", 0, 0, 1, 1, []]],
                [["scale", 2, 0, 1, []]], [["scale", 2, 3, 1, []]],
                [["scale", 2, 1, 3, []]], [["scale", 2, 1, 0, []]],
                [["add", 3, 0, 1, 1, []]]]
    for control in controls:
        try:
            check(control, 3, v=1)
        except RuntimeError:
            continue
        raise RuntimeError("negative self-test accepted")
    try:
        check_compensation([], {1: {2: Fraction(3, 4)}}, 1, 3)
    except RuntimeError:
        return dict(status="PASS_INDEPENDENT_SELF_TEST", rejected_controls=len(controls) + 1)
    raise RuntimeError("compensation control accepted")


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True))
