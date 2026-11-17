# SPDX-License-Identifier: Apache-2.0
"""Recompute Sol's independent evidence and authenticate its scientific fields."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
LABELS = ("7605", "7642", "7643", "7644")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def evidence(report):
    assert report["status"] == "PASS_INDEPENDENT_FINITE_CHECK_SIGNED_OBLIGATIONS_OPEN"
    words = report["words"]
    base = words["7605"]
    erased = [entry[2:] for entry in base["returns_and_lifetimes"]]
    assert len(erased) == 74
    for word in words.values():
        assert [entry[2:] for entry in word["returns_and_lifetimes"]] == erased
        assert word["endpoint_sha256"] == base["endpoint_sha256"]
        assert word["private_ordered_read_count"] == 435
    assert all(row["changed_aligned_private_read_count"] == 0
               for row in report["literal_comparisons"].values())
    assert report["invoice"]["paid_calls"] == 110298
    assert report["invoice"]["target_calls"] == 22461
    assert set(report["mutation_controls"]) == {"charge", "chart_operand", "copy_operand", "phase"}
    assert report["contact_922"]["same_after_complete_contact"]
    assert len(report["private_ordered_reads_combined"]) == 435
    assert report["comparator_final_7644"]["precision_c"] == 2430
    # Source and evidence hashes remain in the stable payload. The interpreter
    # path, argv and file locations depend on the caller's checkout.
    stable = {k:v for k,v in report.items() if k not in ("argv", "cwd")}
    stable["comparator_final_7644"] = {k:v for k,v in report["comparator_final_7644"].items() if k != "path"}
    for group in ("inputs", "primitives"):
        stable[group] = {k:{a:b for a,b in v.items() if a != "path"}
                         for k,v in report[group].items()}
    return stable


def run():
    args = []
    inputs = PACKAGE / "inputs"
    for label in LABELS:
        args.extend(("--word" + label, inputs / (label + "-word.json.gz")))
    args.extend(("--combined", inputs / "combined.json.gz", "--caller", inputs / "7113-caller.json",
                 "--invoice7643", inputs / "7643-invoice.json", "--invoice7644", inputs / "7644-invoice.json",
                 "--primitives", PACKAGE / "closure/pr7644/retained/pr7605",
                 "--comparator-final", PACKAGE / "closure/pr7644/receipts/FINAL.json"))
    with tempfile.TemporaryDirectory(prefix="croc-independent-") as directory:
        output = Path(directory) / "independent.json"
        subprocess.run([sys.executable, "-I", "-B", HERE / "check.py", *args, "--out", output], check=True)
        stable = evidence(json.loads(output.read_bytes()))
        expected = json.loads((PACKAGE / "receipts/independent.json").read_bytes())
        actual = canonical(stable)
        assert hashlib.sha256(actual).hexdigest() == expected["scientific_sha256"]
        assert gzip.decompress((PACKAGE / "receipts" / expected["complete_receipt"]).read_bytes()) == actual
    print("PASS_COMPOSITION_BLIND_INDEPENDENT", flush=True)


if __name__ == "__main__":
    assert __debug__ and sys.version_info[:2] == (3,12)
    run()
