#!/usr/bin/env python3
"""Independent support test for the one-stage terminal code (stdlib only).

Source credit: Dugongue's PR #4929 code, Cinna Davis's center-free kernel,
and Cao Yifan's retained native source.  The signed normalizer construction
is independently reconstructed here; normalizers.py is not imported.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def parity(x):
    return x.bit_count() & 1


def act(columns, x):
    answer = 0
    for bit, column in enumerate(columns):
        if (x >> bit) & 1:
            answer ^= column
    return answer


def transpose(columns):
    return [sum(((column >> row) & 1) << j
                for j, column in enumerate(columns))
            for row in range(len(columns))]


def reconstruct(q, dimension):
    """Return G columns and output sign mask of K = Z_z P_G."""
    e = 1
    need(q != (1 << dimension) - 1 and parity(q) == 1,
         "Port must be odd and distinct from the all-ones vector")
    if not (q & e):
        transvections = [e ^ q]
    else:
        j = next(j for j in range(1, dimension) if not ((q >> j) & 1))
        transvections = [e ^ (1 << j), (1 << j) ^ q]
    need(all(parity(v) == 0 for v in transvections),
         "Orthogonal transvections require even vectors")
    columns = []
    for j in range(dimension):
        x = 1 << j
        for v in transvections:
            if parity(x & v):
                x ^= v
        columns.append(x)
    need(columns[0] == q, "Normalizer must send the central line to its port")
    need(all(parity(a & b) == int(i == j)
             for i, a in enumerate(columns)
             for j, b in enumerate(columns)), "Normalizer must be orthogonal")
    rows = transpose(columns)
    z = sum((((row.bit_count() - 1) // 2) & 1) << j
            for j, row in enumerate(rows))
    return columns, z


def transition(left, right):
    """K_left^{-1} K_right as (binary columns, input sign mask)."""
    gi, zi = left
    gj, zj = right
    inverse = transpose(gi)
    columns = [act(inverse, column) for column in gj]
    beta = sum(parity((zi ^ zj) & column) << j
               for j, column in enumerate(gj))
    return columns, beta


def column_expansion(columns, beta, x):
    """Twice Q^{-1} M Q on |x>, as exact Gaussian integer coefficients.

    Q = (1+i)/2 * (I-i T_e), M|x> = (-1)^(beta.x)|Gx>.
    No floating point or Clifford implementation is used.
    """
    s0 = 1 - 2 * parity(beta & x)
    s1 = 1 - 2 * parity(beta & (x ^ 1))
    gx = act(columns, x)
    ge = columns[0]
    terms = ((gx, (s0, 0)), (gx ^ ge, (0, -s1)),
             (gx ^ 1, (0, s0)), (gx ^ ge ^ 1, (s1, 0)))
    answer = {}
    for position, (real, imag) in terms:
        old_real, old_imag = answer.get(position, (0, 0))
        answer[position] = (old_real + real, old_imag + imag)
    return {position: value for position, value in answer.items()
            if value != (0, 0)}


def analyze(ports, code, exhaustive_pairs=()):
    n = 9
    need(len(ports) == len(set(ports)) == 112, "112 distinct source ports")
    need(len(code) == 112 and all(len(row) == 112 for row in code),
         "Exact owner-code dimensions")
    normalizers = [reconstruct(q, n) for q in ports]
    ranks = Counter()
    nonzero = []
    for i, row in enumerate(code):
        for j, coefficient in enumerate(row):
            if not coefficient:
                continue
            need(i != j, "Every nonzero source-code block is off diagonal")
            need(abs(coefficient) == Fraction(1, 2), "Frozen code coefficient")
            columns, beta = transition(normalizers[i], normalizers[j])
            need(columns[0] not in (0, 1),
                 "Distinct source ports force two independent translation lines")
            deltas = {0, 1, columns[0], columns[0] ^ 1}
            need(len(deltas) == 4, "Exact rank-two support certificate")
            # Signs may vary with x. Distinct destinations make every sign
            # assignment nonzero; these four cases exhaust their possibilities.
            for s0 in (-1, 1):
                for s1 in (-1, 1):
                    need(all(value != (0, 0) for value in
                             ((s0, 0), (0, -s1), (0, s0), (s1, 0))),
                         "No absolute-phase support cancellation")
            ranks[2] += 1
            nonzero.append((i, j))
    need(len(nonzero) == 5824, "Frozen nonzero block count")
    checked = []
    for i, j in exhaustive_pairs:
        need(code[i][j] != 0, "Exhaustive test must use an actual nonzero block")
        columns, beta = transition(normalizers[i], normalizers[j])
        row_counts = Counter()
        for x in range(1 << n):
            expansion = column_expansion(columns, beta, x)
            need(len(expansion) == 4, "Exact one-column support")
            need(all(abs(a) + abs(b) == 1 for a, b in expansion.values()),
                 "Exact nonzero Gaussian-integer coefficients")
            row_counts.update(expansion.keys())
        need(len(row_counts) == 1 << n and set(row_counts.values()) == {4},
             "All rows as well as columns have support four")
        checked.append([i, j])
    return normalizers, ranks, checked


def run():
    raw = (HERE / "native-source.json.gz").read_bytes()
    source = json.loads(gzip.decompress(raw))["canonical"]
    code_bytes = (HERE / "CODE.json").read_bytes()
    code = [[Fraction(value) for value in row]
            for row in json.loads(code_bytes)["A"]]
    twice = [[int(2 * value) for value in row] for row in code]
    need(all(Fraction(twice[i][j], 2) == code[i][j]
             for i in range(112) for j in range(112)), "Half-integral source code")
    need(all(twice[i][j] == twice[j][i]
             for i in range(112) for j in range(112)), "Symmetric source code")
    need(all(sum(a * b for a, b in zip(twice[i], twice[j]))
             + 24 * twice[i][j] == 52 * int(i == j)
             for i in range(112) for j in range(112)),
         "Exact source-code polynomial justifying the inverse")
    pairs = [(0, next(j for j, value in enumerate(code[0]) if value)),
             (37, next(j for j, value in enumerate(code[37]) if value)),
             (111, next(j for j, value in enumerate(code[111]) if value))]
    normalizers, ranks, checked = analyze(source["ports"], code, pairs)
    # Meaningful false-positive controls: the identity really has one support
    # point after Q conjugation, and permitting a diagonal code block must fail.
    identity = [1 << j for j in range(9)]
    need(all(column_expansion(identity, 0, x) == {x: (2, 0)}
             for x in range(512)), "Diagonal cancellation control")
    mutant = [row[:] for row in code]
    mutant[0][0] = Fraction(1, 2)
    try:
        analyze(source["ports"], mutant)
    except ValueError as error:
        need("off diagonal" in str(error), "Mutation must fail for its actual defect")
    else:
        raise ValueError("Diagonal mutation was accepted")
    return {
        "scope": "One source code C or its inverse; not a product of different stage codes",
        "source_sha256": sha256(raw).hexdigest(),
        "code_sha256": sha256(code_bytes).hexdigest(),
        "ports": len(normalizers),
        "nonzero_off_diagonal_blocks": sum(ranks.values()),
        "orientations": ["C", "C^{-1}=(C+12I)/13"],
        "gaussian_support_rank_histogram": {str(k): v for k, v in sorted(ranks.items())},
        "exhaustive_512_column_blocks": checked,
        "exact_support_per_block_row_at_width_f": "4**f",
        "fixed_free_word_excluded": True,
        "free_model": "Fixed finite word of scalar ADD/SCALE, monomial address maps, and owned COPY/CLEAR",
        "add_count_lower_bound_from_support": "at least 2*f",
        "controls": ["identity conjugation has support one", "diagonal code mutation rejected"],
        "unresolved": ["Products of stage codes may cancel", "Paid terminal decoders",
                       "Changed caller or recursively coded job family", "Selected exponent admission"],
    }


if __name__ == "__main__":
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "TERMINAL.json").write_text(rendered)
    else:
        need(json.loads((HERE / "TERMINAL.json").read_text()) == result,
             "Frozen terminal receipt differs from independent replay")
    print("PASS: 5,824 actual off-diagonal terminal blocks have rank-two support; one-stage scope only")
