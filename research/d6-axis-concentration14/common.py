"""Bounded source authentication and binary arithmetic. Apache-2.0."""

import hashlib
import json
import runpy
from pathlib import Path
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "463113d675af7410ac91d53a4fed51ec6494eb9a"
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_json(path, limit=100_000):
    require(not path.is_symlink() and path.is_file(), "regular source required")
    raw = path.read_bytes()
    require(len(raw) <= limit, "source size bound")
    return json.loads(raw)


def authenticate():
    manifest = read_json(PACKAGE / "SOURCES.json")
    require(type(manifest["schema_version"]) is int, "schema type")
    require(
        manifest["schema_version"] == 1 and manifest["base_commit"] == BASE,
        "base/schema",
    )
    expected = {
        GEOMETRY: "input",
        "certificates/selected-result.json": "provenance",
        "docs/research/agent-task-catalog.json": "provenance",
    }
    rows = manifest["files"]
    require(type(rows) is list and len(rows) == 3, "source inventory")
    require({r["path"]: r["usage"] for r in rows} == expected, "source usage/inventory")
    row = next(r for r in rows if r["path"] == GEOMETRY)
    raw = (ROOT / GEOMETRY).read_bytes()
    require(len(raw) < 100_000, "geometry size")
    require(not (ROOT / GEOMETRY).is_symlink(), "linked geometry")
    require(hashlib.sha256(raw).hexdigest() == row["sha256"], "geometry SHA256")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    require(
        hashlib.sha1(blob, usedforsecurity=False).hexdigest() == row["git_blob"],
        "geometry blob",
    )
    predecessors = read_json(PACKAGE / "PREDECESSORS.json")
    require(
        type(predecessors["schema_version"]) is int
        and predecessors["schema_version"] == 1,
        "predecessor schema",
    )
    require(len(predecessors["files"]) == 2, "predecessor inventory")
    require(
        {r["path"] for r in predecessors["files"]}
        == {"vendor/pr3292-PROOF.md", "vendor/pr3295-PROOF.md"},
        "predecessor paths",
    )
    for entry in predecessors["files"]:
        require(entry["usage"] == "provenance", "predecessor usage")
        data = (PACKAGE / entry["path"]).read_bytes()
        require(
            len(data) < 30_000 and hashlib.sha256(data).hexdigest() == entry["sha256"],
            "predecessor bytes",
        )
    return SimpleNamespace(**runpy.run_path(str(ROOT / GEOMETRY)))


def basis(values, bits=9):
    rows = [0] * bits
    for value in values:
        require(type(value) is int and 0 <= value < 1 << bits, "binary vector")
        for pivot in range(bits - 1, -1, -1):
            if value >> pivot & 1:
                if rows[pivot]:
                    value ^= rows[pivot]
                else:
                    rows[pivot] = value
                    break
    return tuple(v for v in reversed(rows) if v)


def span(values):
    reduced = basis(values)
    result = {0}
    for value in reduced:
        result |= {x ^ value for x in result}
    require(len(result) <= 512, "span bound")
    return result


def coordinates(values):
    result = {0: 0}
    for j, value in enumerate(basis(values)):
        result.update({x ^ value: y | (1 << j) for x, y in tuple(result.items())})
    return result


def quadratic(gram, x):
    value = (x >> 1).bit_count()
    for i in range(8):
        for j in range(i + 1, 8):
            value += gram[i][j] * ((x >> (i + 1)) & 1) * ((x >> (j + 1)) & 1)
    return value % 2


def polar(gram, x, y):
    return quadratic(gram, x ^ y) ^ quadratic(gram, x) ^ quadratic(gram, y)


def root_data():
    g = authenticate()
    roots, _, _, coefficients = g.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(c)) for c in coefficients
    )
    require(len(set(labels)) == 120, "full root-label bijection")
    return g, roots, labels
