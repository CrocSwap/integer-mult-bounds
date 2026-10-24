"""Check the concrete witness by full literal replay, without the producer.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from literal import degree_bound, replay
from syntax import fingerprint, validate


def check(program, witness):
    if validate(program).characteristic:
        raise ValueError("the SPD construction requires Q")
    keys = {"schema", "program_sha256", "word", "dimension", "input", "output",
            "epsilon", "epsilon_cap", "numerator_degree_bound", "grid_size",
            "grid_index", "endpoint_difference"}
    if not isinstance(witness, dict) or set(witness) != keys:
        raise ValueError("invalid witness fields")
    if witness["schema"] != "spd-inverse-witness/v1":
        raise ValueError("invalid witness schema")
    if witness["program_sha256"] != fingerprint(program):
        raise ValueError("program binding mismatch")
    word = witness["word"]
    if not isinstance(word, list) or any(type(a) is not str or a not in program["operators"] for a in word):
        raise ValueError("invalid path word")
    n = len(word) + 1
    q = sum(ins["op"] != "linear" for side in ("left", "right") for ins in program[side])
    for key in ("dimension", "input", "output", "numerator_degree_bound", "grid_size", "grid_index"):
        if type(witness[key]) is not int:
            raise ValueError("integer witness field required")
    if witness["dimension"] != n or n > len(program["roles"]) + q:
        raise ValueError("dimension bound mismatch")
    if not 0 <= witness["input"] < len(program["roles"]) or not 0 <= witness["output"] < len(program["roles"]):
        raise ValueError("invalid role index")
    degree = degree_bound(program, n)
    if witness["numerator_degree_bound"] != degree or witness["grid_size"] != degree + 1:
        raise ValueError("grid bound mismatch")
    cap, epsilon = Fraction(witness["epsilon_cap"]), Fraction(witness["epsilon"])
    index = witness["grid_index"]
    if not 0 < cap <= Fraction(1, 4) or not 1 <= index <= degree + 1:
        raise ValueError("invalid grid range")
    if epsilon != cap * (degree + 2 - index) / (degree + 1):
        raise ValueError("invalid grid point")
    difference = replay(program, word, epsilon, witness["input"])
    if witness["endpoint_difference"] != [[str(x) for x in row] for row in difference]:
        raise ValueError("literal endpoint mismatch")
    if not difference[witness["output"]][0]:
        raise ValueError("zero endpoint is not a witness")
    return difference


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("program", type=Path)
    parser.add_argument("witness", type=Path)
    args = parser.parse_args()
    check(json.loads(args.program.read_text()), json.loads(args.witness.read_text()))
    print("PASS_SPD_INVERSE_WITNESS_CHECKED")


if __name__ == "__main__":
    main()
