"""Check exact relations between the routed centre projections."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json


INTERFACE_SHA256 = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return (a & b).bit_count() & 1


def chart_basis(q):
    zero = next(i for i in range(9) if not ((q >> i) & 1))
    v = q ^ (1 << zero)
    out = []
    for i in range(9):
        x = 1 << i
        if zero and ((x & 1) != ((x >> zero) & 1)):
            x ^= 1 | (1 << zero)
        out.append(x ^ (v if dot(v, x) else 0))
    require(out[0] == q, "The first chart vector is not the port")
    require(all(dot(a, b) == (i == j)
                for i, a in enumerate(out) for j, b in enumerate(out)),
            "A chart basis is not orthogonal")
    return out


def route_column(x, stage, basis):
    if not stage:
        return x
    offset = 9 + 8 * (stage - 1)
    out = x & ~((1 << 9) - 1 | ((1 << 8) - 1) << offset)
    out ^= basis[0] if dot(x, basis[0]) else 0
    for i, v in enumerate(basis[1:]):
        out ^= 1 << (offset + i) if dot(x, v) else 0
        out ^= v if (x >> (offset + i)) & 1 else 0
    return out


def act(matrix, x):
    out = 0
    while x:
        bit = x & -x
        out ^= matrix[bit.bit_length() - 1]
        x ^= bit
    return out


def mul(a, b):
    return tuple(act(a, x) for x in b)


def packed(matrix):
    return b"".join(x.to_bytes(3, "little") for x in matrix)


def gram(columns):
    return [[sum(x * y for x, y in zip(a, b)) for b in columns]
            for a in columns]


def sparse_corner(a, products, row=0):
    out = Counter()
    for i in range(112):
        if not a[row][i]:
            continue
        for j in range(112):
            value = a[row][i] * a[i][j] * a[j][row]
            if value:
                out[products[i, j]] += value
    return {g: value for g, value in out.items() if value}


def sixth_moment(a, routes, products):
    # The coefficient at each group element is a sum of rank-one matrices.
    # Store their two endpoint indices and integer coefficients.
    coefficients = {}
    numerator = 0
    for i in range(112):
        for j in range(112):
            if not a[i][j]:
                continue
            left = products[i, j]
            for k in range(112):
                scale = a[i][j] * a[j][k]
                if not scale:
                    continue
                key = packed(mul(left, routes[k]))
                old = coefficients.setdefault(key, [])
                numerator += 16 * scale * scale
                numerator += 2 * scale * sum(
                    value * a[i][u] * a[k][v] for u, v, value in old)
                old.append((i, k, scale))
    return Q(numerator, 56 ** 6), {
        "group_elements": len(coefficients),
        "walks": sum(map(len, coefficients.values())),
        "collision_distribution": dict(sorted(Counter(map(len, coefficients.values())).items())),
    }


def run(interface, with_sixth_moment=False):
    raw = interface.read_bytes()
    require(sha256(raw).hexdigest() == INTERFACE_SHA256, "The interface source pin changed")
    data = json.loads(raw)
    ports = data["ports"]
    columns = [tuple(int(data["R"][r].get(str(i), "0")) for r in range(8))
               for i in range(112)]
    a = gram(columns)
    require(all(sum(columns[i][r] * columns[i][s] for i in range(112)) ==
                56 * (r == s) for r in range(8) for s in range(8)), "R R^T")
    require(Counter(v for row in a for v in row) ==
            {0: 6608, 2: 3920, -2: 1904, 4: 112}, "The Gram entry counts")
    require(all(not a[i][j] or i == j or not dot(ports[i], ports[j])
                for i in range(112) for j in range(112)), "The edge orthogonality")
    bases = [chart_basis(q) for q in ports]
    routes = [tuple(route_column(1 << i, 1, basis) for i in range(17))
              for basis in bases]
    identity = tuple(1 << i for i in range(17))
    require(all(mul(g, g) == identity for g in routes), "A route is not an involution")
    products = {(i, j): mul(routes[i], routes[j])
                for i in range(112) for j in range(112) if a[i][j]}
    collisions = {}
    for pair, g in products.items():
        collisions.setdefault(g, []).append(pair)
    require(Counter(map(len, collisions.values())) == {1: 5824, 112: 1},
            "The edge products are not distinct")
    require(collisions[identity] == [(i, i) for i in range(112)],
            "An edge product is the identity")
    # Check the kernel and image certificates of every nonidentity local block.
    for (i, j), g in products.items():
        if i == j:
            continue
        local = tuple(x & 511 for x in g[:9])
        require(act(local, ports[j]) == 0, "The local kernel certificate")
        require(all(not dot(ports[i], x) for x in local), "The local image certificate")
        require(len({act(local, x) for x in range(512)}) == 256, "The local block rank")

    corner = sparse_corner(a, products)
    g01 = products[0, 1]
    require(corner[g01] == 16, "The isoclinic witness")
    left_commutator = Counter()
    for i in range(112):
        if a[0][i]:
            left_commutator[products[i, 0]] += a[0][i] ** 2
            left_commutator[products[0, i]] -= a[0][i] ** 2
    require(left_commutator[g01] == -4, "The commutator witness")
    conjugated = {mul(mul(routes[0], g), routes[0]): value
                  for g, value in corner.items()}
    defect = {g: corner.get(g, 0) - conjugated.get(g, 0)
              for g in corner.keys() | conjugated.keys()
              if corner.get(g, 0) != conjugated.get(g, 0)}
    require(bool(defect), "The braid obstruction did not hold")
    witness = min(defect)

    # The coefficient of identity defines the normalized trace on a regular cover.
    second_numerator = sum(a[i][j] ** 2 for i in range(112) for j in range(112))
    second_numerator *= 16
    second_numerator += 16 * sum(a[i][j] ** 2
                                 for i in range(112) for j in range(112) if i != j)
    moment1 = Q(112 * 16, 56 ** 2)
    moment2 = Q(second_numerator, 56 ** 4)
    require((moment1, moment2) == (Q(4, 7), Q(27, 343)), "The trace moments")
    difference_second = 16 - 2 * moment1
    difference_fourth = 16 - 4 * moment1 + 2 * moment2
    rank_bound = difference_second ** 2 / difference_fourth
    require(rank_bound == Q(2912, 183), "The rank bound")

    star_checks = 0
    identity73 = tuple(1 << i for i in range(73))
    for basis in bases:
        stages = [identity73] + [tuple(route_column(1 << i, s, basis) for i in range(73))
                                 for s in range(1, 9)]
        for s in range(1, 9):
            for t in range(s + 1, 9):
                expected = list(identity73)
                for k in range(8):
                    i, j = 9 + 8 * (s - 1) + k, 9 + 8 * (t - 1) + k
                    expected[i], expected[j] = expected[j], expected[i]
                require(mul(mul(stages[s], stages[t]), stages[s]) == tuple(expected),
                        "The star-transposition relation")
                star_checks += 1

    result = {
        "status": "PASS_EXACT_ROUTED_PROJECTION_ALGEBRA",
        "interface_sha256": INTERFACE_SHA256,
        "source_base": data["base"],
        "arithmetic": "Integer group coefficients and Fraction",
        "representation": "Full binary orthogonal matrices; no phase specialization",
        "gram_entry_distribution": dict(sorted(Counter(v for row in a for v in row).items())),
        "distinct_nonidentity_edge_products": 5824,
        "star_transposition_checks": star_checks,
        "corner_port": ports[0],
        "noncommutation_witness": {
            "group_columns": list(g01),
            "coefficient_in_commutator_P0_P1_corner_0_0": str(Q(-4, 56 ** 2)),
        },
        "nonisoclinic_witness": {
            "group_columns": list(g01),
            "coefficient_in_P0_P1_P0_corner_0_0": str(Q(16, 56 ** 3)),
            "coefficient_in_any_scalar_multiple_of_P0": "0",
        },
        "nonbraid_witness": {
            "group_columns": list(witness),
            "coefficient_in_P0_P1_P0_minus_P1_P0_P1_corner_0_0": str(Q(defect[witness], 56 ** 3)),
            "coefficient_in_K0_K1_K0_minus_K1_K0_K1_corner_0_0": str(Q(-14 ** 3 * defect[witness], 56 ** 3)),
        },
        "normalized_trace_P0": "8",
        "normalized_trace_P0_P1": str(moment1),
        "normalized_trace_P0_P1_squared": str(moment2),
        "normalized_trace_P0_minus_P1_squared": str(difference_second),
        "normalized_trace_P0_minus_P1_fourth_power": str(difference_fourth),
        "common_range_dimension_upper_bound_per_cover_element": "8/183",
        "equal_J_subspace_codimension_lower_bound_per_cover_element": str(rank_bound),
        "scope": "Exact group-algebra relations and a full-cover dimension bound. No changed supplier, paid router, or kappa claim.",
    }
    if with_sixth_moment:
        moment3, details = sixth_moment(a, routes, products)
        result["normalized_trace_P0_P1_cubed"] = str(moment3)
        result["sixth_moment_calculation"] = details
        h3 = (moment1 * moment3 - moment2 ** 2) / (moment1 - 2 * moment2 + moment3)
        result["common_range_dimension_upper_bound_from_third_moment"] = str(h3)
        result["equal_J_subspace_codimension_lower_bound_from_third_moment"] = str(16 - 2 * h3)
        result["isoclinic_braid_third_moment_required"] = str((1 + Q(13, 196)) * moment2 - Q(13, 196) * moment1)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sixth-moment", action="store_true")
    args = parser.parse_args()
    result = run(args.interface, args.sixth_moment)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    print("edge_products=5824 TL=false commute=false braid=false")
    print("trace_PQ=4/7 trace_PQPQ=27/343 common_J_codimension>=2912/183")
