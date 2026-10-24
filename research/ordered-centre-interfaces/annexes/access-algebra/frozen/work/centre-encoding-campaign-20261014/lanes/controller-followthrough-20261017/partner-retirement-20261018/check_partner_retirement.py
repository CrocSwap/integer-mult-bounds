#!/usr/bin/env python3
"""Check the ordered partner-retirement interface on the pinned response."""

from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "bipartite-eight-20261018"
PAYLOAD_SHA = "0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee"


def need(value, message):
    if not value:
        raise RuntimeError(message)


def add(*terms):
    out = defaultdict(F)
    for coefficient, expression in terms:
        for word, value in expression.items():
            out[word] += coefficient * value
    return {word: value for word, value in out.items() if value}


def symbol(name, port):
    return {((name, port),): F(1)}


def operator(token, expression):
    out = defaultdict(F)
    for word, coefficient in expression.items():
        new = (token,) + word
        if token[0] == "Q" and word[0][0] == "Q" and token[1] == word[0][1]:
            exponent = token[2] + word[0][2]
            new = (("Q", token[1], exponent),) + word[1:] if exponent else word[1:]
        out[new] += coefficient
    return {word: value for word, value in out.items() if value}


def line(port, exponent, expression):
    return operator(("Q", port, exponent), expression)


def route(stage, target, source, expression):
    if target == source:
        return expression
    return operator(("route", stage, target, source), expression)


def graph(rows, values, targets=None, sources=None):
    targets = range(len(rows)) if targets is None else targets
    allowed = set(range(len(rows))) if sources is None else set(sources)
    out = {}
    for target in targets:
        out[target] = add(*[(coefficient, route("t", target, source, values[source]))
                            for source, coefficient in rows[target].items() if source in allowed])
    return out


def word(rows, selected, partner, h, d, omit_s_line=False):
    n = len(rows)
    outside = sorted(set(range(n)) - set(partner))
    x = {p: line(p, 1, h[p]) for p in range(n)}
    y = dict(d)
    for p in selected:
        y[p] = add((1, y[p]), (-1, x[p]))
        if not omit_s_line:
            x[p] = line(p, 1, x[p])
    for p in partner:
        y[p] = add((1, line(p, 1, y[p])), (1, x[p]))
    ordinary = graph(rows, y, outside, outside)
    y.update(ordinary)
    for p in partner:
        x[p], y[p] = y[p], x[p]
    normalized_x = {p: line(p, -1, x[p]) for p in range(n)}
    response = graph(rows, normalized_x)
    x = normalized_x
    y = {p: line(p, -1, add((1, y[p]), (1, response[p]))) for p in range(n)}
    for p in partner:
        x[p], y[p] = y[p], x[p]
    return x, y


def sparse_product(left, right):
    out = []
    for row in left:
        result = defaultdict(F)
        for middle, a in row.items():
            for column, b in right[middle].items():
                result[column] += a * b
        out.append({column: value for column, value in result.items() if value})
    return out


def digest_expressions(values):
    serial = [[(repr(word), str(value)) for word, value in sorted(values[p].items(), key=lambda v: repr(v[0]))]
              for p in sorted(values)]
    return sha256(json.dumps(serial, separators=(",", ":")).encode()).hexdigest()


def main():
    raw = gzip.decompress((SOURCE / "BIPARTITE-EIGHT-PROGRAM.json.gz").read_bytes())
    need(sha256(raw).hexdigest() == PAYLOAD_SHA, "Pinned signed response changed")
    payload = json.loads(raw)
    rows = [{int(p): F(v) for p, v in row.items()} for row in payload["response"]]
    monomial = [{int(p): F(v) for p, v in row.items()} for row in payload["signed_monomial"]]
    n = len(rows)
    for p in payload["small_ports"]:
        need(not monomial[p], "The stored G has zero support on the small block")
        monomial[p] = {p: F(1)}
    selected, partner = payload["selected_ports"], payload["partner_ports"]
    sset, tset = set(selected), set(partner)
    ordinary = set(range(n)) - sset
    outside = set(range(n)) - tset
    rest = ordinary - tset
    need(n == 112 and len(sset) == len(tset) == 8 and not sset & tset,
         "The source has two disjoint eight-port sets")
    need(all(len(row) == 1 and next(iter(row.values())) in (1, -1) for row in monomial),
         "G is a signed permutation on all ports")
    identity = [{p: F(1)} for p in range(n)]
    need(sparse_product(monomial, monomial) == identity, "G squared is the identity")
    need(sparse_product(rows, monomial) == sparse_product(monomial, rows), "J and G commute")
    need({next(iter(monomial[p])) for p in selected} == tset, "G takes S to T")

    h = {p: symbol("h", p) for p in range(n)}
    d = {p: symbol("d", p) for p in range(n)}
    x, y = word(rows, selected, partner, h, d)
    z = {p: d[p] if p in sset else add((1, h[p]), (1, d[p])) for p in range(n)}
    jz = graph(rows, z)
    expected_y = {p: z[p] if p in tset else line(p, -1, jz[p]) for p in range(n)}
    need(y == expected_y, "The complete ordered Y endpoint is the stated code")
    modified_h = {p: line(p, 1, h[p]) if p in sset else h[p] for p in range(n)}
    input_response = dict(modified_h)
    input_response.update({p: z[p] for p in partner})
    jinput = graph(rows, input_response)
    expected_x = {p: add((1, h[p]), (1, line(p, -1, jinput[p]))) if p in tset else modified_h[p]
                  for p in range(n)}
    need(x == expected_x, "The complete ordered X endpoint is the stated map")

    p_data = {p: symbol("p", p) for p in range(n)}
    a = {p: symbol("a", p) for p in selected}
    b = {p: symbol("b", p) for p in selected}
    v = {p: symbol("v", p) for p in ordinary}
    h = {p: add((1, p_data[p]), (1, line(p, -1, b[p]))) if p in sset
         else add((1, p_data[p]), (-1, v[p])) for p in range(n)}
    d = {p: line(p, 1, a[p]) if p in sset else v[p] for p in range(n)}
    x, y = word(rows, selected, partner, h, d)
    z = {p: line(p, 1, a[p]) if p in sset else p_data[p] for p in range(n)}
    jz = graph(rows, z)
    need(y == {p: z[p] if p in tset else line(p, -1, jz[p]) for p in range(n)},
         "The retired Y code contains no borrowed input")
    need(not any(word[-1][0] in ("b", "v") for expression in y.values() for word in expression),
         "All 112 borrowed source columns vanish from retired Y")
    source_x = {p: {word: value for word, value in expression.items() if word[-1][0] in ("b", "v")}
                for p, expression in x.items()}
    diagonal_source = {p: b[p] if p in sset else add((-1, v[p])) for p in range(n)}
    graph_source = graph(rows, diagonal_source, partner, outside)
    expected_source = {p: add((1, diagonal_source[p]), (1, line(p, -1, graph_source[p])))
                       if p in tset else diagonal_source[p] for p in range(n)}
    need(source_x == expected_source, "The source map is the stated unit triangular map")
    undone = dict(source_x)
    current_query = graph(rows, source_x, partner, outside)
    for p in partner:
        undone[p] = add((1, undone[p]), (-1, line(p, -1, current_query[p])))
    need(undone == diagonal_source, "One selected graph shear inverts the source code")
    corrected = dict(x)
    query_input = dict(x)
    query_input.update({p: y[p] for p in partner})
    complete_query = graph(rows, query_input, partner)
    for p in partner:
        corrected[p] = add((1, corrected[p]), (-1, line(p, -1, complete_query[p])))
    need(corrected == {p: line(p, 1, h[p]) if p in sset else h[p] for p in range(n)},
         "The optional eight-query correction returns the unchanged ordinary X")

    _, bad_y = word(rows, selected, partner, h, d, omit_s_line=True)
    need(bad_y != y, "The missing S phase mutation must fail")
    receipt = {
        "status": "PASS_PARTNER_RETIREMENT_ORDERED_CONTENT",
        "scope": "Ordered local content identity, source unit, and pinned principal-unit applicability; no native implementation or supplier decoder claim",
        "source_payload_decompressed_sha256": PAYLOAD_SHA,
        "selected_ports": selected,
        "partner_ports": partner,
        "ordinary_ports": len(ordinary),
        "generic_input_fields": 224,
        "borrowed_source_fields_cancelled_from_Y": 112,
        "retired_FULL_fields": 8,
        "retired_hole_fields": 104,
        "proposed_extra_H1_children": 16,
        "optional_X_correction_extra_H1_queries": 8,
        "Y_ordered_polynomial_sha256": digest_expressions(y),
        "X_ordered_polynomial_sha256": digest_expressions(x),
        "source_unit_ordered_polynomial_sha256": digest_expressions(source_x),
        "mutation_controls_rejected": ["omit_positive_Q_on_selected_X"],
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "PARTNER-RETIREMENT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
