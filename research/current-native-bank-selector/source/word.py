"""Apply the published edits to the pinned parent word."""
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
PARENT = "f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669"
CANDIDATE = "f95eabd1734c7a74f58428cb12f261a81032bef01aed78c8147a4e4f90636939"


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def words():
    raw = gzip.decompress((HERE / "data/source-word.json.gz").read_bytes())
    need(sha256(raw).hexdigest() == PARENT, "parent word digest")
    parent = json.loads(raw)
    edit = json.loads((HERE / "EDIT.json").read_bytes())
    result = dict(parent, frames=parent["frames"] + edit["append_frames"])
    for side in ("initial", "final"):
        result[side] = parent[side].copy()
        for role, old, new in edit[side]:
            need(result[side][role] == old, "boundary edit origin")
            result[side][role] = new
    start = 0
    program = []
    for item in edit["events"]:
        at = item["at"]
        need(start <= at < len(parent["program"]), "edit order")
        need(parent["program"][at] == item["old"], "edit origin")
        program.extend(parent["program"][start:at])
        program.extend(item["new"])
        start = at + 1
    program.extend(parent["program"][start:])
    result["program"] = program
    need(sha256(encoded(result)).hexdigest() == CANDIDATE, "candidate word digest")
    return parent, result


def main_roles(word):
    hosted = word["hosted"]
    return set(word["live"]) | {r + 112 for r in word["live"]} | set(hosted["X2"]) | set(hosted["Y2"])


def catalogue(word):
    paid = {(e[2], e[3]) for e in word["program"] if e[0] == "MOVE"}
    main = main_roles(word)
    helpers = {(u, v) for r, (u, v) in enumerate(zip(word["initial"], word["final"], strict=True)) if r not in main}
    return paid | helpers
