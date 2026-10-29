#!/usr/bin/env python3
"""KB5L registered replay: pins, the exact v = 5 tau >= 1 floor chain, the
realizable replay and hunt, and the shareable-class replay + cap push.
Writes CERTIFICATE.json (newline="\\n").

Run: python3 -B verify.py
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def check_pins():
    """The vendored PR 3012 tree must match the recorded pin set."""
    pins = json.load(open(os.path.join(HERE, "predecessor", "PINS.json"),
                          encoding="utf-8"))
    n = 0
    for rel, want in sorted(pins["files"].items()):
        p = os.path.join(HERE, "predecessor", rel)
        assert sha256_file(p) == want, "pin mismatch: %s" % rel
        n += 1
    print("PASS_KL_PINS vendored-pr3012=%d" % n)
    return n


def run_script(name, markers):
    proc = subprocess.run([sys.executable, "-B", os.path.join(HERE, name)],
                          capture_output=True, text=True, encoding="utf-8",
                          cwd=HERE, timeout=560)
    out = proc.stdout
    assert proc.returncode == 0, (name, proc.returncode, proc.stderr[-2000:])
    missing = [mk for mk in markers if mk not in out]
    assert not missing, "%s missing markers %s" % (name, missing)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(DATA, exist_ok=True)
    npins = check_pins()
    run_script("floor_v5.py", [
        "PASS_KL_PIN configs=400 brute-equals-ladder=400",
        "PASS_KL_V5 configs=749398 cheap=749347 exact=18 "
        "envelope-box2-families=33",
        "PASS_KL_REALIZABLE_V5 instances=120 violations=0",
        "PASS_KL_ALL v5-configs=749398 envelope-families=33 realizable=120",
    ])
    run_script("family_v5.py", [
        "PASS_KL_PROBE model-ok=142 tau>=1-all=0",
        "PASS_KL_SHAPES shapes=6 screen-rejected=15",
        "PASS_KL_HUNT tested=35 hits=0",
        "PASS_KL_FAMILY_ALL shapes=6 hunt-tested=35 hunt-hits=0",
    ])
    run_script("shareable_v3.py", [
        "PASS_KJ_V3 configs=3023 box-equals-cert=2996 candidates=27",
        "PASS_KL_SHAREABLE candidates=27 replay="
        '{"not-found-in-cap": 21, "realized": 3, "unrealizable-column": 3}',
        "PASS_KL_SHAREABLE candidates=27 replay=",
    ])
    digests = {}
    for f in ["data/floor-v5-receipt.json", "data/family-v5-receipt.json",
              "data/shareable-v3-receipt.json", "floor_v5.py", "family_v5.py",
              "shareable_v3.py", "verify.py", "make_meta.py", "README.md",
              "TASK-CARD.md", "TASK.json"]:
        digests[f] = sha256_file(os.path.join(HERE, f))
    body = json.dumps(digests, indent=1, sort_keys=True) + "\n"
    cert = dict(schema_version=1, package="fstar-boxfloor-v5-seedab80f07c",
                markers=["PASS_KL_PINS", "PASS_KL_PIN", "PASS_KL_V5",
                         "PASS_KL_REALIZABLE_V5", "PASS_KL_ALL",
                         "PASS_KL_PROBE", "PASS_KL_SHAPES", "PASS_KL_HUNT",
                         "PASS_KL_FAMILY_ALL", "PASS_KJ_V3",
                         "PASS_KL_SHAREABLE"],
                digests=digests,
                certificate_digest=hashlib.sha256(
                    body.encode("utf-8")).hexdigest()[:16])
    with open(os.path.join(HERE, "CERTIFICATE.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(cert, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("PASS_KL_VERIFY v5-configs=749398 families=33 shapes=6 "
          "realizable=120 hunt=35 shareable=27 pins=%d digest=%s"
          % (npins, cert["certificate_digest"]))


if __name__ == "__main__":
    main()
