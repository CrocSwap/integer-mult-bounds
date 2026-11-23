"""Fixed-prime, all-width rational descriptors for the retained full-GL route.

The caller supplies an odd prime. No prime is chosen for the astronomical
selected compiler. Coefficients are fixed rationals, not width-specific
residues; only the pivot branch can depend on q.
"""
from fractions import Fraction as F
from math import gcd
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def multiply(a, b):
    columns = transpose(b)
    return [[sum(x*y for x, y in zip(row, col)) for col in columns] for row in a]


def inverse(a):
    n = len(a)
    data = [list(row)+eye(n)[i] for i, row in enumerate(a)]
    for k in range(n):
        r = next((i for i in range(k, n) if data[i][k]), None)
        need(r is not None, "singular source basis")
        data[k], data[r] = data[r], data[k]
        pivot = data[k][k]
        data[k] = [x/pivot for x in data[k]]
        for i in range(n):
            if i != k:
                coefficient = data[i][k]
                data[i] = [x-coefficient*y for x, y in zip(data[i], data[k])]
    return [row[n:] for row in data]


def dyadic(x):
    d = F(x).denominator
    return d & (d-1) == 0


def dyadic_unit(x):
    x = abs(F(x))
    return x != 0 and dyadic(x) and x.numerator & (x.numerator-1) == 0


def inverse_operation(operation):
    kind, *args = operation
    if kind == "swap":
        return list(operation)
    if kind == "scale":
        return [kind, args[0], str(1/F(args[1]))]
    need(kind == "add", "known elementary operation")
    return [kind, args[0], args[1], str(-F(args[2]))]


def compile_route(s, q):
    n = len(s)
    need(type(q) is int and q >= 3 and q % 2 == 1, "an odd prime is a theorem premise")
    need(n >= 1 and all(len(row) == n for row in s), "nonempty square matcher")
    s = [[F(x) for x in row] for row in s]
    need(all(dyadic(x) for row in s for x in row), "dyadic matcher entries")
    a = transpose(s)
    elimination = []
    pivots = []
    determinant = F(1)
    for k in range(n):
        r = next((i for i in range(k, n) if gcd(a[i][k].numerator, q) == 1), None)
        need(r is not None, "no q-unit in the remaining pivot column")
        need(gcd(a[r][k].denominator, q) == 1, "q-integral pivot")
        if r != k:
            a[k], a[r] = a[r], a[k]
            elimination.append(["swap", k, r])
            determinant = -determinant
        pivot = a[k][k]
        determinant *= pivot
        pivots.append({"column": k, "selected_row": r, "value": str(pivot)})
        if pivot != 1:
            multiplier = 1/pivot
            elimination.append(["scale", k, str(multiplier)])
            a[k] = [x*multiplier for x in a[k]]
        for i in range(n):
            if i != k and a[i][k]:
                coefficient = -a[i][k]
                elimination.append(["add", i, k, str(coefficient)])
                a[i] = [x+coefficient*y for x, y in zip(a[i], a[k])]
    need(a == eye(n), "complete rational elimination")
    need(dyadic_unit(determinant), "complete matcher determinant must be a dyadic unit")
    forward = [inverse_operation(op) for op in reversed(elimination)]
    # Each word acts on a high row regarded as a column. Forward is S^t.
    reverse = elimination
    denominator = max(x.denominator for row in s for x in row)
    integer_matrix = [[int(x*denominator) for x in row] for row in s]
    maximum = max(1, *(abs(x) for row in integer_matrix for x in row))
    exponent = denominator.bit_length()-1
    height_bound = exponent+n*(maximum.bit_length()+n.bit_length())+1
    swap_count = sum(op[0] == "swap" for op in forward)
    add_count = sum(op[0] == "add" for op in forward)
    upper_count = sum(op[0] == "add" and op[1] < op[2] for op in forward)
    scale_count = sum(op[0] == "scale" for op in forward)
    return {"q": q, "dimension": n, "determinant": str(determinant), "pivots": pivots,
            "forward": forward, "inverse": reverse,
            "coefficient_bits_bound": height_bound,
            "input_common_denominator": str(denominator), "cleared_entry_maximum": str(maximum),
            "carry_numerator_bound": str(n*maximum+denominator),
            "source_counts_per_direction": {
                "ordinary_interchanges": n*(swap_count+2*upper_count),
                "ordinary_interchanges_all_additions_charged_upper": n*(swap_count+2*add_count),
                "ordered_shifts_including_all_carries": n*add_count+n*n,
                "rational_unit_scalings": n*scale_count,
                "low_selection_and_scans": "fixed finite additional source charges"},
            "elementary_counts_per_high_row": {"swaps": swap_count, "adds": add_count,
                                                "upper_adds": upper_count, "scales": scale_count}}


def matrix_record(identifier, matrix, provenance):
    return {"id": identifier, "matrix": [[str(x) for x in row] for row in matrix], "provenance": provenance}


def catalogue():
    bases = json.loads((HERE/"retained/INDEPENDENT-BASES.json").read_text())
    first = {}
    records = []
    for index, item in enumerate(bases):
        basis = [[F(x) for x in row] for row in item["alternative_basis"]]
        rank = item["rank"]
        first.setdefault(rank, (index, inverse(basis)))
        reference, right_inverse = first[rank]
        records.append(matrix_record(f"difference-{index}", multiply(basis, right_inverse),
                       {"kind": "complete_nested_difference_matcher", "left_index": index,
                        "right_index": reference, "nested_pair": item["pair"], "rank": rank}))
    receipt = json.loads((HERE/"retained/EFREE-RESULT.json").read_text())
    order = (0, *range(8, 15), *range(1, 8))
    permutation = [[F(i == order[j]) for j in range(15)] for i in range(15)]
    for index, chart in enumerate(receipt["source"]["charts"]):
        basis = [[F(x) for x in row] for row in chart["basis"]]
        extended = [row+[F(0)]*7 for row in basis]+[[F(0)]*8+row for row in eye(7)]
        route = multiply(multiply(extended, permutation), inverse(extended))
        records.append(matrix_record(f"stage-{index}", route,
                       {"kind": "essential_selected_15_axis_stage_route", "chart_index": index,
                        "input_frame": chart["input_frame"], "output_frame": chart["output_frame"]}))
    for name, matrix in (
        ("pivot-control", [[3, 1], [2, 1]]),
        ("nonunit-shear-control", [[1, 3], [0, 1]]),
        ("fractional-carry-control", [[F(1, 2), F(1, 4)], [0, 2]]),
        ("order-control", [[1, 2], [3, 7]]),
        ("dimension-one", [[F(-1, 2)]]),
    ):
        records.append(matrix_record(name, matrix, {"kind": "explicit_boundary_control"}))
    return records


def main():
    records = catalogue()
    routes = []
    for item in records:
        matrix = [[F(x) for x in row] for row in item["matrix"]]
        for q in (3, 5, 7, 11):
            descriptor = compile_route(matrix, q)
            descriptor["matrix_id"] = item["id"]
            descriptor["coupled_roles"] = {"X": item["id"]+f"@{q}", "Y": item["id"]+f"@{q}"}
            routes.append(descriptor)
    output = {"schema": 1, "orientation": "Each high row x is updated to xS; forward word acts on x^t by S^t.",
              "width_parameter_absent_from_constructor": True,
              "matrices": records, "routes": routes}
    blob = json.dumps(output, sort_keys=True, separators=(",", ":")).encode()
    (HERE/"DESCRIPTORS.json.gz").write_bytes(gzip.compress(blob, compresslevel=9, mtime=0))
    examples = {"matrices": [m for m in records if m["id"] in ("pivot-control", "nonunit-shear-control", "fractional-carry-control")],
                "routes": [r for r in routes if r["matrix_id"] in ("pivot-control", "nonunit-shear-control", "fractional-carry-control") and r["q"] in (3, 5)]}
    (HERE/"EXAMPLES.json").write_text(json.dumps(examples, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"matrices": len(records), "routes": len(routes), "uncompressed_bytes": len(blob),
                      "descriptor_bytes": (HERE/"DESCRIPTORS.json.gz").stat().st_size}))


if __name__ == "__main__":
    main()
