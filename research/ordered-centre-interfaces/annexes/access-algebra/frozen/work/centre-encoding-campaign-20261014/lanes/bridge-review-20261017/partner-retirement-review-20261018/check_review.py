"""Check the partner interface with exact ordered operator columns."""

from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CHECKER_SHA = sha256(Path(__file__).read_bytes()).hexdigest()
LANES = HERE.parents[1]
PRODUCER = LANES / "controller-followthrough-20261017/partner-retirement-20261018"
SOURCE = LANES / "controller-followthrough-20261017/bipartite-eight-20261018"
FREEZE = "ee4c11882ab042f3101b8ccc21e33cfae0348e48af77dcd1667757b94c403af6"
PAYLOAD = "0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee"


def need(test, message):
    if not test:
        raise ValueError(message)


def combine(*terms):
    result = defaultdict(F)
    for coefficient, row in terms:
        for key, value in row.items():
            result[key] += coefficient * value
    return {key: value for key, value in result.items() if value}


def symbol(column):
    return {(column, ()): F(1)}


def op(row, token):
    """Append an operator in execution order. Reduce adjacent Q powers only."""
    result = defaultdict(F)
    for (column, word), value in row.items():
        if word and token[0] == word[-1][0] == "Q" and token[1] == word[-1][1]:
            power = token[2] + word[-1][2]
            next_word = word[:-1] + (("Q", token[1], power),) if power else word[:-1]
        else:
            next_word = word + (token,)
        result[column, next_word] += value
    return {key: value for key, value in result.items() if value}


def q(row, port, power):
    return op(row, ("Q", port, power))


def graph(matrix, vector, targets=None, sources=None, stage="t"):
    targets = range(len(matrix)) if targets is None else targets
    allowed = set(range(len(matrix))) if sources is None else set(sources)
    result = {}
    for row in targets:
        parts = []
        for column, value in matrix[row].items():
            if column in allowed:
                expression = vector[column]
                if row != column:
                    expression = op(expression, ("route", stage, row, column))
                parts.append((value, expression))
        result[row] = combine(*parts)
    return result


def physical_word(matrix, selected, partner, h, d, bad=None):
    n = len(matrix)
    outside = sorted(set(range(n)) - set(partner))
    x = {p: q(h[p], p, 1) for p in range(n)}
    y = dict(d)
    for p in selected:
        y[p] = combine((1, y[p]), (-1, x[p]))
    if bad != "omit_selected_Q":
        for p in selected:
            x[p] = q(x[p], p, 1)
    for p in partner:
        y[p] = q(y[p], p, 1)
        y[p] = combine((1, y[p]), (1, x[p]))
    if bad != "omit_ordinary_gauge":
        y.update(graph(matrix, y, outside, outside))
    for p in partner:
        x[p], y[p] = y[p], x[p]
    normalized = {p: q(x[p], p, -1) for p in range(n)}
    response = graph(matrix, normalized)
    y = {p: q(combine((1, y[p]), (1, response[p])), p, -1) for p in range(n)}
    x = normalized
    for p in partner:
        x[p], y[p] = y[p], x[p]
    return x, y


def expected(matrix, selected, partner, h, d):
    n = len(matrix)
    selected, partner = set(selected), set(partner)
    z = {p: d[p] if p in selected else combine((1, h[p]), (1, d[p])) for p in range(n)}
    hhat = {p: q(h[p], p, 1) if p in selected else h[p] for p in range(n)}
    w = {p: z[p] if p in partner else hhat[p] for p in range(n)}
    jz, jw = graph(matrix, z), graph(matrix, w)
    y = {p: z[p] if p in partner else q(jz[p], p, -1) for p in range(n)}
    x = {p: combine((1, h[p]), (1, q(jw[p], p, -1))) if p in partner else hhat[p]
         for p in range(n)}
    return x, y, z


def mm(left, right):
    out = []
    for row in left:
        result = defaultdict(F)
        for middle, a in row.items():
            for column, b in right[middle].items():
                result[column] += a*b
        out.append({column: value for column, value in result.items() if value})
    return out


def eye(n):
    return [{j: F(1)} for j in range(n)]


def sub(matrix, ports):
    index = {p: i for i, p in enumerate(ports)}
    return [{index[j]: value for j, value in matrix[p].items() if j in index} for p in ports]


def inverse(matrix):
    n = len(matrix)
    left, right = [dict(row) for row in matrix], eye(n)
    determinant = F(1)
    for column in range(n):
        pivot = next(i for i in range(column, n) if left[i].get(column))
        if pivot != column:
            left[column], left[pivot] = left[pivot], left[column]
            right[column], right[pivot] = right[pivot], right[column]
            determinant = -determinant
        value = left[column][column]
        determinant *= value
        left[column] = {j: a/value for j, a in left[column].items()}
        right[column] = {j: a/value for j, a in right[column].items()}
        for i in range(n):
            if i != column and left[i].get(column):
                value = left[i][column]
                left[i] = combine((1, left[i]), (-value, left[column]))
                right[i] = combine((1, right[i]), (-value, right[column]))
    need(left == eye(n), "Exact elimination reached the identity")
    need(mm(matrix, right) == mm(right, matrix) == eye(n), "Both inverse orders")
    return right, determinant


def embed(matrix, ports, n):
    result = [{} for _ in range(n)]
    for i, p in enumerate(ports):
        result[p] = {ports[j]: value for j, value in matrix[i].items()}
    return result


def digest(vector):
    serial = [[(column, word, str(value)) for (column, word), value in sorted(vector[p].items(), key=repr)]
              for p in sorted(vector)]
    return sha256(json.dumps(serial, separators=(",", ":")).encode()).hexdigest()


def main():
    need(sha256((PRODUCER/"FREEZE.json").read_bytes()).hexdigest() == FREEZE, "Frozen theorem pin")
    for name, pin in json.loads((PRODUCER/"FREEZE.json").read_text())["files"].items():
        need(sha256((PRODUCER/name).read_bytes()).hexdigest() == pin, "Frozen producer artifact: " + name)
    raw = gzip.decompress((SOURCE/"BIPARTITE-EIGHT-PROGRAM.json.gz").read_bytes())
    need(sha256(raw).hexdigest() == PAYLOAD, "Exact signed native payload")
    packet = json.loads(raw)
    j = [{int(k): F(v) for k, v in row.items()} for row in packet["response"]]
    n = len(j)
    selected, partner = packet["selected_ports"], packet["partner_ports"]
    s, t = set(selected), set(partner)
    u, v = sorted(set(range(n))-s), sorted(set(range(n))-t)
    rest = sorted(set(range(n))-s-t)
    need(n == 112 and len(s) == len(t) == 8 and not s&t, "The disjoint actual port sets")
    hs, ht = sub(j, u), sub(j, v)
    hsi, hsdet = inverse(hs)
    hti, htdet = inverse(ht)
    need(hsdet == htdet == F(2**60), "Full 104-port principal determinants")
    need(all(a.denominator & (a.denominator-1) == 0 for matrix in (hsi, hti) for row in matrix for a in row.values()),
         "Both complete principal inverses are dyadic")
    g = [{int(k): F(a) for k, a in row.items()} for row in packet["signed_monomial"]]
    for p in packet["small_ports"]:
        need(not g[p], "Stored G is restricted to the large component")
        g[p] = {p:F(1)}
    need(mm(g, g) == eye(n) and mm(g, j) == mm(j, g), "Exact signed relabeling symmetry")
    need({next(iter(g[p])) for p in selected} == t, "The symmetry sends S to T")
    ks = [{p:F(1)} if p in s else dict(j[p]) for p in range(n)]
    rt = [{p:F(1)} if p in t else dict(j[p]) for p in range(n)]
    ksi, kdet = inverse(ks)
    rti, rdet = inverse(rt)
    need(kdet == rdet == hsdet, "Both row codes are complete dyadic units")
    need(mm(mm(ks, rti), mm(rt, ksi)) == eye(n), "The common-view logical decoder inverse")

    h = {p:symbol(p) for p in range(n)}
    d = {p:symbol(n+p) for p in range(n)}
    x0, y0 = physical_word(j, selected, partner, h, d)
    xe, ye, _ = expected(j, selected, partner, h, d)
    need((x0, y0) == (xe, ye), "All 224 independent local input columns")
    need(all(column not in s for row in y0.values() for column, _ in row),
         "The selected h columns are absent for unrestricted local inputs")

    # Build the preceding backward data coefficient from original inputs.
    # Distinct route symbols keep stage-s products in their original order.
    a = {p:q(symbol(p), p, 1) if p in s else symbol(p) for p in range(n)}
    da = graph(j, a, u, selected, stage="s")
    residual = {p:combine((1, symbol(p)), (-1, da[p])) for p in u}
    p_data = graph(embed(hsi, u, n), residual, u, u, stage="s_inverse")
    first = graph(j, a, selected, selected, stage="s")
    cross = graph(j, p_data, selected, u, stage="s")
    p_data.update({p:combine((-1, first[p]), (-1, cross[p])) for p in selected})
    h = {p:combine((1, p_data[p]), (1, q(symbol(n+p), p, -1))) if p in s
         else combine((1, p_data[p]), (-1, symbol(n+p))) for p in range(n)}
    d = {p:a[p] if p in s else symbol(n+p) for p in range(n)}
    x, y = physical_word(j, selected, partner, h, d)
    xe, ye, z = expected(j, selected, partner, h, d)
    need((x, y) == (xe, ye), "All 224 original data and borrowed input columns")
    clean_z = {p:a[p] if p in s else p_data[p] for p in range(n)}
    need(z == clean_z, "The data-only z identity")
    need(all(column < n for row in y.values() for column, _ in row), "Every borrowed coefficient in Y is zero")
    source = {p:{key:value for key, value in row.items() if key[0] >= n} for p, row in x.items()}
    diagonal = {p:symbol(n+p) if p in s else combine((-1, symbol(n+p))) for p in range(n)}
    cross = graph(j, diagonal, partner, v)
    expected_source = {p:combine((1, diagonal[p]), (1, q(cross[p], p, -1))) if p in t else diagonal[p]
                       for p in range(n)}
    need(source == expected_source, "Complete unit triangular borrowed-source code")
    inverse_source = dict(source)
    source_query = graph(j, source, partner, v)
    for p in partner:
        inverse_source[p] = combine((1, inverse_source[p]), (-1, q(source_query[p], p, -1)))
    need(inverse_source == diagonal, "The source coefficient has the stated ordered inverse")
    mixed = {p:y[p] if p in t else x[p] for p in range(n)}
    query = graph(j, mixed, partner)
    corrected = dict(x)
    for p in partner:
        corrected[p] = combine((1, corrected[p]), (-1, q(query[p], p, -1)))
    need(corrected == {p:q(h[p], p, 1) if p in s else h[p] for p in range(n)},
         "The optional eight-query correction on all original columns")
    wrong_query = graph(j, {p:q(mixed[p], p, -1) for p in range(n)}, partner)
    need(wrong_query != {p:q(query[p], p, -1) for p in partner},
         "An inverse line cannot be moved through a graph entry")

    # The selected data term need not be the term supplied by A_s.
    for p in selected:
        arbitrary = op(symbol(p), ("unrestricted_selected_data_map", p))
        h[p] = combine((1, arbitrary), (1, q(symbol(n+p), p, -1)))
    _, weaker_y = physical_word(j, selected, partner, h, d)
    need(weaker_y == y, "The retired code is independent of the selected data coefficient")
    for mutation in ("omit_selected_Q", "omit_ordinary_gauge"):
        _, bad_y = physical_word(j, selected, partner, h, d, bad=mutation)
        need(bad_y != y, "Mutation must fail: " + mutation)

    # A common-view decoder gives D_QS x. The required hole endpoint is q x.
    line_exponents = {p:1 if p in s else 0 for p in range(n)}
    terminal_inverse_lines = {p:1 + line_exponents[p] for p in range(n)}
    need(sum(a == 1 for a in terminal_inverse_lines.values()) == 104
         and sum(a == 2 for a in terminal_inverse_lines.values()) == 8,
         "Final demotion needs 104 odd line powers and eight even powers")
    terminal_native = len(v) + sum(a % 2 for a in terminal_inverse_lines.values())
    full_x_native = len(v) + len(s)
    need((terminal_native, full_x_native) == (208, 112), "Hole and FULL endpoint counts differ")
    need(sha256(Path(__file__).read_bytes()).hexdigest() == CHECKER_SHA, "Checker bytes stayed fixed")
    receipt = {
        "status":"PASS_INDEPENDENT_PARTNER_RETIREMENT",
        "producer_freeze_sha256": FREEZE,
        "source_payload_decompressed_sha256": PAYLOAD,
        "checker_sha256": CHECKER_SHA,
        "local_input_columns":224,
        "original_data_and_borrowed_columns":224,
        "borrowed_columns_cancelled_from_Y":112,
        "selected_h_columns_absent_from_Y":len(s),
        "full_principal_block_sizes":[len(u),len(v)],
        "full_principal_determinants":[str(hsdet),str(htdet)],
        "row_code_determinants":[str(kdet),str(rdet)],
        "prefix_positive_lines":len(s)+len(t),
        "optional_X_inverse_queries":len(t),
        "direct_FULL_x_decoder_native_lines":full_x_native,
        "direct_hole_qx_decoder_native_lines":terminal_native,
        "direct_hole_qx_decoder_even_line_maps":len(s),
        "retired_X_ordered_sha256":digest(x),
        "retired_Y_ordered_sha256":digest(y),
        "source_X_ordered_sha256":digest(source),
        "arbitrary_selected_data_coefficient_passed":True,
        "negative_controls":["omit_selected_Q","omit_ordinary_gauge","commute_q_through_graph"],
        "scope":"Ordered local theorem and full principal-unit check. Native emission, access, inter-stage binding and global terminal price remain separate.",
    }
    (HERE/"REVIEW.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
