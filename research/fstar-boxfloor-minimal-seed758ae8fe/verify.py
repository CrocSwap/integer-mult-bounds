#!/usr/bin/env python3
"""KB5k registered replay: pins, box-floor falsifiers, Lemma LB2 checks, the
mixed-tau formula sweep, the v = 3 tau >= 1 min-box recomputation, and the
bounded tau >= 1 pivot at v = 5. Writes CERTIFICATE.json (newline="\\n").

Run: python3 -B verify.py
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VEND = os.path.join(HERE, "predecessor", "pr2978")
DATA = os.path.join(HERE, "data")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def check_pins():
    """The vendored PR 2978 tree must match its own two recorded pin sets."""
    n = 0
    pins = json.load(open(os.path.join(VEND, "predecessor", "pr2963",
                                       "predecessor", "PINS.json"),
                          encoding="utf-8"))
    for rel, want in sorted(pins["files"].items()):
        p = os.path.join(VEND, "predecessor", "pr2963", "predecessor", rel)
        assert sha256_file(p) == want, "pin mismatch: %s" % rel
        n += 1
    mine = json.load(open(os.path.join(VEND, "predecessor", "PINS.json"),
                          encoding="utf-8"))
    m = 0
    for rel, want in sorted(mine["files"].items()):
        p = os.path.join(VEND, "predecessor", rel)
        assert sha256_file(p) == want, "own pin mismatch: %s" % rel
        m += 1
    print("PASS_KM_PINS vendored-pr2963=%d vendored-own=%d" % (n, m))


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
    check_pins()
    run_script("box_floor_min.py", [
        "PASS_KM_FALSIFIER_V2 tau=0/0 cert=2 box=0 thr=1 independent=2/0",
        "PASS_KM_FALSIFIER_V3 tau=0/0/0 cert=3 box=0 thr=2 independent=3/0",
        "PASS_KM_FALSIFIER_V3B tau=1/0/0 cert=3 box=1 thr=2 independent=3/1",
        "PASS_KM_FALSIFIER_V4 tau=0/0/0/0 cert=4 box=0 thr=2 independent=4/0",
        "PASS_KM_LB2 configs=16761 ok=16761 random=160 ok=160",
        "PASS_KM_MIXEDTAU instances=240 violations=0",
        "PASS_KM_V3TAU1 configs=3023 candidates=27 min-box=2 thr=2",
        "PASS_KM_ALL",
    ])
    run_script("pivot_v5.py", [
        "PASS_KM_PIVOT_V5 tested=240 hits=0",
    ])
    digests = {}
    for f in ["data/km-receipt.json", "data/pivot-v5-receipt.json",
              "box_floor_min.py", "pivot_v5.py", "anchor_replay.py",
              "verify.py", "make_meta.py", "README.md", "TASK-CARD.md",
              "TASK.json"]:
        digests[f] = sha256_file(os.path.join(HERE, f))
    body = json.dumps(digests, indent=1, sort_keys=True) + "\n"
    cert = dict(schema_version=1, package="fstar-boxfloor-minimal-seed758ae8fe",
                markers=["PASS_KM_PINS", "PASS_KM_FALSIFIER_V2",
                         "PASS_KM_FALSIFIER_V3", "PASS_KM_FALSIFIER_V3B",
                         "PASS_KM_FALSIFIER_V4", "PASS_KM_LB2",
                         "PASS_KM_MIXEDTAU", "PASS_KM_V3TAU1",
                         "PASS_KM_PIVOT_V5", "PASS_KM_ALL"],
                digests=digests,
                certificate_digest=hashlib.sha256(
                    body.encode("utf-8")).hexdigest()[:16])
    with open(os.path.join(HERE, "CERTIFICATE.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(cert, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("PASS_KM_VERIFY falsifiers=4 lb2=16761 mixed=240 v3-configs=3023 "
          "pivot=240 digest=%s" % cert["certificate_digest"])


if __name__ == "__main__":
    main()
