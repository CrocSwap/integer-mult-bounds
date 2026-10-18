"""I/O and exact source admission, with no search or proof code. Apache-2.0."""
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/"
WORD = PROVIDER + "CANONICAL-WORD.json.gz"
PROGRAMS = PROVIDER + "LOCAL-PROGRAMS.json.gz"
CHECKS = PROVIDER + "LOCAL-CHECKS.json"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"
RECIPE = "research/complex-ck-target-forest/RECIPE.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def invalid(value):
    raise ValueError("nonfinite JSON: " + value)


def load(path):
    path = Path(path)
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)


def write(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def same(a, b, message):
    need(canonical(a) == canonical(b), message)


def inputs(root):
    root = Path(root)
    manifest = load(HERE / "SOURCES.json")
    for name, pin in manifest["files"].items():
        data = (root / name).read_bytes()
        if pin["encoding"] == "gzip-payload":
            data = gzip.decompress(data)
        need(hashlib.sha256(data).hexdigest() == pin["sha256"], "source pin: " + name)
    word, programs, checks, spec, recipe = (load(root / name) for name in (WORD, PROGRAMS, CHECKS, SPEC, RECIPE))
    provider = spec["providers"]["ck"]
    for filename, obj in (("CANONICAL-WORD.json.gz", word), ("LOCAL-PROGRAMS.json.gz", programs)):
        need(digest(obj) == provider["artifact_semantic_sha256"][filename], "historical SPEC binding")
    need(set(programs) == {"forward", "backward"}, "both program orientations")
    for orientation, events in programs.items():
        need(digest(events) == provider["program_hashes"][orientation] == checks[orientation]["sha256"],
             "program source binding")
    need((word["v"], word["R"], word["h"]) == (112, 492, 9), "CK dimensions")
    return word, programs, checks, recipe, manifest
