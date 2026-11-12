"""Rebuild all eligible cochart intervals and certify a backward separating pairing."""
from argparse import ArgumentParser
from collections import defaultdict
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
    "lead/PRICE.json": "7b0ccc8fd85240568aeddfc1e2c036ac05ab0ec6e8473522bd902a4adcc1e9eb",
    "lead/GEOMETRY.json": "f2aa238ed8c49f0633c3837c6961bfba19482385851a5606578fa6368db79542",
    "lead/BARE.json": "1f19c66e75543ff50f4537d99811812e96935e2c5d3e75ad3a6b23f8032b7869",
    "lead/BASIS.json": "0688a6fe35487c3b79abaca48b583c6cad6a865bd7ae6b5addba846549807092",
    "followup/KEYS.json": "b8566442ed245a2302d287c480cf95d647343ff4f0f141ba6072603fed5bdd6b",
    "followup/RESULT.json": "9970468e3413e143eb9d328512b4e60aacb21672cbb5722ec0e5dd608fe58d14",
}
PIVOT, CAP, SECONDS = 1481, 20, 20


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON keys")
    return result


def stop(*_):
    raise TimeoutError("20-second independent cap")


def intervals(word, roles):
    tape = word["program"]
    charts = {role: word["initial"][role] for role in roles}
    starts = dict.fromkeys(roles, 0)
    stays = defaultdict(list)
    for clock, (op, dest, *args) in enumerate(tape):
        touched = {dest, args[0]} if op in ("ADD", "COPY") else {dest}
        for role in touched & roles:
            stays[role].append((starts[role], clock, charts[role]))
            starts[role] = clock + 1
            if op == "MOVE":
                assert args[0] == charts[role] and args[2] is False
                charts[role] = args[1]
            else:
                assert op in ("ADD", "COPY", "SCALE") and args[-1] == charts[role]
    for role in roles:
        assert charts[role] == word["final"][role]
        stays[role].append((starts[role], len(tape), charts[role]))
    ranges = []
    for role in roles - {PIVOT}:
        i = j = 0
        a, b = stays[role], stays[PIVOT]
        while i < len(a) and j < len(b):
            al, ar, ac = a[i]
            bl, br, bc = b[j]
            lo, hi = max(al, bl), min(ar, br)
            if ac == bc and lo <= hi:
                ranges.append((role, PIVOT, ac, lo, hi))
            i += ar <= br
            j += br <= ar
    return sorted(ranges)


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + SECONDS
    raw = {path: (args.root / path).read_bytes() for path in PINS}
    for path, payload in raw.items():
        if sha256(payload).hexdigest() != PINS[path]:
            raise ValueError(f"changed dependency {path}")
    saved = {path: loads(data, object_pairs_hook=unique) for path, data in raw.items() if path.endswith(".json")}
    payload = decompress(raw["inputs/word.json.gz"])
    assert sha256(payload).hexdigest() == "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word = loads(payload, object_pairs_hook=unique)
    price = saved["lead/PRICE.json"]
    roles = set(price["other_role_cohort"])
    assert len(roles) == 615 and PIVOT not in roles
    for role in roles:
        assert (word["initial"][role], word["final"][role]) == (3, 127)
    ranges = intervals(word, roles | {PIVOT})
    geometry = saved["lead/GEOMETRY.json"]
    assert ranges == [tuple(row) for row in geometry["ranges"]] and len(ranges) == CAP
    assert sum(hi - lo + 1 for _, _, _, lo, hi in ranges) == geometry["raw_cuts"] == 20455
    basis = {tuple(row["key"]) for row in saved["lead/BASIS.json"]["rows"]}
    bare = {tuple(row["key"]) for row in saved["lead/BARE.json"]["rows"]}
    supplement = {tuple(row) for row in saved["followup/KEYS.json"]["ranges"]}
    closure = saved["followup/RESULT.json"]
    assert not closure["unresolved"] and {tuple(row["range"]) for row in closure["rows"]} == supplement
    assert len(basis) == 8 and len(bare) == 16 and basis <= bare and len(supplement) == 12
    assert {(*row[:3], row[-1]) for row in ranges if row not in supplement} == basis
    algebra = run_path(str(args.root / "inputs/bank_trace.py"))
    impulse = {1454: Fraction(1), PIVOT: Fraction(-2)}
    rows = []
    for role, pivot, chart, lo, hi in ranges:
        bank = algebra["trace"](word, hi, [role, pivot], deadline, True)
        pairing = [algebra["dot"](bank[r], impulse) for r in (role, pivot)]
        required = impulse.get(role, 0) - impulse[pivot]
        assert pairing == [0, 0] and required == 2
        rows.append(dict(key=[role, pivot, chart, lo, hi], support=[len(bank[role]), len(bank[pivot])],
                         evaluations=list(map(str, pairing)), required=str(required)))
    control = algebra["trace"](word, 0, [1454, PIVOT], deadline, True)
    assert [algebra["dot"](control[r], impulse) for r in (1454, PIVOT)] == [1, -2]
    assert algebra["dot"]({PIVOT: Fraction(-1)}, impulse) == 2
    alarm(0)
    result = dict(head=price["head"], caller=price["caller"], scope=CAP, raw_cuts=geometry["raw_cuts"],
                  unresolved=0, pins=PINS, rows=rows, controls=["nonzero initial coordinates", "required direction"])
    args.output.write_text(dumps(result, sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    main()
