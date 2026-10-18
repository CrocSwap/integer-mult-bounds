"""Optional witness regeneration; Sympy 1.14.0, not needed for verification."""

import argparse
import json
from pathlib import Path

import lattice


def generate():
    from sympy import Matrix
    from sympy.matrices.normalforms import hermite_normal_form

    rank = 7
    d = lattice.dimension(rank)
    current = [[int(i == j) for j in range(d)] for i in range(d)]
    entrance = [row[:] for row in current]
    for bit in range(rank):
        for a in range(d // 2):
            if (a >> bit) & 1:
                continue
            b = a ^ (1 << bit)
            for component in range(2):
                lattice.restrict(
                    current + entrance, 2 * a + component, 2 * b + component
                )
        current = lattice.stage(current, bit)
    basis = [
        [int(x) for x in row] for row in hermite_normal_form(Matrix(entrance)).tolist()
    ]
    lattice.validate_basis(basis)
    return {
        "rank": rank,
        "rows": [[[j, x] for j, x in enumerate(row) if x] for row in basis],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="new external output path; existing files are refused",
    )
    args = parser.parse_args()
    result = generate()
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(result, separators=(",", ":")) + "\n")
    print("PASS_GENERATED_COUPLED_BASIS", args.output)


if __name__ == "__main__":
    main()
