"""Exact corroboration of the new pivot policy. Nick Petalas, Apache-2.0."""

import hashlib
import itertools
import json
import platform
from pathlib import Path

from policy import bad_prefixes, pivot_plan, require


def projector(u, v, q):
    return [[(int(i == j) - x * y) % q for j, y in enumerate(v)]
            for i, x in enumerate(u)]


def clear_stage(a, k, i, j, q):
    """Independent literal two-sided elimination with equal head positions."""
    m = len(a)
    require(k <= i < m and k <= j < m, "residual pivot positions")
    b = [list(row) for row in a]
    b[k], b[i] = b[i], b[k]
    for row in b:
        row[k], row[j] = row[j], row[k]
    require(b[k][k] != 0, "nonzero pivot")
    inverse = pow(b[k][k], -1, q)
    for ii in range(k + 1, m):
        scale = b[ii][k] * inverse % q
        for jj in range(m):
            b[ii][jj] = (b[ii][jj] - scale * b[k][jj]) % q
    for jj in range(k + 1, m):
        scale = b[k][jj] * inverse % q
        for ii in range(m):
            b[ii][jj] = (b[ii][jj] - scale * b[ii][k]) % q
    return tuple(map(tuple, b))


def execute(a, plan, q):
    m, cost = len(a), 0
    require(len(plan) == m - 1, "complete corank-one plan")
    for k, (i, j) in enumerate(plan):
        a = clear_stage(a, k, i, j, q)
        cost += (i != k) + (j != k)
    require(a[-1][-1] == 0, "zero corank-one remainder")
    require(all(a[i][j] == 0 for i in range(m) for j in range(m) if i != j),
            "full diagonal endpoint")
    return cost


def reverse_tail_execute(a, plan, q):
    """Literal original P C convention, without calling clear_stage."""
    m = len(a)
    b = [list(reversed(row)) for row in a]
    cost = 0
    for k, (i, column) in enumerate(plan):
        last, j = m - 1 - k, m - 1 - column
        b[k], b[i] = b[i], b[k]
        for row in b:
            row[last], row[j] = row[j], row[last]
        require(b[k][last] != 0, "original-convention pivot")
        inverse = pow(b[k][last], -1, q)
        for ii in range(k + 1, m):
            scale = b[ii][last] * inverse % q
            b[ii] = [(x - scale * y) % q for x, y in zip(b[ii], b[k], strict=True)]
        for jj in range(last):
            scale = b[k][jj] * inverse % q
            for row in b:
                row[jj] = (row[jj] - scale * row[last]) % q
        cost += (i != k) + (j != last)
    require(b[-1][0] == 0, "original-convention zero remainder")
    require(all(b[i][j] == 0 for i in range(m) for j in range(m)
                if j != m - 1 - i), "original-convention endpoint")
    return cost


def normalized_pairs(m, q):
    """Every rank-one idempotent once, normalizing the first nonzero u entry."""
    for lead in range(m):
        for tail in itertools.product(range(q), repeat=m - 1 - lead):
            u = (0,) * lead + (1,) + tail
            for free in itertools.product(range(q), repeat=m - 1):
                v = list(free[:lead]) + [0] + list(free[lead:])
                v[lead] = (1 - sum(u[i] * v[i] for i in range(lead + 1, m))) % q
                yield u, tuple(v)


def census():
    rows = []
    for q, m in ((2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 5)):
        counts, cases = [0] * 4, 0
        for u, v in normalized_pairs(m, q):
            plan = pivot_plan(u, v, q)
            p = projector(u, v, q)
            cost = execute(p, plan, q)
            require(cost == reverse_tail_execute(p, plan, q), "convention agreement")
            require(0 <= cost <= 3, "policy upper bound")
            counts[cost] += 1
            cases += 1
        require(cases == q ** (m - 1) * (q**m - 1) // (q - 1), "complete pair count")
        rows.append({"q": q, "m": m, "policy_cost_histogram": counts, "cases": cases})
    return rows


def no_two_swap_plan(p, q):
    """Exhaust every legal pivot path within the two-swap budget, iteratively."""
    m = len(p)
    frontier = {(tuple(map(tuple, p)), 0)}
    visited = 0
    for k in range(m - 1):
        following = set()
        for a, cost in frontier:
            for i in range(k, m):
                for j in range(k, m):
                    total = cost + (i != k) + (j != k)
                    if total <= 2 and a[i][j]:
                        following.add((clear_stage(a, k, i, j, q), total))
        require(len(following) <= 100000, "finite search capacity")
        visited += len(following)
        frontier = following
    require(not frontier, "all two-swap plans excluded")
    return visited


def sharp_family():
    cases, visited = 0, 0
    for q in (2, 3, 5, 7):
        for m in range(4, 13):
            u = (1, 1, 1) + (0,) * (m - 3)
            v = (1, 1, q - 1) + (0,) * (m - 3)
            p = projector(u, v, q)
            require(execute(p, pivot_plan(u, v, q), q) == 3, "sharp witness policy")
            visited += no_two_swap_plan(p, q)
            cases += 1
    return {"witnesses": cases, "two_swap_search_states": visited}


def wide_cases():
    cases = 0
    for q in (2, 3, 5, 7, 11, 31):
        for m in (8, 17, 32, 64):
            for lead in (0, m // 2, m - 1):
                u = tuple(1 if i == lead else (i * i + 3) % q for i in range(m))
                v = [(i + 1) % q for i in range(m)]
                v[lead] = (1 - sum(u[i] * v[i] for i in range(m) if i != lead)) % q
                cost = execute(projector(u, v, q), pivot_plan(u, v, q), q)
                require(cost <= 3, "wide policy bound")
                cases += 1
    return cases


def controls():
    rejected = 0
    for u, v, q in (([1], [1], 3), ([1, 0], [1, 0], 4),
                    ([1, 0], [0, 1], 3), ([1, 0], [1, 3], 3),
                    ([True, 0], [1, 0], 3), ([1, 0], [1], 3)):
        try:
            pivot_plan(u, v, q)
        except ValueError:
            rejected += 1
    require(rejected == 6, "invalid domains reject")
    u, v, q = (1, 1, 1, 0), (1, 1, 2, 0), 3
    p, plan = projector(u, v, q), pivot_plan(u, v, q)
    for damaged in ([(0, 0)] * 3, [(3, 3), (1, 1), (2, 2)],
                    [(0, 3), (1, 1), (2, 2)]):
        try:
            execute(p, damaged, q)
        except ValueError:
            rejected += 1
    require(rejected == 9, "home-only, omitted bridge and inactive anchor reject")
    row_cost = sum(i != k for k, (i, _) in enumerate(plan))
    col_cost = sum(j != k for k, (_, j) in enumerate(plan))
    require(row_cost == 1, "row swaps must be charged")
    require(col_cost == 2, "column swaps must be charged")
    require(bad_prefixes([1, 1, 2, 0], 3) == [0, 2], "last bad prefix matters")
    return {"rejecting_controls": rejected, "semantic_controls": 3}


def receipt():
    result = {"status": "PASS_CORANK_ONE_PIVOT_POLICY", "claim_type": "scoped proof",
              "census": census(), "sharp_family": sharp_family(),
              "wide_cases": wide_cases(), "controls": controls(),
              "python": platform.python_version()}
    here = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "policy.py", "verify.py")
    result["sha256"] = {}
    for name in names:
        data = (here / name).read_bytes()
        require(len(data) <= 131072, "receipt file capacity")
        result["sha256"][name] = hashlib.sha256(data).hexdigest()
    return result


if __name__ == "__main__":
    print(json.dumps(receipt(), indent=2, sort_keys=True))
