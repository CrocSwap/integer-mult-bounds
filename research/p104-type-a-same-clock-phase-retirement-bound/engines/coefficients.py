"""Bound the four same-clock even coefficients at the Type A unit-body endpoints."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
CALLER_SHA256 = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
FLIPS = (0, 18)
ROWS = (0, 1, 18, 19)
COLUMNS = (2, 9, 20, 27)


def stop(*_):
    raise TimeoutError("20-second exact cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(20)
    source = ROOT / "literal.py"
    engine = run_path(str(source))
    diagonal, transfer, difference, minor, rank = [
        engine[name] for name in ("diagonal", "transfer", "difference", "minor", "rank")
    ]
    raw = (ROOT / "inputs/CALLER.json").read_bytes()
    assert sha256(raw).hexdigest() == CALLER_SHA256
    caller = loads(raw)
    events = caller["events"]
    assert len(events) == 4783
    alpha = Fraction(caller["types"]["A"]["alpha2"])
    baseline_plus = diagonal(1)
    baseline_minus = diagonal(-1)
    assert transfer(events, alpha, 1) == baseline_plus
    assert transfer(events, alpha, -1) == baseline_minus

    minus_changed = difference(transfer(events, alpha, -1, (1,) * 4), baseline_minus)
    minus_minor = minor(minus_changed, ROWS, COLUMNS)
    assert minus_minor["determinant"] == 64
    assert set(ROWS).isdisjoint(COLUMNS)

    plus_changed = difference(transfer(events, alpha, 1, (-1,) * 4), baseline_plus)
    assert rank(plus_changed) == 4
    plus_nonzero = [
        [i, j, v] for i, row in enumerate(plus_changed) for j, v in enumerate(row) if v
    ]
    desired_minus = diagonal(-1)
    for i in FLIPS:
        desired_minus[i][i] = 1

    results = []
    for plus_slots in combinations(range(4), 2):
        coefficients = tuple(1 if i in plus_slots else -1 for i in range(4))
        plus = transfer(events, alpha, 1, coefficients)
        minus = transfer(events, alpha, -1, coefficients)
        assert rank(difference(plus, baseline_plus)) == 2
        assert rank(difference(minus, baseline_minus)) == 2
        residual = difference(desired_minus, minus)
        results.append({
            "coefficients": coefficients,
            "unchanged_plus_rank": 2,
            "unchanged_minus_rank": 2,
            "changed_minus_rank": rank(residual),
        })

    alarm(0)
    print(dumps({
        "pins": {"inputs/CALLER.json": CALLER_SHA256, "literal.py": sha256(source.read_bytes()).hexdigest()},
        "plus_all_opposite_rank": 4,
        "plus_all_opposite_nonzero_entries": plus_nonzero,
        "minus_all_opposite_off_diagonal_minor": minus_minor,
        "flipped_roots": FLIPS,
        "tested_sign_patterns": results,
        "survivors": [r["coefficients"] for r in results if r["changed_minus_rank"] <= 2],
        "cases": 8, "roles": 36, "events": len(events), "hard_cap_seconds": 20,
    }, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
