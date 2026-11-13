"""One exact changed-arrival support gate on #7481 owned1548."""
import gzip
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

PINS = {
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "gate.py": "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9",
}
CASE = "owned1548-two-receivers-advanced-913-1298-pre46664"
CUT = 46664
DONORS = [913, 1197, 587, 1494]
EVENTS = {
    39769: ["ADD", 1548, 913, "-1", 529],
    39777: ["ADD", 927, 913, "-1", 529],
    39778: ["ADD", 1548, 927, "-1/2", 529],
    39779: ["MOVE", 1197, 524, 529, False],
    39780: ["ADD", 1197, 913, "-1", 529],
    39781: ["ADD", 1197, 927, "-1", 529],
    39782: ["SCALE", 927, "-1/2", 529],
    39785: ["MOVE", 1548, 529, 531, True],
    39786: ["ADD", 1298, 1548, "-1/2", 531],
    39787: ["ADD", 1429, 1548, "-1/2", 531],
    39788: ["CLEAR", 1548, 531],
    45418: ["MOVE", 1197, 529, 127, False],
    45419: ["ADD", 1197, 587, "1", 127],
    45583: ["ADD", 1494, 913, "1/2", 529],
    46663: ["MOVE", 1429, 531, 127, False],
    46664: ["ADD", 1153, 1429, "1", 127],
    47227: ["MOVE", 913, 529, 127, False],
    47722: ["MOVE", 1298, 531, 127, False],
    47723: ["ADD", 665, 1298, "1", 127],
}


def emit(result):
    print(json.dumps(result, sort_keys=True, default=str), flush=True)


def cap(_sig, _frame):
    emit(dict(case=CASE, status="UNRESOLVED_CAP", unresolved=[CASE], cap_seconds=30))
    raise SystemExit(124)


def touches(event, role):
    return role in (event[1:3] if event[0] in ("ADD", "COPY") else event[1:2])


def contacts(tape, role, first, end):
    return [i for i in range(first, end) if touches(tape[i], role)]


def evaluate(row, probe):
    return sum(value*probe.get(i, 0) for i, value in row.items())


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    signal.signal(signal.SIGALRM, cap)
    signal.alarm(30)
    root = Path(sys.argv[1]).resolve()
    raw = {name: (root / name).read_bytes() for name in PINS}
    assert {name: sha256(data).hexdigest() for name, data in raw.items()} == PINS
    app = json.loads(raw["7481-APPLICATION.json"])
    word_raw = gzip.decompress(raw["7481-WORD.json.gz"])
    assert sha256(word_raw).hexdigest() == app["candidate_canonical_sha256"]
    word = json.loads(word_raw)
    caller = json.loads(raw["7113-CALLER.json"])
    assert caller["stages"] == sum(e[0] == "J" for e in caller["events"]) == 17
    tape, public = word["program"], word["public"]
    assert all(tape[i] == event for i, event in EVENTS.items())
    assert contacts(tape, 1548, 39769, 39789) == [39769,39778,39785,39786,39787,39788]
    assert contacts(tape, 913, 45584, 47227) == []
    assert contacts(tape, 1298, 39787, 47722) == []
    assert contacts(tape, 1429, 39788, CUT) == [46663]
    assert contacts(tape, 1197, 39782, CUT) == [45418,45419]
    protected = (set(word["live"]) | {r+112 for r in word["live"]} |
                 set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"]))
    assert len(protected) == 400 and 927 in protected
    assert not {913,1197,1298,1429} & protected
    kit = run_path(str(root / "gate.py"))
    _, active, _ = kit["census"](word, CUT)
    assert {r: active[r] for r in (913,1197,587,1494,1298,1429)} == {
        913:529, 1197:127, 587:127, 1494:127, 1298:531, 1429:127}
    assert 1548 not in active
    read = kit["exact_cut_rows"]
    u, = read(tape[:39785], [1548], public)
    historical913, = read(tape[:39769], [913], public)
    historical927, = read(tape[:39778], [927], public)
    expected = {}
    for row, coefficient in ((historical913, -1), (historical927, Q(-1, 2))):
        for i, value in row.items():
            kit["add"](expected, i, coefficient*value)
    assert u == expected
    old1197, = read(tape[:39780], [1197], public)
    new1197, = read(tape[:39782], [1197], public)
    relation = {}
    for row, coefficient in ((new1197, Q(1, 2)), (old1197, Q(-1, 2)), (historical913, Q(-1, 2))):
        for i, value in row.items():
            kit["add"](relation, i, coefficient*value)
    assert relation == u
    needed = {i: -value/2 for i, value in u.items()}
    # The two changed MOVE clocks do not change normalized donor values.
    bank = read(tape[:CUT], DONORS, public)
    pivots = kit["basis"](bank)
    residual, weights = kit["representation"](pivots, needed)
    result = dict(case=CASE, cut=CUT, tested=1, cap_seconds=30, donors=DONORS,
                  donor_rank=len(pivots), required_each=needed, recipients=[1298,1429],
                  advanced_moves={47227:913,47722:1298}, signed_paid_delta={1:-17},
                  signed_productive_delta={}, gross_raw=17, unresolved=[])
    if residual:
        first = min(residual)
        assert first not in pivots
        probe = {first: 1/residual[first]}
        for pivot, (row, _) in sorted(pivots.items(), reverse=True):
            value = -evaluate(row, probe)
            if value:
                probe[pivot] = value
        assert evaluate(needed, probe) == 1 and not any(evaluate(row, probe) for row in bank)
        result.update(status="EXACT_NAMED_DONOR_EXCLUSION", probe=probe)
    else:
        reconstructed = {}
        for j, coefficient in weights.items():
            for i, value in bank[j].items():
                kit["add"](reconstructed, i, coefficient*value)
        assert reconstructed == needed
        result.update(status="EXACT_RATIONAL_SUPPORT_FULL_PRICE_PENDING",
                      representation={DONORS[j]: coefficient for j, coefficient in weights.items()})
    emit(result)
    signal.alarm(0)


if __name__ == "__main__":
    main()
