# QQ16: two-query recovery at a recorded first-pair cut

**Scoped proof; no new supplier or κ.** The two initial ordinary records
`(B0 X_U, B2 X_U)` recover pair 0's original selected X/Y inputs when
combined with the explicitly granted post-B1 selected values, forward
histories and a completed-X descendant. This holds for arbitrary inputs
in all four bank pairs, beyond the particular erased family of this
account's [PR #2153](https://github.com/CrocSwap/integer-mult-bounds/pull/2153).

The [proof](PROOF.md) specifies the observation operator and gives a
decoder D with `D O=J`, where J selects the original four A/T blocks of
pair 0. In particular, its complete kernel has no selected-input defect.
The useful tail identity is

```text
Y_(0,U)^initial = Y_(0,U)^final - K_(2,U) f2.
```

Here final **Y** is the completed-X descendant after the retained signed
terminal. It is not the former-Y hole. The decoder reconstructs the
transient F0 A value; it does not save an extra copy of that value.

**Access to the post-B1 selected cut is a premise.** A controller that
offers only final selected values still needs to preserve or reconstruct
those cut values. This is an information lemma, not physical execution,
a final-only controller, recovery for every bank from two pair-0 reads,
or a complete recursive-cost invoice. Sixteen query coordinates are not
silently identified with sixteen paid rank units.

## Evidence and reproduction

[RESULT.json](RESULT.json) records three zero residuals in a free
noncommutative operator algebra; symbolic propagation of the 17-event
tail; all 160 basis inputs of two independent rational models; and
twelve rejecting controls. Exact row reduction independently checks
`rank [O;J]=rank O` in both models (18 and 27). The actual QQ16 packet's
port partition, Gram identities and selected inverses are rebound to
main. Local call pairs are read from the complete selected template:
F2 is on pair 0, and F8 is on pair 3. The native compiler,
actual-cover full matrix and full selected
cold replay are not rerun. Evidence is author-checked, with no independent
human review or proof-assistant claim.

Standard-library Python 3.12, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-two-query-kernel
```

The registered hook runs normal and optimized replays plus artifact
tests. The direct read-only command also works in a source export:

```sh
python3 -I -O -B research/qq16-two-query-kernel/verify.py
```

Expected marker:

```text
PASS_QQ16_TWO_QUERY_KERNEL pair0_selected_recovered symbolic=3 tail=17 basis=160 controls=12 no_new_kappa
```

`--write` explicitly regenerates the receipt. Default verification changes
no file and compares the complete canonical JSON payload. Source pins
are in [SOURCES.json](SOURCES.json); scope, predecessor heads and next
questions are in [TASK.json](TASK.json). The claim is in
[discussion #2074](https://github.com/CrocSwap/integer-mult-bounds/discussions/2074).

## Open next questions

* Can one actual controller recover `p_A,p_T,d_A` at the B1 cut from its
  final selected records? Trace its literal selected program first.
  This determines whether the present information lemma supplies its
  missing decoder or requires additional paid retention.
* What is the complete native cost of the two pre-F0 records and the
  decoder's `B2` read of a completed-X descendant? Start with the
  actual endpoint frames and charge storage, all chart maps and cleanup
  together. No favorable completed budget is established here; physical
  access, hosting, tape and precision remain the blockers.
* Can 13--15 query coordinates suffice under the same explicit cut
  contract? PR #2153 excludes at most twelve on its erased family.
  First test a proposed compression against the full observation
  operator, rather than only that family. No sharp minimum is claimed.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0.

Ali Romman's PR #1969 supplies the ordered conserved maps, selected
sections, actual native words and ordinary witness schedule. Their
inverse formulas and local realization are not claimed as new here.
This account's PR #2153 supplied the transcript-capacity obstruction and
the explicit two-record handoff. Ross Richardson's PR #2104 supplied
the three-query rank method; Cinna Davis's PR #2079/#2122 tested one
ordinary query and one compressed affine record. Adam Gall's
PR #2086/#2093 provided adjacent logger and query obstructions.
The retained Rohan Arun, Jeremy Kothe, DreamingOfClouds and complex
supplier lineage remains credited in the source package. No pending
executable is imported and no pending result is adopted as a supplier.
Zhihao Chen's PR #377 supplies the retained complete recipe and signed
terminal. Jose Manuel's retained `paired-log-ordered-decoder` package
provides a useful comparison on a different, independent-dirty-log
interface; its global decoder is not a QQ16 selected-port decoder.
