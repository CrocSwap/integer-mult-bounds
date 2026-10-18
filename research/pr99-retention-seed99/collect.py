#!/usr/bin/env python3
"""Recollect the bounded raw-Git proof. Needs the pinned source objects locally.

Fetch missing objects with `git fetch origin refs/pull/99/head` and
`git fetch origin tag archive/pr-reconciliation100-20261013`.
No network request or execution of archived code is made by this collector.
Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import ARCHIVE, BLOBS, ORIGINAL, PARENT, PR99, PR103, RETAINED, ROOT


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

    source = resolve(PR99, ORIGINAL)[1]
    retained = resolve(PR103, RETAINED)[1]
    if source != retained:
        raise ValueError("source and retained subtree differ")
    files = inventory(source)
    changed_trees(commit(PARENT), commit(PR99))
    commit(ARCHIVE)
    for _, (head, path) in BLOBS.items():
        kind, oid = resolve(head, path)
        save(kind, oid)
    # Git-native full-file comparison is a separate collection-time check.
    # The offline checker proves identity through the authenticated tree DAG.
    for path in files:
        original = git("show", PR99 + ":" + ORIGINAL + "/" + path)
        retained_raw = git("show", PR103 + ":" + RETAINED + "/" + path)
        if original != retained_raw:
            raise ValueError("payload mismatch: " + path)
    return {"schema_version": 1, "objects": dict(sorted(objects.items())), "files": dict(sorted(files.items()))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document = collect()
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"COLLECTED_PR99_RETENTION files={len(document['files'])} objects={len(document['objects'])}")


if __name__ == "__main__":
    main()
