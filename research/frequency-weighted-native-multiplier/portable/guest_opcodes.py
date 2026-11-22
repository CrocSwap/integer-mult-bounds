"""Read every instruction and control depth of the pinned CPython guest."""

import json
from collections import Counter
from pathlib import Path

from module_census import Reader


def leb(rd):
    for _ in range(10):
        if rd.byte() < 128:
            return
    raise ValueError("long leb")


def max_free_segment(ops):
    """Bound each forward run of free operators up to a return or fuel charge."""
    blocks = []
    ends = {}
    for offset, op in enumerate(ops):
        if op in (2, 3, 4):
            blocks.append(offset)
        elif op == 5:
            assert ops[blocks[-1]] == 4
            blocks[-1] = offset
        elif op == 11 and blocks:
            begin = blocks.pop()
            if ops[begin] == 5:
                ends[begin] = offset
    assert not blocks
    run = [0] * (len(ops) + 1)
    for offset in reversed(range(len(ops))):
        op = ops[offset]
        if op in (0, 15):
            run[offset] = 1
        elif op in (1, 2, 3, 11, 26):
            run[offset] = 1 + run[offset + 1]
        elif op == 5:
            end = ends[offset]
            run[offset] = 1 + max(run[end], run[end + 1])
    return max(run)


def census(raw):
    rd = Reader(raw)
    rd.take(8)
    counts = Counter()
    max_depth = 0
    free = 0
    while rd.i < len(rd.raw):
        section = rd.byte()
        body = rd.take(rd.uint())
        if section != 10:
            continue
        for _ in range(body.uint()):
            code = body.take(body.uint())
            depth = 1
            ops = []
            for _ in range(code.uint()):
                code.uint()
                code.byte()
            while code.i < len(code.raw):
                op = code.byte()
                ops.append(op)
                name = f"{op:02x}"
                counts[name] += 1
                if op in (0x02, 0x03, 0x04):
                    # These forms have no block parameters and at most one result.
                    assert code.raw[code.i] in (0x40, 0x7C, 0x7D, 0x7E, 0x7F)
                    leb(code)
                    depth += 1
                    max_depth = max(max_depth, depth)
                elif op == 0x0B:
                    depth -= 1
                elif op in (
                    0x0C,
                    0x0D,
                    0x10,
                    0x20,
                    0x21,
                    0x22,
                    0x23,
                    0x24,
                    0x25,
                    0x26,
                    0xD2,
                ):
                    code.uint()
                elif op == 0x0E:
                    for _ in range(code.uint() + 1):
                        code.uint()
                elif op == 0x11:
                    code.uint()
                    code.uint()
                elif op == 0x1C:
                    code.take(code.uint())
                elif 0x28 <= op <= 0x3E:
                    code.uint()
                    code.uint()
                elif op in (0x3F, 0x40):
                    code.uint()
                elif op in (0x41, 0x42, 0xD0):
                    leb(code)
                elif op == 0x43:
                    code.take(4)
                elif op == 0x44:
                    code.take(8)
                elif op == 0xFC:
                    ext = code.uint()
                    counts[f"fc.{ext}"] += 1
                    if ext in (8, 10, 12, 14):
                        code.uint()
                        code.uint()
                    elif ext in (9, 11, 13, 15, 16, 17):
                        code.uint()
                    else:
                        assert ext < 8
                else:
                    assert (
                        op in (0, 1, 5, 0x0F, 0x1A, 0x1B, 0xD1) or 0x45 <= op <= 0xC4
                    ), (op, code.i)
                assert depth >= 0 and (depth or code.i == len(code.raw))
            assert depth == 0
            free = max(free, max_free_segment(ops))
    return counts, max_depth, free


if __name__ == "__main__":
    c, d, f = census((Path(__file__).parent / "python-3.12.0.wasm").read_bytes())
    print(
        json.dumps(
            {
                "instructions": sum(v for k, v in c.items() if "." not in k),
                "max_control_depth": d,
                "max_free_segment": f,
                "opcode_counts": c,
            },
            indent=2,
            sort_keys=True,
        )
    )
