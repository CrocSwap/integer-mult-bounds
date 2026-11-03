"""Exact finite certificate for nonlinear binary C5 partial recovery."""

import hashlib
import itertools
import json
from pathlib import Path


EXPECTED = (5, 10, 15, 20, 24, 28, 31, 32)
FULL = (1 << 32) - 1
PACKAGE = Path(__file__).resolve().parent
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
         "VERIFY.json", "verify.py", "independent.py")
FOUR_FIVES = ((0, 3, 12, 27, 29), (1, 2, 13, 26, 28),
              (4, 7, 8, 25, 31), (5, 6, 9, 24, 30))
WITNESSES = {
    5: ((7, 11, 22, 24), (0, 12, 15, 17, 23), (2, 4, 21, 25, 26),
        (5, 9, 10, 18, 20), (8, 14, 16, 19, 31)),
    6: ((2, 12, 17, 31), (3, 13, 18, 30), (1, 7, 22, 25, 26),
        (4, 8, 11, 19, 21), (5, 6, 10, 27, 29), (9, 15, 20, 23, 24)),
    7: ((1, 25, 30), (3, 13, 20, 26), (9, 14, 18, 21),
        (0, 12, 15, 17, 23), (2, 4, 19, 28, 31),
        (5, 6, 10, 27, 29), (7, 8, 11, 16, 22)),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def confuse(x, y):
    difference = x ^ y
    return any((difference >> i) & 1
               and not (difference >> ((i - 1) % 5)) & 1
               and not (difference >> ((i + 1) % 5)) & 1
               for i in range(5))


def enumerate_classes():
    levels = [[0]]
    for size in range(1, 7):
        current = []
        for members in itertools.combinations(range(32), size):
            if all(not confuse(x, y)
                   for x, y in itertools.combinations(members, 2)):
                current.append(sum(1 << x for x in members))
        levels.append(sorted(current))
    require(not levels[6], "a six-input correct message class exists")
    require(tuple(map(len, levels)) == (1, 32, 256, 640, 480, 32, 0),
            "complete class inventory differs")
    return levels


def five_packings(fives):
    stack = [(0, 0, ())]
    complete = []
    nodes = 0
    for _ in range(1 + sum(32 ** k for k in range(1, 6))):
        if not stack:
            break
        start, union, chosen = stack.pop()
        nodes += 1
        require(len(chosen) <= 4, "five disjoint five-input classes exist")
        if len(chosen) == 4:
            complete.append(union)
        for index in range(start, len(fives)):
            if not union & fives[index]:
                stack.append((index + 1, union | fives[index],
                              chosen + (index,)))
    require(not stack, "packing work bound exhausted")
    require(nodes == 3249 and len(complete) == 1600, "packing inventory")
    require(len(set(complete)) == 1600, "four-pack unions are not distinct")
    return sorted(complete), nodes


def exclude_seven(packings, fours):
    four_set = set(fours)
    checks = 0
    for union in packings:
        remaining = FULL ^ union
        candidates = [a for a in fours if a & remaining == a]
        for a, b in itertools.combinations(candidates, 2):
            checks += 1
            if not a & b:
                require((remaining ^ a ^ b) not in four_set,
                        "a complete seven-message protocol exists")
    require(checks == 25280, "complement pair inventory")
    return checks


def standard_classes():
    classes = [[] for _ in range(8)]
    for x in range(32):
        bits = tuple((x >> i) & 1 for i in range(5))
        label = (bits[0] ^ bits[1]) + 2 * (bits[2] ^ bits[3]) + 4 * bits[4]
        classes[label].append(x)
    return tuple(tuple(c) for c in classes)


def protocol(classes):
    require(1 <= len(classes) <= 8, "message alphabet size")
    encoder = [0] * 32
    tables = [[[None] * 4 for _ in range(5)] for _ in classes]
    seen = set()
    for label, members in enumerate(classes):
        require(1 <= len(members) <= 5, "message class size")
        for x in members:
            require(type(x) is int and 0 <= x < 32, "binary input")
            require(x not in seen, "message classes overlap")
            seen.add(x)
            encoder[x] = label
            for i in range(5):
                left = (x >> ((i - 1) % 5)) & 1
                right = (x >> ((i + 1) % 5)) & 1
                context = left + 2 * right
                old = tables[label][i][context]
                bit = (x >> i) & 1
                require(old is None or old == bit, "conflicting decoder output")
                tables[label][i][context] = bit
    for table in tables:
        for row in table:
            for context in range(4):
                if row[context] is None:
                    row[context] = 0
    return encoder, tables


def execute(encoder, tables):
    successful = []
    for x in range(32):
        label = encoder[x]
        answers = []
        for i in range(5):
            left = (x >> ((i - 1) % 5)) & 1
            right = (x >> ((i + 1) % 5)) & 1
            answers.append(tables[label][i][left + 2 * right])
        if answers == [(x >> i) & 1 for i in range(5)]:
            successful.append(x)
    return successful


def witnesses():
    plans = {m: FOUR_FIVES[:m] for m in range(1, 5)}
    plans.update(WITNESSES)
    plans[8] = standard_classes()
    for messages in range(1, 9):
        encoder, tables = protocol(plans[messages])
        successful = execute(encoder, tables)
        require(len(successful) == EXPECTED[messages - 1], "attaining protocol")
    return plans


def controls():
    bad = ((), ((0, 1),), ((0,), (0,)), ((32,),), ((True,),),
           (tuple(range(6)),), tuple((x,) for x in range(9)))
    for classes in bad:
        try:
            protocol(classes)
        except ValueError:
            continue
        raise ValueError("malformed or false witness accepted")
    encoder, tables = protocol(FOUR_FIVES)
    tables[0][0][0] ^= 1
    require(len(execute(encoder, tables)) < 20, "decoder mutation undetected")
    return len(bad) + 1


def source_hashes():
    root = PACKAGE.parents[1]
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    require(len(manifest["files"]) == 5, "source declaration count")
    result = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            data = (root / row["path"]).read_bytes()
            require(len(data) < 1 << 20, "source size")
            digest = hashlib.sha256(data).hexdigest()
            require(digest == row["sha256"], "changed cited input")
            result[row["path"]] = digest
    require(len(result) == 3, "live source count")
    return result


def main():
    sources = source_hashes()
    levels = enumerate_classes()
    packings, nodes = five_packings(levels[5])
    pairs = exclude_seven(packings, levels[4])
    plans = witnesses()
    control_count = controls()
    inventory = json.dumps(levels, separators=(",", ":")).encode()
    inventory_digest = hashlib.sha256(inventory).hexdigest()
    require(inventory_digest ==
            "a39ed8349b302d38efbdacb422c394044ec1c2042364c21f4d01ddda1a555c73",
            "complete class inventory digest")
    package_hashes = {}
    for name in FILES:
        data = (PACKAGE / name).read_bytes()
        require(len(data) < 1 << 20, "package file size")
        package_hashes[name] = hashlib.sha256(data).hexdigest()
    receipt = {
        "status": "PASS_NONLINEAR_CYCLE_SUCCESS",
        "claim_type": "finite certificate with a scoped combinatorial proof",
        "message_values": list(range(1, 9)), "success_counts": list(EXPECTED),
        "class_counts_by_size": list(map(len, levels)),
        "inventory_sha256": inventory_digest,
        "packing_nodes": nodes, "four_five_packings": len(packings),
        "complement_pair_checks": pairs, "controls": control_count,
        "attainers": {str(m): plans[m] for m in range(1, 9)},
        "package_sha256": package_hashes, "input_sha256": sources,
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
