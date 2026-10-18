"""Bounded model and fixed source inventory. Nick Petalas, Apache-2.0."""

import hashlib
import json
import runpy
from pathlib import Path
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
BASE = "463113d675af7410ac91d53a4fed51ec6494eb9a"
INVENTORY = {
    "certificates/selected-result.json": "provenance",
    "docs/research/agent-task-catalog.json": "provenance",
    GEOMETRY: "input",
}
RETAINED = {"vendor/pr3267-PROOF.md", "vendor/pr3267-RESULT.json"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_bytes(path):
    require(path.is_file() and not path.is_symlink(), "regular source file")
    require(path.stat().st_size <= 100000, "bounded source file")
    return path.read_bytes()


def authenticate(package=PACKAGE, root=ROOT):
    source = json.loads(bounded_bytes(package / "SOURCES.json"))
    require(
        set(source) == {"schema_version", "base_commit", "files", "retained_files"},
        "source manifest schema",
    )
    require(
        source["schema_version"] == 1 and source["base_commit"] == BASE, "source base"
    )
    rows, retained = source["files"], source["retained_files"]
    require(type(rows) is list and len(rows) == 3, "source inventory length")
    require(type(retained) is list and len(retained) == 2, "retained inventory length")
    require({r["path"] for r in rows} == set(INVENTORY), "fixed source paths")
    require({r["local_path"] for r in retained} == RETAINED, "fixed retained paths")
    for row in rows:
        require(
            set(row) == {"path", "usage", "git_blob", "sha256"}, "source row schema"
        )
        require(row["usage"] == INVENTORY[row["path"]], "source usage")
    for row in retained:
        require(
            set(row)
            == {
                "local_path",
                "usage",
                "source_commit",
                "source_path",
                "git_blob",
                "sha256",
            },
            "retained row schema",
        )
        require(row["usage"] == "attribution", "retained usage")
        require(
            row["source_commit"] == "008f042859a5183d1323228a68aa1038f8d7718a",
            "retained source commit",
        )
        name = row["local_path"].removeprefix("vendor/pr3267-")
        require(
            row["source_path"] == "research/p112-mixed-support38/" + name,
            "retained source path",
        )
    for row in [r for r in rows if r["usage"] == "input"] + retained:
        path = root / row["path"] if "path" in row else package / row["local_path"]
        raw = bounded_bytes(path)
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == row["git_blob"], "source Git blob")
    return source


def geometry():
    authenticate()
    return SimpleNamespace(**runpy.run_path(str(ROOT / GEOMETRY)))


def basis(values, bits=9):
    require(len(values) <= 512 and 1 <= bits <= 18, "binary capacity")
    rows = []
    for value in values:
        require(type(value) is int and 0 <= value < 1 << bits, "binary label")
        for row in rows:
            value = min(value, value ^ row)
        if value:
            rows = sorted(
                [min(row, row ^ value) for row in rows] + [value], reverse=True
            )
    return tuple(rows)


def span(values):
    rows = basis(values)
    result = {0}
    for row in rows:
        result.update(x ^ row for x in tuple(result))
    require(len(result) == 1 << len(rows), "independent binary basis")
    return result


def coordinate_map(values):
    rows = basis(values)
    mapping = {0: 0}
    for j, row in enumerate(rows):
        mapping.update({x ^ row: y | (1 << j) for x, y in tuple(mapping.items())})
    return mapping


def quadratic(gram, label):
    x = label >> 1
    return (
        x.bit_count()
        + sum(
            gram[i][j] * ((x >> i) & 1) * ((x >> j) & 1)
            for i in range(8)
            for j in range(i + 1, 8)
        )
    ) % 2


def polar(gram, x, y):
    return quadratic(gram, x ^ y) ^ quadratic(gram, x) ^ quadratic(gram, y)
