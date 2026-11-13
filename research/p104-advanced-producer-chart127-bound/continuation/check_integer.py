"""Price and test the one pre-ADD48155 bank with public1369 advanced."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import stderr, version_info

ROOT = Path(__file__).resolve().parent.parent
PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
}
CUT, RECEIVER, ADVANCED, CHART = 48155, 1351, 1369, 127
CASE = "public1351-advanced1369-pre48155"


def emit(record):
    print(dumps(record, sort_keys=True, default=str), flush=True)


def on_cap(_signum, _frame):
    emit({"status": "CAP", "tested": 0, "unresolved": [CASE], "cap_seconds": 30})
    raise SystemExit(124)


def span(frame):
    out = {0}
    for generator in frame:
        out |= {x ^ generator for x in out}
    assert len(out) == 2 ** len(frame)
    return out


def contacts(tape, role, lo, hi):
    return [i for i in range(lo, hi) if tape[i][1] == role or
            (tape[i][0] in ("ADD", "COPY") and tape[i][2] == role)]


def evaluation(row, probe):
    return sum(value * probe.get(j, 0) for j, value in row.items())


def check_chronology(word):
    tape = word["program"]
    events = {
        36360: ["ADD", 1098, 1538, "1", 240],
        36361: ["SCALE", 1098, "-1", 240],
        36375: ["SCALE", ADVANCED, "-1", 240],
        37772: ["INIT", 1568, 240],
        37773: ["ADD", 1568, 863, "1", 240],
        38867: ["MOVE", RECEIVER, 516, 518, False],
        38868: ["ADD", RECEIVER, 1020, "-1", 518],
        39580: ["ADD", 1538, 1568, "-2", 240],
        39581: ["MOVE", 1538, 240, 518, True],
        39582: ["ADD", 1020, 1538, "1", 518],
        46186: ["MOVE", 1020, 518, 127, False],
        46187: ["ADD", 1098, 1568, "3", 240],
        46188: ["MOVE", 1098, 240, 127, False],
        46189: ["ADD", 1020, 1098, "1", 127],
        48154: ["MOVE", RECEIVER, 518, 127, False],
        CUT: ["ADD", 408, RECEIVER, "1", 127],
        52128: ["ADD", ADVANCED, 1568, "12", 240],
        52129: ["MOVE", ADVANCED, 240, 127, False],
        52131: ["ADD", ADVANCED, 524, "-2", 127],
    }
    assert all(tape[clock] == event for clock, event in events.items())
    assert contacts(tape, RECEIVER, 38867, CUT + 1) == [38867, 38868, 48154, CUT]
    assert contacts(tape, ADVANCED, 36375, 52132) == [36375, 52128, 52129, 52131]
    assert [i for i in range(37774, 52129) if tape[i][1] == 1568] == []
    frames = word["frames"]
    assert span(frames[516]) < span(frames[518]) < span(frames[127])
    assert span(frames[240]) < span(frames[127])
    assert [len(frames[j]) for j in (516, 518, 127, 240)] == [4, 8, 9, 4]


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    signal(SIGALRM, on_cap)
    alarm(30)
    data = {path: (ROOT / path).read_bytes() for path in PINS}
    assert {path: sha256(value).hexdigest() for path, value in data.items()} == PINS
    native = decompress(data["inputs/7481-WORD.json.gz"])
    assert sha256(native).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(native)
    app = loads(data["inputs/7481-APPLICATION.json"])
    caller = loads(data["inputs/7113-CALLER.json"])
    copies = caller["stages"]
    assert copies == sum(e[0] == "J" for e in caller["events"]) == 17
    assert app["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    check_chronology(word)
    power = run_path(str(ROOT / "inputs/pricing.py"))["power_bounds"]
    low, high = map(Fraction, app["directed_crossing_bracket"])
    gross = (copies * (1 + power(4, high)[0] - power(5, low)[1]),
             copies * (1 + power(4, low)[1] - power(5, high)[0]))
    assert Fraction("0.15453192223429987") <= gross[0] <= gross[1] <= Fraction("0.15453192223429988")
    print("PINNED_CHRONOLOGY_AND_PRICE", file=stderr, flush=True)

    kit = run_path(str(ROOT / "inputs/gate.py"))
    tape = word["program"]
    _, active, _ = kit["census"](word, CUT)
    assert active[ADVANCED] == 240 and active[1568] == 240
    bank = sorted(r for r, chart in active.items() if chart == CHART)
    assert {1020, 1098, 408, RECEIVER} <= set(bank)

    def read(clock, roles):
        return kit["exact_cut_rows"](tape[:clock], roles, word["public"])

    def sum_rows(*terms):
        out = {}
        for row, scalar in terms:
            for j, value in row.items():
                kit["add"](out, j, scalar * value)
        return out

    p, = read(36360, [1098])
    w, = read(37774, [1568])
    h, = read(38868, [1020])
    a, = read(39580, [1538])
    old = dict(zip([*bank, ADVANCED], read(CUT, [*bank, ADVANCED]), strict=True))
    assert old[1020] == sum_rows((h, 1), (p, -1), (w, 1))
    assert old[1098] == sum_rows((p, -1), (a, -1), (w, 3))
    donors = {role: old[role] for role in bank if role != RECEIVER}
    donors[ADVANCED] = sum_rows((old[ADVANCED], 1), (w, 12))
    own = sum_rows((old[RECEIVER], 1), (h, 1))
    roles = sorted(donors)
    print(f"EDITED_BANK_READY {len(roles) + 1}", file=stderr, flush=True)
    result = {
        "case": CASE, "tested": 1, "unresolved": [], "cap_seconds": 30, "cut": CUT,
        "pins": PINS, "gross": gross, "signed_paid_delta": {1: -17, 4: -17, 5: 17},
        "donors": roles, "advanced_role": ADVANCED,
    }
    integer_engine = ROOT / "continuation/integer_basis.py"
    assert sha256(integer_engine.read_bytes()).hexdigest() == "f7a8b29abde8b6c9f3ad3b55ecb1eba56ba2ac0211db2fac6a2ed294cd980943"
    separator = run_path(str(integer_engine))["separator"]
    edited = [*(donors[role] for role in roles), own]
    target = old[RECEIVER]
    probe, pivots = separator(edited, target)
    result["integer_pivots"] = pivots
    result["integer_engine_sha256"] = "f7a8b29abde8b6c9f3ad3b55ecb1eba56ba2ac0211db2fac6a2ed294cd980943"
    if probe is None:
        result.update(status="INCLUSION_DETECTED_EXACT_COEFFICIENTS_PENDING",
                      unresolved=[CASE])
    else:
        value = evaluation(target, probe)
        assert value and not any(evaluation(row, probe) for row in edited)
        probe = {j: scalar / value for j, scalar in probe.items()}
        assert evaluation(target, probe) == 1
        assert not any(evaluation(row, probe) for row in edited)
        result.update(status="EXACT_FIXED_ADVANCED_BANK_EXCLUSION", probe=probe,
                      donor_support=False, historical_h=evaluation(h, probe),
                      old_1351_response="1")
    emit(result)
    alarm(0)


if __name__ == "__main__":
    main()
