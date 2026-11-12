"""Walk the exact public paths for four fixed-peer signed two-ADD retimes."""
from bisect import bisect_left
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from itertools import groupby
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "8226a2b9c9240455d6fcdaf3a38929e3336e89f35aed3f15b81564f07ed8387f",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
WORD_PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def checked(path):
    data = (ROOT / path).read_bytes()
    if sha256(data).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return data


def frame_span(frame):
    span = {0}
    for vector in frame:
        assert vector not in span
        span |= {vector ^ prior for prior in span}
    return span


def contacts(event):
    return event[1:3] if event[0] in ("ADD", "COPY") else event[1:2]


def signed_action(pair, roles):
    matrix = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    for _, event in pair:
        op, destination, source, coeff, _ = event
        assert op == "ADD"
        d, s = roles.index(destination), roles.index(source)
        matrix[d] = [x + Fraction(coeff) * y for x, y in zip(matrix[d], matrix[s])]
    return [[str(x) for x in row] for row in matrix]


def pre_chart(cut, moves, initial):
    index = bisect_left([clock for clock, _ in moves], cut)
    return moves[index - 1][1][3] if index else initial


def intervals(rows):
    out = []
    for value, run in groupby(rows, key=lambda row: row[1:]):
        clocks = [clock for clock, *_ in run]
        assert clocks[-1] - clocks[0] + 1 == len(clocks)
        out.append([clocks[0], clocks[-1], *value])
    return out


def controls():
    move = (9, ["MOVE", 2, 4, 7, False])
    assert [pre_chart(c, [move], 4) for c in (8, 9, 10)] == [4, 4, 7]
    assert contacts(["ADD", 3, 2, "-1", 4]) == [3, 2]
    assert contacts(["COPY", 3, 2, "1", 4]) == [3, 2]
    assert contacts(["SCALE", 2, "1/2", 4]) == [2]
    assert signed_action([(0, ["ADD", 2, 3, "-1", 4]), (1, ["ADD", 3, 2, "1/2", 4])],
                         [2, 3]) == [["1", "-1"], ["1/2", "1/2"]]
    return ["pre-event MOVE boundary", "ADD/COPY source contacts", "signed sequential ADD"]


def trace(word, roles):
    public = word["public"]
    initial = word["initial"] + [None] * word["owned_fields"]
    state = initial[:]
    moves = {role: [] for role in roles}
    scalar = {role: [] for role in roles}
    spans = [frame_span(frame) for frame in word["frames"]]
    for clock, event in enumerate(word["program"]):
        op, destination, *args = event
        current = state[destination]
        owned = destination >= public
        if op == "MOVE":
            before, after, recorded_owned = args
            assert before == current and recorded_owned == owned
            assert spans[before] < spans[after] or owned and spans[after] < spans[before]
            state[destination] = after
            if destination in moves:
                moves[destination].append((clock, event))
        elif op in ("INIT", "CLEAR"):
            assert owned
            if op == "INIT":
                assert current is None
                state[destination] = args[0]
            else:
                assert current == args[0]
                state[destination] = None
        else:
            assert op in ("ADD", "COPY", "SCALE")
            assert current == args[-1] and Fraction(args[-2])
            if op in ("ADD", "COPY"):
                assert args[0] != destination and state[args[0]] == current
        if op != "MOVE":
            for role in contacts(event):
                if role in scalar:
                    scalar[role].append((clock, event))
    assert state == word["final"] + [None] * word["owned_fields"]
    return initial, moves, scalar


def classify(case, program, initial, moves, scalar):
    f, g, mover = case["key"]
    a, b, c = case["charts"]
    peer = case["peer"]
    low, high = case["late_pre_event_cuts"]
    assert (low, high) == (f + 3, g)
    assert program[f] == ["MOVE", mover, a, b, False]
    assert program[g] == ["MOVE", mover, b, c, False]
    pair = [[i, program[i]] for i in (f + 1, f + 2)]
    assert pair == case["original_pair"]
    assert signed_action(pair, [mover, peer]) == case["normalized_matrix"]
    assert [(t, e) for t, e in moves[mover] if f <= t <= g] == [
        (f, program[f]), (g, program[g])
    ]
    assert [[t, e] for t, e in scalar[mover] if f < t < g] == pair
    assert pre_chart(f + 1, moves[peer], initial[peer]) == b
    assert pre_chart(f + 2, moves[peer], initial[peer]) == b
    peer_contacts = [(t, e) for t, e in scalar[peer] if low <= t < high]
    first = peer_contacts[0] if peer_contacts else None
    cuts = []
    for cut in range(low, high + 1):
        chart = pre_chart(cut, moves[peer], initial[peer])
        assert chart != a
        clean = first is None or first[0] >= cut
        cuts.append((cut, chart, clean, chart == c and clean))
    return {
        "key": case["key"], "peer": peer, "charts": [a, b, c],
        "early_excluded": len(cuts), "late_tested": len(cuts),
        "first_crossed_scalar": first,
        "peer_moves_through_window": [(t, e) for t, e in moves[peer] if low <= t < high],
        "first_peer_scalars_in_corridor": peer_contacts[:2],
        "late_intervals": intervals(cuts),
        "late_peer_at_c": sum(chart == c for _, chart, _, _ in cuts),
        "late_peer_at_c_with_exactly_one_crossed_scalar": sum(
            chart == c and first is not None and first[0] < cut
            and (len(peer_contacts) < 2 or cut <= peer_contacts[1][0])
            for cut, chart, _, _ in cuts
        ),
        "survivors": [cut for cut, _, _, passed in cuts if passed],
    }


def timeout(*_):
    raise TimeoutError("20-second replay cap")


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(20)
    cases, windows = [], []
    reason = None
    events = None
    try:
        price = loads(checked("plan/PRICE.json"), object_pairs_hook=unique)
        cases = price["cases"]
        assert price["caps"] == {"late_cuts": 4124, "prototypes": 1, "runner_seconds": 20,
                                 "typed_cuts": 8248, "windows": 4}
        assert price["word_sha256"] == PINS["inputs/7334-WORD.json.gz"]
        raw = decompress(checked("inputs/7334-WORD.json.gz"))
        assert sha256(raw).hexdigest() == price["payload_sha256"] == WORD_PAYLOAD
        word = loads(raw, object_pairs_hook=unique)
        program = word["program"]
        assert len(program) == 76466 and word["public"] == 1501
        assert len(cases) == 4 and sum(r["per_endpoint_typed_count"] for r in cases) == 4124
        roles = {role for row in cases for role in (row["key"][2], row["peer"])}
        assert len(roles) == 8 and min(roles) >= 0 and max(roles) < word["public"]
        initial, moves, scalar = trace(word, roles)
        events = len(program)
        for case in cases:
            windows.append(classify(case, program, initial, moves, scalar))
    except TimeoutError as exc:
        reason = str(exc)
    finally:
        alarm(0)
    counts = Counter()
    for row in windows:
        counts.update({key: row[key] for key in (
            "early_excluded", "late_tested", "late_peer_at_c",
            "late_peer_at_c_with_exactly_one_crossed_scalar"
        )})
        counts["survivors"] += len(row["survivors"])
    print(dumps({
        "pins": PINS, "word_payload_sha256": WORD_PAYLOAD, "controls": controls(),
        "completed_literal_events": events, "windows": windows, "counts": counts,
        "unresolved_late_cut_intervals": [r["late_pre_event_cuts"] for r in cases[len(windows):]],
        "unresolved_late_count": 4124 - counts["late_tested"], "timeout": reason,
    }, indent=2, sort_keys=True))
    if reason:
        raise SystemExit(124)


if __name__ == "__main__":
    main()
