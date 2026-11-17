#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reconstruct the 134/329 contact edit and replay the complete native and signed application."""

import argparse
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
RECEIPTS = ROOT / "receipts"
REMOTE = "https://github.com/CrocSwap/integer-mult-bounds.git"
HEADS = {
    7605: "e1d2756eecf03e146338239fee81772a99ba8d4c",
    7642: "d7f82810689ed2cd649ec9aaaf3b1485b585c82e",
}
PACKAGES = {
    7605: Path("research/p104-timed-helper757"),
    7642: Path("research/p104-main46-original-clear"),
}
OLD_WORD = "aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916"
NEW_WORD = "dcd797e45b6d4b74411a8a73a9b6e8247bb2ea8744924332b0dd43db3e219f02"
GZIP_OBSERVATIONS = {"incumbent_gzip_sha256_observed", "candidate_gzip_sha256"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(checkout, *args):
    return subprocess.check_output(["git", "-C", str(checkout), *args], text=True, timeout=120).strip()


def source_checkout(pr, explicit, work):
    root = explicit.resolve() if explicit else work / f"source-{pr}"
    if explicit is None:
        root.mkdir()
        git(root, "init", "-q")
        git(root, "remote", "add", "source", REMOTE)
        git(root, "config", "remote.source.promisor", "true")
        git(root, "config", "remote.source.partialclonefilter", "blob:none")
        git(root, "sparse-checkout", "set", "--no-cone", f"/{PACKAGES[pr]}/")
        git(root, "fetch", "-q", "--no-tags", "--depth=1", "--filter=blob:none", "source", HEADS[pr])
        require(git(root, "rev-parse", "FETCH_HEAD") == HEADS[pr], f"Inexact fetch for #{pr}")
        git(root, "checkout", "--detach", "-q", HEADS[pr])
    require(git(root, "rev-parse", "HEAD") == HEADS[pr], f"Wrong source checkout for #{pr}")
    require(not git(root, "status", "--porcelain", "--untracked-files=all", "--", str(PACKAGES[pr])),
            f"Modified source package for #{pr}")
    require((root / PACKAGES[pr]).is_dir(), f"Missing package for #{pr}")
    return root


def run(work, name, script, *args, timeout):
    stdout, stderr = work / f"{name}.stdout", work / f"{name}.stderr"
    with stdout.open("xb") as out, stderr.open("xb") as err:
        result = subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)],
                                stdout=out, stderr=err, timeout=timeout)
    if result.returncode:
        sys.stderr.buffer.write(stderr.read_bytes())
        sys.stderr.buffer.write(stdout.read_bytes())
        result.check_returncode()
    print(f"PASS {name}", flush=True)
    return stdout


def require_word(path, expected):
    require(sha256(decompress(path.read_bytes())).hexdigest() == expected,
            f"Canonical word digest differs for {path.name}")


def require_json(actual, expected, *, container_observations=()):
    fresh = json.loads(actual.read_bytes())
    sealed = json.loads(expected.read_bytes())
    for key in container_observations:
        fresh.pop(key, None)
        sealed.pop(key, None)
    require(fresh == sealed, f"Fresh receipt differs from {expected.name}")


def reconstruct_7642(work, source_7605, source_7642):
    package = source_7642 / PACKAGES[7642]
    run(work, "verify-7642", package / "verify.py", timeout=30)
    # This published runner checks the exact #7605 138-file source closure.
    finite = work / "predecessor-finite"
    run(work, "finite-7642", package / "replay.py", "--source-checkout", source_7605,
        "--work", finite, "--finite-only", timeout=180)
    old_word = finite / "word.json.gz"
    require_word(old_word, OLD_WORD)
    return package, finite, old_word


def main():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12) or not __debug__:
        raise ValueError("Use CPython 3.12 with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True, help="a new evidence directory")
    parser.add_argument("--source-7605", type=Path, help="existing checkout at the exact #7605 head")
    parser.add_argument("--source-7642", type=Path, help="existing checkout at the exact #7642 head")
    parser.add_argument("--prepare-only", action="store_true", help="stop before starting native replay")
    args = parser.parse_args()

    work = args.work.resolve()
    work.mkdir()
    src_7605 = source_checkout(7605, args.source_7605, work)
    src_7642 = source_checkout(7642, args.source_7642, work)
    pkg_7642, finite, old_word = reconstruct_7642(work, src_7605, src_7642)
    candidate = work / "word.json.gz"
    phase = run(work, "contact-phase", ROOT / "checks/replay_contact_phase.py",
                "--word", old_word, "--round305", ROOT / "round305",
                "--engine-root", src_7605 / PACKAGES[7605] / "retained/role902/independent/engines",
                "--candidate", candidate, timeout=65)
    require_word(candidate, NEW_WORD)
    require_json(phase, RECEIPTS / "PHASE.json", container_observations=GZIP_OBSERVATIONS)

    recount = work / "recount"
    recount.mkdir()
    run(work, "signed-invoice-recount", ROOT / "checks/recount307.py", "--baseline", old_word,
        "--candidate", candidate, "--source-7605", src_7605, "--source-7642", src_7642,
        "--phase", RECEIPTS / "PHASE.json", "--output", recount, timeout=35)
    require_json(recount / "RECOUNT.json", RECEIPTS / "RECOUNT.json")
    require_json(recount / "invoice-new.json", RECEIPTS / "invoice-new.json")

    old_overlay = work / "overlay-7642"
    run(work, "prepare-7642", pkg_7642 / "application/prepare_overlay.py",
        "--source-checkout", src_7605, "--overlay", old_overlay, "--candidate", old_word,
        "--peer-edits", pkg_7642 / "inputs/edits7610.json", "--invoice-receipt", finite / "INVOICE.json",
        timeout=35)
    old_app = old_overlay / "application.py"
    old_patch = old_overlay / "application-checked.py"
    run(work, "adapt-native-7642", pkg_7642 / "application/patch_native.py", old_app,
        "--output", old_patch, "--receipt", work / "NATIVE-PATCH-7642.json", timeout=20)
    old_patch.replace(old_app)
    for artifact in ("NATIVE.json", "SIGNED.json", "FINAL.json"):
        copyfile(pkg_7642 / "receipts" / artifact, old_overlay / "data" / artifact)

    overlay = work / "overlay"
    run(work, "prepare-contact", ROOT / "application/prepare_307.py",
        "--overlay-7642", old_overlay, "--output", overlay, "--candidate", candidate,
        "--contact", ROOT / "round305/gate.json", "--invoice", recount / "invoice-new.json",
        timeout=35)
    app = overlay / "application.py"
    patch = overlay / "application-checked.py"
    run(work, "adapt-native-contact", ROOT / "application/patch_native307.py", app,
        "--output", patch, "--receipt", work / "NATIVE-PATCH-CONTACT.json", timeout=20)
    patch.replace(app)
    if args.prepare_only:
        print("PASS exact contact, phase, invoice and overlay preparation", flush=True)
        return

    for artifact in ("NATIVE.json", "SIGNED.json", "FINAL.json"):
        copyfile(RECEIPTS / artifact, overlay / "data" / artifact)
    for stage in ("native", "signed"):
        run(work, f"complete-{stage}", ROOT / "application/run_stage.py", stage, "--overlay", overlay,
            "--work", work / stage, timeout=500)
    require_json(work / "signed/FINAL.json", RECEIPTS / "FINAL.json")
    print("PASS full 134/329 conditional native and signed application", flush=True)


if __name__ == "__main__":
    main()
