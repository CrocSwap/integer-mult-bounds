"""Exact rank-two diagonal completion anchors for the six Type A words."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
CALLER_SHA256 = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
ROLES = 36
ANCHOR_ROWS = (0, 1, 18, 19)
ANCHOR_COLS = (2, 9, 20, 27)
FLIPS = (0, 17)


def choose_anchor(matrix, avoid):
    original_rows = tuple(i for i in ANCHOR_ROWS if i != avoid)
    original_cols = tuple(i for i in ANCHOR_COLS if i != avoid)
    candidates = (
        (original_rows, original_cols),
        (tuple(i for i in range(ROLES) if i != avoid), None),
    )
    for rows, cols in candidates:
        for r, s in combinations(rows, 2):
            columns = cols
            if columns is None:
                columns = tuple(i for i in range(ROLES) if i not in (avoid, r, s))
            first = next((i for i in columns if matrix[r][i] or matrix[s][i]), None)
            if first is None:
                continue
            for j in columns:
                det = matrix[r][first] * matrix[s][j] - matrix[r][j] * matrix[s][first]
                if det:
                    return [r, s], [first, j], det
    return None


def stop(*_):
    raise TimeoutError("20-second exact cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(20)
    source = ROOT / "literal.py"
    engine = run_path(str(source))
    diagonal, transfer, difference, rank = (
        engine[k] for k in ("diagonal", "transfer", "difference", "rank")
    )
    raw = (ROOT / "inputs/CALLER.json").read_bytes()
    assert sha256(raw).hexdigest() == CALLER_SHA256
    caller = loads(raw)
    alpha = Fraction(caller["types"]["A"]["alpha2"])
    events = caller["events"]
    reference = diagonal(-1)
    assert transfer(events, alpha, -1) == reference
    changed = diagonal(-1)
    for i in FLIPS:
        changed[i][i] = 1

    patterns = []
    for positive in combinations(range(4), 2):
        coefficients = tuple(1 if i in positive else -1 for i in range(4))
        erased = transfer(events, alpha, -1, coefficients)
        off_diagonal_reference = difference(erased, reference)
        assert rank(off_diagonal_reference) == 2
        anchors = []
        missing = []
        for role in range(ROLES):
            anchor = choose_anchor(off_diagonal_reference, role)
            if anchor is None:
                missing.append(role)
                continue
            rows, cols, det = anchor
            assert set(rows).isdisjoint(cols)
            assert role not in rows and role not in cols
            anchors.append([role, rows, cols, det])

        # Changing one anchored diagonal produces the same 2×2 block and
        # a nonzero 3×3 determinant by the Schur-complement identity.
        role, rows, cols, det = anchors[0]
        control = [row.copy() for row in off_diagonal_reference]
        control[role][role] += 2
        assert engine["minor"](control, (*rows, role), (*cols, role))["determinant"] == 2 * det
        patterns.append({
            "coefficients": coefficients, "anchors": anchors, "missing_roles": missing,
            "changed_pair_rank": rank(difference(erased, changed)),
        })

    alarm(0)
    print(dumps({
        "pins": {"inputs/CALLER.json": CALLER_SHA256, "literal.py": sha256(source.read_bytes()).hexdigest()},
        "candidate_pair": FLIPS, "patterns": patterns,
        "number_of_anchors": sum(len(x["anchors"]) for x in patterns),
        "words": len(patterns), "hard_cap_seconds": 20, "controls": ["original -I", "one corrupted diagonal"],
    }, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
