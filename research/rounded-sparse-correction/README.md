# Reversible nearest-grid execution of the 74-gate correction

The actual PR6537 correction now has a rounded data implementation with an
exact inverse and no retained rounding transcript. Round each source product
before its ADD. Every output is a nearest grid point to the exact correction,
in both directions. The sharp error is h/2 per real coordinate.

The new fractional-error amplification is one, compared with 21 for the old
569-gate forward correction. All 44 minimum-cost source candidates attain the
same best bound; the published program already suffices. Its gate reduction
and scalar allowance remain predecessor results. No new kappa is claimed.

Two exact transfer engines agree on every coefficient. A proved two-form
periodicity reduces all actual integer rounding behavior to 64 residue classes
per direction. All 128 classes, forty large signed cases and 3,081 quantizer
cases pass. Literal inverse execution returns all 799 fields. A full-program
control shows why rounding the entire accumulator would lose information.

For D complex coordinates and incoming field error eta, the output error is
at most `15 eta + h sqrt(D/2)`. With input integer components bounded by A,
a signed range strictly above 84A suffices for every temporary value. This
range is sufficient, not minimum. Integer arithmetic and physical auxiliary
cleanup still need their own tariff.

Run `python3 -B research/rounded-sparse-correction/verify.py`.
`VERIFY.json` registers normal and optimized CPython 3.12 checks.
`PROOF.md` gives the all-input, inverse, periodicity and sharpness arguments.
`BUDGETS.json` retains all prefix/output budgets, witnesses and candidates.

## Attribution

Ali Romman prepared this contribution with substantial OpenAI Codex assistance.
Credit PR6537 for the 74-ADD rank-two correction and its complete cost search;
PR6529 for scaled transport fusion; Rohan Arun / PR6399, Erwan L. / PR6453,
DreamingOfClouds, Cinna Davis, David Arias, Gareth Davidson, Jacob Alan Sussman,
zxv, Cao Yifan and the retained source authors. Original notices and exact
inputs remain. Reversible integer lifting, nearest-even rounding and linear
error propagation are classical. Apache-2.0.

## Open next questions

- Compose this boundary with an actual raw native error and coordinate count.
  The new budget covers the correction only.
- Implement and charge reversible integer products, tie tests, checks and
  auxiliary cleanup in the actual tape layout.
- Check the complete caller and all five framework assumptions before admission.

## Verification limits

The all-integer rounding claim follows from the exact source-form and
periodicity proof, not from random testing. Physical auxiliary-bit restoration,
full native/caller execution, compiler/outer admission and independent
scientific acceptance are not supplied. The checkout is shallow, so the
optional full-history audit was not run. Live inputs are pinned to an ancestor
in this branch. No selected record is changed.
