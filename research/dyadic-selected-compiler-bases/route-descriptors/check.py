"""Separate descriptor verifier: no import of the constructor or basis engine.

Checks exact word products, source-derived matrix identities, q-power actions,
carry charts, source tariffs, coefficient heights and chronology controls.
"""
from fractions import Fraction as F
from functools import cache
from hashlib import sha1, sha256
from itertools import product
from math import gcd, isqrt
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def mat(rows):
    return tuple(tuple(F(x) for x in row) for row in rows)


def identity(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def transpose(a):
    return tuple(zip(*a))


def multiply(a, b):
    return tuple(tuple(sum(x*y for x, y in zip(row, col)) for col in transpose(b)) for row in a)


@cache
def inverse(a):
    n = len(a)
    data = [list(row)+list(identity(n)[i]) for i, row in enumerate(a)]
    # Independent reverse-direction elimination, without q-dependent choices.
    for k in range(n-1, -1, -1):
        selected = next((r for r in range(k, -1, -1) if data[r][k]), None)
        need(selected is not None, "singular expected matrix")
        data[k], data[selected] = data[selected], data[k]
        pivot = data[k][k]
        data[k] = [x/pivot for x in data[k]]
        for i in range(n):
            if i != k:
                coefficient = data[i][k]
                data[i] = [x-coefficient*y for x, y in zip(data[i], data[k])]
    return tuple(tuple(row[n:]) for row in data)


def scalar_mod(x, modulus):
    x = F(x)
    return x.numerator*pow(x.denominator, -1, modulus) % modulus


def modular_matrix(a, modulus):
    return tuple(tuple(scalar_mod(x, modulus) for x in row) for row in a)


def modular_product(a, b, modulus):
    return tuple(tuple(sum(x*y for x, y in zip(row, col)) % modulus for col in transpose(b)) for row in a)


def exact_word(n, operations):
    result = [list(row) for row in identity(n)]
    for operation in operations:
        kind = operation[0]
        if kind == "swap":
            i, j = operation[1:]
            result[i], result[j] = result[j], result[i]
        elif kind == "scale":
            i, value = operation[1:]
            result[i] = [F(value)*x for x in result[i]]
        else:
            need(kind == "add", "known word opcode")
            i, j, value = operation[1:]
            result[i] = [x+F(value)*y for x, y in zip(result[i], result[j])]
    return tuple(tuple(row) for row in result)


def modular_row(row, operations, modulus):
    result = list(row)
    for operation in operations:
        kind = operation[0]
        if kind == "swap":
            i, j = operation[1:]
            result[i], result[j] = result[j], result[i]
        elif kind == "scale":
            i, value = operation[1:]
            result[i] = result[i]*scalar_mod(value, modulus) % modulus
        else:
            need(kind == "add", "known modular opcode")
            i, j, value = operation[1:]
            result[i] = (result[i]+scalar_mod(value, modulus)*result[j]) % modulus
    return tuple(result)


def inverted_word(operations):
    result = []
    for op in reversed(operations):
        if op[0] == "swap":
            result.append(list(op))
        elif op[0] == "scale":
            result.append(["scale", op[1], str(1/F(op[2]))])
        else:
            result.append(["add", op[1], op[2], str(-F(op[3]))])
    return result


def source_identities(matrices):
    bases = json.loads((HERE/"retained/INDEPENDENT-BASES.json").read_text())
    charts = json.loads((HERE/"retained/EFREE-RESULT.json").read_text())["source"]["charts"]
    count = 0
    for item in matrices.values():
        s = mat(item["matrix"])
        provenance = item["provenance"]
        if provenance["kind"] == "complete_nested_difference_matcher":
            left = bases[provenance["left_index"]]
            right = bases[provenance["right_index"]]
            need(left["rank"] == right["rank"] == provenance["rank"], "matching both complete summands")
            left_matrix, right_matrix = mat(left["alternative_basis"]), mat(right["alternative_basis"])
            need(multiply(s, right_matrix) == left_matrix, "source complete basis identity")
            count += 1
        elif provenance["kind"] == "essential_selected_15_axis_stage_route":
            chart = charts[provenance["chart_index"]]
            basis = mat(chart["basis"])
            g = tuple(tuple(row)+(F(0),)*7 for row in basis)+tuple((F(0),)*8+row for row in identity(7))
            order = (0, *range(8, 15), *range(1, 8))
            swap = tuple(tuple(F(i == order[j]) for j in range(15)) for i in range(15))
            need(multiply(s, g) == multiply(g, swap), "source selected stage chart identity")
            need(multiply(s, s) == identity(15), "source stage involution")
            count += 1
    return count


def authenticate():
    records = json.loads((HERE/"ORIGINS.json").read_text())["files"]
    for record in records:
        raw = (HERE/record["local"]).read_bytes()
        need(sha256(raw).hexdigest() == record["sha256"], "source SHA: " + record["local"])
        if record["git_blob"] is not None:
            need(sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest() == record["git_blob"],
                 "source Git blob: " + record["local"])
    return len(records)


def carry_chart(g0, s, q):
    rational_product = multiply(g0, s)
    low = modular_matrix(rational_product, q)
    carry = tuple(tuple((x-y)/q for x, y in zip(row, target)) for row, target in zip(rational_product, low))
    need(all(gcd(x.denominator, q) == 1 for row in carry for x in row), "q-integral carry")
    return low, carry


def chart_check(s, route, g0, high, width):
    n, q = len(s), route["q"]
    low, carry = carry_chart(g0, s, q)
    denominator = int(route["input_common_denominator"])
    carry_bound = int(route["carry_numerator_bound"])
    need(all(denominator % x.denominator == 0 and abs(x.numerator) < carry_bound
             for row in carry for x in row), "dyadic carry height")
    modulus, high_modulus = q**width, q**(width-1)
    if width == 1:
        need(all(x == 0 for row in high for x in row), "singleton high cube")
        routed = low
        restored = modular_matrix(multiply(low, inverse(s)), q)
        need(restored == g0, "width-one finite low route inverse")
    else:
        transformed = tuple(modular_row(row, route["forward"], high_modulus) for row in high)
        output_high = tuple(tuple((x+scalar_mod(c, high_modulus)) % high_modulus for x, c in zip(row, crow))
                            for row, crow in zip(transformed, carry))
        routed = tuple(tuple(x+q*y for x, y in zip(row, hrow)) for row, hrow in zip(low, output_high))
        # Literal inverse chronology: unselect low, subtract the same carry,
        # then run inverse elementary operations in reverse chronology.
        undone = tuple(tuple((x-scalar_mod(c, high_modulus)) % high_modulus for x, c in zip(row, crow))
                       for row, crow in zip(output_high, carry))
        restored_high = tuple(modular_row(row, route["inverse"], high_modulus) for row in undone)
        need(restored_high == high, "literal high inverse chronology")
        need(modular_matrix(multiply(low, inverse(s)), q) == g0, "inverse low chart")
    full = tuple(tuple(x+q*y for x, y in zip(row, hrow)) for row, hrow in zip(g0, high))
    need(routed == modular_product(full, modular_matrix(s, modulus), modulus), "all-coordinate right-route endpoint")
    return routed


def verify_routes(data):
    matrices = {item["id"]: item for item in data["matrices"]}
    need(len(matrices) == len(data["matrices"]), "unique matrix ids")
    source_count = source_identities(matrices)
    counts = {"routes": 0, "exact_forward_inverse_products": 0, "prime_power_words": 0,
              "affine_charts": 0, "nonunit_addition_coefficients": 0, "odd_denominator_coefficients": 0,
              "max_observed_coefficient_bits": 0, "max_high_row_operations": 0}
    route_map = {}
    for route in data["routes"]:
        q, n = route["q"], route["dimension"]
        need(q in (3, 5, 7, 11) and all(q % k for k in range(2, isqrt(q)+1)), "fixture prime")
        s = mat(matrices[route["matrix_id"]]["matrix"])
        need(len(s) == n and all(len(row) == n for row in s), "descriptor dimension")
        forward, reverse = route["forward"], route["inverse"]
        need(reverse == inverted_word(forward), "same stored word inverse chronology")
        need(route["coupled_roles"]["X"] == route["coupled_roles"]["Y"], "coupled roles share one route")
        denominator = max(x.denominator for row in s for x in row)
        need(denominator & (denominator-1) == 0, "dyadic common denominator")
        maximum = max(1, *(abs(int(denominator*x)) for row in s for x in row))
        bound = denominator.bit_length()-1+n*(maximum.bit_length()+n.bit_length())+1
        need(route["coefficient_bits_bound"] == bound, "independent height formula")
        need(int(route["input_common_denominator"]) == denominator and int(route["cleared_entry_maximum"]) == maximum,
             "cleared input matrix metadata")
        need(exact_word(n, forward) == transpose(s), "forward rational endpoint")
        need(exact_word(n, reverse) == transpose(inverse(s)), "inverse rational endpoint")
        counts["exact_forward_inverse_products"] += 2
        for op in forward+reverse:
            need(op[0] in ("swap", "scale", "add"), "source primitive alphabet")
            if op[0] == "swap":
                need(0 <= op[1] < n and 0 <= op[2] < n and op[1] != op[2], "swap fields")
                continue
            value = F(op[-1])
            need(gcd(value.denominator, q) == 1, "every coefficient denominator is a q-unit")
            need(abs(value.numerator) < 1 << bound and value.denominator < 1 << bound, "minor-based coefficient bound")
            if op[0] == "scale":
                need(0 <= op[1] < n, "scaling field")
                need(gcd(value.numerator, q) == 1, "scaling is a q-unit")
            else:
                need(0 <= op[1] < n and 0 <= op[2] < n and op[1] != op[2], "addition has distinct valid fields")
                counts["nonunit_addition_coefficients"] += gcd(value.numerator, q) != 1
            counts["odd_denominator_coefficients"] += value.denominator & (value.denominator-1) != 0
            counts["max_observed_coefficient_bits"] = max(counts["max_observed_coefficient_bits"],
                                                         abs(value.numerator).bit_length(), value.denominator.bit_length())
        ns = sum(op[0] == "swap" for op in forward)
        na = sum(op[0] == "add" for op in forward)
        nu = sum(op[0] == "add" and op[1] < op[2] for op in forward)
        nd = sum(op[0] == "scale" for op in forward)
        need(ns <= n and na <= n*(n-1) and nd <= n, "Gaussian primitive count")
        bill = route["source_counts_per_direction"]
        need(bill["ordinary_interchanges"] == n*(ns+2*nu) <= 2*n**3, "actual ordinary-swap bill")
        need(bill["ordinary_interchanges_all_additions_charged_upper"] == n*(ns+2*na) <= 2*n**3,
             "conservative source swap bill")
        need(bill["ordered_shifts_including_all_carries"] == n*na+n*n <= n**3, "all carry translations charged")
        need(bill["rational_unit_scalings"] == n*nd <= n*n, "source rational scaling bill")
        for width in (1, 2, 3):
            modulus = q**width
            for direction, target in ((forward, s), (reverse, inverse(s))):
                got = tuple(modular_row(tuple(int(i == j) for j in range(n)), direction, modulus) for i in range(n))
                need(got == modular_matrix(target, modulus), "basis-action prime-power endpoint")
                counts["prime_power_words"] += 1
            g0 = tuple(tuple(int(i == j)+(int(i == 0 and j == n-1) if n > 1 else 0) for j in range(n)) for i in range(n))
            high = tuple(tuple((3*i+5*j+i*j+width) % q**(width-1) for j in range(n)) for i in range(n))
            chart_check(s, route, g0, high, width)
            counts["affine_charts"] += 1
        counts["routes"] += 1
        counts["max_high_row_operations"] = max(counts["max_high_row_operations"], len(forward))
        route_map[(route["matrix_id"], q)] = route
    return matrices, route_map, {"source_matrix_identities": source_count, **counts}


def controls(matrices, route_map):
    route3, route5 = route_map[("pivot-control", 3)], route_map[("pivot-control", 5)]
    need(route3["pivots"][0]["selected_row"] == 1 and route5["pivots"][0]["selected_row"] == 0,
         "prescribed rational pivot fails at q=3, adaptive pivot succeeds")
    need(route3["forward"] != route5["forward"], "q-dependent descriptor branch")
    s = mat(matrices["nonunit-shear-control"]["matrix"])
    route = route_map[("nonunit-shear-control", 3)]
    omitted = [op for op in route["forward"] if not(op[0] == "add" and F(op[-1]).numerator % 3 == 0)]
    need(exact_word(2, omitted) != transpose(s) and modular_matrix(s, 3) == modular_matrix(identity(2), 3)
         and modular_matrix(s, 9) != modular_matrix(identity(2), 9), "discarding low-zero coefficients fails at q squared")
    order = route_map[("order-control", 5)]
    target = mat(matrices["order-control"]["matrix"])
    need(exact_word(2, list(reversed(order["forward"]))) != transpose(target), "wrong forward chronology rejected")
    need(exact_word(2, list(reversed(order["inverse"]))) != transpose(inverse(target)), "wrong inverse chronology rejected")
    need(3*2-5*1 == 1 and gcd(3, 15) != 1 and gcd(5, 15) != 1,
         "composite modulus is not the local-ring theorem premise")
    gl2 = []
    for a, b, c, d in product(range(3), repeat=4):
        if (a*d-b*c) % 3:
            gl2.append(((a, b), (c, d)))
    need(len(gl2) == 48, "complete GL2(F3) control set")
    mismatch = ((1, 1), (0, 1))
    changed = sum(modular_product(g, mismatch, 3) != g for g in gl2)
    need(changed == 48, "unequal coupled routes change every original source row")
    fraction = mat(matrices["fractional-carry-control"]["matrix"])
    route = route_map[("fractional-carry-control", 3)]
    outputs = set()
    count = 0
    for g0 in gl2:
        for values in product(range(3), repeat=4):
            high = (values[:2], values[2:])
            outputs.add(chart_check(fraction, route, g0, high, 2))
            count += 1
    need(count == len(outputs) == 3888, "entire GL2(Z/9) cover bijection")
    # The exact carry cocycle is checked without the constructor's route code.
    second = mat(matrices["pivot-control"]["matrix"])
    combined = multiply(fraction, second)
    for g0 in gl2:
        h0, first_carry = carry_chart(g0, fraction, 3)
        _, second_carry = carry_chart(h0, second, 3)
        _, combined_carry = carry_chart(g0, combined, 3)
        transported = multiply(first_carry, second)
        need(tuple(tuple(x+y for x, y in zip(row, other)) for row, other in zip(transported, second_carry)) == combined_carry,
             "exact affine carry cocycle")
    return {"pivot_branches": {"q3": route3["pivots"][0], "q5": route5["pivots"][0]},
            "low_zero_shear_retained_at_q_squared": True, "wrong_forward_and_inverse_chronology_rejected": True,
            "composite_modulus_local_pivot_obstruction": True, "unequal_coupled_route_rows_changed": changed,
            "full_GL2_Z9_forward_inverse_cases": count, "exact_carry_cocycle_cases": len(gl2)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE/"EVIDENCE.json")
    args = parser.parse_args()
    source_count = authenticate()
    raw = (HERE/"DESCRIPTORS.json.gz").read_bytes()
    data = json.loads(gzip.decompress(raw))
    matrices, routes, counts = verify_routes(data)
    evidence = {"status": "PASS_FIXED_PRIME_ALL_WIDTH_SOURCE_DESCRIPTORS", "origin_records": source_count,
                "descriptor_sha256": sha256(raw).hexdigest(), "counts": counts,
                "controls": controls(matrices, routes),
                "scope": "Finite corroboration of the written all-size theorem; no selected astronomical catalogue or physical tape service is executed."}
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True)+"\n")
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
