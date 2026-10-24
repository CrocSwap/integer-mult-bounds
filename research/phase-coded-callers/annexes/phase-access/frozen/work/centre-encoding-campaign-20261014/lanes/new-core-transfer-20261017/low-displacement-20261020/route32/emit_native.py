#!/usr/bin/env python3
"""Emit the complete native data word for the route-compatible response."""

import argparse
from copy import deepcopy
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
EMITTER = PARENT / "emit_native.py"
EMITTER_PIN = "599987ddfe2fdb8fd4be533d783e24bf40a95b6c69118ec1552a10b06f1d5745"
MODEL = HERE / "model-normal/ROUTE32-MODEL.json"
MODEL_PIN = "85d44223697700a916e4cffeb334c8f82179f6535f7b0db64a37eddf37bedf52"
SOURCES = {
    PARENT / "native-normal-v2/NATIVE-PROGRAM.json.gz":
        "e387b082422f085efc8122497cdda0b5211a86b0418af4b9fdbc1da15ac71558",
    PARENT / "odd16-normal-v2/EXTENSION-PROGRAM.json.gz":
        "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4",
}


def need(test, message):
    if not test:
        raise ValueError(message)


need(sha256(EMITTER.read_bytes()).hexdigest() == EMITTER_PIN, "Frozen native emitter")
spec = importlib.util.spec_from_file_location("route32_native_helpers", EMITTER)
n = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = n
spec.loader.exec_module(n)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    need(sha256(MODEL.read_bytes()).hexdigest() == MODEL_PIN, "Frozen route-compatible model")
    model = json.loads(MODEL.read_bytes())
    cyclic = json.loads(n.read("independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json"))
    inherited = {}
    source = None
    for path, pin in SOURCES.items():
        raw = gzip.decompress(path.read_bytes())
        need(sha256(raw).hexdigest() == pin, "Native phase source pin")
        source = json.loads(raw)
        word = source["providers"]["base"]["forward"]
        for key, recipe in word["native_recipes"].items():
            old, new = map(int, key.split(":"))
            pair = tuple(word["frames"][old]), tuple(word["frames"][new])
            if pair in inherited:
                need(inherited[pair] == recipe, "Repeated exact recipe agrees")
            inherited[pair] = recipe
    base = source["providers"]["base"]["forward"]
    words = {direction: n.make_word(cyclic, model, direction) for direction in ("forward", "backward")}
    frames = words["forward"]["frames"]
    need(frames == words["backward"]["frames"], "Both orientations have identical actual frames")
    pairs = sorted({(event[2], event[3]) for word in words.values()
                    for event in word["events"] if event[0] == "native"})
    recipes, fresh, reused = {}, 0, 0
    for old, new in pairs:
        pair = tuple(frames[old]), tuple(frames[new])
        if pair in inherited:
            recipe = inherited[pair]
            reused += 1
        else:
            operation = n.compiler.canonical_frame(9, pair[0]).adjoint().then(
                n.compiler.canonical_frame(9, pair[1]))
            recipe, _ = n.compiler.lower_child(operation)
            n.phase.equal(n.phase.recipe(recipe), n.phase.adjoint(n.phase.frame(pair[0], 9))
                          + n.phase.frame(pair[1], 9), "Fresh route32 native phase")
            fresh += 1
            if fresh % 100 == 0:
                print("Fresh route32 phases", fresh, flush=True)
        need(recipe["rank"] == len(pair[1]) - len(pair[0]), "Exact new native rank")
        recipes[str(old) + ":" + str(new)] = recipe
    reports = {}
    for direction, word in words.items():
        word["native_recipes"] = recipes
        word["endpoint_adapters"] = base["endpoint_adapters"]
        need(word["start"] == base["start"] and word["final"] == base["final"],
             "Identical inherited endpoint indices")
        need(all(word["frames"][i] == base["frames"][i] for i in word["start"] + word["final"]),
             "Identical inherited endpoint bases")
        reports[direction] = n.verify_word(word, n.rows(model["response"]), direction)
        need(reports[direction]["native_profile"] == {1: 944, 3: 48, 5: 64, 6: 64}
             and reports[direction]["native_mass"] == 1792
             and reports[direction]["real_scalar_primitives"] == 4312, "Complete native invoice")
    bad = deepcopy(words["forward"])
    del bad["events"][bad["transfer_records"][0]["event"]]
    try:
        n.verify_word(bad, n.rows(model["response"]), "forward")
    except ValueError:
        pass
    else:
        raise ValueError("The missing transfer control was accepted")
    payload = {"schema": "route32-native-v1", "model": model,
               "providers": {provider: words for provider in source["providers"]}}
    data = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    saved = json.loads(data)
    for provider, directions in saved["providers"].items():
        for direction, word in directions.items():
            need(n.verify_word(word, n.rows(saved["model"]["response"]), direction) == reports[direction],
                 "Serialized complete native replay " + provider + " " + direction)
    (args.out / "ROUTE32-NATIVE.json.gz").write_bytes(gzip.compress(data, mtime=0))
    checks = {
        "status": "PASS_ROUTE32_COMPLETE_NATIVE",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "model_sha256": MODEL_PIN,
        "payload_decompressed_sha256": sha256(data).hexdigest(),
        "fresh_native_phases": fresh,
        "inherited_native_phases": reused,
        "inherited_endpoint_phases": 224,
        "reports": reports,
        "missing_transfer_rejected": True,
        "scope": "Complete local native data word. The416 other fields are unchanged. Productive helper progress, common-root conjugation, moving-code transitions and recursive hosting are separate.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n")
    print(json.dumps(checks, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
