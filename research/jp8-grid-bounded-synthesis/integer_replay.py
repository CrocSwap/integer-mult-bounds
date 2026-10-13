#!/usr/bin/env python3
"""Independent integer-only replay of the historical JP8 scalar projections.

Prepared for Philipp (@mightyOil) with substantial OpenAI Codex assistance.
Apache-2.0. Python 3.11+, standard library only. No project modules or Fraction
arithmetic are imported. This checks scalar words, not the full complex circuit
or a multiplication bound. All checks remain active under ``python -I -O``.

A row is (k, sparse_integers), representing sparse_integers / 2**k. Each written
row is normalized by removing every common factor of two allowed by k. Rows are
never mutated after construction, so copying a row can safely share its value.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = ROOT / "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8"
N, V = 716, 112
WORK = ("W", 0)
PRIVATE = (WORK,) + tuple(("C", i) for i in range(8))
ZERO = (0, {})


class VerificationError(ValueError):
    """An integer replay obligation failed."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def reduced(numerator, denominator):
    require(type(numerator) is int and type(denominator) is int and denominator,
            "invalid scalar ratio")
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    common = gcd(abs(numerator), denominator)
    numerator, denominator = numerator // common, denominator // common
    require(denominator & (denominator - 1) == 0, "non-dyadic scalar ratio")
    return numerator, denominator.bit_length() - 1


def trailing_twos(value):
    require(value != 0, "zero has no finite two-adic valuation")
    value = abs(value)
    return (value & -value).bit_length() - 1


def row(denominator_power, coefficients):
    coefficients = {column: value for column, value in coefficients.items() if value}
    require(denominator_power >= 0, "negative denominator power")
    if not coefficients:
        return ZERO
    common = min(denominator_power, min(trailing_twos(x) for x in coefficients.values()))
    if common:
        coefficients = {column: value >> common for column, value in coefficients.items()}
    return denominator_power - common, coefficients


def row_sum(left, right, sign=1):
    power = max(left[0], right[0])
    result = {column: value << (power - left[0]) for column, value in left[1].items()}
    for column, value in right[1].items():
        result[column] = result.get(column, 0) + sign * (value << (power - right[0]))
    return row(power, result)


def row_multiple(value, numerator, denominator_power=0):
    return row(value[0] + denominator_power,
               {column: coefficient * numerator for column, coefficient in value[1].items()})


def initial_rows():
    result = {("L", i): (0, {i: 1}) for i in range(N)}
    result.update({register: (0, {N + i: 1}) for i, register in enumerate(PRIVATE)})
    return result


def primitive(rows, instruction):
    """Integer row arithmetic; no macro evaluation is used by this interpreter."""
    require(isinstance(instruction, (tuple, list)) and len(instruction) >= 2,
            "malformed primitive")
    tag, target = instruction[0], tuple(instruction[1])
    require(target in rows, "unknown primitive target")
    require(tag in ("clear", "copy", "add", "subtract", "double", "halve", "negate"),
            "unknown primitive tag")
    require(len(instruction) == (3 if tag in ("copy", "add", "subtract") else 2),
            "primitive arity")
    if tag in ("copy", "add", "subtract"):
        source = tuple(instruction[2])
        require(source in rows and source != target, "invalid primitive source")
    if tag == "clear":
        rows[target] = ZERO
    elif tag == "copy":
        rows[target] = rows[source]
    elif tag in ("add", "subtract"):
        rows[target] = row_sum(rows[target], rows[source], 1 if tag == "add" else -1)
    elif tag == "double":
        rows[target] = row_multiple(rows[target], 2)
    elif tag == "halve":
        # Increase the common denominator; never use integer truncating division.
        rows[target] = row_multiple(rows[target], 1, 1)
    else:
        rows[target] = row_multiple(rows[target], -1)


def macro_oracle(rows, op):
    """Direct integer scalar semantics, independent of either primitive emitter."""
    tag, target = op[0], tuple(op[1])
    require(target in rows and target != WORK, "invalid scalar target")
    if tag == "clear":
        rows[target] = ZERO
    elif tag == "copy":
        source = tuple(op[2])
        require(source in rows and source not in (target, WORK), "invalid scalar source")
        rows[target] = rows[source]
    elif tag == "scale":
        numerator, power = reduced(op[2], op[3])
        require(numerator and abs(numerator) & (abs(numerator) - 1) == 0,
                "scale is not a signed power of two")
        rows[target] = row_multiple(rows[target], numerator, power)
    elif tag == "add":
        source = tuple(op[2])
        require(source in rows and source not in (target, WORK), "invalid scalar source")
        numerator, power = reduced(op[3], op[4])
        require(numerator, "zero addition coefficient")
        rows[target] = row_sum(rows[target], row_multiple(rows[source], numerator, power))
        rows[WORK] = ZERO
    else:
        raise VerificationError("unknown scalar macro")


def naf_statistics(numerator):
    """Length and nonzero count from the defining non-adjacent-digit recurrence."""
    require(type(numerator) is int and numerator > 0, "invalid NAF numerator")
    length = weight = 0
    while numerator:
        if numerator & 1:
            digit = 1 if numerator == 1 or numerator % 4 == 1 else -1
            numerator -= digit
            weight += 1
        numerator >>= 1
        length += 1
    return length, weight


def comparator_lengths(numerator, denominator_power):
    """Count copy, shifts, non-leading digits, accumulation, and final clear."""
    require(numerator > 0, "invalid comparator numerator")
    if numerator == 1 and denominator_power == 0:
        return {"binary-forward": 2}
    binary_length, binary_weight = numerator.bit_length(), numerator.bit_count()
    naf_length, naf_weight = naf_statistics(numerator)
    removed = trailing_twos(numerator)
    odd = numerator >> removed
    reverse_binary_length, reverse_binary_weight = odd.bit_length(), odd.bit_count()
    reverse_naf_length, reverse_naf_weight = naf_statistics(odd)
    return {
        "binary-forward": binary_length + binary_weight + denominator_power + 1,
        "naf-forward": naf_length + naf_weight + denominator_power + 1,
        "binary-reverse": reverse_binary_length + reverse_binary_weight + 1
            + abs(reverse_binary_length - 1 + removed - denominator_power),
        "naf-reverse": reverse_naf_length + reverse_naf_weight + 1
            + abs(reverse_naf_length - 1 + removed - denominator_power),
    }


def validate_path(entry):
    n, d = entry["numerator"], entry["denominator"]
    require(type(n) is int and 1 <= n <= 127 and type(d) is int and d in (1, 2, 4, 8, 16),
            "certificate coefficient outside domain")
    require(gcd(n, d) == 1 and (n, d) != (1, 1), "unreduced or unit graph coefficient")
    operations, sign = entry["operations"], entry["end_sign"]
    require(isinstance(operations, list) and type(sign) is int and sign in (-1, 1),
            "invalid certificate path")
    require(type(entry["preparation_steps"]) is int and entry["preparation_steps"] == len(operations),
            "certificate preparation invoice")
    state, bound = d, n * d
    for operation in operations:
        if operation == "double":
            state *= 2
        elif operation == "halve":
            require(state % 2 == 0, "certificate path leaves coefficient grid")
            state //= 2
        elif operation == "add":
            state += d
        elif operation == "subtract":
            state -= d
        elif operation == "negate":
            state = -state
        else:
            raise VerificationError("unknown certificate operation")
        require(abs(state) <= bound, "certificate path exceeds magnitude envelope")
    require(state == sign * n, "certificate signed endpoint")
    costs = comparator_lengths(n, d.bit_length() - 1)
    require(canonical(entry["horner_macro_costs"]) == canonical(costs), "independent comparator lengths differ")
    selected = len(operations) + 3 < min(costs.values())
    require(type(entry["strict_horner_improvement"]) is bool
            and entry["strict_horner_improvement"] == selected, "certificate selection flag")
    return selected


def prepare_certificate(certificate, programs):
    require(certificate["schema"] == "jp8-grid-bounded-synthesis/1", "certificate schema")
    all_entries, selected = {}, {}
    for entry in certificate["entries"]:
        key = entry["numerator"], entry["denominator"]
        require(key not in all_entries, "duplicate certificate coefficient")
        all_entries[key] = entry
        if validate_path(entry):
            selected[key] = entry
    source = set()
    for events in programs.values():
        for event in events:
            if event[0] == "scalar" and event[1][0] == "add":
                n, power = reduced(event[1][3], event[1][4])
                key = abs(n), 1 << power
                if key != (1, 1) and abs(n) <= 127 and power <= 4:
                    source.add(key)
    require(set(all_entries) == source, "certificate source coefficient coverage")
    require(len(all_entries) == 49 and len(selected) == 7, "claimed coefficient census")
    return all_entries, selected


def emit_baseline(op):
    """Reconstruct PR696 binary/copy and unit words without importing a lowerer."""
    tag, target = op[0], tuple(op[1])
    require(target != WORK, "scalar work alias")
    if tag == "clear":
        return [("clear", target)]
    if tag == "copy":
        source = tuple(op[2])
        require(source not in (target, WORK), "scalar source alias")
        return [("copy", target, source)]
    if tag == "scale":
        numerator, power = reduced(op[2], op[3])
        require(numerator and abs(numerator) & (abs(numerator) - 1) == 0,
                "scale is not a signed power of two")
        shift = abs(numerator).bit_length() - 1 - power
        return ([("double" if shift > 0 else "halve", target)] * abs(shift)
                + ([("negate", target)] if numerator < 0 else []))
    require(tag == "add", "unknown scalar macro")
    source = tuple(op[2])
    require(source not in (target, WORK), "scalar source alias")
    numerator, power = reduced(op[3], op[4])
    require(numerator, "zero addition coefficient")
    accumulate = "add" if numerator > 0 else "subtract"
    if abs(numerator) == 1 and power == 0:
        return [(accumulate, target, source), ("clear", WORK)]
    word = [("copy", WORK, source)]
    for position in range(abs(numerator).bit_length() - 2, -1, -1):
        word.append(("double", WORK))
        if (abs(numerator) >> position) & 1:
            word.append(("add", WORK, source))
    word += [("halve", WORK)] * power
    return word + [(accumulate, target, WORK), ("clear", WORK)]


def emit_replacement(op, selected):
    if op[0] != "add":
        return emit_baseline(op)
    numerator, power = reduced(op[3], op[4])
    entry = selected.get((abs(numerator), 1 << power))
    if entry is None:
        return emit_baseline(op)
    target, source = tuple(op[1]), tuple(op[2])
    word = [("copy", WORK, source)]
    for operation in entry["operations"]:
        word.append((operation, WORK, source) if operation in ("add", "subtract")
                    else (operation, WORK))
    sign = (1 if numerator > 0 else -1) * entry["end_sign"]
    return word + [("add" if sign > 0 else "subtract", target, WORK), ("clear", WORK)]


def historical_count(op):
    if op[0] in ("clear", "copy"):
        return 1
    if op[0] == "scale":
        n, power = reduced(op[2], op[3])
        return abs(abs(n).bit_length() - 1 - power) + (n < 0)
    n, power = reduced(op[3], op[4])
    return abs(n).bit_length() + abs(n).bit_count() + power + 2


class Trace:
    def __init__(self):
        self.rows = initial_rows()
        self.tags = Counter()
        self.maximum_denominator = 0
        self.maximum_l1_numerator, self.maximum_l1_power = 1, 0
        self.source_reads = self.register_reads = 0
        self.digest = hashlib.sha256()

    def run(self, op, word, frame, event_index):
        target = tuple(op[1])
        source = tuple(op[2]) if op[0] in ("copy", "add") else None
        allowed_writes = {target, WORK} if op[0] == "add" else {target}
        allowed_reads = allowed_writes | ({source} if source is not None else set())
        for instruction in word:
            tag, written = instruction[0], tuple(instruction[1])
            require(written in allowed_writes, "primitive writes outside its macro")
            reads = [] if tag in ("clear", "copy") else [written]
            if len(instruction) == 3:
                read_register = tuple(instruction[2])
                require(read_register in allowed_reads, "primitive reads outside its macro")
                reads.append(read_register)
            primitive(self.rows, instruction)
            self.source_reads += reads.count(source) if source is not None else 0
            self.register_reads += len(reads)
            self.tags[tag] += 2
            self.maximum_denominator = max(self.maximum_denominator, self.rows[written][0])
            # Compare exact dyadic norms by integer cross multiplication.
            # All initial basis rows have norm one; only the written row changes.
            power, coefficients = self.rows[written]
            numerator = sum(abs(value) for value in coefficients.values())
            if (numerator << self.maximum_l1_power) > (self.maximum_l1_numerator << power):
                self.maximum_l1_numerator, self.maximum_l1_power = numerator, power
            self.digest.update(canonical([event_index, frame, instruction]) + b"\n")
        if op[0] == "add":
            require(self.rows[WORK] == ZERO, "dirty coefficient scratch")

    def receipt(self):
        denominator = 1 << self.maximum_l1_power
        common = gcd(self.maximum_l1_numerator, denominator)
        numerator, denominator = self.maximum_l1_numerator // common, denominator // common
        maximum_l1 = str(numerator) if denominator == 1 else f"{numerator}/{denominator}"
        return {"real_primitives": sum(self.tags.values()),
                "primitive_tags": dict(sorted(self.tags.items())),
                "primitive_word_sha256": self.digest.hexdigest(),
                "maximum_fractional_denominator_exponent": self.maximum_denominator,
                "maximum_scalar_prefix_row_l1": maximum_l1,
                "real_macro_source_reads": 2 * self.source_reads,
                "real_total_register_reads": 2 * self.register_reads}


def full_endpoint(rows, orientation):
    for index in range(N):
        expected = {index: 1}
        if orientation == "forward" and V <= index < 2 * V:
            expected[index - V] = 1
        elif orientation == "backward" and index < V:
            expected[index + V] = -1
        require(rows[("L", index)] == (0, expected), "full scalar endpoint")
    require(all(rows[register] == ZERO for register in PRIVATE), "private scalar endpoint")


def replay_orientation(orientation, events, checks, selected):
    require(sha(events) == checks["sha256"], "source orientation semantic hash")
    baseline, replacement = Trace(), Trace()
    oracle = initial_rows()
    paid = Counter()
    historical = macros = additions = units = changed = 0
    non_scalar_digest = hashlib.sha256()
    frame_digest = hashlib.sha256()
    for index, event in enumerate(events):
        if event[0] != "scalar":
            require(event[0] in ("climb", "center", "phase", "adapter", "residual_adapter"),
                    "unknown nonscalar event")
            if event[0] == "climb":
                paid[event[5]] += 1
            elif event[0] == "center":
                paid[event[4]] += 1
            non_scalar_digest.update(canonical([index, event]) + b"\n")
            continue
        require(len(event) == 3, "scalar event arity")
        op, frame = event[1:]
        old_word, new_word = emit_baseline(op), emit_replacement(op, selected)
        require(len(new_word) <= len(old_word), "replacement raised primitive bill")
        macros += 1
        historical += 2 * historical_count(op)
        changed += old_word != new_word
        if op[0] == "add":
            additions += 1
            n, power = reduced(op[3], op[4])
            units += abs(n) == 1 and power == 0
        macro_oracle(oracle, op)
        baseline.run(op, old_word, frame, index)
        replacement.run(op, new_word, frame, index)
        # Every primitive is restricted to target and W, so checking the written
        # rows propagates equality of all 725 columns/registers by induction.
        target = tuple(op[1])
        for trace in (baseline, replacement):
            require(trace.rows[target] == oracle[target], "macro target differs from integer oracle")
            require(trace.rows[WORK] == oracle[WORK], "macro scratch differs from integer oracle")
        frame_digest.update(canonical([index, frame]) + b"\n")
    for rows in (oracle, baseline.rows, replacement.rows):
        full_endpoint(rows, orientation)
    require(baseline.rows == replacement.rows == oracle, "all-register endpoint comparison")
    require(len(events) == checks["events"] and macros == checks["scalar_macros"], "source event/macro census")
    require(historical == checks["real_component_primitive_bound"], "historical primitive invoice")
    require(dict(paid) == {int(key): value for key, value in checks["paid_profile"].items()}, "paid profile")
    old, new = baseline.receipt(), replacement.receipt()
    require(historical - old["real_primitives"] == 2 * (additions + units), "PR696 primitive invoice")
    require(new["maximum_fractional_denominator_exponent"] <= old["maximum_fractional_denominator_exponent"],
            "replacement increases full-trace fractional guard")
    require((replacement.maximum_l1_numerator << baseline.maximum_l1_power) <=
            (baseline.maximum_l1_numerator << replacement.maximum_l1_power),
            "replacement increases scalar prefix row-L1 maximum")
    return {"total_exact_input_columns": N + len(PRIVATE), "logical_input_columns": N,
            "arbitrary_private_input_columns": len(PRIVATE), "arbitrary_helper_columns_restored": N - 2 * V,
            "private_registers_erased": len(PRIVATE), "events": len(events), "scalar_macros": macros,
            "macro_boundaries_compared_with_integer_oracle": macros, "changed_macros": changed,
            "addition_macros_with_coefficient_work_clear": additions,
            "historical_real_primitives": historical, "lowerings": {"pr696": old, "replacement": new},
            "saved_real_primitives_vs_pr696": old["real_primitives"] - new["real_primitives"],
            "extra_real_source_reads_vs_pr696": new["real_macro_source_reads"] - old["real_macro_source_reads"],
            "non_scalar_event_indexed_sha256": non_scalar_digest.hexdigest(),
            "scalar_frame_indexed_sha256": frame_digest.hexdigest(),
            "paid_profile": {str(key): value for key, value in sorted(paid.items())}}


def local_word_check(op, word, *, coefficient_grid=False):
    """Three independent integer columns expose dirty scratch and prefix faults."""
    t, s = ("T", 0), ("S", 0)
    rows = {t: (0, {0: 1}), s: (0, {1: 1}), WORK: (0, {2: 1})}
    oracle = rows.copy()
    macro_oracle(oracle, op)
    initialized = False
    for instruction in word:
        require(tuple(instruction[1]) != s, "source register modified")
        primitive(rows, instruction)
        if tuple(instruction[1]) == WORK:
            initialized = True
        if coefficient_grid and initialized:
            scratch_power, scratch_values = rows[WORK]
            require(set(scratch_values) <= {1}, "dirty scratch dependency")
            n, power = reduced(op[3], op[4])
            require(scratch_power <= power, "coefficient grid excursion")
            require(abs(scratch_values.get(1, 0)) <= abs(n) * (1 << scratch_power),
                    "coefficient magnitude excursion")
    require(rows[WORK] == oracle[WORK], "dirty coefficient scratch")
    require(rows == oracle, "incorrect local macro endpoint")


def negative_controls(selected):
    t, s = ("T", 0), ("S", 0)
    op = ["add", list(t), list(s), 5, 2]
    word = emit_replacement(op, selected)
    local_word_check(op, word, coefficient_grid=True)
    half_index = next(i for i, instruction in enumerate(word) if instruction[0] == "halve")
    wrong_half = list(word)
    wrong_half[half_index] = ("double", WORK)
    cases = {
        "wrong_accumulation_sign": (op, word[:-2] + [("subtract", t, WORK)] + word[-1:], False,
                                    "incorrect local macro endpoint"),
        "dirty_scratch_missing_clear": (op, word[:-1], False, "dirty coefficient scratch"),
        "incorrect_halving": (op, wrong_half, False, "incorrect local macro endpoint"),
        "endpoint_neutral_grid_excursion":
            (op, word[:1] + [("halve", WORK)] * 2 + [("double", WORK)] * 2 + word[1:],
             True, "coefficient grid excursion"),
        "incorrect_scale_sign": (["scale", list(t), -2, 1], [("double", t)], False,
                                 "incorrect local macro endpoint"),
        "missing_source_copy": (op, word[1:], True, "dirty scratch dependency"),
    }
    result = {}
    for name, (macro, bad_word, grid, expected) in cases.items():
        try:
            local_word_check(macro, bad_word, coefficient_grid=grid)
        except VerificationError as error:
            require(str(error) == expected, "negative control failed for an unrelated reason: " + name)
            result[name] = str(error)
        else:
            raise VerificationError("accepted negative control: " + name)
    # Demonstrate that the grid control isolates a prefix violation: its endpoint
    # is nevertheless correct when the prefix guard is deliberately disabled.
    local_word_check(op, cases["endpoint_neutral_grid_excursion"][1], coefficient_grid=False)
    return result


def positive_controls():
    require(row(3, {0: -12, 1: 4}) == (1, {0: -3, 1: 1}), "row common-denominator normalization")
    require(row_sum((2, {0: 1}), (1, {0: -1, 1: 3})) == (2, {0: -1, 1: 6}),
            "unaligned denominator addition")
    require(row_multiple((0, {0: -1}), 1, 1) == (1, {0: -1}), "negative exact halving")
    require(row_sum((3, {0: 3}), (3, {0: 3}), -1) == ZERO, "exact cancellation")
    require(reduced(2, -1) == (-2, 0), "negative input denominator")
    require(naf_statistics(31) == (6, 2), "NAF carry control")
    return {"integer_row_arithmetic_cases": 5, "NAF_carry_cases": 1}


def verify(programs, checks, inherited, certificate):
    """Return independently reconstructed, deterministic scalar evidence."""
    require(set(programs) == {"forward", "backward"}, "program orientation coverage")
    positive = positive_controls()
    entries, selected = prepare_certificate(certificate, programs)
    programs_result = {orientation: replay_orientation(orientation, programs[orientation], checks[orientation], selected)
                       for orientation in ("forward", "backward")}
    return {"status": "PASS_JP8_INTEGER_SCALAR_CROSSCHECK", "schema": "jp8-integer-scalar-crosscheck/1",
            "input_semantic_sha256": {"programs": sha(programs), "checks": sha(checks),
                                      "inherited": sha(inherited), "certificate": sha(certificate)},
            "arithmetic": "normalized sparse integer rows with a common power-of-two denominator",
            "certificate_coefficients_checked": len(entries), "selected_replacements": len(selected),
            "selected_coefficients": [f"{n}/{d}" for n, d in sorted(selected, key=lambda key: (key[0] * 16 // key[1]))],
            "independently_recomputed_comparator_lengths": {
                f"{n}/{d}": comparator_lengths(n, d.bit_length() - 1) for n, d in sorted(selected)},
            "programs": programs_result, "positive_controls": positive,
            "negative_controls": negative_controls(selected),
            "scope": "Historical PR626 JP8 scalar projections only; no complex-event or multiplication-bound proof.",
            "finite_graph_optimality_rechecked": False, "kappa_claim": None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--programs", type=Path, default=PROVIDER / "LOCAL-PROGRAMS.json.gz")
    parser.add_argument("--checks", type=Path, default=PROVIDER / "LOCAL-CHECKS.json")
    parser.add_argument("--inherited", type=Path, default=PROVIDER / "INDEPENDENT-LOCAL-REPLAY.json")
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--json", action="store_true", help="print deterministic receipt")
    args = parser.parse_args()
    result = verify(read(args.programs), read(args.checks), read(args.inherited), read(args.certificate))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['status']} columns=725 orientations=2 independent_integer_macro_oracle=pass "
              f"negative_controls={len(result['negative_controls'])}")


if __name__ == "__main__":
    main()
