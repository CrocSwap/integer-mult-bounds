#!/usr/bin/env python3
"""Reconstruct and reconcile the single post-review PR210 source transition.

Default: source/provenance checks and small negative controls only.
--output NEW_DIRECTORY: also run all eight native stages, then the independent
stream audit. --audit-existing REPLAY_DIRECTORY explicitly reuses a replay.
No network, branch changes, or edits to the historical package are performed.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
from stream_audit import audit, require

STAGES = ["banks", "bit", "complex", "finite", "math", "primes", "raw", "scalar"]
CURRENT_KAPPA = "710069340338651/1000000000000000000"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def blob_id(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def check_file(path, expected):
    require(not path.is_symlink() and path.is_file(), "missing/nonregular input: " + str(path))
    data = path.read_bytes()
    require(len(data) == expected["bytes"] and hashlib.sha256(data).hexdigest() == expected["sha256"]
            and blob_id(data) == expected["git_blob"], "source identity mismatch: " + str(path))


def manifest(directory, expected_hash):
    path = directory / "MANIFEST.json"
    require(sha(path) == expected_hash, "package manifest mismatch")
    actual = {}
    for item in directory.rglob("*"):
        require(not item.is_symlink(), "symlink in source package")
        if item.is_file() and item != path:
            actual[item.relative_to(directory).as_posix()] = sha(item)
    require(actual == read_json(path)["files"], "missing, modified or unpinned package input")
    return len(actual)


def check_sources(pins):
    count = manifest(ROOT / pins["package"], pins["before_manifest_sha256"])
    require(count == 121, "unexpected historical input count")
    require(sha(HERE / "source-delta.patch") == pins["patch_sha256"], "source delta changed")
    source = ROOT / pins["comparison_source"]
    require(sha(source) == pins["comparison_sha256"], "historical comparison snapshot changed")
    comparison = read_json(source)["210"]
    delta = {r["path"] for r in pins["post_review_delta"]}
    carried = {r["path"] for r in pins["unchanged_unresolved"]}
    unresolved = {r["path"]: r for r in comparison["unresolved"]}
    require(len(delta) == 19 and len(carried) == 128 and not delta & carried,
            "invalid post-review partition")
    require(delta | carried == unresolved.keys(), "unresolved path omitted from partition")
    require(pins["current_parent"] == pins["reviewed_head"], "transition is not one commit")
    for row in pins["unchanged_unresolved"]:
        require(row["git_blob"] == unresolved[row["path"]]["blob"], "ancestor identity mismatch")
    prefix = pins["package"] + "/"
    for row in pins["post_review_delta"]:
        if row["path"].startswith(prefix):
            path = ROOT / row["path"]
            if row["before"] is None:
                require(not path.exists(), "added file already in historical package")
            else:
                check_file(path, row["before"])
        else:
            check_file(HERE / "submitted" / Path(row["path"]).name, row["after"])
    old_certificate = next(r["before"] for r in pins["post_review_delta"]
                           if r["path"] == "certificates/five-stage-source527-banks-certificate.json")
    check_file(ROOT / "research/community-round9-audit/pr210-certificate.json", old_certificate)
    return dict(total_branch_diff=comparison["total"], previously_matched=len(comparison["matched"]),
                unresolved=len(unresolved), post_review_changes=len(delta),
                unchanged_since_review=len(carried),
                unchanged_groups=dict(sorted(Counter("/".join(p.split("/")[:2]) for p in carried).items())))


def reconstruct(pins, destination):
    package = destination / pins["package"]
    shutil.copytree(ROOT / pins["package"], package)
    patch = str(HERE / "source-delta.patch")
    for options in (["--check"], []):
        subprocess.run(["git", "apply", "--whitespace=nowarn", *options, patch],
                       cwd=destination, check=True, capture_output=True)
    require(manifest(package, pins["after_manifest_sha256"]) == 127,
            "unexpected current input count")
    for row in pins["post_review_delta"]:
        if row["path"].startswith(pins["package"] + "/"):
            check_file(destination / row["path"], row["after"])
    return package


def check_git_objects(pins):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT)
    changed = set(git("diff", "--name-only", pins["reviewed_head"], pins["current_head"]).decode().splitlines())
    require(changed == {r["path"] for r in pins["post_review_delta"]}, "Git delta differs")
    parent = git("rev-parse", pins["current_head"] + "^").decode().strip()
    require(parent == pins["reviewed_head"], "Git parent differs")
    for row in pins["post_review_delta"]:
        for side, ref in (("before", pins["reviewed_head"]), ("after", pins["current_head"])):
            expected = row[side]
            if expected is not None:
                data = git("show", ref + ":" + row["path"])
                require(blob_id(data) == expected["git_blob"] and hashlib.sha256(data).hexdigest() == expected["sha256"],
                        "Git content differs: " + row["path"])
    for row in pins["unchanged_unresolved"]:
        for ref in (pins["reviewed_head"], pins["current_head"]):
            oid = git("rev-parse", ref + ":" + row["path"]).decode().strip()
            require(oid == row["git_blob"], "unresolved ancestral file changed")
    return "PASS_EXACT_GIT_OBJECTS"


def validate_receipt(receipt, pins):
    require(receipt.get("status") == "PASS_IMMUTABLE_PARITY_FUSED_SOURCE527_FIVE_STAGE_BANKED_CONSTRUCTION",
            "native construction did not pass")
    require(receipt.get("fresh_stages") == STAGES, "incomplete native stage coverage")
    require(receipt.get("inputs_unchanged") is True, "native source changed during replay")
    require(receipt.get("manifest_sha256") == pins["after_manifest_sha256"], "wrong replay source")
    require(receipt.get("files") == 127 and receipt.get("kappa") == CURRENT_KAPPA, "wrong replay result")
    require(receipt.get("negative_controls") == ["omitted " + s + " stage" for s in STAGES],
            "missing native omission controls")


def check_replay(directory, pins):
    receipt = read_json(directory / "verification.json")
    validate_receipt(receipt, pins)
    expected = read_json(HERE / "submitted/five-stage-source527-banks-certificate.json")
    require(read_json(directory / "certificate.json") == expected, "fresh exact certificate differs")
    require(all((directory / (s + ".json")).is_file() for s in STAGES), "missing native stage output")
    raw = read_json(directory / "raw.json")
    current = raw["five_stage_profile"]
    previous = raw["producer_ledger"]["five_stage_profile"]
    delta = Counter({int(r): n for r, n in current["histogram"].items()})
    delta.subtract({int(r): n for r, n in previous["histogram"].items()})
    require({r: n for r, n in delta.items() if n} == {8: -15, 12: -15, 20: 15}, "wrong five-stage delta")
    require(previous["calls"] == 494994 and current["calls"] == 494979, "wrong five-stage call count")
    require(previous["rank_mass"] == current["rank_mass"] == 2830840, "five-stage rank mass changed")
    old_certificate = read_json(ROOT / "research/community-round9-audit/pr210-certificate.json")
    old_profile, new_profile = old_certificate["bit_profile"], expected["bit_profile"]
    normalized_delta = Counter({int(r): n for r, n in new_profile["histogram"].items()})
    normalized_delta.subtract({int(r): n for r, n in old_profile["histogram"].items()})
    require({r: n for r, n in normalized_delta.items() if n} == {8: -180, 12: -180, 20: 180},
            "wrong normalized paid delta")
    for key in ("W", "deficit", "literal_rank_mass", "literal_stock", "m", "maxchild",
                "normalization", "physical_replicas", "rank_mass"):
        require(old_profile[key] == new_profile[key], "inventory changed: " + key)
    require(old_profile["calls"] - new_profile["calls"] == 180 and
            old_profile["literal_children"] - new_profile["literal_children"] == 900,
            "wrong complete call reduction")
    require(Fraction(expected["kappa"]) < Fraction(read_json(ROOT / "certificates/selected-result.json")["kappa"]),
            "historical result unexpectedly exceeds selection; refresh research context")
    result = audit(directory)
    result["five_stage_delta"] = {8: -15, 12: -15, 20: 15}
    result["five_stage_calls"] = [previous["calls"], current["calls"]]
    result["complete_profile_reconciliation"] = dict(
        normalized_delta={8: -180, 12: -180, 20: 180},
        normalized_calls=[old_profile["calls"], new_profile["calls"]],
        literal_children=[old_profile["literal_children"], new_profile["literal_children"]],
        unchanged_normalized_rank_mass=new_profile["rank_mass"],
        unchanged_literal_rank_mass=new_profile["literal_rank_mass"],
        unchanged_literal_stock=new_profile["literal_stock"],
        previous_kappa=old_certificate["kappa"], reproduced_kappa=expected["kappa"])
    result["native_receipt"] = receipt
    names = [s + ".json" for s in STAGES] + ["certificate.json", "verification.json", "parity.json"]
    result["replay_artifact_sha256"] = {name: sha(directory / name) for name in names}
    return result


def controls(pins):
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern="test_reconciliation.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    require(result.wasSuccessful(), "stream controls failed")
    good = read_json(HERE / "submitted/five-stage-source527-banks-verification.json")
    validate_receipt(good, pins)
    rejected = []
    for name, key, value in [("missing stage", "fresh_stages", STAGES[:-1]),
                             ("different source", "manifest_sha256", "0" * 64),
                             ("changed input", "inputs_unchanged", False),
                             ("missing controls", "negative_controls", []),
                             ("wrong kappa", "kappa", "1/100")]:
        bad = dict(good); bad[key] = value
        try:
            validate_receipt(bad, pins)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("receipt corruption accepted: " + name)
    return dict(stream_tests=result.testsRun, rejected_receipt_controls=rejected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--output", type=Path, help="new directory for fresh source reconstruction and full replay")
    mode.add_argument("--audit-existing", type=Path, help="explicitly reuse an existing native replay")
    parser.add_argument("--git-check", action="store_true", help="also recheck fetched exact historical/current Git objects")
    args = parser.parse_args()
    pins = read_json(HERE / "PINS.json")
    summary = dict(status="PASS_SOURCE_RECONCILIATION", base_commit=pins["base_commit"],
                   reviewed_head=pins["reviewed_head"], current_head=pins["current_head"],
                   provenance=check_sources(pins), controls=controls(pins))
    if args.git_check:
        summary["git_objects"] = check_git_objects(pins)
    if args.output:
        output = args.output.resolve()
        require(not output.exists() and not output.is_relative_to(ROOT), "output must be new and outside the repository")
        output.mkdir(parents=True)
        package = reconstruct(pins, output / "source")
        with (output / "native.log").open("w") as log:
            subprocess.run([sys.executable, "-B", str(package / "verify.py"), "--output", str(output / "replay")],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        summary["replay_mode"] = "fresh_native_replay"
        summary["replay"] = check_replay(output / "replay", pins)
        summary["status"] = "PASS_PR210_HEAD_RECONCILIATION"
        (output / "RESULT.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    else:
        with tempfile.TemporaryDirectory(prefix="pr210-reconciliation-") as temporary:
            reconstruct(pins, Path(temporary))
        if args.audit_existing:
            summary["replay_mode"] = "explicit_existing_replay_audit"
            summary["replay"] = check_replay(args.audit_existing.resolve(), pins)
            summary["status"] = "PASS_PR210_HEAD_RECONCILIATION"
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
