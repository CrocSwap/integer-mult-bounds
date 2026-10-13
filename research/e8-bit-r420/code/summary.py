"""Compare every number verify.sh produced with EXPECTED.json and with the cited PRs' own receipts, and print the
summary.
usage: summary.py PACKAGE_DIR OUTPUT_DIR
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

H, W = Path(sys.argv[1]), Path(sys.argv[2])
J = lambda p: json.loads(Path(p).read_text())
e = J(H / "EXPECTED.json")
x, cc, k4, k5, lg = J(W / "xcheck.json"), J(W / "cout/columns.json"), J(W / "cout/columns_k4.json"), \
    J(W / "cout/columns_k5.json"), J(W / "cout/legality.json")
r9, r11, c480, c489 = J(W / "RESULT9.json"), J(W / "RESULT11.json"), J(W / "c480/RESULT9.json"), J(W / "c489/RESULT11.json")
ew = e["word"]
assert {str(a): b for a, b in cc["local_raw_H"]} == ew["local_histogram"]
assert (cc["payload_prefix_bits"], k4["payload_prefix_bits"], k5["payload_prefix_bits"]) == \
    (ew["five_stage_payload_bits"], ew["nine_stage_payload_bits"], ew["eleven_stage_payload_bits"])
assert (lg["records"], lg["common_frame_ADDs"], lg["rank_mass"]) == tuple(ew["legality"][k] for k in
                                                                         ("records", "common_frame_ADDs", "rank_mass"))
for k in ("hypotheses", "conclusion", "interleaving"):
    assert x[k] == e["interface"][k], k


def same(r, ex, names, extra=()):
    assert r["bit_lower"] == ex["bit_lower"], (r["bit_lower"], ex["bit_lower"])
    for k in extra:
        assert r[k] == ex[k], k
    for n in names:
        for f in ("kappa", "binding_component", "complex_lower"):
            assert r["kappa"][n][f] == ex["kappa"][n][f], (n, f)


same(r9, e["nine"], ("pr535", "pr531"))
assert r9["bit_profile"] == e["nine"]["profile"] and r9["bit"] == e["nine"]["bit"]
same(r11, e["eleven"], ("pr535", "pr531"), ("emitted_program_sha256",))
assert r11["bit_profile"] == e["eleven"]["profile"] and r11["bit"] == e["eleven"]["bit"]
names = ("pr535", "pr531", "pr484", "pr471", "pr458")
same(c480, e["controls"]["pr510_r480_nine"], names)
same(c489, e["controls"]["pr493_r489_eleven"], names, ("emitted_program_sha256",))
# the controls against the cited PRs' own receipts
e510 = J(H / "vendor/pr510/e8-r480-nine-stage/EXPECTED.json")["nine"]
e493 = J(H / "../e8-bit-carrier-skeleton/EXPECTED.json")["eleven"]
e535, a535 = J(H / "data/complex/pr535/EXPECTED.json"), J(H / "data/complex/pr535/EXACT-ASSEMBLY-PR493.json")
e531 = J(H / "../direct-delivery504-global/EXPECTED.json")
assert c480["bit_lower"] == e510["bit_lower"] and c480["bit_profile"] == e510["profile"]
assert all(c480["kappa"][n]["kappa"] == e510["kappa"][n]["kappa"] for n in e510["kappa"])
assert c480["kappa"]["pr535"]["kappa"] == e535["kappa"] and c480["kappa"]["pr535"]["binding_component"] == "bit"
assert c489["bit_lower"] == e493["bit_lower"] and c489["bit_profile"] == e493["profile"]
assert c489["emitted_program_sha256"] == e493["emitted_program_sha256"]
assert all(c489["kappa"][n]["kappa"] == e493["kappa"][n]["kappa"] for n in ("pr484", "pr471", "pr458"))
assert c489["kappa"]["pr535"]["kappa"] == a535["kappa"] and c489["kappa"]["pr535"]["binding_component"] == "bit"
assert c489["kappa"]["pr531"]["kappa"] == e531["kappa"] and c489["kappa"]["pr531"]["binding_component"] == "complex"
c9, c11, k = F(r9["bit_lower"]), F(r11["bit_lower"]), F(r9["kappa"]["pr535"]["kappa"])
assert r11["kappa"]["pr535"]["kappa"] == r9["kappa"]["pr535"]["kappa"]
b535, b531 = F(e535["complex_lower"]), F(e531["complex_lower"])
assert c11 > b535 > b531 and c9 > b535
p = lambda a, b: "%+.4f%%" % (100 * float(F(a) / F(b) - 1))
print("PASS bit c, nine stages (PR #510's pipeline, 32 replicas, all %d residuals hosted whole, 0 banks) = %s = %s"
      % (r9["bit"]["hosted_residuals"], r9["bit_lower"], r9["bit_lower_decimal"]))
print("     %s over PR #510's R480 (%s), %s over PR #493's R489 at eleven stages" %
      (p(c9, e510["bit_lower"]), e510["bit_lower_decimal"], p(c9, e493["bit_lower"])))
print("PASS bit c, eleven stages (PR #493's pipeline) = %s = %s (%s over PR #493's R489, same pipeline)"
      % (r11["bit_lower"], r11["bit_lower_decimal"], p(c11, e493["bit_lower"])))
for n, rec in (("pr535", e535), ("pr531", e531)):
    kk = r9["kappa"][n]
    print("PASS kappa with PR #%s's complex b = %s: %s = %s (%s-bound; the same with the nine- and the eleven-stage c);"
          " the PR's own kappa is %s (%s-bound), change %s" % (n[2:], kk["complex_lower"], kk["kappa"], kk["kappa_decimal"],
                                                              kk["binding_component"], rec["kappa"],
                                                              rec["binding_component"], p(kk["kappa"], rec["kappa"])))
print("     controls reproduced exactly: PR #510's R480 c %s and, with PR #535's b, PR #535's kappa %s (bit-bound);"
      % (c480["bit_lower_decimal"], c480["kappa"]["pr535"]["kappa_decimal"]))
print("     PR #493's R489 c %s, with PR #531's b PR #531's kappa %s (complex-bound), with PR #535's b PR #535's"
      " control kappa %s (bit-bound)" % (c489["bit_lower_decimal"], c489["kappa"]["pr531"]["kappa_decimal"],
                                       c489["kappa"]["pr535"]["kappa_decimal"]))
