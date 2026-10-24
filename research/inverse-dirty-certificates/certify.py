"""Produce an exact inverse-aware certificate, without expanding group words.

Prepared for Krzysztof Wójt with OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import json
from pathlib import Path

from algebra import compile_program, produce
from fields import Field
from oracles import apply_witness, unipotent_operators


def explicit_witness(program, certificate):
    if certificate["verdict"] != "different":
        raise ValueError("an equal endpoint has no distinguishing witness")
    f = Field(program["field"])
    word = certificate["word"]
    n = len(word) + 1
    operators = unipotent_operators(program, word)
    encode = lambda row: [f.dump(x) for x in row]
    inputs = {role: encode([f.one if i == certificate["input"] and j == n-1 else f.zero
                            for j in range(n)]) for i, role in enumerate(program["roles"])}
    differences = apply_witness(program, word, program["roles"][certificate["input"]])
    return {"schema": "inverse-dirty-witness/v1", "program_sha256": certificate["program_sha256"],
            "field": program["field"], "dimension": n,
            "operators": {a: [encode(row) for row in matrix] for a, matrix in operators.items()},
            "inputs": inputs,
            "endpoint_difference": {role: encode(row) for role, row in zip(program["roles"], differences)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("program", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--witness", type=Path, help="also export literal matrices and inputs on failure")
    args = parser.parse_args()
    program = json.loads(args.program.read_text(encoding="utf-8"))
    certificate = produce(program)
    witness = explicit_witness(program, certificate) if args.witness else None
    args.output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
    if args.witness:
        args.witness.write_text(json.dumps(witness, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": certificate["verdict"],
                      "states": compile_program(program)["dimension"],
                      "certificate": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
