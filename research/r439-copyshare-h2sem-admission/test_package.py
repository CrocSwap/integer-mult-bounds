#!/usr/bin/env python3
"""Package-level controls: relocation replay plus real on-disk corruption rejection."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
NEED = ["research/e8-bit-p111-tuned/code/xcheck_p.py",
        "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"]


def run(pkg, expect_ok):
    proc = subprocess.run([sys.executable, "-I", "-B", str(pkg / "verify.py")],
                          capture_output=True, text=True)
    if expect_ok:
        if proc.returncode != 0:
            raise ValueError("relocated replay failed: " + proc.stderr[-500:])
        if "PASS_R439_COPYSHARE_H2SEM_ADMISSION" not in proc.stdout:
            raise ValueError("relocated replay missing PASS line")
    else:
        if proc.returncode == 0:
            raise ValueError("corrupted replay was accepted")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        pkg = base / "research/r439-copyshare-h2sem-admission"
        shutil.copytree(HERE, pkg)
        for name in NEED:
            dst = base / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dst)
        run(pkg, True)  # positive fixture at a fresh location

        victim = base / NEED[1]
        blob = bytearray(victim.read_bytes())
        blob[len(blob) // 2] ^= 0x01
        victim.write_bytes(bytes(blob))
        run(pkg, False)  # source corruption rejected by the pin block
        shutil.copyfile(ROOT / NEED[1], victim)

        cert = pkg / "CERTIFICATE.json"
        data = json.loads(cert.read_text())
        data["baseline_d_source_reads"] += 1
        cert.write_text(json.dumps(data, indent=2) + "\n")
        run(pkg, False)  # receipt corruption rejected by certificate comparison

        missing = pkg / "SOURCES.json"
        missing.unlink()
        run(pkg, False)  # missing pins rejected
    print("PASS_TEST_PACKAGE_R439_COPYSHARE_H2SEM relocation=ok controls=3")


if __name__ == "__main__":
    main()
