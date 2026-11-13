"""Exhaust every proper mask and parity on all fixed Type B 36/37 prefix cuts."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

HERE = Path(__file__).resolve().parent
PINS = {
    "check_type_b_root.py": "4734ba6500c4934b3f8616f4c39a62e458909685c9e6f306130ddb101127eba9",
    "type_a_laurent.py": "1043c6cb86af5c3fe348e62e5e7f89c2148e1273f1456382907a1a77a739b0df",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
}
TOTAL = 4784
SURVIVOR_CAP = 1
FULL_BODY = tuple(range(1, 18))
state = dict(last_completed_cut=None, cuts_tested=0, first_unvisited_cut=0, survivors=[])


def verify(path, pin):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == pin, path
    return raw


def emit(record):
    print(json.dumps(record, default=str, sort_keys=True, separators=(",", ":")), flush=True)


def cap(_sig, _frame):
    emit(dict(status="UNRESOLVED_CAP", total_cut_cap=TOTAL, **state))
    raise SystemExit(124)


def sector_rows(columns, sector):
    tables = []
    for column in columns:
        table = {}
        for role, row in enumerate(column, 36):
            for (phase, body), coeff in row.items():
                key = (body, phase % 2), role
                sign = sector ** (phase // 2)
                prior = table.get(key, (0, 0))
                value = tuple(a+sign*b for a, b in zip(prior, coeff, strict=True))
                if any(value):
                    table[key] = value
                else:
                    table.pop(key, None)
        tables.append(table)
    zero = (0, 0)
    return [(key, (tables[0].get(key, zero), tables[1].get(key, zero)))
            for key in sorted(tables[0].keys() | tables[1].keys())]


def admissible(key):
    body, parity = key
    return bool(body) and len(body) < 17 and len(set(body)) == len(body) and parity in (0, 1)


def classify(rows, minor):
    base = minor(rows)
    # Both prefix columns are independent over the full Laurent algebra.
    # A sector's coefficient matrix must therefore have independent columns.
    assert base["rank"] == 2
    possible = {key[0] for key in base["keys"] if admissible(key[0])}
    survivors, rejected = [], []
    for key in sorted(possible):
        residual = minor([(row_key, value) for row_key, value in rows if row_key[0] != key])
        (survivors if residual["rank"] < 2 else rejected).append([key, residual])
    return dict(base_minor=base, checked_classes=sorted(possible), survivors=survivors, rejected=rejected)


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_root", type=Path)
    parser.add_argument("--cap", type=int, choices=(30, 120), default=30)
    args = parser.parse_args()
    state["cap_seconds"] = args.cap
    signal.signal(signal.SIGALRM, cap)
    signal.alarm(args.cap)
    root = args.input_root.resolve()
    raw = {name: verify((HERE if name.endswith(".py") else root) / name, pin)
           for name, pin in PINS.items()}
    caller = json.loads(raw["7113-CALLER.json"])
    app = json.loads(raw["7481-APPLICATION.json"])
    assert app["claim_decimal"] == "0.003647081039689"
    kind = caller["types"]["B"]
    assert kind["offset"] == 36 and kind["roles"] == 36
    assert kind["ports"] == [15, 17, 27, 34, 35, 42, 47, 55]
    assert kind["diagonal"][:2] == [[-1, 0]+[1]*17]*2
    tape = caller["events"]
    assert len(tape)+1 == TOTAL and caller["stages"] == 17
    leaf = run_path(str(HERE / "check_type_b_root.py"))
    engine = run_path(str(HERE / "type_a_laurent.py"))
    add, scale = engine["add_scaled"], engine["scaled"]
    minor, propagate = leaf["minor"], leaf["propagate"]
    # A single allowed body class cannot remove both rows of a minor with
    # inadmissible empty/full bodies, but a rank-one deletion can survive.
    test = [((((1,), 0), 36), ((1, 0), (0, 0))),
            ((((2,), 1), 37), ((0, 0), (1, 0)))]
    assert len(classify(test, minor)["survivors"]) == 2
    assert not classify([(( ((), 0), role), values) for (_, role), values in test], minor)["survivors"]
    columns = [[{} for _ in range(36)] for _ in range(2)]
    for j, column in enumerate(columns):
        column[j] = {(0, ()): (Q(1), Q(0))}
    emit(dict(status="START", cap_seconds=args.cap, total_cut_cap=TOTAL, pins=PINS,
              survivor_cap=SURVIVOR_CAP, fixed_old_roots=[36, 37],
              mask_rule="nonempty proper squarefree subsets of all 17 stage bodies"))
    survivor = None
    for clock in range(TOTAL):
        if survivor is None:
            plus, minus = (classify(sector_rows(columns, q), minor) for q in (1, -1))
            plus_keys = {tuple(key) for key, _ in plus["survivors"]}
            minus_keys = {tuple(key) for key, _ in minus["survivors"]}
            survivors = sorted(plus_keys & minus_keys)
            emit(dict(cut=clock, plus=plus, minus=minus, surviving_classes=survivors))
            state["last_completed_cut"] = clock
            state["cuts_tested"] = clock+1
            state["first_unvisited_cut"] = clock+1 if clock+1 < TOTAL else None
            if survivors:
                survivor = survivors[0]
                state["survivors"] = [[clock, survivor]]
                state["other_unvisited_classes_at_cut"] = survivors[1:]
        if clock < len(tape):
            for column in columns:
                propagate(column, tape[clock], add, scale)
    for j, column in enumerate(columns):
        expected = [{} for _ in range(36)]
        expected[j] = {(3, FULL_BODY): (Q(1), Q(0))}
        assert column == expected
    status = "FIRST_PREFIX_SURVIVOR" if survivor else "PASS_FIXED_CLASS_CENSUS"
    emit(dict(status=status, exact_original_endpoints=True, survivor_cap=SURVIVOR_CAP,
              total_cut_cap=TOTAL, **state))
    signal.alarm(0)


if __name__ == "__main__":
    main()
