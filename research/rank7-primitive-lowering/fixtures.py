# SPDX-License-Identifier: Apache-2.0
"""The three literal PR3042/3056/3060 blocks and their private-buffer inverses."""

import copy

from lower import certify, execute, require

FRAME = [256, 128, 64, 38, 20, 10, 1]
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
BLOCKS = {
    "parent": [
        ("add", 0, 1, -1, 1),
        ("add", 1, 0, 1, 1),
        ("add", 0, 1, -1, 1),
        ("add", 1, 0, 1, 1),
    ],
    "three_add": [("add", 1, 0, 1, 1), ("add", 0, 1, -1, 1), ("add", 1, 0, 2, 1)],
    "tariff": [
        ("add", 1, 0, -1, 1),
        ("add", 0, 1, 1, 1),
        ("scale", 0, -1, 1),
        ("scale", 1, -1, 1),
    ],
}


def inverse(block):
    result = []
    for gate in reversed(block):
        if gate[0] == "add":
            result.append((*gate[:3], -gate[3], gate[4]))
        else:
            result.append((*gate[:2], gate[3], gate[2]))
    return result


def address(block, registers, frame):
    result = []
    for gate in block:
        if gate[0] == "add":
            result.append(
                [gate[0], registers[gate[1]], registers[gate[2]], *gate[3:], frame]
            )
        else:
            result.append([gate[0], registers[gate[1]], *gate[2:], frame])
    return result


def produce(parent, variant):
    require(variant in BLOCKS, "named block variant")
    require(
        parent["restore"][175:179] == address(BLOCKS["parent"], (22, 230), FRAME),
        "literal restore preimage",
    )
    require(
        parent["cleanup"][33:37] == address(inverse(BLOCKS["parent"]), (22, 934), FULL),
        "literal cleanup preimage",
    )
    result = copy.deepcopy(parent)
    result["restore"][175:179] = address(BLOCKS[variant], (22, 230), FRAME)
    result["cleanup"][33:37] = address(inverse(BLOCKS[variant]), (22, 934), FULL)
    return result


def instructions(block, dual=False):
    result = []
    for gate in block:
        kind, target = gate[:2]
        if kind == "add":
            _, target, source, a, b = gate
            if dual:
                target, source, a = source, target, -a
        else:
            source, a, b = 1 - target, *gate[2:]
            if dual:
                a, b = b, a
        mapping = (target, source, 2)
        for operation in certify(kind, a, b):
            item = [operation[0], mapping[operation[1]]]
            if len(operation) > 2:
                item.append(mapping[operation[2]])
            if len(operation) > 3:
                item.append(operation[3])
            result.append(tuple(item))
    return result


def check_blocks():
    targets = {
        (False, False): ((0, -1), (1, -1), (0, 0)),
        (True, False): ((-1, 1), (-1, 0), (0, 0)),
        (False, True): ((-1, -1), (1, 0), (0, 0)),
        (True, True): ((0, 1), (-1, -1), (0, 0)),
    }
    rows = ((1, 0), (0, 1), (0, 0))
    counts = {}
    for name, block in BLOCKS.items():
        counts[name] = {}
        for backwards in (False, True):
            for dual in (False, True):
                recipe = instructions(inverse(block) if backwards else block, dual)
                require(
                    execute(recipe, rows) == targets[backwards, dual],
                    "dirty block/inverse/dual identity",
                )
                require(len(recipe) == 4, "four explicit unit instructions")
                counts[name][f"inverse={backwards},dual={dual}"] = len(recipe)
    return counts
