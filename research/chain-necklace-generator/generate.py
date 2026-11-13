"""Exact suffix-pruned chain necklaces; standard-library Python 3.12."""

import json
from itertools import product

MAX_MODULUS = 5


def domain(modulus: int, target: int) -> None:
    if type(modulus) is not int or not 1 <= modulus <= MAX_MODULUS:
        raise ValueError("modulus must be an integer in 1..5")
    if type(target) is not int or not 0 <= target < modulus:
        raise ValueError("target must be an integer in 0..modulus-1")


def step(counts: tuple[int, ...], residue: tuple[int, ...],
         symbol: int, modulus: int) -> tuple[int, int, int]:
    """Append 0, 1 or 2, corresponding to the chain's letters 1, 2, 3."""
    a, b, t = residue
    if symbol == 1:
        a += counts[0]
    elif symbol == 2:
        b += counts[1]
        t += residue[0]
    return a % modulus, b % modulus, t % modulus


def suffix_table(modulus: int) -> tuple[dict, dict]:
    domain(modulus, 0)
    table = {(0, 0, 0): {(0, 0, 0)}}
    work = {"table_transitions": 0, "table_cells": (modulus + 1) ** 3}
    for counts in product(range(modulus + 1), repeat=3):
        if counts == (0, 0, 0):
            continue
        residues = set()
        for symbol in range(3):
            if counts[symbol] == 0:
                continue
            previous = tuple(n - (j == symbol) for j, n in enumerate(counts))
            for residue in table[previous]:
                residues.add(step(previous, residue, symbol, modulus))
                work["table_transitions"] += 1
        table[counts] = residues
    work["table_states"] = sum(len(values) for values in table.values())
    return table, work


def can_finish(modulus: int, target: int, counts: tuple[int, ...],
               residue: tuple[int, ...], table: dict) -> bool:
    remaining = tuple(modulus - n for n in counts)
    a, b, t = residue
    need_a = (-a - counts[0] * remaining[1]) % modulus
    need_b = (-b - counts[1] * remaining[2]) % modulus
    need_t = (target - t - a * remaining[2] - counts[0] * need_b) % modulus
    return (need_a, need_b, need_t) in table[remaining]


def representatives(modulus: int, target: int) -> tuple[tuple, dict]:
    """Return each lexicographically least valid rotation exactly once."""
    domain(modulus, target)
    table, work = suffix_table(modulus)
    work.update(nodes=0, symbol_trials=0, prefix_transitions=0,
                suffix_lookups=0, suffix_rejections=0, terminal_tests=0,
                rotation_tests=0, outputs=0)
    length = 3 * modulus
    stack = [((0,), (1, 0, 0), (0, 0, 0), 1)]
    result = []
    node_bound = (3 ** (length + 1) - 1) // 2
    for _ in range(node_bound):
        if not stack:
            break
        word, counts, residue, period = stack.pop()
        work["nodes"] += 1
        if len(word) == length:
            work["terminal_tests"] += 1
            if length % period == 0:
                if residue != (0, 0, target):
                    raise RuntimeError("completion invariant failed")
                result.append(word)
            continue
        lower = word[len(word) - period]
        for symbol in range(2, lower - 1, -1):
            work["symbol_trials"] += 1
            if counts[symbol] == modulus:
                continue
            next_counts = tuple(n + (j == symbol) for j, n in enumerate(counts))
            next_residue = step(counts, residue, symbol, modulus)
            work["prefix_transitions"] += 1
            work["suffix_lookups"] += 1
            if not can_finish(modulus, target, next_counts, next_residue, table):
                work["suffix_rejections"] += 1
                continue
            next_period = period if symbol == lower else len(word) + 1
            stack.append((word + (symbol,), next_counts, next_residue, next_period))
    else:
        raise RuntimeError("finite tree bound exhausted")
    work["outputs"] = len(result)
    return tuple(result), work


if __name__ == "__main__":
    words, counts = representatives(5, 1)
    print(json.dumps({"modulus": 5, "target": 1, "work": counts,
                      "representatives": ["".join(str(x + 1) for x in w)
                                          for w in words]}, sort_keys=True))
