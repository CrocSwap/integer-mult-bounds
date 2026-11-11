#!/usr/bin/env python3
"""The one-way Y-exit move onto frame 1 is not a retained endpoint.

The round-three word and the retained emitter are predecessor inputs. This
checker recomputes the exit charts and replays the one-way transports. It
does not trust the counts in PROOF.md as inputs. Failures raise ValueError,
including under python -O.
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


def named_roles(event):
    kind = event[0]
    if kind in ("add", "copy"):
        return (event[1], event[2])
    if kind in ("scale", "warp", "transport"):
        return (event[1],)
    return ()


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


def index_events(events):
    by_role = [[] for _ in range(640)]
    for index, event in enumerate(events):
        for role in named_roles(event):
            if required_chart(event, role) is not None:
                by_role[role].append(index)
    return by_role


def walk_role(events, indexes, role, start, end, dims, spaces):
    current = start
    variation = 0
    monotone_up = True
    downward = 0
    for index in indexes:
        event = events[index]
        chart = required_chart(event, role)
        need(current == chart, "pin or departure is on the walked chart")
        if event[0] == "transport" and event[1] == role:
            source, dest, width = event[2], event[3], event[4]
            need(spaces[source] < spaces[dest] or spaces[dest] < spaces[source], "strict nesting")
            need(width == abs(dims[dest] - dims[source]) and width >= 1, "width is the dimension gap")
            if dims[dest] < dims[current]:
                monotone_up = False
                downward += 1
            variation += width
            current = dest
        elif event[0] == "warp" and event[1] == role:
            need(dims[event[3]] == dims[event[4]], "this warp preserves dimension")
            current = event[4]
    need(current == end, "walk ends on the demanded chart")
    need(variation == abs(dims[end] - dims[start]), "rank mass equals the net dimension change")
    return {"variation": variation, "monotone_up": monotone_up, "downward": downward}


def insert_after_last(events, by_role, roles, final, full_id):
    """Append one width-1 transport after each role's last pinned event."""
    inserts = []
    for role in roles:
        indexes = by_role[role]
        need(indexes, "Y role has a pinned event")
        last = indexes[-1]
        event = events[last]
        need(event[0] == "add", "the last pin is an add")
        need(required_chart(event, role) == final[role], "the last add uses the exit chart")
        inserts.append((last, role, final[role]))
    lasts = [last for last, _, _ in inserts]
    need(len(lasts) == len(set(lasts)), "Y roles do not share a last pin")
    out = list(events)
    for last, role, chart in sorted(inserts, reverse=True):
        out[last + 1:last + 1] = [("transport", role, chart, full_id, 1)]
    return out


def replay(engine, payload, starts, events, expect_final):
    """Chart and row rules of the retained replay, with an explicit final tuple."""
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
            need(role != source and current[role] == current[source] == frame, "scalar common chart")
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
            need(len(frames[source]) == len(frames[dest]), "replayed warp preserves dimension")
            out = {}
            for (variable, word), value in rows[role].items():
                word = word[1:] if word and word[0] == -symbol else (symbol,) + word
                engine.plus(out, {(variable, word): value})
            rows[role] = out
            current[role] = dest
    decoded = [{i: value for (i, _), value in row.items()} for row in rows]
    mismatches = [index for index, (got, want) in enumerate(zip(current, expect_final)) if got != want]
    return decoded, dict(paid), current, mismatches


def raised_histogram(paid, extra):
    out = dict(paid)
    out[1] = out[1] + extra
    return out


def optimistic_gap(added_rank1, centre_widths):
    need(type(added_rank1) is int and added_rank1 >= 0, "added rank-1 count")
    need(all(type(width) is int and width >= 1 for width in centre_widths), "centre widths")
    return added_rank1 - sum(centre_widths)


def expect_fail(fn, message):
    try:
        fn()
    except ValueError:
        return
    raise ValueError(message)


def survey(engine, payload, starts, events):
    frames = payload["canonical"]["frames"]
    final = payload["canonical"]["final"]
    dims = [len(basis) for basis in frames]
    spaces = list(map(engine.span, frames))
    ambient = payload["canonical"]["h"]
    block = payload["canonical"]["v"]
    need(ambient == 9 and block == 112, "ambient dimension and block length")
    need(len(final) == 632 and len(starts) == 640, "632 recorded finals and 640 starts")
    full = [index for index, basis in enumerate(frames) if len(basis) == ambient]
    need(full == [1], "one retained rank-9 frame")
    full_id = full[0]
    need(frames[full_id] == [256, 128, 64, 32, 16, 8, 4, 2, 1], "frame 1 basis")
    need(len(spaces[full_id]) == 512, "frame 1 span has size 2^9")
    need(all(final[role] == full_id for role in range(block)), "every X exit uses frame 1")
    y_roles = list(range(block, 2 * block))
    y_ids = [final[role] for role in y_roles]
    need(len(set(y_ids)) == block, "112 distinct Y exit charts")
    need(all(chart != full_id for chart in y_ids), "no Y exit is frame 1")
    for chart in y_ids:
        need(dims[chart] == ambient - 1, "every Y exit chart has dimension 8")
        need(spaces[chart] < spaces[full_id], "every Y exit span sits strictly inside frame 1")
        need(abs(dims[chart] - dims[full_id]) == 1, "the one-way transport has width 1")
    role = block
    chart = final[role]
    need(chart == 142, "role 112 exits on chart 142")
    need(frames[chart] == [256, 128, 64, 32, 16, 9, 4, 3], "role 112 basis")
    need(len(spaces[chart]) == 256, "role 112 span has size 2^8")
    need(1 in spaces[full_id] and 1 not in spaces[chart], "direction 1 is in frame 1 and not in chart 142")

    by_role = index_events(events)
    warp_count = 0
    for event in events:
        if event[0] == "warp":
            warp_count += 1
            need(dims[event[3]] == dims[event[4]], "emitted warp preserves dimension")
    need(warp_count == 240, "the emitted word has 240 warps")
    retained_final = final + [0] * 8
    for index in range(640):
        end = retained_final[index]
        facts = walk_role(events, by_role[index], index, starts[index], end, dims, spaces)
        if index in y_roles:
            need(dims[starts[index]] == 0 and dims[end] == 8, "Y role runs from dimension 0 to 8")
            need(facts["monotone_up"] and facts["variation"] == 8, "emitted Y walk is monotone of mass 8")
        if index >= 632:
            need(facts["downward"] == 1 and facts["variation"] == 8, "each centre is one downward step of width 8")
            need(end == 0, "each centre ends on the empty chart")
    helpers = Counter(dims[final[index]] - dims[payload["canonical"]["start"][index]]
                      for index in range(2 * block, 632))
    need(dict(helpers) == {4: 28, 7: 7, 8: 47, 9: 326}, "helper target histogram")
    centre = [event for event in events if event[0] == "transport" and event[1] >= 632]
    need(len(centre) == 8 and all(event[3] == 0 and event[4] == 8 for event in centre),
         "eight centre transports onto chart 0")
    return {"full_id": full_id, "by_role": by_role, "retained_final": retained_final,
            "centre_widths": [event[4] for event in centre], "spaces": spaces, "dims": dims}


def controls(engine, payload, starts, events, facts, original_rows):
    frames = payload["canonical"]["frames"]
    final = payload["canonical"]["final"]
    full_id = facts["full_id"]
    retained = facts["retained_final"]
    by_role = facts["by_role"]
    role = 112
    one = insert_after_last(events, by_role, [role], final, full_id)
    every = insert_after_last(events, by_role, range(112, 224), final, full_id)

    rejected = False
    try:
        engine.replay(payload, starts, one)
    except ValueError as exc:
        rejected = str(exc) == "complete emitted recursive invoice"
    need(rejected, "retained replay rejects the role-112 one-way move on the invoice")

    rows, paid, _current, mismatches = replay(engine, payload, starts, one, retained)
    need(rows == original_rows, "the role-112 transport does not change the operator")
    need(paid == raised_histogram(engine.PAID, 1), "one exit adds one rank-1 child")
    need(mismatches == [role] and _current[role] == full_id, "role 112 ends on frame 1")

    changed = list(retained)
    changed[role] = full_id
    rows, paid, current, mismatches = replay(engine, payload, starts, one, changed)
    need(not mismatches and current == changed and rows == original_rows, "frame 1 accepts role 112")
    need(paid == raised_histogram(engine.PAID, 1), "accepted role-112 bill")

    rows, paid, current, mismatches = replay(engine, payload, starts, every, retained)
    need(rows == original_rows, "moving every Y exit does not change the operator")
    need(paid == raised_histogram(engine.PAID, 112), "112 exits add 112 rank-1 children")
    need(mismatches == list(range(112, 224)), "the retained tuple fails on every Y role")
    need(all(current[index] == full_id for index in mismatches), "each moved role sits on frame 1")

    changed = list(retained)
    for index in range(112, 224):
        changed[index] = full_id
    rows, paid, current, mismatches = replay(engine, payload, starts, every, changed)
    need(not mismatches and current == changed and rows == original_rows,
         "replacing every Y exit by frame 1 accepts the move")
    need(paid == raised_histogram(engine.PAID, 112), "accepted all-Y bill")
    need(paid[8] == 8 and paid[1] == engine.PAID[1] + 112, "centre rank-8 calls stay")

    last = by_role[role][-1]
    chart = final[role]
    early = events[:last] + [("transport", role, chart, full_id, 1)] + events[last:]
    early_final = list(retained)
    early_final[role] = full_id
    expect_fail(lambda: replay(engine, payload, starts, early, early_final),
                "a transport before the last add misses that add's chart")

    for centre_role in range(632, 640):
        centre_at = next(index for index, event in enumerate(every)
                         if event[0] == "transport" and event[1] == centre_role)
        transport = every[centre_at]
        need(transport[3] == 0 and transport[4] == 8, "centre transport onto chart 0")
        need(transport[2] != 0, "centre source chart is not the empty chart")
        if centre_role == 632:
            need(transport[2] == 254, "role 632 departs from chart 254")
        nxt = next(event for event in every[centre_at + 1:] if centre_role in named_roles(event))
        need(nxt[0] == "add" and nxt[4] == 0 and nxt[2] == centre_role,
             "the next pin after a centre transport is an add on chart 0")
    centre_at = next(index for index, event in enumerate(every)
                     if event[0] == "transport" and event[1] == 632)
    dropped = every[:centre_at] + every[centre_at + 1:]
    expect_fail(lambda: replay(engine, payload, starts, dropped, changed),
                "deleting the centre transport misses the next chart-0 add")

    need(optimistic_gap(112, facts["centre_widths"]) == 48, "predecessor gap is 112 minus 64")
    need(optimistic_gap(224, facts["centre_widths"]) == 160, "the round-trip gap stays 160")
    need(abs(len(frames[chart]) - len(frames[full_id])) == 1, "width formula")
    expect_fail(lambda: need(abs(8 - 9) == 2, "wrong width"), "a width-2 claim must fail")
    expect_fail(lambda: need(final[role] == full_id, "role 112 is not frame 1"),
                "the retained exit is not frame 1")
    for rank in range(1, 9):
        for denominator in range(1, 9):
            for numerator in range(denominator + 1):
                need(rank ** numerator <= rank ** denominator, "integer power comparison")
                if rank > 1 and numerator < denominator:
                    need(rank ** numerator < rank ** denominator, "strict integer power comparison")


def main():
    engine = load_engine()
    payload = authenticate(engine)
    starts, centers, events = engine.emit(payload)
    need(len(centers) == 8 and len(starts) == 640, "eight centre inputs")
    original_rows = engine.replay(payload, starts, events)
    facts = survey(engine, payload, starts, events)
    local_rows, paid, current, mismatches = replay(
        engine, payload, starts, events, facts["retained_final"])
    need(local_rows == original_rows and not mismatches and current == facts["retained_final"],
         "local replay matches the retained matrix and endpoint")
    need(paid == engine.PAID, "local replay matches the retained invoice")
    controls(engine, payload, starts, events, facts, original_rows)
    print(
        "PASS_Y_EXIT_ONE_WAY_FRAME1_ENDPOINT "
        "role112_chart=142 role112_dim=8 frame1_dim=9 "
        "y_exits=112 retained_accepts=false "
        "changed_endpoint_moment_increase=112 "
        "predecessor_gap_at_least=48 "
        "operator_preserved=true "
        "evidence_class=scoped-proof "
        "no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
