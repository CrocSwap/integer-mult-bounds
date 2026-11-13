"""Test two required quotient directions for the single proposed 728 lift."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import stderr, version_info

ROOT = Path(__file__).resolve().parent.parent
CASE = "lift728-owned1537-chart127-pre49170"
OWNER, CARRIER, RECIPIENT, ADVANCED = 1537, 728, 1004, 1397
SOURCE, CUT = 41491, 49170
PINS = {
    "inputs/7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
    "next-lift728/integer_basis.py": "f7a8b29abde8b6c9f3ad3b55ecb1eba56ba2ac0211db2fac6a2ed294cd980943",
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
    assert word["initial"][CARRIER] == 3 and word["final"][CARRIER] == 1090
    hosted = word["hosted"]
    protected = set(word["live"]) | {r + 112 for r in word["live"]} | set(hosted["X2"]) | set(hosted["Y2"])
    assert len(protected) == 400 and CARRIER not in protected
    assert tape[30631][:3] == ["ADD", OWNER, CARRIER]
    assert contacts(tape, CARRIER, 30631, len(tape)) == [30631]
    events = {
        35119: ["ADD", ADVANCED, 1162, "-1", 1090],
        SOURCE: ["MOVE", OWNER, 1090, 477, True],
        41492: ["ADD", RECIPIENT, OWNER, "1", 477],
        41495: ["CLEAR", OWNER, 477],
        46133: ["MOVE", RECIPIENT, 477, 127, False],
        46135: ["ADD", RECIPIENT, 813, "1", 127],
        46209: ["ADD", RECIPIENT, 1162, "-1", 127],
        CUT: ["SCALE", RECIPIENT, "4", 127],
        51411: ["MOVE", ADVANCED, 1090, 127, False],
        51412: ["ADD", 787, ADVANCED, "-2", 127],
        54998: ["ADD", 830, RECIPIENT, "1/2", 127],
    }
    assert all(tape[i] == e for i, e in events.items())
    assert contacts(tape, RECIPIENT, 41492, CUT + 1) == [41492, 46133, 46135, 46209, CUT]
    assert contacts(tape, OWNER, SOURCE, 41496) == [SOURCE, 41492, 41495]
    assert contacts(tape, ADVANCED, 35119, 51413) == [35119, 51411, 51412]
    frames = [span(word["frames"][chart]) for chart in (3, 1090, 477, 127)]
    assert [len(frame) for frame in frames] == [1, 16, 256, 512]
    assert all(a < b for a, b in zip(frames, frames[1:]))
    power = run_path(str(ROOT / "inputs/pricing.py"))["power_bounds"]
    low, high = map(Fraction, app["directed_crossing_bracket"])
    gross = (copies * (power(9, high)[0] - power(5, low)[1]),
             copies * (power(9, low)[1] - power(5, high)[0]))
    assert Fraction("67.27630796481413") <= gross[0] <= gross[1] <= Fraction("67.27630796481414")
    print("PINNED_CHRONOLOGY_AND_PRICE", file=stderr, flush=True)

    kit = run_path(str(ROOT / "inputs/gate.py"))
    _, source_live, _ = kit["census"](word, SOURCE)
    _, live, _ = kit["census"](word, CUT)
    assert source_live[OWNER] == source_live[CARRIER] == 1090
    assert live[RECIPIENT] == 127 and live[ADVANCED] == live[CARRIER] == 1090
    roles = sorted([r for r, chart in live.items() if chart == 127 and r != RECIPIENT] + [ADVANCED])
    assert len(roles) == len(set(roles)) and CARRIER not in roles and OWNER not in live
    read = kit["exact_cut_rows"]
    e, t = read(tape[:SOURCE], [CARRIER, OWNER], word["public"])
    assert e == {CARRIER: Fraction(1)}
    bank = read(tape[:CUT], roles, word["public"])
    print(f"BANK_READY {len(bank)}", file=stderr, flush=True)
    separate = run_path(str(ROOT / "next-lift728/integer_basis.py"))["separator"]
    p, rank = separate(bank, t)
    result = {
        "case": CASE, "cut": CUT, "cap_seconds": 30, "pins": PINS, "bank_roles": roles,
        "gross": gross, "signed_paid_delta": {4: -17, 5: 17},
        "signed_productive_delta": {4: -17, 9: 17},
    }
    if p is None:
        result.update(status="T_INCLUSION_COEFFICIENTS_PENDING", unresolved=[CASE])
    else:
        assert all(not value(row, p) for row in bank) and value(t, p)
        print(f"FIRST_DIRECTION_SEPARATED {rank}", file=stderr, flush=True)
        q, augmented_rank = separate([*bank, t], e)
        if q is None:
            result.update(status="RANK_ONE_RELATION_COEFFICIENTS_PENDING", unresolved=[CASE])
        else:
            assert all(not value(row, q) for row in bank) and not value(t, q)
            minor = [[value(e, probe), value(t, probe)] for probe in (p, q)]
            determinant = minor[0][0] * minor[1][1] - minor[0][1] * minor[1][0]
            assert determinant
            result.update(status="EXACT_TWO_DIRECTION_QUOTIENT_EXCLUSION", unresolved=[],
                          bank_rank=rank, augmented_rank=augmented_rank, probes=[p, q],
                          minor=minor, determinant=determinant)
    emit(result)
    alarm(0)


if __name__ == "__main__":
    main()
