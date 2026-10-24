"""Review the changed centre response, native words, gauges, and metric."""

import ast
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
FAMILY = LANES / "controller-followthrough-20261017"
PARTIAL = FAMILY / "partial-orthogonal"
STRUCTURED = FAMILY / "structured-centres"
CORE_PIN = "a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa"
STRUCTURED_PIN = "2b9de1454c2025ae4e230bd64de36b4f6c937628c63fc5afede6640dd3c0e1e1"
SYMMETRIC_PIN = "84e527589ab11fa59136e262c75511d9f71af1ba55504fb59b73ac789a350dff"
GAUGES_V2_PIN = "deea4844f2327a73129c213df915819ec845fb9c97a30498d43f231a2267e733"
FREEZES = {
    PARTIAL: "b3938cd51d756df996f8421742c88bd96ab8fcddc7372c373c6fcbc5048d2bf1",
    STRUCTURED: "5e762396d55ac47b34bbe60e30c62a429ddd6fc1f018cb4b4b94d3670d374a19",
}


def need(value, label):
    if not value:
        raise ValueError(label)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load_gzip(path, pin=None):
    raw = gzip.decompress(path.read_bytes())
    if pin:
        need(sha256(raw).hexdigest() == pin, "Compressed source pin")
    return json.loads(raw)


def decode(rows):
    return [{int(k): F(v) for k, v in row.items() if F(v)} for row in rows]


def add(a, b, scale=F(1)):
    for key, value in b.items():
        result = a.get(key, F(0)) + scale*value
        if result:
            a[key] = result
        else:
            a.pop(key, None)


def eye(n):
    return [{i: F(1)} for i in range(n)]


def transpose(a, columns=None):
    answer = [{} for _ in range(len(a) if columns is None else columns)]
    for i, row in enumerate(a):
        for j, value in row.items():
            answer[j][i] = value
    return answer


def mm(a, b):
    result = []
    for row in a:
        target = {}
        for j, value in row.items():
            add(target, b[j], value)
        result.append(target)
    return result


def determinant(a):
    a = [dict(row) for row in a]
    value = F(1)
    for j in range(len(a)):
        pivot = next((i for i in range(j, len(a)) if a[i].get(j)), None)
        if pivot is None:
            return F(0)
        if pivot != j:
            a[pivot], a[j] = a[j], a[pivot]
            value = -value
        value *= a[j][j]
        for i in range(j+1, len(a)):
            if a[i].get(j):
                add(a[i], a[j], -a[i][j]/a[j][j])
    return value


def scalar_price(gate):
    op = gate[0]
    if op in ("clear", "copy"):
        return 2
    coefficient = F(*gate[-2:])
    a, b = abs(coefficient.numerator), coefficient.denominator
    need(a and b & (b-1) == 0, "Nonzero dyadic scalar")
    if op == "scale":
        need(a & (a-1) == 0, "Dyadic unit SCALE")
        return 2*(abs((a.bit_length()-1)-(b.bit_length()-1)) + int(coefficient < 0))
    need(op == "add", "Scalar opcode")
    return 2*(3+(a.bit_length()-1)+a.bit_count()+(b.bit_length()-1))


def native_replay(events, word, reference, response, backward):
    size = len(word["start"])
    state = {i: {(i, ()): F(1)} for i in range(size+8)}
    frames = dict(enumerate(word["start"]+[0]*8))
    private = set()
    price, macros = 0, 0
    profile = Counter()

    def slot(token):
        if token[0] == "L":
            need(0 <= token[1] < size, "Live field range")
            return token[1]
        if token[0] == "C":
            need(0 <= token[1] < 8, "Owned field range")
            return size+token[1]
        need(token[0] == "Z", "Private field namespace")
        return ("Z", token[1])

    for event in events:
        tag = event[0]
        if tag == "scalar":
            gate, frame = event[1:]
            op, target = gate[0], slot(gate[1])
            price += scalar_price(gate)
            macros += 1
            if op == "clear":
                need(isinstance(target, int) and target >= size, "Only owned inputs are cleared")
                state[target], frames[target] = {}, frame
            else:
                need(frames[target] == frame, "Target physical frame")
                if op == "scale":
                    coefficient = F(*gate[2:4])
                    state[target] = {k: coefficient*v for k, v in state[target].items() if coefficient*v}
                else:
                    source = slot(gate[2])
                    need(target != source and frames[source] == frame, "Source physical frame")
                    if op == "copy":
                        need(isinstance(target, int) and target >= size, "Owned COPY target")
                        state[target] = dict(state[source])
                    else:
                        add(state[target], state[source], F(*gate[3:5]))
        elif tag == "climb":
            target, old, new, rank = event[2:6]
            need(frames[target] == old, "Native input frame")
            need(len(word["frames"][new])-len(word["frames"][old]) == rank, "Native rank difference")
            frames[target] = new
            profile[rank] += 1
        elif tag == "warp":
            target, op, old, new = slot(event[1]), event[2], event[3], event[4]
            need(frames[target] == old, "Warp input frame")
            frames[target] = new
            out = {}
            for (source, history), coefficient in state[target].items():
                history = history[1:] if history and history[0] == -op else (op,)+history
                add(out, {(source, history): coefficient})
            state[target] = out
        elif tag == "zero_buffer":
            target = ("Z", event[2])
            if event[1] == "alloc":
                need(target not in private, "Private zero allocation")
                private.add(target)
                state[target], frames[target] = {}, 1
            else:
                need(target in private and not state[target], "Private zero return")
                private.remove(target)
                del state[target], frames[target]
        else:
            need(tag in ("phase", "adapter", "residual_adapter"), "Known native record")
    expected = {i: {(i, ()): F(1)} for i in range(size+8)}
    for i in range(size, size+8):
        expected[i] = {}
    for i, row in enumerate(response):
        for j, value in row.items():
            target, source = (j, 112+i) if backward else (112+i, j)
            add(expected[target], {(source, ()): -value if backward else value})
    need(state == expected, "All arbitrary data, helper, and owned columns")
    need(not private and [frames[i] for i in range(size)] == word["final"], "Endpoint frame and private contract")
    need(all(frames[i] == 0 for i in range(size, size+8)), "Owned endpoint frames")
    fixed = lambda stream: [e for e in stream if e[0] not in ("scalar", "phase")]
    need(fixed(events) == fixed(reference), "Every native, adapter, and zero-buffer record is unchanged")
    phases = lambda stream: [e for e in stream if e[0] == "phase"]
    need(len(phases(events)) == len(phases(reference)) and phases(events)[1:] == phases(reference)[1:],
         "Only the first descriptive phase label changes")
    need(profile == {1:2433, 2:724, 3:228, 4:102, 5:20}, "Complete recursive child profile")
    return dict(arbitrary_input_columns=size+8, scalar_real_primitives=price, scalar_macros=macros,
                native_profile=dict(profile), native_rank_mass=sum(k*v for k, v in profile.items()),
                native_children=sum(profile.values()), borrowed_helpers_restored=size-224,
                private_zero_buffers_restored=len(word["zero_buffers"]), owned_outputs_zero=8)


def gauge_replay(events):
    state = eye(112)+[{}]
    price, query_starts = 0, 0
    for event in events:
        need(event[0] == "scalar" and event[2] == 0, "Common-frame gauge event")
        gate = event[1]
        op = gate[0]
        field = lambda token: 112 if token == ["C", 0] else token[1]
        target = field(gate[1])
        price += scalar_price(gate)
        if op == "copy":
            need(target == 112 and not state[target], "Known-zero serial owned field")
            state[target] = dict(state[field(gate[2])])
            query_starts += 1
        elif op == "scale":
            value = F(*gate[2:4])
            state[target] = {k: value*v for k, v in state[target].items() if value*v}
        else:
            need(op == "add" and target != field(gate[2]), "Gauge ADD")
            add(state[target], state[field(gate[2])], F(*gate[3:5]))
    need(not state[112] and query_starts == 8, "Eight complete queries restore C0")
    return state[:112], price


def lift(value):
    for shift in range(11):
        denominator = 1 << shift
        numerator = int(value)*denominator % 1000003
        if numerator > 500001:
            numerator -= 1000003
        if abs(numerator) <= 64:
            return F(numerator, denominator)
    raise ValueError("No declared small dyadic lift")


def symmetric_review(geometry, structured_response, centres):
    path = LANES / "oblique-native-20261017/interior-cut/SYMMETRIC-RESPONSE-SEARCH.json"
    need(digest(path) == SYMMETRIC_PIN, "Pinned symmetric family")
    data = json.loads(path.read_text())
    matrices = []
    basis = {}
    for direction in data["symmetric_directions"]:
        matrix = [{} for _ in range(112)]
        for key, value in direction["effect"].items():
            i, j = ast.literal_eval(key)
            matrix[i][j] = lift(value)
        need(transpose(matrix) == matrix and all(i not in row for i, row in enumerate(matrix)),
             "Exact symmetric zero-diagonal direction")
        row = {112*i+j: value for i, source in enumerate(matrix) for j, value in source.items()}
        while row:
            pivot = min(row)
            if pivot in basis:
                add(row, basis[pivot], -row[pivot])
            else:
                value = row[pivot]
                basis[pivot] = {k: v/value for k, v in row.items()}
                break
        need(row, "Independent symmetric direction")
        matrices.append(matrix)
    need(len(matrices) == len(basis) == 42, "Exact family dimension")
    large = set(geometry["large_ports"])
    small = set(range(112))-large
    for matrix in matrices[:32]:
        need(all((i in small and set(row) <= small) or not row for i, row in enumerate(matrix)),
             "The first32 directions have support only on the64-port block")
    factors = [F(2) if i in (0, 5) else F(-1) for i in range(8)]
    witness, formed, projectors = [{} for _ in range(112)], [{} for _ in range(112)], []
    for index, matrix in enumerate(matrices):
        if index < 32:
            weight = F(2 if index % 4 in (2, 3) else 1)
        elif index < 40:
            weight = 1/factors[index-32]
        else:
            weight = F(0)
        for dest, row in zip(formed, matrix):
            add(dest, row, weight)
        if 32 <= index < 40:
            for dest, row in zip(witness, matrix):
                add(dest, row, weight/6)
            adjacency = [{j: weight*v for j, v in row.items()} for row in matrix]
            projector = mm(adjacency, adjacency)
            for dest, row in zip(projector, adjacency):
                add(dest, row, -4)
            projector = [{j: v/5 for j, v in row.items()} for row in projector]
            need(mm(projector, projector) == projector and sum(row.get(i, 0) for i, row in enumerate(projector)) == 6,
                 "Each vertex has a rank-six range projector")
            centre = centres[index-32]
            expected = [{j: centre.get(i, 0)*v/2 for j, v in centre.items() if centre.get(i, 0)*v}
                        for i in range(112)]
            for dest, row in zip(expected, projector):
                add(dest, row, -1)
            need(expected == adjacency, "Each vertex response is its centre outer product minus its range projector")
            projectors.append(projector)
    need(formed == structured_response and witness == decode(geometry["witness"]), "Independent family and witness assembly")
    total = [{} for _ in range(112)]
    for i, projector in enumerate(projectors):
        for dest, row in zip(total, projector):
            add(dest, row)
        for other in projectors[:i]:
            need(mm(projector, other) == [{} for _ in range(112)], "Orthogonal vertex mode spaces")
    need(total == [{i: F(1)} if i in large else {} for i in range(112)], "Vertex spaces cover exactly the 48 ports")
    incidence_counts = Counter()
    # Expand each scalar polynomial directly. Off-diagonal monomials combine.
    for column in range(112):
        linear = [{} for _ in range(112)]
        for variable, matrix in enumerate(matrices):
            for row in range(112):
                if column in matrix[row]:
                    linear[row][variable] = matrix[row][column]
        polynomial = {}
        for i, row in enumerate(witness):
            for j, y in row.items():
                for a, left in linear[i].items():
                    for b, right in linear[j].items():
                        add(polynomial, {tuple(sorted((a, b))): y*left*right})
        if column in small:
            expected = {(40, 40):F(1, 6), (40, 41):F(-2, 3), (41, 41):F(7, 8)}
        else:
            incident = [i for i in range(8) if column in centres[i]]
            need(len(incident) == 2, "Two vertices per physical column")
            incidence_counts.update(incident)
            expected = {(32+i, 32+i):F(5, 3)*factors[i]**2 for i in incident}
        need(polynomial == expected, "Exact quadratic-form polynomial at each physical column")
    need(incidence_counts == {i:12 for i in range(8)}, "Every constrained centre coefficient occurs")
    need(F(7, 8)*F(1, 6)-F(1, 3)**2 == F(5, 144), "Strict positive two-by-two certificate")
    return dict(dimension=42, column_polynomials=112, positive_block_determinant="5/144",
                forced_zero_coefficients=list(range(32, 42)), sharp_rank_bound=64)


def main():
    manifest_pins = {}
    for directory, pin in FREEZES.items():
        need(digest(directory/"FREEZE.json") == pin, "Producer freeze pin")
        manifest = json.loads((directory/"FREEZE.json").read_text())
        for name, expected in manifest["artifacts"].items():
            need(digest(directory/name) == expected, "Frozen producer artifact " + name)
        manifest_pins[str(directory.relative_to(LANES))] = pin
    core = load_gzip(LANES/"new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz", CORE_PIN)
    structured = load_gzip(STRUCTURED/"STRUCTURED-CENTRES-PROGRAM.json.gz", STRUCTURED_PIN)
    partial_receipt = json.loads((PARTIAL/"PARTIAL-ORTHOGONAL.json").read_text())
    partial = load_gzip(PARTIAL/"PARTIAL-ORTHOGONAL-PROGRAM.json.gz", partial_receipt["payload_decompressed_sha256"])
    geometry = json.loads((PARTIAL/"SYMMETRIC-FAMILY.json").read_text())
    receipt = json.loads((STRUCTURED/"STRUCTURED-CENTRES.json").read_text())
    reports = {}
    for family, packet, price in (("partial", partial, 86664), ("structured", structured, 87360)):
        response = decode(packet["response"])
        detail = {}
        for provider, item in packet["providers"].items():
            need(item["canonical"] == core["providers"][provider]["canonical"], "Actual canonical source word")
            for direction in ("forward", "backward"):
                result = native_replay(item["programs"][direction], item["canonical"],
                                       core["providers"][provider]["programs"][direction],
                                       response, direction == "backward")
                need(result["scalar_real_primitives"] == price, "Independent complete scalar invoice")
                detail[provider+"_"+direction] = result
        reports[family] = detail
        expected_det = -F(2**88) if family == "partial" else F(2**64*5**8)
        need(determinant(response) == expected_det, "Independent response determinant")
        print(family, "four native words and full invoice pass", flush=True)
    e = decode(structured["response"])
    k = decode(structured["centre_rows"])
    large = sorted({p for row in k for p in row})
    small = sorted(set(range(112))-set(large))
    need(len(k) == 8 and len(large) == 48 and all(len(row) == 12 and all(abs(v) == 1 for v in row.values()) for row in k),
         "Eight signed twelve-port centre rows")
    need(mm(k, transpose(k, 112)) == [{i:F(12)} for i in range(8)], "Actual centre Gram12I")
    outer = mm(transpose(k, 112), k)
    square = mm(e, e)
    for i in range(112):
        if i in small:
            need(set(e[i]) <= set(small) and square[i] == {i:F(4)}, "Closed Hadamard response")
        else:
            expected = {j:v/2 for j, v in outer[i].items()}
            add(expected, {i:F(1)}, -1)
            need(e[i] == expected, "Exact E48 formula")
    need(e == transpose(e), "Symmetry on all 112 ports")
    inverse = decode(structured["inverse"])
    need(mm(e, inverse) == mm(inverse, e) == eye(112), "Both rational inverse orders")
    minors = receipt["orthogonal_minor_ports"]
    need(len(minors) == 6 and sorted(p for minor in minors for p in minor) == large, "Six-minor exact partition")
    for minor in minors:
        restricted = [{p:v for p, v in row.items() if p in minor} for row in k]
        need(mm(restricted, transpose(restricted, 112)) == [{i:F(2)} for i in range(8)], "Each complete minor has Gram2I")
    subsets, balanced = [], 0
    for mask in range(64):
        selected = {p for i, minor in enumerate(minors) if mask >> i & 1 for p in minor}
        ordinary = set(large)-selected
        count = mask.bit_count()
        for fields, expected in ((selected, count), (ordinary, 6-count)):
            restricted = [{p:v for p, v in row.items() if p in fields} for row in k]
            need(mm(restricted, transpose(restricted, 112)) == [{i:F(2*expected)} if expected else {} for i in range(8)],
                 "Every union of complete minors has the required Gram")
        if count in (1, 2, 3, 4):
            h, hi = eye(112), eye(112)
            for i in ordinary:
                row = {j:v for j, v in outer[i].items() if j in ordinary}
                add(h[i], row, F(-1, 2))
                add(hi[i], row, F(1, 2*(count-5)))
            need(mm(h, hi) == mm(hi, h) == eye(112), "Ordinary inverse for every valid union")
        if count in (2, 3, 4):
            signs = {i:F(-1) if i in selected else F(1) for i in range(112)}
            a = [{i:signs[i]} for i in range(112)]
            ai = [{i:signs[i]} for i in range(112)]
            for i in large:
                add(a[i], outer[i], F(1, 2*(count-5)))
                add(ai[i], {j:signs[i]*v*signs[j] for j, v in outer[i].items()}, F(1, 2*(count-1)))
            need(mm(a, ai) == mm(ai, a) == eye(112), "Data inverse for every valid union")
            if count == 3:
                need(all(value.denominator & (value.denominator-1) == 0 for matrix in (h, hi, a, ai) for row in matrix for value in row.values()),
                     "Every balanced interface is dyadic")
                kp = [{j:signs[j]*v for j, v in row.items()} for row in k]
                need(mm(kp, transpose(k, 112)) == [{} for _ in range(8)], "Balanced signed Gram is zero")
                balanced += 1
        subsets.append(dict(mask=mask, selected_minors=count, selected_ports=len(selected)))
    gauges = json.loads((STRUCTURED/"RANK8-GAUGES.json").read_text())
    gauge_maps, gauge_prices = {}, {}
    for name, program in gauges["programs"].items():
        gauge_maps[name], gauge_prices[name] = gauge_replay(program)
        need(gauge_prices[name] == gauges["reports"][name]["scalar_real_primitives"], "Independent serial gauge invoice")
    for name in ("data", "ordinary"):
        need(mm(gauge_maps[name], gauge_maps[name+"_inverse"]) == mm(gauge_maps[name+"_inverse"], gauge_maps[name]) == eye(112), "Literal gauge inverse orders")
    selected, ordinary = set(gauges["selected_ports"]), set(gauges["ordinary_ports"])
    signs = {i:F(-1) if i in selected else F(1) for i in range(112)}
    wanted = [{i:signs[i]} for i in range(112)]
    for i in large:
        add(wanted[i], outer[i], F(-1, 4))
    need(gauge_maps["data"] == wanted, "Literal data gauge equals P minus Gram/4")
    wanted = eye(112)
    for i in ordinary:
        add(wanted[i], {j:v for j, v in outer[i].items() if j in ordinary}, F(-1, 2))
    need(gauge_maps["ordinary"] == wanted, "Literal ordinary gauge equals its formula")
    need(digest(STRUCTURED/"GAUGES-V2-FREEZE.json") == GAUGES_V2_PIN, "Separate V2 gauge freeze")
    gauge_manifest = json.loads((STRUCTURED/"GAUGES-V2-FREEZE.json").read_text())
    for name, pin in gauge_manifest["artifacts"].items():
        need(digest(STRUCTURED/name) == pin, "Frozen V2 artifact " + name)
    gauges_v2 = json.loads((STRUCTURED/"RANK8-GAUGES-V2.json").read_text())
    gauge_v2_prices = {}
    for name, program in gauges_v2["programs"].items():
        actual, gauge_v2_prices[name] = gauge_replay(program)
        need(actual == gauge_maps[name], "Scaled-query V2 has the identical complete map and zero output")
        expected = 2368 if name.startswith("data") else 1172
        need(gauge_v2_prices[name] == expected == gauges_v2["reports"][name]["scalar_real_primitives"],
             "Independent V2 scalar invoice")
    metric = symmetric_review(geometry, e, k)
    report = dict(status="PASS_INDEPENDENT_STRUCTURED_CENTRE_REVIEW", producer_freezes=manifest_pins,
                  source_core_decompressed_sha256=CORE_PIN, structured_payload_sha256=STRUCTURED_PIN,
                  native_programs=reports, centre_gram="12I8", centre_support_ports=large,
                  complete_minor_gram="2I8", all_minor_subsets=subsets, balanced_dyadic_subsets=balanced,
                  scalar_gauge_prices=gauge_prices, gauge_owned_contract="C0 starts and ends at zero; 112 arbitrary data fields",
                  scalar_gauge_v2_prices=gauge_v2_prices, gauge_v2_freeze_sha256=GAUGES_V2_PIN,
                  metric=metric, checker_sha256=digest(Path(__file__)))
    (HERE/"REVIEW.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(report["status"], "all64minor subsets;20balanced dyadic interfaces", flush=True)


if __name__ == "__main__":
    main()
