"""Enumerate exact #7481 endpoint-exchange windows from reverse literal ADD anchors."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import alarm
from time import perf_counter

PINS = {
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
MAX_WINDOW, CASES = 64, 32
REGRESSIONS = (28403, 34444, 35351, 35458, 35509, 37023, 37388, 37539, 45477)


def span(axes):
    space = {0}
    for axis in axes:
        space |= {axis ^ word for word in space}
    return space


def event_pair(event):
    if event[0] == "ADD":
        return frozenset(event[1:3])
    if event[0] == "SCALE":
        return frozenset([event[1]])
    return frozenset()


def compatible(event, roles, chart):
    used = event_pair(event)
    return bool(used) and used <= roles and event[-1] == chart


def windows_reverse(tape, public):
    # Any useful window contains an ADD. Expanding a fixed ADD anchor in
    # both directions finds its unique maximal window, including edge SCALEs.
    windows = set()
    for clock in range(len(tape) - 1, -1, -1):
        event = tape[clock]
        if event[0] != "ADD":
            continue
        roles = event_pair(event)
        if len(roles) != 2 or max(roles) >= public:
            continue
        chart = event[-1]
        lo, hi = clock, clock + 1
        while lo and compatible(tape[lo - 1], roles, chart):
            lo -= 1
        while hi < len(tape) and compatible(tape[hi], roles, chart):
            hi += 1
        windows.add((lo, hi, *sorted(roles), chart))
    return sorted(windows)


def literal_matrix(tape, roles):
    a, b = roles
    rows = {a: [Q(1), Q(0)], b: [Q(0), Q(1)]}
    for event in tape:
        op, dest = event[:2]
        scalar = Q(event[-2])
        if op == "SCALE":
            rows[dest] = [value * scalar for value in rows[dest]]
        else:
            src = event[2]
            rows[dest] = [value + scalar * update
                          for value, update in zip(rows[dest], rows[src])]
    return [rows[a], rows[b]]


def is_crossed(matrix):
    return matrix[0][0] == matrix[1][1] == 0 and bool(matrix[0][1] and matrix[1][0])


def price_sign(old, crossed):
    assert sum(old) == sum(crossed) and min(*old, *crossed) > 0
    # For 0<kappa<1, fixed-sum strict concavity orders any two ranks
    # strictly by their imbalance, even when the intervals are close.
    balance_gain = abs(old[1] - old[0]) - abs(crossed[1] - crossed[0])
    return (balance_gain > 0) - (balance_gain < 0)


def positive_price(old, new, price, bracket):
    lo, hi = bracket
    lower = 17 * (sum(price(rank, hi)[0] for rank in new)
                  - sum(price(rank, lo)[1] for rank in old))
    upper = 17 * (sum(price(rank, lo)[1] for rank in new)
                  - sum(price(rank, hi)[0] for rank in old))
    assert lower <= upper
    return lower, upper


def endpoint_geometry(word, roles, main, spaces):
    if set(roles) & main:
        return "hosted", None, None
    a, b = roles
    u, v = (word["initial"][r] for r in roles)
    x, y = (word["final"][r] for r in roles)
    frames = word["frames"]
    old = (len(frames[x]) - len(frames[u]), len(frames[y]) - len(frames[v]))
    new = (len(frames[y]) - len(frames[u]), len(frames[x]) - len(frames[v]))
    if not (spaces[u] < spaces[x] and spaces[v] < spaces[y]):
        return "nonproductive_old", old, new
    if not (spaces[u] < spaces[y] and spaces[v] < spaces[x]):
        return "crossed_not_strictly_nested", old, new
    sign = price_sign(old, new)
    return {-1: "negative_price", 0: "equal_price", 1: "positive_price"}[sign], old, new


def controls(price, bracket):
    good = [["ADD", 0, 1, "1", 0], ["ADD", 1, 0, "-1", 0],
            ["ADD", 0, 1, "1", 0], ["SCALE", 1, "-1", 0]]
    changed = [event.copy() for event in good]
    changed[1][3] = "-2"
    assert windows_reverse(good, 2) == [(0, 4, 0, 1, 0)]
    assert is_crossed(literal_matrix(good, (0, 1)))
    assert not is_crossed(literal_matrix(changed, (0, 1)))
    toy = {"initial": [0, 1], "final": [3, 2],
           "frames": [[], [1, 2], [1, 2, 4], [1, 2, 4, 8, 16, 32]]}
    spaces = list(map(span, toy["frames"]))
    assert endpoint_geometry(toy, (0, 1), set(), spaces) == ("positive_price", (6, 1), (3, 4))
    assert positive_price((6, 1), (3, 4), price, bracket)[0] > 0
    toy["frames"][2] = [1, 4, 8]
    spaces = list(map(span, toy["frames"]))
    toy["final"] = [2, 3]
    assert endpoint_geometry(toy, (0, 1), set(), spaces)[0] == "crossed_not_strictly_nested"
    assert price_sign((4, 5), (3, 6)) == -1


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    root = parser.parse_args().inputs
    start = perf_counter()
    alarm(30)
    blob = {path: (root / path).read_bytes() for path in PINS}
    assert {path: sha256(data).hexdigest() for path, data in blob.items()} == PINS
    raw = gzip.decompress(blob["7481-WORD.json.gz"])
    assert sha256(raw).hexdigest() == NATIVE
    word = json.loads(raw)
    tape = word["program"]
    assert len(tape) == 76475
    app = json.loads(blob["7481-APPLICATION.json"])
    assert app["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    bracket = tuple(map(Q, app["directed_crossing_bracket"]))
    assert 0 < bracket[0] <= bracket[1] < 1
    price = run_path(str(root / "pricing.py"))["power_bounds"]
    controls(price, bracket)
    main_roles = set(word["live"]) | {r + 112 for r in word["live"]}
    main_roles.update(word["hosted"]["X2"] + word["hosted"]["Y2"])
    spaces = list(map(span, word["frames"]))
    window_list = windows_reverse(tape, word["public"])
    by_case = {}
    eligible, above_window_limit = [], []
    for lo, hi, a, b, chart in window_list:
        status, old, crossed = endpoint_geometry(word, (a, b), main_roles, spaces)
        key = (lo, hi, a, b, chart)
        by_case[key] = status
        if status == "positive_price":
            bucket = eligible if hi-lo <= MAX_WINDOW else above_window_limit
            bucket.append((key, old, crossed))
    regression = []
    for clock in REGRESSIONS:
        roles = tuple(sorted(event_pair(tape[clock])))
        matrix = literal_matrix(tape[clock:clock + 3], roles)
        assert is_crossed(matrix)
        containing = [case for case in by_case if case[0] <= clock < case[1]
                      and case[2:4] == roles]
        assert len(containing) == 1 and clock + 3 <= containing[0][1]
        regression.append((clock, roles, by_case[containing[0]]))
    checked, open_cases = eligible[:CASES], eligible[CASES:]
    exact = []
    for key, old, crossed in checked:
        lo, hi, a, b, _ = key
        directed = positive_price(old, crossed, price, bracket)
        assert directed[0] > 0
        matrix = literal_matrix(tape[lo:hi], (a, b))
        exact.append({"case": key, "old_ranks": old, "new_ranks": crossed,
                      "raw_signed_saving_interval": directed, "matrix": matrix,
                      "crossed_monomial": is_crossed(matrix)})
    survivors = [case["case"] for case in exact if case["crossed_monomial"]]
    counts = Counter(by_case.values())
    print(json.dumps({
        "status": "SURVIVOR" if survivors else "CAPPED" if open_cases else "EXHAUSTED",
        "case_key": ["start_inclusive", "end_exclusive", "lower_role", "higher_role", "chart"],
        "pinned_word_sha256": NATIVE, "case_cap": CASES, "window_length_limit": MAX_WINDOW,
        "metadata_window_count": len(by_case), "classification_counts": counts,
        "classified_windows": [[*key, label] for key, label in by_case.items()],
        "regressions": regression, "synthetic_controls": "PASS",
        "checked": exact, "survivor_ids": survivors, "open_cap_cases": open_cases,
        "out_of_domain_positive_above_window_limit": above_window_limit,
        "seconds": perf_counter() - start,
    }, default=str, sort_keys=True, indent=2))
    alarm(0)


if __name__ == "__main__":
    main()
