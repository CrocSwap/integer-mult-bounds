#!/usr/bin/env python3
"""Exact distinguished-factor tariffs in ordered reserved-scratch echo trees."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

MAX_SPACE = 10


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(n: int, space: int, index: int) -> None:
    require(all(type(v) is int for v in (n, space, index)), "integer inputs required")
    require(0 <= space <= MAX_SPACE, "space outside bounded reference domain")
    require(1 <= n <= 1 << space, "infeasible factor count")
    require(0 <= index < n, "factor index outside word")


def minimum(n: int, space: int, index: int) -> tuple[int, int]:
    """Return the exact invocation minimum and its binary depth."""
    validate(n, space, index)
    for depth in range(space + 1):
        unit = 1 << (space - depth)
        left = (index + unit - 1) // unit
        right = (n - 1 - index + unit - 1) // unit
        if left + right <= (1 << depth) - 1:
            return 1 << depth, depth
    raise ValueError("feasible word had no admissible depth")


def construct(n: int, space: int, index: int) -> tuple[tuple[int, ...], ...]:
    """Return a postorder binary witness; nodes 0..n-1 are ordered leaves."""
    _, depth = minimum(n, space, index)
    unit = 1 << (space - depth)
    block = (index + unit - 1) // unit
    positions = list(range(index)) + [block * unit]
    positions += list(range((block + 1) * unit, (block + 1) * unit + n - 1 - index))
    require(len(set(positions)) == n and max(positions) < 1 << space, "bad slots")
    nodes: list[tuple[int, ...]] = [()] * n
    level = dict(zip(positions, range(n)))
    for _ in range(space):
        parents: dict[int, list[int]] = {}
        for address in sorted(level):
            parents.setdefault(address // 2, []).append(level[address])
        level = {}
        for address, children in parents.items():
            if len(children) == 1:
                level[address] = children[0]
            else:
                require(len(children) == 2, "nonbinary compressed trie")
                nodes.append(tuple(children))
                level[address] = len(nodes) - 1
    require(list(level.values()) == [len(nodes) - 1], "bad witness root")
    return tuple(nodes)


def inspect_tree(nodes: tuple[tuple[int, ...], ...]) -> tuple[int, tuple[int, ...]]:
    """Independently evaluate reserved space and all complete-call multipliers."""
    require(1 <= len(nodes) <= 2047, "tree capacity exceeded")
    spaces: list[int] = []
    parents = [0] * len(nodes)
    leaves = []
    for number, children in enumerate(nodes):
        require(isinstance(children, tuple), "children must be immutable")
        if not children:
            spaces.append(0)
            leaves.append(number)
            continue
        require(2 <= len(children) <= MAX_SPACE + 1, "invalid arity")
        require(len(set(children)) == len(children), "duplicate child")
        require(all(type(c) is int and 0 <= c < number for c in children), "bad edge")
        for child in children:
            parents[child] += 1
        spaces.append(len(children) - 1 + max(spaces[c] for c in children))
    require(parents == [1] * (len(nodes) - 1) + [0], "not one tree")
    counts = [0] * len(nodes)
    counts[-1] = 1
    order = []
    stack = [len(nodes) - 1]
    for _ in range(len(nodes)):
        require(bool(stack), "early traversal exhaustion")
        node = stack.pop()
        children = nodes[node]
        if not children:
            order.append(node)
        for j, child in enumerate(children):
            counts[child] = counts[node] * (2 if j in (0, len(children) - 1) else 4)
        stack.extend(reversed(children))
    require(not stack and order == leaves, "wrong ordered leaf sequence")
    return spaces[-1], tuple(counts[leaf] for leaf in leaves)


def all_arity_oracle(max_space: int) -> list[dict[tuple[int, int], int]]:
    """Minimize one leaf's count over all root arities and sibling sizes."""
    require(0 <= max_space <= 6, "oracle capacity exceeded")
    tables: list[dict[tuple[int, int], int]] = []
    for space in range(max_space + 1):
        table = {(0, 0): 1}
        for arity in range(2, space + 2):
            remaining = space - arity + 1
            capacity = 1 << remaining
            for slot in range(arity):
                multiplier = 2 if slot in (0, arity - 1) else 4
                for (a, b), price in tables[remaining].items():
                    for left in range(slot, slot * capacity + 1):
                        after = arity - 1 - slot
                        for right in range(after, after * capacity + 1):
                            key = (a + left, b + right)
                            candidate = multiplier * price
                            table[key] = min(table.get(key, (1 << space) + 1), candidate)
        require(len(table) == (1 << space) * ((1 << space) + 1) // 2, "oracle coverage")
        tables.append(table)
    return tables


def whole_trees(limit: int) -> list[list[tuple[int, tuple[int, ...]]]]:
    """Enumerate every ordered tree, retaining space and its entire count vector."""
    require(1 <= limit <= 8, "whole-tree capacity exceeded")
    families: list[list[tuple[int, tuple[int, ...]]]] = [[], [(0, (1,))]]
    for size in range(2, limit + 1):
        rows = []
        for arity in range(2, size + 1):
            # A partial ordered forest stores used leaves, peak child space and counts.
            forest = [(0, 0, ())]
            for slot in range(arity):
                next_forest = []
                for used, peak, counts in forest:
                    remaining = arity - slot - 1
                    for child_size in range(1, size - used - remaining + 1):
                        for child_space, child_counts in families[child_size]:
                            factor = 2 if slot in (0, arity - 1) else 4
                            new_counts = counts + tuple(factor * c for c in child_counts)
                            next_forest.append((used + child_size, max(peak, child_space), new_counts))
                forest = next_forest
            rows.extend((arity - 1 + peak, counts) for used, peak, counts in forest if used == size)
        families.append(rows)
    return families


def check_oracles() -> dict[str, int]:
    tables = all_arity_oracle(6)
    oracle_cases = 0
    for space, table in enumerate(tables):
        for (left, right), price in table.items():
            require(price == minimum(left + right + 1, space, left)[0], "oracle disagreement")
            oracle_cases += 1
    tree_count = comparisons = 0
    best: dict[tuple[int, int, int], int] = {}
    for size, family in enumerate(whole_trees(8)):
        for used, counts in family:
            tree_count += 1
            for space in range(used, 8):
                for index, price in enumerate(counts):
                    key = (size, space, index)
                    best[key] = min(best.get(key, price), price)
                    require(price >= minimum(size, space, index)[0], "whole-tree lower bound")
                    comparisons += 1
    for (size, space, index), price in best.items():
        require(price == minimum(size, space, index)[0], "whole-tree optimum")
    return {"all_arity_cases": oracle_cases, "whole_trees": tree_count,
            "whole_tree_factor_comparisons": comparisons, "whole_tree_optima": len(best)}


def check_witnesses() -> dict[str, int]:
    witnesses = leaves = 0
    for space in range(9):
        for size in range(1, (1 << space) + 1):
            for index in range(size):
                nodes = construct(size, space, index)
                used, counts = inspect_tree(nodes)
                require(used <= space and len(counts) == size, "witness contract")
                require(counts[index] == minimum(size, space, index)[0], "nonattaining witness")
                witnesses += 1
                leaves += size
    parity_cases = 0
    for space in range(2, 11):
        size = (1 << space) - 1
        for index in range(size):
            expected = (1 << space) if index % 2 else (1 << (space - 1))
            require(minimum(size, space, index)[0] == expected, "parity corollary")
            parity_cases += 1
    require([minimum(7, 3, i)[0] for i in range(7)] == [4, 8, 4, 8, 4, 8, 4], "fixture")
    return {"constructed_witnesses": witnesses, "witness_leaf_occurrences": leaves,
            "parity_cases": parity_cases}


def check_controls() -> dict[str, int]:
    bad = ((0, 0, 0), (2, 0, 0), (1, -1, 0), (1, 11, 0), (2, 1, -1),
           (2, 1, 2), (True, 1, 0), (1, 1.0, 0))
    rejected = 0
    for args in bad:
        try:
            minimum(*args)
        except ValueError:
            rejected += 1
    require(rejected == len(bad), "input control accepted")
    invalid_trees = ((), ((), (0,)), ((), (0, 0)), ((), (0, 2)), ((), (), (1, 0)))
    for nodes in invalid_trees:
        try:
            inspect_tree(nodes)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("malformed tree accepted")
    # Position-free capacity and one-floor rounding give false cheap odd positions.
    require(minimum(7, 3, 1)[0] > 4, "position-free false tariff survived")
    require(1 // 2 + 5 // 2 <= 3 and minimum(7, 3, 1)[0] == 8, "floor mutant survived")
    require(minimum(1, 0, 0) == (1, 0), "single-factor boundary")
    require(minimum(8, 3, 0)[0] == 8, "saturated-capacity boundary")
    return {"rejected_inputs_and_trees": rejected, "semantic_controls": 4}


def source_hashes() -> dict[str, str]:
    package = Path(__file__).resolve().parent
    source_manifest = json.loads((package / "SOURCES.json").read_text())
    sources = source_manifest["files"]
    require(len(sources) <= 8, "source capacity exceeded")
    files = [package / name for name in
             ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")]
    for row in sources:
        if row["usage"] == "input":
            path = package.parent.parent / row["path"]
            require(path.is_file() and not path.is_symlink(), "missing source proof")
            require(path.stat().st_size <= 262144, "source size exceeded")
            require(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], "source hash")
            files.append(path)
    require(len(files) == 7, "unexpected receipt inputs")
    hashes = {}
    for path in files:
        require(path.is_file() and not path.is_symlink(), "invalid receipt file")
        require(path.stat().st_size <= 262144, "receipt input too large")
        hashes[str(path.relative_to(package.parent.parent))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main() -> None:
    hashes = source_hashes()
    result = {"status": "PASS_DISTINGUISHED_ECHO_FACTOR", "no_new_kappa": True,
              **check_oracles(), **check_witnesses(), **check_controls(), "sha256": hashes}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
