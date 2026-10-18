"""Independent grouping and exact column replay of emitted fan-in blocks.

Sagar Thakrar with substantial OpenAI Codex assistance. Apache-2.0.
Uses the emitter under test and source admission, not their grouping or replay.
"""
from fractions import Fraction
from itertools import groupby
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lowering import lower
from verify import read_sources

WORK = ("W", 0)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def independent_blocks(events):
    """Partition the literal event positions, including every hard boundary."""
    labelled = []
    phase = None
    for index, event in enumerate(events):
        label = None
        if event[0] == "phase":
            phase = event[1]
        if phase == "full_frame_cleanup" and event[0] == "scalar" and event[2] == 1:
            op = event[1]
            if op[0] == "add":
                target, source = tuple(op[1]), tuple(op[2])
                q = abs(Fraction(op[3], op[4]))
                if target[0] == source[0] == "L" and target != source and q not in (0, 1):
                    check(q.denominator & (q.denominator - 1) == 0, "non-dyadic source")
                    label = (target, q)
        labelled.append((label, index))
    for label, run in groupby(labelled, key=lambda item: item[0]):
        positions = [index for _, index in run]
        if label is not None and len(positions) >= 2:
            yield positions[0], positions[-1] + 1


def primitive_column(program, column, positions):
    """An input column is one flat vector of scalar register values."""
    values = column.copy()
    for instruction in program:
        tag = instruction[0]
        target = positions[instruction[1]]
        if tag == "clear":
            check(len(instruction) == 2, "clear arity")
            values[target] = Fraction(0)
        elif tag == "add":
            check(len(instruction) == 4, "add arity")
            source, sign = positions[instruction[2]], instruction[3]
            check(source != target and sign in (-1, 1), "signed-add contract")
            values[target] += sign * values[source]
        elif tag in ("double", "half"):
            check(len(instruction) == 2, "scale arity")
            values[target] *= Fraction(2) if tag == "double" else Fraction(1, 2)
        else:
            raise ValueError("unknown primitive: " + str(tag))
    return values


def check_block(block):
    operations = [event[1] for event in block]
    registers = sorted({tuple(op[1]) for op in operations}
                       | {tuple(op[2]) for op in operations} | {WORK})
    positions = {register: index for index, register in enumerate(registers)}
    program = lower(block)
    check(program[-1] == ("clear", WORK), "missing declared final clear")
    rejected_clear_mutation = False
    for incoming in range(len(registers)):
        column = [Fraction(int(index == incoming)) for index in range(len(registers))]
        expected = column.copy()
        for op in operations:
            target, source = positions[tuple(op[1])], positions[tuple(op[2])]
            expected[target] += Fraction(op[3], op[4]) * expected[source]
        expected[positions[WORK]] = Fraction(0)
        check(primitive_column(program, column, positions) == expected,
              "emitted boundary column differs")
        if primitive_column(program[:-1], column, positions) != expected:
            rejected_clear_mutation = True
    check(rejected_clear_mutation, "omitted final clear was undetected")
    baseline = 0
    for op in operations:
        q = abs(Fraction(op[3], op[4]))
        baseline += 3 + q.numerator.bit_length() - 1 + q.numerator.bit_count()
        baseline += q.denominator.bit_length() - 1
    check(len(program) < baseline, "block does not save charged work")
    return baseline, len(program), len(registers)


def main():
    _, programs, _, _ = read_sources()
    check(list(independent_blocks(programs["forward"])) == [], "forward inventory changed")
    events = programs["backward"]
    blocks = list(independent_blocks(events))
    additions = sum(end - start for start, end in blocks)
    baseline = lowered = columns = 0
    for start, end in blocks:
        old, new, count = check_block(events[start:end])
        baseline += old
        lowered += new
        columns += count
    check((len(blocks), additions, baseline, lowered, columns)
          == (999, 3022, 18075, 8231, 5020), "independent inventory or cost differs")
    print("PASS_JP8_FANIN_COLUMNS blocks=999 local_columns=5020 "
          "real_saved=19688 omitted_clear_rejections=999")


if __name__ == "__main__":
    main()
