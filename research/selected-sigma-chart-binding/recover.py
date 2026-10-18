#!/usr/bin/env python3
"""Recover PR1879 five-array witnesses from the selected raw dictionary only.

This producer is deliberately not imported by verify.py. No source port basis,
provider recipe or predecessor checker is used to find a factorization.
Prepared for Adam Gall with OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import gzip
from pathlib import Path

from verify import canonical, load_inputs, require


def unit_index(value: int) -> int | None:
    return value.bit_length() - 1 if value > 0 and value & (value - 1) == 0 else None


def recover(columns: list[int]) -> list[list[int]]:
    """Find A=(I+u*a^T)P, with a.u=0, using only the packed columns.

    If A is not a permutation, any nonunit column v must be e_i+u. Thus
    v+e_i, i=0..n-1, contains every possible u. Each proposed u gives a
    bipartite matching problem between columns and coordinate units. A
    successful matching explicitly determines P and a. The final checker,
    not this search, is the acceptance oracle.
    """
    n = len(columns)
    anchor = next((v for v in columns if unit_index(v) is None), None)
    candidates = [0] if anchor is None else [anchor ^ (1 << i) for i in range(n)]
    for update in candidates:
        options = []
        for column in columns:
            choices = []
            index = unit_index(column)
            if index is not None:
                choices.append((index, 0))
            index = unit_index(column ^ update)
            if index is not None and update:
                choices.append((index, 1))
            if not choices:
                break
            options.append(choices)
        if len(options) != n:
            continue
        owner = [-1] * n
        chosen = [None] * n

        def augment(column: int, seen: set[int]) -> bool:
            for index, coefficient in options[column]:
                if index in seen:
                    continue
                seen.add(index)
                if owner[index] < 0 or augment(owner[index], seen):
                    owner[index] = column
                    chosen[column] = (index, coefficient)
                    return True
            return False

        if not all(augment(column, set()) for column in range(n)):
            continue
        forward = [item[0] for item in chosen]
        coefficients = sum(item[1] << item[0] for item in chosen)
        if (update & coefficients).bit_count() % 2:
            continue
        backward = [0] * n
        for column, index in enumerate(forward):
            backward[index] = column
        return [forward, backward, columns,
                [(update >> i) & 1 for i in range(n)],
                [(coefficients >> i) & 1 for i in range(n)]]
    raise ValueError("no recovered permutation/transvection certificate; no singularity claim")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="New .json.gz file; existing outputs are refused")
    args = parser.parse_args()
    require(not args.output.exists(), "refusing to replace an existing witness")
    values, _ = load_inputs()
    entries = {key: recover(columns) for key, columns in sorted(values["sigmas"].items())}
    witness = {"format": "pr1879-five-array-chart-witnesses-v1", "dimension": 73, "entries": entries}
    payload = canonical(witness)
    with args.output.open("xb") as output:
        output.write(gzip.compress(payload, mtime=0))
    print(f"RECOVERED_SELECTED_SIGMA_WITNESSES charts={len(entries)} dimension=73 payload_bytes={len(payload)}")


if __name__ == "__main__":
    main()
