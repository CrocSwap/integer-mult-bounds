"""Sequential FOUR packet boundary with an explicit linear-width bill.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import sys
SOURCE = Path(__file__).resolve().parents[1] / "selected-complex-compact-adapters"
sys.path.insert(0, str(SOURCE))
from streams import Tape, need, copy, digit_permutation
from compact import Layout
from monomial import execute_monomial, binary_word


def reorder(source, labels, wanted, record_bits):
    """Move complete records by successive physical digit interchanges."""
    need(len(set(labels)) == len(labels) and set(labels) == set(wanted),
         "permutation must retain every axis")
    need(len(wanted) == len(labels), "permutation extent")
    current = list(labels)
    swaps = []
    for i, label in enumerate(wanted):
        j = current.index(label)
        if i != j:
            source = digit_permutation(source, len(labels), i, j, record_bits, (0, 2, 1, 3))
            current[i], current[j] = current[j], current[i]
            swaps.append((i, j))
    return source, swaps


def alias_layout(labels, column, record_bits):
    aliases = {axis: "v" + str(i) for i, axis in enumerate(column)}
    return Layout(tuple((aliases.get(axis, "spectator_" + str(j)), 1)
                        for j, axis in enumerate(labels)), record_bits)


def boundary(source, output, labels, columns, right, left, rank,
             coefficient_bits, child):
    """Preserve source, call one complete child, and replace owned output."""
    need(source is not output and source.meter is output.meter, "distinct owned output")
    need(source.head == output.head == 0, "boundary heads must be at origin")
    need(len(set(labels)) == len(labels), "duplicate physical axis")
    need(columns and all(len(c) == 9 for c in columns), "nine-bit source columns")
    axes = [x for col in columns for x in col]
    need(len(set(axes)) == len(axes) and set(axes) <= set(labels), "invalid active axes")
    need(rank == 3 and coefficient_bits >= 2, "event8814 interface")
    record_bits = 2 * coefficient_bits
    volume = (1 << len(labels)) * record_bits
    need(len(source.data) == volume, "complete payload rectangle")
    old_output = len(output.data)
    work = Tape(source.meter)
    copy(source, work, volume)
    source.finish(); source.rewind(); work.rewind()
    # The retained fixture's native chart d exchanges axes 0 and 1.
    for col in columns:
        a, b = sorted((labels.index(col[0]), labels.index(col[1])))
        work = digit_permutation(work, len(labels), a, b, record_bits, (0, 2, 1, 3))
        work = execute_monomial(work, alias_layout(labels, col, record_bits),
                                right, 1, 1, 1, 0, coefficient_bits)
    active = [axis for col in reversed(columns) for axis in reversed(col[:rank])]
    wanted = list(labels)
    for i, axis in enumerate(active):
        j = wanted.index(axis)
        wanted[i], wanted[j] = wanted[j], wanted[i]
    work, swaps = reorder(work, labels, wanted, record_bits)
    returned = child(work, len(active), tuple(wanted), record_bits)
    need(returned is not source and returned is not output and returned.meter is source.meter,
         "child returned a caller-owned tape")
    need(returned.head == 0 and len(returned.data) == volume, "child return shape")
    need(returned is work or not work.data, "child did not retire its input")
    work = returned
    for a, b in reversed(swaps):
        work = digit_permutation(work, len(labels), a, b, record_bits, (0, 2, 1, 3))
    for col in columns:
        work = execute_monomial(work, alias_layout(labels, col, record_bits),
                                left, 1, 1, 1, 0, coefficient_bits)
        a, b = sorted((labels.index(col[0]), labels.index(col[1])))
        work = digit_permutation(work, len(labels), a, b, record_bits, (0, 2, 1, 3))
    output.erase()
    copy(work, output, volume)
    work.finish(); work.erase(); output.rewind()
    passes = len(columns) * (len(binary_word(right)) + len(binary_word(left)) + 4) + 2 * len(swaps)
    return {"volume": volume, "old_output": old_output, "columns": len(columns),
            "ordering_swaps_each_way": len(swaps), "full_volume_passes": passes,
            "wrapper_transitions": 18 * volume * passes + 15 * volume + 3 * old_output,
            "child_calls": 1, "ordinary_calls": 0}
