"""Exact necessary support for a one-direction replacement of the owned exchange."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import argv

PINS = {
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
}
LEFT = (111, 121, 173, 235, 752, 881, 891, 937, 999, 1501, 1522, 1549)
RIGHT = ((40536, 1527), (40536, 613), (40546, 611), (40548, 1279))
MOVES = {
    40536: ["MOVE", 613, 558, 559, False],
    40538: ["MOVE", 1549, 549, 559, True],
    40546: ["MOVE", 611, 556, 559, False],
    40548: ["MOVE", 1279, 560, 559, False],
    40556: ["MOVE", 1527, 559, 549, True],
}


def cap(_signum, _frame):
    print('{"status":"UNRESOLVED_CAP","window":[40536,40558]}', flush=True)
    raise SystemExit(124)


def response(row, probe):
    return sum(row.get(i, 0) * value for i, value in probe.items())


def check_direction(engine, rows, target):
    pivots = engine["basis"](rows)
    remainder, coefficients = engine["representation"](pivots, target)
    probe = {}
    if remainder:
        free = min(remainder)
        probe[free] = Q(1)
        for pivot, (row, _) in sorted(pivots.items(), reverse=True):
            value = -sum(a * probe.get(k, 0) for k, a in row.items() if k != pivot)
            if value:
                probe[pivot] = value
        assert not any(response(row, probe) for row in rows)
        assert response(target, probe) == remainder[free] != 0
    return len(pivots), probe, coefficients if not remainder else {}


def main():
    assert __debug__
    signal(SIGALRM, cap)
    alarm(30)
    root = Path(argv[1])
    raw = {name: (root / name).read_bytes() for name in PINS}
    assert {name: sha256(data).hexdigest() for name, data in raw.items()} == PINS
    data = decompress(raw["7481-WORD.json.gz"])
    assert sha256(data).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(data)
    tape, frames = word["program"], word["frames"]
    assert {i: e for i, e in enumerate(tape[40536:40558], 40536)
            if e[0] == "MOVE" and set(e[2:4]) & {549, 559}} == MOVES
    assert len(frames[559]) - len(frames[549]) == 1
    assert tape[40539] == ["ADD", 613, 1549, "1", 559]
    assert tape[40557] == ["ADD", 173, 1527, "1", 549]
    caller = loads(raw["7113-CALLER.json"])
    assert caller["stages"] == sum(e[0] == "J" for e in caller["events"]) == 17
    app = loads(raw["7481-APPLICATION.json"])
    assert app["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    engine = run_path(str(root / "gate.py"))
    _, active, _ = engine["census"](word, 40536)
    assert tuple(sorted(i for i, c in active.items() if c == 549)) == LEFT
    assert [i for i, c in active.items() if c == 559] == [1527]
    read, public = engine["exact_cut_rows"], word["public"]
    left = read(tape[:40536], LEFT, public)
    right = [read(tape[:clock], [role], public)[0] for clock, role in RIGHT]
    result = []
    for name, rows, cut, role in (("L_TO_R", left, 40558, 173), ("R_TO_L", right, 40540, 613)):
        target, = read(tape[:cut], [role], public)
        rank, probe, combination = check_direction(engine, rows, target)
        result.append({"retained_direction": name, "offered_rank": rank, "target_role": role,
                       "target_cut": cut, "probe": probe, "combination": combination,
                       "target_response": response(target, probe) if probe else None})
    print(dumps({"status": "EXACT_ONE_DIRECTION_EXCLUSION" if all(r["probe"] for r in result)
                 else "NECESSARY_GATE_SURVIVES", "directions": result,
                 "source_left_roles": LEFT, "source_right_rows": RIGHT, "pins": PINS,
                 "gross_raw": 17, "productive_delta": {}, "runner_cap_seconds": 30,
                 "window": [40536, 40558], "unresolved": []}, sort_keys=True, indent=2, default=str))
    alarm(0)


if __name__ == "__main__":
    main()
