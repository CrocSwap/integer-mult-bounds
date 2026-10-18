#!/usr/bin/env python3
"""Independent bit/carry solution counter; imports no other project code.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
MAX_BITS = 6


def check(condition, message):
    if not condition:
        raise ValueError(message)


def solutions(bits, mask, slope, offset, *, require_zero_final_carry=False):
    """Count a*y+b == y XOR M modulo 2^L without enumerating addresses.

    The state is the unconsumed multiplication/addition carry. Branch on the
    next bit of y, compare one output bit, and merge equal carry states.
    """
    carries = {offset: 1}
    for position in range(bits):
        wanted_xor = (mask >> position) & 1
        next_carries = {}
        for carry, count in carries.items():
            for digit in (0, 1):
                value = carry + slope * digit
                if value % 2 == (digit ^ wanted_xor):
                    successor = value // 2
                    next_carries[successor] = next_carries.get(successor, 0) + count
        carries = next_carries
    # Congruence modulo 2^L intentionally ignores all higher output bits.
    return carries.get(0, 0) if require_zero_final_carry else sum(carries.values())


def run():
    primary = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    rows = []
    for bits in range(1, MAX_BITS + 1):
        size = 2 ** bits
        digest = sha256()
        for mask in range(size):
            digits = [(mask // 2 ** i) % 2 for i in range(bits - 1)]
            expected = 2 ** (bits - min(digits.count(0), digits.count(1)))
            global_maximum = 0
            for slope in range(size):
                counts = [solutions(bits, mask, slope, offset) for offset in range(size)]
                check(sum(counts) == size, "Bit/carry partition is incomplete")
                global_maximum = max(global_maximum, max(counts))
                digest.update(struct.pack("<" + "I" * size, *counts))
            check(global_maximum == expected, "All-slope maximum differs")
        row = {"bits": bits, "agreement_counts_covered": size ** 3,
               "all_histograms_sha256": digest.hexdigest()}
        reference = primary["census"][bits - 1]
        check(reference["bits"] == bits, "Missing primary width")
        check(row["all_histograms_sha256"] == reference["all_histograms_sha256"],
              "Independent histogram differs from literal enumeration")
        rows.append(row)

    # Negative control: integer equality is not modular equality.
    modular = solutions(6, 15, 63, 15)
    integer_only = solutions(6, 15, 63, 15, require_zero_final_carry=True)
    check(modular == 32 and integer_only == 1, "Final-carry control changed")
    check(modular != integer_only, "Dropping nonzero final carries went undetected")
    return {
        "status": "PASS_XOR_AFFINE_INDEPENDENT",
        "method": "Least-significant-bit multiplication/addition carry automaton; no address loop, project imports, or primary formula calls.",
        "bits_inclusive": [1, MAX_BITS], "mask_count": 126,
        "agreement_counts_covered": sum(row["agreement_counts_covered"] for row in rows),
        "census": rows,
        "negative_control": {"bits": 6, "mask": 15, "slope": 63, "offset": 15,
                             "modular_solutions": modular, "integer_equality_solutions": integer_only},
        "scope": "Finite independent cross-check; the universal argument is a written proof, not a finite census.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = run()
    receipt = HERE / "INDEPENDENT.json"
    if args.write:
        receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    else:
        check(report == json.loads(receipt.read_text(encoding="utf-8")), "Independent receipt differs")
    print("PASS_XOR_AFFINE_INDEPENDENT: 126 masks; 299,592 exact agreement counts; final-carry control rejected")


if __name__ == "__main__":
    main()
