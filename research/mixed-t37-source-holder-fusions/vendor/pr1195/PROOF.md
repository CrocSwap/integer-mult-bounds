# Proof note: two source-holder fusions

**Setting.** The base is #1148's joint-entrance word `1f666402…` (decompressed payload), whose scalar program equals the
seven-slot k8 word `c2b29430…` of #1018 (checked by gate comparison of A, B, cleanup and the early-cleanup indices). The
result is `bd8a8dc5…`. `RECIPE.json` lists the literal difference; `build_word.py` checks every removed element.

**Scalar edits, site X=439** (copy pair: entering helper 584 = E + 439 after its copy gate; slot holders 10 and 74):

- delete the second-holder donation `74 += −½·584` and its early-cleanup restore `74 += ½·584`;
- move the source-holder donation `10 += −½·439` to directly after the last write of 10 before target 190 reads it
  (FULL-cleanup restore `10 += ½·439` unchanged);
- full read-set exchange of (584, 439): target 126 now reads `126 += −½·439` instead of receiving 584 through holder 74,
  and its entrance pre-read `126 += ½·584` is deleted.

**Site X=444** is the same with copy pair (590, 444), holders 34 and 98, targets 214 and 150: the donation `98 += 590` and its
tail `98 += −590` are deleted, `34 += 444` is repositioned (restore `34 += −444` unchanged), and target 150 reads
`150 += 444` with its pre-read `150 += −590` deleted.

Relative to #1148's word, all other differences are frame annotations (33 A gates, 24 kept B gates, early-cleanup frames) and
the order of commuting FULL-cleanup prepends, which act on pairwise distinct registers.

**Exactness.** Every register still has the same value at the end of B, so the complete program map is unchanged: each
deleted delivery of E into a target is replaced by the exchanged read of X together with the deleted pre-read, exactly as
in the read-set exchange rule (the B-segment map is checked mod p while searching). The binding check is #645's independent
`audit_local.py`: exact rational endpoint replay of all 704 columns in both orientations, monotone frame chains, centre
levels, dyadic units, zero entrance response, wrapper exclusion and the final helper row/column cones. The PR635 native chain
replays the word again (transport, ledgers, local replay, wrappers, all phase edges).

**Necessity of each edit.** `controls.py` removes or perturbs each part of each site (restore, donation, its sign, the fused
target read, donation and restore together). All ten mutants fail the all-column endpoint check.

**Paid profile.** The exact frame optimum of the new program changes the local profile by `{1:−3, 2:+3, 3:−2, 4:+2, 5:−1}` per site. The
rank mass (5,590) and every helper width (total 3,734) are unchanged, as required by the invariant `local mass − width = 1856`.

**Hosting.** Entrance frames (`start_extra`), end frames (`helper_final`), ports, centres, target levels and the width
inventory are identical to #1148's word. Hence #1148's frozen T16 owners, windows, charts and idle profile apply verbatim;
the strict admission re-checks every role in its actual window, the controller mutations, the finite invoice (prefix 397 <
512 charged bits, physical row coefficient below 20,161), both moment engines and the 47 outer inequalities.

**Pricing.** With global profile `{1:339912, 2:72576, 3:58752, 4:19296, 5:11520, 8:1152, 24:1, 48:4918}` the certified complex
root and the retained outer assembly with the PR589 bit supplier give κ = 837829001135967/5·10¹⁷; the complex side binds.
