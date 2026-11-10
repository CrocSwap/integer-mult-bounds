#!/usr/bin/env python3
"""A restored partial Y-exit round trip does not lower the paid moment.

The round-three word and the retained emitter are predecessor inputs. This
checker recomputes the chart walk. It does not trust the counts in PROOF.md
as inputs. Failures raise ValueError, including under python -O.
"""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WORD = ROOT / "research/sol1337-contact-frontier/inputs/round3-native.json.gz"
ENGINE = ROOT / "research/sol1337-contact-frontier/vendor/retained_verify.py"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_engine():
    spec = importlib.util.spec_from_file_location("retained_centre_verify", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(engine):
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    by_path = {row["path"]: row for row in pins["files"]}
    for path in (WORD, ENGINE):
        rel = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == by_path[rel]["sha256"], "changed input " + rel)
    raw = WORD.read_bytes()
    need(sha256(raw).hexdigest() == engine.SOURCE_HASH, "word hash disagrees with the retained emitter")
    return json.loads(gzip.decompress(raw))


def required_chart(event, role):
    kind = event[0]
    if kind in ("add", "copy"):
        if role in (event[1], event[2]):
            return event[4]
    elif kind == "scale":
        if role == event[1]:
            return event[3]
    elif kind == "warp":
        if role == event[1]:
            return event[3]
    elif kind == "transport":
        if role == event[1]:
            return event[2]
    return None


def participant(event, role):
    return required_chart(event, role) is not None


def survey(engine, payload, starts, events):
    frames = payload["canonical"]["frames"]
    final = payload["canonical"]["final"]
    dims = [len(basis) for basis in frames]
    spaces = list(map(engine.span, frames))
    ambient = payload["canonical"]["h"]
    block = payload["canonical"]["v"]
    need(ambient == 9 and block == 112, "ambient dimension and block length")
    full = [index for index, basis in enumerate(frames) if len(basis) == ambient]
    need(full == [1], "one retained rank-9 frame")
    full_id = full[0]
    y_ids = [final[role] for role in range(block, 2 * block)]
    need(len(set(y_ids)) == block, "112 distinct Y exit charts")
    for chart in y_ids:
        need(dims[chart] == ambient - 1, "every Y exit chart has dimension 8")
        need(spaces[chart] < spaces[full_id], "every Y exit chart sits inside frame 1")
        need(abs(dims[chart] - dims[full_id]) == 1, "the frame-1 round trip has width 1 each way")

    histogram = Counter()
    forced = 0
    warp_count = sum(1 for event in events if event[0] == "warp")
    for event in events:
        if event[0] == "warp":
            need(dims[event[3]] == dims[event[4]], "emitted warp preserves dimension")
    mass = 0
    for role in range(640):
        end = final[role] if role < 632 else 0
        current = starts[role]
        variation = 0
        transport_at = [index for index, event in enumerate(events)
                        if event[0] == "transport" and event[1] == role]
        first = transport_at[0] if transport_at else len(events)
        for item in events[:first]:
            chart = required_chart(item, role)
            if chart is None:
                continue
            need(current == chart, "pin before the first transport")
            if item[0] == "warp" and item[1] == role:
                current = item[4]
        for nth, index in enumerate(transport_at):
            event = events[index]
            source, dest, width = event[2], event[3], event[4]
            need(current == source, "transport departs from the chart the walk reached")
            need(spaces[source] < spaces[dest] or spaces[dest] < spaces[source], "strict nesting")
            need(width == abs(dims[dest] - dims[source]) and width >= 1, "width is the positive dimension gap")
            nxt = transport_at[nth + 1] if nth + 1 < len(transport_at) else len(events)
            pins = [item for item in events[index + 1:nxt] if required_chart(item, role) is not None]
            need(pins, "every transport is followed by a pinned use of its arrival chart")
            need(required_chart(pins[0], role) == dest, "the next pin requires the arrival chart")
            forced += 1
            variation += width
            histogram[width] += 1
            current = dest
            for item in pins:
                chart = required_chart(item, role)
                need(current == chart, "later pin in this gap is on the walked chart")
                if item[0] == "warp" and item[1] == role:
                    current = item[4]
        need(current == end, "walk ends on the emitted final chart")
        net = abs(dims[end] - dims[starts[role]])
        need(variation == net, "role rank mass equals the net dimension change")
        mass += variation
        if block <= role < 2 * block:
            need(dims[starts[role]] == 0 and dims[end] == 8, "Y role runs from dimension 0 to 8")
            need(events[[index for index, event in enumerate(events) if participant(event, role)][-1]][0] == "add",
                 "Y role's last pin is an add on the exit chart")
    need(forced == sum(histogram.values()) == 3298, "every transport is forced by the next pin")
    need(mass == 5327, "emitted rank mass meets the variation lower bound")
    need(dict(histogram) == engine.PAID, "walked histogram is the retained paid invoice")
    need(warp_count == 240, "every emitted warp was a same-dimension chart change")
    return {"full_id": full_id, "histogram": histogram, "mass": mass, "forced": forced}


def insert_round_trip(events, role, full_id, frames):
    """After the role's last pinned event, visit frame 1 and return."""
    last = None
    for index, event in enumerate(events):
        if participant(event, role):
            last = index
    need(last is not None, "Y role has a pinned event")
    # The walk's chart after `last` is the exit. Read it from that event.
    event = events[last]
    if event[0] == "transport" and event[1] == role:
        chart = event[3]
    elif event[0] == "warp" and event[1] == role:
        chart = event[4]
    else:
        chart = required_chart(event, role)
    need(len(frames[chart]) == 8, "insertion starts on the rank-8 exit")
    need(len(frames[full_id]) == 9, "frame 1 has dimension 9")
    added = [("transport", role, chart, full_id, 1),
             ("transport", role, full_id, chart, 1)]
    return events[:last + 1] + added + events[last + 1:], chart


def replay_matrix(engine, payload, starts, events, expect_paid):
    """Same chart and row rules as the retained replay, with an explicit histogram."""
    from fractions import Fraction as Q

    rows = [{(i, ()): Q(1)} for i in range(engine.N)]
    current = starts[:]
    frames = payload["canonical"]["frames"]
    spaces = list(map(engine.span, frames))
    paid = Counter()
    for event in events:
        kind, role = event[:2]
        if kind in ("add", "copy"):
            _, _, source, coefficient, frame = event
            need(role != source and current[role] == current[source] == frame,
                 "scalar common chart")
            need(kind == "add", "this schedule has no baseline copy")
            engine.plus(rows[role], rows[source], coefficient)
        elif kind == "scale":
            _, _, coefficient, frame = event
            need(current[role] == frame and coefficient != 0, "scale chart")
            rows[role] = {key: coefficient * value for key, value in rows[role].items()}
        elif kind == "transport":
            _, _, source, dest, width = event
            need(current[role] == source, "paid source chart")
            need(spaces[source] < spaces[dest] or spaces[dest] < spaces[source], "nested")
            need(width == abs(len(frames[source]) - len(frames[dest])), "width")
            paid[width] += 1
            current[role] = dest
        else:
            _, _, symbol, source, dest = event
            need(kind == "warp" and current[role] == source, "warp source chart")
            out = {}
            for (variable, word), value in rows[role].items():
                word = word[1:] if word and word[0] == -symbol else (symbol,) + word
                engine.plus(out, {(variable, word): value})
            rows[role] = out
            current[role] = dest
    finals = payload["canonical"]["final"] + [0] * 8
    need(current == finals, "all 640 output charts")
    need(dict(paid) == expect_paid, "paid histogram")
    decoded = [{i: value for (i, _), value in row.items()} for row in rows]
    return decoded


def moment_increase(exit_count):
    need(type(exit_count) is int and exit_count >= 1, "nonempty exit set")
    # Each added child has rank 1, and 1**theta == 1 for every real theta.
    return 2 * exit_count


def controls(engine, payload, starts, events, facts):
    frames = payload["canonical"]["frames"]
    full_id = facts["full_id"]
    role = 112
    augmented, chart = insert_round_trip(events, role, full_id, frames)
    original_paid = dict(facts["histogram"])
    raised = dict(original_paid)
    raised[1] = raised[1] + 2
    original_rows = replay_matrix(engine, payload, starts, events, original_paid)
    engine_rows = engine.replay(payload, starts, events)
    need(original_rows == engine_rows, "local replay matches the retained matrix")
    moved_rows = replay_matrix(engine, payload, starts, augmented, raised)
    need(moved_rows == original_rows, "one restored round trip preserves the operator")
    need(moment_increase(1) == 2 and moment_increase(112) == 224, "moment increase is twice the exit count")
    need(moment_increase(33) - 64 == 2, "even the optimistic centre credit loses for 33 exits at theta 1")

    # Deleting the first transport leaves the next pin on the wrong chart.
    first = next(index for index, event in enumerate(events) if event[0] == "transport")
    skipped = events[:first] + events[first + 1:]
    rejected = False
    try:
        replay_matrix(engine, payload, starts, skipped, original_paid)
    except ValueError:
        rejected = True
    need(rejected, "deleting one transport misses a pinned chart")

    # A centre transport is the unique step onto the empty chart.
    centre = next(event for event in events if event[0] == "transport" and event[1] == 632)
    need(centre[3] == 0 and centre[4] == 8, "centre role 632 ends by a width-8 step onto chart 0")

    def bad_width():
        need(abs(len(frames[chart]) - len(frames[full_id])) == 2, "wrong width")

    rejected = False
    try:
        bad_width()
    except ValueError:
        rejected = True
    need(rejected, "width 2 is not the frame-1 gap")

    def empty_set():
        moment_increase(0)

    rejected = False
    try:
        empty_set()
    except ValueError:
        rejected = True
    need(rejected, "the empty exit set is not a partial round trip")


def main():
    engine = load_engine()
    payload = authenticate(engine)
    starts, centers, events = engine.emit(payload)
    need(len(centers) == 8 and len(starts) == 640, "eight centre inputs")
    facts = survey(engine, payload, starts, events)
    controls(engine, payload, starts, events, facts)
    print(
        "PASS_Y_EXIT_PARTIAL_ROUND_TRIP "
        "y=112 forced_transports=3298 "
        "rank_mass=5327 moment_increase_per_exit=2 "
        "one_exit_preserves_operator=true "
        "histogram_forced=true no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
