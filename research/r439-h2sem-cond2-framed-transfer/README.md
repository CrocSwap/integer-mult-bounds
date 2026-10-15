# H2-F: the H2-sem no-target-feedback clause is not used by the framed transfer (no new kappa)

**Scoped interface admission on the pinned selected R439 word; no circuit pricing, no supplier adoption.**
The selected result, the selected bit supplier and `upstream/` are unchanged.

The merged package `research/r439-copyshare-h2sem-admission` (Aaron Wang) records its F4-shaped
target-feeding-helper wrap as operator-exact but rejected only by PR1194's H2-sem condition 2, and
leaves open whether that clause is needed at the framed level, with the exact use of H1 in the
interleaved lemma named as the check to make. This package makes that check and answers it.

## What this package establishes

H1's role in the interleaved scalar-interface lemma (`research/e8-bit-r420/README.md`, the #543
lemma inherited by the selected word's checker) is confined to the z-gate transvection induction
over the gates of W0 = (A, scatter, B) and the cleanup C: "A z-gate reads only z registers
(H1, H3), so it multiplies U_k on the left by an elementary transvection". The D section enters
the lemma only as the operator y -> y + N s. Under the PR1194 substitution bridge the lemma is
invoked on the virtual splice word, which keeps the original target-only D, and the actual D
prefix is transferred by coefficient-matrix equality on all basis columns at the zero frame with
identical state and frames at the D/A cut. None of these steps consults whether a
target-feeding gate occurs inside the actual D.

The instance check: the F4 wrap is rebuilt through the pinned predecessor machinery (its own
unmodified module, its pinned certificate facts reproduced field for field), and every semantic
premise and conclusion component passes:

| component | F4 wrap |
|---|---|
| H2-sem condition 1 (zero frame, distinct operands from targets and helpers) | pass |
| complete D operator on all 661 basis columns | exact |
| state and frames at the D/A cut | equal to baseline |
| semantic N = K | pass |
| H1 restricted to W0 and C (byte-equal sections; baseline flags all pass) | pass |
| U, J, Uinv conclusion flags of the unchanged checker | pass |
| inherited flag failures | exactly H1_no_target_feeds_z, H2_D_frame0_targets_from_helpers, K_equals_D |
| D source reads | 18154, as pinned |

Only the three global syntactic flags fail — the same three recorded in the predecessor
certificate. Removing condition 2 therefore does not change what the transfer verifies. F5-shaped
source feeds remain inadmissible through condition 1 together with the framed replay's
nested-climb legality (`climb not nested: register 0 from frame 2 (dim 1) to frame 0 (dim 0)`),
which is re-checked here without condition 2.

The protective work condition 2 was conservatively doing is shown to be carried by the semantic
conditions, through three new negative controls:

| control | outcome |
|---|---|
| N1 uncompensated feed (body rows keep reading the dirtied helper) | rejected: 67 target columns moved by the fed target's dirt, first column 111 |
| N2 feed compensated by the wrong target | rejected on 67 target columns |
| N3 restore moved past the fed target's own gate (span crossing it) | rejected: the fed helper's identity row breaks |

## Reproduce

Standard library only, about two minutes, from the repository root:

```sh
python3 -I -B research/r439-h2sem-cond2-framed-transfer/verify.py
python3 scripts/research_package.py --package research/r439-h2sem-cond2-framed-transfer --check-only
```

Expected final line:

```text
PASS_R439_H2SEM_COND2_FRAMED_TRANSFER columns=661 compensated_rows=67 n1_columns=67 n2_columns=67 controls=6 no_new_kappa
```

The verifier pins every consumed source by SHA-256 (`SOURCES.json`), rebuilds the F4 wrap
deterministically through the predecessor package's own unmodified module, replays all 661 basis
columns through the unchanged `xcheck_p.py` owner checker, compares the inherited flag failures
and read counts field for field against the pinned predecessor certificate, runs the three
negative controls and the F5 exclusion, and compares the complete report against `CERTIFICATE.json`.

## Scope and what is not claimed

* **No pricing.** The F4 wrap is an operator-preserving admissibility probe (it adds 69 reads),
  not a saving. Whether any target-feedback implementation beats its restricted alternative in a
  priced model is the census side: open #2567 (at most eight registers, unit-cost single-source
  gates) and discussions/1290, /1544. This package adds no evidence on savings either way.
* **Admission, not supplier adoption.** No word is proposed for the selected chain; F/B positive
  envelopes, the 104/192-bit guards, hosted costs and the paid profile were not recomputed for
  any variant. The outer assembly, all-size compiler, hosting, precision/tape, recovery and
  analytic obligations are untouched.
* **Scoped to the transfer argument.** The result is about the necessity of condition 2 inside the
  framed transfer for the interleaved-lemma conclusion, under this word's D-prefix equivalence
  discipline. It does not restate the whole H2-sem contract for other architectures, other words
  or nonzero-frame placements.
* The chronological substitution bridge, the module argument and the semantic D contract are
  PR1194's and are consumed unmodified; this package adds the necessity analysis and the instance
  evidence.

## Open next questions

* Does a target-feedback wrap with a genuine positive saving exist in a priced model? Why it
  matters: the enlarged admissible class only pays off if a priced construction uses it. First
  step: extend the #2567 dirty-shear census's cost model with multi-operand compensated reads (the
  F4 class is two-operand), beyond its single-source unit-cost gates. Blocked by: that census's
  model and at-most-eight-register domain are #2567's scope; extending the model is a separate
  priced search.
* Should the inherited checker expose per-section H1 flags? Why it matters: consumers must
  currently re-derive "H1 on W0 and C" from byte-equality of the non-D sections plus the baseline
  flags, as this verifier does. First step: a backward-compatible optional per-section flag in
  `xcheck_p.py`'s interface report. Blocked by: the checker is a pinned source for many merged
  packages; any edit must be a separate reviewed change.

## Credit and disclosure

Prepared by Abhinav Ramachandran (geckods) with substantial assistance from a Hermes agent
(Nous Research, GLM-5.3) under the standard donation prompt. Credit: **Aaron Wang,
r439-copyshare-h2sem-admission** (the F4/F5 constructions, the pinned certificate and machinery
reused unmodified), **woklerx, PR1194** (`research/r439-semantic-d-contract-seed10/PROOF.md`: the
H2-sem contract and the chronological substitution bridge), **eumemic PR555** and
**DreamingOfClouds PR589** (the R439 word), the R420/#543 interleaved-lemma lineage, and the
pinned `xcheck_p.py` owner checker. Apache-2.0; no independent human review is claimed.
Assignment nonce `2276dce171053917945d67a485ce77f3` (task `bit-helper-contract`, priority
revision 5); claim and investigation thread: discussions/2684.
