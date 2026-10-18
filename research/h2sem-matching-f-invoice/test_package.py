#!/usr/bin/env python3
"""Relocation smoke and corruption controls for h2sem-matching-f-invoice."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PASS = "PASS_H2SEM_MATCHING_F_INVOICE"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(args, cwd, expect_ok):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)
    ok = proc.returncode == 0 and PASS in proc.stdout
    if expect_ok:
        need(ok, "expected PASS, got code=%s out=%r err=%r"
             % (proc.returncode, proc.stdout[-500:], proc.stderr[-500:]))
    else:
        need(not ok, "corrupt package unexpectedly passed")
    return proc


def main():
    with tempfile.TemporaryDirectory(prefix="h2sem-matching-f-") as tmp:
        tmp = Path(tmp)
        dest_root = tmp / "repo with spaces"
        pkg = dest_root / "research" / "h2sem-matching-f-invoice"
        pkg.parent.mkdir(parents=True)

        shutil.copytree(HERE, pkg)
        pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
        for item in pins["files"]:
            src = ROOT / item["path"]
            target = dest_root / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)

        py = sys.executable
        run([py, "-I", "-B", str(pkg / "verify.py")], dest_root, True)

        # Corruption 1: mutate a live input pin byte.
        word = dest_root / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
        blob = bytearray(word.read_bytes())
        blob[0] ^= 0xFF
        word.write_bytes(blob)
        run([py, "-I", "-B", str(pkg / "verify.py")], dest_root, False)
        shutil.copy2(ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz", word)

        # Corruption 2: mutate certificate F bill.
        cert = pkg / "CERTIFICATE.json"
        data = json.loads(cert.read_text(encoding="utf-8"))
        data["bills"]["match7"]["F"] += 1
        cert.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        run([py, "-I", "-B", str(pkg / "verify.py")], dest_root, False)
        shutil.copy2(HERE / "CERTIFICATE.json", cert)

        # Corruption 3: mutate MATCHING7 pair list.
        matching = pkg / "MATCHING7.json"
        mdata = json.loads(matching.read_text(encoding="utf-8"))
        mdata["pairs"] = mdata["pairs"][:-1]
        mdata["pair_count"] = len(mdata["pairs"])
        matching.write_text(json.dumps(mdata, indent=2) + "\n", encoding="utf-8")
        run([py, "-I", "-B", str(pkg / "verify.py")], dest_root, False)
        shutil.copy2(HERE / "MATCHING7.json", matching)

        # Corruption 4: Boolean substituted for integer rank_mass.
        data = json.loads(cert.read_text(encoding="utf-8"))
        data["rank_mass"] = True
        cert.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        run([py, "-I", "-B", str(pkg / "verify.py")], dest_root, False)
        shutil.copy2(HERE / "CERTIFICATE.json", cert)

        # Corruption 5: on-disk certificate duplicate-key style — drop a control.
        data = json.loads(cert.read_text(encoding="utf-8"))
        data["controls"] = data["controls"][:-1]
        cert.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        run([py, "-I", "-B", str(pkg / "verify.py")], dest_root, False)

    print("PASS_H2SEM_MATCHING_F_INVOICE_PACKAGE_CONTROLS relocation=1 corruptions=5")


if __name__ == "__main__":
    main()
