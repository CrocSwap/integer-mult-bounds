"""Check the actual centre constants without producer imports."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
LANE = HERE.parents[1]
LANES = LANE.parent
PRODUCER = LANE / "rational-code-admission-20261020"
PINS = {
    "rank30": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json",
        "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
    ),
    "rank16": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
        "7160a8764f0b12131e30dd1ca90a28b781b9dd99e8eb2f1935b8592aaf48037b",
    ),
    "literal": (
        PRODUCER / "centre-constants-normal/CENTRE-CONSTANTS.json",
        "9f45130ccde5bf1624bf051f4b10023411d6f35f0ac99bd6ab13572d4c530368",
    ),
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    columns = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col) if x and y)
             for col in columns] for row in a]


def dense(rows, n):
    return [[F(row.get(str(j), 0)) for j in range(n)] for row in rows]


def inverse(a):
    n = len(a)
    rows = [row[:] + unit for row, unit in zip(a, eye(n))]
    for j in range(n):
        k = next((k for k in range(j, n) if rows[k][j]), None)
        need(k is not None, "Nonsingular exact matrix")
        rows[j], rows[k] = rows[k], rows[j]
        q = rows[j][j]
        rows[j] = [x / q for x in rows[j]]
        for k in range(n):
            if k != j and rows[k][j]:
                q = rows[k][j]
                rows[k] = [x - q * y for x, y in zip(rows[k], rows[j])]
    return [row[n:] for row in rows]


def height(x, p):
    d, result = x.denominator, 0
    while d % p == 0:
        d //= p
        result += 1
    return result


def dyadic(a):
    return all(x.denominator & (x.denominator - 1) == 0 for row in a for x in row)


def row_minor(a):
    basis, indices = {}, []
    for i, original in enumerate(a):
        row = original[:]
        for p in sorted(basis):
            q = row[p]
            if q:
                row = [x - q * y for x, y in zip(row, basis[p])]
        p = next((p for p, x in enumerate(row) if x), None)
        if p is not None:
            q = row[p]
            basis[p] = [x / q for x in row]
            indices.append(i)
            if len(indices) == len(a[0]):
                break
    need(len(indices) == len(a[0]), "Full column rank")
    return indices


def factor(g):
    if g[0] == "NEG":
        return F(-1)
    if g[0] == "SCALE2":
        return F(2) ** g[2]
    if g[0] == "MULTIPLY_ODD":
        return F(g[2])
    need(g[0] == "DIVIDE_ODD", "Known scalar gate")
    return F(1, g[2])


def replay(word, n, initial=None, integral=False):
    rows = eye(n + 2) if initial is None else [row[:] for row in initial]
    peak = max(sum(abs(x) for x in row) for row in rows)
    temporary = F(0)
    levels = {p: 0 for p in (2, 3, 5, 7)}
    divisions = 0
    for g in word:
        t = g[1]
        need(0 <= t < n, "Only centre targets")
        if g[0] == "ADD":
            s, q = g[2:]
            need(0 <= s < n and s != t and q in (-1, 1), "Only centre unit sources")
            temporary = max(temporary, sum(abs(x) for x in rows[t]) +
                            sum(abs(x) for x in rows[s]))
            rows[t] = [x + q * y for x, y in zip(rows[t], rows[s])]
        else:
            if g[0] == "DIVIDE_ODD" and integral:
                need(all(x.denominator == 1 and x.numerator % g[2] == 0
                         for x in rows[t]), "Exact integer numerator division")
                divisions += 1
            q = factor(g)
            rows[t] = [q * x for x in rows[t]]
        if integral:
            need(all(x.denominator == 1 for x in rows[t]), "Integral stored prefix")
        peak = max(peak, sum(abs(x) for x in rows[t]))
        for p in levels:
            levels[p] = max(levels[p], max(height(x, p) for x in rows[t]))
    need(rows[n:] == eye(n + 2)[n:] if initial is None else rows[n:] == initial[n:],
         "Arbitrary spectator rows are unchanged")
    need(all(row[n:] == [0, 0] for row in rows[:n]), "No spectator columns enter data")
    return rows, {"stored_l1": str(peak), "unit_add_operand_l1": str(temporary),
                  "height": levels, "exact_odd_divisions": divisions}


def reverse_replay(word, n):
    result = []
    for i in range(n + 2):
        row = [F(i == j) for j in range(n + 2)]
        for g in reversed(word):
            if g[0] == "ADD":
                row[g[2]] += g[3] * row[g[1]]
            else:
                row[g[1]] *= factor(g)
        result.append(row)
    return result


def square_code(u, d, selected):
    n, r = len(u), len(selected)
    ordinary = [i for i in range(n) if i not in selected]
    ua, uu = [u[i] for i in selected], [u[i] for i in ordinary]
    ai = inverse(ua)
    projection = mm(uu, ai)
    c = [row[:] for row in d]
    for k, i in enumerate(ordinary):
        row = [F(i == j) for j in range(n)]
        for j, a in enumerate(selected):
            row[a] -= projection[k][j]
        c.append(row)
    du = [[row[i] for i in ordinary] for row in d]
    x = mm(u, du)
    ci = [u[i][:] + [-value for value in x[i]] for i in range(n)]
    for j, i in enumerate(ordinary):
        ci[i][r + j] += 1
    need(mm(c, ci) == mm(ci, c) == eye(n), "Both complete square-code inverse orders")
    bound = {p: max(height(x, p) for row in d for x in row) for p in (3, 5, 7)}
    for a in (c, ci):
        need(all(max(height(x, p) for row in a for x in row) <= bound[p] for p in bound),
             "Square code and inverse preserve the D odd-height bound")
    return {
        "minor_rows": selected,
        "minor_inverse_is_dyadic": dyadic(ai),
        "minor_inverse_denominators": sorted({x.denominator for row in ai for x in row}),
        "code_heights": {p: max(height(x, p) for row in c for x in row) for p in bound},
        "inverse_code_heights": {p: max(height(x, p) for row in ci for x in row) for p in bound},
        "checked_data_columns": n,
        "symbolic_phase_extension": "J=Q^2 U, J_A^-1=U_A^-1 Q_A^2, D=B0^-1 V Q^2; Q^4=I.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    need(shutil.disk_usage(HERE).free >= 3 * 2**30, "Disk floor")
    data, sources = {}, {}
    for name, (path, pin) in PINS.items():
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == pin, "Source hash " + name)
        sources[name] = {"path": str(path), "sha256": pin}
        if name == "rank16":
            raw = gzip.decompress(raw)
            digest = sha256(raw).hexdigest()
            need(digest == "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
                 "Native payload hash")
            sources[name]["payload_sha256"] = digest
        obj = json.loads(raw)
        data[name] = obj.get("model", obj)
    results = {}
    for family, n in (("rank16", 16), ("rank30", 30)):
        model = data[family]
        literal = data["literal"]["families"][family]
        u, v = dense(model["correction_U"], n), dense(model["correction_V"], 112)
        need(dyadic(u) and dyadic(v), "Both actual factors are dyadic")
        b = mm(v, u)
        g = [[x + F(i == j) for j, x in enumerate(row)] for i, row in enumerate(b)]
        uv = mm(u, v)
        e = [[x + F(i == j) for j, x in enumerate(row)] for i, row in enumerate(uv)]
        need(e == dense(model["response"], 112), "Actual response I+UV")
        expected = eye(n)
        if n == 16:
            for i in range(n):
                expected[i][i] = F(-6 if i < 8 else -8)
        else:
            for i in range(0, 16, 2):
                expected[i][i:i + 2] = [F(-4), F(1)]
                expected[i + 1][i:i + 2] = [F(2), F(-2)]
            for i in range(16, n):
                expected[i][i] = b[i][i]
            need(Counter(b[i][i] for i in range(16, n)) == {F(-5): 11, F(-3): 3},
                 "Actual scalar block multiplicities")
        need(b == expected, "Complete actual block matrix, including off-block zeros")
        bi, gi = inverse(b), inverse(g)
        need(mm(b, bi) == mm(bi, b) == eye(n) and
             mm(g, gi) == mm(gi, g) == eye(n), "Both matrix inverse orders")
        targets = {"B0": b, "B0_inverse": bi, "G0": g, "G0_inverse": gi}
        checks = {}
        for label, target in targets.items():
            if label in ("B0", "G0"):
                need(target == [[F(x) for x in row] for row in literal[label]],
                     "Published constant matrix")
            word = literal["words"][label]
            target_full = eye(n + 2)
            target_full[:n] = [row + [F(0), F(0)] for row in target]
            rows, bounds = replay(word, n)
            need(rows == reverse_replay(word, n) == target_full, "Both scalar replay directions")
            counts = Counter(gate[0] for gate in word)
            if n == 16:
                need(not counts["ADD"], "Every rank16 prefix is fieldwise scalar")
            cost = 8 * counts["ADD"] + 2 * (counts["SCALE2"] + counts["NEG"])
            expected_cost = (96 if label.startswith("B0") else 32) if n == 16 else (
                204 if label.startswith("B0") else 270)
            need(cost == expected_cost, "Exact old scalar invoice")
            scans = Counter((gate[0], gate[2]) for gate in word
                            if gate[0] in ("MULTIPLY_ODD", "DIVIDE_ODD"))
            expected_scans = {3: 16} if n == 16 and label.startswith("B0") else (
                {5: 16, 7: 16} if n == 16 else (
                    {3: 22, 5: 22} if label.startswith("B0") else {}))
            need({p: 2 * count for (_, p), count in scans.items()} == expected_scans,
                 "Exact separate odd scans")
            scale = 2**bounds["height"][2]
            for p in (3, 5, 7):
                scale *= p**bounds["height"][p]
            initial = [[scale * x for x in row] for row in eye(n + 2)]
            grid_result, grid_bounds = replay(word, n, initial, True)
            need(grid_result == [[scale * x for x in row] for row in target_full],
                 "Generic exact integer grid")
            valid_bounds = None
            if label.endswith("_inverse"):
                source = targets[label.removesuffix("_inverse")]
                initial = eye(n + 2)
                initial[:n] = [row + [F(0), F(0)] for row in source]
                result, valid_bounds = replay(word, n, initial, True)
                need(result == eye(n + 2), "Valid-code decode without any root scale")
            checks[label] = {"old_real_scalar_units": cost,
                             "complex_gate_counts": dict(counts),
                             "independent_field_frame_covariance": n == 16,
                             "real_odd_scans": expected_scans, "prefix": bounds,
                             "generic_grid_scale": scale, "generic_grid": grid_bounds,
                             "valid_code": valid_bounds}
        d = mm(bi, v)
        need(mm(d, u) == eye(n), "Actual constant section DJ=I")
        selected = row_minor(u)
        section = square_code(u, d, selected)
        results[family] = {"centre_dimension": n,
                           "factor_U_denominators": sorted({x.denominator for row in u for x in row}),
                           "factor_V_denominators": sorted({x.denominator for row in v for x in row}),
                           "word_checks": checks, "square_section": section}
    receipt = {"status": "PASS_INDEPENDENT_ACTUAL_CENTRE_CONSTANT_REVIEW",
               "source_pins": sources, "families": results,
               "native_calls_replayed": 0,
               "scope": "Common-chart scalar words and an algebraic square section. No source access, physical views, leases, controller, or caller admission."}
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])
    print(json.dumps({family: row["square_section"] for family, row in results.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
