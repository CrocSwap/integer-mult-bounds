"""Compose signed-digit preparation and shared complex cleanup work.

Prepared for Gareth Davidson (@bitplane) with substantial OpenAI Codex
assistance. Apache-2.0. The binary fallback is Sagar Thakrar's PR696
lowering, preserved verbatim under vendor/ with its attribution.
Cleanup sharing adapts ellipsi2's PR722; concurrent PR723 independently
supplies the matching JP8 signed-digit result. See README.md for all pins.
"""

import importlib.util
from fractions import Fraction
from pathlib import Path


def load_reference():
    path = Path(__file__).resolve().parent / "vendor" / "pr696_lower.py"
    spec = importlib.util.spec_from_file_location("pr696_reference", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reference = load_reference()


def signed_digits(n):
    """Most-significant-first non-adjacent binary digits of a positive int."""
    if type(n) is not int or n <= 0:
        raise ValueError("expected a positive integer")
    digits = []
    while n:
        digit = 0 if n % 2 == 0 else 2 - n % 4
        digits.append(digit)
        n = (n - digit) // 2
    return tuple(reversed(digits))


def lower(op, work=("W", 0)):
    """Emit priced real primitives, retaining the binary word on ties.

    Logical source and target must be distinct from work. Incoming work may
    be arbitrary and is cleared at each addition's exit, exactly as in PR696.
    The caller executes every primitive at the original scalar macro's frame.
    """
    binary = reference.lower(op, work)
    if op[0] != "add":
        return binary
    q = Fraction(op[3], op[4])
    if abs(q) == 1:
        return binary
    source, target = tuple(op[2]), tuple(op[1])
    digits = signed_digits(abs(q.numerator))
    candidate = [("copy", work, source)]
    for digit in digits[1:]:
        candidate.append(("double", work))
        if digit:
            candidate.append(("add" if digit == 1 else "subtract", work, source))
    candidate.extend([("halve", work)] * (q.denominator.bit_length() - 1))
    candidate.extend([
        ("add" if q > 0 else "subtract", target, work),
        ("clear", work),
    ])
    return candidate if len(candidate) < len(binary) else binary


def sharing_key(event):
    """PR722's fixed-full-frame, unchanged-source/non-unit sharing class."""
    if event[0] != "scalar" or event[2] != 1 or event[1][0] != "add":
        return None
    op = event[1]
    # Reuse the reference's nonzero/dyadic/alias validation.
    reference.lower(op)
    q = abs(Fraction(op[3], op[4]))
    return (tuple(op[2]), q) if q != 1 else None


def blocks(events):
    """Partition exact events; sharing is restricted to full-frame cleanup.

    Adapted from ellipsi2's PR722 grouping rule. Every intervening event,
    frame change, coefficient change or source change terminates a block.
    """
    phase, index = None, 0
    while index < len(events):
        event = events[index]
        if event[0] == "phase":
            phase = event[1]
        key = sharing_key(event) if phase == "full_frame_cleanup" else None
        stop = index + 1
        if key is not None:
            while stop < len(events) and sharing_key(events[stop]) == key:
                stop += 1
        yield index, events[index:stop]
        index = stop


def lower_block(events, work=("W", 0), signed=True):
    """Prepare once, accumulate in original order, clear at block exit."""
    if not events or any(e[0] != "scalar" for e in events):
        raise ValueError("expected a nonempty scalar block")
    lowering = lower if signed else reference.lower
    if len(events) == 1:
        return lowering(events[0][1], work)
    key = sharing_key(events[0])
    if key is None or any(sharing_key(e) != key for e in events):
        raise ValueError("incompatible sharing block")
    # Validation with the actual work register is needed before composition.
    for event in events:
        reference.lower(event[1], work)
    result = lowering(events[0][1], work)[:-2]
    for _, op, _ in events:
        sign = Fraction(op[3], op[4]) > 0
        result.append(("add" if sign else "subtract", tuple(op[1]), work))
    result.append(("clear", work))
    return result
