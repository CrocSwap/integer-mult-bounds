# Sprint claim: fixed-support nonlinear Hurwitz messages

- Track: structural decoder research; OS-random assignment seed **42**.
- Random draw: `3666255942` from `od -An -N4 -tu4 /dev/urandom`; below
  the unbiased rejection cutoff `4294967200`; residue modulo 100 is 42.
- Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Claim time: 2026-10-13 05:17 UTC; expected finish: 05:55 UTC.
- Object: ten Hurwitz E8 lines with perfect-matching orthogonality; finite,
  deterministic, zero-error messages with fixed source and reader supports,
  arbitrary binary block width, and potentially nonlinear joint decoding.
- Hypothesis: under the explicit per-message charge `q * c(R,A)`, where q
  is transmitted bit width and c is the predecessor's quaternionic pairing
  rank, allowing vector and nonlinear messages still costs at least the
  sum of demanded bit widths. The physical width-pricing premise is assumed,
  not proved for arbitrary physical suppliers.
- Method: replace scalar rank subadditivity by conditional transcript
  injectivity; average over all 32 orthogonal-pair transversals. Verify the
  finite geometric inequalities and genuinely nonlinear attaining examples.
- Deliverable: scoped negative-result proof, exact reproducible certificate,
  source pins, and controls that exercise the boundary assumptions.

Three candidates considered, in seed-selected order (`42 mod 3 = 0`):

1. Nonlinear and vector messages on the Hurwitz perfect-matching geometry.
   Chosen: #703 explicitly excludes this model, and a counting argument is a
   different method from its binary rank proof.
2. Extend the degenerate-label quotient argument in format-limits-corrected
   C.4 to repeated/vector labels. Deferred: first requires a more precise
   interface for how partial subspace messages are physically copied.
3. Mixed-port E8 replacement. Not chosen: #715 already proves saturation in
   the minimal-deletion class; #747 covers the nearby star-puncture problem.

The selected certificate, actual #626/#622/#623 construction and maintainer
review, current status, contribution-review index and PR ledger were read.
Selected kappa remains `51110230636731/31250000000000000`, conditional on
the recorded implementation and analytic assumptions.

No pinned coordination issue exists (fresh GitHub query immediately before
this local claim). No reservation issue was opened. Open-PR searches for
`Hurwitz nonlinear` and `entropy copy` returned no matches. Inspected #703
and #738 (scalar-total floors), and #757/#761 (fixed-label scalar P111
floors); they leave the nonlinear model outside scope. #740 is our previous,
separate inventory-provenance contribution. No worker delegation is used.

Orientation and selection ended here. The final quarter of this bounded
iteration is reserved for verification, refreshed overlap checks and handoff.

## Result update

Completed the scoped negative result and exact replay: the fixed-support,
additively width-priced nonlinear message model has minimum copy charge
10b on the ten Hurwitz lines. The proof is by transcript injectivity, with
nonlinear attaining codes, all support inequalities, twelve mathematical
rejection controls and two artifact mutation controls. It does not prove
the physical width-pricing premise or claim a new kappa. The refreshed
overlap review is recorded in [VALIDATION.md](VALIDATION.md).

Reviewable result:
[contribution branch](https://github.com/azide0x37/integer-mult-bounds/tree/codex/seed42-hurwitz-nonlinear-copy-floor/research/hurwitz-nonlinear-copy-floor).
This is the single additional PR requested after #740; stop after submission.
