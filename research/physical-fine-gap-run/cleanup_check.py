"""Separate source-aware live-prefix cleanup check, adapted for pinned runtime.
Prepared for @CubeJerry with separate OpenAI Codex assistance. Apache-2.0.
This is external verification, not part of the online consumer.
"""


def run(Tape, blank):
    def metrics(tape):
        return tuple(getattr(tape.meter, key) for key in ("reads", "writes", "moves"))

    def roundtrip(tape, length):
        before = metrics(tape)
        for i in range(length):
            tape.append(i % 2)
        tape.rewind(); tape.clear()
        after = metrics(tape)
        if tape.head != 1 or any(cell != blank for cell in tape.cells[1:]):
            raise ValueError("nonempty or misplaced current-body clear")
        return tuple(a-b for a, b in zip(after, before))

    checks = []
    for history in (1, 8, 128, 4096):
        old = Tape()
        roundtrip(old, history)
        retained = len(old.cells)
        for current in (0, 1, 3, 7):
            actual = roundtrip(old, current)
            expected = roundtrip(Tape(), current)
            if actual != expected:
                raise ValueError("history-dependent physical cleanup actions")
            if len(old.cells) < retained:
                raise ValueError("retained backing was silently deallocated")
            checks.append(dict(history=history, current=current, actions=actual,
                               retained_cells=len(old.cells)))
    return checks
