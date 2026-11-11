"""Single retained chart lower-price screen for the fixed-volume BIT contract."""

import argparse
from fractions import Fraction
from functools import cache
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import time

PINS = {
    "deps/inputs/WORD.json.gz": "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78",
    "deps/inputs/INVOICE.json": "a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b",
    "deps/price.py": "6a33aac4c7032de9bb3881da248f5371b69c6b9af0893220825727f3d4878fae",
    "screen/pr7200_verify.py": "90f23e033bfced9673da33c07123eb749493164d5557f372a16b674e45461e1f",
    "screen/retag.py": "cf9b4fbe12225f3c258648d3e49660111976523babfa788dd09a267d9e7b904b",
    "screen/CERT.json": "36e221ac20102e40f0e419444d85b588278d3bdcd0e4c212bb2d907844811186",
}


def authenticated(roots):
    for key, digest in PINS.items():
        prefix, relative = key.split("/", 1)
        path = roots[prefix] / relative
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"changed input {key}")


def gf2_basis(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length()
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return basis


def contains(basis, row):
    while row:
        pivot = row.bit_length()
        if pivot not in basis:
            return False
        row ^= basis[pivot]
    return True


def interval_string(interval):
    return [str(n) for n in interval]


def save(out, filename, payload):
    path = out / filename
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def run(deps, out, start):
    screen = Path(__file__).resolve().parent
    authenticated({"deps": deps, "screen": screen})
    src = runpy.run_path(str(screen / "pr7200_verify.py"))
    rewrite = runpy.run_path(str(screen / "retag.py"))
    price = runpy.run_path(str(deps / "price.py"))
    word = json.loads(gzip.decompress((deps / "inputs" / "WORD.json.gz").read_bytes()))
    invoice = json.loads((deps / "inputs" / "INVOICE.json").read_bytes())
    frames, ranks, canonical = src["geometry"](word)
    changed, origin, adjusted, _ = rewrite["retag"](word, rewrite["modules"](word))
    old, _, _ = src["trace"](word, range(len(word["program"])), {}, frames, ranks, canonical)
    new, sites, available = src["trace"](changed, origin, adjusted, frames, ranks, canonical)
    assert old == {int(rank): n for rank, n in invoice["native_paid"].items()}
    assert len(sites) == len(adjusted) == 35
    delta = {r: new[r] - old[r] for r in new.keys() | old.keys() if new[r] != old[r]}
    assert delta == {1: -48, 2: 21, 3: -6, 4: 6, 6: -8, 7: 8}
    target = Fraction(price["TARGET"])
    h = {0: (Fraction(0), Fraction(0))}
    h.update({r: price["power_bounds"](r, target) for r in range(1, 9)})
    paid = {int(r): n for r, n in invoice["paid"].items()}
    targets = {int(r): n for r, n in invoice["targets"].items()}
    p_lo, p_hi = price["cost"](paid, target)
    t_lo, t_hi = price["cost"](targets, target)
    d_lo, d_hi = price["cost"](delta, target)
    shortfall = (p_lo - t_hi + 18*d_lo - 111, p_hi - t_lo + 18*d_hi - 111)
    assert shortfall[0] > 0
    initial = {
        "inputs": PINS, "target": str(target), "old_native": dict(old),
        "retag_delta": delta, "changed_calls": 18, "formal_H1_credit": 111,
        "raw_baseline_paid_minus_targets": interval_string((p_lo-t_hi, p_hi-t_lo)),
        "retag_cost_per_call": interval_string((d_lo, d_hi)),
        "saving_needed_whole": interval_string(shortfall),
        "saving_needed_per_changed_call": interval_string(tuple(x/18 for x in shortfall)),
        "zero_price_for_all_35_adjusted_moves_stock_upper_per_call":
            str(sum(h[ranks[site["target_chart"]]][1] for site in sites)),
        "scope": "one distinct positive retained canonical donor chart per delivery, fixed field volume",
    }
    save(out, "PRICE.json", initial)
    control = src["support_check"](sites, available, frames, ranks, canonical,
                                    json.loads((screen / "CERT.json").read_text()))
    assert control == {"empty": 79, "explicit": 512, "aggregate_cases": 382, "aggregate_recipients": 24}
    assert contains(gf2_basis([3, 6]), 5)
    assert not contains(gf2_basis([3, 6]), 4)
    # A simple nonnested pair. The rank of P-Q is 2 although their ranks coincide.
    x, y = (1, 0), (1, 1)
    assert 2*len(src["eliminate"]((x, y))) - 2 == 2
    # A charge that mistakenly uses the absolute rank difference admits this pair for free.
    assert abs(len((x,)) - len((y,))) == 0

    @cache
    def basis(chart, due):
        return gf2_basis(row for row, first in available[chart].items() if first <= due)

    @cache
    def distance(chart, other):
        union = src["eliminate"](frames[chart][0] + frames[other][0])
        return 2*len(union) - ranks[chart] - ranks[other]

    donors = sorted({chart for chart in canonical.values() if ranks[chart]})
    # Candidate stock is rounded upward per site. Costs of forming, routing and
    # cleaning donors are credited zero only in this optimistic upper bound.
    records = []
    for site in sites:
        if time.monotonic() - start >= 114:
            break
        target_chart, target_row, due = (site[k] for k in ("target_chart", "target_row", "due"))
        baseline_rank = ranks[target_chart]
        chart_count = support_count = nonnested_count = cheaper_count = 0
        cheaper = []
        for chart in donors:
            if chart == target_chart:
                continue
            chart_count += 1
            if not contains(basis(chart, due), target_row):
                continue
            support_count += 1
            low_rank = distance(chart, target_chart)
            nonnested_count += low_rank > abs(ranks[chart] - baseline_rank)
            if low_rank < baseline_rank:
                cheaper_count += 1
                cheaper.append((low_rank, chart))
        best = min(cheaper, default=None)
        optimistic = Fraction(0) if best is None else h[baseline_rank][1] - h[best[0]][0]
        records.append({
            "event": site["event"], "target_chart": target_chart, "due": due, "old_rank": baseline_rank,
            "chart_count": chart_count, "support_count": support_count, "nonnested_support": nonnested_count,
            "cheaper_count": cheaper_count, "cheaper": cheaper,
            "saving_upper": str(optimistic),
        })
    complete = len(records) == len(sites)
    upper = sum(Fraction(row["saving_upper"]) for row in records) + sum(
        h[ranks[site["target_chart"]]][1] for site in sites[len(records):]
    )
    receipt = {
        **initial, "predecessor_control": control, "positive_declared_charts": len(donors),
        "positive_observed_charts": sum(bool(available[chart]) for chart in donors),
        "scope_exhausted": complete, "unresolved_sites": len(sites) - len(records),
        "all_chart_pairs": sum(r["chart_count"] for r in records),
        "span_pairs": sum(r["support_count"] for r in records),
        "nonnested_span_pairs": sum(r["nonnested_support"] for r in records),
        "lower_price_pairs": sum(r["cheaper_count"] for r in records),
        "optimistic_saving_upper_per_call": str(upper),
        "optimistic_saving_upper_whole": str(18*upper),
        "shortfall_remaining_lower": str(shortfall[0] - 18*upper),
        "formation_routing_ownership_restoration": "granted free in upper, nonnegative when charged",
        "schedule": "grants independent donor availability through next target contact, no interference",
        "decision": "PIVOT" if 18*upper < shortfall[0] else "UNRESOLVED",
        "sites": records,
        "elapsed_seconds": time.monotonic() - start,
    }
    save(out, "STOCK.json", receipt)
    print(json.dumps({k: v for k, v in receipt.items() if k != "sites"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deps", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    run(args.deps.resolve(), args.out.resolve(), time.monotonic())
