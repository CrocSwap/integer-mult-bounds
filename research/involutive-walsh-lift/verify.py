"""Replay the exact involutive Walsh lift and bind its separate checks.

New code uses Apache-2.0 and OpenAI Codex assistance. The proof scope is
the unchanged selected scalar word, not a new centre controller.
"""

from hashlib import sha1, sha256
from pathlib import Path
import argparse
import gzip
import json
import subprocess
import sys


PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import sources


STAGES = (
    ("generate_walsh.py", "GENERATION.json", "PASS_GENERATED_WALSH_AND_INVOLUTIVE_NATIVE_LIFT"),
    ("review_native.py", "WALSH-RETARGET-REVIEW.json", "PASS_INDEPENDENT_WALSH_RETARGET_FRAMES_AND_ACTUAL_WORD_LEDGER"),
    ("review_doubled.py", "DOUBLED-WALSH-REVIEW.json", "PASS_EXACT_DOUBLED_WALSH_NATIVE_LOWERING"),
    ("global_walsh.py", "GLOBAL-CHECKS.json", "PASS_SELECTED_GLOBAL_DOUBLED_WALSH_BINDING"),
    ("review_global.py", "GLOBAL-WALSH-REVIEW.json", "PASS_INDEPENDENT_SELECTED_GLOBAL_WALSH_HISTORY"),
    ("verify_invoice.py", "DILATION-INVOICE.json", "PASS_EXACT_TWOFOLD_DILATION_INVOICE_AND_MOMENT_TRANSFER"),
    ("review_invoice.py", "DILATION-INVOICE-REVIEW.json", "PASS_INDEPENDENT_DILATION_ARITHMETIC_AND_SOURCE_BINDING"),
)


def digest(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return sha256(raw).hexdigest()


def check_sources(repo):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    sources.require(manifest["source_commit"] == sources.BASE, "The manifest base differs.")
    objects = [(entry["path"], entry) for entry in manifest["archives"]]
    objects += list(manifest["direct_files"].items())
    for path, entry in objects:
        raw = sources.read_git(repo, path, entry["sha256"])
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        sources.require(blob == entry["git_blob"], "The Git object pin differs: " + path)
    for entry in manifest["archives"]:
        sources.archive_members(repo, entry["path"], entry["sha256"], entry["members"])
    print("PASS_ALL_PINNED_SOURCE_OBJECTS_AND_MEMBERS", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=PACKAGE.parents[1])
    parser.add_argument("--out", type=Path, default=PACKAGE / "evidence")
    args = parser.parse_args()
    sources.require(__debug__, "Run with source assertions enabled; do not use -O.")
    repo, out = args.repo.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    check_sources(repo)
    receipts = {}
    for script, receipt, status in STAGES:
        subprocess.run([sys.executable, "-I", "-B", str(PACKAGE / script),
                        "--repo", str(repo), "--out", str(out)], check=True)
        result = json.loads((out / receipt).read_text())
        sources.require(result["status"] == status, "The check status differs: " + script)
        receipts[receipt] = result

    generated = receipts["GENERATION.json"]
    for name, record in generated["files"].items():
        sources.require(digest(out / name) == record["payload_sha256"],
                        "The generated native payload differs: " + name)
    global_check = receipts["GLOBAL-CHECKS.json"]
    for name, field in (("DATA-PHASES.json.gz", "data_phase_content_sha256"),
                        ("GLOBAL-BINDING.json.gz", "global_binding_content_sha256")):
        sources.require(digest(out / name) == global_check[field], "A global payload differs.")
    for name, pin in global_check["local_native_payload_content_sha256"].items():
        sources.require(digest(out / name) == pin, "A global native dependency differs.")
    for name, field in (("WALSH-RETARGET-REVIEW.json", "local_native_review_sha256"),
                        ("DOUBLED-WALSH-REVIEW.json", "doubled_native_review_sha256")):
        sources.require(digest(out / name) == global_check[field], "A global review dependency differs.")
    doubled = receipts["DILATION-INVOICE.json"]["dilations"][0]
    sources.require(doubled["factor"] == 2 and all(doubled["strict_checks"].values()),
                    "The twofold invoice is not admitted by its finite guards.")
    sources.require(global_check["paid_profile"] == doubled["profile"],
                    "The global operator profile and invoice differ.")
    sources.require((global_check["paid_rank"], global_check["rank_deficit"],
                     global_check["productive_endpoint_operators"]) ==
                    (doubled["rank_mass"], doubled["rank_deficit"], doubled["live"]),
                    "The global stock, mass, or deficit differs from its invoice.")

    artifacts = {name for _, name, _ in STAGES} | set(generated["files"])
    artifacts.update(("DATA-PHASES.json.gz", "GLOBAL-BINDING.json.gz"))
    result = {
        "status": "PASS_INVOLUTIVE_WALSH_LIFT_PACKAGE",
        "source_commit": sources.BASE,
        "source_manifest_sha256": digest(PACKAGE / "SOURCES.json"),
        "python": sys.version,
        "code_sha256": {p.name: digest(p) for p in sorted(PACKAGE.glob("*.py"))},
        "proof_sha256": {p.name: digest(p) for p in sorted(PACKAGE.glob("*.md"))},
        "artifact_content_sha256": {name: digest(out / name) for name in sorted(artifacts)},
        "checks": {name: receipts[name]["status"] for _, name, _ in STAGES},
        "complete_profile": global_check["paid_profile"],
        "dimension": 146, "productive_families": doubled["live"],
        "rank_mass": doubled["rank_mass"], "rank_deficit": doubled["rank_deficit"],
        "scope": "Exact local and global operator lift, complete unchanged-word finite invoice, and unchanged complex moment under the inherited all-size interfaces.",
        "not_claimed": ["A closed centre decoder or its native cost",
                        "A changed-word owner or invoice certificate",
                        "A flattened all-size instruction tape",
                        "A new kappa bound or a change of the selected frontier"],
    }
    (out / "REPLAY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    main()
