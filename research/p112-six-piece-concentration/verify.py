#!/usr/bin/env python3
"""Source-bound six-piece concentration replay. Apache-2.0."""

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model  # noqa: E402

PINS = {
    3278: (
        "67280b1da48a14435d7fde3ec81314c768a8dd3e",
        "e3f722da7cca7d89dbc38796be5c175f78f78dd5d52036cdd0fbc33cf3c39086",
        "inherited-premises",
        "research/p112-mixed-support39/PROOF.md",
    ),
    3282: (
        "9607079de93907d87e6430d6de154f21a66c03e4",
        "66fad2325fb51fa6d04ef1787730b5cca915e82df5c5cf14b14e49b13e294025",
        "caller-context",
        "research/p112-b6-t4-reconciliation/PROOF.md",
    ),
}


def authenticate_predecessors(directory=HERE):
    manifest = model.read_json(directory / "PREDECESSORS.json")
    model.require(
        type(manifest) is dict
        and manifest.get("schema") == "p112-six-piece-predecessors/v1",
        "predecessor schema",
    )
    rows = manifest.get("files")
    model.require(
        type(rows) is list
        and len(rows) == 2
        and all(type(row) is dict for row in rows),
        "predecessor inventory",
    )
    model.require([row.get("pr") for row in rows] == sorted(PINS), "predecessor IDs")
    paths = []
    for row in rows:
        pr = row["pr"]
        head, digest, usage, origin = PINS[pr]
        name = f"predecessors/PR{pr}-PROOF.md"
        model.require(
            row.get("commit") == head
            and row.get("sha256") == digest
            and row.get("retained_path") == name
            and row.get("usage") == usage
            and row.get("source_path") == origin
            and row.get("url")
            == f"https://github.com/CrocSwap/integer-mult-bounds/pull/{pr}",
            "predecessor pin and usage",
        )
        path = directory / name
        model.require(
            path.is_file() and not path.is_symlink() and path.stat().st_size <= 262144,
            "bounded regular predecessor",
        )
        model.require(
            hashlib.sha256(path.read_bytes()).hexdigest() == digest, "predecessor bytes"
        )
        paths.append(path)
    model.require(
        set((directory / "predecessors").iterdir()) == set(paths),
        "predecessor file inventory",
    )


def main():
    model.require(not sys.argv[1:], "no command-line arguments accepted")
    authenticate_predecessors()
    observed = model.result()
    model.require(
        observed == model.read_json(HERE / "RESULT.json"), "six-piece result differs"
    )
    print("PASS_SIX_PIECE_CONCENTRATION profile=4,5^3,6^6 excluded no_new_kappa")


if __name__ == "__main__":
    main()
