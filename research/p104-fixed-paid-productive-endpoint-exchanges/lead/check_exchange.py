"""Screen a frozen native word for paid-neutral two-role endpoint exchanges."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

CAP = 32
WINDOW_CAP = 64
PINS = {
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def cap(_signal, _frame):
    raise SystemExit(124)


def coordinates(event):
    if event[0] == "ADD":
        return frozenset(event[1:3]), event[-1]
    if event[0] == "SCALE":
        return frozenset([event[1]]), event[-1]
    return frozenset(), None


def windows(tape, public):
    """Find maximal contiguous intervals for the exact pair and chart of an ADD."""
    tagged = [coordinates(event) for event in tape]
    reached = {}
    for anchor, (pair, chart) in enumerate(tagged):
        if len(pair) != 2 or max(pair) >= public:
            continue
        key = (chart, pair)
        if reached.get(key, -1) > anchor:
            continue
        start, stop = anchor, anchor + 1
        while start:
            roles, frame = tagged[start - 1]
            if frame != chart or not roles or not roles <= pair:
                break
            start -= 1
        while stop < len(tape):
            roles, frame = tagged[stop]
            if frame != chart or not roles or not roles <= pair:
                break
            stop += 1
        reached[key] = stop
        yield start, stop, chart, tuple(sorted(pair))


def spans(frames):
    result = []
    for basis in frames:
        space = {0}
        for vector in basis:
            space |= {x ^ vector for x in space}
        assert len(space) == 2 ** len(basis)
        result.append(space)
    return result


def product(events, pair):
    rows = {pair[0]: (Fraction(1), Fraction(0)),
            pair[1]: (Fraction(0), Fraction(1))}
    for op, dest, *parts in events:
        if op == "ADD":
            source, coefficient, _ = parts
            rows[dest] = tuple(a + Fraction(coefficient) * b
                               for a, b in zip(rows[dest], rows[source]))
        else:
            assert op == "SCALE"
            rows[dest] = tuple(Fraction(parts[0]) * a for a in rows[dest])
    return [rows[role] for role in pair]


def signed_exchange(rows):
    (a, b), (c, d) = rows
    return a == d == 0 and abs(b) == abs(c) == 1


def price_class(old, new):
    assert sum(old) == sum(new)
    return (abs(old[0] - old[1]) > abs(new[0] - new[1])) - (
        abs(old[0] - old[1]) < abs(new[0] - new[1]))


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=Path(__file__).resolve().parents[1] / "inputs")
    args = parser.parse_args()
    signal(SIGALRM, cap)
    alarm(30)
    raw = {name: (args.inputs / name).read_bytes() for name in PINS}
    assert {name: sha256(blob).hexdigest() for name, blob in raw.items()} == PINS
    decoded = decompress(raw["7481-WORD.json.gz"])
    assert sha256(decoded).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(decoded)
    app = loads(raw["7481-APPLICATION.json"])
    caller = loads(raw["7113-CALLER.json"])
    assert caller["stages"] == 17
    lo, hi = map(Fraction, app["directed_crossing_bracket"])
    assert 0 < lo < hi < 1
    ranks = list(map(len, word["frames"]))
    space = spans(word["frames"])
    main_roles = set(word["live"]) | {r + 112 for r in word["live"]}
    main_roles.update(word["hosted"]["X2"] + word["hosted"]["Y2"])
    assert len(main_roles) == 400
    tape = word["program"]
    assert len(tape) == 76475 and word["public"] == 1501
    assert product(tape[35351:35354], (798, 1135)) == [(0, -1), (1, 0)]
    assert not signed_exchange(product(tape[35351:35353], (798, 1135)))
    assert price_class((7, 9), (8, 8)) == 1
    assert price_class((8, 4), (3, 9)) == -1
    power = run_path(str(args.inputs / "pricing.py"))["power_bounds"]

    counts = Counter()
    tested, pending, rejects = [], [], {}
    for start, stop, chart, pair in sorted(windows(tape, word["public"])):
        counts["all_maximal_windows"] += 1
        identity = [start, stop, chart, list(pair)]
        left, right = pair
        i, j = (word["initial"][role] for role in pair)
        a, b = (word["final"][role] for role in pair)
        old = (ranks[a] - ranks[i], ranks[b] - ranks[j])
        new = (ranks[b] - ranks[i], ranks[a] - ranks[j])
        if stop - start > WINDOW_CAP:
            reason = "above_window_length"
        elif main_roles.intersection(pair):
            reason = "fixed_main_role"
        elif min(old) <= 0:
            reason = "not_two_productive_targets"
        elif min(new) <= 0 or price_class(old, new) <= 0:
            reason = "not_strictly_positive_crossed_price"
        elif not (space[i] < space[b] and space[j] < space[a]):
            reason = "crossed_frames_not_nested"
        else:
            reason = None
        if reason:
            counts[reason] += 1
            rejects.setdefault(reason, []).append(identity)
            continue
        counts["eligible"] += 1
        if len(tested) == CAP:
            pending.append(identity)
            continue
        low = 17 * (sum(power(r, hi)[0] for r in new) - sum(power(r, lo)[1] for r in old))
        high = 17 * (sum(power(r, lo)[1] for r in new) - sum(power(r, hi)[0] for r in old))
        assert 0 < low <= high
        matrix = product(tape[start:stop], pair)
        tested.append({"id": identity, "old": old, "new": new, "gross": [low, high],
                       "action": matrix, "signed_exchange": signed_exchange(matrix)})
    print(dumps({"scope": "maximal by exact chart and pair anchored on ADD",
                 "status": "CAPPED" if pending else "EXHAUSTED",
                 "time_cap_seconds": 30, "matrix_cap": CAP,
                 "counts": counts, "pins": PINS, "tested": tested, "unresolved": pending,
                 "rejected_ids": rejects, "controls": "literal sign and incomplete exchange pass"},
                indent=2, sort_keys=True, default=str))
    alarm(0)


if __name__ == "__main__":
    main()
