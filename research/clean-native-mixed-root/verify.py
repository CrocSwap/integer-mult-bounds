#!/usr/bin/env python3
"""A signed invoice conditional on two retained predecessor interfaces.

Produced by Nick Petalas. Apache-2.0.
The exact interval arithmetic is zxv's retained implementation. Historical
construction claims are premises, not conclusions of this verifier.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAVING = Q("0.0032868")
COPIES = 18


def need(condition, message):
    if not condition:
        raise ValueError(message)


def histogram(raw):
    need(isinstance(raw, dict) and 1 <= len(raw) <= 145, "bounded histogram")
    result = Counter()
    for rank, count in raw.items():
        need(str(int(rank)) == rank and 1 <= int(rank) <= 145, "canonical rank")
        need(type(count) is int and 0 < count <= 100000, "positive bounded count")
        result[int(rank)] = count
    return result


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    live = [row for row in sources["files"] if row["usage"] == "input"]
    need(len(live) == 1, "one retained arithmetic input")
    snapshots = sources["retained_external_snapshots"]
    need(len(snapshots) == 6, "two receipts, two proofs and two notices")
    checked = {}
    paths = [(live[0], HERE.parents[1] / live[0]["path"])]
    paths.extend((row, HERE / row["path"]) for row in snapshots)
    for row, path in paths:
        data = path.read_bytes()
        need(sha256(data).hexdigest() == row["sha256"], "source SHA256: " + str(path))
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(sha1(blob).hexdigest() == row["git_blob"], "source Git blob: " + str(path))
        checked[row["path"]] = row["sha256"]
    path = HERE.parents[1] / live[0]["path"]
    spec = importlib.util.spec_from_file_location("retained_bounds", path)
    need(spec is not None and spec.loader is not None, "arithmetic module loader")
    bounds = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bounds)
    return checked, bounds


def compose(root, merge, copies=COPIES):
    old, new = root["local"], merge["local"]
    need(copies == root["caller"]["native_stages"] == COPIES, "eighteen native copies")
    for key in ("public_inputs", "owned_fields", "peak_owned_fields", "helpers"):
        need(old[key] == new[key], "preserved local interface: " + key)
    need(new["owned_lifetimes"] == old["owned_lifetimes"] + 1, "one charged lifetime")
    need(new["real_scalar_allowance"] == old["real_scalar_allowance"] + 508,
         "all additional scalar allowance is charged")
    old_local, new_local = histogram(old["paid"]), histogram(new["paid"])
    delta = Counter(new_local)
    delta.subtract(old_local)
    need({r: n for r, n in delta.items() if n} == {1: -1, 4: -1, 5: 1},
         "the complete local recursive substitution")
    targets = histogram(root["price"]["targets"])
    remainder = histogram(root["price"]["paid"])
    remainder.subtract({r: copies * n for r, n in old_local.items()})
    need(all(n >= 0 for n in remainder.values()), "all other caller jobs retained")
    paid = remainder + Counter({r: copies * n for r, n in new_local.items()})
    need(sum(targets.values()) == 13652 and sum(paid.values()) == 67132,
         "complete productive and paid field counts")
    target_mass = sum(r * n for r, n in targets.items())
    paid_mass = sum(r * n for r, n in paid.items())
    need((target_mass, paid_mass) == (185740, 184980), "complete unchanged rank masses")
    routes = (sum(new_local.values()) + merge["native"]["helper_normalizers"]
              + merge["native"]["main_adapters"] + 4 * 104 + 4 * new["owned_lifetimes"]) * 1000
    ordinary = routes + new["real_scalar_allowance"]
    need(ordinary == 5512178 and ordinary < 10**7, "charged local ordinary envelope")
    return targets, paid, {"local_routes": routes, "local_scalar": new["real_scalar_allowance"],
                           "local_ordinary_total": ordinary, "local_budget": 10**7,
                           "additional_lifetimes": copies, "peak_owned_fields": new["peak_owned_fields"]}


def margin(bounds, targets, paid):
    target = bounds.moment(targets, 1 - SAVING)
    cost = bounds.moment(paid, 1 - SAVING)
    return target[0] - cost[1], target[1] - cost[0]


def controls(root, merge, bounds):
    rejected = []
    mutations = [("helper target debit", "helpers", "9", 1),
                 ("unpaid merged query", "paid", "5", -1),
                 ("omitted scalar cleanup", "real_scalar_allowance", None, -508),
                 ("omitted scratch lifetime", "owned_lifetimes", None, -1),
                 ("larger peak treated as unchanged", "peak_owned_fields", None, 1)]
    for label, key, rank, change in mutations:
        damaged = deepcopy(merge)
        if rank is None:
            damaged["local"][key] += change
        else:
            damaged["local"][key][rank] += change
        try:
            compose(root, damaged)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("semantic mutation accepted: " + label)
    for copies in (17, 19):
        try:
            compose(root, merge, copies)
        except ValueError:
            rejected.append("wrong native multiplicity " + str(copies))
        else:
            raise ValueError("wrong native multiplicity accepted")
    for rank in range(1, 146):
        low, high = bounds.power(rank, Q(1, 2))
        need(0 < low <= high and low * low <= rank <= high * high,
             "integer square-root enclosure control")
    return {"rejected": rejected, "exact_square_root_controls": 145}


def build_result():
    checked, bounds = authenticate()
    root = json.loads((HERE / "inputs/root-result.json").read_text())
    merge = json.loads((HERE / "inputs/merge-result.json").read_text())
    targets, paid, ordinary = compose(root, merge)
    new_margin = margin(bounds, targets, paid)
    old_margin = margin(bounds, targets, histogram(root["price"]["paid"]))
    need(Q("0.0130615") < new_margin[0] <= new_margin[1] < Q("0.0130617"),
         "strict positive combined raw margin")
    need(old_margin[1] < 0, "the old root invoice cannot fund this saving")
    one, four, five = [bounds.power(r, 1 - SAVING) for r in (1, 4, 5)]
    gain = (COPIES * (one[0] + four[0] - five[1]),
            COPIES * (one[1] + four[1] - five[0]))
    need(gain[0] > 0 and new_margin[0] - old_margin[1] <= gain[1]
         and gain[0] <= new_margin[1] - old_margin[0], "full signed substitution identity")
    result = {"status": "PASS_CLEAN_NATIVE_MIXED_ROOT_SIGNED_INVOICE",
              "claim_type": "scoped accounting proof conditional on retained interfaces",
              "saving_screen": str(SAVING), "whole_algorithm_kappa_claimed": False,
              "targets": dict(sorted(targets.items())), "paid": dict(sorted(paid.items())),
              "productive_fields": sum(targets.values()), "paid_jobs": sum(paid.values()),
              "target_rank_mass": 185740, "paid_rank_mass": 184980,
              "native_copies": COPIES, "paid_job_reduction": COPIES,
              "combined_margin": bounds.display(new_margin),
              "predecessor_invoice_margin_at_same_saving": bounds.display(old_margin),
              "signed_gain": bounds.display(gain), "ordinary_allowance": ordinary,
              "controls": controls(root, merge, bounds), "source_sha256": checked}
    result["verifier_sha256"] = sha256(Path(__file__).read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    result = build_result()
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.write_result is not None:
        args.write_result.write_text(encoded)
    else:
        need(json.loads((HERE / "RESULT.json").read_text()) == json.loads(encoded),
             "generated receipt matches exact sources and current verifier")
    print(encoded, end="")


if __name__ == "__main__":
    main()
