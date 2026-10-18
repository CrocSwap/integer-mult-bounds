# SPDX-License-Identifier: Apache-2.0
"""Check actual non-cold HPE wrapper events, not an auxiliary word annotation.

This is a finite event-to-literal binding, not a scalar or native replay.
"""
import json

MAX_REGISTERS = 4096
MAX_FRAMES = 4096
MAX_EVENTS = 100_000
PHASES = ("zero_frame_precondition", "entry_adapters", "A", "centers", "B",
          "cleanup_tail", "final", "exit_adapters", "full_frame_cleanup", "done")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def integer(value, stop):
    require(type(value) is int and 0 <= value < stop, "invalid integer index")
    return value


def same(actual, expected):
    # Unlike Python equality, JSON serialization distinguishes true from 1.
    return json.dumps(actual, sort_keys=True, allow_nan=False) == json.dumps(
        expected, sort_keys=True, allow_nan=False)


def target_states(word, pairs):
    require(type(word["h"]) is int and word["h"] == 9, "expected nine-dimensional frames")
    v = integer(word["v"], MAX_REGISTERS // 2)
    n = 2 * v + integer(word["R"], MAX_REGISTERS)
    require(0 < n <= MAX_REGISTERS, "register capacity exceeded")
    frames = word["frames"]
    require(2 <= len(frames) <= MAX_FRAMES, "frame capacity exceeded")
    require(frames[0] == [] and frames[1] == [256, 128, 64, 32, 16, 8, 4, 2, 1],
            "wrong ZERO or FULL frame convention")
    for rows in frames:
        require(type(rows) is list and len(rows) <= 9, "invalid frame basis")
        for row in rows:
            require(type(row) is int and 0 < row < 512, "invalid frame vector")
    require(len(word["start"]) == len(word["final"]) == n, "register inventory")
    for f in word["start"] + word["final"]:
        integer(f, len(frames))
    states = {}
    for r in range(2 * v, n):
        e, u = word["start"][r], word["final"][r]
        if e == 0 or u == 1:
            continue  # Cold and FULL-ended helpers are explicitly outside this check.
        key = (tuple(frames[e]), tuple(frames[u]))
        require(key in pairs, "non-cold HPE pair absent from Lean literals")
        states[r] = {"entrance": e, "terminal": u, "pair": pairs[key],
                     "current": e, "pre": None, "post": None,
                     "first_touch": None, "last_touch": None}
    require(states, "no non-cold HPE helpers")
    return states, n, len(frames)


def wrapper(event, phase, index, state, recipes):
    require(len(event) == 5, "HPE wrapper must name its terminal frame")
    _, kind, _, e, u = event
    require(type(e) is int and type(u) is int and
            e == state["entrance"] and u == state["terminal"], "wrong wrapper pair")
    key = f"{e}:{u}"
    require(key in recipes, "missing event-selected recipe")
    recipe = recipes[key]
    require(type(recipe["rank"]) is int and recipe["rank"] == 7, "wrong residual rank")
    side = "right" if kind == "pre" else "left"
    require(same(recipe[side], state["pair"][side]), "event-selected monomial differs from Lean")
    if kind == "pre":
        require(phase == "entry_adapters" and state["pre"] is None and
                state["post"] is None and state["current"] == e, "pre wrapper order")
    else:
        require(kind == "post" and phase == "full_frame_cleanup" and
                state["pre"] is not None and state["post"] is None and
                state["current"] == u, "post wrapper order")
    state[kind] = index


def touch(state, index, frame):
    require(state["pre"] is not None and state["post"] is None,
            "helper touched outside wrappers")
    require(state["current"] == frame, "helper frame mismatch")
    if state["first_touch"] is None:
        state["first_touch"] = index
    state["last_touch"] = index


def operands(operation, n):
    require(type(operation) is list and operation, "invalid scalar operation")
    tag = operation[0]
    sizes = {"clear": 2, "copy": 3, "scale": 4, "add": 5}
    require(type(tag) is str and tag in sizes and len(operation) == sizes[tag],
            "invalid scalar shape")
    regs = operation[1:3] if tag in ("copy", "add") else operation[1:2]
    for reg in regs:
        require(type(reg) is list and len(reg) == 2 and reg[0] in ("L", "C"),
                "invalid scalar register")
        integer(reg[1], n)
    if tag in ("add", "scale"):
        numerator, denominator = operation[-2:]
        require(type(numerator) is int and type(denominator) is int and
                denominator != 0, "invalid scalar coefficient")
    return regs


def instruction(event, phase, index, states, recipes, n, frame_count):
    tag = event[0]
    if tag == "residual_adapter":
        require(len(event) in (4, 5) and event[1] in ("pre", "post"), "wrapper shape")
        r = integer(event[2], n)
        integer(event[3], frame_count)
        if len(event) == 5:
            integer(event[4], frame_count)
        if r in states:
            wrapper(event, phase, index, states[r], recipes)
    elif tag == "adapter":
        require(len(event) == 4 and event[1] in ("old_to_new", "new_to_old"), "adapter shape")
        r = integer(event[2], n)
        integer(event[3], frame_count)
        require(r not in states, "ordinary adapter on an HPE helper")
    elif tag == "climb":
        require(len(event) == 6 and event[1] == phase, "climb shape or phase")
        r = integer(event[2], n)
        old, new = integer(event[3], frame_count), integer(event[4], frame_count)
        require(type(event[5]) is int and 0 < event[5] <= 9, "climb rank")
        if r in states:
            touch(states[r], index, old)
            states[r]["current"] = new
    elif tag == "scalar":
        require(len(event) == 3, "scalar event shape")
        frame = integer(event[2], frame_count)
        for tag, r in operands(event[1], n):
            if tag == "L" and r in states:
                touch(states[r], index, frame)
    elif tag == "center":
        require(len(event) == 5, "center shape")
        integer(event[1], n)
        integer(event[2], frame_count)
        integer(event[3], frame_count)
        require(type(event[4]) is int and 0 < event[4] <= 9, "center rank")
    else:
        raise ValueError("unknown emitted event tag")


def check(word, events, adapters, pairs):
    """Bind every non-cold HPE helper; do not silently skip an unknown pair."""
    states, n, frame_count = target_states(word, pairs)
    require(type(events) is list and 0 < len(events) <= MAX_EVENTS, "event capacity exceeded")
    recipes = adapters["recipes"]
    require(type(recipes) is dict and len(recipes) <= MAX_FRAMES, "recipe capacity exceeded")
    phases = 0
    for index, event in enumerate(events):
        require(type(event) is list and event, "invalid event")
        if event[0] == "phase":
            require(len(event) == 2 and phases < len(PHASES) and
                    event[1] == PHASES[phases], "phase order")
            phases += 1
        else:
            require(0 < phases < len(PHASES), "instruction outside invocation")
            instruction(event, PHASES[phases - 1], index, states, recipes, n, frame_count)
    require(phases == len(PHASES), "incomplete invocation")
    bindings = []
    for r, state in sorted(states.items()):
        pre, post = state["pre"], state["post"]
        first, last = state["first_touch"], state["last_touch"]
        require(pre is not None and post is not None and first is not None and
                pre < first <= last < post, "missing wrapper or helper touch")
        require(state["current"] == state["terminal"], "wrong final helper frame")
        bindings.append({"helper": r, "recipe": f'{state["entrance"]}:{state["terminal"]}',
                         "pre": pre, "first_touch": first, "last_touch": last, "post": post})
    return {"events": len(events), "helpers": len(bindings), "bindings": bindings}
