"""One exact support gate for the four named paid returns before SCALE49170."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import version_info

ROOT = Path(__file__).resolve().parent.parent
PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
}
CASE = "owned1537-four-returns-pre49170"
SOURCE, CUT = 41491, 49170
ROLES = (813, 1162, 1448, 1397)


def emit(record):
    print(dumps(record, sort_keys=True, default=str), flush=True)


def on_cap(_signum, _frame):
    emit({"status": "CAP", "tested": 0, "unresolved": [CASE], "cap_seconds": 30})
    raise SystemExit(124)


def span(frame):
    values = {0}
    for generator in frame:
        values |= {value ^ generator for value in values}
    assert len(values) == 2 ** len(frame)
    return values


def contacts(tape, role, lo, hi):
    return [i for i in range(lo, hi) if tape[i][1] == role or
            (tape[i][0] in ("ADD", "COPY") and tape[i][2] == role)]


def value(row, probe):
    return sum(coefficient * probe.get(i, 0) for i, coefficient in row.items())


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    signal(SIGALRM, on_cap)
    alarm(30)
    raw = {path: (ROOT / path).read_bytes() for path in PINS}
    assert {path: sha256(data).hexdigest() for path, data in raw.items()} == PINS
    decoded = decompress(raw["inputs/7481-WORD.json.gz"])
    assert sha256(decoded).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(decoded)
    caller = loads(raw["inputs/7113-CALLER.json"])
    app = loads(raw["inputs/7481-APPLICATION.json"])
    assert caller["stages"] == sum(e[0] == "J" for e in caller["events"]) == 17
    assert app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    tape = word["program"]
    events = {
        35119: ["ADD", 1397, 1162, "-1", 1090],
        SOURCE: ["MOVE", 1537, 1090, 477, True],
        41492: ["ADD", 1004, 1537, "1", 477],
        41495: ["CLEAR", 1537, 477],
        46133: ["MOVE", 1004, 477, 127, False],
        46134: ["MOVE", 813, 1090, 127, False],
        46135: ["ADD", 1004, 813, "1", 127],
        46208: ["MOVE", 1162, 1090, 127, False],
        46209: ["ADD", 1004, 1162, "-1", 127],
        46676: ["MOVE", 1448, 1090, 127, False],
        CUT: ["SCALE", 1004, "4", 127],
        49594: ["ADD", 1004, 1144, "-8", 127],
        49721: ["ADD", 1004, 502, "-4", 127],
        51411: ["MOVE", 1397, 1090, 127, False],
        51412: ["ADD", 787, 1397, "-2", 127],
        54998: ["ADD", 830, 1004, "1/2", 127],
    }
    assert all(tape[clock] == e for clock, e in events.items())
    assert contacts(tape, 1537, SOURCE, 41496) == [SOURCE, 41492, 41495]
    assert contacts(tape, 1004, 41492, 54999) == [41492, 46133, 46135, 46209, CUT, 49594, 49721, 54998]
    assert contacts(tape, 1397, 35119, 51413) == [35119, 51411, 51412]
    frames = [span(word["frames"][chart]) for chart in (1090, 477, 127)]
    assert frames[0] < frames[1] < frames[2] and [len(frame) for frame in frames] == [16, 256, 512]
    kit = run_path(str(ROOT / "inputs/gate.py"))
    _, source_live, _ = kit["census"](word, SOURCE)
    _, cut_live, _ = kit["census"](word, CUT)
    assert source_live[1537] == 1090 and 1537 >= word["public"]
    assert 1537 not in cut_live and cut_live[1004] == 127
    assert [cut_live[r] for r in ROLES] == [127, 127, 127, 1090]
    assert all(r < word["public"] for r in ROLES)
    power = run_path(str(ROOT / "inputs/pricing.py"))["power_bounds"]
    low, high = map(Fraction, app["directed_crossing_bracket"])
    gross = (17 * power(4, high)[0], 17 * power(4, low)[1])
    assert Fraction("67.65706456310804") <= gross[0] <= gross[1] <= Fraction("67.65706456310805")
    read = kit["exact_cut_rows"]
    target, = read(tape[:SOURCE], [1537], word["public"])
    rows = read(tape[:CUT], ROLES, word["public"])
    pivots = kit["basis"](rows)
    residual, coeff = kit["representation"](pivots, target)
    result = {
        "case": CASE, "tested": 1, "unresolved": [], "cap_seconds": 30,
        "cut": CUT, "donors": ROLES, "rank": len(pivots), "pins": PINS,
        "signed_paid_delta": {4: -17}, "gross": gross,
    }
    if residual:
        coordinate = min(residual)
        assert coordinate not in pivots
        probe = {coordinate: 1 / residual[coordinate]}
        for pivot, (row, _) in sorted(pivots.items(), reverse=True):
            response = -value(row, probe)
            if response:
                probe[pivot] = response
        assert value(target, probe) == 1 and not any(value(row, probe) for row in rows)
        result.update(status="EXACT_NAMED_FOUR_RETURNS_EXCLUSION", probe=probe)
    else:
        rebuilt = {}
        for index, coefficient in coeff.items():
            for j, x in rows[index].items():
                kit["add"](rebuilt, j, x * coefficient)
        assert rebuilt == target
        result.update(status="EXACT_RATIONAL_SUPPORT", coefficients={ROLES[j]: x for j, x in coeff.items()})
    emit(result)
    alarm(0)


if __name__ == "__main__":
    main()
