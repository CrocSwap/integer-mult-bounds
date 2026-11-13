"""Test a single fixed lower-chart terminal contraction of public720."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import stderr, version_info

ROOT = Path(__file__).resolve().parent.parent
CASE = "terminal720-chart265-pre41307"
CUT = 41307
PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
}


def emit(record):
    print(dumps(record, default=str, sort_keys=True), flush=True)


def on_cap(_signum, _frame):
    emit({"status": "CAP", "tested": 0, "unresolved": [CASE], "cap_seconds": 30})
    raise SystemExit(124)


def span(frame):
    space = {0}
    for g in frame:
        space |= {x ^ g for x in space}
    assert len(space) == 2 ** len(frame)
    return space


def contacts(tape, role, lo, hi):
    return [i for i in range(lo, hi) if tape[i][1] == role or
            (tape[i][0] in ("ADD", "COPY") and tape[i][2] == role)]


def value(row, probe):
    return sum(v * probe.get(j, 0) for j, v in row.items())


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    signal(SIGALRM, on_cap)
    alarm(30)
    data = {path: (ROOT / path).read_bytes() for path in PINS}
    assert {path: sha256(raw).hexdigest() for path, raw in data.items()} == PINS
    native = decompress(data["inputs/7481-WORD.json.gz"])
    assert sha256(native).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(native)
    caller = loads(data["inputs/7113-CALLER.json"])
    app = loads(data["inputs/7481-APPLICATION.json"])
    copies = caller["stages"]
    assert copies == sum(e[0] == "J" for e in caller["events"]) == 17
    assert app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    tape = word["program"]
    events = {
        32738: ["ADD", 236, 92, "1", 265],
        32750: ["MOVE", 92, 265, 1091, False],
        32940: ["ADD", 92, 1529, "1", 1091],
        33128: ["INIT", 1511, 1091],
        33129: ["ADD", 1511, 92, "1", 1091],
        40828: ["MOVE", 720, 599, 265, False],
        40829: ["ADD", 236, 720, "2", 265],
        40833: ["ADD", 454, 236, "1", 265],
        41307: ["MOVE", 236, 265, 751, False],
        45363: ["MOVE", 720, 265, 1091, False],
        45364: ["ADD", 720, 1511, "-1/4", 1091],
        45365: ["CLEAR", 1511, 1091],
    }
    assert all(tape[k] == row for k, row in events.items())
    assert contacts(tape, 720, 40829, len(tape)) == [40829, 45363, 45364]
    assert contacts(tape, 1511, 33128, 45366) == [33128, 33129, 33131, 45348, 45364, 45365]
    hosted = word["hosted"]
    protected = set(word["live"]) | {r + 112 for r in word["live"]} | set(hosted["X2"]) | set(hosted["Y2"])
    assert len(protected) == 400 and 720 not in protected
    assert word["initial"][720] == 3 and word["final"][720] == 1091
    initial, lower, upper = (span(word["frames"][c]) for c in (3, 265, 1091))
    assert initial < lower < upper and [len(initial),len(lower),len(upper)] == [1,8,16]
    power = run_path(str(ROOT / "inputs/pricing.py"))["power_bounds"]
    lo, hi = map(Fraction, app["directed_crossing_bracket"])
    gross = (17 * (1 + power(3,hi)[0] - power(4,lo)[1]),
             17 * (1 + power(3,lo)[1] - power(4,hi)[0]))
    assert Fraction("0.13900113391906015") <= gross[0] <= gross[1] <= Fraction("0.13900113391906017")
    kit = run_path(str(ROOT / "inputs/gate.py"))
    _, active, _ = kit["census"](word, CUT)
    roles = sorted(r for r,chart in active.items() if chart == 265)
    assert roles == [236,454,720,1000,1208,1347]
    read = kit["exact_cut_rows"]
    target, = read(tape[:33129], [92], word["public"])
    assert [target] == read(tape[:45364], [1511], word["public"])
    bank = read(tape[:CUT], roles, word["public"])
    assert [bank[roles.index(720)]] == read(tape[:45363], [720], word["public"])
    print("PINNED_CHRONOLOGY_PRICE_AND_BANK", file=stderr, flush=True)

    def test(allowed):
        rows = [bank[roles.index(role)] for role in allowed]
        basis = kit["basis"](rows)
        residual, coefficients = kit["representation"](basis, target)
        if not residual:
            rebuilt = {}
            for index, weight in coefficients.items():
                for j, entry in rows[index].items():
                    kit["add"](rebuilt, j, weight * entry)
            assert rebuilt == target
            return None, {allowed[i]: weight for i, weight in coefficients.items()}
        j = min(residual)
        probe = {j: 1 / residual[j]}
        for pivot, (row, _) in sorted(basis.items(), reverse=True):
            response = -value(row, probe)
            if response:
                probe[pivot] = response
        assert value(target, probe) == 1 and not any(value(row,probe) for row in rows)
        return probe, {}

    donor_roles = [r for r in roles if r != 720]
    _, pure = test(donor_roles)
    probe, coeff = test(roles)
    result = {
        "case": CASE, "cut": CUT, "cap_seconds": 30, "tested": 1, "unresolved": [],
        "pins": PINS, "bank_roles": roles, "gross": gross, "signed_paid_delta": {1:-17},
        "signed_productive_delta": {3:17,4:-17}, "pure_donor_coefficients": pure,
    }
    if probe is not None:
        result.update(status="EXACT_FIXED_LOWER_BANK_EXCLUSION", probe=probe)
    else:
        result.update(status="EXACT_RATIONAL_SUPPORT", coefficients=coeff,
                      final_self_coefficient=1 - coeff.get(720,0) / Fraction(4))
    emit(result)
    alarm(0)


if __name__ == "__main__":
    main()
