"""Independent segmentation and scalar-basis check of the local rescaling witness.

Prepared for Jeff Cox (@namredips) with substantial OpenAI Codex assistance.
Apache-2.0. This checker does not import the planner or its cost functions.
"""

from collections import Counter
from fractions import Fraction
from itertools import pairwise

WORK = ("W", 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _log2_power(value):
    """Integer division recognizes exact powers independently of bit lengths."""
    numerator, denominator = value.numerator, value.denominator
    if numerator <= 0:
        return None
    exponent = 0
    while numerator % 2 == 0:
        numerator //= 2
        exponent += 1
    while denominator % 2 == 0:
        denominator //= 2
        exponent -= 1
    return exponent if numerator == denominator == 1 else None


def _horner_work(coefficient):
    digits = bin(abs(coefficient.numerator))[2:]
    denominator_power = _log2_power(Fraction(coefficient.denominator))
    require(coefficient != 0 and denominator_power is not None,
            "crosscheck requires nonzero dyadic coefficients")
    return len(digits) - 1 + digits.count("1") + denominator_power


def _runs(events):
    """Maximal consecutive nonunit, full-frame, fixed-source cleanup runs."""
    phase, source, current, runs = None, None, [], []
    for index, event in enumerate(events):
        if event[0] == "phase":
            phase = event[1]
        candidate = None
        if (phase == "full_frame_cleanup" and event[0] == "scalar"
                and event[2] == 1 and event[1][0] == "add"):
            op = event[1]
            target, source_register = tuple(op[1]), tuple(op[2])
            coefficient = Fraction(op[3], op[4])
            if (target[0] == source_register[0] == "L"
                    and target != source_register and abs(coefficient) != 1):
                _horner_work(coefficient)
                candidate = (index, coefficient, source_register)
        if candidate is None or candidate[2] != source:
            if current:
                runs.append(current)
            current = []
        if candidate is not None:
            current.append(candidate)
            source = candidate[2]
        else:
            source = None
    if current:
        runs.append(current)
    return runs


def _optimal_partition(run):
    """Dynamic programming over every permitted final block of each prefix.

    Minimize primitive cost, then prefer more blocks at equal cost. The latter
    canonically cuts all zero-saving edges, avoiding needless work lifetimes.
    """
    costs, partitions, candidate_blocks = [0], [[]], 0
    for stop in range(1, len(run) + 1):
        best, best_partition, shift_cost = None, None, 0
        for start in range(stop - 1, -1, -1):
            if start < stop - 1:
                step = _log2_power(abs(run[start + 1][1] / run[start][1]))
                if step is None:
                    break
                shift_cost += abs(step)
            block_cost = _horner_work(run[start][1]) + 2 + stop - start + shift_cost
            partition = partitions[start] + [(run[start][0], run[stop - 1][0] + 1)]
            key = (costs[start] + block_cost, -len(partition))
            candidate_blocks += 1
            if best is None or key < best:
                best, best_partition = key, partition
        costs.append(best[0])
        partitions.append(best_partition)
    return costs[-1], partitions[-1], candidate_blocks


def _execute(values, circuit):
    for instruction in circuit:
        op, target = instruction[:2]
        require(target in values, "circuit writes an undeclared register")
        if op == "clear":
            values[target] = Fraction(0)
        elif op == "double":
            values[target] *= 2
        elif op == "halve":
            values[target] /= 2
        elif op == "neg":
            values[target] = -values[target]
        elif op in ("copy", "inc"):
            source = instruction[2]
            require(source in values, "circuit reads an undeclared register")
            if op == "copy":
                values[target] = values[source]
            else:
                require(instruction[3] in (-1, 1), "nonprimitive signed addition")
                values[target] += instruction[3] * values[source]
        else:
            raise ValueError("unknown primitive: " + str(op))


def _check_map(events, circuit):
    """One scalar replay per basis vector, including the incoming work vector."""
    live = {tuple(event[1][i]) for event in events for i in (1, 2)}
    registers = sorted(live | {WORK})
    for basis in registers:
        actual = {register: Fraction(register == basis) for register in registers}
        expected = actual.copy()
        for event in events:
            op = event[1]
            expected[tuple(op[1])] += Fraction(op[3], op[4]) * expected[tuple(op[2])]
        expected[WORK] = Fraction(0)
        _execute(actual, circuit)
        require(actual == expected, "block boundary differs on basis " + str(basis))
    return len(registers)


def _semantic_controls(events, circuit):
    """The first selected block witnesses dirty work, erasure, sign and shift."""
    require(circuit[0] == circuit[-1] == ("clear", WORK),
            "selected circuit must clear work at entry and exit")
    mutations = [("missing_entry_clear", circuit[1:]),
                 ("missing_exit_clear", circuit[:-1])]
    accumulate = next(i for i, op in enumerate(circuit)
                      if op[0] == "inc" and op[1] != WORK)
    changed = list(circuit)
    op = changed[accumulate]
    changed[accumulate] = (*op[:3], -op[3])
    mutations.append(("wrong_accumulation_sign", changed))
    for index in range(accumulate + 1, len(circuit)):
        if circuit[index][0] in ("double", "halve"):
            changed = list(circuit)
            op = changed[index]
            changed[index] = ("halve" if op[0] == "double" else "double", op[1])
            mutations.append(("wrong_rescale_direction", changed))
            break
    rejected = []
    for name, changed in mutations:
        try:
            _check_map(events, changed)
        except ValueError as error:
            require(str(error).startswith("block boundary differs"),
                    "negative control failed for an unrelated reason: " + name)
            rejected.append(name)
        else:
            raise ValueError("semantic negative control accepted: " + name)
    return rejected


def crosscheck(events, spans, lower_block):
    """Check the complete restricted optimum and every supplied primitive map."""
    runs = _runs(events)
    expected_spans, baseline, optimum, candidate_blocks = [], 0, 0, 0
    rejected_edges, profitable_edges = Counter(), Counter()
    incompatible_edges = 0
    for run in runs:
        baseline += sum(_horner_work(entry[1]) + 3 for entry in run)
        cost, partition, checked = _optimal_partition(run)
        optimum += cost
        candidate_blocks += checked
        expected_spans.extend(span for span in partition if span[1] - span[0] > 1)
        for previous, following in pairwise(run):
            left, right = abs(previous[1]), abs(following[1])
            step = _log2_power(right / left)
            if step is None:
                incompatible_edges += 1
                continue
            gain = _horner_work(right) + 2 - abs(step)
            if gain > 0:
                profitable_edges["equal_magnitude" if left == right else "distinct_magnitude"] += 1
            else:
                rejected_edges[(str(left), str(right), step, -2 * gain)] += 1
    supplied_spans = [tuple(span) for span in spans]
    require(supplied_spans == expected_spans,
            "provided spans differ from canonical dynamic-programming optimum")
    basis_cases, actual_saved, primitive_count, controls = 0, 0, 0, []
    for start, stop in supplied_spans:
        block = events[start:stop]
        circuit = lower_block(block)
        coefficients = [Fraction(*event[1][3:]) for event in block]
        standalone = sum(_horner_work(q) + 3 for q in coefficients)
        block_cost = _horner_work(coefficients[0]) + 2 + len(block)
        block_cost += sum(abs(_log2_power(abs(right / left)))
                          for left, right in pairwise(coefficients))
        require(len(circuit) == block_cost,
                "emitted block length differs from independent cost")
        basis_cases += _check_map(block, circuit)
        actual_saved += standalone - len(circuit)
        primitive_count += len(circuit)
        if not controls:
            controls = _semantic_controls(block, circuit)
    require(actual_saved == baseline - optimum,
            "emitted primitive length differs from independent optimum")
    return {
        "status": "PASS_INDEPENDENT_DP_AND_SCALAR_BASIS",
        "eligible_additions": sum(map(len, runs)),
        "maximal_fixed_source_runs": len(runs),
        "largest_run": max(map(len, runs), default=0),
        "dp_candidate_blocks_checked": candidate_blocks,
        "selected_blocks": len(supplied_spans),
        "scalar_basis_inputs_checked": basis_cases,
        "selected_block_component_primitives": primitive_count,
        "eligible_singleton_component_primitives": baseline,
        "eligible_optimal_component_primitives": optimum,
        "saved_real_component_primitives": 2 * actual_saved,
        "profitable_edges": dict(sorted(profitable_edges.items())),
        "incompatible_odd_numerator_edges": incompatible_edges,
        "nonpositive_transition_count": sum(rejected_edges.values()),
        "nonpositive_transition_census": [
            {"from_magnitude": left, "to_magnitude": right, "shift": step,
             "extra_real_primitives_if_merged": extra, "count": count}
            for (left, right, step, extra), count in sorted(rejected_edges.items())
        ],
        "semantic_negative_controls_rejected": controls,
        "scope": "Finite primitive maps on arbitrary live/work input; exact DP optimum only within fixed-source, ordered power-of-two rescaling blocks.",
    }
