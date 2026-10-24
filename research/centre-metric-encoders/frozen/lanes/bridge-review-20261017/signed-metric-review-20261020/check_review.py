"""Check the signed metric and the actual one-centre completion."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
OLD = HERE.parent / "fixed-reader-reuse-review-20261020"
MODEL = LANES / "oblique-native-20261017/signed-metric-reciprocal-20261020"
CODE = LANES / "new-core-transfer-20261017/low-displacement-20261020/signed-sixteen-20261020"
MODEL_FREEZE = "9dbff19fa68567eadea82cef2add71fda3ffe7228944028d06d53880da8b70f7"
MODEL_PIN = "df2d2028c99028db3c645b3311d7f31ff96efe72f6f9257f99157ce030ff43d0"
CODE_FREEZE = "8739b5dbba6a5422c9b68035683876931fbf8f6599a43375d10e73eee55b2de2"
CODE_PIN = "5ba0e042c6f27aa24e230e27a4eca5e1da573d3e39d22dab93886b207f14016c"
PAIRED_FREEZE = "810508791ea43aecaaf894c3cb50a8170d3e6f1f8e52684e274cda16c2c2db57"
PAIRED_PIN = "99fad6bbc9e4a463a576fe33c8d2093739e5c696851412b1e9115c78d88daec1"
OLD_PIN = "d8d782ecc13fdd2d26380fc4b047fc6d6781417ec694fdd3dea910dce04c2e2a"


def need(test, reason):
    if not test:
        raise ValueError(reason)


def read(path, pin, compressed=False):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Source pin: " + str(path))
    return json.loads(raw)


def freeze(path, pin):
    value = read(path, pin)
    for name, expected in value["files"].items():
        raw = (path.parent / name).read_bytes()
        pin = expected["sha256"] if isinstance(expected, dict) else expected
        need(sha256(raw).hexdigest() == pin, "Frozen file: " + name)
        if isinstance(expected, dict) and "decompressed_sha256" in expected:
            need(sha256(gzip.decompress(raw)).hexdigest() == expected["decompressed_sha256"],
                 "Frozen decompressed file: " + name)
    return value


freeze(OLD / "FREEZE.json", OLD_PIN)
spec = importlib.util.spec_from_file_location("independent_signed_metric_math", OLD / "check_review.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def transpose(a, columns):
    result = [{} for _ in range(columns)]
    for i, row in enumerate(a):
        for j, value in row.items():
            result[j][i] = value
    return result


def diagonal(values):
    return [{i: F(value)} for i, value in enumerate(values)]


def difference(a, b):
    out = [dict(row) for row in a]
    for row, source in zip(out, b):
        for p, value in source.items():
            r.put(row, p, -value)
    return out


def rank(a, columns):
    state = [dict(row) for row in a]
    pivot = 0
    for j in range(columns):
        found = next((i for i in range(pivot, len(state)) if state[i].get(j)), None)
        if found is None:
            continue
        state[pivot], state[found] = state[found], state[pivot]
        divisor = state[pivot][j]
        state[pivot] = {q: c / divisor for q, c in state[pivot].items()}
        for i in range(pivot + 1, len(state)):
            value = state[i].get(j, F(0))
            for q, c in state[pivot].items():
                r.put(state[i], q, -value * c)
        pivot += 1
    return pivot


def modular_rank(a, columns, prime):
    state = [{j: (v.numerator * pow(v.denominator, -1, prime)) % prime for j, v in row.items()}
             for row in a]
    pivot = 0
    for j in range(columns):
        found = next((i for i in range(pivot, len(state)) if state[i].get(j)), None)
        if found is None:
            continue
        state[pivot], state[found] = state[found], state[pivot]
        reciprocal = pow(state[pivot][j], -1, prime)
        state[pivot] = {q: value * reciprocal % prime for q, value in state[pivot].items()}
        for i in range(pivot + 1, len(state)):
            value = state[i].get(j, 0)
            for q, coefficient in state[pivot].items():
                state[i][q] = (state[i].get(q, 0) - value * coefficient) % prime
        pivot += 1
    return pivot


def install(a, local, ports):
    for p, row in zip(ports, local):
        a[p] = {ports[j]: value for j, value in row.items()}


def local_model(n):
    k = n - 4
    u = [F(1)] * (n - 2) + [F(k), F(0)]
    ell = [F(-1)] * (n - 2) + [F(1), F(0)]
    reflection = r.eye(n)
    for i, value in enumerate(u):
        for j, coefficient in enumerate(ell):
            r.put(reflection[i], j, value * coefficient)
    permutation = r.eye(n)
    permutation[-2], permutation[-1] = permutation[-1], permutation[-2]
    metric = diagonal([1] * (n - 2) + [F(-1, k)] * 2)
    metric_inverse = diagonal([1] * (n - 2) + [-k] * 2)
    response = r.matmul(permutation, reflection)
    inverse = r.matmul(reflection, permutation)
    need(sum(a * b for a, b in zip(u, ell)) == -2, "Reflection scalar")
    need(r.matmul(reflection, reflection) == r.eye(n), "Local reflection")
    need(r.matmul(response, inverse) == r.matmul(inverse, response) == r.eye(n), "Local reciprocal orders")
    need(r.matmul(transpose(response, n), r.matmul(metric, response)) == metric, "Local signed metric")
    return dict(E=response, inverse_E=inverse, R=reflection, P=permutation, J=metric, inverse_J=metric_inverse)


def local_code(n):
    def row(*terms):
        out = {}
        for indices, value in terms:
            for j in indices:
                r.put(out, j, F(value))
        return out
    ell = row((range(n - 2), -1), ([n - 2], 1))
    if n == 6:
        rows = [ell, row(([2], 1), ([3], -1)), row(([0], 1), ([1], -1)),
                row(([5], 1)), row(([0, 1], 1), ([2, 3], -1)),
                row((range(4), 1), ([4], -2))]
        gram = [2, 2, 2, -2, 4, -4]
    else:
        need(n == 8, "Actual local block size")
        rows = [ell, row(([4, 5], 1), ([6], F(-1, 2))),
                row(([4], 1), ([5], -1)), row(([7], 1)),
                row(([0], 1), ([1], -1)), row(([2], 1), ([3], -1)),
                row(([0, 1], 1), ([2, 3], -1)),
                row((range(4), 1), ([4, 5], 2), ([6], -2))]
        gram = [2, 1, 2, -4, 2, 2, 4, -4]
    return rows, diagonal(gram)


def dyadic_exponent(value):
    value = abs(value)
    need(value and value.numerator & (value.numerator - 1) == 0
         and value.denominator & (value.denominator - 1) == 0, "A signed power of two")
    return value.numerator.bit_length() - value.denominator.bit_length()


def replay(word, count=640):
    state = r.eye(count)
    bill, peak, height = 0, F(1), 0
    for op, target, source, coefficient in word:
        c = F(coefficient)
        exponent = dyadic_exponent(c)
        need(0 <= target < count, "Target range")
        if op == "add":
            need(0 <= source < count and source != target, "Independent source")
            for j, value in state[source].items():
                r.put(state[target], j, c * value)
            bill += 8 + 2 * abs(exponent)
        else:
            need(op == "scale" and source is None, "Scale grammar")
            state[target] = {j: c * value for j, value in state[target].items()}
            bill += 2 * (abs(exponent) + (c < 0))
        peak = max(peak, sum(abs(c) for c in state[target].values()))
        for value in state[target].values():
            d = value.denominator
            need(d & (d - 1) == 0, "No odd denominator at any prefix")
            height = max(height, d.bit_length() - 1)
    return state, {"scalar_primitives": bill, "row_sum_peak": str(peak), "binary_height": height,
                   "input_columns": count, "instructions": len(word)}


def inverse_word(word):
    return [[op, target, source, str(-F(c) if op == "add" else 1 / F(c))]
            for op, target, source, c in reversed(word)]


def inverse_adjoint_word(word):
    return [["add", source, target, str(-F(c))] if op == "add"
            else [op, target, source, str(1 / F(c))]
            for op, target, source, c in word]


def direct_clean(c, selected):
    out = r.eye(224)
    for p in range(112):
        if p in selected:
            out[p] = {112 + p: F(-1)}
            out[112 + p] = dict(c[p])
        else:
            out[p] = dict(c[p])
            for j, value in c[p].items():
                r.put(out[112 + p], j, value)
    return out


def general_completion(power):
    k, n = 2**power, 2**power + 4
    c = r.eye(n)
    for i in range(k):
        c[i] = {j: F((-1) ** ((i & j).bit_count())) for j in range(k)}
    alpha = F(k - 2, 4)
    c[0] = {j: 1 + alpha for j in range(k)}
    c[0].update({k: F(k, 2), k + 1: F(k, 2), k + 2: -2 - alpha})
    c[k] = {j: F(-1) for j in range(k + 2)}
    c[k][k + 2] = F(1)
    c[k + 1] = {k: F(1), k + 1: F(-1)}
    c[k + 2] = {j: 1 - alpha for j in range(k)}
    c[k + 2].update({k: F(-k, 2), k + 1: F(-k, 2), k + 2: alpha})
    c = [{j: value for j, value in row.items() if value} for row in c]
    model = local_model(n)
    g = diagonal([-2 * k] + [k] * (k - 1) + [2, 2, 2 * k, -k])
    need(r.matmul(c, r.matmul(model["inverse_J"], transpose(c, n))) == g,
         "General one-centre diagonal Gram")
    signed = [dict(row) for row in c]
    signed[k] = {j: -value for j, value in c[k].items()}
    need(r.matmul(c, model["R"]) == signed, "General ordinary rows are fixed")
    return {"n": n, "k": k, "centre_coordinate": k, "gram": [str(row[i]) for i, row in enumerate(g)],
            "determinant_squared": str(16 * k**k)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "normal")
    args = parser.parse_args()
    freeze(MODEL / "MODEL-FREEZE.json", MODEL_FREEZE)
    freeze(CODE / "FREEZE.json", CODE_FREEZE)
    freeze(CODE / "PAIRED-FREEZE.json", PAIRED_FREEZE)
    model = read(MODEL / "model-normal-v2/RESPONSE.json.gz", MODEL_PIN, True)
    code = read(CODE / "run-v2-normal/SIGNED-SIXTEEN.json.gz", CODE_PIN, True)
    paired = read(CODE / "paired-normal/PAIRED-SIGNED-SIXTEEN.json.gz", PAIRED_PIN, True)
    for relative, pin in model["source_pins"].values():
        read(LANES / relative, pin, relative.endswith(".gz")) if relative.endswith((".json", ".gz")) else \
            need(sha256((LANES / relative).read_bytes()).hexdigest() == pin, "Model arithmetic source")
    cyclic_path, cyclic_pin = model["source_pins"]["cyclic"]
    cyclic = read(LANES / cyclic_path, cyclic_pin)
    need(model["ports"] == cyclic["ports"] and model["pair_codes"] == cyclic["pair_codes"],
         "Pinned actual physical pair geometry")
    h = r.eye(112)
    for pair in model["pair_codes"]:
        ports = pair["ports"]
        install(h, [{j: F(c) for j, c in enumerate(row) if c} for row in pair["matrix"]], ports)
    hi, _ = r.invert(h)
    need(h == r.sparse(model["pair_code"]) and hi == r.sparse(model["pair_code_inverse"]),
         "Independent actual pair transform")
    modes = {name: r.eye(112) for name in ("E", "inverse_E", "R", "P", "J", "inverse_J")}
    cm, gm = r.eye(112), r.eye(112)
    all_ports, centres, special = [], [], []
    local_reports = {}
    for block in model["blocks"]:
        ports = block["ports"]
        all_ports += ports
        centres.append(ports[0])
        special += ports[-2:]
        if len(ports) == 6:
            need(set(ports) == set(cyclic["cyclic_carriers"][block["vertex"]]), "Actual six-mode component")
        else:
            need(all((model["ports"][p] & model["ports"][q]).bit_count() % 2 == (p == q)
                     for p in ports for q in ports), "Actual orthonormal eight-clique")
        local = local_model(len(ports))
        c, g = local_code(len(ports))
        need(r.matmul(c, r.matmul(local["inverse_J"], transpose(c, len(ports)))) == g,
             "Independently constructed local code Gram")
        ci, determinant = r.invert(c)
        need(determinant == -8 and r.matmul(ci, c) == r.eye(len(ports)), "Local dyadic inverse")
        for name, matrix in local.items():
            install(modes[name], matrix, ports)
        install(cm, c, ports)
        install(gm, g, ports)
        local_reports[str(len(ports))] = {"determinant": str(determinant),
                                          "gram": [str(row[i]) for i, row in enumerate(g)]}
    need(sorted(all_ports) == list(range(112)) and centres == model["centre_ports"] == code["centre_ports"],
         "Complete sixteen-block partition")
    selected = set(centres)
    for pair in model["pair_codes"]:
        p, q = pair["ports"]
        need((p in selected) == (q in selected), "Complete selected physical pairs")
        need(modes["J"][p][p] == modes["J"][q][q], "Input metric pair closure")
        need(gm[p][p] == gm[q][q], "Output Gram pair closure")
    physical = {name: r.matmul(hi, r.matmul(a, h)) for name, a in modes.items()}
    need(all(modes[name] == r.sparse(model["mode"][name])
             and physical[name] == r.sparse(model["physical"][name]) for name in modes),
         "Every independently derived physical model matrix")
    e, ei, reflection, permutation, j, k = (physical[name] for name in modes)
    need(r.matmul(transpose(e, 112), r.matmul(j, e)) == j, "Actual signed metric")
    need(transpose(ei, 112) == r.matmul(j, r.matmul(e, k)), "Actual inverse-adjoint conversion")
    need(Counter(row[i] for i, row in enumerate(j)) == {F(1): 80, F(-1, 2): 16, F(-1, 4): 16},
         "Physical metric weights")
    need(all(not a[p].get(p) for a in (e, ei) for p in range(112)), "Both physical response diagonals")
    need(all((model["ports"][p] & model["ports"][q]).bit_count() % 2 == 0
             for p, row in enumerate(e) for q in row), "Actual orthogonal physical response support")
    support = [p for p in range(112) if permutation[p] != {p: F(1)}]
    need(support == sorted(special) and len(support) == 32
         and sum(map(len, permutation)) == 160, "Paid P support and non-monomial census")
    need(rank(difference(reflection, r.eye(112)), 112) == 16
         and rank(difference(e, r.eye(112)), 112) == 32, "Both displacement ranks")
    ordinary_hi = r.eye(112)
    for p in range(112):
        if p not in selected:
            ordinary_hi[p] = hi[p]
    c = r.matmul(ordinary_hi, r.matmul(cm, h))
    g = r.matmul(c, r.matmul(k, transpose(c, 112)))
    need(c == r.sparse(code["code"]) and cm == r.sparse(code["mode_code"]), "Actual physical one-centre code")
    need(r.matmul(c, transpose(c, 112)) != r.eye(112)
         and r.matmul(transpose(e, 112), e) != r.eye(112), "The code and response are not Euclidean unitary")
    need(all(set(row) == {p} for p, row in enumerate(g)), "Physical diagonal output Gram")
    need(g == r.sparse(code["output_metric"]) and k == r.sparse(code["input_metric"]), "Exact K and G")
    gi = diagonal([1 / row[p] for p, row in enumerate(g)])
    ci = r.matmul(k, r.matmul(transpose(c, 112), gi))
    cd = r.matmul(gi, r.matmul(c, k))
    need(r.matmul(c, ci) == r.matmul(ci, c) == r.eye(112)
         and ci == r.sparse(code["inverse"])
         and cd == transpose(ci, 112) == r.sparse(code["inverse_adjoint"]), "Both complete inverse identities")
    zc = [{q: (-1 if p in selected else 1) * value for q, value in row.items()}
          for p, row in enumerate(c)]
    need(r.matmul(c, reflection) == zc and zc == r.sparse(code["coded_reflection"]),
         "The code diagonalizes the reflection")
    need([c[p] for p in centres] == r.sparse(model["reflection_L"])
         and [g[p][p] for p in centres] == [F(4)] * 8 + [F(2)] * 8, "Physical reader normalization")
    readers = [c[p] for p in centres]
    euclidean_gram = r.matmul(readers, transpose(readers, 112))
    need(euclidean_gram == diagonal([10] * 8 + [7] * 8), "The new Euclidean reader Gram")
    prime_ranks = {}
    for prime in (3, 5, 7):
        a, gram_rank = modular_rank(readers, 112, prime), modular_rank(euclidean_gram, 16, prime)
        need(a == 16 and gram_rank == (16 if prime == 3 else 8), "Actual odd-prime ranks")
        prime_ranks[str(prime)] = {"reader_rank": a, "gram_rank": gram_rank,
                                   "complex_unitary_coordinate_bound": 2 * a - gram_rank}
    cn = r.matmul(h, r.matmul(c, hi))
    need(cn == r.sparse(code["native_code"]), "Actual native coordinate code")
    need(all(not c[p].get(p) and not cn[p].get(p) for p in range(112) if p not in selected),
         "Every ordinary physical and native diagonal")
    groups = [set(block["ports"]) for block in model["blocks"]]
    need(all(any(p in group and set(cn[p]) <= group for group in groups)
             for p in range(112) if p not in selected), "Ordinary native support remains in its mode block")
    reports = {}
    expected = dict(physical, inverse_adjoint_E=transpose(ei, 112), metric_inverse_adjoint_E=transpose(ei, 112))
    for name, word in model["scalar_words"].items():
        state, reports["model/" + name] = replay(word)
        need(state[:112] == expected[name] and state[112:] == r.eye(640)[112:], "All640 model word columns")
    expected = {"code": c, "inverse": ci, "literal_inverse_adjoint": cd, "diagonal_inverse_adjoint": cd}
    for name, word in code["scalar_words"].items():
        state, reports["code/" + name] = replay(word)
        need(state[:112] == expected[name] and state[112:] == r.eye(640)[112:], "All640 code word columns")
    need(reports["code/code"]["scalar_primitives"] == reports["code/inverse"]["scalar_primitives"] == 5564,
         "Complete C and inverse costs")
    need(reports["code/code"]["row_sum_peak"] == "24"
         and reports["code/inverse"]["row_sum_peak"] == "9"
         and reports["code/code"]["binary_height"] == reports["code/inverse"]["binary_height"] == 3,
         "Exact C and inverse prefix bounds")
    for name in ("code", "inverse"):
        word = code["scalar_words"][name]
        index = next(i for i, gate in enumerate(word) if gate[0] == "add")
        wrong, _ = replay(word[:index] + word[index + 1:])
        need(wrong[:112] != expected[name], "Deleted ADD control: " + name)
    wrong_c = r.matmul(hi, r.matmul(cm, h))
    need([wrong_c[p] for p in centres] != readers, "The full left inverse pair code changes the readers")
    wrong_j = [dict(row) for row in j]
    wrong_j[special[0]][special[0]] *= -1
    need(r.matmul(transpose(e, 112), r.matmul(wrong_j, e)) != wrong_j,
         "One changed metric sign fails")
    fw = list(code["scalar_words"]["code"])
    fw += [["add", 112 + p, p, "1"] for p in range(112) if p not in selected]
    for p in centres:
        fw += [["add", 112 + p, p, "1"], ["add", p, 112 + p, "-1"], ["add", 112 + p, p, "1"]]
    state, reports["clean/forward_scalar"] = replay(fw)
    need(state[:224] == direct_clean(c, selected) == r.sparse(code["clean_maps"]["forward"])
         and state[224:] == r.eye(640)[224:], "Arbitrary clean inputs and416 outside fields")
    pre, post = (code["clean_metric_wrappers"][name] for name in ("pre", "post"))
    def diagonal_word(a, offset=0):
        return [["scale", offset + p, None, str(row[p])] for p, row in enumerate(a) if row[p] != 1]
    need(pre == diagonal_word(j) + diagonal_word(gi, 112)
         and post == diagonal_word(g) + diagonal_word(g, 112), "Exact metric signs and baseline banks")
    converted = pre + inverse_adjoint_word(fw) + post
    state, reports["clean/converted_scalar"] = replay(converted)
    target = r.eye(224)
    for p in range(112):
        if p in selected:
            target[p] = {112 + p: F(-1)}
            target[112 + p] = dict(c[p])
        else:
            target[p] = dict(c[p])
            r.put(target[p], 112 + p, F(-1))
    need(state[:224] == target == r.sparse(code["clean_maps"]["converted_inverse_adjoint"])
         and state[224:] == r.eye(640)[224:], "Full metric-converted inverse-adjoint on arbitrary inputs")
    missing_target_pre = [gate for gate in pre if gate[1] < 112] + inverse_adjoint_word(fw) + post
    wrong, _ = replay(missing_target_pre)
    need(wrong[:224] != target, "The target metric input scales cannot be omitted")
    def exchange(field):
        if field is None:
            return None
        return field + 112 if field in selected else (field - 112 if field - 112 in selected else field)
    swapped_word = [[op, exchange(t), exchange(s), value] for op, t, s, value in converted]
    swapped_target = [{exchange(q): value for q, value in target[exchange(p)].items()} for p in range(224)]
    state, reports["clean/selected_conjugate"] = replay(swapped_word)
    need(state[:224] == swapped_target == r.sparse(code["clean_maps"]["selected_conjugate"])
         and state[224:] == r.eye(640)[224:], "Complete selected-bank conjugation")
    _, wrapper_bill = replay(pre + post)
    need(wrapper_bill["scalar_primitives"] == 1264, "Both-bank metric wrapper price")
    cbar = r.matmul(hi, r.matmul(cm, h))
    cbar_t = transpose(cbar, 112)
    gbar = r.matmul(cbar, r.matmul(k, cbar_t))
    need(all(set(row) == {p} for p, row in enumerate(gbar)), "Paired output metric is diagonal")
    gbar_i = diagonal([1 / row[p] for p, row in enumerate(gbar)])
    cbar_i = r.matmul(k, r.matmul(cbar_t, gbar_i))
    cbar_it = transpose(cbar_i, 112)
    paired_matrices = {"code": cbar, "transpose": cbar_t, "inverse": cbar_i,
                       "inverse_transpose": cbar_it, "input_metric": k,
                       "input_metric_inverse": j, "output_metric": gbar,
                       "output_metric_inverse": gbar_i}
    need(all(value == r.sparse(paired[name]) for name, value in paired_matrices.items()),
         "Every paired code and metric matrix")
    need(r.matmul(cbar, cbar_i) == r.matmul(cbar_i, cbar) == r.eye(112)
         and r.matmul(cbar_t, r.matmul(gbar_i, cbar)) == j,
         "Both paired inverse orders and transpose metric contract")
    selected_h, selected_hi = r.eye(112), r.eye(112)
    for p in centres:
        selected_h[p], selected_hi[p] = h[p], hi[p]
    need(selected_h == r.sparse(paired["centre_recovery"])
         and r.matmul(selected_hi, c) == cbar
         and r.matmul(selected_h, cbar) == c, "Paid exact reader recovery")
    need([gbar[p][p] for p in centres] == [F(2)] * 16, "All paired centre norms are two")
    need([cbar[p] for p in range(112) if p not in selected]
         == [c[p] for p in range(112) if p not in selected], "Ordinary rows are unchanged")
    need(r.matmul(cbar, reflection)
         == [{q: (-1 if p in selected else 1) * value for q, value in row.items()}
             for p, row in enumerate(cbar)], "Paired reflection diagonalization")
    suffix, reports["paired/selected_pair_suffix"] = replay(paired["selected_pair_inverse_word"])
    need(suffix[:112] == selected_hi and suffix[112:] == r.eye(640)[112:]
         and reports["paired/selected_pair_suffix"]["scalar_primitives"] == 80,
         "The selected pair suffix is fully paid")
    need(paired["scalar_words"]["code"]
         == code["scalar_words"]["code"] + paired["selected_pair_inverse_word"],
         "Literal original code plus selected pair suffix")
    old_native_t = r.matmul(h, r.matmul(transpose(c, 112), hi))
    bad_rows = [p for p in range(112) if p not in selected
                and not any(p in group and set(old_native_t[p]) <= group for group in groups)]
    need(len(bad_rows) == 32, "The original transpose fails 32 ordinary support rows")
    for name, matrix in (("code", cbar), ("transpose", cbar_t)):
        native = r.matmul(h, r.matmul(matrix, hi))
        need(native == r.sparse(paired["native_codes"][name])
             == (cm if name == "code" else transpose(cm, 112)), "Paired native chart identity")
        need(all(not matrix[p].get(p) and not native[p].get(p)
                 and any(p in group and set(native[p]) <= group for group in groups)
                 for p in range(112) if p not in selected),
             "Both paired ordinary diagonals and mode supports")
    for name, word in paired["scalar_words"].items():
        state, report = replay(word)
        reports["paired/" + name] = report
        need(state[:112] == paired_matrices[name] and state[112:] == r.eye(640)[112:],
             "All640 paired code word columns")
        need(report["scalar_primitives"] == 5644 and report["binary_height"] == 3
             and report["instructions"] == 752, "Complete paired word invoice")
        need(report["row_sum_peak"]
             == {"code": "24", "transpose": "8", "inverse": "10", "inverse_transpose": "6"}[name],
             "Exact paired prefix row norm")
    result = {
        "status": "PASS_INDEPENDENT_SIGNED_METRIC_AND_SIXTEEN_CENTRES",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "model_freeze_sha256": MODEL_FREEZE, "model_payload_sha256": MODEL_PIN,
        "code_freeze_sha256": CODE_FREEZE, "code_payload_sha256": CODE_PIN, "local_codes": local_reports,
        "paired_freeze_sha256": PAIRED_FREEZE, "paired_payload_sha256": PAIRED_PIN,
        "physical_metric_census": dict(Counter(str(row[p]) for p, row in enumerate(j))),
        "output_metric_census": dict(Counter(str(row[p]) for p, row in enumerate(g))),
        "reflection_rank": 16, "response_minus_identity_rank": 32, "P_support": 32, "P_nonzero": 160,
        "euclidean_reader_gram": [10] * 8 + [7] * 8, "odd_prime_ranks": prime_ranks,
        "negative_controls": ["deleted_code_ADD", "deleted_inverse_ADD", "full_left_pair_inverse",
                              "changed_metric_sign", "omitted_target_metric_input"],
        "reports": reports, "clean_metric_wrapper_scalar": 1264,
        "paired_output_metric_census": dict(Counter(str(row[p]) for p, row in enumerate(gbar))),
        "old_transpose_ordinary_support_failures": bad_rows,
        "general_power_two_examples": [general_completion(power) for power in range(7)],
        "producer_code_imported": False, "native_service_claimed": False,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    (args.output / "REVIEW-CHECKS.json").write_bytes(raw)
    print(result["status"])
    print(sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
