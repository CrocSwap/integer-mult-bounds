#!/usr/bin/env python3
"""Authoring only: collect the pinned Git proof and recover the missing originals.

Thiago Goulart (@Tuafo), with substantial OpenAI Codex assistance. Apache-2.0.
Requires the original PR148 head in the local object database. Does not fetch.
"""
import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAIN = "ef5f39403610d231a0c27e8a6b4f08c10209bcd6"
HEAD = "975c3cf5d4ee0c90d5a76500d431bfc59102bb72"
COMPARISON = "56b66d58297deca1d7dd130247d720e960f77a37"
PARENT = "c8b22bc5c10dba497ac25804e27d9647d818e2ff"
HISTORY = "research/pr-reconciliation-20261012/content-comparison.json"
ARCHIVE = "research/coordinated-frames-and-entrance-banks"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    objects = {}

    def remember(kind, oid):
        if oid not in objects:
            raw = git("cat-file", kind, oid)
            objects[oid] = {"type": kind, "base64": base64.b64encode(raw).decode("ascii")}
        return base64.b64decode(objects[oid]["base64"])

    def remember_tree(oid):
        raw = remember("tree", oid)
        offset = 0
        while offset < len(raw):
            end = raw.index(b"\0", offset)
            mode, _ = raw[offset:end].split(b" ", 1)
            child = raw[end + 1:end + 21].hex()
            if mode == b"40000":
                remember_tree(child)
            offset = end + 21

    def inventory(revision):
        result = {}
        for line in git("ls-tree", "-rz", revision).split(b"\0"):
            if line:
                header, name = line.split(b"\t", 1)
                mode, kind, oid = header.decode().split()
                if kind != "blob":
                    raise ValueError("non-blob inventory entry")
                result[name.decode()] = {"mode": mode, "blob": oid}
        return result

    chain = git("rev-list", "--first-parent", HEAD, "^" + COMPARISON).decode().splitlines()
    for commit in (MAIN, COMPARISON, *chain):
        raw = remember("commit", commit)
        if commit in (HEAD, COMPARISON, PARENT):
            remember_tree(raw.splitlines()[0].split()[1].decode())
    ht, mt, bt, pt = map(inventory, (HEAD, MAIN, COMPARISON, PARENT))
    old = json.loads((ROOT / HISTORY).read_bytes())["148"]
    historical = {r["path"]: r["blob"] for r in old["matched"] + old["unresolved"]}
    changes = {p: ht.get(p) for p in ht.keys() | bt.keys() if ht.get(p) != bt.get(p)}
    if historical != {p: r["blob"] for p, r in changes.items()}:
        raise ValueError("published comparison is not the complete pinned Git delta")
    direct = sorted(p for p in ht.keys() | pt.keys() if ht.get(p) != pt.get(p))
    baseline = json.loads((ROOT / ARCHIVE / "BASELINE.json").read_bytes())
    archive = b"".join((ROOT / ARCHIVE / r["file"]).read_bytes() for r in baseline["parts"])
    if hashlib.sha256(archive).hexdigest() != baseline["archive_sha256"]:
        raise ValueError("archive drift")
    rows = []
    inputs = {HISTORY, ARCHIVE + "/BASELINE.json"}
    inputs.update(ARCHIVE + "/" + r["file"] for r in baseline["parts"])
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for name, entry in sorted(changes.items()):
            matches = [p for p, value in mt.items() if value == entry]
            if matches:
                path = name if name in matches else min(matches, key=lambda p: (len(p), p))
                storage = {"kind": "main-file", "path": path}
                inputs.add(path)
            elif name in z.namelist() and hashlib.sha1(
                    b"blob " + str(len(z.read(name))).encode() + b"\0" + z.read(name)).hexdigest() == entry["blob"]:
                storage = {"kind": "pr181-archive", "member": name}
            else:
                path = HERE / "original" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(git("cat-file", "blob", entry["blob"]))
                storage = {"kind": "recovered", "path": "original/" + name}
            rows.append({"path": name, **entry, "direct_change": name in direct, "storage": storage})
    for name in ("LICENSE", "NOTICE"):
        (HERE / "original" / name).write_bytes(git("cat-file", "blob", ht[name]["blob"]))

    # Authenticate each live main path through its exact enclosing Git trees.
    for name in sorted(inputs):
        parts = name.split("/")
        for index in range(len(parts)):
            spec = MAIN + (":" + "/".join(parts[:index]) if index else "^{tree}")
            remember("tree", git("rev-parse", spec).decode().strip())
    dump(HERE / "TREE-PROOF.json", {"schema_version": 1, "objects": objects})
    dump(HERE / "COVERAGE.json", {"schema_version": 1, "main_commit": MAIN,
         "head_commit": HEAD, "comparison_base": COMPARISON, "direct_base": PARENT, "rows": rows})
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    sources["files"] = [r for r in sources["files"] if r["usage"] == "provenance"]
    for name in sorted(inputs):
        raw = (ROOT / name).read_bytes()
        if raw != git("show", MAIN + ":" + name):
            raise ValueError("input differs from the research base: " + name)
        sources["files"].append({"path": name, "usage": "input", "git_blob": mt[name]["blob"],
                                 "sha256": hashlib.sha256(raw).hexdigest()})
    dump(HERE / "SOURCES.json", sources)
    manifest = json.loads((HERE / "VERIFY.json").read_bytes())
    manifest["inputs"] = sorted(inputs)
    dump(HERE / "VERIFY.json", manifest)
    print(json.dumps({"paths": len(rows), "direct_changes": len(direct), "tree_objects_and_commits": len(objects),
          "storage": {kind: sum(r["storage"]["kind"] == kind for r in rows)
                      for kind in ("main-file", "pr181-archive", "recovered")}}, indent=2))


if __name__ == "__main__":
    main()
