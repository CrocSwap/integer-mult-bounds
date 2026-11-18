"""Interpret the finite graph with separate sparse storage and dispatch.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The graph and fixture ABI are shared; the source CPU is not called here.
"""


def run(code, tapes, limit):
    if len(tapes) != 14 or len({id(t) for t in tapes}) != 14:
        raise ValueError("distinct tape owners")
    origins = [t.origin for t in tapes]
    heads = origins[:]
    low, high = heads[:], heads[:]
    widths = [len(t.cells) for t in tapes]
    cells = {(i, j): v for i, tape in enumerate(tapes)
             for j, v in enumerate(tape.cells) if v != 2}
    writes = [0] * 14
    pc = 0
    for steps in range(1, limit + 1):
        instruction = code[pc]
        kind = instruction[0]
        if kind == 'H':
            return {"outcome": instruction[1], "steps": steps, "heads": heads,
                    "low": low, "high": high, "writes": writes,
                    "cells": [[cells.get((i, j), 2) for j in range(widths[i])]
                              for i in range(14)]}
        if kind == 'J':
            pc = instruction[1]
            continue
        tape = instruction[1]
        position = heads[tape]
        if kind == 'R':
            symbol = cells.get((tape, position), 2)
            pc = instruction[2][symbol]
        elif kind == 'W':
            writes[tape] += 1
            if instruction[2] == 2:
                cells.pop((tape, position), None)
            else:
                cells[tape, position] = instruction[2]
            pc += 1
        elif kind == 'M':
            heads[tape] += instruction[2]
            position = heads[tape]
            if not 0 <= position < widths[tape]:
                raise ValueError("sparse head outside supplied window")
            pc += 1
        else:
            raise ValueError("nonliteral instruction")
        low[tape] = min(low[tape], position)
        high[tape] = max(high[tape], position)
    raise TimeoutError("sparse interpreter limit")


def check_return(result, tapes, before, expected):
    if result['heads'] != [t.origin for t in tapes]:
        raise ValueError("sparse head return")
    for i in range(14):
        wanted = before[i][:]
        if i == 5 and result['outcome'] == 'DONE':
            wanted[tapes[i].origin] = expected
        if result['cells'][i] != wanted:
            raise ValueError("sparse owner state")
    if any(result['writes'][:5]):
        raise ValueError("sparse borrowed write")
    if result['writes'][5] != int(result['outcome'] == 'DONE'):
        raise ValueError("sparse output lifetime")
    if any(lo < tape.origin - 1 for lo, tape in zip(result['low'], tapes)):
        raise ValueError("sparse opaque exterior access")
