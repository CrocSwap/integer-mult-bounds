#!/usr/bin/env python3
"""Exact finite audit of the endpoint-gauge quadratic Gauss normal form.

Copyright 2026 yssite. Apache-2.0.
Prepared with substantial OpenAI Codex assistance. No supplier code is imported.
"""
import argparse
from collections import Counter
from hashlib import sha256, shake_256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "2921874911956718fcaaaf9396fe8267b3cfa9f0"
SEED = "d207afb6a1a4565a4812f3e58a38ad45"
SOURCE_PATHS = (
    "notes/endpoint-gauge-complex.tex",
    "tests/test_endpoint_gauge.py",
)
UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


class VerificationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def rotate(value, exponent):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def vectors(n):
    return tuple(product((0, 1), repeat=n))


def index(vector):
    value = 0
    for bit in vector:
        value = 2 * value + bit
    return value


def symmetric_matrices(n):
    positions = [(i, j) for i in range(n) for j in range(i, n)]
    for bits in product((0, 1), repeat=len(positions)):
        matrix = [[0] * n for _ in range(n)]
        for (i, j), bit in zip(positions, bits):
            matrix[i][j] = matrix[j][i] = bit
        yield tuple(map(tuple, matrix))


def quadratic_table(matrix, lift):
    """All refinements of B: diagonal B_ii+2*l_i, cross terms 2*B_ij."""
    n = len(matrix)
    require(len(lift) == n and all(type(x) is int and x in (0, 1) for x in lift),
            "invalid diagonal lift")
    require(all(len(row) == n for row in matrix), "invalid matrix shape")
    require(all(type(matrix[i][j]) is int and matrix[i][j] in (0, 1)
                and matrix[i][j] == matrix[j][i]
                for i in range(n) for j in range(n)), "nonbinary or nonsymmetric matrix")
    return tuple((sum((matrix[i][i] + 2 * lift[i]) * v[i] for i in range(n))
                  + 2 * sum(matrix[i][j] * v[i] * v[j]
                            for i in range(n) for j in range(i + 1, n))) % 4
                 for v in vectors(n))


def linear_images(matrix):
    return tuple(index(tuple(sum(a * b for a, b in zip(row, v)) % 2 for row in matrix))
                 for v in vectors(len(matrix)))


def walsh(table):
    """Unnormalized Fourier transform, using Gaussian-integer butterflies."""
    values = [UNITS[q] for q in table]
    width = 1
    while width < len(values):
        for start in range(0, len(values), 2 * width):
            for j in range(start, start + width):
                a, b = values[j], values[j + width]
                values[j] = (a[0] + b[0], a[1] + b[1])
                values[j + width] = (a[0] - b[0], a[1] - b[1])
        width *= 2
    return tuple(values)


def direct_walsh(table):
    """Separate oracle: count the four phases in each character sum."""
    answer = []
    for s in range(len(table)):
        counts = [0, 0, 0, 0]
        for z, q in enumerate(table):
            counts[(q + 2 * ((s & z).bit_count() % 2)) % 4] += 1
        answer.append((counts[0] - counts[2], counts[1] - counts[3]))
    return tuple(answer)


def check_polarization(table, images):
    require(table[0] == 0, "quadratic refinement must vanish at zero")
    for x in range(len(table)):
        for y in range(len(table)):
            require((table[x ^ y] - table[x] - table[y]) % 4
                    == 2 * ((x & images[y]).bit_count() % 2), "polarization mismatch")


def normal_form(table, inverse, gauss, x, y):
    # B is the polarization matrix, so the G in the source statement is B^-1.
    phase = (-table[inverse[x]] - table[inverse[y]]
             + 2 * ((x & inverse[y]).bit_count() % 2))
    return rotate(gauss, phase)


def root_phase(gauss, n):
    # Check S_q * (1-i)^n / 2^n in {1,i,-1,-i}, without division.
    a, b = gauss
    for _ in range(n):
        a, b = a + b, b - a
    choices = tuple((x * (1 << n), y * (1 << n)) for x, y in UNITS)
    require((a, b) in choices, "fourth-root normalization failed")
    return choices.index((a, b))


def check_case(matrix, lift, *, transform=walsh, formula=normal_form):
    n = len(matrix)
    table = quadratic_table(matrix, lift)
    images = linear_images(matrix)
    check_polarization(table, images)
    spectrum = transform(table)
    require(spectrum == direct_walsh(table), "Walsh/direct mismatch")
    radical = tuple(x for x, image in enumerate(images) if image == 0)
    rank = len(set(images)).bit_length() - 1
    require(len(set(images)) == 1 << rank, "nonlinear image cardinality")
    alternating = all(matrix[i][i] == 0 for i in range(n))
    if rank == n:
        inverse = [0] * len(images)
        for x, image in enumerate(images):
            inverse[image] = x
        phase = root_phase(spectrum[0], n)
        for x in range(len(table)):
            for y in range(len(table)):
                require(spectrum[x ^ y] == formula(table, inverse, spectrum[0], x, y),
                        "normal-form kernel mismatch")
        return dict(rank=rank, alternating=alternating, phase=phase,
                    kernel_entries=len(table)**2)

    # Boundary audit: support is an affine annihilator of the radical,
    # and nonzero squared magnitudes are 2^n * |radical|, not 2^n.
    support = 0
    for s, (a, b) in enumerate(spectrum):
        expected = all(table[u] == 2 * ((s & u).bit_count() % 2) for u in radical)
        require(a*a + b*b == (len(table) * len(radical) if expected else 0),
                "singular support/magnitude mismatch")
        support += bool(a or b)
    require(support == 1 << rank and support < len(table), "singular flatness boundary failed")
    return dict(rank=rank, alternating=alternating, phase=None, kernel_entries=0)


def reject(action, expected):
    try:
        action()
    except VerificationError as error:
        require(expected in str(error), "control rejected for the wrong reason: " + str(error))
    else:
        raise VerificationError("negative control was accepted: " + expected)


def negative_controls():
    odd = ((1,),)
    hyperbolic = ((0, 1), (1, 0))
    noninvolutory = ((1, 1), (1, 0))
    controls = []

    def control(name, action, message):
        reject(action, message)
        controls.append(name)

    control("omit_global_gauss", lambda: check_case(hyperbolic, (0, 0),
            formula=lambda q, inv, s, x, y: normal_form(q, inv, (1, 0), x, y)), "kernel mismatch")
    control("rotate_global_phase", lambda: check_case(odd, (0,),
            formula=lambda q, inv, s, x, y: rotate(normal_form(q, inv, s, x, y), 1)), "kernel mismatch")
    control("use_B_instead_of_inverse", lambda: check_case(noninvolutory, (0, 0),
            formula=lambda q, inv, s, x, y: normal_form(q, linear_images(noninvolutory), s, x, y)),
            "kernel mismatch")
    control("conjugate_endpoint_phases", lambda: check_case(odd, (0,),
            formula=lambda q, inv, s, x, y: rotate(s, q[inv[x]] + q[inv[y]]
                                                + 2*((x & inv[y]).bit_count() % 2))), "kernel mismatch")
    control("omit_bilinear_phase", lambda: check_case(hyperbolic, (0, 0),
            formula=lambda q, inv, s, x, y: rotate(s, -q[inv[x]] - q[inv[y]])), "kernel mismatch")
    control("discard_signed_refinement", lambda: check_case(odd, (1,),
            formula=lambda q, inv, s, x, y: normal_form((0, 1), inv, s, x, y)), "kernel mismatch")
    control("omit_Walsh_stages", lambda: check_case(odd, (0,),
            transform=lambda q: tuple(UNITS[v] for v in q)), "Walsh/direct mismatch")
    control("singular_as_full_rank", lambda: root_phase((4, 0), 2), "fourth-root")
    control("nonzero_constant", lambda: check_polarization((1, 2), (0, 1)), "vanish at zero")
    control("wrong_polarization", lambda: check_polarization((0, 1, 1, 0), (0, 1, 2, 3)),
            "polarization mismatch")
    control("nonsymmetric_B", lambda: quadratic_table(((1, 1), (0, 1)), (0, 0)), "nonsymmetric")
    return controls


def seeded_cases():
    # A fixed-cost extension, not an exhaustive claim at these dimensions.
    for n in (5, 6, 9):
        for case in range(8):
            raw = shake_256(bytes.fromhex(SEED) + bytes((n, case))).digest(n*n + n)
            bits = iter(byte % 2 for byte in raw)
            matrix = [[0]*n for _ in range(n)]
            for i in range(n):
                for j in range(i, n):
                    matrix[i][j] = matrix[j][i] = next(bits)
            yield tuple(map(tuple, matrix)), tuple(next(bits) for _ in range(n))


def census():
    rows = []
    for n in range(5):
        counts = Counter()
        ranks, phases = Counter(), Counter()
        for matrix in symmetric_matrices(n):
            counts["symmetric_matrices"] += 1
            for lift in product((0, 1), repeat=n):
                result = check_case(matrix, lift)
                counts["refinements"] += 1
                counts["direct_sum_terms"] += 1 << (2*n)
                counts["polarization_pairs"] += 1 << (2*n)
                ranks[str(result["rank"])] += 1
                if result["phase"] is not None:
                    counts["nonsingular_refinements"] += 1
                    counts["alternating_nonsingular" if result["alternating"]
                           else "nonalternating_nonsingular"] += 1
                    counts["kernel_entries"] += result["kernel_entries"]
                    phases[str(result["phase"])] += 1
                else:
                    counts["singular_refinements"] += 1
        require(counts["refinements"] == 1 << (n*(n+3)//2), "incomplete coefficient census")
        fields = ("symmetric_matrices", "refinements", "nonsingular_refinements",
                  "singular_refinements", "alternating_nonsingular", "nonalternating_nonsingular",
                  "kernel_entries", "direct_sum_terms", "polarization_pairs")
        rows.append(dict(dimension=n, **{k: counts[k] for k in fields},
                         rank_counts=dict(sorted(ranks.items())), phase_counts=dict(sorted(phases.items()))))
    sampled = []
    for matrix, lift in seeded_cases():
        encoded = canonical(dict(matrix=matrix, lift=lift)).encode("ascii")
        sampled.append(dict(dimension=len(matrix), input_sha256=sha256(encoded).hexdigest(),
                            **check_case(matrix, lift)))
    return dict(schema="signed-gauss-census-v1", base_sha=BASE, seed_hex=SEED,
                exhaustive=rows, sampled=sampled, negative_controls=negative_controls(),
                scope="Finite identity and singular-boundary verification; no new kappa or supplier admission.")


def source_bindings(root):
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    require(manifest["base_sha"] == BASE and set(manifest["files"]) == set(SOURCE_PATHS),
            "source inventory mismatch")
    for path, record in manifest["files"].items():
        require(sha256((root / path).read_bytes()).hexdigest() == record["sha256"],
                "source digest mismatch: " + path)
    return len(SOURCE_PATHS)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=HERE.parents[1])
    parser.add_argument("--output", type=Path, help="Write the checked receipt to a new file")
    args = parser.parse_args()
    pinned = source_bindings(args.source_root)
    result = census()
    expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
    require(canonical(result) == canonical(expected), "census receipt mismatch")
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    totals = {k: sum(row[k] for row in result["exhaustive"])
              for k in ("refinements", "nonsingular_refinements", "singular_refinements", "kernel_entries")}
    print("PASS_SIGNED_GAUSS_CENSUS", " ".join(f"{k}={v}" for k, v in totals.items()),
          f"sampled={len(result['sampled'])} controls={len(result['negative_controls'])} pins={pinned}")


if __name__ == "__main__":
    main()
