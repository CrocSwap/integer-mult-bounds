"""Direct odd-count return; frozen cached-borrow body otherwise unchanged.

Credit Nick Petalas/6495, Arham Tahir/2877, David Arias/2753 and
Jose Manuel/2697. New branch by ToikY with OpenAI Codex assistance.
Apache-2.0.
"""
ZERO, ONE, LEFT, RIGHT, BLANK = range(5)


def decrement(counter):
    if counter.finished:
        raise ValueError("positive countdown")
    tape = counter.tape
    digit = tape.read()
    if digit == ONE:
        tape.write(ZERO)
        tape.step(1)
        if tape.read() == RIGHT:
            counter.finished = True
        tape.step(-1)
        return
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
