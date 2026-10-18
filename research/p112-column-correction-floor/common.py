"""Package integrity and strict, deterministic receipts. Apache-2.0.

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {"research/p112-single-lift/geometry.py",
          "research/complex-frame-pair-decoders/PROOF.md"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def strict_load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    def bad_constant(value):
        raise ValueError("nonfinite JSON: " + value)

    return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=bad_constant)


def sources(root=ROOT, manifest=None):
    manifest = strict_load(HERE / "SOURCES.json") if manifest is None else manifest
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    need(len(rows) == len(INPUTS) and {r["path"] for r in rows} == INPUTS,
         "complete live source inventory")
    for row in rows:
        data = (Path(root) / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"],
             "source bytes: " + row["path"])
    return [{"path": r["path"], "sha256": r["sha256"]}
            for r in sorted(rows, key=lambda r: r["path"])]


def same(actual, expected, message):
    # Typed canonical equality rejects True for 1 and 1.0 for 1 as well.
    need(canonical(actual) == canonical(expected), message)


def write_new(path, value):
    with Path(path).open("x") as stream:
        stream.write(json.dumps(value, sort_keys=True, indent=2) + "\n")
