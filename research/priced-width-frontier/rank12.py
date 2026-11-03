"""Price the positive-rank child calls at the exact rank-12 parent of PR #4507."""
from collections import Counter
from fractions import Fraction
from math import gcd, lcm
from runpy import run_path

from checks import require
from pricing import Menu, first_periodic_replication, frontier


def invoice(parent_replication, rows):
    leaves = dispatches = 0
    schedules = []
    for row in rows:
        units = parent_replication * row["jobs"]
        big, rem = divmod(units, row["nested_width"])
        narrow, rest = divmod(rem, row["small_width"])
        require(rest == 0, "source chronological remainder")
        copies = row["occurrences"]
        leaves += copies * (big*row["nested_leaves"] + narrow*row["small_leaves"])
        dispatches += copies * (big+narrow)
        schedules.append(dict(narrow=narrow, nested=big))
    return leaves, dispatches, schedules


def source_rows(package, retained):
    source = run_path(str(package / "source/4507-batches.py"))
    targets, paid = {2: 4, 3: 1}, {1: 6, 2: 2}
    compiled = source["compile_widths"](targets, paid, 12)
    flow = source["direct_flow"](targets, paid, 12)
    counts = Counter()
    for s, count in flow["sources"].items():
        if s < 12:  # The original rank-zero complement has zero cost.
            counts[12 - s, count] += 1
    for cut in flow["cuts"]:
        counts[cut["rank"], cut["count"]] += cut["copies"]
    baseline = retained["chronology_counterexample"]
    require(compiled["widths"] == baseline["widths_through_12"] and
            {str(k): v for k, v in flow["sources"].items()} == baseline["aggregate_sources"] and
            {str(k): v for k, v in flow["exits"].items()} == baseline["aggregate_exits"],
            "rank-12 frozen source ledger")
    rows = []
    for (rank, q), copies in sorted(counts.items()):
        small, large = compiled["widths"][rank], compiled["nested_widths"][rank]
        leaves, old = compiled["leaves"][rank], compiled["nested_leaves"][rank]
        require(large % small == 0 and old*small == leaves*large, "rank-12 child library identity")
        rows.append(dict(rank=rank, jobs=q, occurrences=copies, small_width=small,
                         nested_width=large, small_leaves=leaves, nested_leaves=old))
    return rows, sum(flow["sources"].values()), Fraction(compiled["leaves"][12], compiled["widths"][12])


def scaled_library(rows, scale, overheads=None):
    overheads = {} if overheads is None else overheads
    cuts = []
    for r in rows:
        ratio = r["nested_width"]//r["small_width"]
        copies = r["occurrences"]
        small, big = overheads.get(r["rank"], (1, 1))
        programs = {1: copies*(r["small_leaves"]+small), ratio: copies*(r["nested_leaves"]+big)}
        cuts.append((scale*r["jobs"]//r["small_width"], Menu(programs.items())))
    return cuts


def fee_boundary(rows, parent, scale):
    results = []
    for small, big in [(1, 1), (1, 3919), (1, 3920), (1, 3921), (Fraction(3,5), Fraction(1,3))]:
        cuts = scaled_library(rows, scale, {8: (small, big)})
        period, _, points = frontier(cuts, parent*scale)
        saving = max(Fraction(0), Fraction(8*(3920*small-big), parent*2744000))
        expected = [700, 2744000] if saving > 0 else [700]
        require([k*scale for k, _, _ in points] == expected and points[0][1]-points[-1][1] == saving,
                "rank-8 dispatch price boundary")
        require(period == (3920 if saving > 0 else 1), "rank-8 price-dependent period")
        results.append(dict(smaller_fee=str(small), nested_fee=str(big), coordinates=expected,
                            normalized_saving=str(saving)))
    return results


def check_rank12(package, retained):
    rows, parent, unpriced = source_rows(package, retained)
    scale = lcm(*(r["small_width"]//gcd(r["small_width"], r["jobs"]) for r in rows))
    require((scale, parent, unpriced) == (700, 158, Fraction(19448, 1975)), "rank-12 base")
    cuts = scaled_library(rows, scale)
    period, floor, points = frontier(cuts, scale*parent)
    observed = []
    snapshots = []
    for k in range(1, period+1):
        a = k*scale
        leaves, fees, counts = invoice(a, rows)
        require(Fraction(leaves,a*parent) == unpriced, "rank-12 normalized leaf count")
        price = Fraction(leaves+fees,a*parent)
        if k == 1 or k == period:
            snapshots.append(dict(a=a, leaves=leaves, child_dispatches=fees, cost=str(price), counts=counts))
        if not observed or price < observed[-1][1]:
            observed.append((a, price))
        expected = Fraction(349039,27650) if k < 3920 else Fraction(684112521,54194000)
        require(price == expected, "rank-12 dispatch plateau")
    require(observed == [(k*scale, price) for k, price, _ in points] and
            [a for a, _ in observed] == [700, 2744000], "rank-12 Pareto records")
    require(period == 3920 and floor == observed[-1][1] and first_periodic_replication(cuts) == 1,
            "rank-12 periodic tail")
    only = next(r for r in rows if r["rank"] == 8)
    require((only["jobs"], only["occurrences"], only["small_width"], only["nested_width"]) ==
            (1, 8, 700, 2744000), "rank-12 separate exits")
    return dict(parent_sources=parent, positive_cut_occurrences=sum(r["occurrences"] for r in rows),
                feasible_stride=scale, uniform_leaf_cost=str(unpriced), period=scale*period,
                first_periodic_replication=1, checked_feasible_replications=period,
                cost_difference=str(observed[0][1]-observed[-1][1]), rows=rows, frontier=snapshots,
                rank8_fee_boundary=fee_boundary(rows, parent, scale))
