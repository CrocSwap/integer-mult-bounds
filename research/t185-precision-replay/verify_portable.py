#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent portability adapter for pinned PR2863; never edits its inputs.

Credit Dugongue/PR2863 for the five preserved finite mathematics checkers and
Yiyang/PR2857 for retained sources. This adapter is by digitalis-p with substantial
OpenAI Codex assistance. It does not claim that the original wrapper passes.
"""
import argparse
import gzip
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import zlib
from fractions import Fraction
from pathlib import Path

HEAD = "34328b1d5e5bebac62d5cabec993dfbfd7b2123f"
MANIFEST_SHA = "e1276c24fba1eb4c83ae040da63addad4a73f83120775ab40a79136c6080d59b"
RECOVERY = {".gitattributes", "vendor/pr2857/.gitattributes"}
RECOVERY_BYTES = b"* -text\n"
PAYLOAD_SHA = "7a972fdb2228dc04ca8319e2c3db26ee01a0c68ab86465b642100a35d72834dc"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def read(path):
    return json.loads(path.read_bytes())


def inventory(root):
    result = {}
    for path in root.rglob("*"):
        need(not path.is_symlink(), "source symlink")
        if path.is_file() and path != root / "MANIFEST.json":
            result[path.relative_to(root).as_posix()] = sha(path)
    return result


def authenticate(original, recovered):
    need(sha(original / "MANIFEST.json") == MANIFEST_SHA, "immutable manifest pin")
    need((original / "MANIFEST.json").read_bytes() ==
         (recovered / "MANIFEST.json").read_bytes(), "unchanged recovered manifest")
    pins = read(original / "MANIFEST.json")
    old = inventory(original)
    need(set(pins) - set(old) == RECOVERY, "exact published missing-file pattern")
    need(old == {key: value for key, value in pins.items() if key not in RECOVERY},
         "all present published source bytes and inventory")
    need(inventory(recovered) == pins, "complete recovered inventory and hashes")
    for name in RECOVERY:
        need(pins[name] == digest(RECOVERY_BYTES), "manifest recovery hash")
        need((recovered / name).read_bytes() == RECOVERY_BYTES, "exact recovered bytes")
    return pins


def gzip_payload_equal(reference, regenerated):
    expected = gzip.decompress(reference)
    actual = gzip.decompress(regenerated)
    need(actual == expected, "regenerated gzip payload mismatch")
    return expected


def must_reject(label, operation):
    try:
        operation()
    except (ValueError, OSError, EOFError, zlib.error):
        return {"control": label, "rejected": True}
    raise ValueError("negative control accepted: " + label)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--original", required=True, type=Path)
    ap.add_argument("--recovered", required=True, type=Path)
    ap.add_argument("--work", required=True, type=Path)
    args = ap.parse_args()
    original, root, work = [p.resolve() for p in
                            (args.original, args.recovered, args.work)]
    need(not sys.flags.optimize, "upstream component assertions must be enabled")
    need(not work.exists(), "fresh work directory required")
    for source in (original, root):
        need(not work.is_relative_to(source) and not source.is_relative_to(work),
             "work must be disjoint from immutable inputs")
    pins = authenticate(original, root)
    work.mkdir(parents=True)
    base = root / "vendor/pr2857"
    commands = [
        ("construct", [root / "reproduce_t185.py", "--baseline", base,
                       "--relay-plan", root / "RELAY-PLAN.json", "--out", work / "constructed"]),
        ("owners", [root / "tools/audit_owners2857.py", "--source-package", base,
                    "--candidate", root / "data", "--out", work / "OWNERS.json"]),
        ("moment", [root / "tools/audit_moment2857.py", "--source", base,
                    "--candidate", root / "data", "--out", work / "MOMENT.json"]),
        ("separate-review", [root / "review/review_current.py", "--package", base,
                             "--candidate", root / "data", "--claim", root / "CLAIM.json",
                             "--field", "kappa", "--out", work / "REVIEW.json"]),
        ("exact-optimality", [root / "review/profile_lp_certificate.py", "--package", base,
                              "--candidate-profile", root / "data/PROFILE.json",
                              "--out", work / "lp"]),
    ]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               PYTHONINTMAXSTRDIGITS="0", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    stages = []
    for name, command in commands:
        log = work / (name + ".log")
        started = time.monotonic()
        argv = [sys.executable, "-B", *map(str, command)]
        with log.open("w", encoding="utf-8", newline="\n") as stream:
            result = subprocess.run(argv, cwd=work, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, check=False)
        stages.append({"name": name, "command": argv, "exit_code": result.returncode,
                       "seconds": time.monotonic() - started, "log_sha256": sha(log),
                       "entry_script_sha256": sha(command[0]),
                       "complete_authenticated_input_manifest_sha256": MANIFEST_SHA,
                       "fresh_execution": True})
        need(result.returncode == 0, "upstream component failed: " + name)
        print("PASS fresh " + name, flush=True)
    comparisons = {}
    for name in ("ORDER.json", "DISPATCH.json", "PROVIDERS.json", "PROFILE.json"):
        a, b = (root / "data" / name).read_bytes(), (work / "constructed" / name).read_bytes()
        need(a == b, "regenerated exact data mismatch: " + name)
        comparisons[name] = {"byte_equal": True, "sha256": digest(a), "bytes": len(a)}
    a = (root / "data/FILL.json.gz").read_bytes()
    b = (work / "constructed/FILL.json.gz").read_bytes()
    payload = gzip_payload_equal(a, b)
    need(digest(payload) == PAYLOAD_SHA, "independently recorded payload pin")
    offsets = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    comparisons["FILL.json.gz"] = {
        "container_byte_equal": a == b, "stored_sha256": digest(a),
        "regenerated_sha256": digest(b), "stored_bytes": len(a), "regenerated_bytes": len(b),
        "differing_shared_offsets_count": len(offsets), "first_differing_shared_offsets": offsets[:64],
        "stored_header_hex": a[:10].hex(), "regenerated_header_hex": b[:10].hex(),
        "payload_byte_equal": True, "payload_bytes": len(payload), "payload_sha256": digest(payload)}
    # Positive container control retains every payload byte. The malicious control
    # alters an actual call/time coordinate, then recomputes a valid CRC/ISIZE.
    header_only = bytearray(a)
    header_only[9] = 3 if a[9] != 3 else 255
    need(gzip_payload_equal(a, bytes(header_only)) == payload, "OS header positive control")
    malicious = json.loads(payload)
    need(isinstance(malicious["rows"][0][0], int), "known row call coordinate")
    before = malicious["rows"][0][0]
    malicious["rows"][0][0] += 1
    forged = gzip.compress(json.dumps(malicious, separators=(",", ":")).encode(), mtime=0)
    controls = [
        must_reject("valid gzip with altered first owner-row call coordinate",
                    lambda: gzip_payload_equal(a, forged)),
        must_reject("truncated gzip trailer", lambda: gzip_payload_equal(a, a[:-1])),
        must_reject("immutable stored container cannot be replaced by header variant",
                    lambda: need(digest(bytes(header_only)) == pins["data/FILL.json.gz"],
                                 "stored container pin changed")),
    ]
    claim, admission, release, native, moment, lp = [read(p) for p in [
        root / "CLAIM.json", root / "evidence/ADMISSION-RESULT.json",
        root / "evidence/RELEASE-RECEIPT.json", root / "evidence/NATIVE-RESULT.json",
        work / "MOMENT.json", work / "lp/RESULT.json"]]
    need(admission["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE"
         and release["status"] == "PASS_RELEASE", "stored complete release statuses")
    need(Fraction(claim["kappa"]) == Fraction(admission["kappa"]) ==
         Fraction(release["kappa_decimal"]) == Fraction(moment["target"]), "exact headline binding")
    need(sha(root / "evidence/RELEASE-RECEIPT.json") == admission["release_receipt_sha256"] ==
         claim["release_receipt_sha256"], "complete release receipt binding")
    need(sha(root / "evidence/NATIVE-RECEIPT.json") == native["native_receipt_sha256"] ==
         claim["native_receipt_sha256"] == admission["native_receipt_sha256"], "native binding")
    need(lp["status"] == "PASS_EXACT_CURRENT_INVENTORY_PRIMAL_DUAL_AND_ACTUAL_ATTAINMENT"
         and lp["pattern_count"] == 1163, "fixed-model optimum binding")
    need(authenticate(original, root) == pins, "source drift")
    outputs = {p.relative_to(work).as_posix(): sha(p) for p in sorted(work.rglob("*")) if p.is_file()}
    result = {
        "status": "PASS_INDEPENDENT_PORTABLE_FINITE_REPLAY",
        "source_head": HEAD, "source_manifest_sha256": MANIFEST_SHA,
        "source_manifest_entries": len(pins), "recovered_files": sorted(RECOVERY),
        "recovered_bytes_hex": RECOVERY_BYTES.hex(), "recovery_sha256": digest(RECOVERY_BYTES),
        "stages": stages, "data_comparisons": comparisons, "negative_controls": controls,
        "positive_controls": ["OS header variation accepted with identical complete payload"],
        "altered_owner_row_call_before": before, "altered_owner_row_call_after": before + 1,
        "output_sha256": outputs, "verifier_sha256": sha(Path(__file__).resolve()),
        "runtime": {"python": sys.version, "executable": sys.executable,
                    "platform": platform.platform(), "zlib_build": zlib.ZLIB_VERSION,
                    "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION},
        "original_wrapper_status": "FAIL: missing two manifested files; after exact recovery, gzip-container byte comparison fails on Python3.12/Linux",
        "scope": "Fresh execution of five preserved finite mathematical stages plus complete byte/hash and unchanged output bindings. Immutable inputs remain strictly byte-hashed; only regenerated gzip comparison uses exact decompressed bytes per CONTRIBUTING. Original wrapper is unchanged and is not claimed to pass. Stored native/outer receipts are authenticated, not freshly reproduced here. All inherited asymptotic conditions remain.",
    }
    (work / "RESULT.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    main()
