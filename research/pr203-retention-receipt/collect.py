#!/usr/bin/env python3
"""Recollect the bounded raw-Git proof for PR203. Needs the pinned source objects locally.

Fetch missing objects with:
  git fetch origin refs/pull/203/head
  git fetch origin refs/pull/187/head
  git fetch origin refs/pull/193/head
  git fetch origin tag archive/pr-reconciliation100-20261013
  git fetch origin tag archive/pr-reconciliation-next100-20261013
No network request or execution of archived code is made by this collector.
steph4n (@steph4n-gh), with substantial Google Gemini assistance. Apache-2.0.
"""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import (
    ARCHIVE_92, ARCHIVE_NEXT100, FANO_COMPLETION_BLOB, FANO_COMPLETION_PATH,
    MERGE_BASE, PKG_DIR, PKG_WORKFLOW, PR187, PR187_PHYSICAL_BLOB,
    PR187_PHYSICAL_PATH, PR193, PR193_BALANCED_FANO_BLOB,
    PR193_BALANCED_FANO_PATH, PR193_CERT_BLOB, PR193_CERT_PATH, PR203, ROOT,
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
    t_203 = commit(PR203)
    changed_trees(t_mb, t_203)

    _, pkg_203 = resolve(PR203, PKG_DIR)
    _, wf_203 = resolve(PR203, PKG_WORKFLOW)
    files = {PKG_WORKFLOW: {"mode": "100644", "blob": wf_203}}
    for path, row in inventory(pkg_203).items():
        files[PKG_DIR + "/" + path] = row

    for row in files.values():
        save("blob", row["blob"])

    _, b187 = resolve(PR187, PR187_PHYSICAL_PATH)
    if b187 != PR187_PHYSICAL_BLOB:
        raise ValueError("PR187 emitted-physical.json blob mismatch")
    save("blob", b187)

    _, b193 = resolve(PR193, PR193_CERT_PATH)
    if b193 != PR193_CERT_BLOB:
        raise ValueError("PR193 certificate.json blob mismatch")
    save("blob", b193)

    _, bf193 = resolve(PR193, PR193_BALANCED_FANO_PATH)
    if bf193 != PR193_BALANCED_FANO_BLOB:
        raise ValueError("PR193 balanced_fano.py blob mismatch")
    save("blob", bf193)

    _, fc193 = resolve(PR193, FANO_COMPLETION_PATH)
    if fc193 != FANO_COMPLETION_BLOB:
        raise ValueError("PR193 fano_completion.py blob mismatch")
    save("blob", fc193)

    commit(ARCHIVE_92)
    commit(ARCHIVE_NEXT100)

    return {
        "schema_version": 1,
        "objects": dict(sorted(objects.items())),
        "files": dict(sorted(files.items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document = collect()
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"COLLECTED_PR203_RETENTION files={len(document['files'])} objects={len(document['objects'])}")


if __name__ == "__main__":
    main()
