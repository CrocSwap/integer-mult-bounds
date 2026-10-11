# Complex supplier b ≈ 1.327·10⁻³ under whole-residual hosting: shared-donor kernel and entrance gauges with paid residual wrappers (conditional on two lemmas)

**Certified complex saving b = 1326789535340266/10¹⁸ ≈ 1.326790·10⁻³, +4.68 % over #442's 1.267453·10⁻³,** on #442's whole-residual idle-axis hosting (no
cross-family split) with the rule of #458 extended to banks: an entering helper is the only owner of its physical family (data or bank) in every invocation. It rests on two lemmas that are the review points:
**Lemma A** (paid residual wrappers R_E⁻¹ / L_E⁻¹ with explicit spectators; the entrances are isotropic, not coordinate entrances) and **Lemma G**
(nonzero-frame compensation and the centre scatter); see [PROOF.md](PROOF.md). The bit side is not changed by this package.

## What it does
On #433's split-centre complex word (R = 560, m = 73, nine stages) two tools of the bit side are ported:

| complex word | entering helpers | entrance rank | b (·10⁻³) | gain over #442 |
| --- | ---: | ---: | ---: | ---: |
| #442 | 0 | 0 | 1.267453 | |
| shared-donor kernel (#417/#435/#434/#439/#440; 79 pivots, rank-1 entrances) | 79 | 79 | 1.305684 | +3.02 % |
| entrance gauges (#401/#408–#416; nested per target and per centre) | 80 | 106 | 1.306413 | +3.07 % |
| **both** | 122 | 148 | **1.326790** | **+4.68 %** |

An entering helper's residual has width 9 − e (e = entrance rank), which tiles #442's idle children of ranks 8/16/32/48. Under the one-helper rule the word with both
tools hosts 39,792 of 40,320 residuals whole; the other 528 (all of width 8) sit in 66 banks of their own, one entering helper per replica per bank family and the spectators in the bank's pad (live stock 7,746, maximum child 9, rank deficit 2,496).

## Relation to #458 and #449
#458 (chafreaky) ships the 79-pivot kernel of the draft #449 on an eleven-stage complex word with paid, emitted residual adapters and the one-helper rule. This package
adopts exactly that treatment (wrappers, spectators, one helper per family) on the nine-stage word and adds the entrance gauges; it supersedes the draft #449, whose
hosting allowed several helpers on one family and left the spectator coordinates of an entering helper unplaced.
The one-owner rule is applied to bank families too (an entering helper owns its bank family alone in the invocation; its spectators are the first cells of the bank's pad, borrowed and not deducted, as #471 borrows spectators
in the same owner array).

## Result of `verify.py`
- complex b (two exact moment engines, next grid point rejected): **1326789535340266/10¹⁸**; the complex-only κ cap of this lineage is 1.325031·10⁻³ (#442's complex word: 1.265849·10⁻³; the #448/#450 lineage used in #464 and #469 has complex roots of about 1.44·10⁻³).
- Strict outer assembly (six bootstrap levels, 47 inequalities, next grid point and zero-η, zero-β, unit-β controls rejected) for two bit suppliers: #442's own bit word (run here):
  κ = 1.237552·10⁻³, bit-bound, unchanged; and the eleven-stage R724 mixed word under whole-residual hosting (bit c = 1.280810·10⁻³, a **pinned input** from our bit-side
  package, not re-run here): κ = 1.279171·10⁻³, bit-bound. **No new κ is claimed: the bit side binds.** The current lemma-less κ frontier is #478 (Dugongue) at 1.295509·10⁻³, which sits at #458's complex cap; this supplier raises that cap; #458, #460 and #462 are bit-bound, not complex-bound. On the complex side b is
  +2.28 % over #458's 1.297204·10⁻³ and +1.65 % over #471's 1.305232·10⁻³ (#471 admits our kernel79 through normalisation plus same-owner spectator borrowing; credited). The R724 pairing is informational; our related R715 word is #463.
- Regression anchor: with the empty selection the generalised scripts reproduce #433's CANONICAL-WORD, LOCAL-PROGRAMS, LOCAL-CHECKS, parent GLOBAL-TEMPLATE and
  INDEPENDENT-REPLAY, and #442's hosted template and `HOSTED.json` (compared byte for byte within one run; the gzip container bytes depend on the zlib of the Python in use, so the `.gz` files of a Python 3.14 and a Python 3.12 run differ; `EXPECTED.json` therefore pins the Lemma G inputs `CANONICAL-WORD.json` and `LOCAL-PROGRAMS.json` by the sha256 of their decompressed JSON, never of the `.gz` bytes).
- Exact checks on the gauge + kernel word: arbitrary-dirt and inverse-transpose replay on 800 columns; emitted program replay in both orientations with centre lifetimes
  and with the paid wrappers; an independent read-back of the serialized stream; exact Gaussian recipes (global phase included) for every used frame transition; exact decoding of
  the serialized wrapper monomials (L⁻¹ S_E R⁻¹ = C_[w] ⊗ I on every entrance frame); independent hosting audit with the one-owner rule and the spectator chart on data and bank families;
  an independent check stage for Lemma G (`code/lemmaG/`, imports no package script): label / scalar / accounting checker, exhaustive instance identities on all 512 basis columns, the complete program end to end, and 14 necessity mutants.
- Mutation controls, all rejected, several through the certifying scripts themselves (`audit_gk`, `emit_gk`, `replay_gk`, `audit_hosted_gk`): kernel and gauge gates, entrances, target levels,
  centre chains, wrappers (missing, misplaced, wrong frame, wrong phase / translation / quadratic form / sides / width), centre descent steps, two helpers on one family
  (accepted by #442's rule, rejected here), the same on bank families (the nine-cell-footprint layout), spectator records on data and bank families, owners in the private namespace, owners on another replica's families, wrappers on data / target / centre registers,
  and four selection-level conditions; the generators `hosted_gk.py` and `integrate_gk.py` refuse the eight-entering-helpers-per-bank tiling (`code/controls_hosting.py`).

## Plain statements about the scope
- **The entrances are not coordinate entrances.** Every entrance frame consists of even-weight vectors of F2⁹ (the dot product is alternating on E; 15 of the 16 frames of the headline word are
  totally isotropic). The bit-style criterion of #440 (`validate_isometries`) is NOT met and cannot be: no orthogonal map of O(9,2) sends such an E to coordinate axes. With
  entrances restricted to those that meet it the gain is 0 (`provenance/iso1.py`). Lemma A therefore uses two-sided paid monomials: part (i), L_E⁻¹ S_E R_E⁻¹ = C_[w] ⊗ I, is checked exactly; part (iii),
  that the wrappers surround a whole invocation of a host or bank family on which nothing else acts, is #458's argument and is assumed.
- #442's shipped complex audit asserted `w == 9` and #433's emit asserted start frame 0 for compensated registers; the marked copies (`audit_gk.py`, `emit_gk.py`, `integrate_gk.py`,
  `replay_gk.py`, `hosted_gk.py`, every change marked `GK:`) and the generated `audit_hosted_gk.py` generalise exactly these assumptions.
- **Lemma G** reduces to #425's conjugation lemma and to the virtual entrance of #471 / #458 plus a schedule lemma (PROOF.md §2, hypotheses (a)-(d)); the common-label property is checked on the emitted streams, not assumed.
- Hosting is whole-residual: one slot (child, port, offset) per residual, `offset + width ≤ rank`; no residual is split across families or children.
- All inherited interfaces of #370, #386, #425, #433, #442 remain assumptions. This is a conditional finite witness, not a theorem.

## Run
This package lives in the tree of PR #442 and runs that package unchanged first (pinned by `SOURCE.json`).
```sh
python3 -B research/e8-complex-gauge-kernel/verify.py /absolute/new/output [--all] [--discover-check]
```
Python 3.11+ and numpy (the Lemma G check stage); `--discover-check` also needs scipy and recomputes the frozen hosting selections (HiGHS), requiring equality. `--all` adds the kernel-only and
gauge-only words. About 25 minutes (PR #442's replay is 4 minutes of it; the exact phase recipes of each word take 2.5 minutes, the Lemma G stage about 10). The output directory must not exist.

## Files
`PROOF.md` lemmas and scope · `verify.py` · `EXPECTED.json` · `SOURCE.json`, `MANIFEST.json` · `data/selections/*.json` frozen kernel classes and gauge entrances (helper indices),
`data/SELECTION.json` frozen hosting selections (patterns of distinct stages per idle-child copy), `data/bit-suppliers-pinned.json` · `code/` (`gk_word.py` applies a selection;
`audit_gk.py`, `emit_gk.py`, `integrate_gk.py`, `replay_gk.py`, `hosted_gk.py` are marked copies of #433's/#442's scripts; `onehost_gk.py`, `adapters_gk.py`, `audit_hosted_gk.py`,
`assemble_gk.py`, `controls_*.py`, `run_variant.py`; `lemmaG/` the independent Lemma G check stage run by `verify.py`) · `provenance/` the search scripts (not run by `verify.py`).

## Credits
#458 (chafreaky: paid residual adapters, spectator chart and the one-helper rule), #442 (DaysSky: idle-axis hosting and the pipeline this extends), #433 (icekylinx: split centres),
#425 and #386 (jacklightChen / Zhihao Chen: mutable-basis packets, compressed windows), the shared-donor kernels and resets of the bit word: #417 and #439 (chafreaky),
#434, #435 and #438 (rohanarun), #436, #437, #440 and #441 (eumemic); the authors of #401 and #408–#416 (entrance gauges and prefixes); #370 (Dylan Crow); Jacob Sussman's E8 unit; and #451 for the
cross-family obstruction that makes whole-residual hosting the safe base; #471 (normalisation of the complete invocation and same-owner spectator borrowing, which admits the kernel79 word) and #472 (the current lemma-less κ frontier).
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
