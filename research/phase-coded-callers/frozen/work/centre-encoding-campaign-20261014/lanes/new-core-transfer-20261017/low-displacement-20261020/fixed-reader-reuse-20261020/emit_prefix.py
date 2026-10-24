#!/usr/bin/env python3
"""Emit the checked native prefix before a routed reader query."""

import argparse
from copy import deepcopy
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "row-only-capture-20261020"
LANES = HERE.parents[2]
PINS = {
    "reuse": (SOURCE / "reuse-normal/LINE-ENTRY-REUSE.json.gz",
              "efe67a962752f2c36513d84094d215fd0909a5360707938ff99d62743dc72110"),
    "checker": (SOURCE / "emit_capture.py",
                "1557c9f38b1d89f6d38e920d8db604607519a99cf37366b4c15414aed489cf1f"),
    "review": (LANES / "new-native-recipes-20261017/line-entry-reuse-review-20261020/FREEZE.json",
               "cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c"),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def read(name):
    path, pin = PINS[name]
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned source " + name)
    return raw


read("checker")
spec = importlib.util.spec_from_file_location("reuse_prefix_base", PINS["checker"][0])
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = json.loads(read("reuse"))
    read("review")
    response = base.n.rows(source["response"])
    selected = set(source["selected_ports"])
    providers, reports = {}, {}
    for provider, original in source["providers"].items():
        word = deepcopy(original)
        end = original["stage_ranges"]["late_query"][0]
        word["events"] = word["events"][:end]
        del word["stage_ranges"]["late_query"]
        report = base.verify(word, base.n.r.identity(112), response,
                             [{} for _ in range(112)], selected)
        need(report["real_scalar_primitives"] == 6456 and report["native_mass"] == 1792,
             "The complete carrier-only invoice")
        need(end == 2406 and len(word["events"]) == end, "The exact complete prefix cut")
        providers[provider], reports[provider] = word, report
    payload = {
        "schema": "sixteen-record-carrier-prefix-v1",
        "source_pins": {key: {"path": str(path), "sha256": pin}
                        for key, (path, pin) in PINS.items()},
        "ports": source["ports"], "selected_ports": source["selected_ports"],
        "ordinary_ports": source["ordinary_ports"], "response": source["response"],
        "providers": providers,
        "physical_contract": {
            "input": "X=Qx; Y_U=y_U; Y_P=Q_P z, with arbitrary independent z.",
            "output": "Xout=F9x; Yout_U=F9q_U(y+Ex)_U; Yout_P=F9z.",
            "scope": "The complete native prefix ends before any selected reader query.",
        },
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    for provider, word in json.loads(raw)["providers"].items():
        need(base.verify(word, base.n.r.identity(112), response,
                         [{} for _ in range(112)], selected) == reports[provider],
             "The serialized prefix passes")
    (args.out / "CARRIER-PREFIX.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {"status": "PASS_EXACT_CARRIER_ONLY_PREFIX",
               "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "payload_decompressed_sha256": sha256(raw).hexdigest(),
               "reports": reports}
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
