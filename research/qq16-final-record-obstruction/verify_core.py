"""Independent source-bound QQ16 final-record obstruction checks.

New code: Apache-2.0; substantial OpenAI Codex assistance. The retained
QQ16 maps are credited to Ali Romman; route and centre sources retain
all upstream attribution. No predecessor executable is imported.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from itertools import combinations
from pathlib import Path
import gzip
import json
import tarfile

A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
PACKET = "research/joint-query/certificate.json.gz"
INPUT_PINS = {
    ARCHIVE: "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754",
    PACKET: "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7",
}
MEMBER_PINS = {
    "slots/local/CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    "t16/global/base/work/complex-nine-native/DATA-PHASES.json": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz": "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518",
}
PAIRS = ((0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4))
AXES = tuple(1 << j for j in range(73))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def load(root):
    raw = {}
    for name, pin in INPUT_PINS.items():
        data = (Path(root) / name).read_bytes()
        need(sha256(data).hexdigest() == pin, "source hash: " + name)
        raw[name] = data
    members = {}
    with tarfile.open(fileobj=BytesIO(raw[ARCHIVE]), mode="r:gz") as archive:
        for name, pin in MEMBER_PINS.items():
            found = [m for m in archive.getmembers() if m.name == name]
            need(len(found) == 1 and found[0].isfile(), "one regular archive member")
            data = archive.extractfile(found[0]).read()
            need(sha256(data).hexdigest() == pin, "archive member hash: " + name)
            members[name.rsplit("/", 1)[-1]] = json.loads(gzip.decompress(data) if name.endswith(".gz") else data)
    return members, json.loads(gzip.decompress(raw[PACKET]))


def plus(*terms):
    out = {}
    for coefficient, row in terms:
        for key, value in row.items():
            out[key] = out.get(key, 0) + coefficient * value
    return {key: value for key, value in out.items() if value}


def reconstruct_R(word, program):
    need((word["v"], word["R"], word["h"]) == (112, 480, 9), "source geometry")
    rows = [{p: Q(1)} if p < 112 else {} for p in range(712)]
    for event in program:
        if event == ["phase", "centers"]:
            return [[rows[c].get(p, Q(0)) for p in range(112)] for c in word["centers"]]
        if event[0] != "scalar":
            continue
        op = event[1]
        target = op[1][1] + (704 if op[1][0] == "C" else 0)
        if op[0] == "clear":
            rows[target] = {}
        elif op[0] == "scale":
            rows[target] = plus((Q(op[2], op[3]), rows[target]))
        else:
            need(op[0] in ("add", "copy"), "source scalar alphabet")
            source = op[2][1] + (704 if op[2][0] == "C" else 0)
            rows[target] = rows[source].copy() if op[0] == "copy" else plus((1, rows[target]), (Q(op[3], op[4]), rows[source]))
    raise ValueError("missing source centre cut")


def act(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def route(basis, stage):
    if stage == 0:
        return AXES
    result = []
    for vector in AXES:
        for i, local in enumerate(basis):
            swap = local ^ AXES[9 + 8 * (stage - 1) + i]
            if (vector & swap).bit_count() & 1:
                vector ^= swap
        result.append(vector)
    return tuple(result)


def gram(R, ports):
    return [[sum(R[i][p] * R[j][p] for p in ports) for j in range(8)] for i in range(8)]


def source_checks(members, packet, mutation=None):
    if mutation == "native_route_placement":
        packet = deepcopy(packet)
        first = packet["programs"]["F_1"]
        first[1][2], first[2][2] = first[2][2], first[1][2]
    R = reconstruct_R(members["CANONICAL-WORD.json.gz"], members["LOCAL-PROGRAMS.json.gz"]["forward"])
    expected = [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet["R_rows"]]
    if mutation == "centre_coefficient":
        R[0][U[0]] += 1
    need(R == expected, "operation-derived centre matrix")
    need((packet["A_ports"], packet["T_ports"], packet["U_ports"]) == (list(A), list(T), list(U)), "port partition")
    for ports, scalar in ((U, 48), (A, 4), (T, 4)):
        need(gram(R, ports) == [[Q(scalar * (i == j)) for j in range(8)] for i in range(8)], "Gram identity")
    need(all(sum(R[i][p] ** 2 for i in range(8)) == 4 for p in U), "ordinary column norm")
    phases = members["DATA-PHASES.json"]
    need(phases["m"] == 73 and len(phases["recipes"]) == 112, "actual phase dimension")
    registry = {tuple(row["owner_right_matrix_columns"]) for row in packet["map_registry"].values()}
    routes = {}
    for p, record in enumerate(phases["recipes"]):
        basis = tuple(record["idle_children"][0]["orthogonal_axes"][:8])
        need(record["port"] == p, "phase port binding")
        local = (record["q"],) + basis
        need(all(0 < v < (1 << 9) for v in local), "local chart domain")
        need(all((local[i] & local[j]).bit_count() % 2 == (i == j) for i in range(9) for j in range(9)), "local chart orthonormality")
        for s in range(9):
            columns = route(basis, s)
            need(all(act(columns, column) == AXES[i] for i, column in enumerate(columns)), "route involution")
            need(columns in registry, "route absent from native packet")
            native = packet["programs"]["F_" + str(s)]
            need(native[0][:3] == ["retained_core", "forward", s], "native forward stage")
            if s:
                event = native[p + 1]
                need(event[:2] == ["cover_map", ["L", p]], "native route field placement")
                actual = tuple(packet["map_registry"][event[2]]["owner_right_matrix_columns"])
                need(actual == columns, "native route stage/port binding")
            else:
                need(native[1][0] == "cover_sweep", "stage zero has no route prefix")
            routes[s, p] = columns
    if mutation == "relative_route_collision":
        routes[1, U[1]] = routes[1, U[0]]
    checks = []
    for s, t in PAIRS:
        labels = [tuple(act(routes[s, p], v) for v in routes[t, p]) for p in U]
        need(len(set(labels)) == len(U), "relative route collision")
        coefficient = [[sum(4 * R[i][p] * R[j][p] for p in U) for j in range(8)] for i in range(8)]
        need(coefficient == [[Q(192 * (i == j)) for j in range(8)] for i in range(8)], "cross-Gram identity coefficient")
        trace = sum(coefficient[i][i] for i in range(8))
        normalized = trace / (48 * 48)
        need(normalized == Q(2, 3), "normalized pair trace")
        checks.append({"stages": [s, t], "distinct_relative_routes": len(set(labels)),
                       "relative_routes_sha256": sha256(canonical(labels).encode()).hexdigest(),
                       "cross_gram_identity_diagonal": "192", "cross_gram_identity_trace": str(trace),
                       "projection_product_trace_per_owner": str(normalized)})
    triple_rank = Q(24 * 24, 28)
    image_rank = triple_rank - 16
    defect = 2 * image_rank - 8
    need((triple_rank, image_rank, defect) == (Q(144, 7), Q(32, 7), Q(8, 7)), "rank arithmetic")
    recipe = members["GLOBAL-TEMPLATE.json.gz"]["recipe"]
    pairs = [e["pair"] for e in recipe if e["kind"] == "local"]
    need(pairs == [0, 0, 0, 1, 1, 2, 2, 3, 3], "literal local pair binding")
    need(len(recipe) == 19, "literal recipe length")
    return {"R_columns_sha256": sha256(canonical([[int(R[k][p]) for k in range(8)] for p in range(112)]).encode()).hexdigest(),
            "centre_sha256": sha256(canonical([[str(x) for x in row] for row in R]).encode()).hexdigest(),
            "bound_native_routes": len(routes), "pair_checks": checks,
            "triples": [[0, 1, 2], [2, 3, 4]], "triple_trace_per_owner": "24",
            "triple_square_trace_per_owner": "28", "stacked_rank_lower_per_owner": str(triple_rank),
            "constrained_image_lower_per_owner": str(image_rank), "selected_defect_lower_per_owner": str(defect)}, recipe


# Formal typed linear expressions. A monomial is (ordered operator word,
# variable). Only same-stage selected inverse identities and the four
# explicitly stated ordinary-query constraints are reduced.
INVERSE = {"LA": "PA", "PA": "LA", "LT": "PT", "PT": "LT"}


def variable(name):
    return {((), name): 1}


def operated(name, expression, mutation=None):
    out = {}
    for (word, symbol), coefficient in expression.items():
        if word and name[:-1] in INVERSE and word[0] == INVERSE[name[:-1]] + name[-1]:
            out = plus((1, out), (coefficient, {(word[1:], symbol): 1}))
        elif not word and name.startswith("B"):
            zero = {("B0", "z0"), ("B2", "z0"), ("B3", "z1"), ("B4", "z1")}
            if mutation == "omit_B3_kernel":
                zero.remove(("B3", "z1"))
            if mutation == "omit_B4_kernel":
                zero.remove(("B4", "z1"))
            if (name, symbol) in zero:
                continue
            if (name, symbol) == ("B1", "z0"):
                sign = 1 if mutation == "wrong_d_sign" else -1
                out = plus((1, out), (sign * coefficient, {(("LA1",), "d"): 1}))
            elif (name, symbol) == ("B2", "z1"):
                sign = -1 if mutation == "wrong_link_sign" else 1
                out = plus((1, out), (sign * coefficient, {(("LA2",), "d"): 1}))
            else:
                out = plus((1, out), (coefficient, {((name,) + word, symbol): 1}))
        else:
            out = plus((1, out), (coefficient, {((name,) + word, symbol): 1}))
    return out


def expr_json(expression):
    return [[list(word), symbol, coefficient] for (word, symbol), coefficient in sorted(expression.items())]


def trajectory(recipe, mutation=None):
    recipe = deepcopy(recipe)
    if mutation == "wrong_local_pair":
        next(e for e in recipe if e.get("stage") == 2)["pair"] = 1
    elif mutation == "wrong_local_orientation":
        next(e for e in recipe if e.get("stage") == 2)["reverse"] = True
    elif mutation == "wrong_bridge_sign":
        next(e for e in recipe if e["kind"] == "bridge")["coefficient"] *= -1
    def op(name, v):
        return operated(name, v, mutation)
    def query(s, fields):
        return plus((1, op("B" + str(s), fields[0])), (1, op("LA" + str(s), fields[1])), (1, op("LT" + str(s), fields[2])))
    def forward(s, x, y):
        f = query(s, x)
        nx = [plus((1, x[0]), (-1, op("K" + str(s), f))),
              op("PA" + str(s), op("LT" + str(s), x[2])), op("PT" + str(s), f)]
        ny = [plus((1, y[0]), (1, nx[0]))] + [plus((1, x[j]), (1, y[j]), (-1, nx[j])) for j in (1, 2)]
        return nx, ny, f
    def backward(s, t, x, y):
        u = deepcopy(y)
        u[1] = plus((1, y[1]), (1, op("PA" + str(t), plus((1, op("B" + str(t), y[0])), (1, op("LT" + str(t), y[2]))))))
        a, b = op("LT" + str(s), x[2]), query(s, u)
        ny = [plus((1, y[0]), (1, op("K" + str(s), a))), u[1],
              plus((1, u[2]), (-1, op("PT" + str(s), plus((1, b), (11, a)))))]
        nx = [plus((1, x[0]), (-1, y[0])), plus((1, x[1]), (1, y[1]), (-1, u[1])),
              op("PT" + str(s), plus((1, b), (12, a)))]
        return nx, ny
    d, z0, z1 = map(variable, ("d", "z0", "z1"))
    sign = 1 if mutation == "wrong_initial_T_sign" else -1
    xt = plus((sign, op("PT0", op("LA0", d))))
    banks = [[[z0, d, xt], [{}, plus((-1, d)), plus((-1, xt))]],
             [[z1, {}, {}], [{}, {}, {}]]] + [[[{},{},{}], [{},{},{}]] for _ in range(2)]
    records = [op("B0", z0), op("B2", z0), op("B3", z1), op("B4", z1)]
    need(not any(records), "all 64 initial query coordinates vanish")
    histories, states = {}, []
    for index, event in enumerate(recipe):
        if mutation == "omit_negative_bridge" and event == {"kind": "bridge", "src": 1, "dst": 0, "coefficient": -1}:
            continue
        if event["kind"] == "local":
            s, k = event["stage"], event["pair"]
            need(event["reverse"] == bool(s % 2), "literal local orientation")
            x, y = banks[k]
            if event["reverse"]:
                banks[k] = list(backward(s, s + 1, x, y))
            else:
                nx, ny, histories[s] = forward(s, x, y)
                banks[k] = [nx, ny]
        elif event["kind"] == "bridge":
            i, j, c = event["src"], event["dst"], event["coefficient"]
            banks[j][0][0] = plus((1, banks[j][0][0]), (c, banks[i][0][0]))
            banks[i][1][0] = plus((1, banks[i][1][0]), (-c, banks[j][1][0]))
        else:
            need(event == {"kind": "terminal", "pairs": 4}, "literal terminal")
            for pair in banks:
                old_x, old_y = pair[0][0], pair[1][0]
                pair[0][0], pair[1][0] = old_y, plus((-1, old_x))
        if index == 1:
            need(banks[0] == [[{}, plus((-1, d)), {}], [z0, d, {}]], "post-B1 state")
        if index >= 3:
            need(not any(field for pair in banks for fields in pair for field in fields[1:]), "selected fields vanish after F2")
        states.append({"event": event, "ordinary": [expr_json(fields[0]) for pair in banks for fields in pair],
                       "selected_nonzero_blocks": sum(bool(field) for pair in banks for fields in pair for field in fields[1:])})
    need(sorted(histories) == [0, 2, 4, 6, 8] and not any(histories.values()), "all five forward histories vanish")
    need(not any(fields[1] or fields[2] for pair in banks for fields in pair), "final selected zero")
    need(not any(pair[1][0] for pair in banks), "final completed-X zero")
    need([pair[0][0] for pair in banks] == [z0, z1, {}, {}], "former-Y residual endpoints")
    if mutation == "observe_former_Y":
        need(not any(pair[0][0] for pair in banks), "former-Y is not an allowed observation")
    if mutation == "observe_B1_cut":
        need(not d, "B1-cut record detects family")
    if mutation == "observe_B1_initial":
        need(not op("B1", z0), "missing initial chart detects family")
    return {"events": states, "zero_forward_stages": sorted(histories), "zero_initial_record_coordinates_per_owner": 64,
            "initial_record_contract": [{"pair": k, "stages": [0, 2] if k == 0 else [2*k+1, 2*k+2],
                                         "source": "initial ordinary X", "coordinates_per_stage_per_owner": 8} for k in range(4)],
            "original_X0_A": expr_json(d), "final_former_Y": [expr_json(pair[0][0]) for pair in banks],
            "scope": "ordinary-only bridges; no selected interventions before complete F2; homogeneous selected-only operations after F2 preserve this family"}


def report(root):
    members, packet = load(root)
    sources, recipe = source_checks(members, packet)
    algebra = trajectory(recipe)
    rejected = []
    for mutation in ("centre_coefficient", "relative_route_collision", "native_route_placement"):
        try:
            source_checks(members, packet, mutation)
        except ValueError:
            rejected.append(mutation)
        else:
            raise ValueError("source mutation accepted: " + mutation)
    for mutation in ("wrong_initial_T_sign", "wrong_d_sign", "wrong_link_sign", "omit_B3_kernel", "omit_B4_kernel",
                     "omit_negative_bridge", "wrong_local_pair", "wrong_local_orientation", "wrong_bridge_sign",
                     "observe_former_Y", "observe_B1_cut", "observe_B1_initial"):
        try:
            trajectory(recipe, mutation)
        except ValueError:
            rejected.append(mutation)
        else:
            raise ValueError("trajectory mutation accepted: " + mutation)
    return {"status": "PASS_QQ16_FINAL_RECORD_OBSTRUCTION", "sources": sources, "trajectory": algebra,
            "rejected_controls": rejected, "claim": "actual regular-cover selected defect >= ceil(8|G|/7); no supplier or kappa claim"}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    print(json.dumps(report(root), indent=2))