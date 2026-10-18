"""Exact finite controls for the replica-prefix lemma; no supplier replay.

The positive model has two replicas, three register families (X, Y, H),
and two rational coordinates per replica/family.  A call shears Y by X in
one replica while borrowing arbitrary dirty H in the other replica.  After
restoring H, it applies a non-scalar rational orthogonal residual to H.
Each (replica, family) has its own two-coordinate l2 norm; the ambient
norm is the maximum over all six individual family norms.

Matrix equalities below hold for every input of this finite model.  The
additional norm examples and negative controls support the written lemma;
they neither establish its dimension-independent proof nor replay any
native supplier, the eight-replica source schedule, or the full algorithm.
Only the Python 3.10+ standard library is used.  Checks survive python -O.
License: Apache-2.0, following the repository license.  This contribution
was developed with substantial AI assistance from OpenAI Codex.
"""

from __future__ import annotations

from fractions import Fraction as Q
from itertools import combinations
import json


Matrix = tuple[tuple[Q, ...], ...]
Vector = tuple[Q, ...]
REPLICAS = 2
FAMILIES = ("X", "Y", "H")
WIDTH = 2
DIMENSION = REPLICAS * len(FAMILIES) * WIDTH
ROTATION: Matrix = ((Q(3, 5), Q(-4, 5)), (Q(4, 5), Q(3, 5)))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def identity(n: int) -> Matrix:
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def transpose(a: Matrix) -> Matrix:
    return tuple(zip(*a))


def multiply(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(sum((x * y for x, y in zip(row, col)), Q(0))
                       for col in transpose(b)) for row in a)


def apply(a: Matrix, v: Vector) -> Vector:
    return tuple(sum((x * y for x, y in zip(row, v)), Q(0)) for row in a)


def index(replica: int, family: str, coordinate: int) -> int:
    return (replica * len(FAMILIES) + FAMILIES.index(family)) * WIDTH + coordinate


def owner(row: int) -> int:
    return row // (len(FAMILIES) * WIDTH)


def add_family(a: Matrix, dst: tuple[int, str], src: tuple[int, str],
               scale: Q) -> Matrix:
    rows = list(a)
    for c in range(WIDTH):
        d, s = index(*dst, c), index(*src, c)
        rows[d] = tuple(x + scale * y for x, y in zip(a[d], a[s]))
    return tuple(rows)


def rotate_helper(a: Matrix, replica: int) -> Matrix:
    rows = list(a)
    old = tuple(a[index(replica, "H", c)] for c in range(WIDTH))
    new = multiply(ROTATION, old)
    for c in range(WIDTH):
        rows[index(replica, "H", c)] = new[c]
    return tuple(rows)


def borrow(a: Matrix, active: int, helper: int, source_scale: Q = Q(1),
           target_scale: Q = Q(1), *, restore: bool = True,
           compensate: bool = True) -> tuple[Matrix, ...]:
    """h+=s*x; y+=t*h; h-=s*x; y-=t*h; then h:=U*h.

    Return each stage, including the residual.  Omissions are exposed only
    for negative controls.  No assumption that initial h is zero is made.
    """
    require(active != helper, "positive model must borrow across replicas")
    x, y, h = (active, "X"), (active, "Y"), (helper, "H")
    stages = []
    a = add_family(a, h, x, source_scale)
    stages.append(a)
    a = add_family(a, y, h, target_scale)
    stages.append(a)
    if restore:
        a = add_family(a, h, x, -source_scale)
        stages.append(a)
    if compensate:
        a = add_family(a, y, h, -target_scale)
        stages.append(a)
    stages.append(rotate_helper(a, helper))
    return tuple(stages)


def endpoint(active: int, helper: int, scale: Q) -> Matrix:
    a = add_family(identity(DIMENSION), (active, "Y"), (active, "X"), scale)
    return rotate_helper(a, helper)


def replica_diagonal(a: Matrix) -> bool:
    return all(value == 0 or owner(i) == owner(j)
               for i, row in enumerate(a) for j, value in enumerate(row))


def family_norm_squared(v: Vector) -> dict[tuple[int, str], Q]:
    return {(r, f): sum((v[index(r, f, c)] ** 2 for c in range(WIDTH)), Q(0))
            for r in range(REPLICAS) for f in FAMILIES}


def max_family_norm_squared(v: Vector) -> Q:
    return max(family_norm_squared(v).values())


def vector(entries: dict[tuple[int, str, int], Q | int]) -> Vector:
    result = [Q(0)] * DIMENSION
    for coordinate, value in entries.items():
        result[index(*coordinate)] = Q(value)
    return tuple(result)


def signed_gadgets() -> dict[str, object]:
    require(multiply(transpose(ROTATION), ROTATION) == identity(2),
            "helper residual must be exactly orthogonal")
    require(ROTATION[0][1] != 0 and ROTATION[1][0] != 0,
            "helper residual must not be a scalar identity")
    cases = 0
    for active in range(REPLICAS):
        helper = 1 - active
        for s in (-1, 1):
            for t in (-1, 1):
                stages = borrow(identity(DIMENSION), active, helper, Q(s), Q(t))
                require(stages[-1] == endpoint(active, helper, Q(s * t)),
                        "signed gadget endpoint differs from local shear plus residual")
                require(replica_diagonal(stages[-1]),
                        "completed gadget leaks between replicas")
                require(not replica_diagonal(stages[0]),
                        "model did not exercise a cross-replica internal prefix")
                for c in range(WIDTH):
                    h = index(helper, "H", c)
                    require(stages[2][h] == identity(DIMENSION)[h],
                            "helper was not restored before compensation and residual")
                cases += 1
    return {"cases": cases, "both_replica_directions": True,
            "borrow_and_target_signs": [-1, 1],
            "residual": [[str(x) for x in row] for row in ROTATION],
            "endpoint_matrix_equalities": "all inputs in the 12-dimensional model"}


def interleavings() -> dict[str, object]:
    """All six shuffles of two calls in each of two replicas."""
    samples = list(identity(DIMENSION))
    samples += [tuple(Q(1) for _ in range(DIMENSION)),
                tuple(Q((-1) ** i) for i in range(DIMENSION)),
                tuple(Q(i - 5, 3) for i in range(DIMENSION)),
                vector({(0, "H", 0): 7, (0, "H", 1): -2,
                        (1, "H", 0): -3, (1, "H", 1): 5})]
    signs = ((1, 1), (-1, 1))
    final_matrices = set()
    schedules = []
    boundaries = 0
    norm_checks = 0
    for zero_positions in combinations(range(4), 2):
        schedule = tuple(0 if p in zero_positions else 1 for p in range(4))
        counts, coefficients = [0, 0], [0, 0]
        actual = expected = identity(DIMENSION)
        for active in schedule:
            helper = 1 - active
            sign = signs[active][counts[active]]
            actual = borrow(actual, active, helper, Q(sign))[-1]
            expected = multiply(endpoint(active, helper, Q(sign)), expected)
            counts[active] += 1
            coefficients[active] += sign
            require(actual == expected and replica_diagonal(actual),
                    "interleaved completed boundary is not replica diagonal")
            # Check the closed form independently of endpoint composition.
            for r in range(REPLICAS):
                for c in range(WIDTH):
                    y = index(r, "Y", c)
                    row = list(identity(DIMENSION)[y])
                    row[index(r, "X", c)] = Q(coefficients[r])
                    require(actual[y] == tuple(row), "wrong replica-local shear sum")
            for sample in samples:
                out = apply(actual, sample)
                initial_norms = family_norm_squared(sample)
                output_norms = family_norm_squared(out)
                for r in range(REPLICAS):
                    require(output_norms[r, "H"] == initial_norms[r, "H"],
                            "helper rotation changed its owner's individual family l2 norm")
                    require(output_norms[r, "X"] == initial_norms[r, "X"],
                            "replica source family changed")
                cap = Q(1 + max(counts))
                require(max_family_norm_squared(out) <= cap ** 2 * max(initial_norms.values()),
                        "finite completed-boundary max-depth majorant failed")
                norm_checks += 1
            boundaries += 1
        schedules.append(list(schedule))
        final_matrices.add(actual)
    require(len(final_matrices) == 1, "shuffle changed the completed endpoint")
    return {"schedules": schedules, "completed_boundaries": boundaries,
            "sample_vectors": len(samples), "exact_squared_norm_checks": norm_checks,
            "sample_majorant": "1 + maximum calls completed in any one replica",
            "distinct_final_matrices": len(final_matrices)}


def omission_controls() -> list[dict[str, object]]:
    clean = endpoint(0, 1, Q(1))
    unrestored = borrow(identity(DIMENSION), 0, 1, restore=False)[-1]
    require(unrestored != clean and not replica_diagonal(unrestored),
            "missing-restoration control was not rejected")
    witness = vector({(0, "X", 0): 1})
    output = apply(unrestored, witness)
    require(family_norm_squared(output)[1, "H"] == 1,
            "missing-restoration witness did not retain foreign source data")
    uncompensated = borrow(identity(DIMENSION), 0, 1, compensate=False)[-1]
    require(uncompensated != clean and not replica_diagonal(uncompensated),
            "missing-dirt-compensation control was not rejected")
    dirty = vector({(1, "H", 0): 1})
    require(apply(uncompensated, dirty)[index(0, "Y", 0)] == 1,
            "dirty helper witness did not contaminate target")
    return [{"name": "missing_restoration", "foreign_source_in_helper": True},
            {"name": "missing_dirt_compensation", "foreign_helper_in_target": True}]


def unbounded_prefix_control() -> dict[str, object]:
    # h+=N*x; y+=h/N; h-=N*x; y-=h/N has the SAME endpoint
    # for every nonzero N, but its first prefix sends (x,h)=(1,0)
    # to (1,N).  Restoration is therefore insufficient without a local cap.
    witness = vector({(0, "X", 0): 1})
    cases = []
    for n in (2, 17, 1_000_000):
        stages = borrow(identity(DIMENSION), 0, 1, Q(n), Q(1, n))
        require(stages[-1] == endpoint(0, 1, Q(1)),
                "scaled borrowing endpoint depends on internal amplification")
        prefix_squared = max_family_norm_squared(apply(stages[0], witness))
        endpoint_squared = max_family_norm_squared(apply(stages[-1], witness))
        require(prefix_squared == n * n and endpoint_squared == 1,
                "unbounded-prefix witness has incorrect exact norms")
        cases.append({"N": n, "first_prefix_norm_squared": n * n,
                      "endpoint_norm_squared": 1})
    return {"name": "restored_endpoint_unbounded_prefix", "cases": cases,
            "parameterized_identity": "endpoint independent of N; first-prefix norm = N",
            "required_hypothesis": "retain the local primitive-prefix cap"}


def rotate_coordinates(a: Matrix, first: int, second: int) -> Matrix:
    rows = list(a)
    rows[first], rows[second] = multiply(ROTATION, (a[first], a[second]))
    return tuple(rows)


def unitary_controls() -> list[dict[str, object]]:
    result = []
    # Choosing inputs (1,-1) turns the first row into 7/5.
    for second_replica, name in ((0, "unitary_mixes_families"),
                                 (1, "global_unitarity_is_not_max_family_contraction")):
        first = index(0, "X", 0)
        second = index(second_replica, "Y", 0)
        a = rotate_coordinates(identity(DIMENSION), first, second)
        v = vector({(0, "X", 0): 1, (second_replica, "Y", 0): -1})
        out = apply(a, v)
        require(multiply(transpose(a), a) == identity(DIMENSION),
                "unitarity negative control was not exactly unitary")
        require(sum(x * x for x in out) == sum(x * x for x in v) == 2,
                "global l2 norm was not preserved")
        require(max_family_norm_squared(v) == 1 and max_family_norm_squared(out) == Q(49, 25),
                "unitary mixing failed to amplify the max-family norm")
        require(replica_diagonal(a) == (second_replica == 0),
                "unitary control uses the wrong replica support")
        result.append({"name": name, "global_l2_squared_before_and_after": 2,
                       "max_family_squared_before": "1",
                       "max_family_squared_after": "49/25"})
    return result


def inter_replica_endpoint_control() -> dict[str, object]:
    # One scalar family per replica, two replicas.  Each event has max-family
    # operator norm 2 (the maximum absolute row sum).  With one event per replica,
    # an invalid replica-independent argument would give cap 2 overall.
    # The events actually mix replicas and compose to exceed that cap.
    first: Matrix = ((Q(1), Q(1)), (Q(0), Q(1)))
    second: Matrix = ((Q(1), Q(0)), (Q(1), Q(1)))
    for a in (first, second):
        require(max(sum(abs(x) for x in row) for row in a) == 2,
                "individual event max-family operator cap failed")
    total = multiply(second, first)
    out = apply(total, (Q(1), Q(1)))
    require(total == ((Q(1), Q(1)), (Q(1), Q(2))),
            "wrong mixing-endpoint composition")
    require(max(x * x for x in out) == 9 > 4,
            "inter-replica mixing did not refute the independent-depth cap")
    return {"name": "inter_replica_endpoint_mixing", "events_per_replica": 1,
            "individual_operator_norm_upper_bound": 2,
            "input_max_family_squared": 1, "output_max_family_squared": 9,
            "incorrect_independent_depth_upper_bound_squared": 4}


def run_checks() -> dict[str, object]:
    """Return a deterministic, JSON-serializable receipt or raise on failure."""
    signed = signed_gadgets()
    shuffled = interleavings()
    controls = omission_controls()
    controls.append(unbounded_prefix_control())
    controls.extend(unitary_controls())
    controls.append(inter_replica_endpoint_control())
    receipt: dict[str, object] = {
        "status": "PASS",
        "scope": "exact finite models; not a native supplier or eight-replica replay",
        "replicas": REPLICAS, "families": list(FAMILIES),
        "coordinates_per_replica_family": WIDTH,
        "norm": "maximum over (replica, family) of that family's two-coordinate l2 norm",
        "signed_dirty_helper_gadgets": signed,
        "interleavings": shuffled,
        "negative_controls": controls,
    }
    # Check this interface as well; callers can safely serialize the receipt.
    json.dumps(receipt, sort_keys=True)
    return receipt


if __name__ == "__main__":
    receipt = run_checks()
    print("replica-prefix model checks: PASS "
          f"({receipt['signed_dirty_helper_gadgets']['cases']} signed gadgets, "
          f"{receipt['interleavings']['completed_boundaries']} completed boundaries, "
          f"{len(receipt['negative_controls'])} negative controls)")
