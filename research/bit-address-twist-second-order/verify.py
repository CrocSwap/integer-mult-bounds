#!/usr/bin/env python3
"""Exact corroboration of PROOF.md; no predecessor code or external inputs.

Two implementations: bit-packed truncated polynomials, and finite support sets
over F2[(Z/4)^9]. The latter projects only after applying the actual calls.
Python 3.12 stdlib. Krzysztof Wójt, substantial OpenAI Codex assistance.
Apache-2.0. The seven-call pattern is JoyboyBrian's PR4953.
"""

from fractions import Fraction
from itertools import combinations_with_replacement, permutations
import json
import random


DIM = 9
MONOMIALS = [()] + [(i,) for i in range(DIM)] + list(combinations_with_replacement(range(DIM), 2))
INDEX = {m: i for i, m in enumerate(MONOMIALS)}
SIZE = len(MONOMIALS)
MASKS = [sum(1 << i for i, m in enumerate(MONOMIALS) if len(m) == d) for d in range(3)]
ZERO = (0,) * DIM
ONES = (1, 1, 1)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bits(value):
    while value:
        low = value & -value
        yield low.bit_length() - 1
        value ^= low


def unit(i):
    return tuple(int(k == i) for k in range(DIM))


def poly_mul(left, right):
    out = 0
    for i in bits(left):
        for j in bits(right):
            if len(MONOMIALS[i]) + len(MONOMIALS[j]) <= 2:
                out ^= 1 << INDEX[tuple(sorted(MONOMIALS[i] + MONOMIALS[j]))]
    return out


def residue4(value):
    value = Fraction(value)
    need(value.denominator % 2 == 1, "even denominator outside the theorem")
    return value.numerator * pow(value.denominator, -1, 4) % 4


def frame_poly(frame):
    """[A] -> product (1+t_i)^a_i with a_i reduced modulo four."""
    out = 1
    for i, value in enumerate(frame):
        a = residue4(value)
        factor = 1
        if a & 1:
            factor ^= 1 << INDEX[(i,)]
        if a & 2:  # binomial(a,2) mod 2; in particular (1+t)^2=1+t^2.
            factor ^= 1 << INDEX[(i, i)]
        out = poly_mul(out, factor)
    return out


def apply_linear(columns, value):
    out = 0
    for i in bits(value):
        out ^= columns[i]
    return out


def address_map(columns, address):
    return tuple(sum(columns[j][i] * address[j] for j in range(DIM)) % 4 for i in range(DIM))


IDENTITY = tuple(unit(i) for i in range(DIM))


def inverse(columns):
    """Invert an address map over Z/4, using only unit pivots."""
    rows = [[columns[j][i] % 4 for j in range(DIM)] + list(unit(i)) for i in range(DIM)]
    for col in range(DIM):
        pivot = next((r for r in range(col, DIM) if rows[r][col] % 2), None)
        need(pivot is not None, "address map is not invertible modulo two")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = pow(rows[col][col], -1, 4)
        rows[col] = [v * scale % 4 for v in rows[col]]
        for r in range(DIM):
            if r != col:
                scale = rows[r][col]
                rows[r] = [(a - scale * b) % 4 for a, b in zip(rows[r], rows[col])]
    return tuple(tuple(rows[i][DIM + j] for i in range(DIM)) for j in range(DIM))


def permutation_twist(p, q):
    return tuple(unit(3 * p[i // 3] + q[i % 3]) for i in range(DIM))


def pbq_twist(left, right):
    """Columns of A -> left A right, reduced modulo four."""
    return tuple(tuple(residue4(left[r][i] * right[j][s]) for r in range(3) for s in range(3))
                 for i in range(3) for j in range(3))


def polynomial_twist(columns):
    generators = [frame_poly(column) ^ 1 for column in columns]
    out = []
    for monomial in MONOMIALS:
        value = 1
        for i in monomial:
            value = poly_mul(value, generators[i])
        out.append(value)
    return tuple(out)


def call(x, y, frame, twists=(IDENTITY,) * 3):
    need(sum(a * b for a, b in zip(x, y)) % 2 == 1, "non-idempotent paid projector")
    return (x, y, tuple(residue4(a) for a in frame), twists)


def compile_call(item):
    x, y, frame, twists = item
    forward = [polynomial_twist(t) for t in twists]
    backward = [polynomial_twist(inverse(t)) for t in twists]
    delta = frame_poly(frame) ^ 1
    result = []
    for source in range(3):
        for monomial in range(SIZE):
            value = 1 << monomial
            source_poly = backward[source][monomial] if y[source] else 0
            change = poly_mul(delta, source_poly)
            state = [(value if r == source else 0) ^
                     (apply_linear(forward[r], change) if x[r] else 0) for r in range(3)]
            result.append(sum(p << (r * SIZE) for r, p in enumerate(state)))
    return tuple(result)


def group_call(state, item):
    """Separate sparse finite-group implementation, with no polynomial steps."""
    x, y, frame, twists = item
    before = [{address_map(inverse(twists[r]), a) for a in state[r]} for r in range(3)]
    source = set()
    for r in range(3):
        if y[r]:
            source.symmetric_difference_update(before[r])
    shifted = {tuple((a + b) % 4 for a, b in zip(address, frame)) for address in source}
    delta = shifted ^ source
    return [{address_map(twists[r], a) for a in (before[r] ^ delta if x[r] else before[r])}
            for r in range(3)]


def project_group(state):
    out = 0
    for r, support in enumerate(state):
        for address in support:
            out ^= frame_poly(address) << (r * SIZE)
    return out


def run_polynomial(operators, state):
    for op in operators:
        state = apply_linear(op, state)
    return state


def target_operator(frame):
    multiplier = frame_poly(frame)
    return tuple(poly_mul(multiplier, 1 << i) << (r * SIZE) for r in range(3) for i in range(SIZE))


SWAP = permutation_twist((1, 0, 2), (1, 0, 2))


def witness_calls(private_twist=SWAP, diagonal_frame=None):
    if diagonal_frame is None:
        diagonal_frame = unit(8)
    result = [call(ONES, ONES, unit(0))]
    for s in range(3):
        e = tuple(int(r == s) for r in range(3))
        twists = tuple(IDENTITY if r == s else private_twist for r in range(3))
        result += [call(ONES, e, unit(4), twists), call(e, e, diagonal_frame)]
    return result


def direct_calls():
    return [call(tuple(int(r == s) for r in range(3)), tuple(int(r == s) for r in range(3)), unit(i))
            for s in range(3) for i in (0, 4, 8)]


def rank_binary(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def check_ring():
    rng = random.Random(4953)
    for i in range(DIM):
        t = 1 << INDEX[(i,)]
        square = 1 << INDEX[(i, i)]
        need(poly_mul(t, t) == square, "polynomial square lost")
        for n, expected in enumerate((1, 1 ^ t, 1 ^ square, 1 ^ t ^ square)):
            need(frame_poly(tuple(n if j == i else 0 for j in range(DIM))) == expected, "binomial parity")
    for _ in range(128):
        a = tuple(Fraction(rng.randrange(-8, 9), rng.choice((1, 3, 5))) for _ in range(DIM))
        b = tuple(Fraction(rng.randrange(-8, 9), rng.choice((1, 3, 5))) for _ in range(DIM))
        need(frame_poly(tuple(x + y for x, y in zip(a, b))) == poly_mul(frame_poly(a), frame_poly(b)),
             "group-to-polynomial homomorphism")
    try:
        residue4(Fraction(1, 2))
    except ValueError:
        pass
    else:
        raise ValueError("even-denominator control accepted")
    for a in range(1, 1 << DIM):
        columns = [poly_mul(a << 1, 1 << INDEX[(i,)]) for i in range(DIM)]
        need(rank_binary(columns) == DIM, "multiplication by nonzero linear form not injective")
    # An exterior-algebra implementation would erase this genuine obstruction.
    t0 = 1 << INDEX[(0,)]
    square = poly_mul(t0, t0)
    square_free = sum(1 << i for i, m in enumerate(MONOMIALS) if len(set(m)) == len(m))
    need(square != 0 and square & square_free == 0, "square-deletion false-pass control")
    return {"odd_denominator_homomorphism_pairs": 128, "nonzero_linear_forms": 511}


def check_twists():
    perms = list(permutations(range(3)))
    twists = [permutation_twist(p, q) for p in perms for q in perms]
    # Include non-permutation PBQ maps; their substitutions have quadratic terms.
    left = [[1, Fraction(1, 3), 0], [0, 1, 0], [0, 0, -1]]
    right = [[1, 0, 0], [0, 1, 2], [0, 0, 1]]
    extras = [pbq_twist(left, right), pbq_twist(right, left)]
    for t in twists + extras:
        poly = polynomial_twist(t)
        inv = polynomial_twist(inverse(t))
        for i in range(SIZE):
            need(apply_linear(inv, poly[i]) == 1 << i, "twist inverse action")
        for i in range(DIM):
            for j in range(DIM):
                need(apply_linear(poly, poly_mul(1 << (i + 1), 1 << (j + 1))) ==
                     poly_mul(poly[i + 1], poly[j + 1]), "twist product action")
    return twists, extras


def check_local_pairs(twists):
    """Exhaust the reduced two-edge domain, not 36^(3*7) global assignments."""
    count = rejected = equal_maps = distinct_sources = 0
    for u in twists:
        ui = [column.index(1) for column in u]
        for v in twists:
            vi = [column.index(1) for column in v]
            for source_a in range(DIM):
                output = ui[source_a]
                source_b = vi.index(output)  # enforces the first-order cancellation
                a = 1 << INDEX[(output,)]
                defects = [poly_mul(a, (1 << INDEX[(ui[i],)]) ^ (1 << INDEX[(vi[i],)]))
                           for i in range(DIM)]
                cancels = not any(defects)
                need(cancels == (u == v), "second-order cancellation iff equal transport")
                if cancels:
                    need(source_a == source_b, "private/shared diagonal cancellation missing")
                count += 1
                rejected += not cancels
                equal_maps += cancels
                distinct_sources += source_a != source_b
                need(source_a == source_b or not cancels, "distinct source frame escaped")
    expected = (11664, 11340, 324, 10368)
    need((count, rejected, equal_maps, distinct_sources) == expected, "local pair coverage changed")
    return dict(zip(("cases", "rejected", "equal_transport_cases", "distinct_source_cases"), expected))


def check_words(extras):
    calls = witness_calls()
    ops = [compile_call(c) for c in calls]
    identity_frame = tuple(int(i in (0, 4, 8)) for i in range(DIM))
    target = target_operator(identity_frame)
    first_mask = sum((MASKS[0] | MASKS[1]) << (r * SIZE) for r in range(3))
    second_mask = sum(MASKS[2] << (r * SIZE) for r in range(3))
    # This filtration check explains all-order invariance; no 5,040-order census.
    for op in ops:
        for r in range(3):
            for i, monomial in enumerate(MONOMIALS):
                basis = 1 << (r * SIZE + i)
                increment = op[r * SIZE + i] ^ basis
                if len(monomial) == 1:
                    need(increment & ~second_mask == 0, "increment did not raise degree")
                elif len(monomial) == 2:
                    need(increment == 0, "call changed degree two modulo degree three")
    for r in range(3):
        for i in range(SIZE):
            basis = 1 << (r * SIZE + i)
            need((run_polynomial(ops, basis) ^ target[r * SIZE + i]) & first_mask == 0,
                 "predecessor first-order action no longer matches")
    dirty = 1 << INDEX[(0,)]
    residual = ((1 << INDEX[(0, 0)]) ^ (1 << INDEX[(0, 4)])) << SIZE
    expected_role1 = residual >> SIZE
    summed = dirty
    for op in ops:
        summed ^= apply_linear(op, dirty) ^ dirty
    need((summed >> SIZE) & ((1 << SIZE) - 1) == expected_role1, "all-order dirty obstruction")
    orders = [list(range(7)), list(reversed(range(7))), [1, 3, 5, 0, 2, 4, 6]]
    oracle_cases = 0
    for order in orders:
        ordered = [ops[i] for i in order]
        need(run_polynomial(ordered, dirty) == summed, "order-independent degree-one action")
        for r in range(3):
            for input_index in range(-1, DIM):
                initial = [{ZERO} if s == r else set() for s in range(3)]
                if input_index >= 0:
                    initial[r].symmetric_difference_update({unit(input_index)})
                state = initial
                for i in order:
                    state = group_call(state, calls[i])
                need(project_group(state) == run_polynomial(ordered, project_group(initial)),
                     "finite group oracle disagrees with quotient action")
                oracle_cases += 1
    direct = direct_calls()
    direct_ops = [compile_call(c) for c in direct]
    for i in range(3 * SIZE):
        need(run_polynomial(direct_ops, 1 << i) == target[i], "direct nine-call positive control")
    # Same oracle comparison on two non-permutation, odd-denominator PBQ fixtures.
    for extra in extras:
        changed = [call(ONES, (1, 0, 0), unit(4), (extra, IDENTITY, extra))]
        compiled = [compile_call(c) for c in changed]
        for i in range(-1, DIM):
            initial = [{ZERO}, set(), set()]
            if i >= 0:
                initial[0].symmetric_difference_update({unit(i)})
            need(project_group(group_call(initial, changed[0])) == run_polynomial(compiled, project_group(initial)),
                 "non-permutation twist oracle")
            oracle_cases += 1
    # Semantic mutations must fail the cheaper first-order screen already.
    mutations = [calls[:1] + calls[2:], witness_calls(IDENTITY), witness_calls(diagonal_frame=unit(4))]
    for mutated in mutations:
        compiled = [compile_call(c) for c in mutated]
        need(any((run_polynomial(compiled, 1 << (r * SIZE)) ^ target[r * SIZE]) & first_mask
                 for r in range(3)), "call/frame/twist mutation escaped")
    need(expected_role1 & (MASKS[0] | MASKS[1]) == 0 and expected_role1 != 0,
         "first-order truncation false-pass control")
    return {"finite_group_oracle_cases": oracle_cases, "representative_orders": len(orders),
            "direct_positive_basis_vectors": 3 * SIZE, "semantic_mutations_rejected": len(mutations),
            "dirty_role1_residual": ["t00^2", "t00*t11"], "all_order_justification": "filtration plus PROOF.md"}


def main():
    need(SIZE == 55, "degree-two quotient dimension")
    report = {"quotient_dimension_per_role": SIZE, "ring": check_ring()}
    twists, extras = check_twists()
    report["permutation_twists"] = len(twists)
    report["non_permutation_PBQ_fixtures"] = len(extras)
    report["local_cancellation"] = check_local_pairs(twists)
    report["word_checks"] = check_words(extras)
    report["status"] = "PASS_BIT_ADDRESS_TWIST_SECOND_ORDER"
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
