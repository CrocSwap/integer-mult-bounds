# SPDX-License-Identifier: Apache-2.0
"""Separate fixed-denominator integer replay of every normalized prefix row."""

import hashlib
import json
from math import gcd

UNIT = 1 << 32


def trace(events):
    if not 1 <= len(events) <= 30_000:
        raise ValueError("bounded integer stream")
    rows = {r: {(r, ()): UNIT} for r in range(632)}
    digest = hashlib.sha256()
    active = False
    for index, event in enumerate(events):
        if event == ["phase", "A"]:
            active = True
        if event == ["phase", "centers"]:
            if not active:
                raise ValueError("integer phase order")
            return digest.hexdigest()
        if event[0] not in ("scalar", "warp"):
            continue
        if event[0] == "warp":
            target, op = event[1][1], event[2]
            changed = {}
            for (v, word), z in rows[target].items():
                moved = list(word)
                if moved and moved[0] + op == 0:
                    del moved[0]
                else:
                    moved.insert(0, op)
                changed[v, tuple(moved)] = z
        else:
            gate = event[1]
            target = gate[1][1]
            source, numerator, denominator = (
                (target, gate[2], gate[3])
                if gate[0] == "scale"
                else (gate[2][1], gate[3], gate[4])
            )
            changed = {} if gate[0] == "scale" else dict(rows[target])
            for atom, z in rows[source].items():
                product, remainder = divmod(z * numerator, denominator)
                if remainder:
                    raise ValueError("fixed integer grid exhausted")
                changed[atom] = changed.get(atom, 0) + product
            changed = {a: z for a, z in changed.items() if z}
        if len(changed) > 4096 or any(len(w) > 256 for _, w in changed):
            raise ValueError("integer support bound")
        rows[target] = changed
        encoded = []
        for (v, w), z in sorted(changed.items()):
            divisor = gcd(abs(z), UNIT)
            encoded.append([v, list(w), z // divisor, UNIT // divisor])
        digest.update(
            json.dumps(
                [index, ["L", target], encoded], sort_keys=True, separators=(",", ":")
            ).encode()
        )
    raise ValueError("missing integer stage end")
