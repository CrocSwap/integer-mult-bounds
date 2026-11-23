"""Exercise the seven binary stage stacks and the Gaussian historical allocator."""

from contextlib import ExitStack
from io import BytesIO

from check_stage_inventory import inventory


def verify():
    from stack_tapes import Arena
    from spool import Arena as GaussianArena

    kinds = inventory()
    stages = [Arena() for _ in range(7)]
    maxima = [{} for _ in stages]

    def visit(stage, level):
        arena = stages[stage]
        records = []
        with ExitStack() as scope:
            for site, arity in kinds.items():
                for i, page in enumerate(scope.enter_context(arena.frames(site, arity))):
                    data = bytes([(71 * stage + 19 * level + i + len(site)) % 255 + 1])
                    data *= 19 + stage + 3 * level + i
                    page.write(data)
                    records.append((page, data))
                    key = site, i
                    maxima[stage][key] = max(maxima[stage].get(key, 0), page.base + len(data))
            pending, answers = arena.pending, arena.answers
            pending_top, answers_top = pending.top, answers.top
            argument = bytes([stage + 1, level + 1]) * 13
            expected = argument[::-1]
            source = BytesIO(argument)
            source.seek(len(argument))
            pending.push_reverse(source, len(argument))
            answers.append(BytesIO(expected), len(expected))
            for key, top in ((("pending", 0), pending.top), (("answers", 0), answers.top)):
                maxima[stage][key] = max(maxima[stage].get(key, 0), top)
            if level:
                visit(stage, level - 1)
            elif stage:
                visit(stage - 1, 2)
            for page, data in records:
                page.seek(0)
                assert page.read() == data
            restored = BytesIO()
            pending.pop_forward(restored, len(argument))
            assert restored.getvalue() == argument and pending.top == pending_top
            restored = BytesIO()
            answers.take_answers(answers_top, restored)
            assert restored.getvalue() == expected and answers.top == answers_top

    try:
        # Use the same historical addresses for a second sibling after the first returns.
        visit(6, 2)
        visit(6, 2)
        for arena, extent in zip(stages, maxima, strict=True):
            assert len(arena.heads) == 20
            for key, head in arena.heads.items():
                assert not head.frames and head.peak == extent[key]
                head.file.seek(0)
                assert head.file.read() == bytes(head.peak)
        peaks = sum(arena.counts()[2] for arena in stages)
        moves = sum(arena.counts()[1] for arena in stages)
    finally:
        for arena in stages:
            arena.close()

    gaussian = GaussianArena(4, 1)
    try:
        roots = [gaussian.field() for _ in range(4)]
        for i, field in enumerate(roots):
            field.stream.write(bytes([i + 1]) * gaussian.extent)
        roots.pop().retire()
        assert gaussian.high == 4 and gaussian.live == 3
        starts = []
        for _ in range(2):
            with gaussian.child(2) as child:
                starts.append(child.start)
                assert child.start == 4 * gaussian.extent
                fields = [child.field() for _ in range(5)]
                for field in fields:
                    field.stream.write(b"q" * child.extent)
                fields[-1].retire()
                with child.child(1) as inner:
                    assert inner.start == child.start + 5 * child.extent
                    field = inner.field()
                    field.stream.write(b"r" * inner.extent)
                    field.retire()
                for field in fields[:-1]:
                    field.stream.seek(0)
                    assert field.stream.read(child.extent) == b"q" * child.extent
                    field.retire()
        assert starts[0] == starts[1]
        for i, field in enumerate(roots):
            field.stream.seek(0)
            assert field.stream.read(gaussian.extent) == bytes([i + 1]) * gaussian.extent
            field.retire()
    finally:
        gaussian.close()

    assert (peaks, moves, starts[0]) == (10752, 125062, 128)
    print("seven binary stages, 20 arena heads and 91 scratch slots per stage;",
          "historical bytes", peaks, "charged movements", moves, "Gaussian sibling base", starts[0])


if __name__ == "__main__":
    verify()
