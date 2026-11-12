"""Independently intersect role 1454's contact spans and certify all reverse pairings."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

PINS = {
    "inputs/word.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/bank_trace.py": "681fda5cc1d4b1ac07c62601ceb052f167a51fb73d28b23f454f8f50f6a8e27b",
    "lead/GEOMETRY.json": "f2aa238ed8c49f0633c3837c6961bfba19482385851a5606578fa6368db79542",
    "third/IMPULSE.json": "d7b30091bd881711f4de7339216368ef8de1649e35cddb00d4dd29be2185b3af",
    "third/PREFIX.json": "e17e9b4dfb359eed4e478ea6ae7d2cc247687867054f3991f19bbd51e4ab73d9",
    "followup/KEYS.json": "ee3ad61078a0a2e5e0a0dcdab672734fa60ffd49880fd12d328f1d1e5490a065",
    "followup/RESULT.json": "d2d31b2fc11f0d0388e2c0238df4bcac3d68293154ad72b3de2f6f0046d7697e",
}
THIRD, PIVOT, CASES, SECONDS = 1454, 1481, 15, 20


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON keys")
    return result


def stop(*_):
    raise TimeoutError("20-second independent cap")


def chart_intervals(word):
    chart, lo = word["initial"][THIRD], 0
    for clock, (op, dest, *args) in enumerate(word["program"]):
        if dest != THIRD and not (op in ("ADD", "COPY") and args[0] == THIRD):
            continue
        yield lo, clock, chart
        lo = clock + 1
        if op == "MOVE":
            assert dest == THIRD and args[0] == chart and not args[2]
            chart = args[1]
        else:
            assert op in ("ADD", "COPY", "SCALE") and args[-1] == chart
    assert chart == word["final"][THIRD]
    yield lo, len(word["program"]), chart


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + SECONDS
    raw = {p: (args.root / p).read_bytes() for p in PINS}
    for path, data in raw.items():
        if sha256(data).hexdigest() != PINS[path]:
            raise ValueError(f"changed dependency {path}")
    docs = {p: loads(v, object_pairs_hook=unique) for p, v in raw.items() if p.endswith(".json")}
    payload = decompress(raw["inputs/word.json.gz"])
    assert sha256(payload).hexdigest() == "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word = loads(payload, object_pairs_hook=unique)
    assert len(word["program"]) == 76466
    geometry = docs["lead/GEOMETRY.json"]
    third_spans = list(chart_intervals(word))
    ranges = []
    for role, pivot, chart, lo, hi in geometry["ranges"]:
        assert pivot == PIVOT and THIRD not in (role, pivot)
        for a, b, other_chart in third_spans:
            start, end = max(lo, a), min(hi, b)
            if chart == other_chart and start <= end:
                ranges.append((role, pivot, THIRD, chart, start, end))
    receipt = docs["third/IMPULSE.json"]
    saved = set()
    for row in receipt["unresolved"]:
        role, pivot, chart, _, _ = row["range"]
        segment = row["segment"]
        saved.add((role, pivot, THIRD, chart, segment["first"], segment["last"]))
    assert len(ranges) == CASES and set(ranges) == saved
    raw_cuts = sum(hi - lo + 1 for _, _, _, _, lo, hi in ranges)
    assert raw_cuts == receipt["counts"]["prefix pending"] == 16494
    assert geometry["raw_cuts"] - raw_cuts == receipt["counts"]["no coframe"] == 3961
    prefix = docs["third/PREFIX.json"]
    checked = {tuple(row["key"]) for row in prefix["rows"]}
    assert len(checked) == 8
    followup = docs["followup/RESULT.json"]
    remaining = {tuple(row) for row in docs["followup/KEYS.json"]["ranges"]}
    assert len(remaining) == 7 and {tuple(row["range"]) for row in followup["rows"]} == remaining
    assert sum(row[-1] - row[-2] + 1 for row in remaining) == followup["raw_cuts"] == 478
    assert {(*row[:4], row[-1]) for row in ranges if row not in remaining} == checked
    algebra = run_path(str(args.root / "inputs/bank_trace.py"))
    impulse = {1251: Fraction(1), PIVOT: Fraction(4)}
    rows = []
    for key in ranges:
        role, pivot, third, _, _, hi = key
        roles = [role, pivot, third]
        bank = algebra["trace"](word, hi, roles, deadline, True)
        pairing = [algebra["dot"](bank[r], impulse) for r in roles]
        required = impulse.get(role, 0) - impulse[pivot]
        assert pairing == [0, 0, 0] and required == -4
        rows.append(dict(key=key, support=[len(bank[r]) for r in roles],
                         evaluations=list(map(str, pairing)), required=str(required)))
    predecessor = algebra["trace"](word, 0, [1251, PIVOT], deadline, True)
    assert [algebra["dot"](predecessor[r], impulse) for r in (1251, PIVOT)] == [1, 4]
    alarm(0)
    result = dict(head=geometry["head"], caller=geometry["caller"], pins=PINS, cases=CASES,
                  coframed_raw_cuts=raw_cuts, unresolved=0, rows=rows)
    args.output.write_text(dumps(result, sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    main()
