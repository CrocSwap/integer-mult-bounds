#!/usr/bin/env python3
"""Separate integer-matrix check of the copied-center circuit identities.

Does not use verify.py's primitive interpreter, prefix engine, or costing.
It imports only its deterministic rewrite and source binding. Apache-2.0.
Prepared for @ssteeper with substantial OpenAI Codex assistance.
"""

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("quarter", HERE / "verify.py")
quarter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quarter)


def demand(condition, message):
    if not condition:
        raise ValueError(message)


def integer_boundary(block, backward):
    """All coefficients are stored as integers in units of one quarter.

    The tested block has exactly one quarter factor on every dependency path;
    divisibility checks make any attempted second factor observable.
    """
    scalars = [e[1] for e in block if e[0] == "scalar"]
    regs = sorted({tuple(op[1]) for op in scalars} |
                  {tuple(op[2]) for op in scalars if op[0] in ("copy", "add")})
    index = {r: i for i, r in enumerate(regs)}
    size = len(regs)
    matrix = [[4 * int(i == j) for j in range(size)] for i in range(size)]
    for op in scalars:
        target = index[tuple(op[1])]
        if op[0] == "clear":
            matrix[target] = [0] * size
        elif op[0] == "copy":
            matrix[target] = matrix[index[tuple(op[2])]].copy()
        elif op[0] == "scale":
            a, b = op[2:4]
            demand(all(a * x % b == 0 for x in matrix[target]), "nonintegral quarter grid")
            matrix[target] = [a * x // b for x in matrix[target]]
        elif op[0] == "add":
            source = index[tuple(op[2])]
            a, b = op[3:5]
            demand(all(a * x % b == 0 for x in matrix[source]), "nonintegral tap grid")
            matrix[target] = [x + a * y // b for x, y in zip(matrix[target], matrix[source])]
        else:
            raise ValueError("unknown operation")

    # Direct gather/scatter specification, not a replay of the old block.
    center = next(r for r in regs if r[0] == "C")
    expected = [[4 * int(i == j) for j in range(size)] for i in range(size)]
    expected[index[center]] = [0] * size
    if backward:
        send = next(op for op in scalars if op[0] == "add" and op[2] == list(center))
        recipient = index[tuple(send[1])]
        taps = [op for op in scalars if op[0] == "add" and op[1] == list(center)]
        for op in taps:
            expected[recipient][index[tuple(op[2])]] -= op[3]
    else:
        copied = next(op for op in scalars if op[0] == "copy")
        source = index[tuple(copied[2])]
        taps = [op for op in scalars if op[0] == "add"]
        for op in taps:
            expected[index[tuple(op[1])]][source] += op[3]
    demand(len(taps) == 28 and matrix == expected, "direct integer block specification")
    return size * size


def main():
    quarter.check_sources()
    entries = 0
    cases = 0
    controls = 0
    for name in quarter.PROVIDERS:
        programs = quarter.read(quarter.ROOT / quarter.REPLAY / name / "LOCAL-PROGRAMS.json.gz")
        for direction, events in programs.items():
            back = direction == "backward"
            new, _ = quarter.transform(events, back)
            start, _, blocks = quarter.center_blocks(events)
            for k, old in enumerate(blocks):
                candidate = new[start + 33*k:start + 33*(k+1)]
                entries += integer_boundary(old, back) + integer_boundary(candidate, back)
                cases += 2
                # The incoming private coordinate is included in the matrix.
                # Only backward initial clears are indispensable: forward copy
                # overwrites that dirt, so no false omission claim is made.
                bad = candidate[1:] if back else candidate[:-1]
                try:
                    integer_boundary(bad, back)
                except ValueError:
                    controls += 1
                else:
                    raise ValueError("dirty/private clear omission accepted")
    print(f"PASS_CENTER_QUARTER_INTEGER blocks={cases} matrix_entries={entries} clear_controls={controls}")


if __name__ == "__main__":
    main()
