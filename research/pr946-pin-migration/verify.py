#!/usr/bin/env python3
"""Reconcile PR946's complete inventory with literal JSON hash references.

This is a historical, exact-byte inventory, not a general dependency parser.
All scanned data comes from BASE's Git tree, never mutable working-tree JSON.
Only the optional --check-proposal requires the independently fetched PR head.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = "407d52ff15b2217b6e22bce44728b4c3907b6515"
HEAD = "b6e22dbf548d72f18b722ccb6c2ea8e3d9df6ac1"
PARENT = "91a2094f2e022930069e8cfdc810a3ea1b81cd09"
COVERAGE = "research/community-batch952-audit/CONTENT-COVERAGE.json"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


class Blobs:
    """Read only named immutable Git blobs, with one persistent subprocess."""
    def __enter__(self):
        self.proc = subprocess.Popen(["git", "-C", str(ROOT), "cat-file", "--batch"],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return self

    def read(self, name):
        require("\n" not in name and "\r" not in name, "Invalid Git object name")
        self.proc.stdin.write(name.encode("utf-8") + b"\n")
        self.proc.stdin.flush()
        header = self.proc.stdout.readline().split()
        require(len(header) == 3 and header[1] == b"blob", "Missing/non-blob source: " + name)
        count = int(header[2])
        data = self.proc.stdout.read(count)
        require(len(data) == count and self.proc.stdout.read(1) == b"\n", "Truncated blob")
        return data

    def __exit__(self, *_):
        self.proc.stdin.close()
        self.proc.stdout.close()
        self.proc.wait()


def tree(commit):
    result = {}
    for entry in git("ls-tree", "-r", "-z", commit).split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        mode, kind, oid = meta.decode("ascii").split()
        if kind == "blob":
            result[path.decode("utf-8")] = (mode, oid)
    return result


def pointer(parts):
    return "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in parts)


def scan_json(data):
    # We inspect strings and structure only. Leaving numeric tokens as None
    # avoids Python's version-dependent giant-integer digit limit and avoids
    # mistaking a numeric 64-digit value for a string SHA256 reference.
    def unique_pairs(pairs):
        obj = {}
        for key, value in pairs:
            require(key not in obj, "Duplicate JSON key: " + key)
            obj[key] = value
        return obj
    return json.loads(data, parse_int=lambda _: None, parse_float=lambda _: None,
                      object_pairs_hook=unique_pairs)


def references(obj, changed, parts=()):
    """Closed grammar: path->hex, path->{sha256:hex}, and explicit records.

    A result means exactly that these strings occur together in this shape.
    It does not establish that a verifier consumes the record, or that its
    digest semantics are raw bytes rather than a canonical representation.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in changed:
                if isinstance(value, str) and SHA256.fullmatch(value):
                    yield key, value, pointer(parts + (key,)), "path_to_digest"
                elif isinstance(value, dict):
                    digest = value.get("sha256")
                    if isinstance(digest, str) and SHA256.fullmatch(digest):
                        yield key, digest, pointer(parts + (key, "sha256")), "path_to_sha256_record"
            yield from references(value, changed, parts + (key,))
        for path_key, digest_key in (("path", "sha256"), ("repository_path", "sha256"),
                                     ("source_path", "source_sha256"), ("file", "sha256")):
            path, digest = obj.get(path_key), obj.get(digest_key)
            if isinstance(path, str) and path in changed and isinstance(digest, str) and SHA256.fullmatch(digest):
                yield path, digest, pointer(parts + (digest_key,)), path_key + "_record"
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from references(value, changed, parts + (i,))


def location_kind(path):
    if any(part in path.split("/") for part in ("submitted", "submitted-context", "before-integration", "vendor")):
        return "archived_or_vendor"
    if path.startswith("certificates/"):
        return "certificate"
    if path.startswith("docs/"):
        return "review_document"
    return "research_or_other"


def classify(digest, before, after):
    if before == after:
        return "unchanged" if digest == before else "other_digest"
    if digest == before:
        return "old_bytes_reference"
    if digest == after:
        return "proposed_bytes_reference"
    return "other_digest"


def inventory(check_proposal=False):
    files = tree(BASE)
    with Blobs() as blobs:
        coverage_raw = blobs.read(files[COVERAGE][1])
        cov = json.loads(coverage_raw)["pull_requests"]["946"]
        require(cov["head"] == HEAD and cov["changed_files"] == len(cov["files"]) == 165,
                "Unexpected frozen PR946 inventory")
        proposed = {row["source_path"]: row["source_sha256"] for row in cov["files"]}
        require(len(proposed) == 165, "Duplicate proposed path")
        require(all(SHA256.fullmatch(d) for d in proposed.values()), "Invalid proposed digest")
        old = {path: sha(blobs.read(files[path][1])) if path in files else None for path in proposed}
        changes = [{"path": p, "base_blob": files[p][1] if p in files else None,
                    "base_sha256": old[p], "proposed_sha256": proposed[p],
                    "state": "added" if p not in files else ("same_bytes" if old[p] == proposed[p] else "different_bytes")}
                   for p in sorted(proposed)]
        if check_proposal:
            require(git("rev-parse", HEAD + "^").decode().strip() == PARENT, "Proposal parent mismatch")
            actual = set(git("diff", "--name-only", "-z", PARENT, HEAD).decode().strip("\0").split("\0"))
            require(actual == set(proposed), "Proposal diff differs from 165-file inventory")
            for path, digest in proposed.items():
                require(sha(blobs.read(HEAD + ":" + path)) == digest, "Proposal payload mismatch: " + path)
        rows, scanned, parsed, failed = [], [], [], []
        scanned_bytes = 0
        for path, (mode, oid) in sorted(files.items()):
            if not path.endswith(".json") or mode == "120000":
                continue
            data = blobs.read(oid)
            scanned.append(path)
            scanned_bytes += len(data)
            try:
                obj = scan_json(data)
            except (ValueError, UnicodeError):
                failed.append(path)
                continue
            parsed.append(path)
            for target, digest, ptr, schema in references(obj, proposed):
                rows.append({"consumer": path, "consumer_blob": oid, "pointer": ptr,
                             "schema": schema, "target": target, "recorded_sha256": digest,
                             "classification": classify(digest, old[target], proposed[target]),
                             "location_kind": location_kind(path)})
        rows.sort(key=lambda r: (r["consumer"], r["pointer"], r["target"], r["schema"]))
        old_rows = [r for r in rows if r["classification"] == "old_bytes_reference"]
        conflicts = sorted({r["target"] for r in old_rows})
        return {"schema": "pr946-literal-pin-impact-v1", "base_commit": BASE,
                "base_tree": git("rev-parse", BASE + "^{tree}").decode().strip(),
                "proposal_head": HEAD, "proposal_parent": PARENT,
                "inventory_source": COVERAGE, "inventory_sha256": sha(coverage_raw),
                "scope": "All tracked regular JSON files at BASE; closed literal path/digest grammar. References are not proven runtime dependencies.",
                "scan": {"json_files": len(scanned), "json_bytes": scanned_bytes,
                         "parsed_json": len(parsed), "parse_failures": failed,
                         "scanned_paths_sha256": sha(("\n".join(scanned) + "\n").encode())},
                "summary": {"proposed_files": len(changes), "change_states": dict(sorted(Counter(r["state"] for r in changes).items())),
                            "reference_classes": dict(sorted(Counter(r["classification"] for r in rows).items())),
                            "old_reference_locations": dict(sorted(Counter(r["location_kind"] for r in old_rows).items())),
                            "old_reference_consumers": len({r["consumer"] for r in old_rows}),
                            "old_reference_targets": len(conflicts)},
                "old_reference_targets": conflicts, "changes": changes, "references": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-proposal", action="store_true", help="Additionally check all actual PR Git blobs and its complete diff")
    parser.add_argument("--write", type=Path, help="Write a new deterministic inventory; refuses overwrite")
    args = parser.parse_args()
    result = inventory(args.check_proposal)
    if args.write:
        with args.write.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, sort_keys=True, indent=2)
            stream.write("\n")
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
        require(result == expected, "Historical inventory differs from EXPECTED.json")
    print("PASS_PR946_PIN_INVENTORY " + json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
