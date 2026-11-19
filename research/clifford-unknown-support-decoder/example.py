"""Emit a four-qubit tensor train for two measured parities."""

import argparse
import json
from pathlib import Path


def syndrome(x):
    edges = ((0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3))
    return sum(((x >> a) & (x >> b) & 1) << j for j, (a, b) in enumerate(edges))


def observation(width=13):
    if width < 2:
        raise ValueError("the parity example needs at least two sites")
    records = [[], [], []]
    # Codes 0, 1, 2 and 3 are powers of i. The canonical dense chart is -W/16.
    amplitudes = (("-1/16", 0), (0, "-1/16"), ("1/16", 0), (0, "1/16"))
    for x in range(16):
        tag = syndrome(x)
        for y in range(16):
            q = 16*x + y
            phase = (2*((x & y).bit_count() % 2) + (x & 1)) % 4
            for offset, size, delta, target, extra in (
                (0, 16, tag & 15, 11, 0), (16, 4, tag >> 4, 2, 1)
            ):
                records[0].append([q, 0, offset + delta, *amplitudes[phase]])
                for state in range(size):
                    records[1].append([q, offset+state, offset+(state ^ delta),
                                       *amplitudes[phase]])
                records[2].append([q, offset+(target ^ delta), 0,
                                   *amplitudes[(phase+extra) % 4]])
    return dict(format="clifford-tt/1", qubits=4,
                cores=[dict(left=a, right=b, entries=r) for (a,b),r in
                       zip(((1,20),(20,20),(20,1)), records, strict=True)],
                sites=[0] + [1]*(width-2) + [2])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--width", type=int, default=13)
    args = parser.parse_args()
    args.output.write_text(json.dumps(observation(args.width), separators=(",", ":")) + "\n")
