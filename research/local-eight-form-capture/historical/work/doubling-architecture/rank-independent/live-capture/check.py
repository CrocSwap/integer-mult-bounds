"""Replay the hosted capture by exact propagation of every input column."""

from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / "work/next-track/complex/pipeline/retimed-4"


def compile_ops(operations):
    result = []
    for event in operations:
        if event[0] == "add":
            result.append((event[1], event[2], Q(event[3], event[4])))
        else:
            assert event[0] == "scale"
            result.append((event[1], -1, Q(event[2], event[3])))
    return result


def apply(vector, operations):
    for dst, src, coefficient in operations:
        if src >= 0:
            if vector[src]:
                vector[dst] += coefficient * vector[src]
        elif vector[dst]:
            vector[dst] *= coefficient


def main():
    wp = BASE / "split-centres/CANONICAL-WORD.json.gz"
    tp = BASE / "complex/GLOBAL-TEMPLATE.json.gz"
    w = json.loads(gzip.decompress(wp.read_bytes()))
    t = json.loads(gzip.decompress(tp.read_bytes()))
    n = 240 + w["R"]
    assert n == 800
    operations = compile_ops(w["precondition"] + w["compensation"] + w["A"] + w["B"] + w["cleanup"])
    prefix = compile_ops(w["precondition"] + w["A"])
    S, D, C = ([{} for _ in range(120)], [{} for _ in range(120)], [{} for _ in range(8)])
    for column in range(n):
        vector = [0] * n
        vector[column] = 1
        apply(vector, operations)
        for row in list(range(120)) + list(range(240, n)):
            assert vector[row] == int(row == column)
        for i in range(120):
            value = vector[120 + i]
            if column < 120 and value:
                S[i][column] = value
            elif 120 <= column < 240:
                assert value == int(column == 120 + i)
            elif column >= 240 and value:
                D[i][column] = value
                assert w["start"][column] == 0
                assert value.denominator.bit_count() == 1
        if column < 120:
            vector = [0] * n
            vector[column] = 1
            apply(vector, prefix)
            for i, center in enumerate(w["centers"][:8]):
                if vector[center]:
                    C[i][column] = vector[center]
    code = [i for i, row in enumerate(S) if row]
    assert len(code) == 112
    assert [[sum(a.get(j, 0) * b.get(j, 0) for j in range(120)) for b in C] for a in C] == [[56 * int(i == j) for j in range(8)] for i in range(8)]
    for i in range(120):
        for j in range(120):
            gram = Q(1, 4) * sum(row.get(i, 0) * row.get(j, 0) for row in C)
            assert S[i].get(j, 0) == (int(i == j) - gram if i in code else 0)
    helpers = tuple(range(758, 750, -1))
    assert all(w["start"][h] == 0 and w["final"][h] == 1 for h in helpers)
    assert all(w["start"][120 + j] == 0 and w["final"][j] == 1 for row in C for j in row)
    for column in range(n):
        vector = [0] * n
        vector[column] = 1
        for helper, row in zip(helpers, C):
            vector[helper] += sum(q * vector[120 + j] for j, q in row.items())
        for i, row in enumerate(D):
            vector[120 + i] -= sum(q * vector[j] for j, q in row.items())
        apply(vector, operations)
        for helper, row in zip(helpers, C):
            vector[helper] += Q(59, 4) * sum(q * vector[j] for j, q in row.items())
        expected = [0] * n
        expected[column] = 1
        if column < 120:
            for i, row in enumerate(S):
                expected[120 + i] += row.get(column, 0)
            for helper, row in zip(helpers, C):
                expected[helper] += Q(59, 4) * row.get(column, 0)
        elif column < 240:
            for helper, row in zip(helpers, C):
                expected[helper] += row.get(column - 120, 0)
        assert vector == expected
    assert t["residual_adapters"]["recipes"]["0"] == {"identity_adapters": True, "post": None, "pre": None, "rank": 9}
    windows = {e["idx"]: e for e in t["execution_schedule"] if e["kind"] == "idle"}
    owners = []
    for helper in helpers:
        family, route = t["calls"][0]["owners"][helper]
        assert 600 <= family <= 607
        pair, side = family // 240, (family % 240) // 120
        assert (pair, side) == (2, 1)
        assert route == [4, 2, 0, 9, 0, list(range(1, 10))]
        assert windows[2]["source_level"] == -1 and windows[2]["pair"] == pair
        roles = []
        for call in t["calls"]:
            if call["replica"] != 0:
                continue
            uses = [(i, r) for i, (f, r) in enumerate(call["owners"]) if f == family]
            assert len(uses) <= 1
            roles.extend({"stage": call["stage"], "register": i, "route": r} for i, r in uses)
        assert [r["stage"] for r in roles if r["stage"] <= 3] == [0, 2, 3]
        owners.append({"helper": helper, "family": family, "entry_frame": "I", "roles": roles})
    result = {
        "status": "PASS_INDEPENDENT_800_COLUMN_DIRTY_CAPTURE",
        "base_columns": n, "complete_capture_columns": n,
        "base_scalar_operations": len(operations),
        "code_ports": len(code), "center_gram": 56,
        "dirt_correction_coefficients": sum(len(row) for row in D),
        "retained_forms": 8,
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (wp, tp)},
        "owners": owners,
        "scope": "Exact local label map and initial owner-frame inventory only. No modified global controller, endpoint uncompute, finite invoice, or new exponent is certified.",
    }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "owners"}, indent=2))


if __name__ == "__main__":
    main()
