#!/usr/bin/env python3
"""Verify the bit-leaf-bootstrap-189 record composition and the next supplier.

Checks every pinned input and package file against SOURCE.json, re-runs the
assembly harness on the vendored PR194 inputs, compares the regenerated result
with certificate.json, and then re-prices the vendored PR200 bit supplier with
the same bootstrap, comparing against next-composition-result.json.

    python3 -B research/bit-leaf-bootstrap-189/verify.py
"""
import hashlib, json, subprocess, sys
from pathlib import Path
from fractions import Fraction as Q

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = HERE / ".work"
PR197_KAPPA = Q(135216063303877, 200000000000000000)     # current published best


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args):
    subprocess.run([sys.executable, "-B"] + [str(x) for x in args], check=True)


def main():
    if sys.flags.optimize:
        raise SystemExit("refusing -O")
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    manifest = json.loads((HERE / "SOURCE.json").read_text())
    drift = sorted(rel for rel, digest in manifest["files"].items()
                   if sha(ROOT / rel) != digest)
    assert not drift, ("pinned input drift", drift)
    WORK.mkdir(exist_ok=True)

    result = HERE / "bootstrap-result.json"
    if result.exists():
        result.unlink()
    run([HERE / "assemble_bootstrap.py",
         "--pr194", ROOT / "research/source-assisted-v4",
         "--pr189", ROOT / "research/paired-cube-twin-local-168",
         "--pin-tarball", ROOT / "research/source-assisted/public/pr168_fd25adb7.tar.gz",
         "--depths", "0", "1", "2", "3"])
    actual = json.loads(result.read_text())
    assert actual == json.loads((HERE / "certificate.json").read_text()), \
        "regenerated result differs from certificate.json"
    assert actual["record_kappa"] == "1668581/2500000000", "PR194 reproduction"
    for depth, row in actual["depths"].items():
        assert row["constraints"] == 47 and row["margins"] == 7, depth
    assert actual["depths"]["0"]["kappa"] == actual["record_kappa"]
    best = actual["best"]

    # The next supplier: PR200's bit word, priced by the same bootstrap.
    generated = WORK / "next-composition-result.json"
    run([HERE / "next_bit_composition.py",
         "--bit-certificate", HERE / "inputs/pr200-bit-certificate.json",
         "--complex-certificate", ROOT / "research/source-assisted-v4/certificate.json",
         "--pr184", ROOT / "research/source-assisted/global/assemble_profiles.py",
         "--pin-tarball", ROOT / "research/source-assisted/public/pr168_fd25adb7.tar.gz",
         "--work", WORK,
         "--out", generated])
    nxt = json.loads(generated.read_text())
    assert nxt == json.loads((HERE / "next-composition-result.json").read_text()), \
        "regenerated next-composition differs from next-composition-result.json"
    for depth, row in nxt["depths"].items():
        assert row["binding"] == "bit", depth
    next_best = Q(nxt["best"]["kappa"])
    assert next_best > PR197_KAPPA, "next composition does not beat #197"
    assert Q(nxt["depths"]["0"]["kappa"]) == Q(6768823, 10**10), \
        "legacy pricing of PR200's bit supplier"

    print("PASS pinned inputs, exact PR194 reproduction, bootstrap depths 0-3, "
          "47 strict constraints and 7 margins per depth")
    print("record kappa=" + best["kappa"] + " (" + repr(best["kappa_decimal"]) + "), "
          "gain vs PR194 = {:+.4f}%".format(best["gain_vs_record"] * 100))
    print("next composition (PR200 bit + bootstrap) kappa=" + nxt["best"]["kappa"] +
          " (" + repr(nxt["best"]["kappa_decimal"]) + "), "
          "gain vs #197 = {:+.4f}%".format(float(next_best / PR197_KAPPA - 1) * 100))
    print("Physical words are inherited pinned inputs; this command does not replay them.")


if __name__ == "__main__":
    main()
