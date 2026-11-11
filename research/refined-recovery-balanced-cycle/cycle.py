"""Random-access rank-one integer frames for the balanced recovery cycle."""

import argparse
import json
from pathlib import Path

N = 112
D = 100
PERIOD = 1 << D
E = (0, 1, 2, 4)
LAMBDA = (1, 2, 4)
ROOT = Path(__file__).resolve().parents[2]


def load_basis(root=ROOT):
    """Read the predecessor's integer lifts, without executing its verifier."""
    path = root / "research/refined-recovery-longer-chains/FRAMES.json"
    spec = json.loads(path.read_text())
    blocks = spec["V_blocks"]
    if len(blocks) != 25 or any(len(block) != 4 for block in blocks):
        raise ValueError("expected 25 blocks of four integer lifts")
    basis = []
    for block in blocks:
        for sparse in block:
            if len(sparse) > N:
                raise ValueError("oversized sparse lift")
            vector = [0] * N
            seen = set()
            for index, value in sparse:
                if type(index) is not int or not 0 <= index < N or index in seen:
                    raise ValueError("invalid or repeated lift coordinate")
                if type(value) is not int or abs(value) > 100:
                    raise ValueError("invalid lift coefficient")
                seen.add(index)
                vector[index] = value
            basis.append(tuple(vector))
    return tuple(basis)


def frame_vector(index, basis):
    """Return v_a in W_a = I + v_a lambda, using reflected Gray order."""
    if type(index) is not int or not 0 <= index < PERIOD:
        raise ValueError("index must be an integer in [0, 2**100)")
    if len(basis) != D or any(len(vector) != N for vector in basis):
        raise ValueError("expected 100 integer vectors of length 112")
    gray = index ^ (index >> 1)
    return tuple(sum(basis[b][i] for b in range(D) if gray >> b & 1)
                 for i in range(N))


def apply_frame(vector, state, sign=1):
    """Apply W or its inverse; lambda has ones at owners 1, 2 and 4."""
    if len(vector) != N or len(state) != N or sign not in (-1, 1):
        raise ValueError("invalid rank-one action")
    if any(type(x) is not int or x.bit_length() > 4096 for x in vector + state):
        raise ValueError("reference actions accept integers of at most 4096 bits")
    coefficient = sign * sum(state[i] for i in LAMBDA)
    return tuple(x + coefficient * v for x, v in zip(state, vector))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=int, required=True)
    args = parser.parse_args()
    basis = load_basis()
    try:
        vector = frame_vector(args.index, basis)
        following = frame_vector((args.index + 1) % PERIOD, basis)
    except ValueError as error:
        parser.error(str(error))
    difference = tuple(x - y for x, y in zip(vector, following))
    output = {"index": args.index, "period": PERIOD,
              "meaning": "W=I+v*lambda; U_to_next=I+delta*lambda",
              "lambda": [[i, 1] for i in LAMBDA],
              "v": [[i, x] for i, x in enumerate(vector) if x],
              "delta": [[i, x] for i, x in enumerate(difference) if x]}
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
