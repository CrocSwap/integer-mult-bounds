"""One fixed grouped Type B rank-137 prefix case on the exact #7113 tape."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

HERE = Path(__file__).resolve().parent
CASE = "type-b-root36-through-36-37-pre3058-even-first"
ROLES = (36, 37)
CUT = 3058
BODY = tuple(range(1, 9))
PINS = {
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
ENGINE = "1043c6cb86af5c3fe348e62e5e7f89c2148e1273f1456382907a1a77a739b0df"


def verify(path, pin):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == pin, path
    return raw


def emit(record):
    print(json.dumps(record, default=str, sort_keys=True), flush=True)


def capped(_sig, _frame):
    emit(dict(case=CASE, status="UNRESOLVED_CAP", unresolved=[CASE], cap_seconds=30))
    raise SystemExit(124)


def multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def propagate(rows, event, add, scale):
    if event[0] == "J":
        _, stage, _, (first, second, alpha, beta) = event
        first, second = first-36, second-36
        assert Q(alpha) == -1 and Q(beta) == Q(1, 2)
        x, y = rows[first], rows[second]
        rows[first] = scale(x, factors=(stage,))
        add(rows[first], y, Q(alpha), Q(0), exponent=1, factors=(stage,))
        rows[second] = scale(y, 1+Q(alpha)*Q(beta), factors=(stage,))
        add(rows[second], x, Q(beta), Q(0), exponent=-1, factors=(stage,))
        return
    if event[0] != "B":
        return
    _, op, role, *args = event
    role -= 36
    if op == "ADD":
        add(rows[role], rows[args[0]-36], Q(args[1]), Q(0))
    elif op == "SWAP":
        peer = args[0]-36
        rows[role], rows[peer] = rows[peer], rows[role]
    elif op == "SCALE":
        rows[role] = scale(rows[role], a=Q(args[0]))
    elif op == "LAMBDA":
        sign, = args
        assert sign in (-1, 1)
        source = rows[role]
        rows[role] = scale(source, Q(1, 2), Q(sign, 2))
        add(rows[role], source, Q(1, 2), Q(-sign, 2), exponent=2)
    else:
        assert op in ("IDLE_ONE", "IDLE_ODD")
        rows[role] = scale(rows[role], exponent=args[1] if op == "IDLE_ODD" else 0,
                           factors=tuple(args[0]))


def forbidden(columns, sector):
    tables = []
    for column in columns:
        table = {}
        for role, row in enumerate(column, 36):
            for (phase, body), coeff in row.items():
                if body == BODY and phase % 2 == 0:
                    continue
                key = role, phase % 2, body
                sign = sector ** (phase // 2)
                prior = table.get(key, (0, 0))
                table[key] = tuple(a+sign*b for a, b in zip(prior, coeff, strict=True))
        tables.append(table)
    return [(key, (tables[0].get(key, (0, 0)), tables[1].get(key, (0, 0))))
            for key in sorted(tables[0].keys() | tables[1].keys())]


def minor(rows):
    first = None
    for key, values in rows:
        if first is None:
            if any(any(z) for z in values):
                first = key, values
            continue
        a, b = first[1]
        c, d = values
        det = tuple(x-y for x, y in zip(multiply(a, d), multiply(b, c), strict=True))
        if any(det):
            return {"rank": 2, "keys": [first[0], key], "rows": [first[1], values], "determinant": det}
    return {"rank": int(first is not None), "first_nonzero": first}


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    signal.signal(signal.SIGALRM, capped)
    signal.alarm(30)
    root = Path(sys.argv[1]).resolve()
    raw = {path: verify(root / path, pin) for path, pin in PINS.items()}
    engine = HERE / "type_a_laurent.py"
    verify(engine, ENGINE)
    old = run_path(str(engine))
    add, scale = old["add_scaled"], old["scaled"]
    caller = json.loads(raw["7113-CALLER.json"])
    app = json.loads(raw["7481-APPLICATION.json"])
    tape = caller["events"]
    kind = caller["types"]["B"]
    assert caller["roles"] == 72 and caller["stages"] == 17 and len(tape) == 4783
    assert kind["offset"] == 36 and kind["ports"] == [15, 17, 27, 34, 35, 42, 47, 55]
    assert kind["diagonal"][:2] == [[-1, 0]+[1]*17]*2
    assert tape[CUT] == ["J", 9, [9, 0, 18, 27], [36, 37, "-1", "1/2"]]
    assert all(e[1] != "QUERY" for e in tape if e[0] == "B")
    columns = []
    for role in ROLES:
        rows = [{} for _ in range(36)]
        rows[role-36] = {(0, ()): (Q(1), Q(0))}
        for clock, event in enumerate(tape):
            if clock == CUT:
                columns.append([dict(row) for row in rows])
            propagate(rows, event, add, scale)
        expected = [{} for _ in range(36)]
        expected[role-36] = {(3, tuple(range(1, 18))): (Q(1), Q(0))}
        assert rows == expected, role
    assert len(columns) == 2
    assert minor([("x", ((1, 0), (0, 0))), ("y", ((0, 0), (1, 0)))])["rank"] == 2
    assert minor([("x", ((1, 0), (1, 0))), ("y", ((2, 0), (2, 0)))])["rank"] == 1
    assert minor([])["rank"] == 0
    result = {str(sector): minor(forbidden(columns, sector)) for sector in (1, -1)}
    lo, hi = map(Q, app["directed_crossing_bracket"])
    power = run_path(str(root / "pricing.py"))["power_bounds"]
    gross = [8*(power(64, hi)[0]+power(73, hi)[0]-power(137, lo)[1]),
             8*(power(64, lo)[1]+power(73, lo)[1]-power(137, hi)[0])]
    assert 0 < gross[0] <= gross[1] < 8
    excluded = any(r["rank"] == 2 for r in result.values())
    emit(dict(case=CASE, status="EXACT_GROUPED_PREFIX_EXCLUSION" if excluded else "PREFIX_SURVIVOR_SUFFIX_UNTESTED",
              unresolved=[] if excluded else [CASE], tested=1, cap_seconds=30, clock=CUT,
              old_roots=ROLES, sectors=result, gross=gross, signed_paid_delta={},
              signed_productive_delta={64:8, 73:8, 137:-8},
              pins={**PINS, "type_a_laurent.py": ENGINE}))
    signal.alarm(0)


if __name__ == "__main__":
    main()
