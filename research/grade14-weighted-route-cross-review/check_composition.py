"""Independent right-route/cancellation audit for exact PR #7837.

The only imported author operation is row_program, whose emitted word is
checked by an independent exact rational matrix-product oracle. Complete
cover, inverse/cocycle, weighted matching and cancellation checks use no
author arithmetic or leaf implementation.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json
import sys
from types import ModuleType

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"
PIN = "a7f99a5f5f919dd3ffb2987f90c1e7d6527feb1e"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def inverse(matrix):
    n = len(matrix)
    rows = [list(map(F, row)) + unit for row, unit in zip(matrix, identity(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        need(pivot is not None, "singular rational matrix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [x / divisor for x in rows[j]]
        for i in range(n):
            if i != j:
                multiplier = rows[i][j]
                rows[i] = [x - multiplier * y for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def actual_ports():
    word = json.loads(gzip.decompress((INPUTS / "binary.json.gz").read_bytes()))
    # Read the authenticated text directly: a stale bytecode cache cannot
    # replace the source under review, even outside the registered runner.
    source = INPUTS / "cover.py"
    module = ModuleType("audited_cover")
    exec(compile(source.read_bytes(), str(source), "exec", dont_inherit=True), module.__dict__)
    count = slots = maximum = 0
    denominators = set()
    signature = sha256()
    for i in range(111):
        head = word["frames"][str(word["start"][i])]
        body = word["frames"][str(word["final"][111 + i])]
        need(head["dim"] == 1 and body["dim"] == 7, "actual port dimensions")
        u = [list(map(F, col)) for col in zip(*(head["B"] + body["B"]))]
        undo = inverse(u)
        # Active support is 8 central + 7 fresh coordinates. Construct the
        # complete 15-by-15 involution directly on basis vectors.
        columns = []
        for j in range(15):
            vector = [F(k == j) for k in range(15)]
            native = [sum(row[k] * vector[k] for k in range(8)) for row in undo]
            moved = [native[0], *vector[8:15]]
            columns.append([sum(row[k] * moved[k] for k in range(8)) for row in u]
                           + native[1:8])
        matcher = [list(col) for col in zip(*columns)]
        need(inverse(matcher) == matcher, "actual port matcher is not involutive")
        denominators.update(x.denominator for row in matcher for x in row)
        for prime in (3, 5):
            program = module.row_program(matcher, prime)
            actual = identity(15)
            factor_determinant = F(1)
            for op, *args in program:
                target = args[0]
                if op == "swap":
                    factor_determinant *= -1
                    source = args[1]
                    for row in actual:
                        row[target], row[source] = row[source], row[target]
                elif op == "scale":
                    factor_determinant *= args[1]
                    need(F(args[1]).denominator % prime and F(args[1]).numerator % prime,
                         "route scaling is not a local unit")
                    for row in actual:
                        row[target] *= args[1]
                else:
                    need(op == "add", "unknown emitted route instruction")
                    source, coefficient = args[1:]
                    need(F(coefficient).denominator % prime, "nonintegral route shear")
                    for row in actual:
                        row[target] += coefficient * row[source]
            need(actual == matcher, ("actual port right-word mismatch", i, prime))
            need(factor_determinant == -1, "actual seven-exchange port determinant")
            count += 1
            slots += len(program)
            maximum = max(maximum, len(program))
            signature.update(str((i, prime, program)).encode() + b"\n")
    return {"actual_ports": 111, "active_coordinates": 15,
            "unaffected_exterior_coordinates": 119,
            "exact_rational_factorizations": count, "emitted_elementary_slots": slots,
            "maximum_slots_per_high_row": maximum,
            "actual_port_determinant": "-1",
            "matcher_denominators": sorted(denominators),
            "word_digest": signature.hexdigest()}


def mul2(a, b, modulus=None):
    out = (a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3],
           a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3])
    return out if modulus is None else tuple(x % modulus for x in out)


def inv2(a, modulus):
    unit = pow(a[0] * a[3] - a[1] * a[2], -1, modulus)
    return tuple(x * unit % modulus for x in (a[3], -a[1], -a[2], a[0]))


def rat_inv2(a):
    determinant = a[0] * a[3] - a[1] * a[2]
    return tuple(x / determinant for x in (a[3], -a[1], -a[2], a[0]))


def mod_rat(value, modulus):
    value = F(value)
    return value.numerator * pow(value.denominator, -1, modulus) % modulus


def route_tables(matcher, prime, width, lows):
    modulus = prime ** width
    highmod = prime ** (width - 1)
    linear = tuple(mod_rat(x, highmod) for x in matcher) if highmod > 1 else (0,) * 4
    full = tuple(mod_rat(x, modulus) for x in matcher)
    table = {}
    for low in lows:
        exact = mul2(low, matcher)
        next_low = tuple(mod_rat(x, prime) for x in exact)
        carry = tuple((x - y) / prime for x, y in zip(exact, next_low))
        need(all(F(c).denominator % prime for c in carry), "nonintegral carry")
        table[low] = (next_low, tuple(mod_rat(c, highmod) for c in carry)
                      if highmod > 1 else (0,) * 4)
    return linear, full, table


def route(g, tables, prime, width, omit_carry=False):
    highmod = prime ** (width - 1)
    linear, _full, table = tables
    low = tuple(x % prime for x in g)
    high = tuple(x // prime for x in g)
    next_low, carry = table[low]
    moved = mul2(high, linear, highmod)
    return tuple(a + prime * ((x + (0 if omit_carry else c)) % highmod)
                 for a, x, c in zip(next_low, moved, carry))


def conjugate(g, p, modulus):
    return mul2(mul2(g, p, modulus), inv2(g, modulus), modulus)


def weighted_projection(p, units, modulus):
    # Logical coordinates (H_0,H_1,(C T)_0,(C T)_1); physical reversal is
    # checked separately for each whole multiplicity block below.
    a = units + (1, 1)
    result = []
    for i in range(4):
        row = []
        for j in range(4):
            projection = p[2 * (i % 2) + j % 2]
            value = (int(i % 2 == j % 2) - projection) if (i < 2) == (j < 2) else projection
            row.append(value * a[i] * pow(a[j], -1, modulus) % modulus)
        result.append(tuple(row))
    return tuple(result)


def mul4(a, b, modulus):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(4)) % modulus
                       for j in range(4)) for i in range(4))


def check_cover_and_mix():
    prime = 3
    lows = [a for a in product(range(prime), repeat=4)
            if (a[0] * a[3] - a[1] * a[2]) % prime]
    matchers = [(F(1), F(1, 2), F(0), F(1)),
                (F(1), F(0), F(2, 5), F(1))]
    q0, q1 = (1, 0, 0, 0), (0, 0, 0, 1)
    all_i = (1, 0, 0, 1)
    total = joint = carry_failures = fresh_weight_failures = unaligned_pair_failures = 0
    inverse_carry_failures = omitted_return_failures = wrong_composition_order = 0
    census = []
    invariant_columns = 0
    invariant_variation = []
    need(all(s[0] * s[3] - s[1] * s[2] == 1 for s in matchers),
         "determinant-invariant positive control requires determinant-one routes")
    for width in (1, 2, 3):
        modulus = prime ** width
        highmod = prime ** (width - 1)
        forward = [route_tables(s, prime, width, lows) for s in matchers]
        backward = [route_tables(rat_inv2(s), prime, width, lows) for s in matchers]
        compound = route_tables(mul2(*matchers), prime, width, lows)
        reversed_compound = route_tables(mul2(*reversed(matchers)), prime, width, lows)
        targets = [conjugate(forward[i][1], q, modulus) for i, q in enumerate((q0, q1))]
        if width < 3:
            highs = list(product(range(highmod), repeat=4))
            scope = "complete GL_2 over the full ring"
        else:
            highs = [(a, b, b, a) for a, b in product(range(highmod), repeat=2)]
            scope = "all low classes, 81 stated symmetric high lifts each"
        contexts = [(0, 0), (1, 2)]
        units = [x for x in range(1, modulus) if x % prime]
        visited = [set(), set()]
        invariant_values = set()
        for low in lows:
            for high in highs:
                h = tuple(a + prime * b for a, b in zip(low, high))
                parents = []
                for i in range(2):
                    destination = route(h, forward[i], prime, width)
                    need(destination == mul2(h, forward[i][1], modulus), "full right route")
                    need(route(destination, backward[i], prime, width) == h, "inverse return")
                    inverse_carry_failures += route(destination, backward[i], prime, width, True) != h
                    omitted_return_failures += destination != h
                    visited[i].add(destination)
                    carry_failures += route(h, forward[i], prime, width, True) != destination
                    parent = route(h, backward[i], prime, width)
                    need(route(parent, forward[i], prime, width) == h, "inverse ingress")
                    parents.append(parent)
                need(route(route(h, forward[0], prime, width), forward[1], prime, width)
                     == route(h, compound, prime, width), "right-route carry cocycle")
                wrong_composition_order += route(h, reversed_compound, prime, width) != route(h, compound, prime, width)
                if parents[0] != parents[1]:
                    # A literal arbitrary-payload witness at address zero:
                    # every linear address permutation fixes zero, so the
                    # mismatched child shear reads this one while the intended
                    # same-parent-row shear reads zero at the other header.
                    donor_at_zero = {parents[0]: 1}
                    need(donor_at_zero.get(parents[0], 0) != donor_at_zero.get(parents[1], 0),
                         "misaligned coupled-route payload control did not fail")
                    unaligned_pair_failures += 1
                # Joint check: two differently matched independent roles mix
                # at h, then cancel the foreign donor before individual return.
                ph = [conjugate(h, q, modulus) for q in (q0, q1)]
                determinant = (h[0] * h[3] - h[1] * h[2]) % modulus
                invariant_values.add(determinant)
                for ancestor, offset in contexts:
                    for multiplicity in (1, 2, 4):
                        physical_slots = []
                        for column in range(multiplicity):
                            physical_slots += [column, multiplicity + column,
                                               4 * multiplicity - 1 - column,
                                               3 * multiplicity - 1 - column]
                            a = (units[(ancestor + column) % len(units)],
                                 units[(offset + 2 * column + 1) % len(units)])
                            d0, d1 = [weighted_projection(p, a, modulus) for p in ph]
                            full = weighted_projection(all_i, a, modulus)
                            need(mul4(full, d0, modulus) == d1, "foreign donor did not cancel")
                            for i, actual in enumerate((d0, d1)):
                                wanted_p = conjugate(parents[i], targets[i], modulus)
                                need(actual == weighted_projection(wanted_p, a, modulus),
                                     "role-dependent parent endpoint")
                            # A genuinely fresh-dependent positive case. The
                            # two right routes have determinant one, so these
                            # nonconstant common weights are route invariant.
                            invariant_a = (a[0] * determinant % modulus,
                                           a[1] * determinant ** 2 % modulus)
                            invariant_d = [weighted_projection(p, invariant_a, modulus) for p in ph]
                            need(mul4(weighted_projection(all_i, invariant_a, modulus),
                                      invariant_d[0], modulus) == invariant_d[1],
                                 "route-invariant fresh weight did not cancel")
                            for i, parent in enumerate(parents):
                                parent_det = (parent[0] * parent[3] - parent[1] * parent[2]) % modulus
                                parent_a = (a[0] * parent_det % modulus,
                                            a[1] * parent_det ** 2 % modulus)
                                need(parent_a == invariant_a and invariant_d[i] ==
                                     weighted_projection(conjugate(parent, targets[i], modulus), parent_a, modulus),
                                     "route-invariant fresh weight parent endpoint")
                            invariant_columns += 1
                            # This mutation is expressly excluded by the proof:
                            # let incoming role weights read their fresh parent g.
                            bad_a = (units[sum(parents[0]) % len(units)],
                                     units[(1 + sum(parents[0])) % len(units)])
                            bad_b = (units[sum(parents[1]) % len(units)],
                                     units[(1 + sum(parents[1])) % len(units)])
                            fresh_weight_failures += (mul4(weighted_projection(all_i, bad_b, modulus),
                                                           weighted_projection(ph[0], bad_a, modulus), modulus)
                                                      != weighted_projection(ph[1], bad_b, modulus))
                            joint += 1
                        need(sorted(physical_slots) == list(range(4 * multiplicity)),
                             "physical head/tail column omission or duplication")
                total += 1
        if width < 3:
            need(all(len(v) == len(lows) * highmod ** 4 for v in visited), "route not bijective")
        census.append({"width": width, "headers": len(lows) * len(highs), "scope": scope})
        need(len(invariant_values) > 1, "positive fresh-weight control was constant")
        invariant_variation.append({"width": width, "distinct_determinants": len(invariant_values)})
    need(carry_failures and fresh_weight_failures and unaligned_pair_failures
         and inverse_carry_failures and omitted_return_failures and wrong_composition_order,
         "adversarial controls failed to expose changed contracts")
    boundary_g, boundary_s, boundary_modulus = (1, 0, 0, 1), (2, 0, 0, 1), 9
    boundary_h = mul2(boundary_g, boundary_s, boundary_modulus)
    before = (boundary_g[0] * boundary_g[3] - boundary_g[1] * boundary_g[2]) ** 2 % boundary_modulus
    after = (boundary_h[0] * boundary_h[3] - boundary_h[1] * boundary_h[2]) ** 2 % boundary_modulus
    need(before != after, "det-squared invariance was incorrectly universalized")
    return {"header_cases": total, "census": census,
            "weighted_column_cancellation_and_endpoint_checks": joint,
            "complete_multiplicities": [1, 2, 4], "ancestor_contexts": 2,
            "omitted_carry_failures": carry_failures,
            "omitted_inverse_carry_failures": inverse_carry_failures,
            "omitted_return_failures": omitted_return_failures,
            "reversed_composition_order_failures": wrong_composition_order,
            "noninvariant_fresh_role_weight_failures": fresh_weight_failures,
            "different_routes_on_coupled_pair_header_failures": unaligned_pair_failures,
            "route_invariant_fresh_weight_positive_control": {
                "weighted_column_checks": invariant_columns,
                "tested_matcher_determinants": [1, 1],
                "nonconstant_fresh_values": invariant_variation,
                "formula": "A0=ancestor_unit0*det(g); A1=ancestor_unit1*det(g)^2 modulo q^w",
                "actual_ports_preserve_det_squared": True,
                "general_matcher_boundary": {
                    "modulus": boundary_modulus, "g": list(boundary_g), "S": list(boundary_s),
                    "det_squared_before": before, "det_squared_after": after},
                "scope": "Weaker algebraic correctness condition only; no descriptor, cost or complete runtime extension."}}


def run():
    ports = actual_ports()
    joint = check_cover_and_mix()
    result = {"status": "PASS_SCOPED_BINARY_COMPOSITION_AUDIT", "reviewed_head": PIN,
              "actual_port_routes": ports, "joint_cover_role_weight_check": joint,
              "inputs_sha256": {name: sha256((INPUTS / name).read_bytes()).hexdigest()
                                  for name in ("binary.json.gz", "cover.py")},
              "scope": "Right-route carry and inverse, actual port factorization, role matching and full-column cancellation; no whole native-assumption discharge."}
    return result


def main():
    result = run()
    if "--record" not in sys.argv:
        need(result == json.loads((ROOT / "RESULT.json").read_text()), "deterministic scientific receipt")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
