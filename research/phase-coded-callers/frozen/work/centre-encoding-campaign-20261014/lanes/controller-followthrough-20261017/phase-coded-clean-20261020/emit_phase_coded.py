#!/usr/bin/env python3
"""Check a phase-coded ordinary response in the clean native word."""

import argparse
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
SOURCE = LANES / (
    "new-core-transfer-20261017/low-displacement-20261020/"
    "clean-late-exchange-20261020"
)
PINS = {
    "forward_producer": (
        SOURCE / "emit_clean_exchange.py",
        "91ee4ce54a5774dfdec7ac0a83f78c5076ef14d0ee30f2dcc7ecf448b869ecbc",
    ),
    "dual_producer": (
        SOURCE / "emit_dual.py",
        "b78a5e653e8436592fd6a8d0e183aa34dcd2f3f1d81a775a0f0d5b5c5007a1a8",
    ),
    "forward": (
        SOURCE / "run-normal/CLEAN-LATE-EXCHANGE.json.gz",
        "b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083",
    ),
    "freeze": (
        SOURCE / "FREEZE.json",
        "96048355033e5f5bdd26dadddb869708faae6f8b0d9a61a1ae696e5a5c20c0bc",
    ),
    "dual_freeze": (
        SOURCE / "DUAL-FREEZE.json",
        "fa8f910fe7f22a696f47513c95e814588723dc8abaaa68061fcba3676c308d43",
    ),
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


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def poly_add(target, source, coefficient=F(1)):
    for key, value in source.items():
        target[key] = target.get(key, F(0)) + coefficient * value
        if not target[key]:
            del target[key]


def poly_identity():
    return [{(i, 0): F(1)} for i in range(640)]


def apply_scalar_map(rows, state):
    result = []
    for row in rows:
        value = {}
        for source, coefficient in row.items():
            poly_add(value, state[source], coefficient)
        result.append(value)
    return result


def encoded_polynomials(rows):
    return [
        [[source, exponent, str(value)]
         for (source, exponent), value in sorted(row.items())]
        for row in rows
    ]


def report_prefix_scope(report):
    report["body_content_prefix_row_one_norm"] = report.pop(
        "maximum_content_prefix_row_one_norm"
    )
    report["physical_entry_prefix_row_one_norm"] = "2"
    report["prefix_scope"] = (
        "The body bound uses its declared typed input. The physical "
        "prefix is a separate unit shear. This is not a complete "
        "recursive numerical-grid invoice."
    )


def remove_transfers(original):
    word = deepcopy(original)
    events, ranges, removed = [], {}, []
    for stage, interval in sorted(
            original["stage_ranges"].items(), key=lambda item: item[1][0]):
        start = len(events)
        for index in range(*interval):
            event = original["events"][index]
            is_transfer = (
                stage == "retained_core"
                and event[0] == "scalar"
                and event[1][0] == "add"
                and 112 <= event[1][1] < 224
                and 0 <= event[1][2] < 112
            )
            if is_transfer:
                removed.append([index, event])
            else:
                events.append(deepcopy(event))
        ranges[stage] = [start, len(events)]
    word["events"], word["stage_ranges"] = events, ranges
    need(len(removed) == 592, "All ordinary source-to-target transfers")
    return word, removed


def expected_zero(code, selected, identity):
    rows = deepcopy(identity)
    for p in selected:
        rows[p] = {112 + p: F(-1)}
        rows[112 + p] = dict(code[p])
    return rows


def expected_dual(code, selected, identity):
    rows = deepcopy(identity)
    for p in selected:
        rows[p] = {112 + p: F(1)}
        rows[112 + p] = {p: F(-1)}
        for j, coefficient in code[p].items():
            if j != p:
                rows[j][112 + p] = -coefficient
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    for name in PINS:
        read(name)
    base = load("phase_clean_source", PINS["forward_producer"][0])
    dual = load("phase_clean_dual", PINS["dual_producer"][0])
    n = base.n
    source = json.loads(read("forward"))
    pivots = source["selected_ports"]
    selected = set(pivots)
    ordinary = [p for p in range(112) if p not in selected]
    code = n.rows(source["code"])
    identity = n.r.identity(640)
    zero_map = expected_zero(code, selected, identity)
    dual_map = expected_dual(code, selected, identity)
    permutation = list(range(640))
    for p in pivots:
        permutation[p], permutation[112 + p] = 112 + p, p

    expected_f = poly_identity()
    expected_b = poly_identity()
    for p in pivots:
        expected_f[p] = {(112 + p, 0): F(-1)}
        expected_f[112 + p] = {(j, 0): v for j, v in code[p].items()}
        expected_b[p] = {(112 + p, 0): F(1)}
        expected_b[112 + p] = {(p, 0): F(-1)}
    for p in ordinary:
        expected_f[112 + p][p, 1] = F(1)
        expected_b[p][112 + p, -1] = F(-1)
        for j in pivots:
            value = -code[j].get(p, F(0))
            if value:
                expected_b[p][112 + j, 0] = value

    providers, reports = {}, {}
    for provider, variants in source["providers"].items():
        providers[provider], reports[provider] = {}, {}
        for entry in ("I", "Q"):
            original = variants[entry]
            forward, removed = remove_transfers(original)
            report = base.verify(forward, zero_map)
            need(
                [e for e in original["events"] if e[0] == "native"]
                == [e for e in forward["events"] if e[0] == "native"],
                "Every native event is unchanged",
            )
            need(
                all(forward[k] == original[k] for k in
                    ("frames", "native_recipes", "input_views", "output_views")),
                "Every native phase and endpoint adapter is unchanged",
            )
            state = poly_identity()
            for p in ordinary:
                state[112 + p][p, 1] = F(1)
            actual = apply_scalar_map(zero_map, state)
            need(actual == expected_f, "All640 ordered forward columns")
            report["physical_entry_adds"] = 96
            report["complete_scalar_primitives"] = (
                report["real_scalar_primitives"] + 96 * 8
            )
            report["removed_transfer_adds"] = len(removed)
            report["formal_Q_order"] = "Q_p remains attached to input source p."
            report_prefix_scope(report)
            providers[provider]["forward_" + entry] = {
                "physical_prefix": [["add", 112 + p, p, "1"] for p in ordinary],
                "prefix_location": "Before every inherited input adapter.",
                "body": forward,
                "removed_transfers": removed,
            }
            reports[provider]["forward_" + entry] = report

            if entry == "Q":
                backward = dual.lower(forward, permutation)
                report_b = base.verify(backward, dual_map)
                state = poly_identity()
                for p in ordinary:
                    state[p][112 + p, -1] = F(-1)
                actual = apply_scalar_map(dual_map, state)
                need(actual == expected_b, "All640 ordered backward columns")
                report_b["physical_entry_adds"] = 96
                report_b["complete_scalar_primitives"] = (
                    report_b["real_scalar_primitives"] + 96 * 8
                )
                report_b["extra_boundary_swaps"] = 0
                report_b["formal_Q_order"] = (
                    "q_p remains attached to input source Y_p."
                )
                report_prefix_scope(report_b)
                providers[provider]["backward_Q"] = {
                    "physical_prefix": [["add", p, 112 + p, "-1"]
                                        for p in ordinary],
                    "prefix_location": "Before every inherited input adapter.",
                    "body": backward,
                }
                reports[provider]["backward_Q"] = report_b

        forward = providers[provider]["forward_Q"]["body"]
        bad = deepcopy(forward)
        bad["events"].append(deepcopy(
            providers[provider]["forward_Q"]["removed_transfers"][0][1]))
        try:
            base.verify(bad, zero_map)
        except ValueError:
            pass
        else:
            raise ValueError("A retained ordinary transfer was accepted")

    payload = {
        "schema": "phase-coded-clean-local-v1",
        "source_pins": {
            name: {"path": str(path), "sha256": pin}
            for name, (path, pin) in PINS.items()
        },
        "selected_ports": pivots,
        "ordinary_ports": ordinary,
        "code": source["code"],
        "providers": providers,
        "zero_response_content": n.r.encoded(zero_map[:224]),
        "zero_response_dual_content": n.r.encoded(dual_map[:224]),
        "phase_coded_forward": encoded_polynomials(expected_f[:224]),
        "phase_coded_backward": encoded_polynomials(expected_b[:224]),
        "contract": {
            "input_Q": "X=Q(a,u), Y_P=Q_P z, Y_R=v.",
            "input_I": "X=Q(a,u), Y_P=z, Y_R=v.",
            "output_frames": "X and Y_P are F9; Y_R is F9 q_R.",
            "forward_content": "(-z,u,a+B u,v+Q_R u)",
            "backward_content": "(z,u+D z-q_R v,-a,v), D=-B^T",
            "prefix": (
                "The physical ordinary ADD is applied before the input "
                "views. It is not a same-frame logical ADD."
            ),
            "scope": (
                "Complete local words. A routed caller and its final "
                "original-input phases are separate obligations."
            ),
        },
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (args.out / "PHASE-CODED.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    receipt = {
        "status": "PASS_PHASE_CODED_CLEAN_LOCAL",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "reports": reports,
        "arbitrary_input_columns": 640,
        "arbitrary_helpers_restored": 416,
        "new_native_kernels": 0,
        "native_phase_scope": (
            "All native kernels and endpoint adapters are byte-exact "
            "inherited records. The physical entry ADD has coefficient "
            "one or minus one and no spatial operator."
        ),
        "scope": payload["contract"]["scope"],
    }
    (args.out / "CHECKS.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
