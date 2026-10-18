"""Authenticate the fixed input/provenance inventory before source import."""

import json
from hashlib import sha1, sha256
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "463113d675af7410ac91d53a4fed51ec6494eb9a"
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
USAGE = {
    "certificates/selected-result.json": "provenance",
    "docs/research/agent-task-catalog.json": "provenance",
    GEOMETRY: "input",
}
RETAINED = {
    "vendor/PR3266-PROOF.md": (
        "3c4e9dc1a3f1b722bd0db867ecfba17d746816d8",
        "research/p112-rank5-support46/PROOF.md",
    ),
    "vendor/PR3266-RESULT.json": (
        "3c4e9dc1a3f1b722bd0db867ecfba17d746816d8",
        "research/p112-rank5-support46/RESULT.json",
    ),
    "vendor/PR3269-PROOF.md": (
        "ebe02d33157dc6c6d3b35df204e4a39242b7429e",
        "research/e8-quadratic-support-capacity/PROOF.md",
    ),
    "vendor/PR3269-RESULT.json": (
        "ebe02d33157dc6c6d3b35df204e4a39242b7429e",
        "research/e8-quadratic-support-capacity/RESULT.json",
    ),
    "vendor/PR3249-PROOF.md": (
        "22c7bf316d55e59f381cc9ba833afccc7702fd58",
        "research/p112-a2-rank5-shortening/PROOF.md",
    ),
    "vendor/PR3249-RESULT.json": (
        "22c7bf316d55e59f381cc9ba833afccc7702fd58",
        "research/p112-a2-rank5-shortening/RESULT.json",
    ),
    "vendor/PR3257-PROOF.md": (
        "1499da8f88c4d0293fe3ae443d0c7fec80f0e2d7",
        "research/p112-a2-support45/PROOF.md",
    ),
    "vendor/PR3257-RESULT.json": (
        "1499da8f88c4d0293fe3ae443d0c7fec80f0e2d7",
        "research/p112-a2-support45/RESULT.json",
    ),
    "vendor/A2-PROOF.md": (
        "129eba68a1ae082ea65dffcfd93a1305165113e1",
        "research/e8-a2-joint-incidence20/PROOF.md",
    ),
    "vendor/A2-RESULT.json": (
        "129eba68a1ae082ea65dffcfd93a1305165113e1",
        "research/e8-a2-joint-incidence20/RESULT.json",
    ),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded(path):
    require(path.is_file() and not path.is_symlink(), "regular source required")
    with path.open("rb") as stream:
        data = stream.read(200001)
    require(len(data) <= 200000, "source size limit")
    return data


def check_digest(data, row):
    require(sha256(data).hexdigest() == row["sha256"], "source SHA256")
    blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    require(blob == row["git_blob"], "source Git blob")


def authenticate(manifest=None):
    if manifest is None:
        manifest = json.loads(bounded(PACKAGE / "SOURCES.json"))
    require(
        set(manifest) == {"schema_version", "base_commit", "files", "retained_files"},
        "manifest schema",
    )
    require(
        manifest["schema_version"] == 1 and manifest["base_commit"] == BASE,
        "manifest base",
    )
    rows = manifest["files"]
    require(
        len(rows) == len(USAGE) and {r["path"] for r in rows} == set(USAGE),
        "pin inventory",
    )
    raw_geometry = b""
    for row in rows:
        require(set(row) == {"path", "usage", "git_blob", "sha256"}, "pin schema")
        require(row["usage"] == USAGE[row["path"]], "pin usage")
        if row["usage"] == "input":
            raw_geometry = bounded(ROOT / row["path"])
            check_digest(raw_geometry, row)
    retained = manifest["retained_files"]
    require(
        len(retained) == len(RETAINED)
        and {r["local_path"] for r in retained} == set(RETAINED),
        "retained inventory",
    )
    for row in retained:
        require(
            set(row)
            == {"local_path", "source_commit", "source_path", "git_blob", "sha256"},
            "retained schema",
        )
        require(
            (row["source_commit"], row["source_path"]) == RETAINED[row["local_path"]],
            "retained source mapping",
        )
        check_digest(bounded(PACKAGE / row["local_path"]), row)
    module = ModuleType("authenticated_p112_geometry")
    # Execute exactly the authenticated bytes without consulting a .pyc file.
    exec(compile(raw_geometry, GEOMETRY, "exec"), module.__dict__)
    return module
