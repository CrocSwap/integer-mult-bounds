#!/usr/bin/env python3
"""Exact finite check of the QQ16 F0/B_1_2 coordinate-cut decoder.

Direct implementation of Ali Romman's pinned conserved contract (PR1969).
Question/J from Gareth Davidson's PR2432; commdata2338's PR2384 Model was
consulted, not imported or vendored. Apache-2.0; OpenAI Codex assistance.
Functions below are rational sums of bit_0(d*v), constant in payload.
"""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
from pathlib import Path
import platform
import tarfile
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
PACKET = "research/joint-query/certificate.json.gz"
PINS = {
    ARCHIVE: "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754",
    PACKET: "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7",
    "research/joint-query/evidence/CONSERVED-QQ16.md":
        "60f0de3a7205ba5046b5ae7ffa8bf2b1ea42ea46b498face0a77966b59e7f3fb",
    "research/joint-query/evidence/JOINT-QUERY-TRANSFER.md":
        "9e13e73ebf3192a6548798c2f1d13bd4d83957e8db0dc34de12b1a5311a52a75",
    "research/joint-query/evidence/QQ16-COVER-ACTION-ADDENDUM.md":
        "4bb4a68d8b4811b6d8364150612056bc124d38f1974d6f603dae68a99c4682fb",
}
MEMBERS = {
    "t16/global/base/work/complex-nine-native/DATA-PHASES.json":
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz":
        "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518",
}
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
J = (1, 2, 3, 4, 5, 6, 8, 12)
S = tuple(p for p in U if p not in J)
IDENTITY = tuple(1 << i for i in range(73))
FAULTS = ("wrong_C_sign", "omit_future_T_subtraction", "omit_y1_A_subtraction",
          "omit_forward_K_correction", "route_inverse_before_R_inverse")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(data, digest, label):
    require(hashlib.sha256(data).hexdigest() == digest, "source hash mismatch: " + label)
    return data


def load_sources():
    raw = {path: authenticate((ROOT / path).read_bytes(), pin, path)
           for path, pin in PINS.items()}
    decoded = []
    with tarfile.open(fileobj=io.BytesIO(raw[ARCHIVE]), mode="r:gz") as archive:
        for name, pin in MEMBERS.items():
            matches = [member for member in archive if member.name == name]
            require(len(matches) == 1 and matches[0].isfile(), "unique regular member: " + name)
            data = authenticate(archive.extractfile(matches[0]).read(), pin, name)
            decoded.append(json.loads(gzip.decompress(data) if name.endswith(".gz") else data))
    return json.loads(gzip.decompress(raw[PACKET])), *decoded


def act(columns, vector):
    value = 0
    while vector:
        bit = vector & -vector
        value ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return value


def linear(coefficients, functions):
    out = {}
    for c, function in zip(coefficients, functions, strict=True):
        if c:
            for v, a in function.items():
                out[v] = out.get(v, Q(0)) + c * a
    return {v: a for v, a in out.items() if v and a}


def add(a, b, scale=1):
    return linear((1, scale), (a, b))


def route(function, columns):
    # An invertible owner map permutes vector labels; it is not a payload map.
    return {act(columns, v): a for v, a in function.items()}


def evaluate(function, owner):
    return sum((a * (act(owner, v) & 1) for v, a in function.items()), Q(0))


def multiply(a, b):
    return [[sum((x * y for x, y in zip(row, col, strict=True)), Q(0))
             for col in zip(*b, strict=True)] for row in a]


def inverse(matrix):
    n = len(matrix)
    rows = [list(row) + [Q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        require(pivot is not None, "singular R_J")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [v / divisor for v in rows[col]]
        for i in range(n):
            if i != col:
                c = rows[i][col]
                rows[i] = [v - c * w for v, w in zip(rows[i], rows[col], strict=True)]
    return [row[n:] for row in rows]


def bind_routes(packet, phases, template):
    require(phases["m"] == 73 and len(phases["recipes"]) == 112, "route dimensions")
    require(template["recipe"][:2] == [
        {"kind": "local", "pair": 0, "reverse": False, "stage": 0},
        {"kind": "local", "pair": 0, "reverse": True, "stage": 1}], "first two events")
    for case, orientation, stage in (("F_0", "F", 0), ("B_1_2", "B", 1)):
        parameters = packet["case_parameters"][case]
        require(parameters["orientation"] == orientation and parameters["stage"] == stage,
                "case binding: " + case)
    require(packet["case_parameters"]["B_1_2"]["future"] == 2, "future chart")
    require(packet["case_parameters"]["F_0"]["explicit_cover_maps"] == 0, "D_0 = I")
    program = packet["programs"]["B_1_2"]
    sweeps = {e[1]: i for i, e in enumerate(program) if e[0] == "cover_sweep"}
    require(list(sweeps) == ["future_E_t", "Y_U_from_X_T", "eight_unsigned_swaps",
                             "Y_T_query_subtract"], "ordered B1 sweep binding")
    forward = {(0, p): IDENTITY for p in range(112)}
    backward = dict(forward)
    bindings = []
    for p, recipe in enumerate(phases["recipes"]):
        basis = recipe["idle_children"][0]["orthogonal_axes"][:8]
        local = [recipe["q"], *basis]
        require(recipe["port"] == p and len(local) == 9, "port chart binding")
        require(all(0 < v < 512 for v in local), "local nine-axis support")
        require(all(((v & w).bit_count() % 2) == (i == j)
                    for i, v in enumerate(local) for j, w in enumerate(local)), "local chart Gram")
        entries = [(i, e[2]) for i, e in enumerate(program)
                   if e[0] == "cover_map" and e[1] == ["L", 112 + p]]
        require(len(entries) == 4, "four actual Y alignment maps")
        positions = [i for i, _ in entries]
        require(positions[0] < sweeps["future_E_t"] < positions[1] < positions[2]
                < sweeps["Y_U_from_X_T"] < sweeps["Y_T_query_subtract"] < positions[3],
                "actual alignment/inverse order")
        for stage, offset in ((2, 0), (1, 2)):
            names = [entries[offset + i][1] for i in range(2)]
            maps = [packet["map_registry"][name] for name in names]
            g, h = [tuple(m["owner_right_matrix_columns"]) for m in maps]
            delta, undo = [m["payload_translation_at_identity_owner"] for m in maps]
            deltas = [b ^ (1 << (9 + 8 * (stage - 1) + i)) for i, b in enumerate(basis)]
            expected = tuple(e ^ act(deltas, sum(((e & d).bit_count() % 2) << i
                                                for i, d in enumerate(deltas))) for e in IDENTITY)
            require(g == expected and len(h) == 73, "registered port route differs from chart")
            require(all(act(g, h[i]) == act(h, g[i]) == IDENTITY[i] for i in range(73)),
                    "two-sided port route inverse")
            beta_lift = sum((((b.bit_count() - 1) // 2) % 2) << (9 + 8 * (stage - 1) + i)
                            for i, b in enumerate(basis))
            require(delta == recipe["q"] ^ beta_lift, "actual Y payload translation")
            require(delta ^ act(g, undo) == undo ^ act(h, delta) == 0,
                    "two-sided registered full-map inverse")
            forward[stage, p], backward[stage, p] = g, h
            bindings.append([stage, p, *names])
    return forward, backward, bindings


class FirstPair:
    def __init__(self, packet, phases, template):
        require(tuple(packet["A_ports"]) == A and tuple(packet["T_ports"]) == T
                and tuple(packet["U_ports"]) == U, "actual R partition")
        self.R = [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet["R_rows"]]
        require(len(self.R) == 8, "eight query coordinates")
        self.grams = {}
        for name, ports, scale in (("A", A, 4), ("T", T, 4), ("U", U, 48)):
            block = [[row[p] for p in ports] for row in self.R]
            gram = multiply(block, list(zip(*block, strict=True)))
            require(gram == [[Q(scale * (i == j)) for j in range(8)] for i in range(8)],
                    "actual Gram: " + name)
            self.grams[name] = gram
        require(len(packet["K_rows"]) == 112 and all(
            Q(packet["K_rows"][p].get(str(i), 0)) == self.R[i][p] / 4
            for p in range(112) for i in range(8)), "actual K = R^T/4")
        self.RJ = [[row[p] for p in J] for row in self.R]
        self.RJ_inverse = inverse(self.RJ)
        identity = [[Q(i == j) for j in range(8)] for i in range(8)]
        require(multiply(self.RJ, self.RJ_inverse) == multiply(self.RJ_inverse, self.RJ)
                == identity, "two-sided R_J inverse")
        self.routes, self.inverses, self.bindings = bind_routes(packet, phases, template)

    def query(self, bank, stage, ports):
        values = [route(bank[p], self.routes[stage, p]) for p in ports]
        return [linear([row[p] for p in ports], values) for row in self.R]

    def section(self, query, stage, ports):
        return {p: route(linear([row[p] / 4 for row in self.R], query), self.inverses[stage, p])
                for p in ports}

    def forward(self, x, y):
        f = self.query(x, 0, range(112))
        kf = self.section(f, 0, U + T)
        old_t = self.section(self.query(x, 0, T), 0, A)
        xx = [add(x[p], kf[p], -1) if p in U else old_t[p] if p in A else kf[p]
              for p in range(112)]
        yy = [add(y[p], xx[p]) if p in U else add(add(x[p], y[p]), xx[p], -1)
              for p in range(112)]
        return xx, yy

    def backward(self, x, y):
        logger = self.section(self.query(y, 2, U + T), 2, A)
        u = [add(y[p], logger[p]) if p in A else y[p] for p in range(112)]
        a, b = self.query(x, 1, T), self.query(u, 1, range(112))
        ku = self.section(a, 1, U)
        correction = self.section([add(bb, aa, 11) for aa, bb in zip(a, b)], 1, T)
        target = self.section([add(bb, aa, 12) for aa, bb in zip(a, b)], 1, T)
        xx = [add(x[p], y[p], -1) if p in U else add(add(x[p], y[p]), u[p], -1)
              if p in A else target[p] for p in range(112)]
        yy = [add(y[p], ku[p]) if p in U else u[p] if p in A else add(u[p], correction[p], -1)
              for p in range(112)]
        return xx, yy


def decode(model, x1_selected, y1_selected, y2_A, C, x1_read, fault=None):
    for fields, ports in ((x1_selected, A + T), (y1_selected, A + T),
                          (y2_A, A), (C, U), (x1_read, S)):
        require(set(fields) == set(ports), "decoder observation boundary")
    require(fault is None or fault in FAULTS, "unknown control")
    f = model.query(x1_selected, 0, T)
    t = model.section(model.query(x1_selected, 0, A), 0, T)
    baseline = 0 if fault == "omit_y1_A_subtraction" else -1
    q = model.query({p: add(y2_A[p], y1_selected[p], baseline) for p in A}, 2, A)
    if fault == "wrong_C_sign":
        C = {p: linear([-1], [value]) for p, value in C.items()}
    future_t, bc = model.query(y1_selected, 2, T), model.query(C, 2, U)
    v = [linear([1, 0 if fault == "omit_future_T_subtraction" else -1, 1], values)
         for values in zip(q, future_t, bc, strict=True)]
    known = model.query(x1_read, 2, S)
    rhs = [add(a, b, -1) for a, b in zip(v, known, strict=True)]
    if fault == "route_inverse_before_R_inverse":
        rhs = [route(value, model.inverses[2, p]) for p, value in zip(J, rhs, strict=True)]
    solved = [linear(row, rhs) for row in model.RJ_inverse]
    x1_U = dict(x1_read)
    for p, value in zip(J, solved, strict=True):
        x1_U[p] = value if fault == "route_inverse_before_R_inverse" else route(value, model.inverses[2, p])
    kf = model.section(f, 0, U)
    x_U = {p: x1_U[p] if fault == "omit_forward_K_correction" else add(x1_U[p], kf[p]) for p in U}
    b0, ell_t = model.query(x_U, 0, U), model.query(t, 0, T)
    x_A = model.section([linear([1, -1, -1], values) for values in zip(f, b0, ell_t)], 0, A)
    x = [x_U[p] if p in U else x_A[p] if p in A else t[p] for p in range(112)]
    y = [linear([-1], [C[p]]) if p in U else linear([1, 1, -1], [x1_selected[p], y1_selected[p], x[p]])
         for p in range(112)]
    return x, y


def observe(x1, y1, x2, y2):
    return ({p: x1[p] for p in A + T}, {p: y1[p] for p in A + T},
            {p: y2[p] for p in A}, {p: x2[p] for p in U}, {p: x1[p] for p in S})


def residual(expected, actual, owners):
    for bank, (want, got) in enumerate(zip(expected, actual, strict=True)):
        for p, (a, b) in enumerate(zip(want, got, strict=True)):
            if a != b:
                for word, owner in owners:
                    av, bv = evaluate(a, owner), evaluate(b, owner)
                    if av != bv:
                        return {"bank": "xy"[bank], "port": p, "owner_word": word,
                                "expected": str(av), "actual": str(bv), "residual": str(bv - av)}
    return None


def build_result():
    packet, phases, template = load_sources()
    model = FirstPair(packet, phases, template)
    # These are actual registered owners, not an invented full orthogonal group.
    owners = [([], IDENTITY)] + [([entry], model.routes[stage, p])
                                for stage, p, entry, _ in model.bindings if p in (0, 1)]
    base_vector = phases["recipes"][0]["idle_children"][0]["orthogonal_axes"][0]
    vectors = [base_vector ^ (1 << i) for i in (17, 18, 32, 64)]
    functions = [{v: Q(1)} for v in vectors]
    require(all(len({evaluate(f, owner) for _, owner in owners}) > 1 for f in functions),
            "basis functions must vary on registered owners")

    def replay(x, y, label):
        x1, y1 = model.forward(x, y)
        x2, y2 = model.backward(x1, y1)
        observed = observe(x1, y1, x2, y2)
        restored = decode(model, *observed)
        require(restored == (x, y), "decoder failure: " + json.dumps({
            "fixture": label, "witness": residual((x, y), restored, owners),
            "note": "a null witness means an unresolved symbolic residual, not a counterexample"}))
        return observed

    for bank in range(2):
        for p in range(112):
            inputs = [[{} for _ in range(112)] for _ in range(2)]
            inputs[bank][p] = functions[(p + 2 * bank) % 4]
            replay(*inputs, f"{'xy'[bank]}[{p}]")
    dense = [[linear([Q((-1) ** (p + bank) * (p % 7 + 1), 1 << ((p + bank) % 4)),
                      Q((-1) ** (p // 3 + bank) * (p % 5 + 1), 1 << (7 + (p + bank) % 3))],
                     [functions[(p + bank) % 4], functions[(p + bank + 1) % 4]])
              for p in range(112)] for bank in range(2)]
    require(all(evaluate(f, IDENTITY) for bank in dense for f in bank), "all 224 dense fields dirty")
    observed = replay(*dense, "dense_signed_dyadic")
    controls = {fault: residual(tuple(dense), decode(model, *observed, fault=fault), owners)
                for fault in FAULTS}
    ineffective = [fault for fault, witness in controls.items() if witness is None]
    require(not ineffective, "ineffective controls (no witnessed nonzero residual): " + str(ineffective))
    return {
        "status": "PASS_QQ16_COORDINATE_CUT_DECODER",
        "source_sha256": PINS, "archive_member_sha256": MEMBERS,
        "partition": {"A": A, "T": T, "U": U, "J": J, "S": S},
        "grams": model.grams, "R_J": model.RJ, "R_J_inverse": model.RJ_inverse,
        "two_sided_R_J_inverse": True,
        "route_bindings": model.bindings, "two_sided_registered_map_inverses": 224,
        "replayed_cases": {"port_basis_placements": 224, "dense_signed_dyadic": 1},
        "function_vectors": vectors, "owner_evaluations_per_function": len(owners),
        "negative_control_witnesses": controls, "formula_corrections": [],
        "scope": "F0/B_1_2 only; full-array observations retained across two cuts; rational owner-bit functions, constant payload",
        "limitations": ["finite function fixtures are not arbitrary-function exhaustiveness",
                        "ordered conserved contract inherited, native words not replayed",
                        "remaining 17 schedule events not replayed", "no final-only or native-cost claim"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", type=Path, help="explicitly create a new result JSON; refuses overwrite")
    args = parser.parse_args()
    started = time.perf_counter()
    result = build_result()
    encoded = json.dumps(result, default=str, sort_keys=True, indent=2) + "\n"
    if args.emit_result:
        with args.emit_result.open("x") as output:
            output.write(encoded)
    print(json.dumps({"status": result["status"], "replayed_cases": result["replayed_cases"],
                      "controls_rejected": len(result["negative_control_witnesses"]),
                      "result_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
                      "elapsed_seconds": round(time.perf_counter() - started, 3),
                      "python": platform.python_version(), "implementation": platform.python_implementation()}))


if __name__ == "__main__":
    main()
