"""Check the fixed-reader query without producer code imports."""

import argparse
from collections import Counter
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
PRODUCER = LANES / "bridge-access-20261017/row-capture-access-20261020"
UNIT = tuple(1 << i for i in range(25))
PIVOTS = (0, 27, 36, 111, 20, 7, 57, 46, 1, 3, 6, 8, 17, 18, 24, 23)
PSET = set(PIVOTS)
REUSE_PIN = "41d689596777344268bca937bb2e7fea302bfff443590aa42e46788409e563bf"
DUAL_PIN = "92ffceb625c3a97745892bb0f06a1140e9031ca3dc8085417d54cde9cc61f455"
PINS = {
    "capture": (
        "controller-followthrough-20261017/row-capture-20261020/"
        "run-normal/ROW-CAPTURE.json",
        "4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7",
    ),
    "native": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
        "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
    ),
    "views": (
        "bridge-access-20261017/matched-stage-access-20261018/"
        "DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
}


def require(test, message):
    if not test:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def pinned_json(path, pin, compressed=False):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    require(digest(raw) == pin, "Pin: " + str(path))
    return json.loads(raw)


def put(row, key, value):
    value += row.get(key, F(0))
    if value:
        row[key] = value
    else:
        row.pop(key, None)


def sparse(raw):
    return [{int(j): F(v) for j, v in row.items() if F(v)} for row in raw]


def eye(n):
    return [{i: F(1)} for i in range(n)]


def matmul(a, b):
    result = []
    for row in a:
        out = {}
        for j, value in row.items():
            for k, other in b[j].items():
                put(out, k, value * other)
        result.append(out)
    return result


def invert(a):
    n = len(a)
    rows = [[a[i].get(j, F(0)) for j in range(n)]
            + [F(i == j) for j in range(n)] for i in range(n)]
    determinant = F(1)
    for j in range(n):
        p = next((i for i in range(j, n) if rows[i][j]), None)
        require(p is not None, "The pivot minor is a unit over Q")
        if p != j:
            rows[j], rows[p] = rows[p], rows[j]
            determinant = -determinant
        value = rows[j][j]
        determinant *= value
        rows[j] = [v / value for v in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                value = rows[i][j]
                rows[i] = [x - value * y for x, y in zip(rows[i], rows[j])]
    return [{j: v for j, v in enumerate(row[n:]) if v} for row in rows], determinant


def scalar_word(rows, word):
    result = [dict(row) for row in rows]
    for op, dst, src, value in word:
        value = F(value)
        if op == "scale":
            result[dst] = {j: value * v for j, v in result[dst].items()}
        else:
            require(op == "add" and src != dst, "Scalar ADD")
            for j, v in result[src].items():
                put(result[dst], j, value * v)
    return result


def apply(a, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= a[bit.bit_length() - 1]
        vector ^= bit
    return result


@cache
def product(a, b):
    return tuple(apply(a, x) for x in b)


def transpose(a):
    return tuple(sum(((a[j] >> i) & 1) << j for j in range(25))
                 for i in range(25))


def route_product(*args):
    result = UNIT
    for a in args:
        result = product(result, a)
    return result


def dot(a, b):
    return (a & b).bit_count() & 1


def chart(q):
    hole = next(i for i in range(9) if not (q >> i) & 1)
    vector = q ^ (1 << hole)
    order = list(range(9))
    order[0], order[hole] = order[hole], order[0]
    basis = tuple((1 << i) ^ (vector if (vector >> i) & 1 else 0)
                  for i in order) + UNIT[9:]
    require(basis[0] == q and product(transpose(basis), basis) == UNIT,
            "Independent port chart")
    return basis


def route(q, stage):
    if not stage:
        return UNIT
    basis = chart(q)
    swaps = [basis[j + 1] ^ UNIT[9 + 8 * (stage - 1) + j] for j in range(8)]
    return tuple(x ^ xor(v for v in swaps if dot(v, x)) for x in UNIT)


def xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


@cache
def line_phase(vector, exponent):
    exponent %= 4
    linear = tuple(exponent if (vector >> i) & 1 else 0 for i in range(25))
    quadratic = 0
    if exponent & 1:
        for i in range(25):
            if (vector >> i) & 1:
                for j in range(i + 1, 25):
                    if (vector >> j) & 1:
                        quadratic ^= 1 << (25 * i + j)
    return linear, quadratic


ZERO_PHASE = ((0,) * 25, 0)


def add_phase(a, b):
    return tuple((x + y) % 4 for x, y in zip(a[0], b[0])), a[1] ^ b[1]


def minus_phase(a):
    return tuple(-x % 4 for x in a[0]), a[1]


def sum_phase(terms):
    result = ZERO_PHASE
    for vector, exponent in terms:
        result = add_phase(result, line_phase(vector, exponent))
    return result


@cache
def full_phase(level, a=UNIT):
    return sum_phase((a[j], 1) for j in range(9 + 8 * level))


def phase_translation(phase):
    require(phase[1] == 0 and all(x % 2 == 0 for x in phase[0]),
            "The phase difference is a translation")
    return sum((x // 2) << i for i, x in enumerate(phase[0]))


def routed_matrix(rows, targets, stage, routes):
    return [{(r, product(routes[stage, p], routes[stage, r])): value
             for r, value in row.items()}
            for p, row in zip(targets, rows)]


def multiply_routed(a, b):
    result = []
    for row in a:
        out = {}
        for (j, ra), value in row.items():
            for (k, rb), other in b[j].items():
                put(out, (k, product(ra, rb)), value * other)
        result.append(out)
    return result


def real_price(op, value):
    value = F(value)
    numerator, denominator = abs(value.numerator), value.denominator
    require(numerator and denominator & (denominator - 1) == 0, "Dyadic coefficient")
    if op == "scale":
        require(numerator & (numerator - 1) == 0, "Dyadic unit scale")
        return 2 * (abs(numerator.bit_length() - denominator.bit_length()) + (value < 0))
    return 2 * (3 + numerator.bit_length() - 1 + numerator.bit_count()
                + denominator.bit_length() - 1)


def replay(operations, dual=False):
    rows = [{(i, UNIT): F(1)} for i in range(640)]
    bounds = [F(1)] * 640
    grid = [0] * 640
    peak, height = F(1), 0
    exact_peak, exact_height = F(1), 0
    norm_witness = None
    height_witness = None
    bill = Counter()
    for index, (op, dst, src, value) in enumerate(operations):
        if op == "map":
            rows[dst] = {(j, product(value, a)): c for (j, a), c in rows[dst].items()}
            bill["maps"] += 1
            continue
        if dual and op == "add":
            dst, src, value = src, dst, -value
        elif dual and op == "scale":
            value = 1 / value
        bill["real_scalar"] += real_price(op, value)
        if op == "scale":
            rows[dst] = {j: value * v for j, v in rows[dst].items()}
            bounds[dst] *= abs(value)
            grid[dst] = max(0, grid[dst] + value.denominator.bit_length()
                            - abs(value.numerator).bit_length())
        else:
            for j, v in rows[src].items():
                put(rows[dst], j, value * v)
            bounds[dst] += abs(value) * bounds[src]
            grid[dst] = max(grid[dst], grid[src] + value.denominator.bit_length() - 1)
        peak, height = max(peak, bounds[dst]), max(height, grid[dst])
        current_norm = sum(abs(v) for v in rows[dst].values())
        current_height = max((v.denominator.bit_length() - 1 for v in rows[dst].values()),
                             default=0)
        if current_norm > exact_peak:
            exact_peak = current_norm
            norm_witness = {"event_index": index, "target": dst,
                            "coefficient_terms": len(rows[dst]),
                            "coefficient_census": dict(Counter(str(c) for c in rows[dst].values()))}
        if current_height > exact_height:
            exact_height = current_height
            (origin, a), coefficient = next(
                (key, c) for key, c in rows[dst].items()
                if c.denominator.bit_length() - 1 == current_height)
            height_witness = {"event_index": index, "target": dst,
                              "origin": origin, "route": a, "coefficient": str(coefficient)}
    return rows, dict(bill), peak, height, {
        "coefficient_row_sum_peak": str(exact_peak),
        "coefficient_binary_height": exact_height,
        "norm_witness": norm_witness, "height_witness": height_witness}


def isolation(word, ports):
    selected = {112 + p for p in PIVOTS}
    frames = list(word["start"])
    require(len(frames) == len(word["final"]) == 640, "All literal input fields")
    require(set(word["frames"][1]) == set(UNIT[:9]), "Literal local FULL frame")
    require(all(word["frames"][frames[p]] == [ports[p]] for p in range(112)),
            "The literal source lines are the actual model ports")
    for p in PIVOTS:
        frames[112 + p] = frames[p]
    initial = list(frames)
    count = Counter()
    native = Counter()
    last_x = None
    for i, event in enumerate(word["events"]):
        op = event[0]
        dst = event[1] if op == "native" else event[1][1]
        if dst < 112:
            last_x = i
        if dst in selected:
            count["removed_" + op] += 1
            if op == "native":
                require(event[4] == 1, "Removed selected children have rank one")
            continue
        if op == "native":
            _, dst, old, new, rank, _ = event
            require(frames[dst] == old, "Retained native frame")
            frames[dst] = new
            native[rank] += 1
        else:
            require(op == "scalar", "Retained event kind")
            _, (kind, dst, src, coefficient), frame = event
            require(src not in selected, "The retained word does not read selected Y")
            require(frames[dst] == frame and (src is None or frames[src] == frame),
                    "Retained scalar frames")
            require(not (dst < 112 and src is not None and src >= 112),
                    "The source word does not read target fields")
            count["retained_scalar"] += real_price(kind, F(coefficient))
    require(count == {"removed_native": 128, "removed_scalar": 122,
                      "retained_scalar": 6456}, "Native deletion and scalar invoice")
    require(last_x == 2638 and len(word["events"]) == 2640, "The complete source cut")
    require(all(frames[p] == 1 for p in range(112)), "All source fields are FULL")
    require(all(frames[t] == initial[t] for t in selected), "Selected Q fields are retained")
    require(all(frames[i] == word["final"][i] for i in range(640) if i not in selected),
            "Other final frames")
    require(all(word["start"][i] == word["final"][i] for i in range(224, 640)),
            "Outside frame endpoints")
    require(native == {1: 1392, 2: 64, 3: 48}, "Retained child census")
    native[8] += 16
    require(sum(k * n for k, n in native.items()) == 1792, "Prospective native mass")
    return {"deletion": dict(count), "last_source_event": last_x,
            "prospective_native_profile": dict(native), "prospective_native_mass": 1792}


def general_reader_example():
    t = [{1: F(1)}, {0: F(1)}]
    w = [{0: F(1), 1: F(1)}, {1: F(1)}]
    b = [{0: F(2), 1: F(1)}, {0: F(-1)}]
    a = [{0: F(-1)}, {1: F(1)}]
    selected_e = [{}, {1: F(2)}]
    m = matmul(w, selected_e)
    computed_selected = eye(2)
    for row, correction in zip(computed_selected, a):
        for j, value in correction.items():
            put(row, j, value)
    require(computed_selected == selected_e and not selected_e[0] and bool(selected_e[1]),
            "The selected response is nonzero and singular")
    require(matmul(w, t) != matmul(t, w), "The general reader example does not commute")

    def mv(matrix, vector):
        return [sum(value * vector[j] for j, value in row.items()) for row in matrix]

    def add(left, right, sign=1):
        return [x + sign * y for x, y in zip(left, right)]

    wrong_copy = False
    for column in range(6):
        initial = [F(i == column) for i in range(6)]
        xp, xr, z = initial[:2], initial[2:4], initial[4:]
        ex_p = add(mv(selected_e, xp), mv(matmul(a, t), xr))
        desired = add(z, add(mv(w, ex_p), mv(b, xr)))
        z = add(z, mv(b, xr))
        z = add(z, mv(w, xp))
        changed = add(xp, mv(t, xr))
        z = add(z, mv(w, changed), -1)
        z = add(z, mv(m, changed))
        restored = add(changed, mv(t, xr), -1)
        require(restored == xp and z == desired, "The arbitrary-reader six-step identity")
        wrong = add(initial[4:], mv(b, xr))
        wrong = add(wrong, xp)
        wrong = add(wrong, changed, -1)
        wrong = add(wrong, mv(m, changed))
        wrong_copy |= wrong != desired
    require(wrong_copy, "A nonidentity W cannot be replaced by two plain copies")
    return {"arbitrary_input_columns": 6, "E_is_singular": True,
            "E_selected_block_is_nonzero": True, "W_and_B_t_do_not_commute": True,
            "plain_copy_negative_control": "fails"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "normal")
    args = parser.parse_args()
    frozen = pinned_json(PRODUCER / "REUSE-FREEZE.json", REUSE_PIN)
    for name, pin in frozen["files"].items():
        require(digest((PRODUCER / name).read_bytes()) == pin, "Producer file: " + name)
    formation = pinned_json(PRODUCER / "FREEZE.json", frozen["formation_freeze_sha256"])
    for name, pin in formation["files"].items():
        require(digest((PRODUCER / name).read_bytes()) == pin, "Formation file: " + name)
    dual = pinned_json(PRODUCER / "DUAL-FREEZE.json", DUAL_PIN)
    require(digest((PRODUCER / "DUAL.md").read_bytes()) == dual["proof_sha256"],
            "The dual proof pin")
    require(dual["reuse_freeze_sha256"] == REUSE_PIN, "The dual dependency pin")
    sources = {name: pinned_json(LANES / path, pin, path.endswith(".gz"))
               for name, (path, pin) in PINS.items()}
    capture, native, views = (sources[k] for k in ("capture", "native", "views"))
    emitted = json.loads((PRODUCER / "reuse-normal/REUSE-PROGRAM.json").read_bytes())
    require(tuple(capture["pivots"]) == tuple(emitted["pivots"]) == PIVOTS, "Pivots")
    model = native["model"]
    e, u, v = (sparse(model[k]) for k in ("response", "correction_U", "correction_V"))
    expected_e = eye(112)
    for row, correction in zip(expected_e, matmul(u, v)):
        for j, value in correction.items():
            put(row, j, value)
    require(e == expected_e == sparse(capture["response"]), "The actual E = I + UV")
    vp = [{j: row[p] for j, p in enumerate(PIVOTS) if p in row} for row in v]
    vpi, vp_det = invert(vp)
    reader = matmul(vpi, v)
    require(reader == sparse(capture["centre_reader"]), "Independent reader derivation")
    require(all({j: value for j, value in row.items() if j in PSET} == {p: F(1)}
                for row, p in zip(reader, PIVOTS)), "LJ = I")
    require(all(not (set(e[p]) & PSET) for p in PIVOTS), "E[P,P] = 0")
    a = [{j: e[i].get(p, F(0)) - F(i == p)
          for j, p in enumerate(PIVOTS) if e[i].get(p, F(0)) != F(i == p)}
         for i in range(112)]
    reconstructed_e = eye(112)
    for row, correction in zip(reconstructed_e, matmul(a, reader)):
        for j, value in correction.items():
            put(row, j, value)
    require(reconstructed_e == e, "E = I + A L")
    code = eye(112)
    inverse = eye(112)
    for p, row in zip(PIVOTS, reader):
        code[p] = dict(row)
        for r, value in row.items():
            if r != p:
                inverse[p][r] = -value
    require(code == sparse(capture["code"]) and inverse == sparse(capture["code_inverse"]),
            "Independent capture maps")
    require(matmul(code, inverse) == matmul(inverse, code) == eye(112), "Both inverse orders")
    for key, target in (("scalar_word", code), ("inverse_scalar_word", inverse)):
        require(scalar_word(eye(112), capture[key]) == target, "Literal capture word: " + key)
        require(sum(real_price(op, F(c)) for op, _, _, c in capture[key]) == 1760,
                "Capture price: " + key)
        require(all(dst in PSET and (src is None or src not in PSET)
                    for _, dst, src, _ in capture[key]), "Complement-only capture word")
    provider_checks = {name: isolation(value["forward"], model["ports"])
                       for name, value in native["providers"].items()}
    records = {(r["stage"], r["port"]): r for r in views["entries"]}
    require(set(records) == {(s, p) for s in range(3) for p in range(112)},
            "All actual D25 views")
    routes = {}
    phase_checks = Counter()
    for (stage, p), record in records.items():
        q = model["ports"][p]
        require(record["q"] == q, "Actual native q")
        rho = route(q, stage)
        routes[stage, p] = rho
        require(rho == tuple(record["route_columns"]), "Independent D25 route")
        require(product(rho, rho) == UNIT and transpose(rho) == rho
                and apply(rho, q) == q, "Route properties")
        align = record["literal_stage_alignment"]
        for level in range(stage, 3):
            actual = add_phase(full_phase(level, rho), line_phase(align["exit_X"], 2))
            require(actual == full_phase(level), "Past-reader FULL view")
            phase_checks["full_views"] += 1
        require(align["exit_X"] == align["exit_Y"], "Equal physical output translations")
        if stage:
            exterior = sum_phase((UNIT[j], 1) for j in range(9, 9 + 8 * stage))
            for name in ("entry_X", "entry_Y"):
                actual = add_phase(full_phase(stage - 1, rho),
                                   line_phase(apply(rho, align[name]), 2))
                expected = add_phase(exterior, line_phase(q, 1))
                require(actual == expected and actual != exterior,
                        "An adjacent physical FULL entry has the positive intrinsic line")
                phase_checks["adjacent_full_to_Q"] += 1
            ordinary = add_phase(actual, line_phase(q, -1))
            require(ordinary == exterior, "An adjacent hole entry has the identity type")
            phase_checks["adjacent_hole_to_I"] += 1
    carrier_checks = []
    for rec in emitted["carrier_recipes"]:
        p, q = rec["port"], model["ports"][rec["port"]]
        basis = tuple(rec["basis_columns"])
        expected_basis = chart(q)[1:9] + chart(q)[:1] + UNIT[9:]
        require(basis == expected_basis and rec["q"] == q and rec["rank"] == 8,
                "Actual H8 carrier basis")
        require(tuple(rec["inverse_columns"]) == transpose(basis)
                and product(transpose(basis), basis) == UNIT, "Carrier orthogonality")
        desired = add_phase(full_phase(0), line_phase(q, -1))
        implemented = add_phase(sum_phase((b, 1) for b in basis[:8]),
                                line_phase(rec["output_translation"], 2))
        require(implemented == desired, "Exact H8 carrier phase")
        require(implemented != add_phase(full_phase(0), line_phase(q, 1)),
                "Negative control: the opposite intrinsic sign fails")
        carrier_checks.append({"port": p, "q": q, "translation": rec["output_translation"]})
    require({c["port"] for c in carrier_checks} == PSET, "All sixteen carriers")
    pair_checks = []
    for pair in emitted["pairs"]:
        s, t = pair["reader_stage"], pair["service_stage"]
        ls = routed_matrix(reader, PIVOTS, s, routes)
        lt = routed_matrix(reader, PIVOTS, t, routes)
        et = routed_matrix(e, range(112), t, routes)
        direct = multiply_routed(ls, et)
        middle = [{key: value for key, value in row.items() if key[0] in PSET}
                  for row in direct]
        require(sum(map(len, direct)) == 3808 and sum(map(len, middle)) == 696,
                "Independent owner-path counts")
        prefix = 9 + 8 * t
        route_table = pair["middle_routes"]
        for record in route_table:
            a, ai = tuple(record["columns"]), tuple(record["inverse_columns"])
            require(ai == transpose(a) and product(a, ai) == product(ai, a) == UNIT,
                    "The source map inverse")
            require(a[prefix:] == UNIT[prefix:], "Every uncompleted axis is fixed")
            delta = phase_translation(add_phase(full_phase(t), minus_phase(full_phase(t, a))))
            reverse_delta = phase_translation(
                add_phase(full_phase(t), minus_phase(full_phase(t, ai))))
            require(record["FULL_translation"] == delta
                    and record["inverse_FULL_translation"] == reverse_delta
                    and reverse_delta == apply(ai, delta), "Complete map and inverse phases")
        for label, stage in (("old_reader_views", s), ("current_code_views", t)):
            require({rec["port"] for rec in pair[label]} == set(range(112)), "All FULL views")
            for rec in pair[label]:
                require(tuple(rec["route_columns"]) == routes[stage, rec["port"]]
                        and rec["translation"] ==
                        records[stage, rec["port"]]["literal_stage_alignment"]["exit_X"],
                        "Emitted FULL view")
        require(pair["old_reader_view_ports"] ==
                {"X": sorted(set(range(112)) - PSET), "Y": list(PIVOTS)}, "Old reader fields")
        operations = []
        part_invoices = []

        def scalar(op, dst, src, coefficient):
            operations.append((op, dst, src, F(coefficient)))

        def maps(stage, ports, offset):
            for p in ports:
                operations.append(("map", offset + p, None, routes[stage, p]))

        def mark(name, begin):
            part = operations[begin:]
            part_invoices.append({
                "part": name,
                "maps": sum(op == "map" for op, _, _, _ in part),
                "real_scalar": sum(real_price(op, value) for op, _, _, value in part
                                   if op != "map"),
            })

        begin = len(operations)
        ordinary = sorted(set(range(112)) - PSET)
        maps(s, ordinary, 0)
        maps(s, PIVOTS, 112)
        for op, p, r, value in capture["scalar_word"]:
            scalar(op, 112 + p, r, value)
        maps(s, ordinary, 0)
        maps(s, PIVOTS, 112)
        mark("old_complement", begin)
        begin = len(operations)
        for p in PIVOTS:
            scalar("add", 112 + p, p, 1)
        mark("first_copy", begin)
        begin = len(operations)
        maps(t, range(112), 0)
        for op, p, r, value in capture["scalar_word"]:
            scalar(op, p, r, value)
        maps(t, range(112), 0)
        mark("current_code", begin)
        begin = len(operations)
        for p in PIVOTS:
            scalar("add", 112 + p, p, -1)
        mark("second_copy", begin)
        begin = len(operations)
        middle_rows = [{} for _ in PIVOTS]
        pindex = {p: i for i, p in enumerate(PIVOTS)}
        integer_census = Counter()
        for op, p, r, value, route_id in pair["middle_query"]:
            value = F(value)
            if op == "scale":
                require(r is None and route_id is None, "Middle scale format")
                middle_rows[pindex[p]] = {
                    key: value * v for key, v in middle_rows[pindex[p]].items()}
                scalar(op, 112 + p, None, value)
            else:
                require(op == "mapped_add_restore" and p in PSET and r in PSET,
                        "The middle query reads existing centres")
                require(value.denominator == 1, "The middle ADD is integral")
                integer_census[str(value)] += 1
                a = tuple(route_table[route_id]["columns"])
                ai = tuple(route_table[route_id]["inverse_columns"])
                put(middle_rows[pindex[p]], (r, a), value)
                operations.append(("map", r, None, a))
                scalar("add", 112 + p, r, value)
                operations.append(("map", r, None, ai))
        require(middle_rows == middle, "The emitted middle query equals the independent product")
        mark("middle", begin)
        begin = len(operations)
        maps(t, range(112), 0)
        for op, p, r, value in capture["inverse_scalar_word"]:
            scalar(op, p, r, value)
        maps(t, range(112), 0)
        mark("current_inverse", begin)
        actual, bill, peak, height, exact_prefix = replay(operations)
        expected = [{(i, UNIT): F(1)} for i in range(640)]
        for p, row in zip(PIVOTS, direct):
            for key, value in row.items():
                put(expected[112 + p], key, value)
        require(actual == expected, "All 640 arbitrary input columns of the complete query")
        require(bill == {"maps": 2064, "real_scalar": 11168}
                and peak == 972 and height == 3, "Independent complete query invoice and bounds")
        require(exact_prefix["coefficient_row_sum_peak"] == "448"
                and exact_prefix["coefficient_binary_height"] == 2,
                "Sharper forward bounds at emitted gate boundaries")
        actual_dual, dual_bill, dual_peak, dual_height, exact_dual_prefix = replay(
            operations, dual=True)
        expected_dual = [{(i, UNIT): F(1)} for i in range(640)]
        for p, row in zip(PIVOTS, direct):
            for (r, a), value in row.items():
                put(expected_dual[r], (112 + p, transpose(a)), -value)
        require(actual_dual == expected_dual, "All 640 input columns of the literal late dual query")
        require(dual_bill == bill, "The dual query keeps the invoice")
        require(exact_dual_prefix["coefficient_row_sum_peak"] == "43/2"
                and exact_dual_prefix["coefficient_binary_height"] == 3,
                "Sharper dual bounds at emitted gate boundaries")
        unordered = [{} for _ in PIVOTS]
        for row_index, (p, row) in enumerate(zip(PIVOTS, reader)):
            for j, value in row.items():
                for r, other in e[j].items():
                    wrong = route_product(routes[s, p], routes[t, j],
                                          routes[s, j], routes[t, r])
                    put(unordered[row_index], (r, wrong), value * other)
        if s:
            require(unordered != direct, "Negative control: inner stage factors cannot commute")
        first_map = next((record for record in route_table
                          if tuple(record["columns"]) != tuple(record["inverse_columns"])), None)
        require(first_map is not None, "Negative control has a noninvolutive map")
        require(product(tuple(first_map["columns"]), tuple(first_map["columns"])) != UNIT,
                "Negative control: repeat of the forward source map does not restore")
        pair_checks.append({
            "reader_stage": s, "physical_level_before_service": t - 1, "service_stage": t,
            "direct_paths": sum(map(len, direct)), "selected_paths": sum(map(len, middle)),
            "distinct_middle_maps": len(route_table),
            "middle_integer_census": dict(integer_census), "parts": part_invoices,
            "query_invoice": bill, "triangle_prefix_bound": str(peak), "binary_height_bound": height,
            "exact_prefix": exact_prefix,
            "all_input_columns": 640, "unchanged_outside_fields": 416,
            "dual_query_all_input_columns": 640,
            "dual_triangle_prefix_bound": str(dual_peak), "dual_binary_height_bound": dual_height,
            "dual_exact_prefix": exact_dual_prefix,
            "ordered_factor_negative_control": "fails" if s else "stage zero is identity",
            "wrong_inverse_map_negative_control": "fails",
        })
    require({(r["reader_stage"], r["service_stage"]) for r in pair_checks} ==
            {(0, 1), (0, 2), (1, 2)}, "All three pairs")
    output = {
        "status": "PASS_INDEPENDENT_FIXED_READER_QUERY_AND_TYPED_DUAL",
        "checker_sha256": digest(Path(__file__).read_bytes()),
        "producer_reuse_freeze_sha256": REUSE_PIN,
        "producer_dual_freeze_sha256": DUAL_PIN,
        "source_pins": PINS, "pivot_minor_determinant": str(vp_det),
        "providers": provider_checks, "phase_checks": dict(phase_checks),
        "H8_carriers": carrier_checks, "pairs": pair_checks,
        "general_reader_example": general_reader_example(),
        "producer_code_imported": False,
        "complete_native_integration_checked": False,
        "complete_supplier_claimed": False,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(output, indent=2, sort_keys=True) + "\n").encode()
    (args.output / "REVIEW-CHECKS.json").write_bytes(raw)
    print(output["status"])
    print(digest(raw))


if __name__ == "__main__":
    main()
