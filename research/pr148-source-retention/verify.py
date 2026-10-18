#!/usr/bin/env python3
"""Offline source-retention proof; does not execute the historical construction.

Thiago Goulart (@Tuafo), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAIN = "ef5f39403610d231a0c27e8a6b4f08c10209bcd6"
HEAD = "975c3cf5d4ee0c90d5a76500d431bfc59102bb72"
COMPARISON = "56b66d58297deca1d7dd130247d720e960f77a37"
PARENT = "c8b22bc5c10dba497ac25804e27d9647d818e2ff"
HISTORY = "research/pr-reconciliation-20261012/content-comparison.json"
ARCHIVE = "research/coordinated-frames-and-entrance-banks"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def oid(kind, raw):
    return hashlib.sha1(kind.encode("ascii") + b" " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def relative(name):
    require(isinstance(name, str) and name and "\\" not in name, "invalid relative path")
    path = PurePosixPath(name)
    require(bool(path.parts) and not path.is_absolute() and path.as_posix() == name
            and not any(p in (".", "..") or ":" in p for p in path.parts), "invalid relative path")
    return path.parts


def read_file(root, name):
    path = root
    for part in relative(name):
        path = path / part
        require(not path.is_symlink(), "symlink input: " + name)
    require(path.is_file() and path.resolve().is_relative_to(root.resolve()), "missing input: " + name)
    return path.read_bytes()


class Proof:
    def __init__(self, document):
        require(document["schema_version"] == 1, "unsupported Git proof")
        self.objects = {}
        for key, row in document["objects"].items():
            require(HEX40.fullmatch(key) and row["type"] in ("commit", "tree"), "invalid Git object")
            raw = base64.b64decode(row["base64"], validate=True)
            require(oid(row["type"], raw) == key, "Git object digest mismatch")
            self.objects[key] = (row["type"], raw)

    def get(self, kind, key):
        require(key in self.objects and self.objects[key][0] == kind, "missing/wrong Git object: " + key)
        return self.objects[key][1]

    def commit(self, key):
        headers = self.get("commit", key).split(b"\n\n", 1)[0].splitlines()
        trees = [line[5:].decode("ascii") for line in headers if line.startswith(b"tree ")]
        parents = [line[7:].decode("ascii") for line in headers if line.startswith(b"parent ")]
        require(len(trees) == 1 and HEX40.fullmatch(trees[0]), "invalid commit tree")
        require(all(HEX40.fullmatch(p) for p in parents), "invalid parent")
        return trees[0], parents

    def tree(self, key):
        raw, offset, entries = self.get("tree", key), 0, {}
        while offset < len(raw):
            end = raw.find(b"\0", offset)
            require(end >= 0 and end + 21 <= len(raw), "truncated Git tree")
            mode, name = raw[offset:end].split(b" ", 1)
            name, mode = name.decode("utf-8"), mode.decode("ascii")
            require(len(relative(name)) == 1 and name not in entries, "duplicate/invalid tree name")
            require(mode in ("40000", "100644", "100755", "120000"), "unsupported Git tree mode")
            entries[name] = {"mode": mode, "blob": raw[end + 1:end + 21].hex()}
            offset = end + 21
        return entries

    def inventory(self, commit):
        result = {}

        def walk(key, prefix):
            for name, entry in self.tree(key).items():
                path = prefix + name
                if entry["mode"] == "40000":
                    walk(entry["blob"], path + "/")
                else:
                    result[path] = entry

        walk(self.commit(commit)[0], "")
        return result

    def lookup(self, commit, name):
        parts = relative(name)
        key = self.commit(commit)[0]
        for index, part in enumerate(parts):
            entries = self.tree(key)
            require(part in entries, "path absent from pinned main: " + name)
            entry = entries[part]
            if index < len(parts) - 1:
                require(entry["mode"] == "40000", "non-directory in Git path")
                key = entry["blob"]
        return entry


def changed(before, after):
    return {p: after.get(p) for p in before.keys() | after.keys() if before.get(p) != after.get(p)}


def verify_data(proof_data, coverage, repo_read, package_read):
    proof = Proof(proof_data)
    require(coverage["schema_version"] == 1, "unsupported coverage")
    for field, expected in (("main_commit", MAIN), ("head_commit", HEAD),
                            ("comparison_base", COMPARISON), ("direct_base", PARENT)):
        require(coverage[field] == expected, "changed pinned endpoint: " + field)

    # Authenticate the two author commits and the inherited comparison history.
    chain, cursor = [], HEAD
    while cursor != COMPARISON:
        require(cursor not in chain and len(chain) < 10, "unexpected commit ancestry")
        chain.append(cursor)
        parents = proof.commit(cursor)[1]
        require(len(parents) == 1, "expected a linear historical chain")
        cursor = parents[0]
    require(len(chain) == 6 and chain[2] == PARENT, "incorrect direct-change base")
    original = proof.inventory(HEAD)
    full_delta = changed(proof.inventory(COMPARISON), original)
    direct_delta = changed(proof.inventory(PARENT), original)
    require(len(full_delta) == 114 and len(direct_delta) == 11, "unexpected Git delta")
    require(all(value is not None for value in full_delta.values()), "unaccounted deletion")

    inputs = {}

    def main_bytes(name):
        if name not in inputs:
            entry = proof.lookup(MAIN, name)
            require(entry["mode"] in ("100644", "100755"), "non-regular main input")
            raw = repo_read(name)
            require(oid("blob", raw) == entry["blob"], "main input drift: " + name)
            inputs[name] = raw
        return inputs[name]

    history = json.loads(main_bytes(HISTORY))["148"]
    historical_rows = history["matched"] + history["unresolved"]
    require(history["total"] == 114 and len(historical_rows) == 114
            and len({r["path"] for r in historical_rows}) == 114, "invalid historical comparison")
    require({r["path"]: r["blob"] for r in historical_rows}
            == {p: v["blob"] for p, v in full_delta.items()}, "historical comparison differs from Git")
    baseline = json.loads(main_bytes(ARCHIVE + "/BASELINE.json"))
    pieces = []
    for row in baseline["parts"]:
        require(len(relative(row["file"])) == 1, "invalid archive part")
        raw = main_bytes(ARCHIVE + "/" + row["file"])
        require(len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"], "archive part drift")
        pieces.append(raw)
    archive = b"".join(pieces)
    require(hashlib.sha256(archive).hexdigest() == baseline["archive_sha256"], "archive concatenation drift")
    rows = coverage["rows"]
    require(len(rows) == 114 and len({r["path"] for r in rows}) == 114, "omitted/duplicate coverage row")
    require({r["path"] for r in rows} == set(full_delta), "coverage is not the complete Git delta")
    counts = {"main-file": 0, "pr181-archive": 0, "recovered": 0}
    recovered = []
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        members = z.namelist()
        for row in rows:
            name = row["path"]
            require({k: row[k] for k in ("mode", "blob")} == full_delta[name], "wrong source entry: " + name)
            require(type(row["direct_change"]) is bool and row["direct_change"] == (name in direct_delta),
                    "wrong author-delta classification: " + name)
            storage, kind = row["storage"], row["storage"]["kind"]
            require(kind in counts, "unknown storage class")
            counts[kind] += 1
            if kind == "main-file":
                require(proof.lookup(MAIN, storage["path"]) == full_delta[name], "wrong retained mode/blob")
                raw = main_bytes(storage["path"])
            elif kind == "pr181-archive":
                require(storage["member"] == name and members.count(name) == 1, "wrong/duplicate archive member")
                info = z.getinfo(name)
                require(not info.is_dir() and ((info.external_attr >> 16) & 0o170000) in (0, 0o100000),
                        "non-regular archive member")
                raw = z.read(name)
            else:
                require(storage["path"] == "original/" + name, "wrong recovered path")
                raw = package_read(storage["path"])
                recovered.append(name)
            require(oid("blob", raw) == row["blob"], "retained payload differs: " + name)
    require(counts == {"main-file": 96, "pr181-archive": 4, "recovered": 14}, "wrong coverage partition")
    require(set(recovered) == {r["path"] for r in history["unresolved"]}, "recovery does not close the recorded gaps")
    for name in ("LICENSE", "NOTICE"):
        require(oid("blob", package_read("original/" + name)) == original[name]["blob"], "missing original license/notice")
    declared = json.loads(package_read("VERIFY.json"))["inputs"]
    require(len(declared) == len(set(declared)) and set(declared) == set(inputs), "incomplete CI invalidation inputs")
    return {"status": "PASS_PR148_SOURCE_RETENTION", "main_commit": MAIN, "head_commit": HEAD,
            "comparison_base": COMPARISON, "direct_base": PARENT, "authenticated_commits": 8,
            "authenticated_objects": len(proof.objects), "comparison_changed_paths": len(full_delta),
            "direct_changed_paths": sorted(direct_delta), "inherited_changed_paths": len(full_delta) - len(direct_delta),
            "coverage": counts, "recovered_paths": sorted(recovered), "live_inputs": len(inputs),
            "scope": "Exact historical source retention and author-delta classification only. No fresh mathematical replay, new kappa, PR disposition or selected-frontier change."}


def verify():
    return verify_data(json.loads(read_file(HERE, "TREE-PROOF.json")),
                       json.loads(read_file(HERE, "COVERAGE.json")),
                       lambda name: read_file(ROOT, name), lambda name: read_file(HERE, name))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="explicitly regenerate the deterministic receipt")
    args = ap.parse_args()
    result = verify()
    if args.write:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        require(json.loads(read_file(HERE, "RESULT.json")) == result, "saved receipt differs")
    print(result["status"] + ": 114 paths = 96 main + 4 archive + 14 recovered; 11 direct changes")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError, zipfile.BadZipFile) as exc:
        raise SystemExit("FAIL_PR148_SOURCE_RETENTION: " + str(exc)) from exc
