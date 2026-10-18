"""Source binding and serialization; no frame or optimization mathematics.

Adapted from Gareth Davidson PR1671 (11fbeaf34609147c124323c2f5e74fc450dad931).
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
BASE = "15d2aca0385b61596155e8421140d08d27e543af"
WORD_SHA = "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8"
PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
INPUTS = {
    "research/r480-owner-optimum/inputs/local/FULL-WORD.json.gz": "WORD.json.gz",
    "research/gauge44-slots/construction/slots/SLOT-PINS-k8.json": "SLOT-PINS.json",
    "research/complex-x4-frame-bound/model.py": "frame_model.py",
    "research/complex-x4-frame-bound/gen_duals.py": "gen_duals.py",
    "research/complex-x4-frame-bound/README.md": "FRAME-METHOD.md",
    "research/complex-local-word-ceiling/ceiling.py": "ceiling.py",
    "research/complex-local-word-ceiling/README.md": "CEILING.md",
    "research/gauge44-slots/independent/audit_local.py": "audit_local.py",
    "research/k8-rank7-composition/data/END-RECIPE.json": "END-RECIPE.json",
    "research/k8-rank7-composition/construct.py": "construct.py",
    "research/k8-rank7-composition/README.md": "END-WITNESS.md",
    "research/selected1042-lineage-resolution98/README.md": "WORD-LINEAGE.md"
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    def bad(value):
        raise ValueError("noninteger/nonfinite JSON number: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_float=bad, parse_constant=bad)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def source_bindings():
    need(parse((HERE / "INPUTS.json").read_bytes()) == INPUTS, "input mapping")
    data = parse((HERE / "SOURCES.json").read_bytes())
    provenance = {"certificates/selected-result.json", "docs/research/agent-task-catalog.json"}
    need(data["base_commit"] == BASE, "source base")
    need(len(data["files"]) == len(INPUTS) + 2 and
         {r["path"] for r in data["files"]} == set(INPUTS) | provenance, "source inventory")
    for row in data["files"]:
        path = row["path"]
        need(row["usage"] == ("input" if path in INPUTS else "provenance"), "source role")
        if path not in INPUTS:
            continue
        raw = (HERE / "references" / INPUTS[path]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "retained source SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == row["git_blob"], "retained source Git blob")
        live = HERE.parents[1] / path
        if live.exists():
            need(live.read_bytes() == raw, "live mathematical source drift")


def retained(name):
    """Keep the retained source's guards active even when the caller uses -O."""
    path = HERE / "references" / name
    result = types.ModuleType("retained_" + path.stem)
    result.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), result.__dict__)
    return result


def word():
    raw = gzip.decompress((HERE / "references/WORD.json.gz").read_bytes())
    pins = parse((HERE / "references/SLOT-PINS.json").read_bytes())
    need(hashlib.sha256(raw).hexdigest() == pins["word_sha256"] == WORD_SHA, "selected word content pin")
    data = parse(raw)
    need({int(r): n for r, n in data["report"]["local_profile"].items()} == PROFILE, "baseline local profile")
    need(data["report"]["R"] == 480 and data["report"]["h"] == 9 and data["report"]["v"] == 112,
         "selected word dimensions")
    need(sum(r*n for r, n in PROFILE.items()) == 5586, "local rank mass")
    return data


def duals():
    raw = gzip.decompress((HERE / "DUALS.json.gz").read_bytes())
    data = parse(raw)
    need(data["schema"] == "selected-k8-contracted-end-duals-v1" and data["word_sha256"] == WORD_SHA,
         "dual word binding")
    return data


def primal_data():
    return parse(gzip.decompress((HERE / "PRIMAL.json.gz").read_bytes()))
