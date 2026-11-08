#!/usr/bin/env python3
"""Unique carriers of the two remaining frame-593 reads on the selected word.

The scalar replay is the selected word's ADD/SCALE/COPY/MOVE contract.
It does not rerun the native channel, physical caller or selected invoice.
Apache-2.0. Prepared by unpaidmoon with substantial Cursor Grok assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = ROOT / "research/p104-helper470-twin-rung-removal/WORD.json.gz"
WORD_SHA256 = "7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f"
CASES = (
    {"slot": 14380, "receiver": 469, "source": 703, "arrival": 17008,
     "witness": 666, "delayed": Q(-1, 4)},
    {"slot": 13716, "receiver": 471, "source": 704, "arrival": 16984,
     "witness": 180, "delayed": Q(-1, 2)},
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_word():
    payload = WORD.read_bytes()
    require(sha256(payload).hexdigest() == WORD_SHA256, "Selected word hash")
    word = json.loads(gzip.decompress(payload))
    require(word["schema"] == "p104-accumulated-block-composition/2", "Word schema")
    require(word["public"] == 770 and word["owned_fields"] == 29, "Word dimensions")
    require(len(word["program"]) == 22803, "Event count")
    return word


def fresh(word):
    public, owned = word["public"], word["owned_fields"]
    rows = [{i: Q(1)} for i in range(public)] + [{} for _ in range(owned)]
    charts = word["initial"][:] + [None] * owned
    return rows, charts


def add(rows, dst, src, coefficient):
    row = rows[dst]
    for key, value in rows[src].items():
        row[key] = row.get(key, 0) + coefficient * value
        if not row[key]:
            del row[key]


def is_multiple(row, source):
    """Return c when row == c*source for some nonzero rational c, else None."""
    if not row or not source:
        return None
    coefficient = None
    for key in set(row) | set(source):
        numerator, denominator = row.get(key, 0), source.get(key, 0)
        if denominator == 0:
            if numerator:
                return None
            continue
        ratio = numerator / denominator
        if coefficient is None:
            if ratio == 0:
                return None
            coefficient = ratio
        elif ratio != coefficient:
            return None
    return coefficient


def apply(rows, charts, event, public):
    op = event[0]
    if op == "MOVE":
        register = event[1]
        require(charts[register] == event[2] and event[4] == (register >= public),
                "MOVE chart or ownership")
        charts[register] = event[3]
    elif op == "INIT":
        register = event[1]
        require(register >= public and charts[register] is None, "INIT lifetime")
        charts[register], rows[register] = event[2], {}
    elif op == "CLEAR":
        register = event[1]
        require(register >= public and charts[register] == event[2], "CLEAR lifetime")
        charts[register], rows[register] = None, {}
    elif op == "SCALE":
        register, coefficient, chart = event[1], Q(event[2]), event[3]
        require(coefficient and charts[register] == chart, "SCALE")
        rows[register] = {key: coefficient * value
                          for key, value in rows[register].items() if coefficient * value}
    else:
        require(op in ("ADD", "COPY"), "Unknown operation")
        register, source, coefficient, chart = event[1], event[2], Q(event[3]), event[4]
        require(coefficient and charts[register] == chart and charts[source] == chart
                and source != register, "Scalar donor chart")
        require(op != "COPY" or (register >= public and not rows[register]), "COPY zero")
        add(rows, register, source, coefficient)


def frames_of(word, register):
    chart = word["initial"][register]
    frames = [chart]
    for event in word["program"]:
        if event[0] == "MOVE" and event[1] == register:
            require(event[2] == chart, "Itinerary continuity")
            chart = event[3]
            frames.append(chart)
    require(chart == word["final"][register], "Final chart")
    return frames


def replay(word, program=None):
    program = word["program"] if program is None else program
    rows, charts = fresh(word)
    public = word["public"]
    for event in program:
        apply(rows, charts, event, public)
    require(charts[:public] == word["final"], "Replay final charts")
    return rows


def move_add(program, read_slot, insert_at, frame):
    """Delete program[read_slot] and insert that ADD at index insert_at of the shortened list.

    insert_at is an index in the original program. For a later index it is also
    the post-deletion insertion index, because one earlier event was removed.
    """
    event = program[read_slot]
    require(insert_at > read_slot, "Delay target follows the read")
    body = program[:read_slot] + program[read_slot + 1:]
    placed = ["ADD", event[1], event[2], event[3], frame]
    return body[:insert_at] + [placed] + body[insert_at:]


def differing_rows(left, right):
    return [register for register, (a, b) in enumerate(zip(left, right)) if a != b]


def analyse(word):
    program = word["program"]
    public = word["public"]
    rows, charts = fresh(word)
    snapshots = {}
    for slot, event in enumerate(program):
        for case in CASES:
            if slot == case["slot"]:
                require(event == ["ADD", case["receiver"], case["source"], "2", 593],
                        "Critical read")
                snapshots[slot] = dict(rows[case["source"]])
                require(charts[case["receiver"]] == 593 and charts[case["source"]] == 593,
                        "Critical charts")
                require(rows[case["receiver"]].get(1, 0) == 0, "Receiver input 1 before the read")
                require(rows[case["source"]].get(1, 0) == Q(1, 4), "Source input 1")
        apply(rows, charts, event, public)
        for case in CASES:
            if slot == case["slot"]:
                require(rows[case["receiver"]].get(1, 0) == Q(1, 2), "Receiver input 1 after the read")
    require(charts[:public] == word["final"], "Replay final charts")
    require(set(snapshots) == {case["slot"] for case in CASES}, "Both snapshots")

    carriers = {case["slot"]: {} for case in CASES}
    direct = {case["slot"]: [] for case in CASES}
    receiver_uses = {case["slot"]: [] for case in CASES}
    present = {case["slot"]: [] for case in CASES}
    rows, charts = fresh(word)
    for slot, event in enumerate(program):
        for case in CASES:
            source_row = snapshots[case["slot"]]
            source = case["source"]
            if rows[source] == source_row and event[0] in ("ADD", "COPY") and event[2] == source:
                direct[case["slot"]].append({"slot": slot, "reader": event[1],
                                              "coefficient": str(Q(event[3])), "frame": event[4]})
            if (event[0] in ("ADD", "COPY") and event[2] == case["receiver"]
                    and case["slot"] < slot < case["arrival"]):
                receiver_uses[case["slot"]].append({
                    "slot": slot, "reader": event[1], "coefficient": str(Q(event[3])),
                    "frame": event[4], "receiver_input1": str(rows[case["receiver"]].get(1, 0)),
                })
        apply(rows, charts, event, public)
        for case in CASES:
            source_row = snapshots[case["slot"]]
            source = case["source"]
            if rows[source] == source_row:
                present[case["slot"]].append((slot, charts[source]))
            register = event[1]
            if charts[register] is None:
                continue
            coefficient = is_multiple(rows[register], source_row)
            if coefficient is not None:
                carriers[case["slot"]][(register, charts[register])] = coefficient

    original = replay(word)
    report = []
    for case in CASES:
        slot = case["slot"]
        source_row = snapshots[slot]
        require(source_row and len(source_row) == 116, "Source support")
        require(1 not in source_row or source_row[1] == Q(1, 4), "Input 1 in the source row")
        pure = [{"register": register, "chart": chart, "multiplier": str(coefficient)}
                for (register, chart), coefficient in sorted(carriers[slot].items())]
        require(pure and all(item["register"] == case["source"] and item["multiplier"] == "1"
                             for item in pure), "Unique unit carrier")
        carrier_charts = {item["chart"] for item in pure}
        receiver_frames = frames_of(word, case["receiver"])
        shared = sorted(set(receiver_frames) & carrier_charts)
        require(shared == [127, 593], "Off-593 meeting is only frame 127")
        require(present[slot], "Source row occurs")
        require(rows_changed_before(program, word, case, source_row), "Row is created at frame 593")
        runs = compress(present[slot])
        delayed_program = move_add(program, slot, case["arrival"], 127)
        require(delayed_program[case["arrival"]] == ["ADD", case["receiver"], case["source"], "2", 127],
                "Inserted read")
        require(program[case["arrival"]] == ["MOVE", case["receiver"], program[case["arrival"]][2], 127, False],
                "Arrival move")
        # The carrier still holds the snapshot when the receiver arrives.
        held_rows, held_charts = replay_until(word, delayed_program, case["arrival"])
        require(held_rows[case["source"]] == source_row, "Delay point still holds the source row")
        require(held_charts[case["source"]] == 127 and held_charts[case["receiver"]] == 127,
                "Delay point is a frame-127 meeting")
        delayed_rows = replay(word, delayed_program)
        diffs = differing_rows(original, delayed_rows)
        require(case["witness"] in diffs and case["receiver"] in diffs, "Delay changes witness rows")
        require(original[case["witness"]].get(1, 0) == 0, "Selected witness input 1")
        require(delayed_rows[case["witness"]].get(1, 0) == case["delayed"], "Delayed witness input 1")
        require(original[case["receiver"]].get(1, 0) == 0, "Selected receiver input 1")
        require(delayed_rows[case["receiver"]].get(1, 0) == Q(-1, 4), "Delayed receiver input 1")
        spliced = program[:slot] + program[slot + 1:]
        spliced = spliced[:slot] + [program[slot]] + spliced[slot:]
        require(differing_rows(original, replay(word, spliced)) == [], "Reinserted read is the original")
        report.append({
            "read_slot": slot,
            "receiver": case["receiver"],
            "source": case["source"],
            "frame": 593,
            "coefficient": "2",
            "source_support": len(source_row),
            "source_input1": "1/4",
            "receiver_input1_after_read": "1/2",
            "pure_carriers": pure,
            "carrier_charts": sorted(carrier_charts),
            "receiver_frames": receiver_frames,
            "shared_frames": shared,
            "source_row_runs": [{"first_slot": a, "last_slot": b, "chart": chart}
                                for (a, b, chart) in runs],
            "direct_reads_of_this_row": direct[slot],
            "arrival_slot": case["arrival"],
            "reads_of_receiver_before_arrival": receiver_uses[slot],
            "delay_final_row_diffs": diffs,
            "witness": {"register": case["witness"], "coordinate": 1,
                        "selected": "0", "delayed": str(case["delayed"])},
        })
    return {"status": "NO_EQUIVALENT_OFF593_HOLDER",
            "word_sha256": WORD_SHA256,
            "reads": report,
            "scope": "Pure carriers and one existing-carrier delay of the two frame-593 reads. "
                     "No new kappa, native replay or carrier retiming."}


def rows_changed_before(program, word, case, source_row):
    """The source row is not already S on the event that creates it."""
    rows, charts = fresh(word)
    public = word["public"]
    for slot, event in enumerate(program):
        if event[1] == case["source"] and event[0] in ("ADD", "SCALE", "COPY"):
            before = dict(rows[case["source"]])
            apply(rows, charts, event, public)
            if rows[case["source"]] == source_row:
                return before != source_row and charts[case["source"]] == 593
        else:
            apply(rows, charts, event, public)
    return False


def replay_until(word, program, index):
    rows, charts = fresh(word)
    for event in program[:index]:
        apply(rows, charts, event, word["public"])
    return rows, charts


def compress(samples):
    runs = []
    for slot, chart in samples:
        if runs and runs[-1][2] == chart and runs[-1][1] == slot - 1:
            runs[-1] = (runs[-1][0], slot, chart)
        else:
            runs.append((slot, slot, chart))
    return runs


def predicate_controls():
    source = {0: Q(1), 1: Q(1, 2)}
    require(is_multiple({0: Q(2), 1: Q(1)}, source) == 2, "Scaled copy")
    require(is_multiple({0: Q(1)}, source) is None, "Proper subset")
    require(is_multiple({0: Q(1), 1: Q(1, 2), 2: Q(1)}, source) is None, "Proper superset")
    require(is_multiple({}, source) is None and is_multiple(source, {}) is None, "Empty row")


def mutation_control(word):
    """Flipping the helper-469 coefficient must change the checked input-1 increment."""
    program = [list(event) for event in word["program"]]
    require(program[14380][3] == "2", "Mutable coefficient")
    program[14380][3] = "1"
    rows, charts = fresh(word)
    public = word["public"]
    for slot, event in enumerate(program):
        apply(rows, charts, event, public)
        if slot == 14380:
            require(rows[469].get(1, 0) == Q(1, 4), "Mutated increment is 1/4, not 1/2")
            return
    raise ValueError("Mutated read was not reached")


def main():
    predicate_controls()
    word = load_word()
    mutation_control(word)
    measured = analyse(word)
    result_path = PACKAGE / "RESULT.json"
    if "--write" in __import__("sys").argv:
        result_path.write_text(json.dumps(measured, indent=2) + "\n", encoding="utf-8")
    committed = json.loads(result_path.read_text(encoding="utf-8"))
    require(measured == committed, "Committed certificate")
    print("PASS_P104_FRAME593_CONTENT_HOLDERS")


if __name__ == "__main__":
    main()
