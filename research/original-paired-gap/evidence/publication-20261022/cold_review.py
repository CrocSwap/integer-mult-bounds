"""Check the publication package with a separate Git object store.

This review uses the Python standard library and Git. It does not change
the source package. OpenAI Codex assisted this review.
"""

from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time


BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
EXPECTED_LINES = [
    "PASS_EXACT_ORIGINAL_PAIRED_MAPS",
    "PASS_ORIGINAL_PAIRED_NATIVE_COMPONENTS",
    "PASS_GENERAL_MONOMIAL_SQUARE_IDENTITIES",
    "PASS_PORTABLE_ORIGINAL_PAIRED_GAP",
]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def git(repo, *args, data=None):
    return subprocess.check_output(["git", "-C", str(repo), *args], input=data)


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(args):
    package = args.package.resolve()
    repo = args.repo.resolve()
    out = args.out.resolve()
    need(not out.exists(), "Use a new cold output directory")
    need(shutil.disk_usage(out.parent).free >= 3 * 1024**3, "Free space is below 3 GiB")
    manifest = json.loads((package / "MANIFEST.json").read_bytes())
    before = {str(p.relative_to(package)): digest(p) for p in package.rglob("*") if p.is_file()}
    need(set(before) == {"MANIFEST.json", *(item["path"] for item in manifest["files"])},
         "The manifest file set differs")
    for item in manifest["files"]:
        path = package / item["path"]
        need(before[item["path"]] == item["sha256"] and path.stat().st_size == item["bytes"],
             "The manifest bytes differ: " + item["path"])
    out.mkdir()
    copy = out / "package"
    shutil.copytree(package, copy)
    bare = out / "source.git"
    subprocess.run(["git", "init", "--bare", "--quiet", str(bare)], check=True)
    objects = []
    for revision in (BASE + ":.gitattributes", BASE + ":research/.gitattributes", BASE, BASE + "^{tree}", BASE + ":research", BASE + ":research/community-frontier1042-audit", BASE + ":" + ARCHIVE):
        oid = git(repo, "rev-parse", revision).decode().strip()
        kind = git(repo, "cat-file", "-t", oid).decode().strip()
        raw = git(repo, "cat-file", kind, oid)
        actual = git(bare, "hash-object", "-w", "-t", kind, "--stdin", data=raw).decode().strip()
        need(actual == oid, "The copied Git object differs")
        objects.append({"revision": revision, "oid": oid, "type": kind, "bytes": len(raw), "sha256": sha256(raw).hexdigest()})
    need(not (bare / "objects/info/alternates").exists(), "The cold repository uses alternates")
    archive = git(bare, "show", BASE + ":" + ARCHIVE)
    need(sha256(archive).hexdigest() == "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754", "The cold archive differs")
    run_out = out / "replay"
    command = [sys.executable, "-I", "-O", "-B", str(copy / "replay.py"), "--repo", str(bare), "--out", str(run_out)]
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("GIT_", "PYTHON", "OMP_", "OPENBLAS_", "MKL_", "VECLIB_"))}
    env.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1")
    started = time.monotonic()
    result = subprocess.run(command, cwd=out, env=env, text=True, capture_output=True)
    elapsed = time.monotonic() - started
    (out / "stdout.txt").write_text(result.stdout, encoding="utf-8")
    (out / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    need(result.returncode == 0 and result.stdout.splitlines() == EXPECTED_LINES, "The cold replay failed")
    comparisons = {}
    for name in ("PAIR-CHECKS.json", "NATIVE-CHECKS.json", "ALGEBRA-CHECKS.json", "REPLAY.json"):
        actual = digest(run_out / name)
        expected = digest(copy / "evidence" / name)
        need(actual == expected, "The cold output differs: " + name)
        comparisons[name] = {"sha256": actual, "matches_retained_receipt": True}
    supplemental = [
        [sys.executable, "-I", "-O", "-B", str(copy / "evidence/independent_algebra.py"), "--out", str(out / "INDEPENDENT-ALGEBRA.json")],
        [sys.executable, "-I", "-O", "-B", str(copy / "evidence/check_negative_witnesses.py"), "--package", str(copy), "--repo", str(bare), "--out", str(out / "NEGATIVE-WITNESSES.json")],
    ]
    supplement_runs = []
    for command2 in supplemental:
        result2 = subprocess.run(command2, cwd=out, env=env, text=True, capture_output=True)
        need(result2.returncode == 0, "A supplementary check failed: " + result2.stderr)
        path = Path(command2[-1])
        need(digest(path) == digest(copy / "evidence" / path.name), "A supplementary receipt differs")
        supplement_runs.append({"command": command2, "stdout": result2.stdout, "stderr": result2.stderr, "sha256": digest(path), "matches_retained_receipt": True})
    after = {str(p.relative_to(package)): digest(p) for p in package.rglob("*") if p.is_file()}
    need(before == after, "The source package changed")
    need(shutil.disk_usage(out).free >= 3 * 1024**3, "Free space is below 3 GiB")
    save(out / "COLD-REPLAY.json", {
        "status": "PASS_CURRENT_PUBLICATION_COLD_REPLAY",
        "review_type": "Separate OpenAI Codex agent review; no human review claim",
        "source_package": str(package), "source_package_unchanged": True,
        "package_files": len(before), "package_manifest_sha256": before["MANIFEST.json"],
        "python": sys.version, "platform": platform.platform(),
        "command": command, "cwd": str(out), "exit_code": result.returncode,
        "stdout": result.stdout, "stderr": result.stderr, "seconds": elapsed,
        "source_objects": objects, "source_alternates": False,
        "source_checkout": False, "source_parent_commits": False,
        "output_comparisons": comparisons, "supplement_runs": supplement_runs,
        "free_bytes_after": shutil.disk_usage(out).free,
    })
    print("PASS_CURRENT_PUBLICATION_COLD_REPLAY")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    main(parser.parse_args())
