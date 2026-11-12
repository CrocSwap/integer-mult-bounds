"""Check four exact public routes for the two chart-32 signed exchange blocks."""
from bisect import bisect_left, bisect_right
from collections import Counter
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "1d9f68e5cd370846b55f36e522d0b2b2468430179ef9337ec2cf3848c1628894",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
MATRICES = {319: [["0", "1"], ["1", "1"]], 1081: [["-1", "1"], ["1", "0"]]}


def unique(items):
    document = dict(items)
    if len(document) != len(items):
        raise ValueError("duplicate JSON key")
    return document


def checked(rel):
    data = (ROOT / rel).read_bytes()
    if sha256(data).hexdigest() != PINS[rel]:
        raise ValueError(f"changed dependency {rel}")
    return data


def frame_span(frame):
    result = {0}
    for vector in frame:
        assert vector not in result
        result |= {x ^ vector for x in result}
    return result


def action(ops, roles):
    vals = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
    for op, role, *args in ops:
        d = roles.index(role)
        if op == "SCALE":
            vals[d] = [Fraction(args[0]) * x for x in vals[d]]
        else:
            assert op == "ADD"
            s = roles.index(args[0])
            vals[d] = [x + Fraction(args[1]) * y for x, y in zip(vals[d], vals[s])]
    return [[str(x) for x in row] for row in vals]


def controls():
    ops = [["ADD", 35, 319, "1", 32], ["SCALE", 319, "-1", 32], ["ADD", 319, 35, "1", 32]]
    assert action(ops, [319, 35]) == MATRICES[319]
    wrong = [ops[0], ["SCALE", 319, "1", 32], ops[2]]
    assert action(wrong, [319, 35]) != MATRICES[319]
    a, b, c = [frame_span(f) for f in ([], [1], [1, 2])]
    assert a <= a <= b and b <= c <= c and not b <= a and not c <= b
    assert (len(b).bit_length() - len(a).bit_length()) == 1
    return ["signed scale mutation", "zero and compensating rank-one leg", "strict span direction"]


def trace(word, roles, spans):
    n = word["public"]
    state = word["initial"] + [None] * word["owned_fields"]
    incidents = {r: [] for r in roles}
    for t, event in enumerate(word["program"]):
        op, d, *args = event
        current = state[d]
        if op == "MOVE":
            start, end, owned = args
            assert start == current and owned == (d >= n)
            assert spans(start) < spans(end) or owned and spans(end) < spans(start)
            state[d] = end
        elif op == "INIT":
            assert d >= n and current is None
            state[d] = args[0]
        elif op == "CLEAR":
            assert d >= n and current == args[0]
            state[d] = None
        else:
            assert op in ("ADD", "COPY", "SCALE") and current == args[-1]
            if op in ("ADD", "COPY"):
                assert args[0] != d and state[args[0]] == current
        touched = [d, args[0]] if op in ("ADD", "COPY") else [d]
        for r in touched:
            if r in incidents:
                incidents[r].append(t)
    assert state == word["final"] + [None] * word["owned_fields"]
    return incidents


def rail(word, role, mid, times, first, last):
    program = word["program"]
    left = bisect_left(times, first)
    right = bisect_right(times, last)
    inside = [(t, program[t]) for t in times[left:right]]
    before = times[left - 1] if left else None
    after = times[right] if right < len(times) else None
    if before is None:
        start = word["initial"][role]
    elif program[before][0] == "MOVE":
        _, target, start, end, owner = program[before]
        assert target == role and end == mid and not owner
    else:
        start = program[before][-1]
        assert start == mid
    if after is None:
        end = word["final"][role]
    elif program[after][0] == "MOVE":
        _, target, start_chart, end, owner = program[after]
        assert target == role and start_chart == mid and not owner
    else:
        end = program[after][-1]
        assert end == mid
    return {"role": role, "before": [before, program[before]] if before is not None else None,
            "after": [after, program[after]] if after is not None else None,
            "outer": [start, end], "inside": inside}


def classify(word, stock, incidents, spans, price):
    f, g, mover = stock["key"]
    a, mid, c = stock["charts"]
    first, _, last = [t for t, _ in stock["contacts"]]
    assert word["program"][f] == ["MOVE", mover, a, mid, False]
    assert word["program"][g] == ["MOVE", mover, mid, c, False]
    assert all(word["program"][t] == event for t, event in stock["contacts"])
    peer, = set(stock["contacts"][0][1][1:3]) - {mover}
    roles = [mover, peer]
    assert all(0 <= r < word["public"] for r in roles)
    actual_matrix = action([event for _, event in stock["contacts"]], roles)
    assert actual_matrix == MATRICES[mover]
    rails = [rail(word, r, mid, incidents[r], first, last) for r in roles]
    assert rails[0]["before"][0] == f and rails[0]["after"][0] == g
    good_inside = all([list(x) for x in path["inside"]] ==
                      [e for e in stock["contacts"] if path["role"] in (e[1][1:3] if e[1][0] == "ADD" else e[1][1:2])]
                      for path in rails)
    ranks = [len(frame) for frame in word["frames"]]
    p_chart, q_chart = rails[1]["outer"]
    assert spans(p_chart) <= spans(mid) <= spans(q_chart)
    peer_ranks = [ranks[mid] - ranks[p_chart], ranks[q_chart] - ranks[mid]]
    cases = []
    for side, chart in [("A", a), ("C", c)]:
        failed = []
        for path in rails:
            source, target = path["outer"]
            if not spans(source) <= spans(chart):
                failed.append([path["role"], "entrance", source, chart])
            if not spans(chart) <= spans(target):
                failed.append([path["role"], "exit", chart, target])
        profile = next((q for q in price["profiles"] if q["side"] == side and q["peer_old"] == peer_ranks), None)
        if not good_inside:
            status = "extra role contact"
        elif failed:
            status = "nesting exclusion"
        elif profile is None or Fraction(profile["complete_probe"][0]) <= 0:
            status = "directed price exclusion"
        else:
            status = "positive topology survivor"
        cases.append({"side": side, "chart": chart, "failed_legs": failed,
                      "status": status, "price": profile})
    return {"key": stock["key"], "roles": roles, "matrix": actual_matrix, "rails": rails,
            "exact_middle_contacts": good_inside, "old_peer_ranks": peer_ranks, "cases": cases}


def stop(*_):
    raise TimeoutError("hard 20-second cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(20)
    price = loads(checked("plan/PRICE.json"), object_pairs_hook=unique)
    assert price["runner_limits"]["literal_events"] == 76466
    assert len(price["stock"]) == 2 and len(price["profiles"]) == 90
    raw = decompress(checked("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw, object_pairs_hook=unique)
    assert len(word["program"]) == 76466
    roles = {319, 35, 1081, 807}

    @cache
    def spans(label):
        return frame_span(word["frames"][label])

    incidents = trace(word, roles, spans)
    results = [classify(word, entry, incidents, spans, price) for entry in price["stock"]]
    assert {r for row in results for r in row["roles"]} == roles
    counts = Counter(case["status"] for row in results for case in row["cases"])
    alarm(0)
    print(dumps({"pins": PINS, "head": price["head"], "caller": price["caller_head"],
                 "controls": controls(), "literal_events": len(word["program"]), "results": results,
                 "counts": counts, "unvisited": []}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
