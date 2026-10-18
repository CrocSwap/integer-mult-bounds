#!/usr/bin/env python3
"""Source-bound QQ16 third-moment certificate. Apache-2.0."""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKET = "research/joint-query/certificate.json.gz"
PINS = {
    PACKET: "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7",
    "research/joint-query/evidence/QQ16-SELECTED-WITNESS.md":
        "52f2ee565320f05282c637aa79eee100606c24240b1b5866f0c8d62e7913c9fc",
    "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json":
        "e35e5868a1322e406191079c0675975b139692ba50b1e2e5fb8a40b6480519f4",
    "research/joint-query/evidence/QQ16-RATIONAL-OBSERVATION-REVIEW.md":
        "9a06ff40830ef80d3566fce77c78639cb64d519d487a0a7f57d543c3146e2c49",
}
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
IDENTITY = tuple(1 << i for i in range(25))
MARKER = "PASS_QQ16_THIRD_MOMENT_CAPACITY"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_packet(repo):
    raw_packet = None
    for name, expected in PINS.items():
        path = repo / name
        need(path.is_file() and path.stat().st_size <= 1_048_576,
             "source size: " + name)
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == expected, "source pin: " + name)
        if name == PACKET:
            raw_packet = raw
    need(raw_packet is not None, "missing packet")
    with gzip.GzipFile(fileobj=io.BytesIO(raw_packet)) as stream:
        payload = stream.read(16_777_217)
    need(len(payload) <= 16_777_216, "decompressed packet size")
    return json.loads(payload)


def apply(columns, vector):
    result = 0
    # Every vector is in the validated 25-axis space.
    for _ in range(25):
        if not vector:
            return result
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    need(vector == 0, "binary vector bound")
    return result


def compose(left, right):
    return tuple(apply(left, c) for c in right)


def route(packet, event):
    need(event[0] == "cover_map", "cover map event")
    columns = packet["map_registry"][event[2]]["owner_right_matrix_columns"]
    need(len(columns) == 73 and all(type(c) is int for c in columns),
         "73 integer route columns")
    need(all(0 < c < 1 << 25 for c in columns[:25]), "active route axes")
    need(columns[25:] == [1 << i for i in range(25, 73)],
         "route must fix all 48 spectator axes")
    return tuple(columns[:25])


def packet_data(packet):
    need((tuple(packet["A_ports"]), tuple(packet["T_ports"]),
          tuple(packet["U_ports"])) == (A, T, U), "selected partition")
    need(len(packet["R_rows"]) == 8, "eight query rows")
    R = [[Q(row.get(str(p), 0)) for p in range(112)]
         for row in packet["R_rows"]]
    need(all(x.denominator == 1 for row in R for x in row), "integer query")
    R = [[int(x) for x in row] for row in R]
    routes = [[IDENTITY] * 112]
    for stage in (1, 2):
        word = packet["programs"][f"F_{stage}"]
        need(word[113][:2] == ["cover_sweep", "X_A_fused_query"],
             "forward alignment cut")
        events = word[1:113]
        need([e[1] for e in events] == [["L", p] for p in range(112)],
             "forward port order")
        routes.append([route(packet, e) for e in events])
    need(packet["programs"]["F_0"][1][:2] ==
         ["cover_sweep", "X_A_fused_query"], "stage-zero identity cut")
    word = packet["programs"]["B_1_2"]
    need(len(word) <= 40_000, "backward event bound")
    future = next(i for i, e in enumerate(word)
                  if e[:2] == ["cover_sweep", "future_E_t"])
    current = next(i for i, e in enumerate(word)
                   if e[:2] == ["cover_sweep", "Y_U_from_X_T"])
    for stage, events in ((2, word[future - 112:future]),
                          (1, word[current - 120:current - 8])):
        need([e[1] for e in events] == [["L", 112+p] for p in range(112)],
             "backward port order")
        need([route(packet, e) for e in events] == routes[stage],
             "forward/backward route binding")
    return R, routes


def dot(left, right):
    return sum(x*y for x, y in zip(left, right))


def check_grams(R):
    for ports, scale in ((U, 48), (A, 4), (T, 4)):
        matrix = [[sum(R[i][p]*R[j][p] for p in ports)
                   for j in range(8)] for i in range(8)]
        need(matrix == [[scale*int(i == j) for j in range(8)]
                        for i in range(8)], "query Gram")
    need([sum(R[i][p]**2 for i in range(8)) for p in U] == [4]*96,
         "ordinary column norms")


def check_swap_charts(routes):
    """A separate certificate: chart swaps and disjoint external axes."""
    charts = []
    for p in U:
        chart = tuple(routes[1][p][9+i] for i in range(8))
        need(all(0 < c < 512 for c in chart), "nine-axis chart")
        need(all((x & y).bit_count() % 2 == int(i == j)
                 for i, x in enumerate(chart) for j, y in enumerate(chart)),
             "orthonormal chart")
        for stage, start in ((1, 9), (2, 17)):
            need(tuple(routes[stage][p][start+i] for i in range(8)) == chart,
                 "common stage chart")
            normals = tuple(chart[i] ^ (1 << (start+i)) for i in range(8))
            rebuilt = []
            for axis in range(25):
                x, out = 1 << axis, 1 << axis
                for n in normals:
                    if (x & n).bit_count() % 2:
                        out ^= n
                rebuilt.append(out)
            need(tuple(rebuilt) == routes[stage][p], "literal chart swap")
            need(compose(routes[stage][p], routes[stage][p]) == IDENTITY,
                 "route involution")
        charts.append(chart)
    need(len(set(charts)) == 96, "distinct ordinary charts")
    return len(set(charts))


def pair_products(routes):
    products = []
    for stage in (1, 2):
        grouped = {}
        for p in U:
            for q in U:
                key = compose(routes[stage][p], routes[stage][q])
                grouped.setdefault(key, []).append((p, q))
        need(len(grouped) == 9121, "ordered product census")
        products.append(grouped)
    common = set(products[0]) & set(products[1])
    need(common == {IDENTITY}, "stage-product intersection")
    diagonal = [(p, p) for p in U]
    need(products[0][IDENTITY] == products[1][IDENTITY] == diagonal,
         "identity product fibres")
    return {"ordered_pairs_per_stage": 9216,
            "distinct_products_per_stage": [len(g) for g in products],
            "intersection_size": len(common), "identity_pairs_per_stage": 96}


def moment_certificate(R, routes):
    check_grams(R)
    chart_count = check_swap_charts(routes)
    census = pair_products(routes)
    columns = {p: tuple(R[i][p] for i in range(8)) for p in U}
    for s, t in ((0, 1), (0, 2), (1, 2)):
        relative = {compose(routes[s][p], routes[t][p]) for p in U}
        need(len(relative) == 96, "distinct relative routes")
    cross = sum(dot(columns[p], columns[p])**2 for p in U)
    triple = sum(dot(columns[p], columns[p])**3 for p in U)
    need((cross, triple) == (1536, 6144), "identity coefficients")
    moments = (Q(24), Q(24) + 6*Q(cross, 48**2),
               Q(24) + 18*Q(cross, 48**2) + 6*Q(triple, 48**3))
    need(moments == (Q(24), Q(28), Q(109, 3)), "projector moments")
    m1, m2, m3 = moments
    bound = Q(85, 39)*m1 - Q(248, 169)*m2 + Q(48, 169)*m3
    need(bound == Q(280, 13), "cubic rank bound")
    need(bound - 8 - 13 == Q(7, 13), "positive width-thirteen residual")
    return {"route_census": census, "independent_distinct_swap_charts": chart_count,
            "cross_trace_coefficient": cross, "triple_trace_coefficient": triple,
            "projector_moments_per_owner": list(map(str, moments)),
            "spectral_polynomial_coefficients": ["0", "85/39", "-248/169", "48/169"],
            "stacked_rank_lower_per_owner": str(bound),
            "selected_defect_lower_per_owner": str(bound - 8),
            "width_thirteen_residual_lower_per_owner": str(bound - 21),
            "necessary_integer_record_width": 14}


def rejected_mutations(R, routes):
    count = 0
    bad_R = [row.copy() for row in R]
    bad_R[0][U[0]] += 1
    try:
        check_grams(bad_R)
    except ValueError:
        count += 1
    collapsed = [routes[0], routes[1], routes[1]]
    try:
        pair_products(collapsed)
    except ValueError:
        count += 1
    duplicate = [row.copy() for row in routes]
    duplicate[1][U[1]] = duplicate[1][U[0]]
    duplicate[2][U[1]] = duplicate[2][U[0]]
    try:
        check_swap_charts(duplicate)
    except ValueError:
        count += 1
    need(count == 3, "semantic mutation controls")
    return count


def report(repo):
    R, routes = packet_data(load_packet(repo))
    result = moment_certificate(R, routes)
    result["semantic_controls_rejected"] = rejected_mutations(R, routes)
    result["status"] = MARKER
    result["scope"] = "Regular-cover information dimension; inherited erased-family contract; no native invoice or new kappa."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    args = parser.parse_args()
    actual = report(args.repo)
    expected = json.loads((HERE / "RESULT.json").read_bytes())
    need(actual == expected, "receipt mismatch")
    print(MARKER + " rank>=280|G|/13 defect>=176|G|/13 width>=14 no_new_kappa")


if __name__ == "__main__":
    main()
