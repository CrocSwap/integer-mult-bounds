"""Exact XOR-layout subsequence enumerator. Produced by Nick Petalas.

Apache-2.0. The finite certificate corroborates the written all-size proof.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(n, mask, limit):
    require(type(n) is int and 0 <= n <= limit, "invalid bit width")
    require(type(mask) is int and 0 <= mask < 1 << n, "invalid XOR mask")


def polynomial(n, mask):
    """Coefficients include the empty subsequence; at most 1024 addresses."""
    validate(n, mask, 10)
    result = [1, 1]
    for bit in range(n):
        if (mask >> bit) & 1:
            square = [0] * (2 * len(result) - 1)
            for i, left in enumerate(result):
                for j, right in enumerate(result):
                    square[i + j] += left * right
            result = square
        else:
            result = [1] + [2 * value for value in result[1:]]
    require(result[0] == 1 and result[1] == 1 << n, "bad normalization")
    return result


def longest_parameters(n, mask):
    """Return (maximum length, log2 of its multiplicity), without huge counts."""
    validate(n, mask, 4096)
    exponent = ones_above = 0
    for bit in range(n - 1, -1, -1):
        if (mask >> bit) & 1:
            ones_above += 1
        else:
            exponent += 1 << ones_above
    return 1 << ones_above, exponent


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def enumerate_cases():
    spec = importlib.util.spec_from_file_location("xor_count_oracle", Path(__file__).with_name("oracle.py"))
    require(spec is not None and spec.loader is not None, "missing oracle")
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    digest = hashlib.sha256()
    cases = subsets = longest_cases = 0
    for n in range(8):
        for mask in range(1 << n):
            predicted = polynomial(n, mask)
            observed = oracle.by_endpoints(n, mask)
            require(predicted == observed, f"polynomial disagreement {n},{mask}")
            length, exponent = longest_parameters(n, mask)
            require((len(predicted) - 1, predicted[-1]) == (length, 1 << exponent), "leading term")
            if n <= 4:
                brute = oracle.by_subsets(n, mask)
                require(predicted == brute, f"subset disagreement {n},{mask}")
                subsets += 1 << (1 << n)
            digest.update(canonical([n, mask, predicted]) + b"\n")
            cases += 1
    for n in range(11):
        for mask in range(1 << n):
            length, count = oracle.longest_only(n, mask)
            expected_length, exponent = longest_parameters(n, mask)
            require((length, count) == (expected_length, 1 << exponent), "LDS count disagreement")
            longest_cases += 1
    return {"polynomial_cases": cases, "subsets_enumerated": subsets,
            "longest_count_cases": longest_cases, "polynomial_sha256": digest.hexdigest()}


def rejection_controls():
    rejected = 0
    for n, mask in [(-1, 0), (11, 0), (2, -1), (2, 4), (True, 0), (2, True), (2.0, 0)]:
        try:
            polynomial(n, mask)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid input accepted")
    require(polynomial(2, 1) == [1, 4, 2], "low-bit fixture")
    require(polynomial(2, 2) == [1, 4, 4], "high-bit fixture")
    require(polynomial(2, 1) != polynomial(2, 2), "bit-order mutant escaped")
    require(polynomial(2, 2) != [1, 4, 2], "length-only multiplicity mutant escaped")
    require(polynomial(2, 2) != [1, 4, 6, 4, 1], "ignored-order mutant escaped")
    return {"invalid_inputs": rejected, "semantic_mutants": 3}


def build_receipt():
    package = Path(__file__).resolve().parent
    files = ["README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py", "oracle.py"]
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in files}
    return {"schema": "xor-subsequence-enumerator/v1", "source_sha256": hashes,
            "finite_evidence": enumerate_cases(), "controls": rejection_controls(),
            "fixtures": {"n2_mask1": polynomial(2, 1), "n2_mask2": polynomial(2, 2)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print a generated receipt without comparison")
    args = parser.parse_args()
    actual = build_receipt()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    expected = json.loads(Path(__file__).with_name("RECEIPT.json").read_text())
    require(canonical(actual) == canonical(expected), "receipt or source mismatch")
    print("PASS_XOR_SUBSEQUENCE_ENUMERATOR " + json.dumps(actual["finite_evidence"], sort_keys=True))
    print("PASS_CONTROLS " + json.dumps(actual["controls"], sort_keys=True))


if __name__ == "__main__":
    main()
