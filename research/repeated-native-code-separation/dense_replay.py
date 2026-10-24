"""Replay the native moments from the dense owner matrix.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
This implementation does not use the eight-mode native replay.
"""

from fractions import Fraction
import json
from pathlib import Path

import numpy as np

PRIME = 65521
VOLUME = 1 << 17


def replay(source: Path, count: int) -> list[list[int]]:
    code = json.loads((source / "CODE.json").read_text())["A"]
    ports = json.loads((source / "NORMALIZERS.json").read_text())["ports"]
    # The dense operator is 28 P. The saved operator is 56 P.
    matrix = np.array(
        [[2 * (i == j) - int(2 * Fraction(code[i][j])) for j in range(112)]
         for i in range(112)], dtype=np.float64
    )
    if max(sum(abs(x) for x in row) for row in matrix) * (PRIME - 1) >= 2**24:
        raise ValueError("The exact binary64 sum bound does not apply")
    maps, signs = [], []
    for port in ports:
        rows = port["G_rows"]
        ys = [sum(((row & x).bit_count() % 2) << j for j, row in enumerate(rows))
              for x in range(512)]
        maps.append(np.array(ys, dtype=np.int32))
        signs.append(np.array(
            [(-1) ** ((port["Z_mask"] & y).bit_count()) for y in ys], dtype=np.int32
        ))
    addresses = np.arange(VOLUME, dtype=np.int32)
    state = np.zeros((112, VOLUME), dtype=np.int32)
    state[0, 1] = 1
    records = []
    for n in range(count):
        records.append((state[:, 1].astype(np.int64) * pow(2, n, PRIME) % PRIME).tolist())
        if n + 1 == count:
            break
        stage = 1 - (n % 2)
        shift = 1 + 8 * stage
        mask = 1 | (255 << shift)
        local = (addresses & 1) | (((addresses >> shift) & 255) << 1)
        remote = addresses & ~mask
        middle = np.empty_like(state)
        for owner in range(112):
            y0 = maps[owner][local]
            y = remote | (y0 & 1) | ((y0 >> 1) << shift)
            middle[owner, y] = signs[owner][local] * state[owner]
        # All operands and all partial sums are integers below 2**24 in
        # absolute value. Binary64 computes each product and sum exactly.
        for start in range(0, VOLUME, 4096):
            stop = start + 4096
            output = matrix @ middle[:, start:stop].astype(np.float64)
            if not np.array_equal(output, np.rint(output)):
                raise ValueError("The dense result is not integral")
            middle[:, start:stop] = output.astype(np.int64) % PRIME
        for owner in range(112):
            y0 = maps[owner][local]
            y = remote | (y0 & 1) | ((y0 >> 1) << shift)
            state[owner] = (signs[owner][local] * middle[owner, y]) % PRIME
    return records
