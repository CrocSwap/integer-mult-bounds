"""Dense exact endpoint and prefix check, independent of the search/lowering.

Eva Ayala / ToikY, with substantial OpenAI Codex assistance. Apache-2.0.
Only the frozen BLOCKS.json data is consumed; no supplier module is imported.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = ("W", 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reg(value):
    require(isinstance(value, (list, tuple)) and len(value) == 2,
            "malformed register")
    return tuple(value)


def universe(ops, baseline, revised):
    names = {WORK}
    for word in (ops, baseline, revised):
        for op in word:
            for value in op[1:]:
                if isinstance(value, (list, tuple)):
                    names.add(reg(value))
    return sorted(names)


def basis(names):
    # Every register, including initially dirty W0, is an independent input.
    return {name: [Fraction(int(i == j)) for i in range(len(names))]
            for j, name in enumerate(names)}


def metrics(state):
    rows = [(sum(abs(x) for x in row), name) for name, row in state.items()]
    norm, name = max(rows)
    denominator = max(x.denominator for row in state.values() for x in row)
    return norm, denominator, name


def replay(word, names, macros=False, work_zero=False):
    state = basis(names)
    if work_zero:
        state[WORK] = [Fraction(0)] * len(names)
    peak_l1, peak_denominator, peak_register = metrics(state)
    peak_position = 0
    counts = Counter()
    for position, op in enumerate(word, 1):
        require(isinstance(op, (list, tuple)) and len(op) >= 2,
                "malformed operation")
        kind, target = op[0], reg(op[1])
        require(target in state, "unknown target")
        row = state[target]
        if kind == "clear":
            require(len(op) == 2, "bad clear arity")
            state[target] = [Fraction(0)] * len(names)
        elif kind == "copy":
            require(len(op) == 3, "bad copy arity")
            state[target] = state[reg(op[2])][:]
        elif kind == "scale" and macros:
            require(len(op) == 4, "bad scale arity")
            scalar = Fraction(op[2], op[3])
            state[target] = [scalar * x for x in row]
        elif kind == "add" and macros:
            require(len(op) == 5, "bad macro add arity")
            scalar = Fraction(op[3], op[4])
            source = state[reg(op[2])]
            state[target] = [x + scalar * y for x, y in zip(row, source)]
        elif kind in ("double", "halve", "negate") and not macros:
            require(len(op) == 2, "bad unary arity")
            scalar = {"double": Fraction(2), "halve": Fraction(1, 2),
                      "negate": Fraction(-1)}[kind]
            state[target] = [scalar * x for x in row]
        elif kind in ("add", "subtract") and not macros:
            require(len(op) == 3, "bad primitive addition arity")
            source = state[reg(op[2])]
            sign = 1 if kind == "add" else -1
            state[target] = [x + sign * y for x, y in zip(row, source)]
        else:
            raise ValueError("unknown operation: " + str(kind))
        counts[kind] += 1
        # Only this target row changed. Every unchanged row was already
        # included in the historical maxima, so inspect the complete changed
        # row at every primitive without rescanning all unchanged rows.
        norm = sum(abs(x) for x in state[target])
        denominator = max(x.denominator for x in state[target])
        name = target
        if norm > peak_l1:
            peak_l1, peak_register, peak_position = norm, name, position
        peak_denominator = max(peak_denominator, denominator)
    return state, {"length": len(word), "counts": dict(sorted(counts.items())),
                   "max_row_l1": str(peak_l1),
                   "max_denominator": peak_denominator,
                   "peak_register": list(peak_register),
                   "peak_position": peak_position}


def field(record, *names):
    for name in names:
        if name in record:
            return record[name]
    raise ValueError("missing block field: " + names[0])


def elide_work_clears(word, incoming_zero):
    """Remove only clears of W already known zero, without supplier code."""
    known_zero, result = incoming_zero, []
    for op in word:
        target = reg(op[1])
        if target == WORK:
            if op[0] == "clear":
                if known_zero:
                    continue
                known_zero = True
            elif op[0] not in ("double", "halve", "negate"):
                known_zero = False
        result.append(op)
    return result


def verify_elision(before, after, names, work_zero):
    lengths = []
    for word in (before, after):
        elided = elide_work_clears(word, work_zero)
        raw_state, raw_metrics = replay(word, names, work_zero=work_zero)
        state, compressed_metrics = replay(elided, names, work_zero=work_zero)
        require(state == raw_state, "clear elision endpoint mismatch")
        for metric in ("max_row_l1", "max_denominator"):
            require(compressed_metrics[metric] == raw_metrics[metric],
                    "clear elision prefix mismatch")
        lengths.append(len(elided))
    return {"baseline_length": lengths[0], "revised_length": lengths[1],
            "delta": lengths[1] - lengths[0],
            "endpoint_and_prefix_equal_to_raw": True}


def verify(record, expected=None):
    ops = field(record, "ops", "macros", "macro_ops")
    before = field(record, "baseline_word", "baseline", "before")
    after = field(record, "word", "new_word", "revised_word", "after")
    names = universe(ops, before, after)
    logical, macro_report = replay(ops, names, macros=True)
    baseline, baseline_report = replay(before, names)
    revised, revised_report = replay(after, names)
    for name in names:
        if name != WORK:
            require(baseline[name] == logical[name], "baseline macro mismatch")
            require(revised[name] == logical[name], "revised macro mismatch")
    require(baseline[WORK] == revised[WORK], "work endpoint mismatch")
    touched_work = any(WORK == reg(value) for word in (before, after)
                       for op in word for value in op[1:]
                       if isinstance(value, (list, tuple)))
    if touched_work:
        require(not any(baseline[WORK]), "work is not cleared")
    delta = len(after) - len(before)
    claimed = field(record, "delta", "claimed_delta")
    require(delta == claimed, "claimed delta mismatch")
    for key, value in (("baseline_length", len(before)), ("word_length", len(after)),
                       ("new_length", len(after)), ("length", len(after))):
        if key in record:
            require(record[key] == value, "claimed length mismatch")
    report = {"basis_size": len(names), "logical_registers": len(names) - 1,
              "dirty_work_input": True, "delta": delta,
              "macro": macro_report, "baseline": baseline_report,
              "revised": revised_report}
    if expected is not None:
        for variant in ("macro", "baseline", "revised"):
            for metric in ("max_row_l1", "max_denominator"):
                require(report[variant][metric] == expected[variant][metric],
                        "prefix report mismatch")
    return report


def expect_rejection(record, expected, label):
    try:
        verify(record, expected)
    except ValueError:
        return label
    raise ValueError("negative control accepted: " + label)


def controls(record, report):
    revised_key = next(key for key in ("word", "new_word", "revised_word", "after")
                       if key in record)
    delta_key = "delta" if "delta" in record else "claimed_delta"
    accepted = []
    bad = deepcopy(record)
    bad[delta_key] += 1
    accepted.append(expect_rejection(bad, report, "corrupt_claimed_cost"))

    # The final flush restores the deliberately deferred one-bit magnitude.
    if record.get("mode") == "flush":
        bad = deepcopy(record)
        final = bad[revised_key][-1]
        require(final[0] in ("double", "halve"), "missing final flush shift")
        bad[revised_key].pop()
        accepted.append(expect_rejection(bad, report, "delete_restoration_shift"))

    bad = deepcopy(record)
    target_update = next((i for i, op in enumerate(bad[revised_key])
                          if op[0] in ("add", "subtract") and reg(op[1]) != WORK), None)
    require(target_update is not None, "no target update for negative control")
    bad[revised_key][target_update][0] = (
        "subtract" if bad[revised_key][target_update][0] == "add" else "add")
    accepted.append(expect_rejection(bad, report, "flip_target_coefficient_sign"))

    bad = deepcopy(record)
    preparation_copy = next((i for i, op in enumerate(bad[revised_key])
                             if op[0] == "copy" and reg(op[1]) == WORK), None)
    require(preparation_copy is not None, "no preparation copy for negative control")
    bad[revised_key].pop(preparation_copy)
    accepted.append(expect_rejection(bad, report, "delete_preparation_copy"))

    # This control has the same endpoint. Prefix checking must still reject it.
    bad = deepcopy(record)
    peak = report["revised"]
    position, name = peak["peak_position"], peak["peak_register"]
    bad[revised_key][position:position] = [["double", name], ["halve", name]]
    bad[delta_key] += 2
    for key in ("word_length", "new_length", "length"):
        if key in bad:
            bad[key] += 2
    modified = verify(bad)
    require(Fraction(modified["revised"]["max_row_l1"]) >
            Fraction(peak["max_row_l1"]), "control did not increase prefix peak")
    accepted.append(expect_rejection(bad, report, "endpoint_correct_prefix_excursion"))
    return accepted


def main():
    payload = json.loads((HERE / "BLOCKS.json").read_text())
    records = payload.get("blocks", payload)
    if isinstance(records, list):
        records = {str(index): record for index, record in enumerate(records)}
    require(isinstance(records, dict), "blocks must be a mapping or list")
    result = {}
    for name, record in records.items():
        if not isinstance(record, dict):
            continue
        report = verify(record)
        before = field(record, "baseline_word", "baseline", "before")
        after = field(record, "word", "new_word", "revised_word", "after")
        ops = field(record, "ops", "macros", "macro_ops")
        names = universe(ops, before, after)
        elision = {"dirty_work": verify_elision(before, after, names, False),
                   "zero_work": verify_elision(before, after, names, True)}
        result[name] = {"report": report, "clear_elision": elision,
                        "negative_controls": controls(record, report)}
    require(bool(result), "no blocks checked")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
