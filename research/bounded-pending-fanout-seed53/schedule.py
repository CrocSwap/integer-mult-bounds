"""Exact signed fanout schedules with a limit on unfinished outputs."""

import json


def schedule(k, capacity):
    if type(k) is not int or k < 0:
        raise ValueError("output count must be a nonnegative integer")
    if type(capacity) is not int or capacity < 1:
        raise ValueError("capacity must be a positive integer")
    word, commits = [], [-1] * k
    sign = 1
    for start in range(0, k, capacity):
        group = range(start, min(start + capacity, k))
        word.extend([[f"A{i}", -sign] for i in group])
        word.append(["B", sign])
        for i in group:
            word.append([f"A{i}", sign])
            commits[i] = len(word) - 1
        sign = -sign
    if sign == -1:
        word.append(["B", -1])
    return {"word": word, "commit_after": commits}


def inverse(word):
    return [item[:-1] + [-item[-1]] for item in reversed(word)]


def factor_word(factors, source, target, scratch):
    if len(factors) == 1:
        return [[factors[0], source, target, 1]]
    middle = len(factors) // 2
    connector, *rest = scratch
    right = factor_word(factors[:middle], source, connector, rest)
    left = factor_word(factors[middle:], connector, target, rest)
    return right + left + inverse(right) + inverse(left)


def lower(plan, factors, k):
    depth = max((len(v) - 1).bit_length() for v in factors.values())
    scratch = list(range(k + 2, k + 2 + depth))
    leaves, ends = [], []
    for name, sign in plan["word"]:
        source, target = (0, k + 1) if name == "B" else (k + 1, int(name[1:]) + 1)
        child = factor_word(factors[name], source, target, scratch)
        leaves.extend(child if sign == 1 else inverse(child))
        ends.append(len(leaves) - 1)
    return {**plan, "leaves": leaves,
            "leaf_commit_after": [ends[t] for t in plan["commit_after"]],
            "dirty_rows": 1 + depth}


def fixture():
    k, capacity = 5, 2
    lengths = {"B": 7, **{f"A{i}": i + 2 for i in range(k)}}
    factors = {name: [f"{name}f{j}" for j in range(n)] for name, n in lengths.items()}
    separate = {"word": [], "commit_after": []}
    for i in range(k):
        separate["word"].extend([[f"A{i}", -1], ["B", 1], [f"A{i}", 1], ["B", -1]])
        separate["commit_after"].append(4 * i + 2)
    plans = {"bounded": schedule(k, capacity),
             "unrestricted": schedule(k, (k + 1) // 2),
             "separate": separate}
    return {"format": "bounded-pending-fanout-v1", "seed": 53,
            "base": "ce7ad1b6ab09452c3478723a2e96ed5ff212dc08",
            "outputs": k, "capacity": capacity, "factors": factors,
            "plans": {name: lower(plan, factors, k) for name, plan in plans.items()},
            "scope": "Exact characteristic-zero queries; no new kappa or physical-memory claim."}


if __name__ == "__main__":
    print(json.dumps(fixture(), indent=2, sort_keys=True))
