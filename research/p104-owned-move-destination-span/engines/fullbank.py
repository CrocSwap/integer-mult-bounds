"""Exact same-clock destination span with constructive or separating witnesses."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
import signal
from time import monotonic

PINS = {
    "round30/complex/source/inputs/WORD.json.gz": "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756",
    "round41/independent/RESULT.json": "1b993aa8c66ffce5d2d9f13cafae320c62230722d599d251fa61afc6534b1bc7",
    "round41/independent/replay_core.py": "fd7a1a7f9cb8f71caa5e0d89ed16ea056503fa283bc05f655eb0da7e8d5fc6e0",
    "round41/lead/r41-price-support/PRICE.json": "1efe8b52e02a8db0ac6a04cdf6b943e515badee5fc0b7bea6ea3fe4a30fd1d01",
}


def unique(items):
    out = dict(items)
    if len(items) != len(out):
        raise ValueError("duplicate JSON key")
    return out


def record(out, name, content):
    tmp = out / (name + ".partial")
    tmp.write_text(json.dumps(content, indent=2, sort_keys=True) + "\n")
    tmp.replace(out / name)


def axpy(dst, src, scale):
    for key, value in src.items():
        updated = dst.get(key, 0) + scale * value
        if updated:
            dst[key] = updated
        else:
            dst.pop(key, None)


def dot(left, right):
    return sum(v * right.get(k, 0) for k, v in left.items())


def solve(target, donors):
    basis = {}
    for role, donor in donors.items():
        row, combination = dict(donor), {role: Fraction(1)}
        for pivot, (old, coefficients) in sorted(basis.items()):
            if pivot in row:
                scale = -row[pivot]
                axpy(row, old, scale)
                axpy(combination, coefficients, scale)
        if row:
            pivot = min(row)
            factor = row[pivot]
            basis[pivot] = ({k: v / factor for k, v in row.items()},
                            {k: v / factor for k, v in combination.items()})

    residual, combination = dict(target), {}
    for pivot, (row, coefficients) in sorted(basis.items()):
        if pivot in residual:
            scale = residual[pivot]
            axpy(residual, row, -scale)
            axpy(combination, coefficients, scale)
    if not residual:
        recovered = {}
        for role, scale in combination.items():
            axpy(recovered, donors[role], scale)
        assert recovered == target
        return len(basis), "combination", combination

    free = min(residual)
    dual = {free: Fraction(1)}
    assert free not in basis
    for pivot, (row, _) in sorted(basis.items(), reverse=True):
        value = -dot(row, dual)
        if value:
            dual[pivot] = value
    assert all(dot(donor, dual) == 0 for donor in donors.values())
    assert dot(target, dual) == residual[free] != 0
    return len(basis), "separating_dual", dual


def controls():
    f = Fraction
    donors = {5: {1: f(1), 4: f(2)}, 6: {2: f(1)}, 7: {3: f(1)}, 8: {1: f(2), 4: f(4)}}
    target = {1: f(-1, 3), 2: f(2, 5), 3: f(1), 4: f(-2, 3)}
    assert solve(target, donors) == (3, "combination", {5: f(-1, 3), 6: f(2, 5), 7: f(1)})
    target[4] = f(2, 3)
    rank, kind, witness = solve(target, donors)
    assert (rank, kind, witness) == (3, "separating_dual", {4: f(1), 1: f(-2)})
    assert solve({0: f(1)}, {}) == (0, "separating_dual", {0: f(1)})
    try:
        unique([("same", 1), ("same", 2)])
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate pin control")
    return ["signed_three_donor_combination", "dependent_row_retained",
            "changed_sign_separating_dual", "empty_bank", "duplicate_key_rejected"]


def as_vector(row):
    denominator, terms = row
    return {key: Fraction(value, denominator) for key, value in terms.items()}


def run(deps, out, seconds):
    start = monotonic()
    out.mkdir(parents=True, exist_ok=False)
    raw = {}
    for path, digest in PINS.items():
        data = (deps / path).read_bytes()
        if sha256(data).hexdigest() != digest:
            raise ValueError(f"changed dependency {path}")
        raw[path] = data
    census = json.loads(raw["round41/independent/RESULT.json"], object_pairs_hook=unique)
    invoice = json.loads(raw["round41/lead/r41-price-support/PRICE.json"], object_pairs_hook=unique)
    assert census["scope_exhausted"] and not census["match_count"] and invoice["copies"] == 17
    hist = Counter(row["rank"] for row in census["records"] if row["nonzero_destination_roles"] >= 3)
    quote = invoice["exact_optimistic_single_site_by_rank"]
    stock = [sum((n * Fraction(quote[str(r)]["saving_interval"][i]) for r, n in hist.items()), Fraction())
             for i in range(2)]
    price = {
        "eligible_sites_after_pair_exclusion": sum(hist.values()),
        "eligible_nonzero_donors": sum(r["nonzero_destination_roles"] for r in census["records"]
                                        if r["nonzero_destination_roles"] >= 3),
        "optimistic_saving_interval": list(map(str, stock)),
        "whole_margin_interval_before_new_charges": [
            str(Fraction(v) + s) for v, s in zip(invoice["baseline_interval"], stock, strict=True)
        ],
        "copies": 17,
        "baseline_interval": invoice["baseline_interval"],
        "crossing_upper": invoice["crossing_upper"],
        "rank_histogram": dict(hist),
        "pins": PINS,
    }
    assert price["eligible_sites_after_pair_exclusion"] == 39 and price["eligible_nonzero_donors"] == 411
    record(out, "PRICE.json", price)

    rows = []
    known = {row["literal_index"]: row for row in census["records"]}
    core = runpy.run_path(str(deps / "round41/independent/replay_core.py"))
    word = json.loads(gzip.decompress(raw["round30/complex/source/inputs/WORD.json.gz"]),
                      object_pairs_hook=unique)

    def visit(index, role, old, chart, rank, charts, values, live):
        donor_ids = [r for r, f in enumerate(charts) if r != role and f == chart and values[r][1]]
        old_count = known[index]
        assert (role, old, chart, rank, len(donor_ids)) == (
            old_count["role"], old_count["from"], old_count["to"], old_count["rank"],
            old_count["nonzero_destination_roles"],
        )
        vector = as_vector(values[role])
        assert vector
        basis_rank, kind, witness = solve(vector, {r: as_vector(values[r]) for r in donor_ids})
        rows.append({"literal_index": index, "role": role, "source_chart": old, "destination_chart": chart,
                     "paid_rank": rank, "donors": donor_ids, "bank_rank": basis_rank, "kind": kind,
                     "witness": {str(k): str(v) for k, v in witness.items()}})

    summary = core["audit"](word, start, seconds - 2, visit)
    visited = {row["literal_index"] for row in rows}
    unvisited = sorted(known.keys() - visited)
    matches = [r["literal_index"] for r in rows if r["kind"] == "combination"]
    remaining = set(unvisited) | set(matches)
    upper = sum((Fraction(quote[str(known[clock]["rank"])]["saving_interval"][1])
                 for clock in remaining), Fraction())
    if summary["scope_exhausted"]:
        assert len(rows) == 47 and sum(len(row["donors"]) for row in rows) == 424
    record(out, "SUPPORT.json", {
        "head": core["HEAD"], "scope": "all nonzero live destination-chart donor rows at each literal MOVE",
        "census": summary, "controls": controls(), "matches": matches,
        "optimistic_saving_upper_after_support": str(upper), "rows": rows, "unvisited_moves": unvisited,
        "price_sha256": sha256((out / "PRICE.json").read_bytes()).hexdigest(),
    })


if __name__ == "__main__":
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dependencies", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--seconds", type=int, default=45, choices=range(4, 46))
    args = parser.parse_args()

    def deadline(_signum, _frame):
        raise TimeoutError("full bank runner watchdog")

    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(args.seconds)
    run(args.dependencies.resolve(), args.out.resolve(), args.seconds)
