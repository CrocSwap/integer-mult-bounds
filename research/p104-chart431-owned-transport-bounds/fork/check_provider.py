"""Check the fixed surviving observer bank of one owned provider fork."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1] / "inputs"
SOURCE, READ = 34527, 34568
BANK = (375, 1135, 1137, 1348, 1535)
ENGINE_PIN = "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9"


def cap(_signal, _frame):
    raise SystemExit(124)


def main():
    assert __debug__
    signal(SIGALRM, cap)
    alarm(30)
    helper = ROOT / "gate.py"
    assert sha256(helper.read_bytes()).hexdigest() == ENGINE_PIN
    engine = run_path(str(helper))
    data = {name: (ROOT / name).read_bytes() for name in engine["PINS"]}
    assert {name: sha256(blob).hexdigest() for name, blob in data.items()} == engine["PINS"]
    raw = decompress(data["7481-WORD.json.gz"])
    assert sha256(raw).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(raw)
    tape = word["program"]
    expected = {34527: ["ADD", 1518, 1513, "1", 243],
                34528: ["MOVE", 1518, 243, 431, True],
                34529: ["ADD", 1507, 1518, "1", 431],
                34530: ["SCALE", 1507, "1/4", 431],
                34532: ["ADD", 1519, 1507, "1", 431],
                34566: ["MOVE", 1348, 3, 431, False],
                34567: ["ADD", 1348, 1137, "4", 431],
                34568: ["ADD", 375, 1507, "-4", 431],
                35443: ["MOVE", 1519, 431, 600, True]}
    assert all(tape[i] == event for i, event in expected.items())
    frames = word["frames"]
    assert [len(frames[x]) for x in (243, 431, 600)] == [4, 3, 1]
    assert set(frames[600]) < set(frames[431]) < set(frames[243])
    _, live, _ = engine["census"](word, READ)
    old_bank = {role for role, chart in live.items() if chart == 431}
    assert old_bank == set(BANK) | {1507, 1518, 1519}
    rows = engine["exact_cut_rows"]
    target, = rows(tape[:SOURCE], [1513], word["public"])
    old_signal, = rows(tape[:READ], [1507], word["public"])
    assert target == {k: 4*v for k, v in old_signal.items()}
    offered = rows(tape[:READ], BANK, word["public"])
    pivots = engine["basis"](offered)
    residual, coefficient = engine["representation"](pivots, target)
    witness = {}
    response = Q(0)
    if residual:
        def separate(j):
            probe = {j: Q(1)}
            for pivot, (row, _) in sorted(pivots.items(), reverse=True):
                value = -sum(v * probe.get(k, 0) for k, v in row.items() if k != pivot)
                if value:
                    probe[pivot] = value
            return probe
        witness = min(map(separate, residual), key=lambda p: (len(p), max(p)))
        assert all(sum(v*witness.get(k, 0) for k, v in row.items()) == 0 for row in offered)
        response = sum(v*witness.get(k, 0) for k, v in target.items())
        assert response
    app = loads(data["7481-APPLICATION.json"])
    lo, hi = map(Q, app["directed_crossing_bracket"])
    h = run_path(str(ROOT / "pricing.py"))["power_bounds"]
    gross = [17*(1+h(2,hi)[0]-h(3,lo)[1]), 17*(1+h(2,lo)[1]-h(3,hi)[0])]
    assert 0 < gross[0] <= gross[1] < 17
    print(dumps({"status": "FIXED_OBSERVER_BANK_EXCLUDED" if residual else "SUPPORT_PASSES",
                 "case_count": 1, "seconds_cap": 30, "old_bank": sorted(old_bank),
                 "surviving_bank": BANK, "bank_rank": len(pivots),
                 "read": READ, "old_source": SOURCE, "residual": residual,
                 "combination": {BANK[i]: v for i,v in coefficient.items()},
                 "witness": witness, "old_u_response": response,
                 "needed_outward_response": -response, "gross": gross,
                 "gross_decimal_display": list(map(float,gross)), "pins": engine["PINS"]},
                indent=2, sort_keys=True, default=str))
    alarm(0)


if __name__ == "__main__":
    main()
