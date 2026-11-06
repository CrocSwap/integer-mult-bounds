"""Shared-counter tape scan, produced by Nick Petalas. Apache-2.0.

The two-phase coordinate algorithm follows PR6151, also by Nick Petalas.
Only marker/bit reads, writes and unit moves access runtime tape contents.
"""


def rewind(tape):
    tape.move(-1)
    while tape.read() != "^":
        tape.move(-1)
    tape.move(1)


def next_block(work):
    """Move from one block's first bit to the next block's first bit."""
    while work.read() != "$":
        work.move(1)
    work.move(1)
    work.move(1)


def previous_block(work):
    """Cross the two delimiters, then rewind the previous block."""
    work.move(-1)
    work.move(-1)
    rewind(work)


def borrow(work):
    while True:
        bit = work.read()
        if bit == "$":
            rewind(work)
            return True
        if bit == "1":
            work.write("0")
            rewind(work)
            return False
        if bit != "0":
            raise ValueError("invalid counter symbol")
        work.write("1")
        work.move(1)


def load(descriptor, work, complement=False):
    nonzero = False
    while True:
        bit = descriptor.read()
        if bit == "$":
            break
        if bit not in ("0", "1"):
            raise ValueError("invalid descriptor symbol")
        value = ("1" if bit == "0" else "0") if complement else bit
        nonzero = nonzero or value == "1"
        work.write(value)
        descriptor.move(1)
        work.move(1)
    if work.read() != "$":
        raise ValueError("counter width mismatch")
    rewind(descriptor)
    rewind(work)
    return nonzero


def clear(work):
    while work.read() != "$":
        work.write("0")
        work.move(1)
    rewind(work)


def advance(descriptor, work, genuine):
    """Return (carry, next phase), leaving the shared head at this block."""
    if not borrow(work):
        return False, genuine
    if genuine and load(descriptor, work, True):
        if borrow(work):
            raise RuntimeError("nonzero padding countdown underflowed")
        return False, False
    load(descriptor, work)
    return True, True


def initialize(descriptors, work):
    for index in range(5):
        load(descriptors[index], work)
        if index < 4:
            next_block(work)
    for _ in range(4):
        previous_block(work)


def finish(work):
    for index in range(5):
        clear(work)
        if index < 4:
            next_block(work)
    for _ in range(4):
        previous_block(work)


def emit(source, target, genuine, restrict):
    if restrict:
        bit = source.read()
        if bit not in ("0", "1"):
            raise ValueError("short or nonbinary source")
        source.move(1)
        if genuine:
            target.write(bit)
            target.move(1)
    else:
        bit = "0"
        if genuine:
            bit = source.read()
            if bit not in ("0", "1"):
                raise ValueError("short or nonbinary source")
            source.move(1)
        target.write(bit)
        target.move(1)


def scan(descriptors, work, source, target, control, restrict=False):
    """Five descriptors and work blocks are ordered fastest to slowest.

    There is exactly one work tape and one work head. Entry shapes, markers,
    ownership and source lengths are promised; this is not a hostile parser.
    """
    if len(descriptors) != 5:
        raise ValueError("five descriptors required")
    genuine = [True] * 5
    initialize(descriptors, work)
    while True:
        control("emit")
        emit(source, target, all(genuine), restrict)
        for index in range(5):
            control("advance")
            carry, genuine[index] = advance(descriptors[index], work, genuine[index])
            if not carry or index == 4:
                break
            next_block(work)
        for _ in range(index):
            previous_block(work)
        if carry and index == 4:
            break
    if source.read() != "$":
        raise ValueError("long source")
    target.write("$")
    rewind(source)
    rewind(target)
    finish(work)
