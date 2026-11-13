"""Test the historical operand for one fixed owned product return."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1] / "inputs"
CUT, HISTORICAL = 35452, 34379
ENGINE_PIN = "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9"


def cap(_signal, _frame):
    raise SystemExit(124)


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--include-retained-product", action="store_true")
    args = parser.parse_args()
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
    required_events = {
        34377: ["ADD", 1135, 1137, "-1", 431],
        HISTORICAL: ["ADD", 1535, 1137, "4", 431],
        35350: ["MOVE", 1135, 431, 243, False],
        35351: ["ADD", 798, 1135, "-1", 243],
        35352: ["ADD", 1135, 798, "1", 243],
        35353: ["ADD", 798, 1135, "-1", 243],
        35448: ["MOVE", 1545, 600, 431, True],
        35449: ["ADD", 1535, 1545, "1", 431],
        35450: ["SCALE", 1535, "1/4", 431],
        35451: ["ADD", 1544, 1535, "1", 431],
        CUT: ["MOVE", 1544, 431, 243, True],
        35453: ["ADD", 1539, 1544, "1", 243],
        35454: ["ADD", 1130, 1539, "1", 243],
    }
    assert all(tape[i] == event for i, event in required_events.items())
    frames = word["frames"]
    assert [len(frames[i]) for i in (600, 431, 243)] == [1, 3, 4]
    assert set(frames[600]) < set(frames[431]) < set(frames[243])
    _, live, _ = engine["census"](word, CUT)
    bank = sorted(role for role, chart in live.items() if chart == 243)
    assert len(bank) == 22 and {798, 1130, 1135, 1539} <= set(bank)
    assert not {1544, 1545, 1535}.intersection(bank)
    read = engine["exact_cut_rows"]
    target, = read(tape[:HISTORICAL], [1137], word["public"])
    base, = read(tape[:35448], [1545], word["public"])
    old, = read(tape[:CUT], [1544], word["public"])
    combined = target.copy()
    for coordinate, value in base.items():
        engine["add"](combined, coordinate, value / 4)
    assert old == combined
    offered = read(tape[:CUT], bank, word["public"])
    if args.include_retained_product:
        offered.append(base)
    labels = bank + (["retained_product"] if args.include_retained_product else [])
    pivots = engine["basis"](offered)
    residual, coefficients = engine["representation"](pivots, target)
    witness, target_value = {}, 0
    if residual:
        def separate(j):
            probe = {j: Q(1)}
            for pivot, (row, _) in sorted(pivots.items(), reverse=True):
                value = -sum(v * probe.get(k, 0) for k, v in row.items() if k != pivot)
                if value:
                    probe[pivot] = value
            return probe
        witness = min(map(separate, residual), key=lambda p: (len(p), max(p)))
        assert all(sum(v*witness.get(k,0) for k,v in row.items()) == 0 for row in offered)
        target_value = sum(v*witness.get(k,0) for k,v in target.items())
        assert target_value
    app = loads(data["7481-APPLICATION.json"])
    assert app["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    lo, hi = map(Q, app["directed_crossing_bracket"])
    h = run_path(str(ROOT / "pricing.py"))["power_bounds"]
    gross = [17*(1+h(2,hi)[0]-h(3,lo)[1]), 17*(1+h(2,lo)[1]-h(3,hi)[0])]
    assert 0 < gross[0] <= gross[1] < 17
    print(dumps({"status": "BANK_EXCLUDES_HISTORICAL_OPERAND" if residual else "SUPPORT_PASSES",
                 "case_cap": 1, "runner_cap_seconds": 30, "cut": CUT, "historical_read": HISTORICAL,
                 "bank": bank, "bank_rank": len(pivots), "residual": residual, "witness": witness,
                 "granted_retained_product": args.include_retained_product,
                 "target_value": target_value,
                 "old1545_at_witness": sum(v*witness.get(k,0) for k,v in base.items()),
                 "combination": {labels[i]: v for i,v in coefficients.items()},
                 "gross_exact": gross, "gross_display": list(map(float,gross)), "pins": engine["PINS"]},
                indent=2, sort_keys=True, default=str))
    alarm(0)


if __name__ == "__main__":
    main()
