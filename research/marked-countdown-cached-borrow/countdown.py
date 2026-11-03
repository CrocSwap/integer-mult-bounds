"""Cached borrow terminator for the retained marked binary countdown.

Produced by Nick Petalas. Apache-2.0.
The marked-counter algorithm and tape vocabulary retain Jose Manuel's credit.
"""


ZERO, ONE, LEFT, RIGHT, BLANK = range(5)


def decrement(counter):
    """Decrement a positive canonical Counter, saving exactly one tape read.

    Entry and exit head: first digit. The zero borrow traverses at most the
    current encoded digit width. No runtime cardinality enters host control.
    Tape symbols are ZERO=0, ONE=1, LEFT=2, RIGHT=3, BLANK=4 in the pinned ABI.
    """
    if counter.finished:
        raise ValueError("positive countdown")
    tape = counter.tape
    digit = tape.read()
    while digit == ZERO:
        tape.write(ONE)
        tape.step(1)
        digit = tape.read()
    if digit != ONE:
        raise ValueError("canonical positive counter")
    tape.write(ZERO)
    tape.step(1)
    if tape.read() == RIGHT:
        tape.write(BLANK)
        tape.step(-1)
        tape.step(-1)
        if tape.read() == LEFT:
            tape.step(1)
            tape.write(ZERO)
            tape.step(1)
            tape.write(RIGHT)
            counter.finished = True
        else:
            tape.step(1)
            tape.write(RIGHT)
    tape.rewind()
