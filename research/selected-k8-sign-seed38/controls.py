"""Actual selected-word mutations and boundary/accounting controls.

Scratch-net with substantial OpenAI Codex assistance. Apache-2.0.
"""


def compare(checker, before, after, precision=False):
    registers = {reg for word in (before, after) for p in word for reg in p[1:]}
    endpoints, envelopes = [], []
    for word in (before, after):
        rows = checker.identity(registers)
        peaks = {reg: (1, 1) for reg in registers}
        depths = {reg: 0 for reg in registers}
        for p in word:
            checker.step(rows, p)
            dst = p[1]
            peaks[dst] = checker.maximum(peaks[dst], checker.norm(rows[dst]))
            depths[dst] = max(depths[dst], rows[dst][1])
        endpoints.append(rows)
        envelopes.append((peaks, depths))
    checker.require(endpoints[0] == endpoints[1], "control endpoint differs")
    if precision:
        checker.require(envelopes[0] == envelopes[1], "control prefix differs")


def rejection(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def run(primary, checker):
    programs, _ = primary.selected_inputs()
    rejected, flush_omissions, update_omissions = 0, 0, 0
    for direction in ("backward", "forward"):
        changed = 0
        for _, _, block in checker.runs(programs[direction]):
            before = [p for e in block for p in checker.lower(e[1])]
            after = checker.compile_signs(before)
            if len(after) == len(before):
                continue
            checker.require(len(after) < len(before), "unexpected cost-increasing run")
            compare(checker, before, after, precision=True)
            if after[-1][0] == "negate":
                omission = len(after) - 1
                flush_omissions += 1
            else:
                omission = max(i for i, p in enumerate(after)
                               if p[0] in ("add", "subtract") and p[1][0] == "L")
                update_omissions += 1
            rejection(lambda: compare(checker, before, after[:omission] + after[omission + 1:]))
            rejected += 1
            wrong = list(after)
            i = next(i for i, p in enumerate(wrong) if p[0] in ("add", "subtract"))
            wrong[i] = ("add" if wrong[i][0] == "subtract" else "subtract", *wrong[i][1:])
            rejection(lambda: compare(checker, before, wrong))
            rejected += 1
            changed += 1
        checker.require(changed == 29, "actual-run control coverage differs")
    a, b, c, work = ("L", 0), ("L", 1), ("L", 2), ("W", 0)
    # Copying a negative value can INCREASE the cost; this is not a universal saving theorem.
    fanout = [("negate", a), ("copy", b, a), ("copy", c, a)]
    candidate = checker.compile_signs(fanout)
    compare(checker, fanout, candidate, precision=True)
    checker.require(len(candidate) == len(fanout) + 2, "copy-fanout cost undercharged")
    # An endpoint-neutral excursion still violates the precise per-register prefix obligation.
    plain = [("add", a, b)]
    excursion = [("double", b), ("halve", b), *plain]
    compare(checker, plain, excursion)
    rejection(lambda: compare(checker, plain, excursion, precision=True))
    # Arbitrary incoming work must be overwritten; the final clear is necessary too.
    good = [("copy", work, b), ("halve", work), ("subtract", a, work), ("clear", work)]
    rejection(lambda: compare(checker, good, good[1:]))
    rejection(lambda: compare(checker, good, good[:-1]))
    # Two negations in separate frames cannot cancel across their physical boundary.
    events = [["scalar", ["scale", list(a), -1, 1], 7],
              ["scalar", ["scale", list(a), -1, 1], 8],
              ["phase", "barrier"],
              ["scalar", ["scale", list(a), -1, 1], 8]]
    checker.require(len(list(primary.segments(events))) == len(list(checker.runs(events))) == 3,
                    "frame/event barrier missing")
    rejection(lambda: compare(checker, [("negate", a)], []))
    checker.require((flush_omissions, update_omissions) == (30, 28), "omission classes differ")
    return {"actual_run_mutants_rejected": rejected, "boundary_flush_omissions": flush_omissions,
            "target_update_omissions": update_omissions, "toy_mutants_rejected": 4,
            "copy_fanout_cost_growth_checked": True, "frame_and_event_barriers_checked": True}
