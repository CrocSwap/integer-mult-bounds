#!/usr/bin/env python3
"""Verify the bit-leaf-bootstrap-189 record composition.

Checks every pinned input and package file against SOURCE.json, re-runs the
assembly harness on the vendored inputs, and compares the regenerated result
with the canonical certificate.json.

    python3 -B research/bit-leaf-bootstrap-189/verify.py
"""
import hashlib, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    if sys.flags.optimize:
        raise SystemExit("refusing -O")
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    manifest = json.loads((HERE / "SOURCE.json").read_text())
    drift = sorted(rel for rel, digest in manifest["files"].items()
                   if sha(ROOT / rel) != digest)
    assert not drift, ("pinned input drift", drift)
    result = HERE / "bootstrap-result.json"
    if result.exists():
        result.unlink()
    subprocess.run([sys.executable, "-B", str(HERE / "assemble_bootstrap.py"),
                    "--pr194", str(ROOT / "research/source-assisted-v4"),
                    "--pr189", str(ROOT / "research/paired-cube-twin-local-168"),
                    "--pin-tarball",
                    str(ROOT / "research/source-assisted/public/pr168_fd25adb7.tar.gz"),
                    "--depths", "0", "1", "2", "3"], check=True)
    actual = json.loads(result.read_text())
    expected = json.loads((HERE / "certificate.json").read_text())
    assert actual == expected, "regenerated result differs from certificate.json"
    assert actual["record_kappa"] == "1668581/2500000000", "PR194 reproduction"
    best = actual["best"]
    for depth, row in actual["depths"].items():
        assert row["constraints"] == 47 and row["margins"] == 7, depth
    assert actual["depths"]["0"]["kappa"] == actual["record_kappa"]
    print("PASS pinned inputs, exact PR194 reproduction, bootstrap depths 0-3, "
          "47 strict constraints and 7 margins per depth")
    print("kappa=" + best["kappa"] + " (" + repr(best["kappa_decimal"]) + ")")
    print("gain vs PR194 = {:+.4f}%".format(best["gain_vs_record"] * 100))
    print("Physical words are inherited pinned inputs; this command does not replay them.")


if __name__ == "__main__":
    main()
