"""Construct an orthogonal witness for a false complete rational inverse identity.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from literal import degree_bound, replay
from algebra import produce
from syntax import validate


def construct(program, parameter_cap=Fraction(1, 4)):
    if validate(program).characteristic:
        raise ValueError("the orthogonal construction requires Q")
    parameter_cap = Fraction(parameter_cap)
    if not 0 < parameter_cap <= Fraction(1, 4):
        raise ValueError("parameter cap must be in (0, 1/4]")
    coefficient = produce(program)
    if coefficient["verdict"] != "different":
        raise ValueError("equal programs have no distinguishing witness")
    word = coefficient["word"]
    n = len(word) + 1
    degree = degree_bound(program, n)
    for index in range(1, degree + 2):
        parameter = parameter_cap * (degree + 2 - index) / (degree + 1)
        difference = replay(program, word, parameter, coefficient["input"])
        if difference[coefficient["output"]][0]:
            return {
                "schema": "orthogonal-inverse-witness/v1",
                "program_sha256": coefficient["program_sha256"],
                "word": word, "dimension": n,
                "input": coefficient["input"], "output": coefficient["output"],
                "parameter": str(parameter), "parameter_cap": str(parameter_cap),
                "numerator_degree_bound": degree,
                "grid_size": degree + 1, "grid_index": index,
                "endpoint_difference": [[str(x) for x in row] for row in difference],
            }
    raise ValueError("the proved root budget was exhausted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("program", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--parameter-cap", default="1/4")
    args = parser.parse_args()
    result = construct(json.loads(args.program.read_text()), Fraction(args.parameter_cap))
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PASS_ORTHOGONAL_INVERSE_WITNESS_PRODUCED")


if __name__ == "__main__":
    main()
