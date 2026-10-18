"""Check the analytic A5 frame bound without enumerating orthogonal frames."""

import argparse
import hashlib
import json
from collections import Counter
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parent.parent
ATTAINING_FRAME = (
    (0, 0, 0, 0, 0, 0, 2, -2),
    (0, 0, 0, 0, 2, 2, 0, 0),
    (0, 0, 2, 2, 0, 0, 0, 0),
    (1, 1, -1, 1, -1, 1, -1, -1),
    (1, 1, -1, 1, 1, -1, 1, 1),
    (1, 1, 1, -1, -1, 1, 1, 1),
    (1, 1, 1, -1, 1, -1, -1, -1),
    (2, -2, 0, 0, 0, 0, 0, 0),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(path.is_file() and not path.is_symlink(), f"missing/linked {path}")
    require(path.stat().st_size <= 2_000_000, f"oversized {path}")
    return json.loads(path.read_bytes())


def bind_sources():
    sources = read_json(PACKAGE / "SOURCES.json")
    inputs = [row for row in sources["files"] if row["usage"] == "input"]
    require(len(inputs) == 13, "inherited input inventory")
    require(len({row["path"] for row in inputs}) == 13, "duplicate input")
    for row in inputs:
        relative = Path(row["path"])
        require(
            not relative.is_absolute()
            and relative.parts[0] == "research"
            and all(part not in (".", "..") for part in relative.parts),
            "noncanonical input path",
        )
        path = REPO / relative
        require(path.is_file() and not path.is_symlink(), f"missing/linked {path}")
        require(path.stat().st_size <= 2_000_000, "oversized inherited input")
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], "input hash"
        )
    prior = read_json(REPO / "research/p112-six-vertex-budget/RESULT.json")
    require(prior["mixed"]["minimum_after_30_cuts"] == 121, "mixed premise")
    require(
        prior["root"]["spectrum"] == {"0": 4, "1": 36, "2": 60, "3": 20},
        "inherited A5 spectrum",
    )
    return prior


def inner(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def canonical(row):
    return max(tuple(row), tuple(-x for x in row))


def root_inventory():
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[i], row[j] = 2, sign
            roots.add(canonical(row))
    roots.update(
        canonical(row) for row in product((-1, 1), repeat=8) if row.count(-1) % 2 == 0
    )
    result = tuple(sorted(roots))
    require(
        len(result) == 120 and all(inner(r, r) == 8 for r in result), "root inventory"
    )
    return result


def evaluations(roots):
    """Evaluate normalized star roots e0+ej against normalized E8 roots."""
    values, costs, variances = [], [], []
    for root in roots:
        row = (0, *(root[0] + root[j] for j in range(1, 6)))
        require(all(x % 2 == 0 for x in row), "nonintegral root pairing")
        row = tuple(x // 2 for x in row)
        values.append(row)
        costs.append(6 - max(Counter(row).values()))
        variances.append(6 * sum(x * x for x in row) - sum(row) ** 2)
    require(Counter(costs) == {0: 4, 1: 36, 2: 60, 3: 20}, "A5 spectrum")
    require(
        Counter(zip(costs, variances, strict=True))
        == {
            (0, 0): 4,
            (1, 5): 36,
            (2, 8): 45,
            (2, 12): 15,
            (3, 9): 20,
        },
        "cost/variance spectrum",
    )
    return tuple(values), tuple(costs), tuple(variances)


def scalar_receipt():
    minimum_one, minimum_two, count = 1000, 1000, 0
    for values in combinations_with_replacement(range(-2, 3), 6):
        count += 1
        cost = 6 - max(Counter(values).values())
        variance6 = 6 * sum(x * x for x in values) - sum(values) ** 2
        pairs = sum((a - b) ** 2 for a, b in combinations(values, 2))
        require(variance6 == pairs, "variance/pair identity")
        if cost == 1:
            minimum_one = min(minimum_one, variance6)
        elif cost >= 2:
            minimum_two = min(minimum_two, variance6)
    require(
        (count, minimum_one, minimum_two) == (210, 5, 8),
        "integer variance lower bounds",
    )
    star = tuple(tuple(int(i in (0, j)) for i in range(8)) for j in range(1, 6))
    gram = tuple(tuple(inner(a, b) for b in star) for a in star)
    require(
        gram == tuple(tuple(1 + int(i == j) for j in range(5)) for i in range(5)),
        "A5 Gram matrix",
    )
    trace = sum(inner(row, row) for row in star)
    total = tuple(sum(row[i] for row in star) for i in range(8))
    require((trace, inner(total, total)) == (10, 30), "Parseval trace inputs")
    return {
        "integer_patterns": count,
        "minimum_variance6_at_cost_one": minimum_one,
        "minimum_variance6_at_cost_two_or_more": minimum_two,
        "star_gram": gram,
        "trace": trace,
        "sum_squared_norm": 30,
    }


def analytic_floor(frame_costs, cuts):
    require(len(frame_costs) == 8 and cuts in (29, 30, 31), "floor domain")
    require(all(type(x) is int and 0 <= x <= 3 for x in frame_costs), "frame costs")
    c = Counter(frame_costs)
    require(8 * c[0] + 3 * c[1] >= 4, "Parseval necessary condition")
    require(2 * c[0] + c[1] >= 2, "integer frame consequence")
    return 180 - 2 * cuts + 2 * c[0] + c[1]


def signature_receipt():
    accepted, total, minimum = 0, 0, 1000
    for signature in combinations_with_replacement(range(4), 8):
        total += 1
        c = Counter(signature)
        if 8 * c[0] + 3 * c[1] < 4:
            continue
        accepted += 1
        minimum = min(minimum, analytic_floor(signature, 30))
    require(total == 165 and minimum == 122, "symbolic frame bound")
    return {
        "signatures": total,
        "pass_variance_necessary_condition": accepted,
        "minimum_floor_at_30": minimum,
    }


def frame_identity(frame):
    require(len(frame) == 8 and all(len(row) == 8 for row in frame), "frame shape")
    require(all(inner(row, row) == 8 for row in frame), "frame normalization")
    require(
        all(inner(a, b) == 0 for a, b in combinations(frame, 2)),
        "frame is not orthogonal",
    )
    matrix = tuple(
        tuple(sum(row[i] * row[j] for row in frame) for j in range(8)) for i in range(8)
    )
    require(
        matrix == tuple(tuple(8 * int(i == j) for j in range(8)) for i in range(8)),
        "frame Parseval matrix",
    )
    return matrix


def witness_receipt(roots, costs, variances):
    matrix = frame_identity(ATTAINING_FRAME)
    require(all(row in roots for row in ATTAINING_FRAME), "frame outside E8")
    frame = tuple(roots.index(row) for row in ATTAINING_FRAME)
    require(sum(variances[i] for i in frame) == 60, "frame variance sum")
    signature = tuple(sorted(costs[i] for i in frame))
    require(signature == (0, 2, 2, 2, 3, 3, 3, 3), "attaining signature")
    order = sorted(
        (i for i in range(120) if i not in frame), key=lambda i: (-costs[i], i)
    )
    bounds = {cut: sum(costs[i] for i in order[cut:]) for cut in (29, 30, 31)}
    require(bounds == {29: 124, 30: 122, 31: 120}, "attaining cut costs")
    require(
        all(bounds[cut] == analytic_floor(signature, cut) for cut in bounds),
        "analytic witness costs",
    )
    return {
        "roots_doubled": ATTAINING_FRAME,
        "frame": frame,
        "frame_matrix": matrix,
        "frame_costs": signature,
        "cuts": order[:30],
        "cut_bounds": bounds,
        "variance6_sum": 60,
    }


def build():
    prior = bind_sources()
    roots = root_inventory()
    _, costs, variances = evaluations(roots)
    witness = witness_receipt(roots, costs, variances)
    raw_roots = json.dumps(roots, separators=(",", ":")).encode()
    result = {
        "root_set_sha256": hashlib.sha256(raw_roots).hexdigest(),
        "scalar": scalar_receipt(),
        "signatures": signature_receipt(),
        "witness": witness,
        "errors": 0,
        "root_floor_at_30": 122,
        "root_floor_at_31": 120,
        "inherited_mixed_floor_at_30": prior["mixed"]["minimum_after_30_cuts"],
        "endpoint_allowance": 120,
        "unstructured_38_cut_floor": sum(sorted(costs)[:82]),
        "frame_census_required_by_new_proof": False,
    }
    require(result["unstructured_38_cut_floor"] == 120, "losing old control")
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new external receipt")
    args = parser.parse_args()
    result = build()
    if args.output:
        require(not args.output.resolve().is_relative_to(REPO), "external output only")
        with args.output.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == read_json(PACKAGE / "RESULT.json"), "receipt differs")
    print(
        "PASS_P112_A5_PARSEVAL patterns=210 signatures=165 root=122 "
        "inherited_mixed=121 allowance=120 frame_census=unneeded errors=0"
    )


if __name__ == "__main__":
    main()
