#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent finite Hall/face check; no solver or predecessor code imports.

Ross Richardson, with substantial OpenAI Codex assistance.  Separate AI
mathematical checks are not independent human review or a formal-kernel proof.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = "be191346391661f4d35fc0d1508d0a6029572576"
BASE = "30f016dd79ee6a23c40d7dab44a9466c148c42dd"


def require(value, reason):
    if not value:
        raise ValueError(reason)


def check_payload(row, raw):
    require(hashlib.sha256(raw).hexdigest() == row["sha256"],
            "frozen source SHA256: " + row["export_path"])
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(blob == row["git_blob"], "frozen source Git blob: " + row["export_path"])
    require(len(raw) == row["bytes"], "frozen source byte count")


def check_sources(root):
    manifest = json.loads((root / "SOURCES.json").read_text())
    require(manifest["source_commit"] == SOURCE and manifest["base_commit"] == BASE,
            "exact scientific pins")
    rows = [row for row in manifest["files"] if "export_path" in row]
    require(len(rows) == 19, "complete frozen evidence subset")
    names = set()
    for row in rows:
        name = row["export_path"]
        path = root / name
        require(name.startswith("sources/") and name not in names and
                path.resolve().is_relative_to((root / "sources").resolve()) and
                path.is_file() and not path.is_symlink(), "unique local frozen source")
        require(row["pin"] == "head:" + SOURCE + ":" + row["path"], "source commit binding")
        names.add(name)
        check_payload(row, path.read_bytes())
    actual = {p.relative_to(root).as_posix() for p in (root / "sources").rglob("*") if p.is_file()}
    require(actual == names, "no unpinned frozen files")
    row = rows[0]
    raw = (root / row["export_path"]).read_bytes()
    bad = bytes([raw[0] ^ 1]) + raw[1:]
    try:
        check_payload(row, bad)
    except ValueError as exc:
        require(str(exc).startswith("frozen source SHA256:"), "source drift rejection reason")
    else:
        raise ValueError("accepted frozen source corruption")
    return {"files": len(rows), "bytes": sum(row["bytes"] for row in rows),
            "source_commit": SOURCE, "manifest_sha256": hashlib.sha256(
                (root / "SOURCES.json").read_bytes()).hexdigest(),
            "controls": ["changed frozen byte rejected before mathematical checks"]}


def source_module(root, name):
    """Load the two new implementations directly from source, without a pyc."""
    path = root / name
    namespace = {"__name__": name[:-3], "__file__": str(path)}
    exec(compile(path.read_bytes(), str(path), "exec"), namespace)
    return namespace


def verify(root=ROOT):
    root = Path(root)
    sources = check_sources(root)
    hall = source_module(root, "independent_hall.py")["verify_hall"](root)
    face = source_module(root, "independent_face.py")["verify_face"](root)
    require(hall["literal_witness"]["conditional_complete_profile"] == face["T74_profile"],
            "literal provider invoice equals independent pattern invoice")
    require(hall["literal_witness"]["idle_profile"] ==
            {rank: 2 * count for rank, count in face["T37"]["idle"].items()},
            "literal idle ranks equal doubled independent pattern ranks")
    require(hall["face_family"]["integer_k_inclusive"] ==
            [face["integer_family"]["first"], face["integer_family"]["last"]],
            "identical mathematical family in both independent checks")
    require(check_sources(root) == sources, "frozen evidence unchanged during replay")
    result = {"status": "PASS_RANK7_CHRONOLOGICAL_FACE_NO_NEW_KAPPA",
              "sources": sources, "hall": hall, "face": face,
              "scope": "Finite source-bound interval obstruction, pattern-family identity and "
                       "literal owner geometry conditional on the supplied native width registry; "
                       "no native residual, precision, outer, all-size or new-kappa admission."}
    # The independent counters use integer keys; the receipt has JSON keys.
    return json.loads(json.dumps(result, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-result", action="store_true")
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    require(not (args.check_result and args.write_result), "choose one result mode")
    result = verify()
    if args.check_result:
        require(result == json.loads((ROOT / "RESULT.json").read_text()), "recorded result matches replay")
    if args.write_result:
        (ROOT / "RESULT.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
