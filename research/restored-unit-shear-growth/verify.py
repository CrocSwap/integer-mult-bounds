"""Bounded exhaustive corroboration; no predecessor executable is imported.

Produced by Nick Petalas. Apache-2.0.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import attaining_word, check_loop, fibonacci, identity, need, trace
from oracle import scalar_census


def matrix_census(n: int, depth: int) -> dict:
    need((n, depth) in ((2, 8), (3, 5)), "matrix census domain")
    alphabet = tuple((i, j, sign) for i in range(n) for j in range(n)
                     if i != j for sign in (-1, 1))
    rows = []
    for length in range(depth + 1):
        visited = closed = 0
        peak_entry = peak_norm = 1
        for word in itertools.product(alphabet, repeat=length):
            endpoint, _ = trace(n, word)
            visited += 1
            if endpoint != identity(n):
                continue
            closed += 1
            entry, norm = check_loop(n, word, length)
            peak_entry, peak_norm = max(peak_entry, entry), max(peak_norm, norm)
        need(visited == len(alphabet) ** length, "complete alphabet coverage")
        rows.append({"length": length, "words": visited, "closed": closed,
                     "max_entry": peak_entry if closed else None,
                     "max_norm": peak_norm if closed else None})
    return {"rows": n, "depth": depth, "by_length": rows}


def sharpness() -> dict:
    digest = hashlib.sha256()
    checked = 0
    for steps in range(129):
        word = attaining_word(steps)
        expected = fibonacci(steps + 1), fibonacci(steps + 2)
        for n in (2, 3, 8):
            peak = check_loop(n, word, 2 * steps)
            need(peak == expected, "sharp coefficient and norm")
            endpoint, heights = trace(n, word)
            need(endpoint == identity(n), "attainer dirty spectators")
            digest.update(json.dumps([n, steps, heights]).encode())
            checked += 1
        if steps < 128:
            need(check_loop(2, word, 2 * steps + 1) == expected, "odd budget")
    return {"even_budget_attainers": checked, "odd_budget_attainers": 128,
            "trace_sha256": digest.hexdigest()}


def controls() -> int:
    valid = attaining_word(3)
    invalid = (
        (2, valid[:-1], 5),
        (2, ((0, 1, 1),), 1),
        (2, ((0, 1, 2),), 1),
        (2, ((0, 0, 1),), 1),
        (2, ((0, 2, 1),), 1),
        (2, ((0, 1, True),), 1),
        (0, (), 0),
        (9, (), 0),
        (2, valid, 5),
        (2, (), 257),
    )
    rejected = 0
    for n, word, budget in invalid:
        try:
            check_loop(n, word, budget)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid loop was admitted")
    need(check_loop(1, (), 0) == (1, 1), "one-row empty word")
    need(check_loop(2, attaining_word(1), 2)[1] > fibonacci(2),
         "one-index-too-small norm bound must fail")
    return rejected + 2


def compare_oracle(primary: dict, other: dict) -> None:
    need(primary["rows"] == other["rows"], "oracle dimension")
    for row in other["by_length"]:
        observed = primary["by_length"][row["length"]]
        for key in ("length", "words", "closed", "max_norm"):
            need(observed[key] == row[key], "matrix/scalar oracle: " + key)


def magnitude_guards() -> int:
    checked = 0
    for steps in range(33):
        for height in (0, 1, 2, 3, 7, 8, 31):
            cells = [height, height]
            cap = height * fibonacci(steps + 2)
            peak = height
            for target, source, sign in attaining_word(steps):
                cells[target] += sign * cells[source]
                peak = max(peak, *map(abs, cells))
            need(cells == [height, height] and peak == cap, "literal sharp guard")
            width = 1 + cap.bit_length()
            need(cap <= 2 ** (width - 1) - 1, "signed width suffices")
            if cap:
                need(cap > 2 ** (width - 2) - 1, "smaller width fails")
            checked += 1
    return checked


def main() -> None:
    primary = [matrix_census(2, 8), matrix_census(3, 5)]
    independent = [scalar_census(2, 6), scalar_census(3, 4)]
    for matrix, scalar in zip(primary, independent):
        compare_oracle(matrix, scalar)
    result = {"claim_type": "scoped proof with finite corroboration",
              "matrix_censuses": primary, "scalar_censuses": independent,
              "sharpness": sharpness(), "controls": controls(),
              "literal_magnitude_guards": magnitude_guards()}
    here = Path(__file__).resolve().parent
    result["file_sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(here.iterdir()) if p.is_file()
    }
    print(json.dumps(result, sort_keys=True))
    print("PASS_RESTORED_UNIT_SHEAR_GROWTH")


if __name__ == "__main__":
    main()
