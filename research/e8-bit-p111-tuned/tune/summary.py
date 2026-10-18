"""Compare every number tune/verify.sh produced with tune/EXPECTED.json, PR #555's EXPECTED.json and the cited receipts,
and print the summary.  `--record` writes tune/EXPECTED.json from the outputs instead (used once, then reviewed).
usage: summary.py PACKAGE_DIR TUNE_DIR OUTPUT_DIR [--record]
Adapted from PR #555's code/summary.py (eumemic); prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0."""
import copy
import gzip
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

H, TD, W = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
record = "--record" in sys.argv[4:]
J = lambda p: json.loads(Path(p).read_text())  # noqa: E731
base = J(H / "EXPECTED.json")
word_p = TD / "bitE8mut-p111-tuned.json.gz"
x, mu, mp = J(W / "xcheck.json"), J(W / "mutants.json"), J(W / "mutants_p.json")
cc, k4, k5, lg = J(W / "cout/columns.json"), J(W / "cout/columns_k4.json"), J(W / "cout/columns_k5.json"), \
    J(W / "cout/legality.json")
r9, r11, g11 = J(W / "RESULT9.json"), J(W / "RESULT11.json"), J(W / "bit/GLOBAL.json")
names = ("pr548", "pr544", "pr535", "pr531")
raw = json.loads(gzip.open(word_p, "rt").read())
content = hashlib.sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

if record:
    e = copy.deepcopy(base)
    ew = e["word"]
    ew.update(file="tune/bitE8mut-p111-tuned.json.gz", file_sha256=hashlib.sha256(word_p.read_bytes()).hexdigest(),
              content_sha256=content, base_content_sha256=base["word"]["content_sha256"],
              gates={k: len(raw[k]) for k in "DABC"},
              local_histogram={str(a): b for a, b in cc["local_raw_H"]},
              legality={k: lg[k] for k in ("records", "common_frame_ADDs", "rank_mass")},
              five_stage_columns=cc["formal_columns_checked"], five_stage_payload_bits=cc["payload_prefix_bits"],
              nine_stage_columns=k4["formal_columns_checked"], nine_stage_payload_bits=k4["payload_prefix_bits"],
              eleven_stage_columns=k5["formal_columns_checked"], eleven_stage_payload_bits=k5["payload_prefix_bits"])
    for k in ("plan_sha256", "params_sha256"):
        ew.pop(k)
    ew["stats"] = None
    del ew["stats"]
    e["interface"] = {k: x[k] for k in ("hypotheses", "conclusion", "interleaving")}
    for key, r in (("nine", r9), ("eleven", r11)):
        d = e[key]
        d["bit_lower"], d["bit_lower_decimal"] = r["bit_lower"], r["bit_lower_decimal"]
        d["profile"], d["bit"] = r["bit_profile"], r["bit"]
        d["kappa"] = {n: {f: r["kappa"][n][f] for f in ("kappa", "kappa_decimal", "complex_lower", "binding_component")}
                      for n in names}
    e["eleven"]["emitted_program_sha256"] = g11["emitted_program_sha256"]
    e["base"] = {"nine_bit_lower": base["nine"]["bit_lower"], "nine_bit_lower_decimal": base["nine"]["bit_lower_decimal"],
                 "eleven_bit_lower": base["eleven"]["bit_lower"],
                 "eleven_bit_lower_decimal": base["eleven"]["bit_lower_decimal"],
                 "note": "PR #555's EXPECTED.json (untuned word); the tune/ pipeline is the same, with the same frozen hosting selections"}
    (TD / "EXPECTED.json").write_text(json.dumps(e, indent=1) + "\n")
    print("   recorded", TD / "EXPECTED.json")
    sys.exit(0)

e = J(TD / "EXPECTED.json")
ew = e["word"]
# word, checker
assert content == ew["content_sha256"] and hashlib.sha256(word_p.read_bytes()).hexdigest() == ew["file_sha256"]
assert ew["base_content_sha256"] == base["word"]["content_sha256"] == json.loads((TD / "moves.json").read_text())["base_content_sha256"]
assert x["status"] == "PASS_EXACT_REPLAY_AND_INTERLEAVED_INTERFACE" and x["v"] == ew["v"] and x["punctured"] == 9
assert x["copy_ranks"] == [7] * 9 and x["totals_on_punctured_hyperplanes"]
for k in ("hypotheses", "conclusion", "interleaving"):
    assert x[k] == e["interface"][k], k
assert mp["all_rejected"] and len(mp["controls"]) == 4
assert {str(a): b for a, b in cc["local_raw_H"]} == ew["local_histogram"]
assert (cc["payload_prefix_bits"], k4["payload_prefix_bits"], k5["payload_prefix_bits"]) == \
    (ew["five_stage_payload_bits"], ew["nine_stage_payload_bits"], ew["eleven_stage_payload_bits"])
assert (cc["formal_columns_checked"], k4["formal_columns_checked"], k5["formal_columns_checked"]) == \
    (ew["five_stage_columns"], ew["nine_stage_columns"], ew["eleven_stage_columns"])
assert (lg["records"], lg["common_frame_ADDs"], lg["rank_mass"]) == tuple(ew["legality"][k] for k in
                                                                         ("records", "common_frame_ADDs", "rank_mass"))
assert ew["legality"] == base["word"]["legality"]      # the transports change no record count and no rank mass


def same(r, ex):
    assert r["bit_lower"] == ex["bit_lower"] and r["bit_lower_decimal"] == ex["bit_lower_decimal"], (r["bit_lower"],)
    assert r["bit_profile"] == ex["profile"] and r["bit"] == ex["bit"]
    for n in names:
        for f in ("kappa", "binding_component", "complex_lower"):
            assert r["kappa"][n][f] == ex["kappa"][n][f], (n, f)


same(r9, e["nine"])
same(r11, e["eleven"])
assert g11["emitted_program_sha256"] == e["eleven"]["emitted_program_sha256"]
# the headline, exactly
assert r9["bit_lower"] == "1733427039589844234749/1000000000000000000000000"
assert r9["bit_lower_decimal"] == "0.001733427039589844234749"
c9, c11 = F(r9["bit_lower"]), F(r11["bit_lower"])
cb9, cb11 = F(base["nine"]["bit_lower"]), F(base["eleven"]["bit_lower"])
assert c9 > cb9 and c11 > cb11
# kappa is that of PR #555: every cited complex b binds
for n in names:
    assert r9["kappa"][n]["kappa"] == base["nine"]["kappa"][n]["kappa"] == r11["kappa"][n]["kappa"]
    assert r9["kappa"][n]["binding_component"] == "complex"
# cross-check with the quick exact pricer (idle remainder read off the base word's audit)
sys.path.insert(0, str(TD))
import fastc  # noqa: E402
import wlib  # noqa: E402
fc = fastc.fast_c(wlib.paid(raw))
assert fc == r9["bit_lower_decimal"], (fc, r9["bit_lower_decimal"])
p = lambda a, b: "%+.4f%%" % (100 * float(F(a) / F(b) - 1))  # noqa: E731
print("PASS bit c, nine stages (PR #555's chain, frozen hosting rediscovered, all %d residuals hosted whole, %d banks) = %s = %s"
      % (r9["bit"]["hosted_residuals"], r9["bit"]["bank_assignments"], r9["bit_lower"], r9["bit_lower_decimal"]))
print("     PR #555 untuned: %s; this word %s" % (base["nine"]["bit_lower_decimal"], p(c9, cb9)))
print("PASS bit c, eleven stages (PR #493's chain as parameterised by PR #545) = %s = %s" % (r11["bit_lower"],
                                                                                          r11["bit_lower_decimal"]))
print("     PR #555 untuned: %s; this word %s" % (base["eleven"]["bit_lower_decimal"], p(c11, cb11)))
for n in names:
    kk = r9["kappa"][n]
    print("PASS kappa with PR #%s's complex b = %s: %s = %s (%s-bound; the same with PR #555's word and with the eleven-stage c)"
          % (n[2:], kk["complex_lower"], kk["kappa"], kk["kappa_decimal"], kk["binding_component"]))
print("     quick pricer (tune/fastc.py: 288 x local paid profile + idle remainder) gives the same nine-stage c: %s" % fc)
print("     local paid profile %s (PR #555: %s)" % (ew["local_histogram"], base["word"]["local_histogram"]))
