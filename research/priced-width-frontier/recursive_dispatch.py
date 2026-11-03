"""Count a unit at every positive node of each unchanged compiled child tree."""
from collections import Counter
from fractions import Fraction
from runpy import run_path

from checks import require
from pricing import first_periodic_replication, frontier
from rank12 import invoice, scaled_library


def call_edges(source, widths):
    edges = [dict() for _ in widths]
    for rank in range(3, len(widths)):
        flow = source["direct_flow"]({2: 4, 3: 1}, {1: 6, 2: 2}, rank)
        parent_count = sum(flow["sources"].values())
        a, remainder = divmod(widths[rank], parent_count)
        require(remainder == 0, "source width divided by parent count")
        groups = [(rank-s, q, 1) for s, q in flow["sources"].items() if s < rank]
        groups += [(c["rank"], c["count"], c["copies"]) for c in flow["cuts"]]
        children = Counter()
        for child, q, copies in groups:
            count, rest = divmod(a*q, widths[child])
            require(rest == 0 and 0 < child < rank, "recursive cut must return whole children")
            children[child] += copies * count
        edges[rank] = dict(children)
    return edges


def tree_prices(edges, leaf_bills):
    fees = [0, 1, 1]
    leaves = [0, 1, 2]
    for children in edges[3:]:
        fees.append(1 + sum(count*fees[child] for child, count in children.items()))
        leaves.append(sum(count*leaves[child] for child, count in children.items()))
    require(leaves == leaf_bills, "recursive leaves disagree with retained compiler")
    return fees


def walk_root(edges, root):
    counts = [0] * (root+1)

    def visit(rank):
        counts[rank] += 1
        for child, copies in edges[rank].items():
            for _ in range(copies):
                visit(child)

    visit(root)
    return counts


def inventories(package):
    source = run_path(str(package / "source/4507-batches.py"))
    compiled = source["compile_widths"]({2: 4, 3: 1}, {1: 6, 2: 2}, 8)
    receipts = {}
    for name, width_field, leaf_field in (("smaller", "widths", "leaves"),
                                          ("nested", "nested_widths", "nested_leaves")):
        edges = call_edges(source, compiled[width_field])
        fees = tree_prices(edges, compiled[leaf_field])
        histogram = walk_root(edges, 8)
        require(sum(histogram) == fees[8] and histogram[1]+2*histogram[2] == compiled[leaf_field][8],
                "literal recursive node inventory")
        receipts[name] = dict(nodes_by_program_rank=fees, rank8_literal_histogram=histogram)
    return receipts


def check_recursive(package, top_level):
    receipts = inventories(package)
    small = receipts["smaller"]["nodes_by_program_rank"]
    big = receipts["nested"]["nodes_by_program_rank"]
    rows = top_level["rows"]
    charges = {r["rank"]: (small[r["rank"]], big[r["rank"]]) for r in rows}
    require(all(big[r["rank"]]*r["small_width"] <= small[r["rank"]]*r["nested_width"] for r in rows),
            "nested recursive density")
    scale, parent = top_level["feasible_stride"], top_level["parent_sources"]
    cuts = scaled_library(rows, scale, charges)
    period, floor, points = frontier(cuts, scale*parent)
    records = []
    for k in range(1, period+1):
        a = k*scale
        leaves, _, plans = invoice(a, rows)
        nodes = sum(r["occurrences"]*(plan["narrow"]*small[r["rank"]]+plan["nested"]*big[r["rank"]])
                    for r, plan in zip(rows, plans, strict=True))
        price = Fraction(leaves+nodes, parent*a)
        if not records or price < Fraction(records[-1]["cost"]):
            records.append(dict(a=a, leaves=leaves, positive_calls=nodes, cost=str(price)))
    require([(r["a"], Fraction(r["cost"])) for r in records] ==
            [(k*scale, price) for k, price, _ in points], "recursive dispatch records")
    require([r["a"] for r in records] == [700, 2744000] and
            floor == Fraction(179870533,10838800) and first_periodic_replication(cuts) == 1,
            "recursive price floor and onset")
    saving = Fraction(records[0]["cost"])-floor
    credit = 3920*small[8] - big[8]
    require((small[8],big[8],credit) == (3639,13928545,336335) and
            saving == Fraction(8*credit, parent*2744000), "rank-8 recursive saving")
    return dict(libraries=receipts, nested_rank8_nodes_saved=credit,
                normalized_saving=str(saving), period=period*scale, frontier=records)
