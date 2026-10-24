#!/usr/bin/env python3
"""Retune the complete native word for the signed-metric response."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "model": (HERE / "model-normal-v2/RESPONSE.json.gz",
              "df2d2028c99028db3c645b3311d7f31ff96efe72f6f9257f99157ce030ff43d0"),
    "model_freeze": (HERE / "MODEL-FREEZE.json",
                     "9dbff19fa68567eadea82cef2add71fda3ffe7228944028d06d53880da8b70f7"),
    "source": (LANES / "new-core-transfer-20261017/low-displacement-20261020/odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
               "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"),
    "native": (LANES / "new-core-transfer-20261017/low-displacement-20261020/emit_native.py",
               "599987ddfe2fdb8fd4be533d783e24bf40a95b6c69118ec1552a10b06f1d5745"),
    "cyclic": (LANES / "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json",
               "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585"),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def read(name):
    path, pin = PINS[name]
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Native source pin " + name)
    return raw


read("native")
spec = importlib.util.spec_from_file_location("signed_metric_native_base", PINS["native"][0])
n = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = n
spec.loader.exec_module(n)
r = n.r


def retune(original, cyclic, mode):
    word = deepcopy(original)
    parameters = {row["id"]: row for row in cyclic["parameters"]}
    transfers = {row["event"]: row for row in original["transfer_records"]}
    events, records = [], []
    for i, event in enumerate(original["events"]):
        if i not in transfers:
            events.append(deepcopy(event))
            continue
        record = deepcopy(transfers[i])
        if record["part"] == "large48":
            parameter = parameters[record["parameter"]]
            carriers = cyclic["cyclic_carriers"][parameter["vertex"]]
            target, source = carriers[parameter["row"]], carriers[parameter["column"]]
        else:
            need(record["part"] == "small64", "Known actual transfer region")
            target, source = record["target_port"], record["source_port"]
        coefficient = mode[target].get(source, F(0))
        need(event[0] == "scalar" and event[1][:3] == ["add", 112 + target, source],
             "The original transfer addresses")
        if coefficient:
            record.update(event=len(events), coefficient=str(coefficient))
            changed = deepcopy(event)
            changed[1][3] = str(coefficient)
            events.append(changed)
            records.append(record)
    word["events"], word["transfer_records"] = events, records
    word["retuned_transfer_count"] = len(records)
    word["deleted_zero_transfers"] = len(transfers) - len(records)
    return word


def inverse_adjoint(original):
    word = deepcopy(original)
    for event in word["events"]:
        if event[0] == "native":
            continue
        op, target, source, coefficient = event[1]
        c = F(coefficient)
        if op == "add":
            event[1] = [op, source, target, str(-c)]
        else:
            need(op == "scale", "The literal inverse-adjoint scalar grammar")
            event[1] = [op, target, None, str(1 / c)]
    for record in word["transfer_records"]:
        record["coefficient"] = str(-F(record["coefficient"]))
    word["duality"] = "Keep event order and each native unitary. Replace each real scalar gate by its inverse transpose."
    return word


def metric_wrapper(original, model, pre_inverse):
    word = deepcopy(original)
    pre = model["metric_inverse_scale_word" if pre_inverse else "metric_scale_word"]
    post = model["metric_scale_word" if pre_inverse else "metric_inverse_scale_word"]

    def events(gates, frames):
        result = []
        for bank in (0, 112):
            for op, target, source, coefficient in gates:
                need(op == "scale" and source is None, "The metric is a physical diagonal")
                result.append(["scalar", [op, bank + target, None, coefficient], frames[bank + target]])
        return result

    prefix, suffix = events(pre, word["start"]), events(post, word["final"])
    word["events"] = prefix + word["events"] + suffix
    for record in word["transfer_records"]:
        record["event"] += len(prefix)
    word["metric_wrapper"] = {"prefix_scalars": len(prefix), "suffix_scalars": len(suffix),
                              "extra_native_children": 0, "real_scalar_primitives": 640}
    return word


def verify(word, response, direction, reference):
    report = n.verify_word(word, response, direction)
    reference_native = [event for event in reference["events"] if event[0] == "native"]
    need([event for event in word["events"] if event[0] == "native"] == reference_native,
         "The complete native sequence is unchanged")
    for key in ("native_recipes", "endpoint_adapters", "frames", "start", "final"):
        need(word[key] == reference[key], "The exact inherited native data " + key)
    need(len(word["start"]) == 640 and len(word["endpoint_adapters"]) == 224,
         "Complete arbitrary-field and adapter counts")
    need(all((event[1] if event[0] == "native" else event[1][1]) < 224
             and (event[0] == "native" or event[1][2] is None or event[1][2] < 224)
             for event in word["events"]), "No helper or owned field is touched")
    state = r.identity(640)
    height = 0
    for event in word["events"]:
        if event[0] == "native":
            continue
        op, target, source, coefficient = event[1]
        c = F(coefficient)
        if op == "add":
            r.add(state[target], state[source], c)
        else:
            state[target] = {p: c * value for p, value in state[target].items() if c * value}
        for value in state[target].values():
            d = value.denominator
            need(not d & (d - 1), "Every prefix remains dyadic")
            height = max(height, d.bit_length() - 1)
    report.update(binary_height=height, explicit_endpoint_monomials=224,
                  inherited_native_recipe_count=len(word["native_recipes"]),
                  new_native_recipe_count=0, native_sequence_byte_equal=True)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    read("model_freeze")
    model, source, cyclic = (json.loads(read(name)) for name in ("model", "source", "cyclic"))
    E, dual = n.rows(model["physical"]["E"]), n.rows(model["physical"]["inverse_adjoint_E"])
    Em = n.rows(model["mode"]["E"])
    dualm = r.transpose(n.rows(model["mode"]["inverse_E"]), 112)
    providers, reports = {}, {}
    for provider, old in source["providers"].items():
        original = old["forward"]
        need(source["model"]["ports"] == model["ports"] == cyclic["ports"],
             "Actual provider labels")
        forward = retune(original, cyclic, Em)
        backward = inverse_adjoint(forward)
        dual_forward = retune(original, cyclic, dualm)
        inverse_backward = inverse_adjoint(dual_forward)
        words = {
            "forward_E": forward,
            "backward_transpose_E": backward,
            "forward_inverse_adjoint_E": dual_forward,
            "backward_inverse_E": inverse_backward,
            "forward_inverse_adjoint_by_metric": metric_wrapper(forward, model, True),
            "backward_inverse_by_metric": metric_wrapper(backward, model, False),
        }
        contracts = {
            "forward_E": (E, "forward"),
            "backward_transpose_E": (E, "backward"),
            "forward_inverse_adjoint_E": (dual, "forward"),
            "backward_inverse_E": (dual, "backward"),
            "forward_inverse_adjoint_by_metric": (dual, "forward"),
            "backward_inverse_by_metric": (dual, "backward"),
        }
        reports[provider] = {}
        for name, word in words.items():
            response, direction = contracts[name]
            reports[provider][name] = verify(word, response, direction, original)
            need(reports[provider][name]["native_profile"] == {1: 1520, 2: 64, 3: 48}
                 and reports[provider][name]["native_mass"] == 1792,
                 "The full local native invoice")
        need(words["backward_transpose_E"] == inverse_adjoint(words["forward_E"])
             and words["backward_inverse_E"] == inverse_adjoint(words["forward_inverse_adjoint_E"]),
             "Both complete literal inverse-adjoint directions")
        for name in ("forward_E", "backward_inverse_E"):
            bad = deepcopy(words[name])
            record = bad["transfer_records"][0]
            del bad["events"][record["event"]]
            try:
                response, direction = contracts[name]
                verify(bad, response, direction, original)
            except ValueError:
                pass
            else:
                raise ValueError("A missing nonzero transfer was accepted")
        providers[provider] = words
    need(reports["base"] == reports["extra"], "Both actual providers have the same verified invoice")
    payload = {
        "schema": "signed-metric-reciprocal-native-v1",
        "source_pins": {name: {"path": str(path.relative_to(LANES)), "sha256": pin}
                        for name, (path, pin) in PINS.items()},
        "model": model, "providers": providers,
        "contracts": {
            "input": "Physical X=Qx, Y=y. The native adapters are explicit.",
            "forward_E": "Physical X=F x, Y=F q(y+E x).",
            "backward_transpose_E": "Physical X=F(x-E^T y), Y=F q y.",
            "forward_inverse_adjoint_E": "Physical X=F x, Y=F q(y+E^-T x).",
            "backward_inverse_E": "Physical X=F(x-E^-1 y), Y=F q y.",
            "scope": "All640 inputs are arbitrary. The416 fields outside the two data banks are unchanged.",
        },
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for provider, words in saved["providers"].items():
        for name, word in words.items():
            response, direction = contracts[name]
            need(verify(word, response, direction, source["providers"][provider]["forward"])
                 == reports[provider][name], "Complete serialized replay")
    (args.out / "NATIVE.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    checks = {
        "status": "PASS_SIGNED_METRIC_NATIVE",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "source_pins": payload["source_pins"], "reports": reports,
        "native_phase_scope": "All inherited native records, ordered frames and endpoint adapters are byte-equal. No new spatial phase recipe is used or claimed.",
        "negative_controls": "One nonzero transfer is deleted and rejected in each principal direction and provider.",
        "scope": "Complete local native data service. Productive helper progress, global routing, centre retention, terminal decoding and recursive hosting remain separate.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(checks, sort_keys=True, indent=2) + "\n")
    print(json.dumps(checks, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
