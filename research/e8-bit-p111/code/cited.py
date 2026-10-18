"""Bind every cited complex b in data/complex-b.json to the cited PR's own receipt (vendored byte-identical or on
main; see code/provenance.py), and check the receipts this package compares against.
usage: cited.py PACKAGE_DIR
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

root = Path(sys.argv[1])
J = lambda p: json.loads((root / p).read_text())  # noqa: E731
t = J("data/complex-b.json")
for s in t["suppliers"]:
    r = J(s["receipt"])
    assert Q(r[s["field"]]) == Q(s["b"]), (s["name"], r[s["field"]], s["b"])
    print("   PR #%d (%s) b = %s = %.15e  [%s]" % (s["pr"], s["author"], s["b"], float(Q(s["b"])), s["role"].split(" (")[0]))
e548, a548 = J("data/complex/pr548/EXPECTED.json"), J("data/complex/pr548/EXACT-ASSEMBLY.json")
e544, a544 = J("data/complex/pr544/EXPECTED.json"), J("data/complex/pr544/EXACT-ASSEMBLY.json")
e535, a535 = J("data/complex/pr535/EXPECTED.json"), J("data/complex/pr535/EXACT-ASSEMBLY-PR493.json")
e510 = J("vendor/pr510/e8-r480-nine-stage/EXPECTED.json")
e531 = J("../direct-delivery504-global/EXPECTED.json")
assert all(a548[f] == e548[f] for f in ("complex_lower", "bit_lower", "kappa"))
assert a548["binding_component"] == "bit" and Q(e548["bit_lower"]) < Q(e548["complex_lower"])
assert all(a544[f] == e544[f] for f in ("complex_lower", "bit_lower", "kappa", "binding_component"))
assert e544["binding_component"] == "bit" and Q(e544["bit_lower"]) < Q(e544["complex_lower"])
assert e535["bit_lower"] == e510["nine"]["bit_lower"] and e535["binding_component"] == "bit"
assert a535["complex_lower"] == e535["complex_lower"] and a535["binding_component"] == "bit"
assert e531["binding_component"] == "complex"
print("   PR #548 receipt: kappa %s, bit-bound at its own bit c = %s" % (e548["kappa"], e548["bit_lower"]))
print("   PR #544 receipt: kappa %s, bit-bound at its own bit c = %s" % (e544["kappa"], e544["bit_lower"]))
print("   PR #535 receipt: kappa %s, bit-bound at PR #510's c = %s; with PR #493's c: kappa %s, bit-bound"
      % (e535["kappa"], e535["bit_lower"], a535["kappa"]))
print("   PR #531 receipt: kappa %s, complex-bound (main's headline)" % e531["kappa"])
