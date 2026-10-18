"""Recursive reference for the retained Root/Good/FallbackPair value grammar.

Adapted from commdata2338's PR2188 descriptor, as retained by PR2234.
The new stack implementation does not call this reference.
Apache-2.0; see NOTICE.md for the exact source and modifications.
"""
from control import need


def value(program, tables, level, index):
    sizes = program.extents()
    need(0 <= index < sizes[level], "reference index")
    modulus = program.q**program.width
    if level == 0:
        return program.unit % modulus
    step = program.steps[level - 1]
    if step.kind == "unit":
        return 1
    table = tables[level - 1]
    need(table.tag == step.tag, "reference field binding")
    f = sizes[level - 1] // 64
    if step.kind == "good":
        return value(program, tables, level - 1, index) * table.pivots[index // f] % modulus
    column = f - 1 - index if step.reverse else index
    def bank(row):
        return value(program, tables, level - 1, row * f + column) if row < 64 else 1
    return (table.diagonal[step.field] * bank(table.permutation[step.field]) *
            pow(bank(step.field), -1, modulus)) % modulus
