"""Resume R68's exact geometry on its sealed unvisited list only."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys
import time

ENGINE_SHA = "478e269bdd6d14d9d3eafe4575b2ee3bbe383ab96efa72aee02e97a5a4bfb0d3"
PRIOR_SHA = "ce9604444161b3532d02eb788cb3a24fbbdaf4c1354d596ac08a2c9edeb72c76"
SELECTION_SHA = "bc14204ea6245da881a117492b77e3ee576022e5b9bda96c077a2b32a9b280a0"
ADMISSION_SHA = "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13"
CASE_CAP = 3358
TIME_CAP = 35


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(raw):
    return sha256(raw).hexdigest()


def read_pinned(path, expected):
    data = path.read_bytes()
    require(digest(data) == expected, "SHA-256 mismatch: " + path.name)
    return data


def selection(prior, expected):
    rows = prior["unvisited"]
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    require(digest(raw) == expected == SELECTION_SHA, "ordered continuation selection mismatch")
    keys = [row["key"] for row in rows]
    checked = {row["key"] for row in prior["visited"]}
    require(len(keys) == len(set(keys)) == CASE_CAP and len(checked) == 64, "wrong continuation count")
    require(checked.isdisjoint(keys), "continued geometry would repeat a prior key")
    return rows


def rank_type(row):
    low, high = sorted(row[-2:])
    return f"{low}+{high}"


def item_key(row):
    return ":".join(map(str, row[:3]))


def read_selection(args):
    prior = json.loads(read_pinned(args.selection, PRIOR_SHA))
    return prior, selection(prior, args.selection_sha)


def run(args):
    prior, rows = read_selection(args)
    here = Path(__file__).resolve().parent
    read_pinned(here / "geometry.py", ENGINE_SHA)
    sys.path.insert(0, str(here))
    from geometry import Geometry, HEAD, NEW_WORD, PROTECTED, RANK_PRICE

    admission = read_pinned(args.admission, ADMISSION_SHA)
    require(HEAD.encode() in admission, "wrong #7334 admission")
    require((prior["comparator_head"], prior["word_sha256"], prior["price_sha256"], prior["admission_sha256"]) ==
            (HEAD, NEW_WORD, RANK_PRICE, ADMISSION_SHA), "R68 witness provenance mismatch")
    price = json.loads(read_pinned(args.price, RANK_PRICE))
    prices = price["rank_prices"]
    packed = read_pinned(args.word, NEW_WORD)
    start = time.monotonic()
    engine = Geometry(json.loads(gzip.decompress(packed)), PROTECTED)
    public_moves = sum(len(clocks) for role, clocks in engine.moves.items() if role < engine.n)
    require(public_moves == price["public_paid_moves"] == prior["public_moves"] == 6232, "wrong public MOVE stock")
    stock = engine.stock()
    stock.sort(key=lambda row: (-Fraction(prices[rank_type(row)]["credit"][1]), row[:3]))
    eligible = [{"key": item_key(row), "rank_type": rank_type(row)} for row in stock]
    checked = [{key: row[key] for key in ("key", "rank_type")} for row in prior["visited"]]
    pending = [{key: row[key] for key in ("key", "rank_type")} for row in rows]
    require(eligible == checked + pending, "fresh inventory disagrees with sealed exact selection")
    by_key = dict(zip((item["key"] for item in eligible), stock))
    require(len(by_key) == len(eligible), "duplicate fresh geometry key")
    visited, survivors = [], []
    for row in rows:
        if len(visited) >= CASE_CAP or time.monotonic() - start >= TIME_CAP:
            break
        price_row = prices[row["rank_type"]]
        require(row["credit_upper"] == price_row["credit"][1], "sealed per-site price disagrees")
        require(Fraction(price_row["complete_margin"][0]) > 0, "nonpositive optimistic one-edit directed price")
        reason, result = engine.geometry(by_key[row["key"]])
        visited.append({**row, "reason": reason})
        if result is not None:
            survivors.append({**result, "rank_type": row["rank_type"], "credit_upper": row["credit_upper"]})
    remaining = rows[len(visited):]
    return {
        "status": "EXHAUSTED" if not remaining else "CAPPED",
        "comparator_head": HEAD, "word_sha256": NEW_WORD, "price_sha256": RANK_PRICE,
        "admission_sha256": ADMISSION_SHA, "geometry_engine_sha256": ENGINE_SHA,
        "r68_receipt_sha256": PRIOR_SHA, "selection_sha256": SELECTION_SHA, "public_moves": public_moves,
        "eligible_paid_pairs_before_geometry": len(stock), "already_checked": len(checked),
        "continuation_keys": len(rows), "case_cap": CASE_CAP, "runner_cap_seconds": TIME_CAP,
        "inventory_by_rank_type": dict(Counter(row["rank_type"] for row in rows)),
        "conditional_price_by_rank_type": {kind: prices[kind] for kind in sorted({r["rank_type"] for r in rows})},
        "visited": visited, "unvisited": remaining, "unresolved": len(remaining),
        "disposition": dict(Counter(row["reason"] for row in visited)), "survivors": survivors,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--selection", type=Path, required=True)
    p.add_argument("--selection-sha", required=True)
    p.add_argument("--selection-only", action="store_true")
    p.add_argument("--word", type=Path)
    p.add_argument("--price", type=Path)
    p.add_argument("--admission", type=Path)
    args = p.parse_args()
    if args.selection_only:
        _, rows = read_selection(args)
        result = {"status": "PASS_SELECTION_ONLY", "selection_sha256": SELECTION_SHA, "keys": len(rows)}
    else:
        require(args.word and args.price and args.admission, "candidate mode needs three dependency paths")
        result = run(args)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
