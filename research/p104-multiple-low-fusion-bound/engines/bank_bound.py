"""Project the sealed geometry onto multiple low donors and reprice the stock."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
import argparse

PINS = {
    "r68_geometry": "ce9604444161b3532d02eb788cb3a24fbbdaf4c1354d596ac08a2c9edeb72c76",
    "r69_geometry": "a2dd10737f5bfbd3818e6766df3890e445fd46f661af9521f5d724b7c56c1d45",
    "r70_support": "34738b6d9031b3170a58f0cb590d81c01ea2c1038810008483d1c24dc7574150",
    "rank_stock": "4a7841699dd17688f6aada5c902a2a91e94558b2b1b4460c46b0e55aa95b3f9f",
    "tariff": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
TARGET = Q("0.0040075385047236")


def require(condition, text):
    if not condition:
        raise ValueError(text)


def checked(path, key):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == PINS[key], f"stale {key}")
    return raw


def rank_type(site):
    return "+".join(map(str, sorted(site["rank_pair"])))


def hkey(site):
    return (site["h"], *site["move_clocks"], site["clock"])


def histogram(obj):
    return Counter({int(r): count for r, count in obj.items()})


def main(args):
    first = loads(checked(args.r68_geometry, "r68_geometry"))
    second = loads(checked(args.r69_geometry, "r69_geometry"))
    prior = loads(checked(args.r70_support, "r70_support"))
    stock = loads(checked(args.rank_stock, "rank_stock"))
    checked(args.tariff, "tariff")
    cost = run_path(str(args.tariff))["cost"]
    require(first["comparator_head"] == second["comparator_head"] == prior["head"] == stock["head"] == HEAD,
            "comparison heads differ")
    require(second["already_checked"] == len(first["visited"]) == 64 and not second["unvisited"], "geometry coverage")
    require(second["continuation_keys"] == len(second["visited"]) == first["unresolved"] == 3358, "geometry counts")
    sites = first["survivors"] + second["survivors"]
    require(len(sites) == len({hkey(site) for site in sites}) == 456, "geometry survivor inventory")
    candidates = [s for s in sites if len(s["low"]) > 1]
    require(len(candidates) == 8 and all(len(s["high"]) == 1 for s in candidates), "exact multi-low inventory")
    ranks = Counter(map(rank_type, candidates))
    require(ranks == {"1+1": 6, "1+2": 2}, "expected rank types")
    rank_prices = stock["rank_prices"]
    delta = Counter()
    for kind, number in ranks.items():
        for rank, change in rank_prices[kind]["paid_delta"].items():
            delta[int(rank)] -= number * change
    paid = histogram(stock["old_complete_paid"])
    signed = histogram(stock["complete_targets"])
    signed.subtract(paid)
    signed_all = signed.copy()
    signed_all.update(delta)
    pre, post, target_credit = (cost(row, TARGET) for row in (signed, signed_all, delta))
    require(pre[1] < post[1] < 0 and target_credit[0] > 0, "target arithmetic")
    require(len({t for s in candidates for t in s["move_clocks"]}) == 16, "unexpected shared paid call")
    previous = Counter(tuple(row["key"][:4]) for row in prior["outcomes"]
                       if row["status"] == "dirty return readout failed" and row["key"][-1] is not None)
    rows = [{"key": s["key"], "h": s["h"], "chart_path": s["chart_path"], "cut": s["clock"],
             "low": s["low"], "high": s["high"], "rank_type": rank_type(s),
             "prior_readout_excluded": previous[hkey(s)] > 0} for s in candidates]
    require({row["h"] for row in rows if row["prior_readout_excluded"]} == {403, 422, 431},
            "previously proved readout exclusions")
    max_credit = max(Q(rank_prices[kind]["credit"][1]) for kind in ranks)
    all_credit = sum(count * Q(rank_prices[kind]["credit"][1]) for kind, count in ranks.items())
    result = {
        "head": HEAD, "inputs": PINS, "geometry_pairs": 3422, "geometry_survivors": len(sites),
        "multi_low_banks": len(candidates), "one_edit_cap": 1, "distinct_paid_calls": 16,
        "bank_shapes": dict(Counter(f'{len(s["low"])}+{len(s["high"])}' for s in candidates)),
        "rank_types": dict(ranks), "rows": rows,
        "full_family_global_gross_upper": stock["one_edit_optimistic_upper"],
        "one_edit_comparator_gross_upper": str(max_credit),
        "all_eight_comparator_gross_upper": str(all_credit),
        "target": str(TARGET), "target_old_margin": list(map(str, pre)),
        "target_all_eight_gross_credit": list(map(str, target_credit)),
        "target_all_eight_margin": list(map(str, post)),
        "scope": "Bound from sealed receipts, no literal word decoding. All eight simultaneously grants every shared geometry and all scalar/physical costs free.",
    }
    print(dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for key in PINS:
        p.add_argument("--" + key.replace("_", "-"), type=Path, required=True)
    main(p.parse_args())
