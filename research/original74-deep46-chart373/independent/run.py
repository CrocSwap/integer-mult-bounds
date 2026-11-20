# SPDX-License-Identifier: Apache-2.0
"""Replay the independent checks using the two authenticated signed invoices."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent


def run():
    inputs = PACKAGE / "inputs"
    for number in ("7645", "7657"):
        signed = json.loads((PACKAGE / "sources" / number / "evidence/SIGNED-RESULT.json").read_bytes())
        invoice = json.loads((inputs / (number + "-invoice.json")).read_bytes())
        assert invoice == signed["price"]["after"]
    result = subprocess.check_output([
        sys.executable, "-I", "-B", str(HERE / "verify_word.py"),
        "--base", inputs / "peer7657.json.gz", "--secondary", inputs / "base7645.json.gz",
        "--candidate", inputs / "candidate.json.gz", "--caller", inputs / "caller.json",
        "--invoice7645", inputs / "7645-invoice.json", "--invoice7657", inputs / "7657-invoice.json",
    ])
    evidence = json.loads(result)
    archived = gzip.decompress((PACKAGE / "receipts/independent.json.gz").read_bytes())
    assert evidence == json.loads(archived)
    assert evidence["status"] == "PASS_INDEPENDENT_NATIVE_AND_INVOICE_DELTA"
    assert evidence["literal"]["arbitrary_input_endpoints"] == 1501
    assert evidence["mutation_controls"]["missing_charge"]["rejected"]
    assert evidence["mutation_controls"]["altered_primary_contact_coefficient"]["endpoint_difference"]
    print("PASS_INDEPENDENT_ORIGINAL74_COURIER_CONTACT", hashlib.sha256(archived).hexdigest(), flush=True)


if __name__ == "__main__":
    assert __debug__ and sys.version_info[:2] == (3, 12)
    run()
