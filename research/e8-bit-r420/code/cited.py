"""Bind every cited complex b in data/complex-b.json to the cited PR's own receipt (vendored byte-identical or on
main; see code/provenance.py), and check the receipts this package compares against.
usage: cited.py PACKAGE_DIR
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

root = Path(sys.argv[1])
t = json.loads((root / "data/complex-b.json").read_text())
for s in t["suppliers"]:
    r = json.loads((root / s["receipt"]).read_text())
    assert Q(r[s["field"]]) == Q(s["b"]), (s["name"], r[s["field"]], s["b"])
    print("   PR #%d (%s) b = %s = %.15e  [%s]" % (s["pr"], s["author"], s["b"], float(Q(s["b"])), s["role"].split(" (")[0]))
e535 = json.loads((root / "data/complex/pr535/EXPECTED.json").read_text())
a535 = json.loads((root / "data/complex/pr535/EXACT-ASSEMBLY-PR493.json").read_text())
e510 = json.loads((root / "vendor/pr510/e8-r480-nine-stage/EXPECTED.json").read_text())
e531 = json.loads((root / "../direct-delivery504-global/EXPECTED.json").read_text())
assert e535["bit_lower"] == e510["nine"]["bit_lower"] and e535["binding_component"] == "bit"
assert a535["complex_lower"] == e535["complex_lower"] and a535["binding_component"] == "bit"
assert e531["binding_component"] == "complex"
print("   PR #535 receipt: kappa %s, bit-bound at PR #510's c = %s; with PR #493's c: kappa %s, bit-bound"
      % (e535["kappa"], e535["bit_lower"], a535["kappa"]))
print("   PR #531 receipt: kappa %s, complex-bound (main's headline)" % e531["kappa"])
