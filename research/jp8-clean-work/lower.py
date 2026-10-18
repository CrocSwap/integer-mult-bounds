"""Conservative clean-work specialization of Sagar Thakrar's PR696 lowering.

faw01, with substantial OpenAI Codex assistance. Apache-2.0.
The supplied macro lowerer must have PR696's zero-work addition postcondition.
"""
from fractions import Fraction

WORK = ("W", 0)
BARRIERS = {"phase", "climb", "center", "adapter", "residual_adapter"}


def scalar_operands(op):
    """Reject macros that could read or write the private coefficient register."""
    tag = op[0]
    if tag not in {"add", "scale", "copy", "clear"}:
        raise ValueError("unknown scalar macro")
    operands = [tuple(op[1])]
    if tag in {"add", "copy"}:
        operands.append(tuple(op[2]))
    if any(len(r) != 2 or r[0] not in {"L", "C"} or
           type(r[1]) is not int or r[1] < 0 for r in operands):
        raise ValueError("scalar operand is not a logical/center register")
    return operands


def specialize(events, macro_lower):
    """Yield (event index, primitive word, preceding-add witness or None).

    Every non-scalar event and every frame change invalidates the knowledge.
    No assumption about private-work transport through a child or adapter is
    needed. Scale/copy/clear macros on L/C preserve existing knowledge.
    """
    previous_frame = None
    last_add = None
    for index, event in enumerate(events):
        if event[0] != "scalar":
            if event[0] not in BARRIERS:
                raise ValueError("unknown event")
            previous_frame = last_add = None
            yield index, (), None
            continue
        _, op, frame = event
        operands = scalar_operands(op)
        if frame != previous_frame:
            last_add = None
        previous_frame = frame
        word = tuple(macro_lower(op, WORK))
        witness = None
        if op[0] == "add":
            coefficient = Fraction(op[3], op[4])
            if abs(coefficient) == 1 and last_add is not None:
                sign = "add" if coefficient > 0 else "subtract"
                if word != ((sign, operands[0], operands[1]), ("clear", WORK)):
                    raise ValueError("unexpected unit lowering")
                word = word[:-1]
                witness = last_add
            last_add = index
        yield index, word, witness
