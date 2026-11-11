"""Bind the cited complex suppliers of data/complex-b-nine.json to the PRs' own receipts (vendored byte-identical,
git blob ids in SOURCE-pr386.json, SOURCE-pr425.json, SOURCE-pr431.json): b and the PR's own kappa must equal the
receipt fields exactly.
usage: cited.py COMPLEX_B.json CONTROLS_DIR
Prepared by eumemic with Anthropic Claude assistance; Apache-2.0."""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

cited = {s["name"]: s for s in json.loads(Path(sys.argv[1]).read_text())["suppliers"]}
d = Path(sys.argv[2])
receipts = {
    "pr386": (d / "pr386/COMBINED.json", "complex_coarse", "kappa", "PASS_CONDITIONAL_COMBINED_KAPPA_ABOVE_2_POW_MINUS_10"),
    "pr425": (d / "pr425/FINAL.json", "complex_b", "kappa", "PASS_FRESH_CONDITIONAL_MUTABLE_BASIS_HAMMING_COMPLEX"),
    "pr431": (d / "pr431/VALIDATION-LOCAL.json", "complex_b", "kappa", "PASS_FULL_HAMMING_FRAME_RETIMING_AND_SOURCE425_REPLAY"),
}
assert set(cited) == set(receipts)
for name, (path, kb, kk, status) in receipts.items():
    r = json.loads(path.read_text())
    assert r["status"] == status, (name, r["status"])
    assert Q(r[kb]) == Q(cited[name]["b"]) and Q(r[kk]) == Q(cited[name]["kappa_with_pr370_bit"]), name
    bit = r.get("bit_c", r.get("bit_coarse"))
    assert Q(bit) == Q(1057833103534317, 10 ** 18), (name, bit)
    print("   %s: b = %s and kappa = %s equal %s/%s (status %s; paired there with PR #370's bit c = %s)"
          % (name, cited[name]["b"], cited[name]["kappa_with_pr370_bit"], path.parent.name, path.name, status, bit))
