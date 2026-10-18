#!/usr/bin/env python3
"""Recollect the bounded raw-Git proof for PR211. Needs the pinned source objects locally.

Fetch missing objects with:
  git fetch origin refs/pull/211/head
  git fetch origin tag archive/pr-reconciliation-next100-20261013
No network request or execution of archived code is made by this collector.
steph4n (@steph4n-gh), with substantial Google Gemini assistance. Apache-2.0.
"""
import argparse
import base64
import gzip
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import (
    ARCHIVE, CASCADE_DIR, CASCADE_WORKFLOW, FRAMES_B64_BLOB, FRAMES_BLOB,
    MERGE_BASE, PACKED_DIR, PACKED_WORKFLOW, PR205, PR210, PR210_FRAMES_PATH,
    PR210_NOTICE_PATH, PR211, PR217, PR217_FRAMES_B64_PATH, PR217_NOTICE_PATH,
    ROOT,
)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def collect():
    objects = {}

    def save(kind, oid):
        raw = git("cat-file", kind, oid)
        objects[oid] = {"type": kind, "base64": base64.b64encode(raw).decode("ascii")}
        return raw

    def tree(oid):
        save("tree", oid)
        result = {}
        for record in git("ls-tree", "-z", oid).split(b"\0"):
            if not record:
                continue
            meta, name = record.split(b"\t", 1)
            mode, kind, child = meta.decode("ascii").split()
            result[name.decode("utf-8")] = ("40000" if kind == "tree" else mode, kind, child)
        return result

    def commit(oid):
        save("commit", oid)
        return git("rev-parse", oid + "^{tree}").decode().strip()

    def resolve(oid, path):
        node = commit(oid)
        for part in path.split("/"):
            _, kind, node = tree(node)[part]
        return kind, node

    def inventory(oid, prefix=""):
        result = {}
        for name, (mode, kind, child) in tree(oid).items():
            path = prefix + name
            if kind == "tree":
                result.update(inventory(child, path + "/"))
            else:
                result[path] = {"mode": mode, "blob": child}
        return result

    def changed_trees(a, b):
        if a == b:
            return
        left, right = tree(a), tree(b)
        for name in set(left) | set(right):
            x, y = left.get(name), right.get(name)
            if x != y and x and y and x[1] == y[1] == "tree":
                changed_trees(x[2], y[2])

    t_mb = commit(MERGE_BASE)
    t_205 = commit(PR205)
    t_211 = commit(PR211)
    changed_trees(t_mb, t_205)
    changed_trees(t_205, t_211)
    changed_trees(t_mb, t_211)

    packed_205 = resolve(PR205, PACKED_DIR)[1]
    packed_211 = resolve(PR211, PACKED_DIR)[1]
    if packed_205 != packed_211:
        raise ValueError("inherited PR205 subtree differs in PR211")
    _, wf_205 = resolve(PR205, PACKED_WORKFLOW)
    _, wf_211 = resolve(PR211, PACKED_WORKFLOW)
    if wf_205 != wf_211:
        raise ValueError("inherited PR205 workflow differs in PR211")

    inherited_files = {PACKED_WORKFLOW: {"mode": "100644", "blob": wf_205}}
    for path, row in inventory(packed_205).items():
        inherited_files[PACKED_DIR + "/" + path] = row

    cascade_211 = resolve(PR211, CASCADE_DIR)[1]
    _, cwf_211 = resolve(PR211, CASCADE_WORKFLOW)
    direct_files = {CASCADE_WORKFLOW: {"mode": "100644", "blob": cwf_211}}
    for path, row in inventory(cascade_211).items():
        direct_files[CASCADE_DIR + "/" + path] = row

    _, frames_210 = resolve(PR210, PR210_FRAMES_PATH)
    if frames_210 != FRAMES_BLOB:
        raise ValueError("PR210 frames blob mismatch")
    resolve(PR210, PR210_NOTICE_PATH)

    _, b64_217 = resolve(PR217, PR217_FRAMES_B64_PATH)
    if b64_217 != FRAMES_B64_BLOB:
        raise ValueError("PR217 compressed frames blob mismatch")
    resolve(PR217, PR217_NOTICE_PATH)
    commit(ARCHIVE)

    b64_raw = save("blob", b64_217)
    _, c205_oid = resolve(PR205, PACKED_DIR + "/certificate.json")
    save("blob", c205_oid)
    for path, row in direct_files.items():
        if path != CASCADE_DIR + "/opframe-bases.json":
            save("blob", row["blob"])

    # Git-native full-byte comparison across all 25 paths and retained copies.
    for path in inherited_files:
        if git("show", PR211 + ":" + path) != git("show", PR205 + ":" + path):
            raise ValueError("inherited payload mismatch: " + path)
    raw_frames_211 = git("show", PR211 + ":" + CASCADE_DIR + "/opframe-bases.json")
    raw_frames_210 = git("show", PR210 + ":" + PR210_FRAMES_PATH)
    raw_frames_217 = gzip.decompress(base64.b64decode(b64_raw.rstrip(b"\n"), validate=True))
    if not (raw_frames_211 == raw_frames_210 == raw_frames_217):
        raise ValueError("opframe-bases.json payload mismatch across PR211/PR210/PR217")

    return {
        "schema_version": 1,
        "objects": dict(sorted(objects.items())),
        "inherited_files": dict(sorted(inherited_files.items())),
        "direct_files": dict(sorted(direct_files.items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document = collect()
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"COLLECTED_PR211_RETENTION inherited={len(document['inherited_files'])} "
          f"direct={len(document['direct_files'])} objects={len(document['objects'])}")


if __name__ == "__main__":
    main()
