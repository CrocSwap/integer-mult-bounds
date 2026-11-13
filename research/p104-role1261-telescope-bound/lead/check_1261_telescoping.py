"""One chart246 support test for the historical increment on #7481 helper1261."""
import gzip
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
from runpy import run_path
import signal
import sys

PINS = {
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
}
CASE = "1261-telescoped-1191-chart246-pre39469"
CUT = 39469
BANK = [1145, 1192, 1261, 1443, 1485, 1486, 1487]
EVENTS = {
    38490: ["MOVE", 1261, 3, 509, False],
    38491: ["ADD", 1191, 1261, "-1", 509],
    38492: ["MOVE", 1191, 509, 771, False],
    38494: ["ADD", 1191, 1050, "1/2", 771],
    38536: ["MOVE", 1191, 771, 925, False],
    38538: ["ADD", 1191, 964, "1/2", 925],
    38876: ["MOVE", 1191, 925, 246, False],
    38878: ["ADD", 1191, 1192, "1/2", 246],
    39433: ["MOVE", 1261, 509, 770, False],
    39434: ["MOVE", 1145, 576, 770, False],
    39435: ["ADD", 1261, 1145, "1/2", 770],
    39436: ["MOVE", 1261, 770, 903, False],
    39438: ["ADD", 1261, 910, "1/2", 903],
    39439: ["MOVE", 1145, 770, 901, False],
    39441: ["ADD", 1145, 953, "-1", 901],
    39465: ["ADD", 910, 894, "-1", 903],
    39466: ["MOVE", 1261, 903, 246, False],
    39467: ["MOVE", 1145, 901, 246, False],
    39468: ["ADD", 1261, 1145, "-1/2", 246],
    39469: ["ADD", 1191, 1261, "1", 246],
}


def output(result):
    print(json.dumps(result, default=str, sort_keys=True), flush=True)


def capped(_signal, _frame):
    output(dict(status="UNRESOLVED_CAP", case=CASE, unresolved=[CASE], cap_seconds=30))
    raise SystemExit(124)


def touches(event, role):
    return role in (event[1:3] if event[0] in ("ADD", "COPY") else event[1:2])


def xor_span(frame):
    values = {0}
    for row in frame:
        assert row not in values
        values |= {row ^ value for value in values}
    return values


def evaluate(row, probe):
    return sum(value * probe.get(j, 0) for j, value in row.items())


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    signal.signal(signal.SIGALRM, capped)
    signal.alarm(30)
    root = Path(sys.argv[1]).resolve()
    pins = {name: (root / name).read_bytes() for name in PINS}
    assert {name: hashlib.sha256(data).hexdigest() for name, data in pins.items()} == PINS
    raw = gzip.decompress(pins["7481-WORD.json.gz"])
    app = json.loads(pins["7481-APPLICATION.json"])
    assert hashlib.sha256(raw).hexdigest() == app["candidate_canonical_sha256"]
    word = json.loads(raw)
    caller = json.loads(pins["7113-CALLER.json"])
    assert caller["stages"] == sum(e[0] == "J" for e in caller["events"]) == 17
    tape, public = word["program"], word["public"]
    assert all(tape[i] == event for i, event in EVENTS.items())
    assert [i for i in range(38490, 39434) if touches(tape[i], 1261)] == [38490, 38491, 39433]
    assert [i for i in range(38491, CUT+1) if touches(tape[i], 1191)] == [
        38491, 38492, 38494, 38536, 38538, 38876, 38878, 39469]
    assert [i for i in range(39433, CUT) if touches(tape[i], 1261)] == [
        39433, 39435, 39436, 39438, 39466, 39468]
    assert [i for i in range(39435, 39469) if touches(tape[i], 1145)] == [
        39435, 39439, 39441, 39467, 39468]
    assert xor_span(word["frames"][3]) < xor_span(word["frames"][509]) < xor_span(word["frames"][770])
    assert [len(word["frames"][c]) for c in (3, 509, 770)] == [0, 3, 6]
    protected = (set(word["live"]) | {r+112 for r in word["live"]} |
                 set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))
    assert len(protected) == 400 and 1191 not in protected and 1261 not in protected and 964 in protected
    kit = run_path(str(root / "gate.py"))
    _, active, _ = kit["census"](word, CUT)
    assert active[1191] == 246
    assert sorted(r for r, frame in active.items() if frame == 246 and r != 1191) == BANK
    read = kit["exact_cut_rows"]
    before, = read(tape[:38491], [1261], public)
    after, = read(tape[:CUT], [1261], public)
    target = {}
    for clock, role in ((39438, 910), (39441, 953)):
        row, = read(tape[:clock], [role], public)
        for j, val in row.items():
            kit["add"](target, j, val / 2)
    telescoped = after.copy()
    for j, val in before.items():
        kit["add"](telescoped, j, -val)
    assert target == telescoped
    bank = read(tape[:CUT], BANK, public)
    pivots = kit["basis"](bank)
    residual, coeff = kit["representation"](pivots, target)
    power = run_path(str(root / "pricing.py"))["power_bounds"]
    lo, hi = map(Q, app["directed_crossing_bracket"])
    gross = [17*(2*power(3, hi)[0]-power(6, lo)[1]),
             17*(2*power(3, lo)[1]-power(6, hi)[0])]
    assert 0 < gross[0] <= gross[1] < 17
    result = dict(case=CASE, cut=CUT, bank=BANK, bank_rank=len(pivots), target=target, gross=gross,
                  fixed_self_coefficient=1, signed_paid_delta={3: -34, 6: 17}, signed_productive_delta={},
                  tested=1, cap_seconds=30, unresolved=[])
    if residual:
        coordinate = min(residual)
        assert coordinate not in pivots
        probe = {coordinate: 1 / residual[coordinate]}
        for pivot, (vector, _) in sorted(pivots.items(), reverse=True):
            value = -evaluate(vector, probe)
            if value:
                probe[pivot] = value
        assert evaluate(target, probe) == 1 and all(not evaluate(row, probe) for row in bank)
        result.update(status="EXACT_FIXED_DONOR_EXCLUSION", probe=probe)
    else:
        rebuilt = {}
        for row, scalar in coeff.items():
            for j, val in bank[row].items():
                kit["add"](rebuilt, j, scalar * val)
        assert rebuilt == target
        result.update(status="EXACT_RATIONAL_SUPPORT_REQUIRES_FULL_PRICE",
                      representation={BANK[r]: c for r, c in coeff.items()})
    output(result)
    signal.alarm(0)


if __name__ == "__main__":
    main()
