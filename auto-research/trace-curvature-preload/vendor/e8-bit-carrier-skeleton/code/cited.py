"""Bind every cited complex b in data/complex-b.json to the cited PR's own EXPECTED.json (vendored byte-identical,
pinned by git blob id; see code/provenance.py), and check the frontier receipts use the same complex supplier.
usage: cited.py PACKAGE_DIR
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

root = Path(sys.argv[1])
t = json.loads((root / "data/complex-b.json").read_text())
by = {}
for s in t["suppliers"]:
    r = json.loads((root / s["receipt"]).read_text())
    assert Q(r[s["field"]]) == Q(s["b"]), (s["name"], r[s["field"]], s["b"])
    by[s["name"]] = Q(s["b"])
    print("   PR #%d (%s) b = %s = %.15e  [%s]  %s" % (s["pr"], s["author"], s["b"], float(Q(s["b"])), s["role"],
                                                      s["status"].split(";")[0]))
for f in t["frontier"]:
    r = json.loads((root / f["receipt"]).read_text())
    assert Q(r["complex_lower"]) == by["pr471"] and r["binding_component"] == "bit"
    print("   PR #%d receipt: kappa %s (bit-bound at c = %.12e) with the same complex b as PR #471" %
          (f["pr"], r["kappa"], float(Q(r["bit_lower"]))))
