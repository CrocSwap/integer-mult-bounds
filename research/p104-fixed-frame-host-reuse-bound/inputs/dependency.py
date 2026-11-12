"""Exact minimum support in the full-suffix signed Type A configurations."""
from fractions import Fraction as F
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/forward.py": "75d94780f9db49a4b08bb0e7fb4bd7fc04adb8cabbf73d83a809179c04c3d439",
}
DIMENSION = 36


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True) if x and y)


def add(a, b, coefficient):
    return [x + coefficient * y for x, y in zip(a, b, strict=True)]


def product(factors, column, inverse=False):
    for u, v in reversed(factors) if inverse else factors:
        column = add(column, u, (-1 if inverse else 1) * dot(v, column))
    return column


def rref(rows):
    rows = [list(row) for row in rows]
    pivots = []
    for col in range(len(rows[0])):
        row = len(pivots)
        pivot = next((i for i in range(row, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        divisor = rows[row][col]
        rows[row] = [x / divisor for x in rows[row]]
        for i, other in enumerate(rows):
            if i != row and other[col]:
                rows[i] = add(other, rows[row], -other[col])
        pivots.append(col)
    return rows, pivots


def nullspace(columns):
    rows, pivots = rref(zip(*columns, strict=True))
    width = len(columns)
    vectors = []
    for j in sorted(set(range(width)) - set(pivots)):
        x = [F(i == j) for i in range(width)]
        for row, pivot in zip(rows[:len(pivots)], pivots, strict=True):
            x[pivot] = -row[j]
        assert all(not dot(x, row) for row in zip(*columns, strict=True))
        vectors.append(x)
    assert len(vectors) == 2
    return pivots, vectors


def supports(kernel):
    slopes = {}
    always_zero = []
    for j, (a, b) in enumerate(zip(*kernel, strict=True)):
        if not a and not b:
            always_zero.append(j)
            continue
        slope = b / a if a else "infinity"
        slopes.setdefault(slope, []).append(j)
    witnesses = []
    for slope, omitted in slopes.items():
        a, b = [vec[omitted[0]] for vec in kernel]
        x = add([b * y for y in kernel[0]], kernel[1], -a)
        support = [i for i, coeff in enumerate(x) if coeff]
        assert set(range(len(x))) - set(support) == set(omitted) | set(always_zero)
        witnesses.append({"slope": str(slope), "omitted": omitted, "support": support,
                          "coefficients": [str(y) for y in x]})
    return {"always_zero": always_zero, "witnesses": witnesses}


def source_factors(unit, apply, tape):
    factors, keys = [], []
    for clock, event in enumerate(tape):
        if event[0] == "J":
            a, b, c, d = event[2]
            shears = [(b, a, 1), (c, d, -1)]
        elif event[:2] == ["A", "QUERY"]:
            assert event[-1] == -1
            shears = [(event[2], event[3], 1)]
        else:
            continue
        prefix = tape[:clock]
        cols = [apply(prefix, unit(j), -1) for j in range(DIMENSION)]
        for dest, source, sign in shears:
            u = apply(prefix, unit(dest), -1, inverse=True)
            v = [2 * sign * col[source] for col in cols]
            assert any(u) and any(v) and not dot(u, v)
            factors.append((u, v))
            keys.append([clock, dest, source])
    assert len(factors) == 38
    return factors, keys


def suffix_transport(factors):
    result = []
    for i, (u, v) in enumerate(factors):
        for a, b in factors[i + 1:]:
            u = add(u, a, dot(b, u))
            v = add(v, b, -dot(v, a))
        assert not dot(u, v)
        result.append((u, v))
    return result


def target(case, factors, transported, units):
    unselected = [f for i, f in enumerate(factors) if i not in case]
    selected = [transported[i] for i in reversed(case)]
    cols = [product(selected, col) for col in units]
    assert cols == [[-x for x in product(unselected, col, inverse=True)] for col in units]
    delta = [add(col, e, -1) for col, e in zip(cols, units, strict=True)]
    _, pivots = rref(zip(*delta, strict=True))
    return cols, pivots


def stop(*_):
    raise TimeoutError("20-second exact nullspace and literal-product cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(20)
    for name, digest in PINS.items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest
    source = run_path(str(ROOT / "inputs/forward.py"))
    unit, apply = source["unit"], source["apply"]
    tape = loads((ROOT / "inputs/CALLER.json").read_bytes())["events"]
    assert len(tape) == 4783
    factors, keys = source_factors(unit, apply, tape)
    units = [unit(i) for i in range(DIMENSION)]
    for e in units:
        assert apply(tape, e, 1) == e
        assert apply(tape, e, -1) == product(factors, e) == [-x for x in e]
    transported = suffix_transport(factors)
    certs, candidates = {}, []
    for axis, name in enumerate(("image", "covector")):
        pivots, kernel = nullspace([f[axis] for f in transported])
        cert = supports(kernel)
        cert["pivots"] = pivots
        cert["kernel"] = [[str(x) for x in col] for col in kernel]
        certs[name] = cert
        candidates.extend((len(w["support"]), w["support"], name) for w in cert["witnesses"])
    controls = [[0, 37], [1, 20, 36], [0, 4, 33, 37]]
    for case in controls:
        assert len(target(case, factors, transported, units)[1]) == len(case)
    minimum, chosen, axis = min(candidates)
    tied = sorted({tuple(case) for length, case, _ in candidates if length == minimum})
    cols, pivots = target(chosen, factors, transported, units)
    assert len(pivots) < minimum and chosen[0] < 2 and chosen[-1] >= 36
    result = {
        "pins": PINS, "budget_seconds": 20, "factor_keys": keys, "factor_count": len(keys),
        "dimension": DIMENSION, "minimum_support": minimum, "chosen": chosen,
        "chosen_axis": axis, "tied_supports": tied, "displacement_pivots": pivots,
        "target_columns": [[str(x) for x in col] for col in cols], "certificates": certs,
        "full_signs": [1, -1], "controls": controls,
    }
    alarm(0)
    print(dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
