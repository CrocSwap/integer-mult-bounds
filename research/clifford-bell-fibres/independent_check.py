"""Check the degree-13 Bell measurement on literal four-qubit matrices.

Matrices are sparse computational-basis columns of Gaussian integers with a
common positive denominator kept outside each frame. No primary checker or
predecessor code is imported. apoursh with substantial OpenAI Codex
assistance. Apache-2.0.
"""

from functools import reduce
from operator import xor

ZERO = (0, 0)
ONE = (1, 0)
ROOTS = (ONE, (0, 1), (-1, 0), (0, -1))
TUPLE = (0, 16, 32, 64, 128, 8)  # zero, Z1..Z4, X4 (bit 0 is qubit 1)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mul(z, w):
    return z[0] * w[0] - z[1] * w[1], z[1] * w[0] + z[0] * w[1]


def conj(z):
    return z[0], -z[1]


def scale(z, n):
    return z[0] * n, z[1] * n


def add_entry(result, index, z):
    a, b = result.get(index, ZERO)
    updated = (a + z[0], b + z[1])
    if updated == ZERO:
        result.pop(index, None)
    else:
        result[index] = updated


def sign(z, j):
    return (-1) ** ((z & j).bit_count() % 2)


def weyl(label):
    x, z = label % 16, label // 16
    return [{j ^ x: (sign(z, j), 0)} for j in range(16)]


def multiply(left, right):
    columns = []
    for col in right:
        result = {}
        for middle, a in col.items():
            for row, b in left[middle].items():
                add_entry(result, row, mul(b, a))
        columns.append(result)
    return columns


def adjoint(u):
    output = [{} for _ in range(16)]
    for j, col in enumerate(u):
        for i, value in col.items():
            output[i][j] = conj(value)
    return output


def rotate(u, exponent):
    return [{r: mul(z, ROOTS[exponent % 4]) for r, z in col.items()} for col in u]


def diagonal_cube(mask):
    # The independent diagonal phases are CZ12, CZ13, CZ23.
    pairs = ((1, 2), (1, 4), (2, 4))
    gate = []
    for j in range(16):
        exponent = sum(1 for k, (a, b) in enumerate(pairs)
                       if mask & (1 << k) and j & a and j & b)
        gate.append({j: ((-1) ** exponent, 0)})
    return gate


def hadamard(bit):
    # The numerator of (1+i) [[1,1],[1,-1]] / 2 at one chosen bit.
    return [{j & ~bit: (1, 1), j | bit: ((-1, -1) if j & bit else (1, 1))}
            for j in range(16)]


def literal_action(u, denominator, label, *, bell):
    """Expand U W_t U^T (Bell pair) or U W_t U^* (singleton correction)."""
    x, z = label % 16, label // 16
    entries = {}
    for j, col in enumerate(u):
        for right, b in col.items():
            factor = scale(b if bell else conj(b), sign(z, j))
            for left, a in u[j ^ x].items():
                add_entry(entries, (left, right), mul(a, factor))
    require(len(entries) == 16, "image is not a signed Weyl matrix")
    x_next, = [r for r, c in entries if c == 0]
    scalar = entries[x_next, 0]
    require(scalar in [scale(root, denominator ** 2) for root in ROOTS],
            "incorrect scaled Bell amplitude")
    phase = ROOTS.index((scalar[0] // denominator ** 2, scalar[1] // denominator ** 2))
    z_next = sum(1 << bit for bit in range(4)
                 if entries[x_next ^ (1 << bit), 1 << bit] != scalar)
    require(all(entries.get((x_next ^ j, j)) == scale(scalar, sign(z_next, j))
                for j in range(16)), "wrong displacement or Walsh sign")
    return x_next | (z_next << 4), phase


def add_scaled_matrix(output, u, alpha):
    for j, col in enumerate(u):
        for i, value in col.items():
            add_entry(output, (i, j), mul(alpha, value))


def sandwich(entries, left, right):
    """Multiply by W_left on the left and W_right^{-1} on the right."""
    return {(i ^ (left % 16), j ^ (right % 16)):
            scale(z, sign(left // 16, i) * sign(right // 16, j))
            for (i, j), z in entries.items()}


def gauge(p, c):
    return (p.bit_count() + c % 3) % 4


def shifted(u, p, c):
    return rotate(multiply(weyl(p), u), gauge(p, c))


def frobenius(u, entries):
    total = [0, 0]
    for j, col in enumerate(u):
        for i, z in col.items():
            term = mul(conj(z), entries.get((i, j), ZERO))
            total[0] += term[0]
            total[1] += term[1]
    return tuple(total)


def calibration(in_gate, d_in, out_gate, d_out):
    t = [literal_action(in_gate, d_in, a, bell=True)[0] for a in TUPLE]
    m = [literal_action(out_gate, d_out, a, bell=True)[0] for a in TUPLE]
    w, w_next = reduce(xor, t), reduce(xor, m)
    denominator = d_in * d_out
    s1 = [{j: ROOTS[j & 1]} for j in range(16)]
    # S1 fixes X4 Z1 Z2 Z3 Z4 as a label, but moves the Bell tuple.
    shapes = [diagonal_cube(c) for c in range(8)] + [s1]
    selected_p = (0, 1, 2, 4, 8, 17, 35, 81, 128, 194, 255)
    detected = {}
    coset_sum = {}
    rho_values = set()
    beta_phases = set()
    gamma_phases = set()
    invisible = wrong_single_weight = isolated_checks = 0
    for c, shape in enumerate(shapes):
        u0 = multiply(out_gate, multiply(shape, adjoint(in_gate)))
        individual = {}
        weights = {}
        for j, p in enumerate(selected_p):
            u = shifted(u0, p, c)
            # Include genuinely complex and nonuniform coefficients, and zero
            # coefficients on the remaining 245 Paulis in each fibre.
            alpha = (1 + (j + c) % 5, (2 * j + c) % 7 - 3)
            weights[p] = alpha
            add_scaled_matrix(individual, u, alpha)
            images = [literal_action(u, denominator, a, bell=True) for a in t]
            sw, gamma = literal_action(u, denominator, w, bell=False)
            matches = [a for a, _ in images] == m
            require(matches == (c < 8), "six pairs selected the wrong symplectic fibres")
            if not matches:
                invisible += 1
                wrong_single_weight += sw == w_next
                continue
            require(sw == w_next, "tuple sum and singleton weight disagree")
            beta = sum(b for _, b in images) % 4
            rho_values.add((beta - gamma) % 4)
            beta_phases.add(beta)
            gamma_phases.add(gamma)
            # Measured singleton numerator after the known 4^13 normalization
            # is removed from the input tensor coordinates.
            add_scaled_matrix(detected, u, mul(ROOTS[beta], alpha))
            add_scaled_matrix(coset_sum, u, alpha)
        if c < 8:
            # On a supplied individual X_R, extraction checks every coefficient,
            # including the 245 making zero contributions to this mixture.
            for p in range(256):
                trace = frobenius(shifted(u0, p, c), individual)
                require(trace == scale(weights.get(p, ZERO), 16 * denominator ** 2),
                        "incorrect Fourier extraction or representative phase")
                isolated_checks += 1
    require(len(rho_values) == 1, "transport phase depends on a Pauli or cube lift")
    rho, = rho_values
    answer = {k: mul(z, ROOTS[rho]) for k, z in coset_sum.items()}
    require(sandwich(detected, w_next, w) == answer and answer,
            "literal singleton correction lost the unweighted coset sum")
    require(invisible == len(selected_p) and wrong_single_weight == invisible,
            "off-coset fixture did not exercise full-tuple filtering")
    return (len(beta_phases), len(gamma_phases), rho, isolated_checks,
            detected != answer, imaginary_phase(beta_phases | gamma_phases))


def decode_cz_mixture():
    # H on the first three qubits turns the Z-shear stabilizer into X
    # shears. Its intersection with the eight allowed CZ shapes is trivial.
    frame = multiply(hadamard(1), multiply(hadamard(2), hadamard(4)))
    t = [literal_action(frame, 8, a, bell=True)[0] for a in TUPLE]
    w = reduce(xor, t)
    buckets = {}
    decoder = {}
    weights = {}
    for c in range(8):
        gate = diagonal_cube(c)
        seed = [literal_action(gate, 1, a, bell=True) for a in t]
        target = tuple(a for a, _ in seed)
        sw, gamma = literal_action(gate, 1, w, bell=False)
        require(target not in decoder and sw == reduce(xor, target),
                "two CZ fibres collide in the transverse frame")
        decoder[target] = (c, sw, (sum(b for _, b in seed) - gamma) % 4)
        for p in (0, 16, 1, 17, 33, 49, 2, 18, 34, 50):
            # The first two terms give (I-Z1) CZ in each corrected fibre.
            # Their diagonal contributions at basis zero cancel exactly.
            if p in (0, 16):
                alpha = scale(ROOTS[-gauge(p, c) % 4], 1 if p == 0 else -1)
            else:
                alpha = (1 + (p+c) % 5, (p+2*c) % 7 - 3)
            weights[c, p] = alpha
            u = shifted(gate, p, c)
            images = [literal_action(u, 1, a, bell=True) for a in t]
            observed_target = tuple(a for a, _ in images)
            beta = sum(b for _, b in images) % 4
            add_scaled_matrix(buckets.setdefault(observed_target, {}),
                              u, mul(alpha, ROOTS[beta]))
    require(len(buckets) == 8, "transverse frame failed to separate all fibres")
    recovered = 0
    for observed_target, observation in buckets.items():
        c, sw, rho = decoder[observed_target]
        corrected = sandwich(observation, sw, w)
        matrix = {k: mul(z, ROOTS[-rho % 4]) for k, z in corrected.items()}
        require((0, 0) not in matrix and (1, 1) in matrix,
                "deliberate observable cancellation was lost")
        for p in range(256):
            result = frobenius(shifted(diagonal_cube(c), p, c), matrix)
            require(result == scale(weights.get((c, p), ZERO), 16),
                    "failed to decode the complete mixed sparse alphabet")
            recovered += 1
    return recovered


def imaginary_phase(phases):
    return bool(phases & {1, 3})


def main():
    identity = weyl(0)
    s1 = [{j: ROOTS[j & 1]} for j in range(16)]
    cnot = [{j ^ (2 if j & 8 else 0): ONE} for j in range(16)]
    # Choose a dense output basis and a non-real input/output basis. The
    # latter exercises the distinction between transpose and adjoint.
    frames = [(identity, 1, identity, 1),
              (identity, 1, multiply(s1, hadamard(8)), 2),
              (multiply(s1, hadamard(1)), 2, multiply(hadamard(2), cnot), 2)]
    results = [calibration(*frame) for frame in frames]
    require(any(row[-2] for row in results), "omitting singleton correction escaped")
    require(any(row[-1] for row in results), "no nonreal phase tested")
    bell_s = literal_action(s1, 1, 0, bell=True)
    adj_s = literal_action(s1, 1, 0, bell=False)
    require(bell_s != adj_s, "using conjugate instead of transpose escaped")
    complete = decode_cz_mixture()
    print("PASS_LITERAL_SIX_BELL_SINGLETON", f"frames={len(frames)}",
          f"input_operators={9 * 11 * len(frames)}",
          f"weyl_extractions={sum(r[3] for r in results)}",
          f"off_coset_same_weight={11 * len(frames)}",
          f"mixture_coefficients={complete} active_mixture_coefficients=80",
          f"transport_units={','.join(str(r[2]) for r in results)}")


if __name__ == "__main__":
    main()
