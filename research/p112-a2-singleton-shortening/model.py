"""A2 singleton capacity and a literal TWOSIDE deletion application."""

import json
from collections import Counter
from hashlib import sha256
from itertools import combinations_with_replacement, product

from vendor.geometry import SIMPLE, dot, require

STAR = ((2, 2, 0, 0, 0, 0, 0, 0), (2, 0, 2, 0, 0, 0, 0, 0))
PROFILE = (2, 2, 2, 5, 6, 6, 6, 7, 7, 7, 7)
CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}


def binary_rank(rows):
    require(len(rows) <= 120 and all(0 <= r < 512 for r in rows), "binary rows")
    pivots = [0] * 9
    for row in rows:
        for _ in range(9):
            if not row:
                break
            pivot = row.bit_length() - 1
            if pivots[pivot]:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return sum(bool(p) for p in pivots)


def singleton_classes(roots):
    require(len(roots) == len(set(roots)) == 120, "complete root inventory")
    classes, doubles, spectrum = [0, 0, 0], 0, Counter()
    for index, root in enumerate(roots):
        values = [0] + [dot(root, vertex) for vertex in STAR]
        counts = Counter(values)
        cost = 3 - max(counts.values())
        spectrum[cost] += 1
        if cost == 1:
            singleton = next(value for value, count in counts.items() if count == 1)
            classes[values.index(singleton)] |= 1 << index
        elif cost == 2:
            doubles |= 1 << index
    require(dict(spectrum) == {0: 36, 1: 81, 2: 3}, "A2 spectrum")
    require([s.bit_count() for s in classes] == [27] * 3, "singleton sizes")
    return tuple(classes), doubles


def transport_receipt(roots, coordinates):
    """Check root-pair transitivity and its invertible binary label action."""
    labels = tuple(
        1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(c)) for c in coordinates
    )
    require(len(set(labels)) == 120, "full root-label injectivity")
    by_root = dict(zip(roots, labels, strict=True))
    signed = tuple(sorted({v for r in roots for v in (r, tuple(-x for x in r))}))
    indices = {r: i for i, r in enumerate(signed)}
    generators = []
    for i, normal in enumerate(SIMPLE):
        mask = sum(((dot(normal, s) // 4) % 2) << (j + 1) for j, s in enumerate(SIMPLE))
        action = []
        for root in signed:
            pairing = dot(root, normal)
            require(pairing % 4 == 0, "integral reflection")
            image = tuple(
                x - (pairing // 4) * y for x, y in zip(root, normal, strict=True)
            )
            require(image in indices, "reflection closure")
            before = by_root[max(root, tuple(-x for x in root))]
            after = before ^ ((((before & mask).bit_count()) % 2) << (i + 1))
            require(
                after == by_root[max(image, tuple(-x for x in image))],
                "reflection/label mismatch",
            )
            action.append(indices[image])
        images = [
            x ^ ((((x & mask).bit_count()) % 2) << (i + 1))
            for x in (1 << j for j in range(9))
        ]
        require(binary_rank(images) == 9, "singular binary reflection")
        generators.append(tuple(action))
    first = tuple(indices[r] for r in STAR)
    queue, seen = [first], {first}
    for index in range(13_440):
        if index >= len(queue):
            break
        a, b = queue[index]
        for action in generators:
            pair = (action[a], action[b])
            require(dot(signed[pair[0]], signed[pair[1]]) == 4, "not an A2 pair")
            if pair not in seen:
                seen.add(pair)
                queue.append(pair)
        require(len(queue) <= 13_440, "pair-orbit capacity")
    total = sum(dot(a, b) == 4 for a in signed for b in signed)
    require(len(queue) == total == 13_440, "incomplete A2 orbit")
    return labels, {
        "ordered_pairs": total,
        "generators": 8,
        "signed_label_checks": 1920,
        "binary_action_rank": 9,
    }


def singleton_hyperplane_receipt(labels, classes):
    """Each 27-label class spans seven dimensions; only 127 cuts are needed."""
    require(len(labels) == len(set(labels)) == 120, "full labels")
    require(
        len(classes) == 3 and all(s.bit_count() == 27 for s in classes),
        "singleton class inventory",
    )
    reports = []
    for singleton in classes:
        block = tuple(labels[j] for j in range(120) if (singleton >> j) & 1)
        require(binary_rank(block) == 7, "singleton span must have rank seven")
        restrictions = set()
        for functional in range(1, 512):
            pattern = sum(
                1 << j
                for j, label in enumerate(block)
                if (functional & label).bit_count() % 2
            )
            if pattern:
                restrictions.add(pattern)
        require(len(restrictions) == 127, "incomplete nonzero restriction inventory")
        hist = Counter(27 - p.bit_count() for p in restrictions)
        require(
            dict(hist) == {0: 1, 11: 27, 12: 36, 15: 36, 16: 27},
            "singleton hyperplane spectrum",
        )
        maximizing = sorted(
            tuple(label for j, label in enumerate(block) if not (p >> j) & 1)
            for p in restrictions
            if 27 - p.bit_count() == 16
        )
        require(len(set(maximizing)) == 27, "maximizing hyperplane inventory")
        reports.append(
            {
                "span_rank": 7,
                "nonzero_restrictions": 127,
                "maximum": max(hist),
                "histogram": dict(sorted(hist.items())),
                "maximizers": len(maximizing),
                "maximizer_sha256": sha256(json.dumps(maximizing).encode()).hexdigest(),
            }
        )
    return reports


def support_lower(common, singleton_cap=16, punctures=8):
    require(type(common) is int and 0 <= common <= 29, "common support range")
    require(type(singleton_cap) is int and 0 <= singleton_cap <= 27, "singleton cap")
    require(type(punctures) is int and 0 <= punctures <= 120, "puncture count")
    # At a singleton coordinate, total support >= 2 - singleton support.
    return 2 * (84 - punctures - common) - 3 * singleton_cap


def original_survivors():
    """Independent transcription of the historical (6,5) weight filters."""
    survivors = []
    distances = (0, 53, 78, 92, 100, 106, 109)
    for size in range(6, 12):
        for weights in combinations_with_replacement(range(2, 8), size):
            if sum(w - 2 for w in weights) >= 36:
                continue
            feasible = True
            for level in range(1, 7):
                prefix = weights[: size - 6 + level]
                global_cap = sum(CAP[w] for w in prefix)
                target = sum(32 if w == 7 else CAP[w] for w in prefix)
                if (
                    (level == 1 and target < 53 and global_cap < 73)
                    or (level == 2 and target < 78 and global_cap < 82)
                    or (level >= 3 and global_cap < distances[level])
                ):
                    feasible = False
                    break
            if not feasible:
                continue
            basis = weights[: size - 6]
            killed = False
            if sum(CAP[w] for w in basis) < 53:
                killed = sum(basis) <= 7 or any(
                    all(
                        sum(w for w, g in zip(basis, assignment, strict=True) if g == k)
                        <= 6
                        for k in (0, 1)
                    )
                    for assignment in product((0, 1), repeat=len(basis))
                )
            if not killed:
                survivors.append(weights)
    require(len(survivors) == 174 and PROFILE in survivors, "historical caller")
    return survivors


def application(required_dimension=6, deleted=4):
    require(type(deleted) is int and 0 <= deleted <= 4, "deletion count")
    require(
        type(required_dimension) is int and 0 <= required_dimension <= 8,
        "code dimension",
    )
    require(required_dimension - deleted >= 2, "two code dimensions must survive")
    retained = PROFILE[: len(PROFILE) - deleted]
    require(deleted == 4, "this application deletes four unrestricted pieces")
    common = sum(CAP[w] for w in retained[:-3])
    endpoint_caps = [CAP[w] for w in retained[-3:]]
    require(common + max(endpoint_caps) < 53, "quotient independence")
    require(common + sum(endpoint_caps[-2:]) < 70, "root-edge classification")
    lower = support_lower(common)
    require(lower > sum(endpoint_caps), "no strict contradiction")
    return {
        "profile": PROFILE,
        "deleted_pieces": deleted,
        "retained_weights": retained,
        "retained_code_dimension_lower": required_dimension - deleted,
        "common_support_cap": common,
        "basis_support_cap": common + max(endpoint_caps),
        "edge_support_cap": common + sum(endpoint_caps[-2:]),
        "endpoint_allowance": sum(endpoint_caps),
        "endpoint_lower": lower,
        "margin": lower - sum(endpoint_caps),
        "excess": sum(w - 2 for w in PROFILE),
    }
