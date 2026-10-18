#!/usr/bin/env python3
"""Independent flat-vector boundary replay of every committed ladder block."""

import gzip
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("ladder", HERE / "circuit.py")
ladder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ladder)


def execute(stream, index, basis_column):
    values = [Q(int(i == basis_column)) for i in range(len(index))]
    for op in stream:
        t = index[op[1]]
        if op[0] == "clear":
            values[t] = Q(0)
        elif op[0] == "add":
            values[t] += op[3] * values[index[op[2]]]
        elif op[0] == "double":
            values[t] *= 2
        elif op[0] == "half":
            values[t] /= 2
        else:
            raise ValueError("unexpected block primitive")
    return values


def main():
    programs_path = ROOT / "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/LOCAL-PROGRAMS.json.gz"
    payload = gzip.decompress(programs_path.read_bytes())
    pins = json.loads((HERE / "SOURCES.json").read_text())["sha256"]
    if hashlib.sha256(payload).hexdigest() != pins[str(programs_path.relative_to(ROOT))]:
        raise ValueError("program source pin mismatch")
    programs = json.loads(payload)
    receipt = json.loads((HERE / "RESULT.json").read_text())
    blocks, columns, missing_clear_rejections = 0, 0, 0
    for orientation, data in receipt["programs"].items():
        events = programs[orientation]
        recorded = [(r["start"], r["stop"]) for r in data["blocks"]]
        if recorded != ladder.select_blocks(events):
            raise ValueError("recorded block inventory differs")
        for i, j in recorded:
            group = events[i:j]
            registers = sorted({tuple(e[1][1]) for e in group} | {tuple(e[1][2]) for e in group})
            registers.append(("W", 0))
            index = {r: k for k, r in enumerate(registers)}
            stream = ladder.lower_block(group)
            for col in range(len(registers)):
                expected = [Q(int(k == col)) for k in range(len(registers))]
                for e in group:
                    op = e[1]
                    expected[index[tuple(op[1])]] += Q(op[3], op[4]) * expected[index[tuple(op[2])]]
                expected[index["W", 0]] = Q(0)
                actual = execute(stream, index, col)
                if actual != expected:
                    raise ValueError(f"column mismatch: {orientation}:{i}:{col}")
                columns += 1
            # For the source basis, the last work value is nonzero. Every
            # block must therefore detect omission of its final clear.
            source_col = index[tuple(group[0][1][2])]
            if execute(stream[:-1], index, source_col)[index["W", 0]] == 0:
                raise ValueError("missing final clear accepted")
            missing_clear_rejections += 1
            blocks += 1
    print(f"PASS_CK_LADDER_COLUMNS blocks={blocks} columns={columns} missing_clear_rejections={missing_clear_rejections}")


if __name__ == "__main__":
    main()
