"""Check the exact prefix contrasts for one productive three-cycle."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1] / "inputs"
ENGINE_SHA = "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9"
CUT, CHART = 36481, 1049
BANK = (1322, 1352, 1440)


def cap(_signal, _frame):
    raise SystemExit(124)


def span(frame):
    space = {0}
    for vector in frame:
        space |= {value ^ vector for value in space}
    return space


def main():
    assert __debug__
    signal(SIGALRM, cap)
    alarm(30)
    path = ROOT / "gate.py"
    assert sha256(path.read_bytes()).hexdigest() == ENGINE_SHA
    engine = run_path(str(path))
    data = {name: (ROOT / name).read_bytes() for name in engine["PINS"]}
    assert {name: sha256(raw).hexdigest() for name, raw in data.items()} == engine["PINS"]
    decoded = decompress(data["7481-WORD.json.gz"])
    assert sha256(decoded).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(decoded)
    app = loads(data["7481-APPLICATION.json"])
    assert app["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert loads(data["7113-CALLER.json"])["stages"] == 17
    tape = word["program"]
    assert tape[CUT - 1:CUT + 3] == [
        ["MOVE", 1322, 3, CHART, False],
        ["ADD", 1352, 1322, "2", CHART],
        ["ADD", 1440, 1322, "-2", CHART],
        ["ADD", 679, 1440, "-1/2", CHART],
    ]
    _, active, _ = engine["census"](word, CUT)
    assert all(active[role] == CHART for role in BANK)
    main_roles = set(word["live"]) | {r + 112 for r in word["live"]}
    main_roles.update(word["hosted"]["X2"] + word["hosted"]["Y2"])
    assert len(main_roles) == 400 and not main_roles.intersection(BANK)
    initial = [word["initial"][role] for role in BANK]
    final = [word["final"][role] for role in BANK]
    crossed = final[1:] + final[:1]
    frames = word["frames"]
    assert all(span(frames[i]) < span(frames[j]) for i, j in zip(initial, crossed))
    old = [len(frames[j]) - len(frames[i]) for i, j in zip(initial, final)]
    new = [len(frames[j]) - len(frames[i]) for i, j in zip(initial, crossed)]
    assert (old, new) == ([9, 5, 2], [5, 7, 4])
    lo, hi = map(Q, app["directed_crossing_bracket"])
    h = run_path(str(ROOT / "pricing.py"))["power_bounds"]
    gross = [17 * (h(7, hi)[0] + h(4, hi)[0] - h(9, lo)[1] - h(2, lo)[1]),
             17 * (h(7, lo)[1] + h(4, lo)[1] - h(9, hi)[0] - h(2, hi)[0])]
    assert 0 < gross[0] <= gross[1] < 17

    rows = engine["exact_cut_rows"](tape[:CUT], BANK, word["public"])
    pivots = engine["basis"](rows)
    contrasts = ({BANK[0]: Q(1), BANK[1]: Q(-1)},
                 {BANK[1]: Q(1), BANK[2]: Q(-1)})
    out = []
    for contrast in contrasts:
        residual, coefficients = engine["representation"](pivots, contrast)
        probe = {}
        if residual:
            j = min(residual)
            probe[j] = Q(1)
            for pivot, (row, _) in sorted(pivots.items(), reverse=True):
                value = -sum(v * probe.get(k, 0) for k, v in row.items() if k != pivot)
                if value:
                    probe[pivot] = value
            assert all(sum(v * probe.get(k, 0) for k, v in row.items()) == 0 for row in rows)
            assert sum(v * probe.get(k, 0) for k, v in contrast.items()) == residual[j]
        out.append({"contrast": contrast, "residual": residual, "probe": probe,
                    "bank_response": [sum(v * probe.get(k, 0) for k, v in row.items()) for row in rows],
                    "target_response": sum(v * probe.get(k, 0) for k, v in contrast.items()),
                    "combination": {BANK[i]: value for i, value in coefficients.items()}})
    assert not engine["representation"](pivots, rows[0])[0]
    print(dumps({"case_count": 1, "cap_seconds": 30,
                 "status": "PREFIX_EXCLUDES_FIXED_CYCLE" if any(r["residual"] for r in out) else "PREFIX_PASSES",
                 "cut": CUT, "bank": BANK, "bank_rank": len(pivots), "old_ranks": old, "new_ranks": new,
                 "gross": gross, "gross_decimal_display": [float(x) for x in gross],
                 "contrasts": out, "input_pins": engine["PINS"], "engine_sha256": ENGINE_SHA},
                sort_keys=True, indent=2, default=str))
    alarm(0)


if __name__ == "__main__":
    main()
