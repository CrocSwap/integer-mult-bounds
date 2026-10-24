#!/usr/bin/env python3
"""Bind both frozen low-displacement words to exact left-coded exits."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
LIB = LANES / "oblique-native-20261017/matched-left-gauge/emit_left_gauge.py"
LIB_PIN = "cb8c0880051b24175d2b84080f51ad65a12e85755b6237e7439d12576ffe9bbf"
PINS = {
    "native-normal-v2/NATIVE-PROGRAM.json.gz":
        "e387b082422f085efc8122497cdda0b5211a86b0418af4b9fdbc1da15ac71558",
    "odd16-normal-v2/EXTENSION-PROGRAM.json.gz":
        "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
    "run-normal/RESPONSE-PROGRAM.json":
        "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
}
CYCLIC = LANES / "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json"
CYCLIC_PIN = "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585"
if sha256(LIB.read_bytes()).hexdigest() != LIB_PIN:
    raise ValueError("Frozen exit compiler pin")
spec = importlib.util.spec_from_file_location("low_coded_exit", LIB)
g = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = g
spec.loader.exec_module(g)
need = g.need


def read(relative):
    raw = (HERE / relative).read_bytes()
    if relative.endswith(".gz"):
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == PINS[relative], "Frozen input " + relative)
    return json.loads(raw)


def translate(old, pairs):
    word = dict(old)
    events = []
    for event in old["events"]:
        if event[0] != "scalar":
            need(event[0] == "native", "Raw input event type")
            events.append(event)
            continue
        op, target, source, coefficient = event[1]
        c = F(coefficient)
        gate = ([op, target, c.numerator, c.denominator] if op == "scale"
                else [op, target, source, c.numerator, c.denominator])
        events.append(["scalar", gate, event[2]])
    word["events"] = events
    word["pair_codes"] = pairs
    return word


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    native = read("native-normal-v2/NATIVE-PROGRAM.json.gz")
    odd = read("odd16-normal-v2/EXTENSION-PROGRAM.json.gz")
    model = read("run-normal/RESPONSE-PROGRAM.json")
    cyclic_raw = CYCLIC.read_bytes()
    need(sha256(cyclic_raw).hexdigest() == CYCLIC_PIN, "Pair geometry pin")
    cyclic = json.loads(cyclic_raw)
    gauge = g.read("coherent-port/isotropic-pair-gauge-20261018/GAUGE-PROGRAMS.json")
    scalar_phase = g.u.compiler.diag(9, (1, 0, 0, 0, 0, 0, 0, 0, 0))
    W = scalar_phase.then(g.u.compiler.cgate(9, 45)).then(scalar_phase)
    need(json.loads(json.dumps(W.circuit)) == gauge["W"]["circuit"], "Exact pinned W circuit")
    W_circuit = tuple(tuple(tuple(v) if isinstance(v, list) else v for v in event)
                      for event in gauge["W"]["circuit"])
    g.u.phase.equal(g.u.phase.recipe(gauge["W"]["native_recipe"]), W_circuit, "Pinned W phase")
    large = set(model["large_ports"])
    inputs = {"rank30": (native["providers"], native["response"]),
              "rank16": (odd["providers"], odd["model"]["response"])}
    programs, receipts = {}, {}
    for name, (providers, response_strings) in inputs.items():
        response = g.rational_rows(response_strings)
        programs[name], receipts[name] = {}, {}
        for family, coded in (("W48_I64", large), ("W112", set(range(112)))):
            programs[name][family], receipts[name][family] = {}, {}
            for provider, words in providers.items():
                programs[name][family][provider], receipts[name][family][provider] = {}, {}
                for direction, old in words.items():
                    translated = translate(old, cyclic["pair_codes"])
                    g.replay(translated, response, direction)
                    word, receipt = g.build(translated, cyclic["ports"], coded, W, W_circuit,
                                            response, direction)
                    g.replay(word, response, direction)
                    need(receipt["real_scalar_primitives"] == (5288 if name == "rank30" else 7384),
                         "Unchanged complete scalar invoice")
                    expected = {
                        ("rank30", "W48_I64"): {1: 988, 2: 48, 4: 55, 5: 55, 6: 9, 7: 9},
                        ("rank30", "W112"): {1: 988, 2: 48, 5: 55, 6: 55, 7: 9, 8: 9},
                        ("rank16", "W48_I64"): {1: 1472, 2: 112},
                        ("rank16", "W112"): {1: 1408, 2: 112, 3: 64},
                    }[name, family]
                    need(receipt["profile"] == expected, "Exact changed-exit profile")
                    need(receipt["native_mass"] == (1696 if family == "W48_I64" else 1824),
                         "Exact changed-exit native mass")
                    need(receipt["all_input_columns"] == 640 and receipt["inline_monomial_maps"] == 48,
                         "All columns and priced zero-rank exits")
                    programs[name][family][provider][direction] = word
                    receipts[name][family][provider][direction] = receipt
            print(name, family, receipts[name][family]["base"]["forward"], flush=True)
    payload = {"schema": "low-displacement-coded-exits-v1", "source_pins": PINS,
               "responses": {"rank30": native["response"], "rank16": odd["model"]["response"]},
               "providers_by_response_and_code": programs}
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(raw)
    for name, families in saved["providers_by_response_and_code"].items():
        response = g.rational_rows(saved["responses"][name])
        for providers in families.values():
            for words in providers.values():
                for direction, word in words.items():
                    g.replay(word, response, direction)
    (args.out / "CODED-EXITS-PROGRAM.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    checks = {
        "status": "PASS_LOW_DISPLACEMENT_CODED_EXITS", "source_pins": PINS,
        "exit_compiler_sha256": LIB_PIN, "exit_compiler_source_pins": g.PINS,
        "cyclic_geometry_sha256": CYCLIC_PIN,
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(raw).hexdigest(),
        "fresh_changed_exit_phases": len(g.PHASE_CACHE), "receipts": receipts,
        "scope": "Exact changed output representations. No free decoder, stage transport, helper progress or complete supplier claim.",
    }
    (args.out / "CODED-EXITS-CHECKS.json").write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n")
    print(checks["status"], checks["payload_decompressed_sha256"], flush=True)


if __name__ == "__main__":
    main()
