"""A paid clean-row schedule for all nonempty source masks.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source order is the classical binary reflected Gray cycle.
"""


def schedule(n):
    if type(n) is not int or n < 1:
        raise ValueError("positive integer source count required")
    yield ("INIT", 0)
    previous = 0
    for k in range(1, 1 << n):
        mask = k ^ (k >> 1)
        yield ("B", (mask ^ previous).bit_length() - 1)
        yield ("A", mask)
        previous = mask
    yield ("B", previous.bit_length() - 1)
    yield ("RELEASE", 0)


def execute(word, sources, dirty, targets, fresh, source_map, output_map):
    """Run complete map calls. INIT pays for owned allocation and zeroing."""
    c, out = fresh, list(targets)
    initialized = released = False
    for op, index in word:
        if op == "INIT":
            if initialized or released or index != 0:
                raise ValueError("invalid allocation")
            c = 0
            initialized = True
        elif not initialized or released:
            raise ValueError("operation outside owned lifetime")
        elif op == "B":
            if not 0 <= index < len(sources):
                raise ValueError("source index")
            c ^= source_map(sources[index], index)
        elif op == "A":
            if not 1 <= index <= len(targets):
                raise ValueError("output mask")
            out[index - 1] ^= output_map(c, index)
        elif op == "RELEASE":
            if c or index != 0:
                raise ValueError("owned row not zero at release")
            released = True
        else:
            raise ValueError("unknown operation")
    if not released:
        raise ValueError("missing release")
    return list(sources), dirty, out, c
