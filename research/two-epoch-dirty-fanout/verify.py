"""Exact two-epoch fanout certificate; standard-library, read-only replay."""

import hashlib
import heapq
import itertools
import json
from pathlib import Path


IDENTITY = (1, 2, 4)
GATES = tuple((i, j) for i in range(3) for j in range(3) if i != j)
PREPARE = ((2, 1), (1, 0), (2, 1))
RESTORE = ((1, 2), (2, 0), (1, 2))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(rows, gate):
    result = list(rows)
    result[gate[0]] ^= result[gate[1]]
    return tuple(result)


def product(left, right):
    result = []
    for row in left:
        value = 0
        for k in range(3):
            if row & (1 << k):
                value ^= right[k]
        result.append(value)
    return tuple(result)


def matrices():
    result = []
    for rows in itertools.product(range(1, 8), repeat=3):
        images = {product((mask,), rows)[0] for mask in range(8)}
        if len(images) == 8:
            result.append(rows)
    require(len(result) == 168, "GL(3,2) inventory")
    return tuple(result)


def prices(epoch, expensive):
    require(epoch in (0, 1), "unknown epoch")
    require(type(expensive) is int and 1 <= expensive <= 1000, "price domain")
    cheap = ((1, 0), (2, 1)) if epoch == 0 else ((2, 0), (1, 2))
    return {gate: 1 if gate in cheap else expensive for gate in GATES}


def distances(cost):
    distance = {IDENTITY: 0}
    witnesses = {IDENTITY: ()}
    pending = [(0, IDENTITY)]
    for _ in range(168 * 6 + 1):
        if not pending:
            break
        value, rows = heapq.heappop(pending)
        if value != distance[rows]:
            continue
        for gate in GATES:
            target = add(rows, gate)
            candidate = value + cost[gate]
            if candidate < distance.get(target, 10**9):
                distance[target] = candidate
                witnesses[target] = witnesses[rows] + (gate,)
                heapq.heappush(pending, (candidate, target))
    require(not pending and len(distance) == 168, "distance capacity")
    return distance, witnesses


def check_distances(distance, witnesses, cost):
    require(distance[IDENTITY] == 0, "distance origin")
    inequalities = 0
    for rows, value in distance.items():
        current = IDENTITY
        total = 0
        require(len(witnesses[rows]) <= 167, "witness length")
        for gate in witnesses[rows]:
            current = add(current, gate)
            total += cost[gate]
        require(current == rows and total == value, "distance witness")
        for gate in GATES:
            require(distance[add(rows, gate)] <= value + cost[gate], "Bellman")
            inequalities += 1
    return inequalities


def factor_certificate(expensive, group):
    before, paths_before = distances(prices(0, expensive))
    after, paths_after = distances(prices(1, expensive))
    bellman = check_distances(before, paths_before, prices(0, expensive))
    bellman += check_distances(after, paths_after, prices(1, expensive))
    candidates = []
    for rows in group:
        if tuple(row.bit_count() % 2 for row in rows) != (1, 0, 0):
            continue
        inverses = [other for other in group if product(other, rows) == IDENTITY]
        require(len(inverses) == 1, "unique inverse")
        candidates.append(before[rows] + after[inverses[0]])
    require(len(candidates) == 24, "legal cut maps")
    expected = 4 if expensive == 1 else 6
    require(min(candidates) == expected, "unrestricted ADD optimum")
    return {"price": expensive, "cut_maps": len(candidates),
            "ADD_optimum": expected, "Bellman_inequalities": bellman}


def forest_certificate(expensive):
    before, after = prices(0, expensive), prices(1, expensive)
    trees = []
    for parent1 in (0, 2):
        for parent2 in (0, 1):
            if (parent1, parent2) == (2, 1):
                continue
            edges = ((1, parent1), (2, parent2))
            bill = sum(before[edge] + after[edge] for edge in edges)
            require(bill == 2 * expensive + 2, "forest bill")
            trees.append(bill)
    require(len(trees) == 3, "rooted tree inventory")
    return min(trees)


def endpoint(prepare, restore, value_mask=8):
    rows = IDENTITY
    for gate in prepare:
        rows = add(rows, gate)
    rows = (rows[0] ^ value_mask, rows[1], rows[2])
    for gate in restore:
        rows = add(rows, gate)
    return rows


def endpoints_and_controls():
    target = (9, 10, 12)
    require(endpoint(PREPARE, RESTORE) == target, "symbolic endpoint")
    concrete = 0
    for width in range(1, 4):
        for values in itertools.product(range(1 << width), repeat=4):
            state = list(values[:3])
            for gate in PREPARE:
                state[gate[0]] ^= state[gate[1]]
            state[0] ^= values[3]
            for gate in RESTORE:
                state[gate[0]] ^= state[gate[1]]
            require(tuple(state) == tuple(x ^ values[3] for x in values[:3]),
                    "arbitrary dirty endpoint")
            concrete += 1
    controls = 0
    for index in range(6):
        pre = PREPARE[:index] + PREPARE[index + 1:] if index < 3 else PREPARE
        j = index - 3
        post = RESTORE[:j] + RESTORE[j + 1:] if index >= 3 else RESTORE
        require(endpoint(pre, post) != target, "deleted gate accepted")
        controls += 1
    require(endpoint(PREPARE, tuple(reversed(PREPARE))) == target,
            "literal inverse should preserve endpoint")
    require(sum(prices(1, 3)[g] for g in reversed(PREPARE)) == 9,
            "literal inverse wrongly priced at three")
    require(endpoint(PREPARE, RESTORE, 0) != target, "missing oracle")
    return concrete, controls + 2


def source_and_package_hashes():
    package = Path(__file__).resolve().parent
    source = json.loads((package / "SOURCES.json").read_text())
    root = package.parent.parent
    for entry in source["files"]:
        if entry.get("usage") == "input":
            digest = hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest()
            require(digest == entry["sha256"], "source hash " + entry["path"])
    files = sorted(path for path in package.iterdir() if path.is_file())
    require(len(files) <= 12, "package inventory bound")
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files}


def main():
    group = matrices()
    certificates = [factor_certificate(value, group) for value in (1, 2, 3, 6, 11)]
    forest = forest_certificate(3)
    concrete, controls = endpoints_and_controls()
    for bad_epoch, bad_price in ((-1, 3), (2, 3), (0, 0), (1, 1001), (0, True)):
        try:
            prices(bad_epoch, bad_price)
        except ValueError:
            controls += 1
        else:
            raise ValueError("invalid price accepted")
    print(json.dumps({"status": "PASS_TWO_EPOCH_DIRTY_FANOUT", "errors": 0,
                      "claim_type": "scoped written proof with exact finite corroboration",
                      "matrices": len(group), "certificates": certificates,
                      "M3_total_optimum": 7, "M3_forest_total": forest + 1,
                      "concrete_assignments": concrete, "controls": controls,
                      "package_sha256": source_and_package_hashes()}, sort_keys=True))


if __name__ == "__main__":
    main()
