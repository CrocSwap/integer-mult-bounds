"""Regression of the generalised compressed nine-stage scripts against PR #386's own receipts.

Run on PR #370's word, global_word_g.py, audit_g.py and certify_g.py must reproduce PR #386's GLOBAL.json, AUDIT.json
and the bit fields of COMBINED.json (vendored byte-identical from #386's validation directory) field for field. The only
fields not compared are wall-clock seconds and the two hashes that cover GEOMETRY.json, whose 'seconds' field differs
on every run (geometry_sha256 and template_sha256).
usage: regress386.py OUR_OUT_DIR PR386_RECEIPT_DIR
Prepared by eumemic with Anthropic Claude assistance; Apache-2.0."""
import json
import sys
from pathlib import Path

ours, ref = Path(sys.argv[1]), Path(sys.argv[2])
skip = {"seconds", "geometry_sha256", "template_sha256"}
g, G = json.loads((ours / "GLOBAL.json").read_text()), json.loads((ref / "GLOBAL.json").read_text())
assert set(g) == set(G), set(g) ^ set(G)
bad = [k for k in G if k not in skip and g[k] != G[k]]
assert not bad, bad
a, A = json.loads((ours / "AUDIT.json").read_text()), json.loads((ref / "AUDIT.json").read_text())
assert set(a) == set(A), set(a) ^ set(A)
bad = [k for k in A if k not in skip and a[k] != A[k]]
assert not bad, bad
c, C = json.loads((ours / "BIT-NINE.json").read_text()), json.loads((ref / "COMBINED.json").read_text())
for k in ("bit_coarse", "bit_moment_interval", "composed_moment_upper", "halving_depth"):
    assert c[k] == C[k], k
for k in ("unit_additions", "route_items", "selector_calls", "coefficient", "coefficient_bits", "two_level_coefficient",
          "two_level_coefficient_bits", "charged_bound_bits", "payload_prefix_bits", "charged_payload_prefix_bits",
          "row_coefficient", "retained_row_coefficient"):
    assert c["finite"][k] == C["finite"][k], k
k386 = c["kappa_with_cited_complex"]["pr386"]
for k in ("complex_coarse", "selected_bit_coarse", "kappa", "bootstrap_chain", "strict_constraints"):
    assert k386[k] == C[k], k
assert k386["cutoff"] == C["finite"]["cutoff"]
print("   regression: on PR #370's word the generalised scripts reproduce PR #386's GLOBAL.json (%d fields), AUDIT.json"
      " (%d fields) and COMBINED.json's bit, finite and kappa fields (c = %s, kappa = %s), except wall-clock seconds and"
      " the two GEOMETRY.json hashes" % (len(G) - 3, len(A) - 2, C["bit_coarse"], C["kappa"]))
