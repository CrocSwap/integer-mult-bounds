"""Exact endpoint, physical-trace and payload-invoice checks; writes no files."""

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

from stream import MAX_L, MAX_R, admit, require, switch


def expected(bits: list[int], length: int, suffix: int, width: int,
             controls: list[int]) -> list[int]:
    # Address-wise oracle, independent of staging or stream order.
    out = [-1] * len(bits)
    for address in range(1 << length):
        prefix = address >> (suffix + 1)
        destination = address ^ (controls[prefix] << suffix)
        for bit in range(width):
            out[destination * width + bit] = bits[address * width + bit]
    return out


def replay(bits: list[int], size: int, trace: list) -> tuple[list, Counter, int]:
    # A separate sparse, unit-action interpreter. Only the trace is shared.
    stores = [dict(enumerate(bits)), {}, {}]
    positions = [0, 0, 0]
    capacities = [len(bits), len(bits), size]
    names = {"source": 0, "output": 1, "scratch": 2}
    counts: Counter = Counter()
    peak = 0
    require(len(trace) <= 10 * len(bits), "trace capacity")
    for name, operation, operand in trace:
        require(name in names, "unknown tape")
        number = names[name]
        position = positions[number]
        counts[operation] += 1
        if operation == "move":
            require(type(operand) is int and operand in (-1, 1), "bad move")
            positions[number] += operand
            require(0 <= positions[number] <= capacities[number], "move bounds")
        else:
            require(0 <= position < capacities[number], "cell bounds")
            if number == 2:
                peak = max(peak, position + 1)
            if operation == "read":
                require(operand in (0, 1) and stores[number].get(position) == operand,
                        "read transcript disagrees with tape")
            else:
                require(operation == "write" and number != 0, "invalid write")
                require(operand is None or type(operand) is int and operand in (0, 1),
                        "bad symbol")
                if operand is None:
                    stores[number].pop(position, None)
                else:
                    stores[number][position] = operand
    require(positions == [0, 0, 0], "unreturned heads")
    require(stores[0] == dict(enumerate(bits)), "changed source")
    require(not stores[2], "dirty scratch")
    require(len(stores[1]) == len(bits), "incomplete output")
    return [stores[1][j] for j in range(len(bits))], counts, peak


def check_case(bits: list[int], length: int, suffix: int, width: int,
               controls: list[int], transcript) -> dict:
    run = switch(bits, length, suffix, width, controls)
    oracle = expected(bits, length, suffix, width, controls)
    out, counts, peak = replay(bits, (1 << suffix) * width, run.trace)
    require(out == oracle == run.output.cells, "wrong switch endpoint")
    fibers = 1 << (length - suffix - 1)
    size = (1 << suffix) * width
    volume = len(bits)
    switched = sum(controls)
    require(run.preparations == list(range(fibers)), "preparation order")
    require(counts == {"read": volume + size * switched,
                       "write": volume + 2 * size * switched,
                       "move": 4 * volume + 4 * size * switched}, "wrong invoice")
    require(peak == (size if switched else 0), "wrong scratch extent")
    require(sum(counts.values()) * 2 <= 19 * volume, "worst-case tariff")
    inverse = switch(out, length, suffix, width, controls)
    require(inverse.output.cells == bits, "inverse endpoint")
    transcript.update(json.dumps([length, suffix, width, controls, bits,
                                  out, dict(counts)], separators=(",", ":")).encode())
    return {"bits": volume, "actions": sum(counts.values()), "switched": switched}


def control_tables(fibers: int) -> list[list[int]]:
    require(1 <= fibers <= 1 << (MAX_L - 1), "control-table capacity")
    if fibers <= 8:
        return [list(x) for x in itertools.product((0, 1), repeat=fibers)]
    return [[0] * fibers, [1] * fibers, [j % 2 for j in range(fibers)],
            [int(j == fibers // 2) for j in range(fibers)]]


def payloads(volume: int) -> list[list[int]]:
    require(1 <= volume <= (1 << MAX_L) * MAX_R, "payload capacity")
    if volume <= 8:
        return [list(x) for x in itertools.product((0, 1), repeat=volume)]
    if volume <= 32:
        return [[0] * volume, [1] * volume] + [
            [int(i == j) for i in range(volume)] for j in range(volume)]
    return [[0] * volume, [1] * volume,
            [(j * j + j // 3 + 1) % 2 for j in range(volume)]]


def expect_rejection(action) -> None:
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control accepted")


def controls() -> int:
    good = ([0, 1, 1, 0], 2, 0, 1, [1, 0])
    bad = [([], 0, 0, 1, [0]), ([], MAX_L + 1, 0, 1, []),
           ([], 2, 2, 1, []), ([], 2, -1, 1, []),
           ([], 2, 0, 0, []), ([], 2, 0, MAX_R + 1, []),
           ([0], 2, 0, 1, [0, 0]), ([0, 1, 2, 0], 2, 0, 1, [0, 0]),
           ([0, 1, 1, 0], 2, 0, 1, [0]),
           ([0, 1, 1, 0], 2, 0, 1, [0, 2])]
    for args in bad:
        expect_rejection(lambda args=args: admit(*args))
    run = switch(*good)
    trace = run.trace
    erase = next(j for j, x in enumerate(trace) if x == ("scratch", "write", None))
    expect_rejection(lambda: replay(good[0], 1, trace[:erase] + trace[erase + 1:]))
    expect_rejection(lambda: replay(good[0], 1, trace[:-1]))
    expect_rejection(lambda: replay(good[0], 1, [("source", "write", 0)] + trace))
    read = next(j for j, x in enumerate(trace) if x[1] == "read")
    corrupt = list(trace)
    name, operation, value = corrupt[read]
    corrupt[read] = (name, operation, 1 - value)
    expect_rejection(lambda: replay(good[0], 1, corrupt))
    wrong = switch(good[0], 2, 0, 1, [0, 1]).output.cells
    require(wrong != expected(*good), "stale-control mutant not detected")
    return len(bad) + 5


def main() -> None:
    transcript = hashlib.sha256()
    totals: Counter = Counter()
    for length in range(1, 5):
        for suffix in range(length):
            for width in (1, 2, 3):
                for table in control_tables(1 << (length - suffix - 1)):
                    for bits in payloads((1 << length) * width):
                        result = check_case(bits, length, suffix, width, table, transcript)
                        totals.update(result)
                        totals["cases"] += 1
    for length, suffix, width in ((8, 6, 7), (12, 10, 16), (12, 0, 1)):
        for table in control_tables(1 << (length - suffix - 1)):
            bits = payloads((1 << length) * width)[-1]
            totals.update(check_case(bits, length, suffix, width, table, transcript))
            totals["cases"] += 1
    package = Path(__file__).resolve().parent
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(package.iterdir()) if p.is_file()}
    result = {"claim_type": "scoped sequential construction",
              "coverage": dict(totals), "negative_controls": controls(),
              "transcript_sha256": transcript.hexdigest(), "package_sha256": hashes}
    print("PASS_CRT_TAIL_SINGLE_BUFFER")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
