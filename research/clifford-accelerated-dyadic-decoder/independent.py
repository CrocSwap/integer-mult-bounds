"""Check the published shifts against an independently reconstructed Gram spectrum.

Uses only the PR 7747 character projection and SCHEDULE.json. apoursh with
substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from math import prod
from pathlib import Path
import json

PACKAGE = Path(__file__).resolve().parent
SCALE = 2**36


def check(predicate, error):
    if not predicate:
        raise ValueError(error)


def spectrum_numerators():
    raw = (PACKAGE / "sources/sp8-projection.json").read_bytes()
    check(sha256(raw).hexdigest() ==
          "0a36754668b66480e5f968c117a4532bc3a5eaab5c9d8448f14a5d0321c2efae",
          "Changed PR 7747 projection")
    projection = json.loads(raw)
    order = sum(projection["element_counts"])
    check(order == 47377612800 and sum(row[0]**2 for row in projection["rows"]) == order,
          "Quotient degree sum")
    numerators = set()
    for index, (degree, *inside) in enumerate(projection["rows"]):
        at_zero = (order if index == 0 else 0) - degree - sum(inside)
        character = [at_zero, *inside, degree]
        check(len(character) == 9, "Incomplete fixed-space sum")
        weighted = sum(a*(-64)**k for k, a in enumerate(character))
        multiplicity, rem = divmod(weighted, order)
        check(rem == 0 and multiplicity > 0, "Invalid width-13 multiplicity")
        node, rem = divmod(SCALE * order * multiplicity, degree * 2**48)
        check(rem == 0, "Chosen fixed-point denominator is insufficient")
        numerators.add(node)
    check(len(projection["rows"]) == 81 and len(numerators) == 52,
          "Missing spectral blocks or levels")
    return sorted(numerators)


def prefix_products(steps, nodes):
    values = [1] * len(nodes)
    denominator = 1
    maximum = Fraction(1)
    peak_step = 0
    for j, (u, v) in enumerate(steps, 1):
        divisor = SCALE * v
        denominator *= divisor
        values = [a*(divisor-u*x) for a, x in zip(values, nodes)]
        stage_max = Fraction(max(map(abs, values)), denominator)
        if stage_max > maximum:
            maximum, peak_step = stage_max, j
    return values, denominator, maximum, peak_step


def extrapolate_alternating(nodes):
    # This checks the sign-alternating interpolant at zero via Newton's
    # divided differences, independently of the builder's Lagrange weights.
    column = [Fraction((-1)**j) for j in range(len(nodes))]
    answer = column[0]
    product = 1
    for j in range(1, len(nodes)):
        column = [(b-a)/(y-x)
                  for a, b, x, y in zip(column, column[1:], nodes, nodes[j:])]
        product *= -nodes[j-1]
        answer += product * column[0]
    return answer


def hadamard(vector):
    return [sum((-1)**((i & j).bit_count() % 2)*x for j, x in enumerate(vector))/2
            for i in range(4)]


def gram_action(vector, levels):
    return hadamard([x*y for x, y in zip(levels, hadamard(vector))])


def data_application(steps, nodes):
    # A rectangular dyadic test with four *actual* levels and a nondiagonal
    # Gram matrix. Disjoint four-square expansions followed by Walsh mixing.
    nodes = [nodes[j] for j in (0, 14, 31, 51)]
    levels = [Fraction(w, SCALE) for w in nodes]
    blocks = []
    for node in nodes:
        weights = []
        j = 0
        while node:
            node, digit = divmod(node, 4)
            weights.extend([Fraction(2**j, 2**18)]*digit)
            j += 1
        blocks.append(weights)
    check([sum(t*t for t in block) for block in blocks] == levels, "Test factorization")
    signal = list(map(Fraction, [1, 2, -3, 5]))
    for noisy in (False, True):
        observations = [[t*z + int(noisy)*(2*i+j+1) for j, t in enumerate(block)]
                        for i, (z, block) in enumerate(zip(hadamard(signal), blocks))]
        adjoint = hadamard([sum(t*z for t, z in zip(block, vector))
                            for block, vector in zip(blocks, observations)])
        decoded = hadamard([row[0]/block[0] for row, block in zip(observations, blocks)])
        canonical = hadamard([s/x for s, x in zip(hadamard(adjoint), levels)])
        initial = hadamard([a-b for a, b in zip(decoded, canonical)])
        for n, d in steps:
            step = Fraction(n, d)
            gram = gram_action(decoded, levels)
            decoded = [a + step*(b-c) for a, b, c in zip(decoded, adjoint, gram)]
            if not noisy:
                check(decoded == signal, "Lost exact recovery on mixed test data")
        residual = hadamard([a-b for a, b in zip(decoded, canonical)])
        expected = [a*prod(1-x*Fraction(n, d) for n, d in steps)
                    for a, x in zip(initial, levels)]
        check(residual == expected, "Rectangular update disagrees with predicted error")
        if noisy:
            check(all(initial), "Test did not excite every selected level")


def main():
    nodes = spectrum_numerators()
    saved = json.loads((PACKAGE / "SCHEDULE.json").read_text())
    dyadic = [(u, 2**b) for u, b in saved["dyadic_steps_numerator_and_fraction_bits"]]
    optimal = [(u, 2**saved["norm_optimal_dyadic_fraction_bits"])
               for u in saved["norm_optimal_dyadic_numerators"]]
    optimal.append(tuple(saved["norm_optimal_final_reciprocal"]))
    a, d, peak, _ = prefix_products(dyadic, nodes)
    check(max(map(abs, a)) << 129 < d and peak == 1 and all(a), "Dyadic contraction")
    b, d, peak, _ = prefix_products(optimal, nodes)
    check(max(map(abs, b)) << 58 < d and b[0] == 0 and all(b[1:]) and peak == 1,
          "Norm-optimal contraction")
    _, _, reverse_peak, at = prefix_products(reversed(dyadic), nodes)
    check(2**138 < reverse_peak < 2**139 and at == 48,
          "Reversed-order intermediate growth control")
    check(2**60 < extrapolate_alternating(nodes) < 2**61, "Full-node degree witness")
    check(2**52 < extrapolate_alternating(nodes[:21] + nodes[22:]) < 2**53,
          "Reduced-node degree witness")
    data_application(dyadic, nodes)
    data_application(optimal, nodes)
    print("PASS_INDEPENDENT_DECODERS levels_reconstructed=52 prefix_bound=1 "
          "reverse_peak>2^138 reverse_peak_step=48 "
          "mixed_rectangular_feasibility_and_noise=passed")


if __name__ == "__main__":
    main()
