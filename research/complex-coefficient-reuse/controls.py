"""Adversarial controls for mathematical and interface failure modes.

Apache-2.0. Substantial OpenAI Codex assistance, prepared for @taizaki69.
"""

from copy import deepcopy
from fractions import Fraction as Q

from lower import WORK, lower_run, lower_scalar


def sample_run():
    # Mixed signs, a repeated target and a non-integral coefficient.
    return [["scalar", ["add", ["L", t], ["L", 2], p, 4], 7]
            for t, p in ((0, 3), (1, -3), (0, -3))]


def check_small(events, ops):
    from verify import check_chunk
    registers = [("L", i) for i in range(3)] + [WORK]
    state = {r: {i: Q(1)} for i, r in enumerate(registers)}
    reference = deepcopy(state)
    env = {r: Q(1) for r in registers}
    check_chunk(events, ops, state, reference, env, env.copy())


def rejected(callback):
    try:
        callback()
    except ValueError:
        return "rejected"
    raise ValueError("negative control was accepted")


def run_controls():
    events = sample_run()
    good = lower_run(events)
    check_small(events, good)
    result = {}

    # These edits all belong to the permitted primitive vocabulary. The
    # rational replay must detect them, independently of run construction.
    mutations = {}
    mutations["omitted_source_copy"] = good[1:]
    mutations["omitted_private_clear"] = good[:-1]
    half = next(i for i, op in enumerate(good) if op[0] == "half")
    mutations["omitted_halving"] = good[:half] + good[half + 1:]
    sign = next(i for i, op in enumerate(good) if op[0] == "sub")
    mutations["wrong_accumulation_sign"] = good[:sign] + [("add",) + good[sign][1:]] + good[sign + 1:]
    use = next(i for i, op in enumerate(good) if len(op) == 3 and op[2] == WORK)
    mutations["coefficient_corrupted_between_targets"] = good[:use + 1] + [("double", WORK)] + good[use + 1:]
    mutations["wrong_target"] = good[:use] + [(good[use][0], ("L", 1), WORK)] + good[use + 1:]
    # This one preserves every endpoint, including the private clear. Only
    # checking the complete intermediate-value budget exposes the defect.
    mutations["endpoint_neutral_prefix_growth"] = (
        good[:use] + [("double", WORK)] * 5 + [("half", WORK)] * 5 + good[use:])
    for name, ops in mutations.items():
        result[name] = rejected(lambda ops=ops: check_small(events, ops))

    for name, edit in (
        ("different_source", lambda e: e[1][1].__setitem__(2, ["L", 0])),
        ("different_magnitude", lambda e: e[1][1].__setitem__(3, 5)),
        ("different_frame", lambda e: e[1].__setitem__(2, 8)),
        ("source_written_in_run", lambda e: e[1][1].__setitem__(1, ["L", 2])),
        ("phase_boundary", lambda e: e.insert(1, ["phase", "centers"])),
    ):
        changed = deepcopy(events)
        edit(changed)
        result[name] = rejected(lambda changed=changed: lower_run(changed))

    result["non_dyadic_coefficient"] = rejected(
        lambda: lower_scalar(["add", ["L", 0], ["L", 2], 1, 3]))
    result["zero_denominator"] = rejected(
        lambda: lower_scalar(["scale", ["L", 0], 1, 0]))
    # The literal backward word contains reciprocated signed scale fields.
    check_small([["scalar", ["scale", ["L", 0], 1, -2], 7]],
                lower_scalar(["scale", ["L", 0], 1, -2]))

    # Exact dirty-work checks over signs and dyadic magnitudes distinct from
    # the selected example. These are finite controls, not a general proof.
    for p in (1, 2, 3, 7, 17, 39):
        for denominator in (1, 2, 4, 16):
            e = [["scalar", ["add", ["L", t], ["L", 2], sign * p, denominator], 7]
                 for t, sign in ((0, 1), (1, -1), (0, -1))]
            if abs(Q(p, denominator)) != 1:
                check_small(e, lower_run(e))
            else:
                for event in e:
                    check_small([event], lower_scalar(event[1]))
    return result


if __name__ == "__main__":
    result = run_controls()
    print("PASS_REUSE_CONTROLS", len(result))
