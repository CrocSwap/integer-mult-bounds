"""Compare every number verify.sh produced with EXPECTED.json and with the cited PRs' own receipts, and print the
summary.
usage: summary.py PACKAGE_DIR OUTPUT_DIR
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

H, W = Path(sys.argv[1]), Path(sys.argv[2])
J = lambda p: json.loads(Path(p).read_text())  # noqa: E731
e = J(H / "EXPECTED.json")
x, mu, mp = J(W / "xcheck.json"), J(W / "mutants.json"), J(W / "mutants_p.json")
cc, k4, k5, lg = J(W / "cout/columns.json"), J(W / "cout/columns_k4.json"), J(W / "cout/columns_k5.json"), \
    J(W / "cout/legality.json")
r9, r11 = J(W / "RESULT9.json"), J(W / "RESULT11.json")
c480, c480s, c545 = J(W / "c480/param/RESULT9.json"), J(W / "c480/stock/RESULT9.json"), J(W / "c545/RESULT11.json")
g11, g545 = J(W / "bit/GLOBAL.json"), J(W / "c545/bit/GLOBAL.json")
ew = e["word"]
# word, checker, controls
assert x["status"] == "PASS_EXACT_REPLAY_AND_INTERLEAVED_INTERFACE" and x["v"] == ew["v"] and x["punctured"] == 9
assert x["copy_ranks"] == [7] * 9 and x["totals_on_punctured_hyperplanes"]
for k in ("hypotheses", "conclusion", "interleaving"):
    assert x[k] == e["interface"][k], k
assert mp["all_rejected"] and len(mp["controls"]) == 4
assert {str(a): b for a, b in cc["local_raw_H"]} == ew["local_histogram"]
assert (cc["payload_prefix_bits"], k4["payload_prefix_bits"], k5["payload_prefix_bits"]) == \
    (ew["five_stage_payload_bits"], ew["nine_stage_payload_bits"], ew["eleven_stage_payload_bits"])
assert (lg["records"], lg["common_frame_ADDs"], lg["rank_mass"]) == tuple(ew["legality"][k] for k in
                                                                         ("records", "common_frame_ADDs", "rank_mass"))


def same(r, ex, names, extra=()):
    assert r["bit_lower"] == ex["bit_lower"], (r["bit_lower"], ex["bit_lower"])
    for k in extra:
        assert r[k] == ex[k], k
    for n in names:
        for f in ("kappa", "binding_component", "complex_lower"):
            assert r["kappa"][n][f] == ex["kappa"][n][f], (n, f)


names = ("pr548", "pr544", "pr535", "pr531")
same(r9, e["nine"], names)
assert r9["bit_profile"] == e["nine"]["profile"] and r9["bit"] == e["nine"]["bit"]
same(r11, e["eleven"], names)
assert r11["bit_profile"] == e["eleven"]["profile"] and r11["bit"] == e["eleven"]["bit"]
assert g11["emitted_program_sha256"] == e["eleven"]["emitted_program_sha256"]
# controls against the cited PRs' own receipts
e510 = J(H / "vendor/pr510/e8-r480-nine-stage/EXPECTED.json")["nine"]
e545 = J(H / "vendor/pr545/EXPECTED.json")
e548, e544, e535 = J(H / "data/complex/pr548/EXPECTED.json"), J(H / "data/complex/pr544/EXPECTED.json"), \
    J(H / "data/complex/pr535/EXPECTED.json")
e531 = J(H / "../direct-delivery504-global/EXPECTED.json")
assert c480 == c480s
assert c480["bit_lower"] == e510["bit_lower"] and c480["bit_profile"] == e510["profile"]
assert all(c480["kappa"][n]["kappa"] == e510["kappa"][n]["kappa"] for n in e510["kappa"])
assert c480["kappa"]["pr535"]["kappa"] == e535["kappa"] and c480["kappa"]["pr535"]["binding_component"] == "bit"
assert c545["bit_lower"] == e545["eleven"]["bit_lower"] and c545["bit_profile"] == e545["eleven"]["profile"]
assert g545["emitted_program_sha256"] == e545["eleven"]["emitted_program_sha256"]
assert c545["kappa"]["pr535"]["kappa"] == e545["kappa"]["pr535"]["kappa"]
c9, c11 = F(r9["bit_lower"]), F(r11["bit_lower"])
assert all(r11["kappa"][n]["kappa"] == r9["kappa"][n]["kappa"] for n in names)
b548 = F(e548["complex_lower"])
assert c11 > b548 and c9 > b548 and all(r9["kappa"][n]["binding_component"] == "complex" for n in names)
p = lambda a, b: "%+.4f%%" % (100 * float(F(a) / F(b) - 1))  # noqa: E731
print("PASS bit c, nine stages (PR #510's pipeline parameterised for v = %d, 32 replicas, all %d residuals hosted whole, "
      "%d banks) = %s = %s" % (ew["v"], r9["bit"]["hosted_residuals"], r9["bit"]["bank_assignments"], r9["bit_lower"],
                               r9["bit_lower_decimal"]))
print("     %s over PR #510's R480 (%s); %s over PR #545's punctured R489 at eleven stages (%s)"
      % (p(c9, e510["bit_lower"]), e510["bit_lower_decimal"], p(c9, e545["eleven"]["bit_lower"]),
         e545["eleven"]["bit_lower_decimal"]))
print("PASS bit c, eleven stages (PR #493's pipeline as parameterised by PR #545) = %s = %s (%s over PR #545's c)"
      % (r11["bit_lower"], r11["bit_lower_decimal"], p(c11, e545["eleven"]["bit_lower"])))
for n, rec in (("pr548", e548), ("pr544", e544), ("pr535", e535), ("pr531", e531)):
    kk = r9["kappa"][n]
    print("PASS kappa with PR #%s's complex b = %s: %s = %s (%s-bound; the same with the nine- and the eleven-stage c);"
          " the PR's own kappa is %s, change %s" % (n[2:], kk["complex_lower"], kk["kappa"], kk["kappa_decimal"],
                                                   kk["binding_component"], rec["kappa"], p(kk["kappa"], rec["kappa"])))
print("     controls reproduced exactly: the parameterised nine-stage files are byte-identical to PR #510's on its R480 word"
      " (c %s; with PR #535's b, PR #535's kappa %s, bit-bound);" % (c480["bit_lower_decimal"],
                                                                     c480["kappa"]["pr535"]["kappa_decimal"]))
print("     PR #545's word through PR #545's files: c %s and emitted-program sha256 %s... as in PR #545's EXPECTED.json;"
      " the receipts of PR #548, #544 and #535 give their own kappa through the same assembly (step 0)"
      % (c545["bit_lower_decimal"], g545["emitted_program_sha256"][:16]))
