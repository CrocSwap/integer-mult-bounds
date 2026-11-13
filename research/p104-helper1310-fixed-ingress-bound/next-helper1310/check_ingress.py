"""Test the historical ingress sum against the fixed chart-1051 bank."""
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
ROLE, CUT, CHART = 1310, 38219, 1051
CASE = "role1310-chart1051-pre38219"


def emit(result):
    print(dumps(result, sort_keys=True, default=str), flush=True)


def capped(_signum, _frame):
    emit({"status": "CAP", "tested": 0, "unresolved": [CASE], "cap_seconds": 30})
    raise SystemExit(124)


def span(frame):
    result = {0}
    for generator in frame:
        result |= {v ^ generator for v in result}
    assert len(result) == 2 ** len(frame)
    return result


def evaluate(row, probe):
    return sum(value * probe.get(j, 0) for j, value in row.items())


def mentions(event, role):
    return event[1] == role or (event[0] in ("ADD", "COPY") and event[2] == role)


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    signal(SIGALRM, capped)
    alarm(30)
    data = {path: (ROOT / path).read_bytes() for path in PINS}
    assert {path: sha256(value).hexdigest() for path, value in data.items()} == PINS
    raw = decompress(data["inputs/7481-WORD.json.gz"])
    assert sha256(raw).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(raw)
    app = loads(data["inputs/7481-APPLICATION.json"])
    caller = loads(data["inputs/7113-CALLER.json"])
    copies = caller["stages"]
    assert copies == sum(event[0] == "J" for event in caller["events"]) == 17
    assert word["initial"][ROLE] == 3 and word["final"][ROLE] == 127
    initial, split, final = [span(word["frames"][chart]) for chart in (3, CHART, 127)]
    assert initial < split < final and len(split) == 32 * len(initial) and len(final) == 16 * len(split)
    tape = word["program"]
    assert tape[35424] == ["ADD", ROLE, 890, "1", 3]
    assert tape[35425] == ["ADD", ROLE, 943, "1", 3]
    assert tape[38217:38219] == [["MOVE", ROLE, 3, CHART, False], ["MOVE", 1311, 3, CHART, False]]
    assert [i for i in range(CUT) if mentions(tape[i], ROLE)] == [35424, 35425, 38217]
    assert tape[CUT][0:2] == ["ADD", ROLE] and tape[CUT][-1] == CHART
    assert tape[CUT + 1][0:3] == ["ADD", 1312, ROLE] and tape[CUT + 1][-1] == CHART

    power = run_path(str(ROOT / "inputs/pricing.py"))["power_bounds"]
    low, high = map(Fraction, app["directed_crossing_bracket"])
    gross_lower = copies * (power(4, high)[0] + power(5, high)[0] - power(9, low)[1])
    gross_upper = copies * (power(4, low)[1] + power(5, low)[1] - power(9, high)[0])
    assert 0 < gross_lower <= gross_upper < copies
    exact = run_path(str(ROOT / "inputs/gate.py"))
    _, active, _ = exact["census"](word, CUT)
    bank = sorted(r for r, chart in active.items() if chart == CHART and r != ROLE)
    assert active[ROLE] == CHART and 1311 in bank
    read = exact["exact_cut_rows"]
    donors = [read(tape[:clock], [role], word["public"])[0] for clock, role in ((35424, 890), (35425, 943))]
    ingress = donors[0].copy()
    for j, coefficient in donors[1].items():
        exact["add"](ingress, j, coefficient)
    assert ROLE not in ingress
    old, *rows = read(tape[:CUT], [ROLE, *bank], word["public"])
    assert old == {ROLE: Fraction(1), **ingress}
    pivots = exact["basis"](rows)
    residual, coefficients = exact["representation"](pivots, ingress)
    result = {
        "case": CASE, "status": "EXACT_RATIONAL_SUPPORT", "tested": 1, "unresolved": [],
        "cap_seconds": 30, "cut": CUT, "chart": CHART, "bank": bank,
        "bank_rank": len(pivots), "pins": PINS, "gross_interval": [gross_lower, gross_upper],
        "signed_productive_delta": {4: copies, 5: copies, 9: -copies},
    }
    if residual:
        coordinate = min(residual)
        assert coordinate not in pivots
        probe = {coordinate: 1 / residual[coordinate]}
        for pivot, (vector, _) in sorted(pivots.items(), reverse=True):
            value = -evaluate(vector, probe)
            if value:
                probe[pivot] = value
        assert evaluate(ingress, probe) == 1
        assert all(evaluate(row, probe) == 0 for row in rows)
        result.update(status="EXACT_FIXED_INGRESS_EXCLUSION", probe=probe,
                      historical_donor_responses=[evaluate(row, probe) for row in donors])
    else:
        restored = {}
        for index, scalar in coefficients.items():
            for j, coefficient in rows[index].items():
                exact["add"](restored, j, scalar * coefficient)
        assert restored == ingress
        result["representation"] = {bank[index]: scalar for index, scalar in coefficients.items()}
    emit(result)
    alarm(0)


if __name__ == "__main__":
    main()
