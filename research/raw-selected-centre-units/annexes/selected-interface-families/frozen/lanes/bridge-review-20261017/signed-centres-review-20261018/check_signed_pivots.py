"""Check signed pivots and data-carried centre queries from exact pair data."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
HELPER = HERE.parent/"structured-centres-review-20261018/check_review.py"
SPEC = importlib.util.spec_from_file_location("review_helpers", HELPER)
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)
GEOMETRY = LANES/"controller-followthrough-20261017/partial-orthogonal/SYMMETRIC-FAMILY.json"
GEOMETRY_PIN = "77fc35b5d78f9dd53193ecb38977e31a7cb9d5c23f0e3839d39f6ea4963f04c2"
PRODUCER = LANES/"controller-followthrough-20261017/bipartite-eight-20261018"
FREEZE_PIN = "c147770b253d8b33a18ba6edb766ab505d203ba8ecd16507764d9a8c1c98e1c1"
PAYLOAD_PIN = "0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee"


def sub(matrix, rows, columns):
    return [{j:matrix[i][q] for j, q in enumerate(columns) if q in matrix[i]} for i in rows]


def inverse(matrix):
    n = len(matrix)
    left, right = [dict(row) for row in matrix], R.eye(n)
    for j in range(n):
        p = next(i for i in range(j, n) if left[i].get(j))
        left[j], left[p] = left[p], left[j]
        right[j], right[p] = right[p], right[j]
        q = left[j][j]
        left[j] = {k:v/q for k, v in left[j].items()}
        right[j] = {k:v/q for k, v in right[j].items()}
        for i in range(n):
            if i != j and left[i].get(j):
                q = left[i][j]
                R.add(left[i], left[j], -q)
                R.add(right[i], right[j], -q)
    R.need(left == R.eye(n), "Exact inverse elimination")
    return right


def dyadic(matrix):
    return all(v.denominator & (v.denominator-1) == 0 for row in matrix for v in row.values())


def block(a, b, c, d):
    n = len(a)
    return [dict(row) | {n+j:v for j, v in other.items()} for row, other in zip(a, b)] + [
        dict(row) | {n+j:v for j, v in other.items()} for row, other in zip(c, d)]


def negate(matrix):
    return [{j:-v for j, v in row.items()} for row in matrix]


def main():
    preceding = HERE.parent/"structured-centres-review-20261018/FREEZE.json"
    R.need(sha256(preceding.read_bytes()).hexdigest() == "2cd35b044728ba32db28a4babb994f8de85c1f0f98dd24a87283991e8ca3607c",
           "Frozen independent matrix and replay helper")
    R.need(sha256(HELPER.read_bytes()).hexdigest() == json.loads(preceding.read_text())["artifacts"]["check_review.py"],
           "Independent helper bytes")
    R.need(sha256(GEOMETRY.read_bytes()).hexdigest() == GEOMETRY_PIN, "Frozen pair geometry")
    g = json.loads(GEOMETRY.read_text())
    large = g["large_ports"]
    position = {v:i for i, v in enumerate(large)}
    alpha = [1, -1, 1, -1, 1, -1, 1, -1]
    k, signed, projectors = [], [{} for _ in large], []
    for sign, vertex in zip(alpha, g["vertices"]):
        row, projector = {}, [{} for _ in large]
        for pair in R.decode(vertex["pair_columns"]):
            R.need(len(pair) == 2 and all(abs(v) == 1 for v in pair.values()), "Signed pair mode")
            R.add(row, pair)
            for i, value in pair.items():
                R.add(projector[position[i]], {position[j]:value*v/2 for j, v in pair.items()})
        R.need(R.mm(projector, projector) == projector, "Vertex projector")
        projectors.append(projector)
        k.append({position[j]:v for j, v in row.items()})
        for target, source in zip(signed, projector):
            R.add(target, source, F(sign))
    total = [{} for _ in large]
    for i, projector in enumerate(projectors):
        for row, source in zip(total, projector):
            R.add(row, source)
        for other in projectors[:i]:
            R.need(R.mm(projector, other) == [{} for _ in large], "Orthogonal vertex spaces")
    R.need(total == R.eye(48), "Complete48-port mode decomposition")
    R.need(all(len(row) == 1 and abs(next(iter(row.values()))) == 1 for row in signed), "Actual signed permutation")
    R.need(R.mm(signed, signed) == R.eye(48), "Signed involution")
    kt = R.transpose(k, 48)
    ak = [{j:F(alpha[i])*v for j, v in row.items()} for i, row in enumerate(k)]
    R.need(R.mm(signed, kt) == R.transpose(ak, 48), "G Ktranspose equals Ktranspose Lambda")
    R.need(R.mm(k, kt) == [{i:F(12)} for i in range(8)], "Centre Gram")
    outer = R.mm(kt, ak)
    j, ji = [dict(row) for row in signed], [dict(row) for row in signed]
    for a, b, source in zip(j, ji, outer):
        R.add(a, source, F(-1, 2))
        R.add(b, source, F(-1, 10))
    R.need(R.mm(j, ji) == R.mm(ji, j) == R.eye(48), "Signed response inverse in both orders")
    selected_ports = [0, 7, 15, 36, 42, 46, 79, 89]
    s = [position[i] for i in selected_ports]
    t = [next(iter(signed[i])) for i in s]
    w = [i for i in range(48) if i not in s+t]
    u = t+w
    R.need(len(set(s+t)) == 16 and sub(signed, s, s) == [{} for _ in s], "Disjoint partner ports")
    ks, k_t, kw = sub(k, range(8), s), sub(k, range(8), t), sub(k, range(8), w)
    li, hi = inverse(sub(j, s, s)), inverse(sub(j, u, u))
    kti = inverse(k_t)
    R.need(dyadic(li) and dyadic(hi) and dyadic(kti), "Actual small and ordinary dyadic units")
    R.need(all(len(row) == 8 for row in kw), "Eight unit entries per ordinary residual query")
    R.need(R.determinant(ks) == R.determinant(k_t) == -4, "Selected and partner determinants")
    R.need(R.determinant(sub(j, s, s)) == R.determinant(sub(j, u, u)) == F(1, 16), "Both principal determinants")
    R.need(R.determinant(j) == 5**8, "Full48-port determinant")
    R.need(sub(ji, s, s) == [{q:v/5 for q, v in row.items()} for row in sub(j, s, s)], "Selected inverse block is L/5")

    # Apply the six operations to all40 arbitrary input columns.
    state = R.eye(40)
    def apply(matrix, fields):
        current = [dict(state[i]) for i in fields]
        for field, row in zip(fields, R.mm(matrix, current)):
            state[field] = row
    def query(sign):
        for i, row in enumerate(kw):
            for q, v in row.items():
                R.add(state[i], state[8+q], F(sign)*v)
    def scatter(sign):
        for i, row in enumerate(R.transpose(kw, 32)):
            for q, v in row.items():
                R.add(state[8+i], state[q], F(sign)*v)
    def scale(value):
        for i, sign in enumerate(alpha):
            state[i] = {q:F(sign)*value*v for q, v in state[i].items()}
    apply(k_t, list(range(8)))
    query(1)
    scale(F(-1, 2))
    apply(sub(signed, w, w), list(range(8, 40)))
    scatter(1)
    apply(R.transpose(k_t, 8), list(range(8)))
    R.need(state == sub(j, u, u), "Six-step forward gauge")
    apply(R.transpose(kti, 8), list(range(8)))
    scatter(-1)
    apply(sub(signed, w, w), list(range(8, 40)))
    scale(F(-2))
    query(-1)
    apply(kti, list(range(8)))
    R.need(state == R.eye(40), "Six-step inverse restores every arbitrary input")

    l, b, d, h = sub(j, s, s), sub(j, s, u), sub(j, u, s), sub(j, u, u)
    top = negate(l)
    for row, addend in zip(top, R.mm(R.mm(b, hi), d)):
        R.add(row, addend)
    a = block(top, negate(R.mm(b, hi)), negate(R.mm(hi, d)), hi)
    bottom = [dict(row) for row in h]
    for row, addend in zip(bottom, R.mm(R.mm(d, li), b)):
        R.add(row, addend, F(-1))
    ai = block(negate(li), negate(R.mm(li, b)), negate(R.mm(d, li)), bottom)
    R.need(R.mm(a, ai) == R.mm(ai, a) == R.eye(48), "Both data-interface inverse orders")
    R.need(dyadic(a) and dyadic(ai) and R.determinant(a) == 1, "Dyadic data interface with determinant1")

    edges = [edge for edge in g["pair_edges"] if alpha[edge["vertices"][0]] != alpha[edge["vertices"][1]]]
    R.need(len(edges) == 12, "Actual cross-sign graph")
    cover_reports, valid = [], []
    for cover in combinations(edges, 8):
        degree = Counter(v for edge in cover for v in edge["vertices"])
        if degree != {i:2 for i in range(8)}:
            continue
        adjacency = {i:[] for i in range(8)}
        for edge in cover:
            a0, a1 = edge["vertices"]
            adjacency[a0].append(a1)
            adjacency[a1].append(a0)
        unseen, components = set(range(8)), 0
        while unseen:
            components += 1
            todo = [min(unseen)]
            while todo:
                v = todo.pop()
                if v in unseen:
                    unseen.remove(v)
                    todo.extend(adjacency[v])
        count = 0
        for bits in product((0, 1), repeat=8):
            ports = sorted(edge["ports"][bit] for edge, bit in zip(cover, bits))
            indices = [position[i] for i in ports]
            value = R.determinant(sub(k, range(8), indices))
            R.need(value in (0, 2**components, -2**components), "Exact signed cycle determinant")
            if value:
                R.need(sub(signed, indices, indices) == [{} for _ in range(8)], "Every valid selected set has zero G block")
                valid.append(ports)
                count += 1
        R.need(count == 2**(8-components), "One parity condition per cycle")
        cover_reports.append(dict(edge_ports=[edge["ports"] for edge in cover], cycles=components,
                                  valid_selected_sets=count))
    R.need(len(cover_reports) == 9 and len(valid) == len({tuple(v) for v in valid}) == 960,
           "All cycle covers and distinct nonsingular selected sets")
    R.need(sha256((PRODUCER/"FREEZE.json").read_bytes()).hexdigest() == FREEZE_PIN, "New native producer freeze")
    for name, pin in json.loads((PRODUCER/"FREEZE.json").read_text())["artifacts"].items():
        R.need(sha256((PRODUCER/name).read_bytes()).hexdigest() == pin, "Frozen new artifact " + name)
    packet = R.load_gzip(PRODUCER/"BIPARTITE-EIGHT-PROGRAM.json.gz", PAYLOAD_PIN)
    old = R.load_gzip(R.STRUCTURED/"STRUCTURED-CENTRES-PROGRAM.json.gz", R.STRUCTURED_PIN)
    old_response = R.decode(old["response"])
    native_response = [{} for _ in range(112)]
    native_inverse = [{} for _ in range(112)]
    for port in range(112):
        if port in position:
            native_response[port] = {large[q]:v for q, v in j[position[port]].items()}
            native_inverse[port] = {large[q]:v for q, v in ji[position[port]].items()}
        else:
            native_response[port] = {q:-v for q, v in old_response[port].items()}
            native_inverse[port] = {q:-v/4 for q, v in old_response[port].items()}
    R.need(R.decode(packet["response"]) == native_response, "Actual new native response equals independently derived J")
    R.need(R.decode(packet["inverse"]) == native_inverse, "Actual full rational inverse formula")
    R.need(R.mm(native_response, native_inverse) == R.mm(native_inverse, native_response) == R.eye(112),
           "Full112-port inverse orders")
    R.need(R.determinant(native_response) == 2**64*5**8, "Full112-port determinant")
    core = R.load_gzip(LANES/"new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz", R.CORE_PIN)
    native_reports = {}
    for provider, item in packet["providers"].items():
        R.need(item["canonical"] == core["providers"][provider]["canonical"], "Unchanged actual canonical word")
        for direction in ("forward", "backward"):
            detail = R.native_replay(item["programs"][direction], item["canonical"],
                                     core["providers"][provider]["programs"][direction],
                                     native_response, direction == "backward")
            R.need(detail["scalar_real_primitives"] == 87360, "Actual native scalar invoice")
            native_reports[provider+"_"+direction] = detail

    def embedded(matrix, indices):
        fields = [large[q] for q in indices]
        answer = R.eye(112)
        for port, row in zip(fields, matrix):
            answer[port] = {fields[q]:v for q, v in row.items()}
        return answer
    expected_gauges = {"ordinary":embedded(h, u), "ordinary_inverse":embedded(hi, u),
                       "data":embedded(a, s+u), "data_inverse":embedded(ai, s+u)}
    gauge_reports = {}
    for name, program in packet["gauge_programs"].items():
        state, price, operations = R.eye(112), 0, Counter()
        for event in program:
            R.need(event[0] == "scalar" and event[2] == 0, "Common-frame scalar gate")
            gate = event[1]
            op, target = gate[0], gate[1]
            R.need(target[0] == "L" and 0 <= target[1] < 112, "Only existing data fields")
            price += R.scalar_price(gate)
            operations[op] += 1
            if op == "scale":
                value = F(*gate[2:4])
                state[target[1]] = {q:value*v for q, v in state[target[1]].items()}
            else:
                R.need(op == "add", "No COPY,CLEAR,or new workspace")
                source = gate[2]
                R.need(source[0] == "L" and 0 <= source[1] < 112 and source != target, "Existing distinct data source")
                R.add(state[target[1]], state[source[1]], F(*gate[3:5]))
        R.need(state == expected_gauges[name], "Literal gauge matches independent signed-pivot map on112columns")
        R.need(price == (4720 if name.startswith("data") else 1648), "Independent literal gauge invoice")
        gauge_reports[name] = dict(real_scalar_primitives=price, operations=dict(operations),
                                   arbitrary_input_columns=112, extra_owned_fields=0, native_children=0)
    report = dict(status="PASS_INDEPENDENT_SIGNED_PIVOTS", geometry_sha256=GEOMETRY_PIN,
                  signs=alpha, selected_ports=selected_ports, partner_ports=[large[i] for i in t],
                  other_ordinary_ports=[large[i] for i in w], selected_and_partner_det="-4",
                  principal_determinants="1/16", response48_determinant=5**8, data_determinant=1,
                  ordinary_arbitrary_input_columns=40, data_arbitrary_input_columns=48,
                  exact_cycle_covers=cover_reports, nonsingular_selected_sets=len(valid),
                  selected_sets_sha256=sha256(json.dumps(sorted(valid), separators=(",", ":")).encode()).hexdigest(),
                  producer_freeze_sha256=FREEZE_PIN, producer_payload_sha256=PAYLOAD_PIN,
                  native_reports=native_reports, gauge_reports=gauge_reports,
                  helper_checker_sha256=sha256(HELPER.read_bytes()).hexdigest(),
                  checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope="Exact signed pair response, native words, common-frame scalar gauges, and cycle-cover family. Physical supplier and recursive cost remain open.")
    (HERE/"SIGNED-PIVOTS.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(report["status"], "960 exact eight-port pivot sets", flush=True)


if __name__ == "__main__":
    main()
