#!/usr/bin/env python3
"""Relocation and proof-relevant source/receipt failure controls. Apache-2.0."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def run(script, cwd, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(script), *map(str, args)],
                          cwd=cwd, text=True, capture_output=True, timeout=30)


def main():
    with tempfile.TemporaryDirectory(prefix="dyadic-connector-check-") as temporary:
        root = Path(temporary) / "relocated"
        target = root / "research" / PACKAGE.name
        target.mkdir(parents=True)
        for name in ("verify.py", "SOURCES.json", "CERTIFICATE.json"):
            shutil.copyfile(PACKAGE / name, target / name)
        pins = json.loads((PACKAGE / "SOURCES.json").read_text())
        for item in pins["files"]:
            if item["usage"] == "input":
                path = root / item["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / item["path"], path)
        for path in root.rglob("*"):
            if path.is_file():
                path.chmod(0o444)
        before = inventory(root)
        ok = run(target / "verify.py", temporary)
        require(ok.returncode == 0 and "PASS_COMPLEX_DYADIC_CONNECTOR" in ok.stdout,
                "relocated optimized replay failed: " + ok.stderr)
        require(inventory(root) == before, "default verification wrote a file")

        original = json.loads((target / "CERTIFICATE.json").read_text())
        corruptions = []
        wrong_bill = json.loads(json.dumps(original))
        wrong_bill["selected_fixture"]["root_scalings"] = 0
        corruptions.append(wrong_bill)
        wrong_word = json.loads(json.dumps(original))
        wrong_word["words"]["B0"][0][2] *= -1
        corruptions.append(wrong_word)
        wrong_bound = json.loads(json.dumps(original))
        wrong_bound["twelve_query_reduction_census"]["full_hits"] = 1
        corruptions.append(wrong_bound)
        for i, data in enumerate(corruptions):
            receipt = Path(temporary) / ("bad-receipt-" + str(i) + ".json")
            receipt.write_text(json.dumps(data))
            bad = run(target / "verify.py", temporary, "--certificate", receipt)
            require(bad.returncode != 0 and "certificate differs from exact replay" in bad.stderr,
                    "corrupted certificate accepted")
        source = root / "research/weighted-signed-connector-seed58/CERTIFICATE.json"
        source.chmod(0o644)
        source.write_bytes(source.read_bytes() + b"\n")
        bad = run(target / "verify.py", temporary)
        require(bad.returncode != 0 and "source drift:" in bad.stderr, "source drift accepted")
    print("PASS_DYADIC_CONNECTOR_PACKAGE relocation=1 read_only=1 receipt_controls=3 source_controls=1")


if __name__ == "__main__":
    main()
