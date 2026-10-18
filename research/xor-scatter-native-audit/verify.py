#!/usr/bin/env python3
"""Replay PR3273's public normaliser through authentic Boost-native checks.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
This is a dedicated finite native replay, not supplier admission.
"""

import argparse
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import tarfile
import tempfile

# Permit only this explicit local module directory when the entry point uses -I.
sys.path.insert(0, str(Path(__file__).resolve().parent))
# A private empty cache prevents old .pyc files replacing the reviewed source.
with tempfile.TemporaryDirectory(prefix="xor-native-import-") as _import_cache:
    _previous_cache = sys.pycache_prefix
    sys.pycache_prefix = _import_cache
    try:
        from independent_invoice import audit_word
        from native_check import command, require, run_native
    finally:
        sys.pycache_prefix = _previous_cache

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
BOUNDARY = "research/xor-scatter-boundary/boundary.py"
ARTIFACTS = ("249-records.bin", "249-states.json", "frames.json")
BOOST_ARCHIVE = {
    "url": "https://archives.boost.io/release/1.85.0/source/boost_1_85_0.tar.bz2",
    "checksum_url": "https://archives.boost.io/release/1.85.0/source/boost_1_85_0.tar.bz2.json",
    "sha256": "7009fe1faa1697476bdc7027703a2badb84e849b7b0baad5086b087b971f8617",
    "scope": "The author replay used unchanged headers extracted from this authenticated upstream archive, without a fixed-width stand-in or a system installation change.",
}


def digest(body):
    return hashlib.sha256(body).hexdigest()


def source_bytes(row, source_root, git_sources):
    path = PurePosixPath(row["path"])
    require(not path.is_absolute() and ".." not in path.parts and str(path) == row["path"],
            "canonical source path")
    if git_sources:
        environment = os.environ.copy()
        environment["GIT_NO_LAZY_FETCH"] = "1"
        pin = row["commit"] + ":" + row["path"]
        blob = subprocess.check_output(
            ["git", "rev-parse", pin], cwd=source_root, env=environment, timeout=30,
        ).decode().strip()
        require(blob == row["git_blob"], "Git source binding: " + row["path"])
        body = subprocess.check_output(
            ["git", "cat-file", "blob", blob], cwd=source_root, env=environment, timeout=30,
        )
    else:
        source = source_root / path
        require(source.is_file() and not source.is_symlink(), "regular source: " + row["path"])
        body = source.read_bytes()
    require(len(body) == row["size_bytes"] and digest(body) == row["sha256"],
            "source SHA256: " + row["path"])
    return body


def snapshot_sources(manifest, source_root, git_sources, destination):
    rows = manifest["files"]
    require(len(rows) == 9 and len({row["path"] for row in rows}) == 9,
            "fixed unique source inventory")
    destination.mkdir()
    for row in rows:
        body = source_bytes(row, source_root, git_sources)
        path = destination / row["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)


def check_snapshot(manifest, snapshot):
    for row in manifest["files"]:
        source_bytes(row, snapshot, False)


def fixtures(original):
    require(original["v"] == 111 and original["R"] == 439 and len(original["ret"]) == 9,
            "selected finite word dimensions")
    require(original["scatter"][0] == [4, 5, 6, 7, 8] and original["ret"][0] == 472,
            "source-bound fixture anchors")
    values = {name: copy.deepcopy(original) for name in
              ("baseline", "paired_absent", "odd_existing", "retained_alias", "odd_absent")}
    values["paired_absent"]["scatter"][0] += [0, 0]
    values["odd_existing"]["scatter"][0] += [4, 4]
    alias = values["retained_alias"]
    alias["ret"].append(alias["ret"][0])
    alias["scatter"][0] += [9, 9]
    values["odd_absent"]["scatter"][0] += [0]
    return values


def prepare_exports(snapshot, workdir):
    original_raw = (snapshot / WORD).read_bytes()
    original = json.loads(gzip.decompress(original_raw))
    words = fixtures(original)
    fixture_dir = workdir / "fixtures"
    fixture_dir.mkdir()
    outputs, receipts, independent = {}, {}, {}
    for name, word in words.items():
        path = fixture_dir / (name + ".json.gz")
        raw = original_raw if name == "baseline" else gzip.compress(
            json.dumps(word, sort_keys=True, separators=(",", ":")).encode(), mtime=0,
        )
        path.write_bytes(raw)
        output = fixture_dir / (name + "-export")
        result = command([sys.executable, "-I", "-B", snapshot / BOUNDARY,
                          "export", path, output], timeout=130)
        if name == "odd_absent":
            require(result.returncode != 0 and not output.exists() and not result.stdout,
                    "invalid endpoint must not publish output")
            require("checker.py rejected" in result.stderr and "REJECT xor-scatter-v1" in result.stderr,
                    "invalid endpoint rejection site")
            receipts[name] = {"accepted": False, "rejection": "authenticated symbolic checker"}
            continue
        require(result.returncode == 0 and output.is_dir(), "boundary CLI: " + result.stderr)
        value = json.loads(result.stdout)
        require(value["schema"] == "xor-scatter-v1", "normaliser schema")
        require(sorted(item.name for item in output.iterdir()) == sorted(ARTIFACTS),
                "boundary artifact inventory")
        hashes = {item: digest((output / item).read_bytes()) for item in ARTIFACTS}
        require(value["export"]["sha256"] == hashes, "boundary output hash receipt")
        canonical = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
        receipts[name] = {"accepted": True, "input_sha256": digest(raw),
                          "input_canonical_sha256": digest(canonical), "boundary": value}
        outputs[name] = output
        independent[name] = audit_word(word)
    for name in ("paired_absent", "odd_existing"):
        for item in ARTIFACTS:
            require((outputs[name] / item).read_bytes() == (outputs["baseline"] / item).read_bytes(),
                    "same normal form must preserve committed export bytes: " + name + "/" + item)
    return outputs, receipts, independent


def compare_independent(native, independent):
    fields = {
        "adds": "total_scalar_adds", "copies": "copies", "erasures": "copies",
        "scatter_adds": "normalised_scatter_adds", "rank_mass": "raw_rank_mass",
    }
    for name, value in independent.items():
        bill = native["fixtures"][name]["invoice"]
        for field, derived in fields.items():
            require(value[derived] == bill[field], "word/native independent invoice: " + name + "/" + field)


def authenticate_boost_archive(archive, backend):
    with archive.open("rb") as stream:
        archive_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    require(archive_hash == BOOST_ARCHIVE["sha256"], "official Boost archive SHA256")
    wanted = {}
    for dependencies in [backend["probe_dependencies"], *backend["native_dependencies"].values()]:
        for name, value in dependencies.items():
            require(name not in wanted or wanted[name] == value, "Boost header changed between builds")
            wanted[name] = value
    require(wanted, "nonempty compiler-observed Boost dependencies")
    seen = set()
    prefix = "boost_1_85_0/"
    with tarfile.open(archive, "r|bz2") as stream:
        for member in stream:
            name = member.name.removeprefix(prefix)
            if not member.name.startswith(prefix) or name not in wanted:
                continue
            require(name not in seen and member.isfile(), "unique regular Boost archive header")
            body = stream.extractfile(member).read()
            require(digest(body) == wanted[name], "compiled Boost header differs from archive: " + name)
            seen.add(name)
    require(seen == set(wanted), "all compiled Boost headers present in authenticated archive")
    return {"archive_sha256": archive_hash, "headers_checked": len(seen),
            "status": "PASS_COMPILED_BOOST_HEADERS_MATCH_OFFICIAL_ARCHIVE"}


def replay(source_root, git_sources, boost_include, boost_archive, compiler, workdir):
    manifest_raw = (PACKAGE / "SOURCES.json").read_bytes()
    manifest = json.loads(manifest_raw)
    implementation = {name: digest((PACKAGE / name).read_bytes())
                      for name in ("verify.py", "native_check.py", "independent_invoice.py")}
    snapshot = workdir / "sources"
    snapshot_sources(manifest, source_root, git_sources, snapshot)
    outputs, boundary, independent = prepare_exports(snapshot, workdir)
    native = run_native(snapshot, outputs, workdir / "native", boost_include, compiler)
    compare_independent(native, independent)
    native["backend"]["archive_authentication"] = authenticate_boost_archive(boost_archive, native["backend"])
    check_snapshot(manifest, snapshot)
    require((PACKAGE / "SOURCES.json").read_bytes() == manifest_raw, "source manifest changed during replay")
    require(implementation == {name: digest((PACKAGE / name).read_bytes()) for name in implementation},
            "audit implementation changed during replay")
    return {
        "schema": "xor-scatter-native-audit/receipt-v1",
        "status": "PASS_XOR_SCATTER_NATIVE_COMPOSITION",
        "base_commit": manifest["base_commit"],
        "investigated_head": manifest["investigated_head"],
        "sources_sha256": digest(manifest_raw),
        "implementation_sha256": implementation,
        "source_count": len(manifest["files"]),
        "source_bytes_unchanged": True,
        "boundary": boundary,
        "independent_word_invoice": independent,
        "native": native,
        "environment": {
            "python": platform.python_version(), "platform": platform.platform(),
            "machine": platform.machine(), "compiler": compiler,
            "author_boost_source": BOOST_ARCHIVE,
        },
        "limits": [
            "Finite normaliser/exporter/native composition only; no production adoption or new kappa.",
            "Empty kernel selection and empty owner/donor inputs make owner intersection checks vacuous.",
            "The native nondegeneracy field names a separate historical bank audit; that audit was not run here.",
            "Full selected ancestry, complete banks, physical hosting/routing, precision/tape, and all-size transfer remain unrun.",
            "Native failure controls are credited regression coverage from PR3210/PR3222, not a new mechanism.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT,
                        help="source checkout/export, or Git object store with --git-sources")
    parser.add_argument("--git-sources", action="store_true",
                        help="read already-fetched exact source blobs; no automatic fetch is intended")
    parser.add_argument("--boost-include", type=Path, required=True,
                        help="genuine Boost include root containing boost/")
    parser.add_argument("--boost-archive", type=Path, required=True,
                        help="official boost_1_85_0.tar.bz2 used to authenticate every compiled Boost header")
    parser.add_argument("--compiler", default="c++")
    parser.add_argument("--workdir", type=Path,
                        help="new scratch directory retained for inspection; otherwise use a temporary directory")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists() and not args.output.is_symlink(), "refuse to overwrite an existing receipt")
    if args.workdir:
        args.workdir.mkdir(parents=True, exist_ok=False)
        result = replay(args.source_root.resolve(), args.git_sources,
                        args.boost_include.resolve(), args.boost_archive.resolve(),
                        args.compiler, args.workdir.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="xor-native-audit-") as scratch:
            result = replay(args.source_root.resolve(), args.git_sources,
                            args.boost_include.resolve(), args.boost_archive.resolve(),
                            args.compiler, Path(scratch))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as receipt:
        json.dump(result, receipt, indent=2, sort_keys=True)
        receipt.write("\n")
    print(json.dumps({"status": result["status"], "receipt": str(args.output),
                      "fixtures": 4, "native_formal_columns_per_fixture": 883,
                      "source_count": result["source_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
