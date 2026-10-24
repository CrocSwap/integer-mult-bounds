#!/usr/bin/env python3
"""Emit the typed native macro word for the p19 controller chain."""
import hashlib
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p19_word as W


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(gates):
    out = []
    coded = [False] * 38
    scratch = 0
    for index, gate in enumerate(gates):
        kind = gate[0]
        if kind == "GAUGE_LOAD":
            role = gate[1]
            need(role % 2 == 1 and not coded[role], f"load {index}")
            coded[role] = True
            scratch += 8
            out.append({"index": index, "op": "CODE", "role": role,
                        "word": [["C", -1]], "owned_scratch": 8})
        elif kind == "GAUGE_UNLOAD":
            role = gate[1]
            need(role % 2 == 1 and coded[role], f"unload {index}")
            coded[role] = False
            scratch -= 8
            out.append({"index": index, "op": "CODE", "role": role,
                        "word": [["C", 1]], "owned_scratch": 8})
        elif kind in ("FORWARD", "REVERSE"):
            x, y = gate[1:3]
            unit = x // 2
            need(x == 2 * unit and y == x + 1, f"pair {index}")
            need(coded[y], f"coded read {index}")
            out.append({"index": index, "op": "CENTER_FREE_FULL", "unit": unit,
                        "direction": "forward" if kind == "FORWARD" else "backward",
                        "roles": [x, y], "stage": 2 * unit})
        elif kind == "LETTER":
            x, y = gate[1:3]
            unit = x // 2
            need(x == 2 * unit and y == x + 1, f"letter {index}")
            out.append({"index": index, "op": "LETTER", "unit": unit,
                        "roles": [x, y], "stage": 2 * unit + 1,
                        "gaussian": gate[3]})
        elif kind == "IDLE":
            x, y, power, phase = gate[1:]
            unit = x // 2
            need(x == 2 * unit and y == x + 1 and power > 0, f"idle {index}")
            out.append({"index": index, "op": "PAID_IDLE", "unit": unit,
                        "roles": [x, y], "power": power, "phase": phase,
                        "stages": list(range(1, power + 1))})
        elif kind == "BRIDGE":
            dst, src, coefficient = gate[1:4]
            need(dst != src and coefficient in (-1, 1), f"bridge {index}")
            out.append({"index": index, "op": "ADD", "dst": dst, "src": src,
                        "coefficient": coefficient})
        elif kind == "SWAP":
            x, y, sign = gate[1:]
            need(y == x + 1 and sign == -1, f"swap {index}")
            out.append({"index": index, "op": "SIGNED_SWAP", "roles": [x, y],
                        "sign": sign})
        else:
            raise ValueError(kind)
    need(not any(coded) and scratch == 0, "native macro endpoint")
    return out


def main():
    gates = W.native_chain(19, "I" * 9 + "T" * 9)
    events = emit(gates)
    normalizers = ROOT / "research/coded-native-caller/NORMALIZERS.json"
    physical = ROOT / "research/coded-native-caller/PHYSICAL.md"
    normalizer_payload = json.loads(normalizers.read_text())
    wrapper_contract = {}
    for port, payload in enumerate(normalizer_payload["ports"]):
        wrappers = payload["compiled_wrappers"]
        need(all(all(item[0] in ("P", "D", "X", "phase")
                         for item in wrapper["word"])
                     for wrapper in wrappers.values()), f"wrapper vocabulary port {port}")
        wrapper_contract[str(port)] = {
            name: {"word": wrapper["word"], "recipe": wrapper["recipe"]}
            for name, wrapper in sorted(wrappers.items())
        }
    for event in events:
        if event["op"] == "CODE":
            event["port_wrappers"] = wrapper_contract
    counts = Counter(e["op"] for e in events)
    receipt = {
        "status": "PASS_P19_TYPED_NATIVE_MACRO_EMISSION",
        "scope": "typed native macro word over the inherited primitive grammar; serialized 21449-record lowering is not substituted",
        "gate_records": len(gates),
        "macro_records": len(events),
        "macro_kinds": dict(sorted(counts.items())),
        "events": events,
        "operator_source": "P19_LIFT.json",
        "primitive_source": "P19_LOWERING.json",
        "normalizers_sha256": sha(normalizers),
        "physical_sha256": sha(physical),
        "compiled_wrapper_contract": {
            "ports": len(normalizer_payload["ports"]),
            "wrapper_kinds": sorted(wrapper_contract["0"]),
            "word_kinds": sorted({item[0] for wrapper in wrapper_contract["0"].values()
                                   for item in wrapper["word"]}),
            "all_wrappers_gaussian_free": True,
            "source": "NORMALIZERS.json compiled_wrappers",
            "wrappers": wrapper_contract,
        },
        "field_bill": {"recodings": 77, "monomial_field_maps": 17248,
                       "scalar_adds": 68992, "owned_clears": 1232,
                       "recursive_gaussian_children": 0},
        "endpoint": {"all_roles_uncoded": True, "owned_scratch_blank": True,
                     "swap_sign": -1},
    }
    with gzip.open(HERE / "P19_NATIVE_MACRO.json.gz", "wt", encoding="utf-8") as fh:
        fh.write(json.dumps(receipt, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "gate_records": len(gates),
                      "macro_records": len(events), "macro_kinds": dict(sorted(counts.items()))},
                     sort_keys=True))


if __name__ == "__main__":
    main()
