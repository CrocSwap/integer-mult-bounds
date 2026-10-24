#!/usr/bin/env python3
"""Check the pair-closed code and its native transpose support."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PINS = {
    "helper": (HERE / "check_signed_sixteen.py",
               "7befca24a7e3fd9afccfda3f494d2a515361fdf7575751d3b690f380a6681b82"),
    "source": (HERE / "run-v2-normal/SIGNED-SIXTEEN.json.gz",
               "5ba0e042c6f27aa24e230e27a4eca5e1da573d3e39d22dab93886b207f14016c"),
    "freeze": (HERE / "FREEZE.json",
               "8739b5dbba6a5422c9b68035683876931fbf8f6599a43375d10e73eee55b2de2"),
}


def need(value, message):
    if not value:
        raise ValueError(message)


def read(name):
    path, pin = PINS[name]
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned input " + name)
    return raw


read("helper")
spec = importlib.util.spec_from_file_location("paired_signed_code", PINS["helper"][0])
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
b, r = m.b, m.r


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    for name in PINS:
        read(name)
    source = json.loads(read("source"))
    model = json.loads(m.read("response"))
    H, Hi = b.rows(source["pair_code"]), b.rows(source["pair_code_inverse"])
    K, J = b.rows(source["input_metric"]), b.rows(source["input_metric_inverse"])
    selected = set(source["centre_ports"])
    selector_inverse = r.identity(112)
    extra = []
    for pair in model["pair_codes"]:
        if set(pair["ports"]) <= selected:
            ports = pair["ports"]
            local = [{j: F(c) for j, c in enumerate(row) if c} for row in pair["matrix"]]
            extra += r.inverse_word(b.factor(local, ports))
            for p in ports:
                selector_inverse[p] = dict(Hi[p])
    C = r.product(selector_inverse, b.rows(source["code"]))
    need(C == r.product(r.product(Hi, b.rows(source["mode_code"])), H),
         "The complete physical pair conjugation")
    Ct = r.transpose(C, 112)
    G = r.product(r.product(C, K), Ct)
    need(all(set(row) == {p} and b.unit(row[p]) for p, row in enumerate(G)),
         "The new physical metric is diagonal")
    Gi = [{p: 1 / row[p]} for p, row in enumerate(G)]
    Ci = r.product(r.product(K, Ct), Gi)
    Cti = r.transpose(Ci, 112)
    need(r.product(C, Ci) == r.product(Ci, C) == r.identity(112), "Both code inverse orders")
    need(r.product(r.product(Ct, Gi), C) == J, "The transpose metric identity")
    groups = [set(block["ports"]) for block in model["blocks"]]
    codes = {"code": C, "transpose": Ct}
    native_codes = {}
    for name, matrix in codes.items():
        native = r.product(r.product(H, matrix), Hi)
        native_codes[name] = native
        need(all(not matrix[p].get(p, 0) and not native[p].get(p, 0)
                 and any(p in group and set(native[p]) <= group for group in groups)
                 for p in range(112) if p not in selected),
             "Every ordinary row has native block support and zero diagonal")
    recovery = r.identity(112)
    for p in selected:
        recovery[p] = dict(H[p])
    need([r.product(recovery, C)[p] for p in source["centre_ports"]]
         == b.rows(model["reflection_L"]), "The complete centre recovery")
    word = source["scalar_words"]["code"] + extra
    words = {"code": word, "transpose": r.transpose_word(word),
             "inverse": r.inverse_word(word),
             "inverse_transpose": r.transpose_word(r.inverse_word(word))}
    expected = {"code": C, "transpose": Ct, "inverse": Ci, "inverse_transpose": Cti}
    reports = {}
    for name, tape in words.items():
        actual, report = b.replay(tape, 640)
        need(actual[:112] == expected[name] and actual[112:] == r.identity(640)[112:],
             "All640 exact columns of each complete word")
        reports[name] = report
    payload = {
        "schema": "paired-signed-sixteen-code-v1",
        "source_pins": {name: {"path": str(path), "sha256": pin} for name, (path, pin) in PINS.items()},
        "centre_ports": source["centre_ports"], "ordinary_ports": source["ordinary_ports"],
        "blocks": model["blocks"], "pair_code": source["pair_code"],
        "pair_code_inverse": source["pair_code_inverse"],
        "code": r.encoded(C), "transpose": r.encoded(Ct),
        "inverse": r.encoded(Ci), "inverse_transpose": r.encoded(Cti),
        "native_codes": {name: r.encoded(matrix) for name, matrix in native_codes.items()},
        "input_metric": r.encoded(K), "input_metric_inverse": r.encoded(J),
        "output_metric": r.encoded(G), "output_metric_inverse": r.encoded(Gi),
        "centre_recovery": r.encoded(recovery), "selected_pair_inverse_word": extra,
        "scalar_words": words,
        "scope": "Complete pair-closed scalar code, its transpose, and exact native support. No native service or routed caller is asserted.",
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (args.out / "PAIRED-SIGNED-SIXTEEN.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_PAIRED_SIGNED_SIXTEEN_CODE",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "all_input_columns": 640, "unchanged_outside_fields": 528,
        "selected_fields": 16, "selected_pair_inverse_price": r.price(extra),
        "reports": reports,
        "output_metric_counts": dict(Counter(str(row[p]) for p, row in enumerate(G))),
        "scope": payload["scope"],
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
