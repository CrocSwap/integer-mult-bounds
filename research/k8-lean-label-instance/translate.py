# SPDX-License-Identifier: Apache-2.0
"""Translate pinned k8 JSON to the retained LemmaG.Event grammar.

This is a source-bound adapter, not a verified implementation of Python/JSON.
Labels encode the tag, owning register and frame injectively in a fixed domain.
"""
from fractions import Fraction

REGISTERS = 712
LOCALS = 704
FRAMES = 1004
MAX_EVENTS = 25000
TAGS = {"pre": 0, "post": 1, "prew": 2, "done": 3}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def label(frame, tag=None, owner=0):
    require(type(frame) is int and 0 <= frame < FRAMES, "frame domain")
    if tag is None:
        return frame
    require(tag in TAGS and type(owner) is int and 0 <= owner < LOCALS, "tag domain")
    return frame + FRAMES * (1 + owner + REGISTERS * TAGS[tag])


def register(value):
    require(isinstance(value, list) and len(value) == 2, "register shape")
    kind, index = value
    require(kind in ("L", "C") and type(index) is int, "register type")
    require(0 <= index < (LOCALS if kind == "L" else 8), "register domain")
    return index if kind == "L" else LOCALS + index


def local(value):
    return register(["L", value])


def initial_labels(canonical):
    c = canonical
    require(c["v"] == 112 and c["R"] == 480 and c["h"] == 9, "selected domain")
    require(len(c["start"]) == len(c["final"]) == LOCALS, "local inventory")
    require(len(c["frames"]) == FRAMES and c["frames"][0] == [] and
            len(c["frames"][1]) == 9, "frame inventory")
    labels = []
    for r, frame in enumerate(c["start"]):
        tag = "pre" if r < 112 else "prew" if r >= 224 and (
            frame != 0 or c["final"][r] != 1) else None
        labels.append(label(frame, tag, r))
    return labels + [label(0)] * 8


def scalar(operation, frame):
    require(isinstance(operation, list) and operation, "scalar shape")
    kind = operation[0]
    sizes = {"add": 5, "scale": 4, "copy": 3, "clear": 2}
    require(kind in sizes and len(operation) == sizes[kind], "scalar arity")
    target = register(operation[1])
    if kind in ("copy", "add"):
        source = register(operation[2])
        require(source != target, "scalar alias")
    if kind in ("add", "scale"):
        numerator, denominator = operation[-2:]
        require(type(numerator) is int and type(denominator) is int and
                numerator != 0 and denominator != 0, "coefficient")
        q = Fraction(numerator, denominator)
        require(abs(q.numerator) <= 2**20 and q.denominator <= 2**20, "coefficient bound")
        return [kind, target, source, q.numerator, q.denominator] if kind == "add" else [
            kind, target, q.numerator, q.denominator]
    return [kind, target, source, label(frame)] if kind == "copy" else [kind, target, label(frame)]


def translate_event(c, event):
    require(isinstance(event, list) and event, "event shape")
    kind = event[0]
    if kind == "phase":
        require(len(event) == 2 and isinstance(event[1], str), "phase shape")
        return None
    if kind == "scalar":
        require(len(event) == 3, "scalar event arity")
        label(event[2])
        return scalar(event[1], event[2])
    if kind in ("climb", "center"):
        require(len(event) == (6 if kind == "climb" else 5), "transport arity")
        r = local(event[2]) if kind == "climb" else register(["C", event[1]])
        old, new = event[-3:-1]
        return ["relabel", r, label(old), label(new)]
    if kind == "adapter":
        require(len(event) == 4, "adapter arity")
        _, way, r, frame = event
        local(r)
        plain = label(frame)
        if way == "old_to_new":
            require(r < 112 or frame == 0, "identity entry frame")
            return ["relabel", r, label(frame, "pre", r) if r < 112 else plain, plain]
        require(way == "new_to_old", "adapter direction")
        require(112 <= r < 224 or frame == 1, "identity exit frame")
        return ["relabel", r, plain, label(frame, "post", r) if 112 <= r < 224 else plain]
    require(kind == "residual_adapter" and len(event) in (4, 5), "event kind/arity")
    _, side, r, entrance = event[:4]
    local(r)
    require(r >= 224 and entrance == c["start"][r], "wrapper entrance")
    terminal = c["final"][r]
    require(entrance != 0 or terminal != 1, "unwrapped helper")
    require(event[4:] == ([terminal] if terminal != 1 else []), "wrapper terminal")
    if side == "pre":
        return ["relabel", r, label(entrance, "prew", r), label(entrance)]
    require(side == "post", "wrapper side")
    return ["relabel", r, label(terminal), label(terminal, "done", r)]


def translate(canonical, events):
    require(isinstance(events, list) and len(events) <= MAX_EVENTS, "event limit")
    start = initial_labels(canonical)
    result, indices = [], []
    for index, event in enumerate(events):
        translated = translate_event(canonical, event)
        if translated is not None:
            result.append(translated)
            indices.append(index)
    require(len(result) <= MAX_EVENTS, "translated limit")
    return start, result, indices


def step(labels, event):
    """Independent plain-list observer for controls and proof checkpoints."""
    kind, target = event[:2]
    after = list(labels)
    if kind == "relabel":
        require(labels[target] == event[2], "relabel source label")
        after[target] = event[3]
    elif kind == "add":
        require(labels[target] == labels[event[2]], "ADD common label")
    elif kind == "copy":
        require(labels[event[2]] == event[3], "COPY source label")
        after[target] = event[3]
    elif kind == "clear":
        after[target] = event[2]
    else:
        require(kind == "scale", "translated kind")
    return after


def observe(start, events):
    labels = start
    for event in events:
        labels = step(labels, event)
    return labels


def lean_event(event):
    kind = event[0]
    if kind == "add":
        _, t, s, n, d = event
        return f".add {t} {s} (({n} : Rat) / {d})"
    if kind == "scale":
        _, t, n, d = event
        return f".scale {t} (({n} : Rat) / {d})"
    return "." + kind + " " + " ".join(map(str, event[1:]))
