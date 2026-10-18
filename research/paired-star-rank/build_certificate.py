#!/usr/bin/env python3
"""Build literal signed-star information-set certificates (Apache-2.0).

Prepared for ellipsi2 with substantial OpenAI Codex assistance.
The separate verifier does not import this module or its elimination routine.
"""

import argparse
import itertools
import json
from pathlib import Path


def signed_sets(p, degree):
    for pairs in itertools.combinations(range(p), degree):
        for signs in itertools.product((0, 1), repeat=degree):
            yield sum(1 << (2 * pair + sign) for pair, sign in zip(pairs, signs))


def build(p, k, include_empty):
    ports = list(signed_sets(p, k))
    stars = [s for d in range(0 if include_empty else 1, k)
             for s in signed_sets(p, d)]
    basis = {}
    for index, star in enumerate(stars):
        row = sum(1 << col for col, port in enumerate(ports) if port & star == star)
        coefficients = 1 << index
        while row:
            pivot = (row & -row).bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (row, coefficients)
                break
            other, combination = basis[pivot]
            row ^= other
            coefficients ^= combination
    pivots = sorted(basis)
    for pivot in reversed(pivots):
        row, coefficients = basis[pivot]
        for earlier in pivots:
            if earlier >= pivot:
                break
            previous, combination = basis[earlier]
            if previous >> pivot & 1:
                basis[earlier] = (previous ^ row, combination ^ coefficients)
    return {
        "p": p,
        "k": k,
        "include_empty": include_empty,
        "ports": ports,
        "stars": stars,
        "information_set": [ports[pivot] for pivot in pivots],
        "decoders_hex": [hex(basis[pivot][1]) for pivot in pivots],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    domains = [(p, k) for k in (2, 3, 4) for p in range(k, 9)]
    payload = {
        "format": "signed-star-information-sets-v1",
        "assignment_seed": 46,
        "principal_domain": [8, 4],
        "cases": [build(p, k, empty) for p, k in domains for empty in (False, True)],
    }
    args.output.write_bytes((json.dumps(payload, indent=2) + "\n").encode("utf-8"))
    for case in payload["cases"]:
        print(f"p={case['p']} k={case['k']} empty={case['include_empty']} "
              f"ports={len(case['ports'])} rank={len(case['information_set'])}")


if __name__ == "__main__":
    main()
