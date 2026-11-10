#!/usr/bin/env python3
"""Regenerate four frozen producer recipes; this is not the independent checker."""
import argparse
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent
PINNED = {
    "sources/NOTICE": [
        "6c5f4a452f7d65ef8ca0980992dce279938b0a1139f6c067f91de78bf8ecb7bd",
        "e6cae17f778e8e31b7c294ff2890c545978931c0"
    ],
    "sources/WORD.json.gz": [
        "0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928",
        "03ea7690285d4cda72815f962d5710ab96e08490"
    ],
    "sources/clifford_exact.py": [
        "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
        "166841a037f069249f6f7f6dedb89248812f59e2"
    ],
    "sources/integration-source.py": [
        "7201df8e32f5c99f7403150e8664042322037906088bc754c67293a241368597",
        "b7be846b10c4c54a4e1558d7b563bc8c3a170223"
    ],
    "sources/native-channel-PROOF.md": [
        "5d743145d389ffdfaffc66096fa7e32c7155b18f73d74755403151d0435bb94c",
        "a69311b74f74a2f8e8f411c1451baacd9bacddce"
    ]
}
CASES = [
    ("move-712-1094", "move", 712, 1094, [703], [12917]),
    ("move-714-1094", "move", 714, 1094, [704], [12930]),
    ("move-1094-127", "move", 1094, 127, [704], [12932]),
    ("helper-3-1094", "helper", 3, 1094, [703], []),
]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def authenticate():
    authenticated = {}
    for filename, (digest, blob) in PINNED.items():
        raw = (HERE / filename).read_bytes()
        require(sha256(raw).hexdigest() == digest, "source SHA256: " + filename)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "source Git blob: " + filename)
        authenticated[filename] = raw
    return authenticated


def span(vectors):
    result = {0}
    for vector in vectors:
        require(type(vector) is int and 0 < vector < 512 and vector not in result, "independent frame")
        result |= {point ^ vector for point in tuple(result)}
    return result


def produce():
    authenticated = authenticate()
    word = json.loads(gzip.decompress(authenticated["sources/WORD.json.gz"]))
    frames = word["frames"]
    require(len(frames) == 1095 and frames[1094] == [7, 9, 35, 66, 400], "frozen new frame")
    new_span = span(frames[1094])
    equivalence = {
        "basis": frames[1094], "rank": 5,
        "older_exact_basis_matches": [i for i, frame in enumerate(frames[:1094]) if frame == frames[1094]],
        "older_span_matches": [i for i, frame in enumerate(frames[:1094]) if span(frame) == new_span],
    }
    actual_moves = [(i, e[1], e[2], e[3]) for i, e in enumerate(word["program"])
                    if e[0] == "MOVE" and 1094 in e[2:4]]
    require(actual_moves == [(12917, 703, 712, 1094), (12930, 704, 714, 1094),
                             (12932, 704, 1094, 127)], "complete new-frame MOVE footprint")
    main = set(word["live"]) | {r + 112 for r in word["live"]}
    helpers = [(r, word["initial"][r], word["final"][r]) for r in range(word["public"])
               if r not in main and 1094 in (word["initial"][r], word["final"][r])]
    require(helpers == [(703, 3, 1094)], "complete new-frame helper footprint")
    # Only this frozen producer is executed; integration/native checker files are data.
    compiler = ModuleType("frozen_frame1094_compiler")
    compiler.__file__ = str(HERE / "sources/clifford_exact.py")
    sys.modules[compiler.__name__] = compiler
    exec(compile(authenticated["sources/clifford_exact.py"], compiler.__file__, "exec"), compiler.__dict__)
    tasks = []
    for label, kind, a, b, roles, indices in CASES:
        recipe, _ = compiler.lower_child(
            compiler.canonical_frame(9, tuple(frames[a])).adjoint().then(
                compiler.canonical_frame(9, tuple(frames[b]))))
        require(type(recipe["rank"]) is int and recipe["rank"] == abs(len(frames[a]) - len(frames[b])),
                "producer native rank")
        tasks.append({"id": label, "kind": kind, "source_frame": a, "target_frame": b,
                      "roles": roles, "event_indices": indices, "recipe": recipe})
    return {"schema_version": 1, "word_sha256": PINNED["sources/WORD.json.gz"][0],
            "compiler_sha256": PINNED["sources/clifford_exact.py"][0],
            "frame1094": equivalence, "tasks": tasks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--emit", action="store_true", help="emit regenerated JSON without comparison")
    mode.add_argument("--check", action="store_true", help="require the retained recipe receipt (default)")
    options = parser.parse_args()
    result = produce()
    if not options.emit:
        retained = HERE / "RECIPES.json"
        require(retained.is_file(), "retained RECIPES.json receipt must exist")
        require(canonical(json.loads(retained.read_bytes())) == canonical(result),
                "exact typed regenerated RECIPES.json receipt")
    print(json.dumps(result, sort_keys=True, indent=2))
