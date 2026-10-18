"""Separate excess-coordinate filter and small-first partition checker."""

from itertools import combinations, combinations_with_replacement

from binding import ROOT, authenticate, read_json, require

G = {0: 2, 1: 4, 2: 8, 3: 12, 4: 20, 5: 36}
DIST = {1: 53, 2: 78, 3: 92, 4: 100, 5: 106, 6: 109}


def accepted(sigmas):
    if sum(sigmas) >= 36:
        return False
    descending = tuple(sorted(sigmas, reverse=True))
    for dropped in range(6):
        rest = descending[dropped:]
        level = 6 - dropped
        capacity = sum(G[s] for s in rest)
        target = sum(32 if s == 5 else G[s] for s in rest)
        if level == 1 and capacity < 73 and target < 53:
            return False
        if level == 2 and capacity < 82 and target < 78:
            return False
        if level > 2 and capacity < DIST[level]:
            return False
    small = sigmas[: len(sigmas) - 6]
    if sum(G[s] for s in small) >= 53:
        return True
    weights = tuple(s + 2 for s in small)
    if sum(weights) <= 7:
        return False
    for mask in range(1 << len(weights)):
        left = sum(w for i, w in enumerate(weights) if mask & (1 << i))
        if left <= 6 and sum(weights) - left <= 6:
            return False
    return True


def contract_counts(weights):
    count = dict.fromkeys((3262, 3205, 3260, 3186, 3192, 3253), 0)
    minima = dict.fromkeys((3262, 3205, 3260), None)
    small_count = len(weights) - 7
    if small_count >= 0:
        for small in combinations(range(len(weights)), small_count):
            cut = sum(G[weights[i] - 2] for i in small)
            remaining = tuple(i for i in range(len(weights)) if i not in small)
            for ends in combinations(remaining, 3):
                bounds = tuple(weights[i] for i in ends)
                count[3262] += cut <= 29 and max(bounds) <= 6
                count[3260] += (
                    cut <= 37 and bounds[0] <= 5 and bounds[1] <= 5 and bounds[2] <= 6
                )
                for number, valid in (
                    (3262, max(bounds) <= 6),
                    (3260, bounds[0] <= 5 and bounds[1] <= 5 and bounds[2] <= 6),
                ):
                    if valid:
                        minima[number] = (
                            cut if minima[number] is None else min(minima[number], cut)
                        )
            for ends in combinations(remaining, 6):
                count[3205] += cut <= 30 and max(weights[i] for i in ends) <= 6
                if max(weights[i] for i in ends) <= 6:
                    minima[3205] = (
                        cut if minima[3205] is None else min(minima[3205], cut)
                    )
            if cut <= 5:
                count[3253] += sum(cut + G[weights[i] - 2] < 53 for i in remaining)
    for number, target in ((3186, (3, 4) + (6,) * 8), (3192, (5,) + (6,) * 8)):
        count[number] = int(
            len(weights) == len(target)
            and all(w <= t for w, t in zip(weights, target, strict=True))
        )
    return count, minima


def check_witness(weights, number, witness):
    small = witness["small_indices"]
    ends = witness["endpoint_indices"]
    deleted = witness["deleted_indices"]
    require(
        sorted(small + ends + deleted) == list(range(len(weights))), "role partition"
    )
    cut = sum(G[weights[i] - 2] for i in small)
    require(cut == witness["common_support_cap"], "cut cap")
    require(
        6 - len(deleted) == witness["retained_code_dimension"], "deletion codimension"
    )
    require([weights[i] for i in ends] == witness["endpoint_weight_caps"], "end ranks")
    if number == 3253:
        anchor = witness["anchor_index"]
        require(cut <= 5 and anchor in ends and len(ends) == 7, "common-five roles")
        require(cut + G[weights[anchor] - 2] < 53, "quotient basis distance")
        require(witness["independent_directions"] == 6, "six directions")
        require(witness["projective_direction_limit"] == 2, "two projective lines")
        require(
            witness["quotient_basis_support_cap"] == cut + G[weights[anchor] - 2],
            "quotient receipt",
        )
    else:
        maxcut, limits, dim = {
            3262: (29, (6,) * 3, 2),
            3205: (30, (6,) * 6, 5),
            3260: (37, (5, 5, 6), 2),
        }[number]
        require(cut <= maxcut and 6 - len(deleted) == dim, "shortening cut/dimension")
        require(
            len(ends) == len(limits)
            and all(weights[i] <= limit for i, limit in zip(ends, limits, strict=True)),
            "end contract",
        )


def main():
    authenticate()
    receipt = read_json(ROOT / "RESULT.json")
    survivors, domain_count = [], 0
    for length in range(6, 11):
        for sigmas in combinations_with_replacement(range(6), length):
            domain_count += 1
            if accepted(sigmas):
                survivors.append([s + 2 for s in sigmas])
    require(domain_count == 7546, "independent finite domain")
    require([r["weights"] for r in receipt["rows"]] == survivors, "independent filter")
    for row in receipt["rows"]:
        counts, minima = contract_counts(row["weights"])
        for name, attempt in row["attempts"].items():
            number = int(name[2:6])
            require(
                attempt.get("valid_partitions", int(attempt.get("applies", False)))
                == counts[number],
                "attempt coverage",
            )
            if number in minima:
                require(
                    attempt["minimum_admissible_cut"] == minima[number],
                    "failed cut boundary",
                )
        seen = set()
        for name, cert in row["certificates"].items():
            number = int(name[2:6])
            seen.add(number)
            if number in (3186, 3192):
                target = [3, 4] + [6] * 8 if number == 3186 else [5] + [6] * 8
                require(
                    cert
                    == {
                        "applies": True,
                        "target_weights": target,
                        "required_code_dimension": 6,
                    },
                    "literal contract",
                )
            else:
                require(cert["valid_partitions"] == counts[number], "partition count")
                check_witness(row["weights"], number, cert["witness"])
        require(
            seen == {n for n, count in counts.items() if count}, "coverage mismatch"
        )
    print(
        "PASS_INDEPENDENT_P112_B6_T4",
        domain_count,
        len(survivors),
        "all partitions and witnesses",
    )


if __name__ == "__main__":
    main()
