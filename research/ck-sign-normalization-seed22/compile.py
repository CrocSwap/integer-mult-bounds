"""Exact lazy-sign compilation within a single scalar frame.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
This compiler is new; the consumed primitive lowering is Sagar Thakrar's PR696.
"""


def optimize_run(primitives):
    """Return an explicit primitive word with identical boundary register values.

    Logical value = (-1 if register in negative else 1) * physical value.
    All pending signs are materialized before returning. No state crosses runs.
    Copy fanout can increase cost in general; no universal saving is asserted.
    """
    negative, result = set(), []
    for instruction in primitives:
        tag, target = instruction[:2]
        if tag == "negate":
            negative.symmetric_difference_update((target,))
            continue
        if tag in ("add", "subtract"):
            source = instruction[2]
            if (target in negative) != (source in negative):
                tag = "subtract" if tag == "add" else "add"
            result.append((tag, target, source))
        elif tag == "copy":
            source = instruction[2]
            sign = source in negative
            negative.discard(target)
            if sign:
                negative.add(target)
            result.append(instruction)
        elif tag == "clear":
            negative.discard(target)
            result.append(instruction)
        elif tag in ("double", "halve"):
            result.append(instruction)
        else:
            raise ValueError("unknown primitive: " + str(tag))
    result.extend(("negate", register) for register in sorted(negative))
    return result
