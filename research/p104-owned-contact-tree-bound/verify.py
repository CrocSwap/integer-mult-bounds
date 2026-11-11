"""Verify the paid floor for independently relabeled owned contact charts."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as F
import gzip
from hashlib import sha1, sha256
from itertools import product
import json
from pathlib import Path
import runpy

PACKAGE = Path(__file__).resolve().parent
CALLER = "inputs/CALLER.json.gz"
INVOICE = "inputs/EARLY-RESULT.json.gz"
STOCK = "inputs/OWNED-STOCK.json.gz"


def authenticated(raw, pin, name):
    blob = f"blob {len(raw)}\0".encode() + raw
    if sha256(raw).hexdigest() != pin["sha256"] or sha1(blob).hexdigest() != pin["git_blob"]:
        raise ValueError(f"Changed source: {name}")
    return raw


def read_inputs(word_path):
    manifest = json.loads((PACKAGE / "PROVENANCE.json").read_bytes())
    pins = manifest["bundled"]
    assert set(pins) == {CALLER, INVOICE, STOCK}
    source = {
        name: json.loads(authenticated(gzip.decompress((PACKAGE / name).read_bytes()), pin, name))
        for name, pin in pins.items()
    }
    if word_path is not None:
        word = json.loads(gzip.decompress(
            authenticated(word_path.read_bytes(), manifest["word_reference"], "literal #7277 word")
        ))
        direct = runpy.run_path(str(PACKAGE / "reconstruct.py"))["reconstruct"]
        rebuilt = direct(word, source[CALLER], source[INVOICE]["invoice"])
        assert rebuilt == source[STOCK]
    return source[STOCK], source[INVOICE], pins


def minimize(row, cost, max_dim):
    dims = dict(row["contacts"])
    assert dims and len(dims) == len(row["contacts"])
    assert all(0 <= d <= max_dim for d in dims.values())
    links = {u: [] for u in dims}
    seen_edges = set()
    old = Counter()
    for u, v, mult in row["links"]:
        assert u < v and (u, v) not in seen_edges and mult > 0
        seen_edges.add((u, v))
        links[u].append((v, mult))
        links[v].append((u, mult))
        old[abs(dims[u] - dims[v])] += mult
    assert len(seen_edges) == len(dims) - 1
    boundary = defaultdict(list)
    for u, d in row["boundary"]:
        assert 0 <= d <= max_dim
        boundary[u].append(d)
        old[abs(dims[u] - d)] += 1
    labels = range(max_dim + 1)
    reached = set()

    def descend(u, parent):
        assert u not in reached
        reached.add(u)
        children = [(descend(v, u), mult) for v, mult in links[u] if v != parent]
        return [
            sum(cost[abs(d - b)] for b in boundary[u])
            + sum(min(sub[q] + mult * cost[abs(d - q)] for q in labels)
                  for sub, mult in children)
            for d in labels
        ]

    best = min(descend(min(dims), None))
    assert reached == set(dims)
    return best, old


def toy_control():
    cost = (0, 5, 8, 10)
    row = {"contacts": [[10, 0], [20, 1], [30, 2]],
           "links": [[10, 20, 2], [20, 30, 1]],
           "boundary": [[10, 0], [20, 2], [30, 3]]}
    exact = min(
        2 * cost[abs(a-b)] + cost[abs(b-c)] + cost[a] + cost[abs(b-2)] + cost[abs(c-3)]
        for a, b, c in product(range(4), repeat=3)
    )
    assert minimize(row, cost, 3)[0] == exact
    bad = {**row, "links": row["links"] + [[10, 30, 1]]}
    try:
        minimize(bad, cost, 3)
    except AssertionError:
        pass
    else:
        raise AssertionError("simple cycle accepted as a tree")


def run(word_path):
    toy_control()
    stock, receipt, pins = read_inputs(word_path)
    regions = stock["regions"]
    assert len(regions) == 138 and stock["copies"] == 17
    assert stock["native_paid_moves"] == 6280 and stock["native_contact_edges"] == 137891
    max_dim = stock["max_old_chart_dimension"]
    assert max_dim == 9
    k = F(receipt["price"]["independent_raw_bracket"][1])
    paid, target = (
        Counter({int(rank): count for rank, count in receipt["invoice"][key].items()})
        for key in ("P", "T")
    )
    assert sum(paid.values()) == 110536 and sum(target.values()) == 22461
    assert sum(rank * (target[rank] - paid[rank]) for rank in paid.keys() | target.keys()) == 1424
    pricing = runpy.run_path(str(PACKAGE / "pricing.py"))
    grid = pricing["GRID"]
    powers = {r: tuple(int(v * grid) for v in pricing["power"](r, k))
              for r in paid.keys() | target.keys() | set(range(1, max_dim + 1))}
    histogram = runpy.run_path(str(PACKAGE / "histogram.py"))
    assert histogram["GRID"] == grid
    for rank, interval in powers.items():
        histogram["verify_price"](rank, k, *interval)
    powers[0] = (0, 0)
    low = [powers[r][0] for r in range(max_dim + 1)]
    high = [powers[r][1] for r in range(max_dim + 1)]
    comparisons = 0

    contacts = set()
    results = {}
    for row in regions:
        group = tuple(clock for clock, _ in row["contacts"])
        assert not contacts.intersection(group)
        contacts.update(group)
        best, original = minimize(row, low, max_dim)
        old_upper = sum(n * powers[r][1] for r, n in original.items())
        assert best <= old_upper
        if any(r > 0 and n for r, n in original.items()):
            results[group] = F(old_upper - best, grid)
            links, boundary = defaultdict(dict), defaultdict(list)
            for u, v, mult in row["links"]:
                links[u][v] = links[v][u] = mult
            for u, d in row["boundary"]:
                boundary[u].append(d)
            floor, hist, checked, ambiguous = histogram["minimum"](
                group, links, boundary, low, high, max_dim + 1
            )
            assert floor == best and ambiguous == 0
            assert hist == tuple(original[r] for r in range(1, max_dim + 1))
            comparisons += checked
        else:
            assert best == 0
    assert len(results) == 20 and comparisons == 6100
    saving = stock["copies"] * sum(results.values())
    _, baseline = pricing["moment"](paid, target, k)
    assert baseline + saving < 0
    return {
        "status": "PASS_OWNED_CONTACT_TREE_FLOOR",
        "benchmark_head": "ed090b57ed88f8859e5ff4643645099e6ba856ea",
        "incumbent_crossing_upper": str(k),
        "all_regions": len(regions),
        "owned_contacts": len(contacts),
        "paid_regions": len(results),
        "unvisited_regions": 0,
        "dropped_simple_cycle_edges": 0,
        "physical_site_tests": 0,
        "whole_saving_upper": str(saving),
        "exact_paid_saving_upper": "0",
        "exact_whole_incumbent_margin_upper": str(baseline),
        "resolved_histogram_comparisons": comparisons,
        "original_margin_upper": str(baseline),
        "whole_incumbent_margin_upper": str(baseline + saving),
        "region_upper_by_contacts": [{"contacts": list(group), "per_copy_upper": str(bound)}
                                     for group, bound in sorted(results.items())],
        "source_sha256": {name: pin["sha256"] for name, pin in pins.items()},
        "controls": ["PASS_EXHAUSTIVE_PARALLEL_EDGE_TOY", "REJECT_SIMPLE_CYCLE"],
    }


if __name__ == "__main__":
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path,
                        help="Regenerate all contacts and the invoice from the exact public #7277 word")
    result = json.dumps(run(parser.parse_args().word), indent=2, sort_keys=True) + "\n"
    assert result == (PACKAGE / "AUDIT.json").read_text()
    print(result, end="")
