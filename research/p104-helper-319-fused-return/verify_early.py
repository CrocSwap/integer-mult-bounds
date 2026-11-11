# SPDX-License-Identifier: Apache-2.0
"""Verify the source, literal local operator, and complete signed price."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from construct import construct, local_certificate
from packing_reference import packing
from source import HERE, canonical, load, need, read, sources


def normalize(x):
    return json.loads(json.dumps(x, default=str))


def run():
    need(__debug__, "Proof assertions enabled")
    with sources() as (vendor, archive, rank9, bundle, parent, old):
        new = construct(old)
        need(canonical(new) == gzip.decompress((HERE / "WORD.json.gz").read_bytes()),
             "Complete emitted word")
        independent = load("p104_319_adjoint", vendor / "independent.py")
        before, after = map(independent.native, (old, new))
        need(normalize(before) == read(parent / "NATIVE-RESULT.json")["native"],
             "Reproduce complete #7314 native inventory")
        need(not after["bad_inputs"], "Arbitrary-input native adjoint")
        need(after["lifetimes"] == 73 and after["owned_peak"] == 50 and
             new["owned_fields"] == old["owned_fields"] == 68 and
             after["rises"] == before["rises"] and
             sum(int(r) * count for r, count in after["rises"].items()) == 56,
             "Complete owned census")
        delta = Counter(after["paid"])
        delta.subtract(before["paid"])
        delta = {r: v for r, v in delta.items() if v}
        need(after["helpers"] == before["helpers"] and delta == {1: -1, 5: -1, 6: 1},
             "Complete native paid and productive delta")
        reference = read(parent / "RESULT.json")["price"]
        old_invoice = {k: {int(r): v for r, v in x.items()} if k in ("T", "P") else x
                       for k, x in reference["after"].items()
                       if k not in ("raw_crossing", "no_E_credit_crossing")}
        new_invoice = deepcopy(old_invoice)
        for r, d in delta.items():
            new_invoice["P"][r] = new_invoice["P"].get(r, 0) + 17 * d
        need(sum(new_invoice["P"].values()) == 110519 and
             sum(new_invoice["T"].values()) == 22461 and new_invoice["S"] == 1424 and
             not new_invoice["empty_root_credits"], "Whole 17-stage invoice")
        engine = load("p104_319_directed_price", bundle / "gate.py")
        gate, price = engine.exact_price(vendor, archive, old_invoice, new_invoice,
                                         {"gate": reference["gate"]})
        need(Q(gate["claim"]) > Q(reference["gate"]["claim"]) and
             price["baseline_rejects_new_claim"], "Exact #7314 comparator rejects the new bound")
        ceiling = packing(new_invoice, after, engine.module("p104_319_tariff",
                          vendor / "interval_gate.py"), Q(gate["claim"]))
        return normalize(dict(status="PASS_HELPER_319_EXACT_NATIVE_AND_SIGNED_PRICE",
                              word_sha256=sha256(canonical(new)).hexdigest(),
                              local=local_certificate(old), native=after, native_delta=delta,
                              invoice=new_invoice, gate=gate, price=price, packing=ceiling))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    if args.out:
        with args.out.open("x") as f:
            json.dump(result, f, sort_keys=True, indent=2)
            f.write("\n")
    else:
        need(result == read(HERE / "EARLY-RESULT.json"), "Every frozen early result field")
    print(result["status"], result["price"]["claim_decimal"], flush=True)
