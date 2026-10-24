#!/usr/bin/env python3
"""Check the final package and bind it to the independent cold replay."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cold-copy", type=Path, required=True)
    parser.add_argument("--pre-snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    wrap = Path(__file__).resolve().parents[2]
    package = wrap / "packages/centre-code-services"
    manifest_path = package / "PACKAGE-MANIFEST.json"
    expected = "2432e5e8dd448a4f22b23bcc8844433870dab2742bd7436c2522fffe2bbe63da"
    require(digest(manifest_path.read_bytes()) == expected, "Final manifest changed")
    manifest = json.loads(manifest_path.read_bytes())
    listed = {}
    for entry in manifest["files"]:
        path = package / entry["path"]
        require(path.is_file() and not path.is_symlink(), "Missing or linked package file")
        data = path.read_bytes()
        require(len(data) == entry["bytes"] and digest(data) == entry["sha256"], entry["path"])
        require(entry["path"] not in listed, "Duplicate manifest path")
        listed[entry["path"]] = entry["sha256"]
    actual = {str(p.relative_to(package)) for p in package.rglob("*") if p.is_file()}
    require(actual == set(listed) | {"PACKAGE-MANIFEST.json"}, "Package file set changed")

    sources = json.loads((package / "SOURCE-MANIFEST.json").read_bytes())
    campaign = Path(sources["original_campaign_root"])
    references = json.loads((package / "REFERENCE-MANIFEST.json").read_bytes())
    source_checks = []
    for kind, entries in (("runtime_or_proof", sources["immutable_inputs"]),
                          ("historical_reference", references["reference_documents"])):
        for entry in entries:
            data = (package / entry["path"]).read_bytes()
            require(data == (campaign / entry["campaign_path"]).read_bytes(), entry["path"])
            require(digest(data) == entry["sha256"] and len(data) == entry["bytes"], entry["path"])
            if "decompressed_sha256" in entry:
                require(digest(gzip.decompress(data)) == entry["decompressed_sha256"], entry["path"])
            source_checks.append({"path": entry["path"], "kind": kind, "sha256": digest(data)})
    join = json.loads((package / "evidence/FIXED-READER-JOIN-CLOSURE.json").read_bytes())
    for relative, entry in join["files"].items():
        data = (package / "frozen" / relative).read_bytes()
        require(digest(data) == entry["sha256"] and len(data) == entry["bytes"], relative)

    before = json.loads(args.pre_snapshot.read_bytes())
    for relative, expected_hash in before.items():
        require(digest((args.cold_copy / relative).read_bytes()) == expected_hash,
                "Cold source changed: " + relative)
    require(all(relative in listed for relative in before), "Initial package file was removed")
    changed = sorted(relative for relative, value in before.items() if listed[relative] != value)
    require(changed == ["README.md"], "A replay input changed after the cold copy")
    for entry in sources["immutable_inputs"]:
        require(before[entry["path"]] == entry["sha256"], "A replay source changed")
    for relative in ("CHECKS.json", "SOURCE-MANIFEST.json", "replay.py", "PROOFS.md"):
        require(before[relative] == listed[relative], relative)

    links = []
    for relative in ("README.md", "PROOFS.md", "PROVENANCE.md", "NOTICE.md"):
        source = package / relative
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", source.read_text()):
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            destination = (source.parent / unquote(parsed.path)).resolve()
            require(destination.is_relative_to(package) and destination.exists(), target)
            links.append({"document": relative, "target": target})

    upstream = []
    repository = campaign.parents[1]
    for entry in json.loads((package / "evidence/SOURCE-LICENSE-CHECK.json").read_bytes())["checks"]:
        obj = entry["source_commit"] + ":" + entry["source_path"]
        data = subprocess.run(["git", "show", obj], cwd=repository, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        require(data == (package / entry["retained_path"]).read_bytes(), obj)
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == entry["git_blob"] and digest(data) == entry["sha256"], obj)
        upstream.append({"git_object": obj, "git_blob": blob, "sha256": digest(data)})
    receipt = {
        "status": "PASS_FINAL_PACKAGE_AND_COLD_SOURCE_BINDING",
        "package_manifest_sha256": expected,
        "listed_file_count": len(listed),
        "package_file_count_including_manifest": len(actual),
        "package_bytes_including_manifest": sum(p.stat().st_size for p in package.rglob("*") if p.is_file()),
        "runtime_and_proof_source_count": len(sources["immutable_inputs"]),
        "historical_reference_count": len(references["reference_documents"]),
        "join_closure_files": len(join["files"]),
        "source_checks": source_checks,
        "pre_replay_snapshot_sha256": digest(args.pre_snapshot.read_bytes()),
        "cold_source_files_unchanged": len(before),
        "changed_existing_files_after_cold_copy": changed,
        "added_files_after_cold_copy": sorted(set(listed) - set(before)),
        "runtime_closure_unchanged": True,
        "local_links": links,
        "upstream_git_object_checks": upstream,
        "scope": "Local source integrity and relocation binding. GitHub rendering and publication are not checked here.",
    }
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(actual), len(source_checks), len(links))


if __name__ == "__main__":
    main()
